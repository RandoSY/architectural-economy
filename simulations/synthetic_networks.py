"""
Section 6.1 Controlled Computational Comparison:
Synthetic Multi-Output Regulatory/Combinatorial Networks.

Constructs matched networks implementing the EXACT SAME portfolio of K predefined
input-output functions f_1(x), ..., f_K(x) across four architectural families:
  1. dedicated:        Independent private subcircuits per output (zero sharing).
  2. shared:           Full reuse of common intermediate combinatorial motifs.
  3. modular_shared:   Shared motifs with bounded fan-out (d_max = 4) limiting
                       single-node coordination liability.
  4. modular_buffered: Modular shared motifs + redundant backup ("shadow") nodes
                       for multi-target regulators (analogous to shadow enhancers),
                       using majority/OR fault buffering against loss-of-function.

Evaluates across K in {4, 8, 12, 16, 24, 32}, 30 random seeds, and input noise
levels eta in {0.0, 0.05}:
  - Distinct internal components (node count)
  - Total directed interactions (edge count)
  - Mean activation/execution cost per evaluation
  - Mean & max single-node knockout blast radius (outputs disrupted)
  - System reliability under single-node knockouts and input noise
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np


@dataclass(frozen=True)
class MotifSpec:
    """A 3-input combinatorial motif: (x[a] AND x[b] AND NOT x[c]) or (x[a] AND x[b])."""
    inputs: Tuple[int, int, int]
    kind: str  # "and_not" or "and_or"

    def eval_vec(self, X: np.ndarray) -> np.ndarray:
        a, b, c = self.inputs
        if self.kind == "and_not":
            return (X[:, a] & X[:, b] & (~X[:, c] & 1)).astype(np.int8)
        else:
            return (X[:, a] & (X[:, b] | X[:, c])).astype(np.int8)


@dataclass
class InternalNode:
    node_id: int
    kind: str            # "motif" or "shadow_motif" or "output_gate"
    motif: MotifSpec | None
    parents: List[int]   # indices into internal nodes (for output_gate / buffer)
    output_idx: int | None = None
    is_buffered_pair: bool = False  # True if output combines primary+shadow pairs


class SyntheticNetwork:
    """Directed acyclic combinatorial network supporting exact single-node knockouts."""

    def __init__(self, n_inputs: int, n_outputs: int) -> None:
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.motif_nodes: List[MotifSpec] = []
        # For each output k: list of motif groups; each group is a list of redundant motif node IDs
        # (length 1 if unbuffered, length 2 if primary + shadow backup; group is active if ANY member fires)
        self.output_groups: List[List[List[int]]] = [[] for _ in range(n_outputs)]
        # How output combines its groups: "or" (disjunctive) or "and" (conjunctive)
        self.output_ops: List[str] = ["or"] * n_outputs

    @property
    def n_internal_nodes(self) -> int:
        # Motif nodes + K output integrator nodes
        return len(self.motif_nodes) + self.n_outputs

    @property
    def n_edges(self) -> int:
        # Each motif takes 3 input edges + edges from motif nodes to output integrators
        motif_in_edges = 3 * len(self.motif_nodes)
        motif_to_out = sum(len(grp) for out_grps in self.output_groups for grp in out_grps)
        return motif_in_edges + motif_to_out

    def eval_all(
        self,
        X: np.ndarray,
        knockout_motif: int | None = None,
        knockout_output: int | None = None,
    ) -> Tuple[np.ndarray, float]:
        """
        Evaluate network on input matrix X (shape [B, M]).
        Returns (Y of shape [B, K], mean_active_nodes_per_sample).
        Loss-of-function knockout forces the knocked-out node's output to 0.
        """
        B = X.shape[0]
        n_m = len(self.motif_nodes)
        motif_vals = np.empty((n_m, B), dtype=np.int8)
        for idx, m in enumerate(self.motif_nodes):
            if idx == knockout_motif:
                motif_vals[idx] = 0
            else:
                motif_vals[idx] = m.eval_vec(X)

        Y = np.empty((B, self.n_outputs), dtype=np.int8)
        for k in range(self.n_outputs):
            if k == knockout_output:
                Y[:, k] = 0
                continue
            groups = self.output_groups[k]
            # Each group evaluates OR over its redundant copies (shadow buffering)
            group_vals = []
            for grp in groups:
                if len(grp) == 1:
                    group_vals.append(motif_vals[grp[0]])
                else:
                    v = motif_vals[grp[0]].copy()
                    for mid in grp[1:]:
                        v |= motif_vals[mid]
                    group_vals.append(v)
            if self.output_ops[k] == "or":
                out_v = np.zeros(B, dtype=np.int8)
                for gv in group_vals:
                    out_v |= gv
            else:
                out_v = np.ones(B, dtype=np.int8)
                for gv in group_vals:
                    out_v &= gv
            Y[:, k] = out_v

        # Execution / activation cost: mean number of active internal nodes per input sample
        active_motifs = motif_vals.sum(axis=0).mean() if n_m > 0 else 0.0
        active_outputs = Y.sum(axis=1).mean()
        return Y, float(active_motifs + active_outputs)


def sample_task_portfolio(
    rng: np.random.Generator,
    n_inputs: int,
    n_outputs: int,
    pool_size: int = 16,
    motifs_per_output: int = 2,
) -> Tuple[List[List[MotifSpec]], List[str]]:
    """
    Generate K output functions drawing combinatorial motifs from a structured
    regulatory motif library (modeling shared developmental/signaling primitives).
    """
    pool: List[MotifSpec] = []
    seen: Set[MotifSpec] = set()
    while len(pool) < pool_size:
        a, b, c = rng.choice(n_inputs, size=3, replace=False)
        kind = "and_not" if rng.random() < 0.6 else "and_or"
        spec = MotifSpec((int(a), int(b), int(c)), kind)
        if spec not in seen:
            seen.add(spec)
            pool.append(spec)

    # Zipf-like motif reuse probabilities (some core regulatory motifs reused heavily)
    ranks = np.arange(1, pool_size + 1, dtype=float)
    probs = (1.0 / ranks**0.8)
    probs /= probs.sum()

    output_specs: List[List[MotifSpec]] = []
    output_ops: List[str] = []
    for _ in range(n_outputs):
        chosen_idx = rng.choice(pool_size, size=motifs_per_output, replace=False, p=probs)
        output_specs.append([pool[int(i)] for i in chosen_idx])
        output_ops.append("or" if rng.random() < 0.7 else "and")

    return output_specs, output_ops


def build_network(
    arch: str,
    n_inputs: int,
    output_specs: List[List[MotifSpec]],
    output_ops: List[str],
    max_fanout: int = 4,
) -> SyntheticNetwork:
    """Build one of the four matched network families implementing the exact same functions."""
    K = len(output_specs)
    net = SyntheticNetwork(n_inputs, K)
    net.output_ops = list(output_ops)

    if arch == "dedicated":
        for k in range(K):
            for m in output_specs[k]:
                mid = len(net.motif_nodes)
                net.motif_nodes.append(m)
                net.output_groups[k].append([mid])

    elif arch == "shared":
        registry: Dict[MotifSpec, int] = {}
        for k in range(K):
            for m in output_specs[k]:
                if m not in registry:
                    registry[m] = len(net.motif_nodes)
                    net.motif_nodes.append(m)
                net.output_groups[k].append([registry[m]])

    elif arch == "modular_shared":
        # Reuse motif nodes up to max_fanout downstream outputs, then spawn a fresh module copy
        buckets: Dict[MotifSpec, List[Tuple[int, int]]] = {}  # spec -> [(node_id, fanout)]
        for k in range(K):
            for m in output_specs[k]:
                lst = buckets.setdefault(m, [])
                if not lst or lst[-1][1] >= max_fanout:
                    mid = len(net.motif_nodes)
                    net.motif_nodes.append(m)
                    lst.append((mid, 1))
                else:
                    mid, cnt = lst[-1]
                    lst[-1] = (mid, cnt + 1)
                net.output_groups[k].append([mid])

    elif arch == "modular_buffered":
        # First assign modular shared nodes (fan-out <= max_fanout), then add a shadow
        # backup copy for any shared motif node whose fan-out >= 2
        buckets: Dict[MotifSpec, List[Tuple[int, int]]] = {}
        raw_assignments: List[List[int]] = [[] for _ in range(K)]
        fanout_map: Dict[int, int] = {}

        for k in range(K):
            for m in output_specs[k]:
                lst = buckets.setdefault(m, [])
                if not lst or lst[-1][1] >= max_fanout:
                    mid = len(net.motif_nodes)
                    net.motif_nodes.append(m)
                    lst.append((mid, 1))
                    fanout_map[mid] = 1
                else:
                    mid, cnt = lst[-1]
                    lst[-1] = (mid, cnt + 1)
                    fanout_map[mid] = cnt + 1
                raw_assignments[k].append(mid)

        # Create shadow backup for every motif node shared by >= 2 outputs
        shadow_map: Dict[int, int] = {}
        for mid, cnt in list(fanout_map.items()):
            if cnt >= 2:
                sid = len(net.motif_nodes)
                net.motif_nodes.append(net.motif_nodes[mid])
                shadow_map[mid] = sid

        for k in range(K):
            for mid in raw_assignments[k]:
                if mid in shadow_map:
                    net.output_groups[k].append([mid, shadow_map[mid]])
                else:
                    net.output_groups[k].append([mid])

    else:
        raise ValueError(f"Unknown arch: {arch}")

    return net


def evaluate_network(
    net: SyntheticNetwork,
    X_clean: np.ndarray,
    Y_ref: np.ndarray,
    X_noisy: np.ndarray,
) -> Dict[str, float]:
    """Measure exact resource costs and perturbation blast-radius/reliability metrics."""
    Y_clean, exec_cost = net.eval_all(X_clean)
    assert np.array_equal(Y_clean, Y_ref), "Matched functional equivalence check failed!"

    # Baseline accuracy under input noise alone
    Y_noise_only, _ = net.eval_all(X_noisy)
    noise_acc = float((Y_noise_only == Y_ref).mean())

    # Single-node loss-of-function perturbations across all internal motif nodes
    n_m = len(net.motif_nodes)
    blast_radii: List[int] = []
    ko_accuracies: List[float] = []
    ko_noisy_accuracies: List[float] = []

    for mid in range(n_m):
        Y_ko, _ = net.eval_all(X_clean, knockout_motif=mid)
        # An output is disrupted if its behavior changes on ANY input in the test suite
        disrupted_outputs = int((Y_ko != Y_ref).any(axis=0).sum())
        blast_radii.append(disrupted_outputs)
        ko_accuracies.append(float((Y_ko == Y_ref).mean()))

        Y_ko_noisy, _ = net.eval_all(X_noisy, knockout_motif=mid)
        ko_noisy_accuracies.append(float((Y_ko_noisy == Y_ref).mean()))

    # Also evaluate output-integrator knockouts (each disrupts exactly 1 output)
    all_blast = list(blast_radii)
    all_acc = list(ko_accuracies)
    for k in range(net.n_outputs):
        Y_ko, _ = net.eval_all(X_clean, knockout_output=k)
        disrupted = int((Y_ko != Y_ref).any(axis=0).sum())
        all_blast.append(disrupted)
        all_acc.append(float((Y_ko == Y_ref).mean()))

    return {
        "distinct_components": float(net.n_internal_nodes),
        "motif_components": float(n_m),
        "total_interactions": float(net.n_edges),
        "execution_cost": exec_cost,
        "motif_mean_blast": float(np.mean(blast_radii)),
        "motif_max_blast": float(np.max(blast_radii)),
        "all_node_mean_blast": float(np.mean(all_blast)),
        "all_node_max_blast": float(np.max(all_blast)),
        "motif_ko_reliability": float(np.mean(ko_accuracies)),
        "motif_ko_noisy_reliability": float(np.mean(ko_noisy_accuracies)),
        "motif_zero_blast_rate": float(np.mean([b == 0 for b in blast_radii])),
        "input_noise_reliability": noise_acc,
    }


def run_experiments() -> Dict:
    n_inputs = 12
    task_counts = [4, 8, 12, 16, 24, 32]
    n_seeds = 30
    noise_rate = 0.05
    architectures = ["dedicated", "shared", "modular_shared", "modular_buffered"]

    rng_global = np.random.default_rng(20261123)
    # Fixed representative sample of 256 input states
    X_clean = rng_global.integers(0, 2, size=(256, n_inputs), dtype=np.int8)
    flip_mask = (rng_global.random(X_clean.shape) < noise_rate).astype(np.int8)
    X_noisy = X_clean ^ flip_mask

    summary: Dict[str, List[Dict]] = {a: [] for a in architectures}

    for K in task_counts:
        per_arch_runs: Dict[str, List[Dict[str, float]]] = {a: [] for a in architectures}

        for seed in range(n_seeds):
            rng = np.random.default_rng(10_000 * K + seed)
            output_specs, output_ops = sample_task_portfolio(
                rng, n_inputs=n_inputs, n_outputs=K, pool_size=16, motifs_per_output=2
            )

            # Build dedicated first as ground-truth functional reference
            net_ded = build_network("dedicated", n_inputs, output_specs, output_ops)
            Y_ref, _ = net_ded.eval_all(X_clean)

            for arch in architectures:
                net = net_ded if arch == "dedicated" else build_network(
                    arch, n_inputs, output_specs, output_ops, max_fanout=4
                )
                metrics = evaluate_network(net, X_clean, Y_ref, X_noisy)
                per_arch_runs[arch].append(metrics)

        for arch in architectures:
            runs = per_arch_runs[arch]
            agg: Dict[str, float | int] = {"n_functions": K, "n_seeds": n_seeds}
            for key in runs[0].keys():
                vals = np.array([r[key] for r in runs], dtype=float)
                agg[f"{key}_mean"] = round(float(vals.mean()), 4)
                agg[f"{key}_sd"] = round(float(vals.std(ddof=1)), 4)
            summary[arch].append(agg)

    return {
        "config": {
            "n_inputs": n_inputs,
            "n_test_states": 256,
            "motif_pool_size": 16,
            "motifs_per_output": 2,
            "max_fanout_modular": 4,
            "input_flip_noise": noise_rate,
            "n_seeds": n_seeds,
        },
        "summary": summary,
    }


if __name__ == "__main__":
    out = run_experiments()
    os.makedirs("results", exist_ok=True)
    with open("results/synthetic_networks.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== Section 6.1 Synthetic Network Architecture Comparison (30 seeds) ===")
    for K in [8, 16, 32]:
        print(f"\n--- K = {K} output functions ---")
        print(
            f"{'Architecture':<18} {'Nodes':>7} {'Edges':>7} {'ExecCost':>9} "
            f"{'MeanBlast':>10} {'MaxBlast':>9} {'KO_Rel':>8} {'ZeroBlast':>10}"
        )
        for arch in ["dedicated", "shared", "modular_shared", "modular_buffered"]:
            r = next(x for x in out["summary"][arch] if x["n_functions"] == K)
            print(
                f"{arch:<18} {r['distinct_components_mean']:>7.1f} {r['total_interactions_mean']:>7.1f} "
                f"{r['execution_cost_mean']:>9.2f} {r['motif_mean_blast_mean']:>10.2f} "
                f"{r['motif_max_blast_mean']:>9.2f} {r['motif_ko_reliability_mean']*100:>7.2f}% "
                f"{r['motif_zero_blast_rate_mean']*100:>9.1f}%"
            )
