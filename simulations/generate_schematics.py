"""
Generate crisp, publication-grade schematic Figures 1 through 6 in a harmonized
slate / steel-blue / teal / amber visual style matching Figures 7 and 8.
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
})

DARK = "#1C2B36"
SLATE = "#5B6B7A"
BLUE = "#2E6F95"
BLUE_BG = "#EDF4F8"
TEAL = "#1F7A68"
TEAL_BG = "#E8F4F1"
AMBER = "#B86B2B"
AMBER_BG = "#FDF3E7"
GRAY_BG = "#F3F6F8"
GRAY_EDGE = "#B6C2CC"


def draw_box(ax, x, y, w, h, title, subtitle="", fc=GRAY_BG, ec=GRAY_EDGE,
             title_color=DARK, sub_color=SLATE, title_size=10.5, sub_size=8.3, lw=1.3, radius=0.12):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center",
                fontsize=sub_size, color=sub_color, zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=title_color, zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color=SLATE, lw=1.4, ls="-", rad=0.0, ms=12):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=ms,
        color=color, linewidth=lw, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}", zorder=2
    )
    ax.add_patch(arr)


def fig1_pdp8_arch(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.1), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")

    ax.text(5.0, 3.15, "PDP-8: a compact stored-program architecture",
            ha="center", va="center", fontsize=12, fontweight="bold", color=DARK)

    # Top 3 blocks
    draw_box(ax, 0.4, 1.85, 2.55, 0.95, "Core memory", "4,096 x 12-bit words")
    draw_box(ax, 3.72, 1.85, 2.55, 0.95, "CPU", "AC  •  Link (L)  •  PC")
    draw_box(ax, 7.05, 1.85, 2.55, 0.95, "Peripheral I/O", "Device-select operations")

    draw_arrow(ax, 2.98, 2.45, 3.69, 2.45)
    draw_arrow(ax, 3.69, 2.20, 2.98, 2.20)
    draw_arrow(ax, 6.30, 2.45, 7.02, 2.45)
    draw_arrow(ax, 7.02, 2.20, 6.30, 2.20)

    ax.text(5.0, 1.50, "Eight primary opcode classes", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color=SLATE)

    opcodes = ["AND", "TAD", "ISZ", "DCA", "JMS", "JMP", "IOT", "OPR"]
    x0 = 0.42
    w = 1.03
    gap = 0.13
    for i, op in enumerate(opcodes):
        is_ext = op in ("IOT", "OPR")
        draw_box(
            ax, x0 + i * (w + gap), 0.78, w, 0.48, op,
            fc=TEAL_BG if is_ext else BLUE_BG,
            ec=TEAL if is_ext else BLUE,
            title_color=TEAL if is_ext else BLUE,
            title_size=10, lw=1.1, radius=0.08
        )

    ax.text(5.0, 0.42, "Elementary operations  →  instruction sequences  →  reusable subroutines",
            ha="center", va="center", fontsize=9.8, fontweight="bold", color=DARK)
    ax.text(5.0, 0.14, "Conceptual block diagram based on DEC (1967) [25,26]; not an electrical schematic.",
            ha="center", va="center", fontsize=8.0, color=SLATE, style="italic")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def fig2_hierarchies(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.0), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")

    # Divider
    ax.plot([5.0, 5.0], [0.3, 2.95], color=GRAY_EDGE, lw=1.0)

    # Left: Bacterial transcription network (fan-out)
    ax.text(2.45, 2.95, "Bacterial transcription network", ha="center", va="center",
            fontsize=11, fontweight="bold", color=TEAL)
    top_l = [(1.1, 2.42), (3.8, 2.42)]
    mid_l = [(0.9, 1.55), (2.0, 1.55), (2.9, 1.55), (4.0, 1.55)]
    bot_l = [(0.55 + i * 0.54, 0.68) for i in range(8)]

    edges_l = [
        (top_l[0], mid_l[0]), (top_l[0], mid_l[1]),
        (top_l[1], mid_l[2]), (top_l[1], mid_l[3]),
        (mid_l[0], bot_l[0]), (mid_l[0], bot_l[1]),
        (mid_l[1], bot_l[2]), (mid_l[1], bot_l[3]),
        (mid_l[2], bot_l[4]), (mid_l[2], bot_l[5]),
        (mid_l[3], bot_l[6]), (mid_l[3], bot_l[7]),
    ]
    for (x1, y1), (x2, y2) in edges_l:
        draw_arrow(ax, x1, y1 - 0.09, x2, y2 + 0.11, color=TEAL, lw=1.35, ms=10)
    for pt in top_l + mid_l + bot_l:
        ax.scatter(*pt, s=75, color=TEAL, zorder=4)
    ax.text(2.45, 0.25, "Fan-out to regulated targets", ha="center", va="center",
            fontsize=9.2, color=SLATE)

    # Right: Linux function-call graph (fan-in)
    ax.text(7.55, 2.95, "Linux function-call graph", ha="center", va="center",
            fontsize=11, fontweight="bold", color=BLUE)
    top_r = [(5.65 + i * 0.54, 2.42) for i in range(8)]
    mid_r = [(5.95, 1.55), (7.0, 1.55), (8.1, 1.55), (9.15, 1.55)]
    bot_r = [(6.5, 0.68), (8.6, 0.68)]

    edges_r = [
        (top_r[0], mid_r[0]), (top_r[1], mid_r[0]),
        (top_r[2], mid_r[1]), (top_r[3], mid_r[1]),
        (top_r[4], mid_r[2]), (top_r[5], mid_r[2]),
        (top_r[6], mid_r[3]), (top_r[7], mid_r[3]),
        (mid_r[0], bot_r[0]), (mid_r[1], bot_r[0]),
        (mid_r[2], bot_r[1]), (mid_r[3], bot_r[1]),
    ]
    for (x1, y1), (x2, y2) in edges_r:
        draw_arrow(ax, x1, y1 - 0.09, x2, y2 + 0.11, color=BLUE, lw=1.35, ms=10)
    for pt in top_r + mid_r + bot_r:
        ax.scatter(*pt, s=75, color=BLUE, zorder=4)
    ax.text(7.55, 0.25, "Fan-in to reusable routines", ha="center", va="center",
            fontsize=9.2, color=SLATE)

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def fig3_molecular_logic(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.7), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.9)
    ax.axis("off")

    ax.text(1.4, 2.68, "Regulatory inputs", ha="center", va="center", fontsize=9.8, fontweight="bold", color=SLATE)
    ax.text(5.2, 2.68, "Illustrative logic", ha="center", va="center", fontsize=9.8, fontweight="bold", color=SLATE)
    ax.text(8.9, 2.68, "Output", ha="center", va="center", fontsize=9.8, fontweight="bold", color=SLATE)

    draw_box(ax, 0.35, 1.90, 2.1, 0.45, "Activator A", fc=GRAY_BG, ec=GRAY_EDGE, title_size=9.5)
    draw_box(ax, 0.35, 1.25, 2.1, 0.45, "Activator B", fc=GRAY_BG, ec=GRAY_EDGE, title_size=9.5)
    draw_box(ax, 0.35, 0.55, 2.1, 0.45, "Repressor C", fc=GRAY_BG, ec=GRAY_EDGE, title_size=9.5)

    draw_box(ax, 3.4, 1.22, 2.2, 1.15, "A AND B", "Joint activation",
             fc=TEAL_BG, ec=TEAL, title_size=10.5, sub_size=8.3)
    draw_box(ax, 3.4, 0.55, 2.2, 0.45, "NOT C", fc=AMBER_BG, ec=AMBER, title_size=10)

    draw_box(ax, 6.5, 0.95, 1.25, 0.85, "AND", fc=BLUE_BG, ec=BLUE, title_size=10.5)
    draw_box(ax, 8.25, 0.98, 1.4, 0.80, "Gene", "ON / OFF", fc=TEAL_BG, ec=TEAL, title_size=10)

    draw_arrow(ax, 2.48, 2.12, 3.37, 2.12, color=TEAL)
    draw_arrow(ax, 2.48, 1.47, 3.37, 1.47, color=TEAL)
    draw_arrow(ax, 2.48, 0.77, 3.37, 0.77, color=AMBER)

    # Stepped lines from A AND B and NOT C into AND
    ax.plot([5.63, 6.05, 6.05], [1.75, 1.75, 1.52], color=SLATE, lw=1.4)
    draw_arrow(ax, 6.05, 1.52, 6.47, 1.52, color=SLATE)
    ax.plot([5.63, 6.05, 6.05], [0.77, 0.77, 1.20], color=SLATE, lw=1.4)
    draw_arrow(ax, 6.05, 1.20, 6.47, 1.20, color=SLATE)

    draw_arrow(ax, 7.78, 1.38, 8.22, 1.38, color=SLATE)

    ax.text(5.0, 0.16, "Idealized rule: A ∧ B ∧ ¬C; real cis-regulatory responses are graded, stochastic, and context-dependent.",
            ha="center", va="center", fontsize=8.2, color=SLATE, style="italic")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def fig4_chromatin_loop(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.7), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.9)
    ax.axis("off")

    ax.text(5.0, 2.68, "Spatial proximity modulates opportunities for regulatory interaction",
            ha="center", va="center", fontsize=11, fontweight="bold", color=DARK)

    # Double-stranded DNA baseline
    ax.plot([0.5, 3.55], [0.88, 0.88], color=BLUE, lw=2.6)
    ax.plot([0.5, 3.55], [0.74, 0.74], color=BLUE, lw=1.4)
    ax.plot([6.25, 9.5], [0.88, 0.88], color=BLUE, lw=2.6)
    ax.plot([6.25, 9.5], [0.74, 0.74], color=BLUE, lw=1.4)

    # Smooth chromatin loop connecting the Enhancer and Promoter DNA strands cleanly
    t = np.linspace(0, 1, 200)
    # Cubic Bezier curves for outer and inner double-stranded DNA loop
    def bezier(p0, p1, p2, p3, t):
        return (
            (1 - t) ** 3 * p0
            + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t ** 2 * p2
            + t ** 3 * p3
        )

    xo = bezier(3.92, 2.35, 7.50, 5.93, t)
    yo = bezier(0.96, 2.78, 2.78, 0.96, t)
    xi = bezier(4.04, 2.65, 7.20, 5.81, t)
    yi = bezier(0.96, 2.62, 2.62, 0.96, t)
    ax.plot(xo, yo, color=BLUE, lw=2.5, zorder=1)
    ax.plot(xi, yi, color=BLUE, lw=1.3, zorder=1)
    ax.text(4.92, 2.02, "Chromatin loop", ha="center", va="center", fontsize=9.2, color=BLUE, fontweight="bold")

    # Regulatory complex
    draw_box(ax, 3.65, 1.25, 2.5, 0.50, "Regulatory complex", fc=GRAY_BG, ec=GRAY_EDGE, title_size=9.5)
    draw_arrow(ax, 4.35, 1.23, 4.05, 1.00, color=SLATE, ls="--", ms=10)
    draw_arrow(ax, 5.45, 1.23, 5.75, 1.00, color=SLATE, ls="--", ms=10)

    # Enhancer, Promoter, Gene blocks
    draw_box(ax, 3.45, 0.62, 1.05, 0.36, "", fc="#E5A864", ec=AMBER, lw=1.4, radius=0.06)
    ax.text(3.975, 0.38, "Enhancer", ha="center", va="center", fontsize=9.5, fontweight="bold", color=AMBER)

    draw_box(ax, 5.35, 0.62, 1.05, 0.36, "", fc="#A7C8DE", ec=BLUE, lw=1.4, radius=0.06)
    ax.text(5.875, 0.38, "Promoter", ha="center", va="center", fontsize=9.5, fontweight="bold", color=BLUE)

    draw_box(ax, 6.85, 0.62, 1.55, 0.36, "", fc="#A7D4C9", ec=TEAL, lw=1.4, radius=0.06)
    ax.text(7.625, 0.38, "Gene", ha="center", va="center", fontsize=9.5, fontweight="bold", color=TEAL)

    ax.text(5.0, 0.10, "Schematic, not to scale; 3D contact increases interaction probability but does not guarantee transcription.",
            ha="center", va="center", fontsize=8.0, color=SLATE, style="italic")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def fig5_distributed_control(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.95), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.15)
    ax.axis("off")

    ax.text(5.0, 2.92, "Distributed genomic control: information and machinery interact",
            ha="center", va="center", fontsize=11, fontweight="bold", color=DARK)

    draw_box(ax, 0.35, 1.78, 2.55, 0.80, "Signals & feedback", "Cellular / environmental",
             fc=GRAY_BG, ec=GRAY_EDGE, title_size=9.8)
    draw_box(ax, 3.65, 1.78, 2.65, 0.80, "Regulatory sequences", "Enhancers • promoters",
             fc=TEAL_BG, ec=TEAL, title_size=9.8)
    draw_box(ax, 7.05, 1.78, 2.60, 0.80, "Chromatin & RNA", "Accessibility • state",
             fc=TEAL_BG, ec=TEAL, title_size=9.8)

    draw_box(ax, 3.65, 0.68, 2.65, 0.78, "Execution machinery", "Factors • polymerases",
             fc=BLUE_BG, ec=BLUE, title_size=9.8)
    draw_box(ax, 7.05, 0.68, 2.60, 0.78, "Cellular functions", "Expression • phenotype",
             fc=BLUE_BG, ec=BLUE, title_size=9.8)

    draw_arrow(ax, 2.93, 2.18, 3.62, 2.18)
    draw_arrow(ax, 6.33, 2.28, 7.02, 2.28)
    draw_arrow(ax, 7.02, 2.06, 6.33, 2.06)
    draw_arrow(ax, 4.97, 1.75, 4.97, 1.49)
    draw_arrow(ax, 8.35, 1.75, 8.35, 1.49)
    draw_arrow(ax, 6.33, 1.07, 7.02, 1.07)

    # Bottom feedback loop from Cellular functions -> Signals & feedback
    ax.plot([8.35, 8.35, 1.62], [0.65, 0.35, 0.35], color=SLATE, lw=1.4)
    draw_arrow(ax, 1.62, 0.35, 1.62, 1.75)

    ax.text(5.0, 0.10, "No central kernel: control emerges from coupled molecular processes.",
            ha="center", va="center", fontsize=8.3, color=SLATE, style="italic")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def fig6_coordination_conservation(out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.05), dpi=240)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")

    ax.plot([5.0, 5.0], [0.35, 3.0], color=GRAY_EDGE, lw=1.0)

    # Panel A: Component substitution
    ax.text(2.45, 2.95, "A • Component substitution", ha="center", va="center",
            fontsize=11, fontweight="bold", color=DARK)
    c1 = patches.Circle((2.45, 2.38), 0.25, facecolor=TEAL, edgecolor=TEAL, zorder=4)
    ax.add_patch(c1)
    ax.text(2.45, 2.38, "R", ha="center", va="center", fontsize=11, fontweight="bold", color="white", zorder=5)

    draw_box(ax, 0.35, 1.25, 1.2, 0.45, "Module 1", fc=BLUE_BG, ec=BLUE, title_color=BLUE, title_size=9)
    draw_box(ax, 1.85, 1.25, 1.2, 0.45, "Module 2'", fc=TEAL_BG, ec=TEAL, title_color=TEAL, title_size=9, lw=1.6)
    draw_box(ax, 3.35, 1.25, 1.2, 0.45, "Module 3", fc=BLUE_BG, ec=BLUE, title_color=BLUE, title_size=9)

    for mx in [0.95, 2.45, 3.95]:
        draw_arrow(ax, 2.45, 2.12, mx, 1.73, color=SLATE)
        draw_arrow(ax, mx, 1.22, mx, 0.80, color=SLATE)
        ax.scatter(mx, 0.65, s=110, color=TEAL, zorder=4)
    ax.text(2.45, 0.36, "Outputs preserved if interface holds", ha="center", va="center", fontsize=9, color=SLATE)

    # Panel B: Shared dependency disruption
    ax.text(7.55, 2.95, "B • Shared dependency disruption", ha="center", va="center",
            fontsize=11, fontweight="bold", color=DARK)
    c2 = patches.Circle((7.55, 2.38), 0.25, facecolor="white", edgecolor=AMBER, lw=2.0, zorder=4)
    ax.add_patch(c2)
    ax.text(7.55, 2.38, "×", ha="center", va="center", fontsize=16, fontweight="bold", color=AMBER, zorder=5)

    draw_box(ax, 5.45, 1.25, 1.2, 0.45, "Module 1", fc=GRAY_BG, ec=GRAY_EDGE, title_color=SLATE, title_size=9)
    draw_box(ax, 6.95, 1.25, 1.2, 0.45, "Module 2", fc=GRAY_BG, ec=GRAY_EDGE, title_color=SLATE, title_size=9)
    draw_box(ax, 8.45, 1.25, 1.2, 0.45, "Module 3", fc=GRAY_BG, ec=GRAY_EDGE, title_color=SLATE, title_size=9)

    for mx in [6.05, 7.55, 9.05]:
        draw_arrow(ax, 7.55, 2.12, mx, 1.73, color=SLATE, ls="--")
        draw_arrow(ax, mx, 1.22, mx, 0.80, color=SLATE, ls="--")
        ax.scatter(mx, 0.65, s=110, color="#D4DCE3", zorder=4)
    ax.text(7.55, 0.36, "Several outputs at risk", ha="center", va="center", fontsize=9, color=SLATE)

    ax.text(5.0, 0.10, "Illustrative hypothesis informed by [20,28,29]; buffering and context modulate perturbation consequences.",
            ha="center", va="center", fontsize=8.0, color=SLATE, style="italic")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=240, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    fig1_pdp8_arch("figures/fig1_pdp8_arch.png")
    fig2_hierarchies("figures/fig2_hierarchies.png")
    fig3_molecular_logic("figures/fig3_molecular_logic.png")
    fig4_chromatin_loop("figures/fig4_chromatin_loop.png")
    fig5_distributed_control("figures/fig5_distributed_control.png")
    fig6_coordination_conservation("figures/fig6_coordination_conservation.png")
    print("Generated figures/fig1..fig6 cleanly.")
