"""Figure 1: the division of labor between the agent and the package (paper/figures/framework.png/.pdf).

Drawn at its printed size (16 cm wide), so the font sizes below are the sizes on the page.

    python paper/figure_framework.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams.update({"font.family": "Arial"})

OUT = Path(__file__).resolve().parent / "figures" / "framework.png"
INK, INK2 = "#0b0b0b", "#52514e"
AGENT, PACKAGE = "#2a78d6", "#0b0b0b"
AGENT_FILL, PACKAGE_FILL = "#e8f0fb", "#f4f3f0"

STAGES = [
    ("Check", "declarations\nvs physics;\nsensor and\nexport faults"),
    ("Prepare", "causal\ncleaning;\nunits;\nresampling"),
    ("Inputs", "shifted by\nthe horizon;\nreach\naudited"),
    ("Evaluate", "time order;\nstrongest\nbaseline;\nbacktest"),
    ("Gate,\nregister", "five gates;\nversions;\nrollback"),
    ("Serve,\nmonitor", "live checks;\ndrift vs test\nerror and\nbaseline"),
    ("Retrain", "champion\nvs\nchallenger"),
]
AGENT_TASKS = [
    (0, 1, "Load any export; decode\npoints; declare quantity\nand unit; fix or accept\neach issue with a reason"),
    (2, 3, "Add inputs and models;\nmark inputs known\nin advance"),
    (4, 4, "Explain;\napproval\nis logged"),
    (5, 6, "Act on alerts:\nfix the sensor\nor retrain"),
]
TITLE, BODY, AGENT_TXT, SMALL = 7, 6, 6.5, 5.5


def box(ax, x, y, w, h, fc, ec, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05", fc=fc, ec=ec, lw=lw))


def arrow(ax, a, b, color=INK2, lw=0.8, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=6, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def main() -> None:
    n = len(STAGES)
    w, gap, x0 = 0.74, 0.13, 0.98          # inches
    xs = [x0 + i * (w + gap) for i in range(n)]
    right = xs[-1] + w
    W, H = right + 0.05, 3.55
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # Lanes and labels (y in inches from the bottom)
    box(ax, 0.02, 2.22, W - 0.04, 1.30, AGENT_FILL, AGENT_FILL)
    box(ax, 0.02, 0.62, W - 0.04, 1.50, PACKAGE_FILL, PACKAGE_FILL)
    ax.text(0.08, 2.87, "LLM agent\n(judgment)", ha="left", va="center", fontsize=TITLE, color=AGENT, weight="bold")
    ax.text(0.08, 1.37, "bemlops\n(same checks\nfor every\nmodel)", ha="left", va="center", fontsize=TITLE,
            color=PACKAGE, weight="bold")
    ax.text(0.08, 2.15, "↓ declarations, decisions", ha="left", va="center", fontsize=SMALL, color=AGENT)
    ax.text(0.08, 2.03, "↑ issues, results, alerts", ha="left", va="center", fontsize=SMALL, color=INK2)

    # Package pipeline
    y0, bh = 0.78, 1.20
    for i, (title, body) in enumerate(STAGES):
        box(ax, xs[i], y0, w, bh, "#ffffff", PACKAGE)
        ax.text(xs[i] + w / 2, y0 + bh - 0.17, title, ha="center", va="center", fontsize=TITLE, color=INK,
                weight="bold", linespacing=1.0)
        ax.text(xs[i] + w / 2, y0 + 0.43, body, ha="center", va="center", fontsize=BODY, color=INK2, linespacing=1.15)
        if i < n - 1:
            arrow(ax, (xs[i] + w, y0 + bh / 2), (xs[i + 1], y0 + bh / 2), color=INK)
    arrow(ax, (xs[6] + w / 2, y0), (xs[3] + w / 2, y0), color=INK, rad=-0.14)
    ax.text((xs[3] + xs[6] + w) / 2, 0.43, "new data: retrain, re-evaluate, re-gate", ha="center", va="center",
            fontsize=SMALL, color=INK2)

    # Agent tasks over the stages they inform
    for a, b, text in AGENT_TASKS:
        left, rgt = xs[a], xs[b] + w
        box(ax, left + 0.02, 2.40, rgt - left - 0.04, 0.98, "#ffffff", AGENT)
        ax.text((left + rgt) / 2, 2.89, text, ha="center", va="center", fontsize=AGENT_TXT, color=INK, linespacing=1.15)
        cx = (left + rgt) / 2
        arrow(ax, (cx - 0.06, 2.40), (cx - 0.06, y0 + bh), color=AGENT)
        arrow(ax, (cx + 0.06, y0 + bh), (cx + 0.06, 2.40), color=INK2)

    # Run record
    box(ax, xs[0], 0.06, right - xs[0], 0.27, "#ffffff", INK2, lw=0.6)
    ax.text((xs[0] + right) / 2, 0.195,
            "Run record: declarations, notes, accepted issues, data fingerprints, settings, metrics, gates, "
            "code version → report, model card, registry", ha="center", va="center", fontsize=SMALL, color=INK)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=600)
    fig.savefig(OUT.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Wrote {OUT} ({W:.2f} x {H:.2f} in)")


if __name__ == "__main__":
    main()
