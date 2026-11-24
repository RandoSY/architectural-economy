"""
Generate publication-grade figures matching the manuscript's visual style
(clean slate/teal/blue/amber palette, crisp typography, no chartjunk).
"""

from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import numpy as np

# Palette harmonized with existing manuscript figures (teal, slate-blue, amber, dark-slate)
COLORS = {
    "dedicated": "#5B6B7A",        # Slate gray
    "inlined": "#5B6B7A",          # Slate gray
    "shared": "#B86B2B",           # Warm amber/ochre (high economy, high blast risk)
    "modular_shared": "#2E6F95",   # Steel blue
    "dual_modular": "#2E6F95",     # Steel blue
    "modular_buffered": "#1F7A68", # Deep teal (Pareto-dominant / buffered)
    "buffered_tmr": "#1F7A68",     # Deep teal
}

LABELS_NET = {
    "dedicated": "Dedicated (no reuse)",
    "shared": "Shared reusable",
    "modular_shared": "Modular shared (d_max=4)",
    "modular_buffered": "Modular + buffered",
}

LABELS_PDP8 = {
    "inlined": "Inlined (dedicated)",
    "shared": "Shared subroutine (JMS)",
    "dual_modular": "Dual-modular (2x MUL)",
    "buffered_tmr": "Buffered TMR (3x MUL)",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#C7D0D9",
    "axes.linewidth": 0.9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.2,
    "grid.color": "#E6EBF0",
    "grid.linewidth": 0.7,
})


def make_synthetic_network_figure(data: dict, out_path: str) -> None:
    summary = data["summary"]
    archs = ["dedicated", "shared", "modular_shared", "modular_buffered"]
    Ks = [r["n_functions"] for r in summary["dedicated"]]

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), dpi=220)
    fig.patch.set_facecolor("white")

    # Panel A: Distinct components vs K
    ax = axes[0]
    for arch in archs:
        means = [r["distinct_components_mean"] for r in summary[arch]]
        sds = [r["distinct_components_sd"] for r in summary[arch]]
        ax.plot(Ks, means, marker="o", lw=2.0, ms=5, color=COLORS[arch], label=LABELS_NET[arch])
        ax.fill_between(
            Ks,
            np.array(means) - np.array(sds),
            np.array(means) + np.array(sds),
            color=COLORS[arch],
            alpha=0.14,
            linewidth=0,
        )
    ax.set_title("A. Implementation cost (components)")
    ax.set_xlabel("Matched output functions (K)")
    ax.set_ylabel("Distinct internal nodes")
    ax.set_xticks(Ks)
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel B: Worst-case & Mean single-node blast radius vs K
    ax = axes[1]
    for arch in archs:
        max_b = [r["motif_max_blast_mean"] for r in summary[arch]]
        mean_b = [r["motif_mean_blast_mean"] for r in summary[arch]]
        ax.plot(Ks, max_b, marker="s", lw=2.0, ms=4.8, color=COLORS[arch], label=LABELS_NET[arch])
        ax.plot(Ks, mean_b, marker="o", lw=1.3, ms=3.8, ls="--", color=COLORS[arch], alpha=0.75)
    ax.set_title("B. Single-node blast radius")
    ax.set_xlabel("Matched output functions (K)")
    ax.set_ylabel("Disrupted outputs (solid: max, dashed: mean)")
    ax.set_xticks(Ks)
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel C: Pareto plane at K = 32 (Distinct components vs Mean blast radius)
    ax = axes[2]
    for arch in archs:
        r = next(x for x in summary[arch] if x["n_functions"] == 32)
        x = r["distinct_components_mean"]
        y = r["motif_mean_blast_mean"]
        xerr = r["distinct_components_sd"]
        yerr = r["motif_mean_blast_sd"]
        ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, fmt="o", ms=8, lw=1.6, capsize=3.5,
            color=COLORS[arch], label=LABELS_NET[arch], zorder=4
        )

    # Direct clean annotations avoiding overlap
    r_ded = next(x for x in summary["dedicated"] if x["n_functions"] == 32)
    r_sha = next(x for x in summary["shared"] if x["n_functions"] == 32)
    r_mod = next(x for x in summary["modular_shared"] if x["n_functions"] == 32)
    r_buf = next(x for x in summary["modular_buffered"] if x["n_functions"] == 32)

    ax.annotate("Dedicated\n(baseline)", (r_ded["distinct_components_mean"], r_ded["motif_mean_blast_mean"]),
                xytext=(-22, 18), textcoords="offset points", fontsize=8, color=COLORS["dedicated"], ha="center")
    ax.annotate("Shared\n(−51% nodes,\n4.3x blast)", (r_sha["distinct_components_mean"], r_sha["motif_mean_blast_mean"]),
                xytext=(14, -22), textcoords="offset points", fontsize=8, color=COLORS["shared"], ha="left")
    ax.annotate("Modular shared\n(caps max=4)", (r_mod["distinct_components_mean"], r_mod["motif_mean_blast_mean"]),
                xytext=(10, 8), textcoords="offset points", fontsize=8, color=COLORS["modular_shared"], ha="left")
    ax.annotate("Modular + buffered\n(dominates dedicated)", (r_buf["distinct_components_mean"], r_buf["motif_mean_blast_mean"]),
                xytext=(-14, 16), textcoords="offset points", fontsize=8, fontweight="bold",
                color=COLORS["modular_buffered"], ha="center")

    # Shaded dominance region (better than dedicated on both axes)
    y_min, y_max = -0.2, 4.8
    ymax_frac = (r_ded["motif_mean_blast_mean"] - y_min) / (y_max - y_min)
    ax.axvspan(38, r_ded["distinct_components_mean"], ymin=0, ymax=ymax_frac,
               color="#1F7A68", alpha=0.06, zorder=1)
    ax.set_xlim(38, 105)
    ax.set_ylim(y_min, y_max)
    ax.set_title("C. Cost–vulnerability Pareto plane (K = 32)")
    ax.set_xlabel("Distinct internal nodes (lower is better)")
    ax.set_ylabel("Mean disrupted outputs (lower is better)")
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Single shared legend at bottom
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(
        "Section 6.1 Controlled Computational Comparison: Synthetic Multi-Output Networks (30 seeds)",
        fontsize=12, fontweight="bold", color="#1C2B36", y=0.99
    )
    plt.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_pdp8_figure(data: dict, out_path: str) -> None:
    bench = data["benchmarks"]
    archs = ["inlined", "shared", "dual_modular", "buffered_tmr"]
    Ns = [r["n_tasks"] for r in bench["inlined"]]

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), dpi=220)
    fig.patch.set_facecolor("white")

    # Panel A: Static code footprint (12-bit words) vs N
    ax = axes[0]
    for arch in archs:
        words = [r["code_words"] for r in bench[arch]]
        ax.plot(Ns, words, marker="o", lw=2.0, ms=5, color=COLORS[arch], label=LABELS_PDP8[arch])
    ax.set_title("A. Static code memory (12-bit words)")
    ax.set_xlabel("Repeated multiply tasks (N)")
    ax.set_ylabel("Code footprint (12-bit words)")
    ax.set_xticks([1, 8, 16, 32, 64])
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.annotate("−70.8% words\nvs. inlined", xy=(64, 477), xytext=(36, 760),
                arrowprops=dict(arrowstyle="->", color=COLORS["shared"], lw=1.1),
                fontsize=8, color=COLORS["shared"], fontweight="bold")

    # Panel B: Non-hanging single-word fault blast radius vs N
    ax = axes[1]
    for arch in archs:
        blast = [r["non_hang_mean_blast_tasks"] for r in bench[arch]]
        ax.plot(Ns, blast, marker="s", lw=2.0, ms=4.8, color=COLORS[arch], label=LABELS_PDP8[arch])
    ax.set_title("B. Routine fault blast radius (non-hanging)")
    ax.set_xlabel("Repeated multiply tasks (N)")
    ax.set_ylabel("Mean tasks corrupted per word fault")
    ax.set_xticks([1, 8, 16, 32, 64])
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel C: Multi-objective trade-off at N = 64 (normalized relative to Inlined = 1.0)
    ax = axes[2]
    r64 = {a: next(r for r in bench[a] if r["n_tasks"] == 64) for a in archs}
    metrics = ["Code words\n(memory)", "Memory cycles\n(time/energy)", "Mean blast\n(non-hang)"]
    x = np.arange(len(metrics))
    width = 0.19

    base_words = r64["inlined"]["code_words"]
    base_cycles = r64["inlined"]["memory_cycles"]
    # For blast radius, express as % of N=64 tasks affected so all axes are crisp ratios
    for idx, arch in enumerate(archs):
        vals = [
            r64[arch]["code_words"] / base_words,
            r64[arch]["memory_cycles"] / base_cycles,
            r64[arch]["non_hang_mean_blast_tasks"] / 64.0 * 2.0,  # scaled: 1.0 = 50% tasks
        ]
        # Wait: cleaner to plot direct log/grouped comparison of 3 clean normalized metrics!
        # Let's plot exact % of max across architectures for crystal-clear comparability:
        pass

    ax.clear()
    # Better Panel C: Direct scatter of Memory Words vs Memory Cycles, marker size = Mean Blast!
    for arch in archs:
        w = r64[arch]["code_words"]
        c = r64[arch]["memory_cycles"] / 1000.0
        b = r64[arch]["non_hang_mean_blast_tasks"]
        size = 60 + b * 6.5
        ax.scatter([w], [c], s=size, color=COLORS[arch], alpha=0.85, edgecolors="#1C2B36", lw=1.0, zorder=4)

    ax.annotate("Inlined\n(1,631 w, 8.9k cyc)\nblast = 0.9",
                (r64["inlined"]["code_words"], r64["inlined"]["memory_cycles"] / 1000.0),
                xytext=(-52, 16), textcoords="offset points", fontsize=7.8, color=COLORS["inlined"], ha="center")
    ax.annotate("Shared (JMS)\n(477 w, 9.2k cyc)\nblast = 55.8",
                (r64["shared"]["code_words"], r64["shared"]["memory_cycles"] / 1000.0),
                xytext=(14, -36), textcoords="offset points", fontsize=7.8, color=COLORS["shared"], ha="left")
    ax.annotate("Dual-modular\n(501 w, 9.2k cyc)\nblast = 28.9",
                (r64["dual_modular"]["code_words"], r64["dual_modular"]["memory_cycles"] / 1000.0),
                xytext=(34, 18), textcoords="offset points", fontsize=7.8, color=COLORS["dual_modular"], ha="left",
                arrowprops=dict(arrowstyle="->", color=COLORS["dual_modular"], lw=0.9))
    ax.annotate("Buffered TMR\n(551 w, 19.7k cyc)\nblast = 2.3 (96.5% masked)",
                (r64["buffered_tmr"]["code_words"], r64["buffered_tmr"]["memory_cycles"] / 1000.0),
                xytext=(16, -6), textcoords="offset points", fontsize=7.8, fontweight="bold",
                color=COLORS["buffered_tmr"], ha="left")

    ax.set_xlim(300, 1850)
    ax.set_ylim(5.5, 22.5)
    ax.set_title("C. Three-way trade-off at N = 64")
    ax.set_xlabel("Code footprint (12-bit words)")
    ax.set_ylabel("Execution cost (thousands of memory cycles)")
    ax.grid(True, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.97, 0.05, "Marker area ∝ fault blast radius", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7.5, color="#5B6B7A", style="italic")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(
        "Section 6.1 Engineering Benchmark: 12-bit DEC PDP-8 Instruction-Level Model",
        fontsize=12, fontweight="bold", color="#1C2B36", y=0.99
    )
    plt.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    with open("results/synthetic_networks.json", "r", encoding="utf-8") as f:
        net_data = json.load(f)
    with open("results/pdp8_benchmark.json", "r", encoding="utf-8") as f:
        pdp8_data = json.load(f)

    make_synthetic_network_figure(net_data, "figures/fig7_synthetic_networks.png")
    make_pdp8_figure(pdp8_data, "figures/fig8_pdp8_benchmark.png")
    print("Saved figures/fig7_synthetic_networks.png and figures/fig8_pdp8_benchmark.png")
