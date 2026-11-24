"""
Section 6.2 Comparative Genomics Empirical Pilot Pipeline.

Implements the exact nested statistical model ladder specified in Section 6.2:
  - M0:  Element-level sequence & genomic covariates Z_elem(e)
  - M1:  M0 + enhancer activity breadth T(e) + target-gene covariates Z_gene(g)
  - M1b: M0 + T(e) + within-target-gene fixed effects alpha_{g(e)} (FWL demeaning)
  - M2:  M1  + higher-order reach B(e), buffering R(e), and interaction B(e)*R(e)
  - M2b: M1b + B(e), R(e), and B(e)*R(e) (strict within-target-gene test)

Evaluation:
  - Leave-one-chromosome-out (LOCO) cross-validation MSE and out-of-sample R^2
  - Genomic-block bootstrap (1 Mb blocks) 95% confidence intervals for beta_1 (B)
    and beta_4 (B*R), accounting for spatial autocorrelation along chromosomes.

Usage:
  1) Real prepared genomic dataset (see genomics/DATA_SOURCES.md):
       python genomics/section6_2_pilot.py --input-csv path/to/k562_enhancers.csv
  2) Self-test pipeline verification (clearly labeled synthetic dry-run, NOT biological data):
       python genomics/section6_2_pilot.py --demo-synthetic
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

Z_ELEM_COLS = [
    "elem_length",
    "gc_content",
    "neutral_rate",
    "align_qual",
    "chromatin_act",
    "log_dist_tss",
    "direct_targets",
]

Z_GENE_COLS = [
    "gene_loeuf",
    "gene_is_tf",
    "gene_expr_breadth",
    "gene_centrality",
]

ARCH_COLS = ["B_reach", "R_buffering", "B_x_R"]


def standardize_df(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        sd = out[c].std(ddof=0)
        if sd > 1e-12:
            out[c] = (out[c] - out[c].mean()) / sd
        else:
            out[c] = 0.0
    return out


def fit_ols(X: np.ndarray, y: np.ndarray, add_intercept: bool = True) -> np.ndarray:
    if add_intercept:
        X = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def predict_ols(X: np.ndarray, beta: np.ndarray, add_intercept: bool = True) -> np.ndarray:
    if add_intercept:
        X = np.column_stack([np.ones(len(X)), X])
    return X @ beta


def within_gene_demean(df: pd.DataFrame, cols: List[str], y_col: str) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Frisch-Waugh-Lovell (FWL) exact within-target-gene demeaning for genes with >= 2 enhancers.
    Absorbs all invariant properties alpha_{g(e)} of target gene g.
    """
    counts = df.groupby("target_gene")["enhancer_id"].transform("count")
    sub = df.loc[counts >= 2].copy().reset_index(drop=True)
    means_X = sub.groupby("target_gene")[cols].transform("mean")
    means_y = sub.groupby("target_gene")[y_col].transform("mean")
    X_dm = sub[cols] - means_X
    y_dm = (sub[y_col] - means_y).to_numpy(dtype=float)
    return X_dm, y_dm


def loco_cv_global(df: pd.DataFrame, feature_cols: List[str], y_col: str) -> Dict[str, float]:
    """Leave-one-chromosome-out cross-validation for global models."""
    preds = np.zeros(len(df), dtype=float)
    y = df[y_col].to_numpy(dtype=float)
    X_all = df[feature_cols].to_numpy(dtype=float)

    for chrom in df["chrom"].unique():
        test_mask = (df["chrom"] == chrom).to_numpy()
        train_mask = ~test_mask
        beta = fit_ols(X_all[train_mask], y[train_mask], add_intercept=True)
        preds[test_mask] = predict_ols(X_all[test_mask], beta, add_intercept=True)

    mse = float(np.mean((y - preds) ** 2))
    r2 = float(1.0 - np.sum((y - preds) ** 2) / np.sum((y - y.mean()) ** 2))
    return {"loco_mse": round(mse, 5), "loco_r2": round(r2, 5)}


def loco_cv_within_gene(df: pd.DataFrame, feature_cols: List[str], y_col: str) -> Dict[str, float]:
    """
    Leave-one-chromosome-out cross-validation for within-target-gene fixed-effects models.
    Evaluates within-gene residual variance explained on held-out chromosomes (genes live
    on single chromosomes, so held-out chromosomes test generalization to unseen genes).
    """
    counts = df.groupby("target_gene")["enhancer_id"].transform("count")
    sub = df.loc[counts >= 2].copy().reset_index(drop=True)
    X_dm_all, y_dm_all = within_gene_demean(sub, feature_cols, y_col)
    X_arr = X_dm_all.to_numpy(dtype=float)
    preds = np.zeros(len(sub), dtype=float)

    for chrom in sub["chrom"].unique():
        test_mask = (sub["chrom"] == chrom).to_numpy()
        train_mask = ~test_mask
        beta = fit_ols(X_arr[train_mask], y_dm_all[train_mask], add_intercept=False)
        preds[test_mask] = predict_ols(X_arr[test_mask], beta, add_intercept=False)

    mse = float(np.mean((y_dm_all - preds) ** 2))
    r2 = float(1.0 - np.sum((y_dm_all - preds) ** 2) / np.sum((y_dm_all - y_dm_all.mean()) ** 2))
    return {"loco_within_mse": round(mse, 5), "loco_within_r2": round(r2, 5), "n_paired_enhancers": int(len(sub))}


def block_bootstrap_ci(
    df: pd.DataFrame,
    feature_cols: List[str],
    y_col: str,
    within_gene: bool,
    n_boot: int = 200,
    block_bp: int = 1_000_000,
    seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Genomic-block bootstrap (1 Mb blocks) 95% confidence intervals."""
    rng = np.random.default_rng(seed)
    work = df.copy()
    work["_block"] = work["chrom"].astype(str) + ":" + (work["start"] // block_bp).astype(str)

    if within_gene:
        counts = work.groupby("target_gene")["enhancer_id"].transform("count")
        work = work.loc[counts >= 2].copy().reset_index(drop=True)
        X_dm, y_dm = within_gene_demean(work, feature_cols, y_col)
        work_X = X_dm.to_numpy(dtype=float)
        work_y = y_dm
        point_beta = fit_ols(work_X, work_y, add_intercept=False)
        coef_names = list(feature_cols)
    else:
        work_X = work[feature_cols].to_numpy(dtype=float)
        work_y = work[y_col].to_numpy(dtype=float)
        point_beta = fit_ols(work_X, work_y, add_intercept=True)
        coef_names = ["intercept"] + list(feature_cols)

    # Group row indices by genomic block
    block_groups = [idx.to_numpy() for _, idx in work.groupby("_block").groups.items()]
    n_blocks = len(block_groups)
    boot_betas = np.zeros((n_boot, len(point_beta)), dtype=float)

    for b in range(n_boot):
        chosen = rng.integers(0, n_blocks, size=n_blocks)
        idx = np.concatenate([block_groups[c] for c in chosen])
        boot_betas[b] = fit_ols(work_X[idx], work_y[idx], add_intercept=not within_gene)

    out: Dict[str, Dict[str, float]] = {}
    for j, name in enumerate(coef_names):
        if name in ("B_reach", "T_breadth", "R_buffering", "B_x_R"):
            lo, hi = np.percentile(boot_betas[:, j], [2.5, 97.5])
            out[name] = {
                "beta": round(float(point_beta[j]), 4),
                "ci95_low": round(float(lo), 4),
                "ci95_high": round(float(hi), 4),
                "se_boot": round(float(boot_betas[:, j].std(ddof=1)), 4),
            }
    return out


def run_pilot_analysis(df: pd.DataFrame, label: str) -> Dict:
    """Run the full Section 6.2 nested ladder (M0 -> M1 -> M1b -> M2 -> M2b)."""
    work = df.copy()
    # Standardize continuous predictors before forming B x R interaction
    cont_cols = Z_ELEM_COLS + Z_GENE_COLS + ["B_reach", "T_breadth", "R_buffering"]
    work = standardize_df(work, [c for c in cont_cols if c != "gene_is_tf"])
    work["B_x_R"] = work["B_reach"] * work["R_buffering"]

    y_col = "constraint_phyloP"

    m0_cols = Z_ELEM_COLS
    m1_cols = Z_ELEM_COLS + ["T_breadth"] + Z_GENE_COLS
    m2_cols = m1_cols + ARCH_COLS

    m1b_cols = Z_ELEM_COLS + ["T_breadth"]
    m2b_cols = m1b_cols + ARCH_COLS

    res = {
        "dataset_label": label,
        "n_enhancers": int(len(work)),
        "n_genes": int(work["target_gene"].nunique()),
        "n_chroms": int(work["chrom"].nunique()),
        "global_cv": {
            "M0_elem_baseline": loco_cv_global(work, m0_cols, y_col),
            "M1_pleiotropy_plus_gene": loco_cv_global(work, m1_cols, y_col),
            "M2_plus_reach_and_buffering": loco_cv_global(work, m2_cols, y_col),
        },
        "within_gene_fe_cv": {
            "M1b_within_gene_baseline": loco_cv_within_gene(work, m1b_cols, y_col),
            "M2b_within_gene_plus_arch": loco_cv_within_gene(work, m2b_cols, y_col),
        },
        "M2_global_bootstrap_ci": block_bootstrap_ci(work, m2_cols, y_col, within_gene=False),
        "M2b_within_gene_bootstrap_ci": block_bootstrap_ci(work, m2b_cols, y_col, within_gene=True),
    }
    return res


def generate_synthetic_verification_data(mode: str, seed: int = 2026) -> pd.DataFrame:
    """
    Generate synthetic enhancer-gene data strictly for PIPELINE VERIFICATION (NOT real biology):
      - mode='confounded_null': True beta_1 = 0, beta_4 = 0, but enhancers of master TFs
        inherit high B_reach from an UNOBSERVED target-gene essentiality factor.
        Tests whether M2b (within-gene FE) avoids false positives!
      - mode='true_coordination': True beta_1 = +0.35, beta_4 = -0.18 on top of confounders.
        Tests whether M2b cleanly recovers both signs and improves LOCO CV.
    """
    rng = np.random.default_rng(seed)
    n_chroms = 12
    genes_per_chrom = 25
    rows = []
    eid = 0

    for c_idx in range(1, n_chroms + 1):
        chrom = f"chr{c_idx}"
        for g_idx in range(genes_per_chrom):
            gene = f"GENE_{c_idx}_{g_idx}"
            tss = int(g_idx * 2_000_000 + rng.integers(100_000, 900_000))
            is_tf = int(rng.random() < 0.22)
            # Unobserved latent gene importance (stronger for TFs)
            latent_gene_imp = rng.normal(1.2 if is_tf else 0.0, 0.8)
            gene_loeuf = float(np.clip(0.8 - 0.3 * latent_gene_imp + rng.normal(0, 0.25), 0.05, 2.0))
            gene_expr_breadth = float(rng.uniform(0.1, 1.0))
            gene_centrality = float(max(0.0, 1.5 + 0.8 * latent_gene_imp + rng.normal(0, 0.5)))

            n_enh = int(rng.integers(2, 7))
            for _ in range(n_enh):
                eid += 1
                offset = int(rng.integers(-250_000, 250_000))
                start = max(1, tss + offset)
                length = int(rng.integers(250, 1200))
                end = start + length
                gc = float(rng.normal(0.48, 0.06))
                neutral_rate = float(rng.normal(1.0, 0.15))
                align_qual = float(rng.uniform(0.6, 1.0))
                chromatin_act = float(rng.normal(0.0, 1.0))
                log_dist = float(np.log10(abs(offset) + 100.0))
                direct_targets = int(rng.integers(1, 4))
                T_breadth = float(rng.integers(1, 20))

                # Context-specific reach B depends on BOTH latent gene importance and local context
                B_context = rng.normal(0.0, 1.0)
                B_reach = float(0.85 * latent_gene_imp + 0.75 * B_context)
                R_buffering = float(rng.normal(0.0, 1.0))

                # True constraint generation
                y = (
                    0.5
                    + 0.25 * chromatin_act
                    - 0.18 * log_dist
                    + 0.22 * (T_breadth / 10.0)
                    + 0.70 * latent_gene_imp  # Strong gene-level confounder!
                    + rng.normal(0, 0.75)
                )
                if mode == "true_coordination":
                    y += 0.35 * B_context - 0.12 * R_buffering - 0.18 * (B_context * R_buffering)

                rows.append({
                    "enhancer_id": f"E{eid:05d}",
                    "chrom": chrom,
                    "start": start,
                    "end": end,
                    "target_gene": gene,
                    "constraint_phyloP": float(y),
                    "B_reach": B_reach,
                    "T_breadth": T_breadth,
                    "R_buffering": R_buffering,
                    "elem_length": float(length),
                    "gc_content": gc,
                    "neutral_rate": neutral_rate,
                    "align_qual": align_qual,
                    "chromatin_act": chromatin_act,
                    "log_dist_tss": log_dist,
                    "direct_targets": float(direct_targets),
                    "gene_loeuf": gene_loeuf,
                    "gene_is_tf": float(is_tf),
                    "gene_expr_breadth": gene_expr_breadth,
                    "gene_centrality": gene_centrality,
                })
    return pd.DataFrame(rows)


def print_summary(res: Dict) -> None:
    print(f"\n=== {res['dataset_label']} ===")
    print(f"Enhancers: {res['n_enhancers']} | Target genes: {res['n_genes']} | Chromosomes: {res['n_chroms']}")
    g = res["global_cv"]
    w = res["within_gene_fe_cv"]
    print(
        f"Global LOCO R^2:      M0={g['M0_elem_baseline']['loco_r2']:.4f} -> "
        f"M1={g['M1_pleiotropy_plus_gene']['loco_r2']:.4f} -> "
        f"M2={g['M2_plus_reach_and_buffering']['loco_r2']:.4f}"
    )
    print(
        f"Within-Gene LOCO R^2: M1b={w['M1b_within_gene_baseline']['loco_within_r2']:.4f} -> "
        f"M2b={w['M2b_within_gene_plus_arch']['loco_within_r2']:.4f}"
    )
    for model_key, title in [
        ("M2_global_bootstrap_ci", "M2 (Global)"),
        ("M2b_within_gene_bootstrap_ci", "M2b (Within-Gene FE)"),
    ]:
        ci = res[model_key]
        b1 = ci["B_reach"]
        b4 = ci["B_x_R"]
        print(
            f"  {title:<22} beta_1(B)={b1['beta']:+.4f} [{b1['ci95_low']:+.4f}, {b1['ci95_high']:+.4f}]  |  "
            f"beta_4(BxR)={b4['beta']:+.4f} [{b4['ci95_low']:+.4f}, {b4['ci95_high']:+.4f}]"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Section 6.2 comparative genomics pilot pipeline.")
    ap.add_argument("--input-csv", type=str, default=None, help="Path to prepared real enhancer CSV.")
    ap.add_argument("--demo-synthetic", action="store_true", help="Run synthetic pipeline self-test (NOT real data).")
    ap.add_argument("--out-json", type=str, default="results/section6_2_pilot_verification.json")
    args = ap.parse_args()

    if args.input_csv:
        df = pd.read_csv(args.input_csv)
        res = run_pilot_analysis(df, label=f"Empirical dataset: {Path(args.input_csv).name}")
        print_summary(res)
        os.makedirs(Path(args.out_json).parent, exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
    elif args.demo_synthetic:
        print("NOTE: Running SYNTHETIC PIPELINE VERIFICATION ONLY (no real biological data).")
        df_null = generate_synthetic_verification_data("confounded_null", seed=2026)
        df_true = generate_synthetic_verification_data("true_coordination", seed=2027)
        res_null = run_pilot_analysis(df_null, "SYNTHETIC DRY-RUN 1: Confounded Null (true beta_1=0, beta_4=0)")
        res_true = run_pilot_analysis(df_true, "SYNTHETIC DRY-RUN 2: True Coordination (beta_1>0, beta_4<0)")
        print_summary(res_null)
        print_summary(res_true)
        os.makedirs(Path(args.out_json).parent, exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump({"note": "Synthetic pipeline verification only", "confounded_null": res_null, "true_coordination": res_true}, f, indent=2)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
