"""Graphical abstract (paper/figures/graphical_abstract.png/.pdf).

Elsevier: at least 531 x 1328 px (h x w), readable at 5 x 13 cm. Drawn at exactly 13 x 5 cm, so font sizes are
the sizes on screen at that scale.

    python paper/figure_graphical_abstract.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams.update({"font.family": "Arial", "pdf.fonttype": 42})
OUT = Path(__file__).resolve().parent / "figures" / "graphical_abstract.png"
INK, INK2 = "#0b0b0b", "#52514e"
BLUE, GREEN, ORANGE = "#2a78d6", "#1baf7a", "#eb6834"
CM = 1 / 2.54


def box(ax, x, y, w, h, fc, ec, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=ec, lw=lw))


def main() -> None:
    W, H = 13.0, 5.0                                  # cm
    fig = plt.figure(figsize=(W * CM, H * CM))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # 1. Division of labor
    box(ax, 0.15, 2.65, 3.6, 2.15, "#e8f0fb", BLUE)
    ax.text(1.95, 4.45, "LLM agent: judgment", ha="center", fontsize=7, weight="bold", color=BLUE)
    ax.text(1.95, 3.25, "reads messy exports,\ndecodes points, declares\nquantities and units", ha="center",
            fontsize=7, color=INK, linespacing=1.15)
    box(ax, 0.15, 0.2, 3.6, 2.25, "#f4f3f0", INK)
    ax.text(1.95, 2.05, "Domain package: checks", ha="center", fontsize=7, weight="bold", color=INK)
    ax.text(1.95, 0.62, "physics, causal cleaning,\nno look-ahead, strongest\nbaseline, gates, monitoring",
            ha="center", fontsize=7, color=INK, linespacing=1.15)
    ax.add_patch(FancyArrowPatch((1.95, 2.65), (1.95, 2.45), arrowstyle="-|>", mutation_scale=6, color=BLUE))

    # 2. Evaluation
    ax.add_patch(FancyArrowPatch((3.85, 2.5), (4.35, 2.5), arrowstyle="-|>", mutation_scale=8, color=INK2, lw=1))
    box(ax, 4.45, 0.2, 3.3, 4.6, "#ffffff", INK2)
    ax.text(6.1, 4.4, "Real buildings", ha="center", fontsize=7, weight="bold", color=INK)
    ax.text(6.1, 2.35, "pre-specified plan\n\n200 BDG2 buildings:\nday-ahead forecasts,\nM&V pseudo-savings,\n"
            "a year of retraining\n\n+ 72 room and\nsystem tasks", ha="center", va="center", fontsize=7,
            color=INK, linespacing=1.15)

    # 3. Findings
    ax.add_patch(FancyArrowPatch((7.85, 2.5), (8.35, 2.5), arrowstyle="-|>", mutation_scale=8, color=INK2, lw=1))
    findings = [
        (GREEN, "Models beat strong rules,\nincl. TOWT, in 66% of buildings"),
        (INK2, "As M&V baselines: matched,\nbut did not beat, TOWT"),
        (ORANGE, "Shuffled CV passed 32 M&V\nbaselines that later failed"),
        (BLUE, "Monthly retraining beat\ndrift-triggered retraining"),
    ]
    for i, (c, text) in enumerate(findings):
        y = 3.75 - i * 1.17
        box(ax, 8.45, y, 4.4, 1.0, "#ffffff", c, lw=1.0)
        ax.text(10.65, y + 0.5, text, ha="center", va="center", fontsize=7, color=INK, linespacing=1.1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=600)
    fig.savefig(OUT.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
