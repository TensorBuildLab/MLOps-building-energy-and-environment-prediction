"""Figure 1: the division of labour between the agent and the package (paper/figures/framework.png).

    python paper/figure_framework.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "figures" / "framework.png"
INK, INK2 = "#0b0b0b", "#52514e"
AGENT, PACKAGE = "#2a78d6", "#0b0b0b"
AGENT_FILL, PACKAGE_FILL = "#e8f0fb", "#f4f3f0"

STAGES = [
    ("Check", "declarations vs\nphysical ranges;\nexport and sensor\nfaults"),
    ("Prepare", "causal cleaning;\nunit conversion;\nresampling;\nforward-fill inputs"),
    ("Inputs", "lags shifted by\nthe horizon;\naudit of how far\neach input reaches"),
    ("Evaluate", "time-ordered split;\nstrongest no-ML\nbaseline; backtest;\nintervals"),
    ("Gate, register", "five promotion\ngates; versions,\nstages, rollback"),
    ("Serve, monitor", "live data checks;\nskew and time-zone\nchecks; drift\nvs test error"),
    ("Retrain", "champion vs\nchallenger on\nrows neither\nhas seen"),
]
AGENT_TASKS = [
    (0, 1, "Load any export; decode point names;\ndeclare quantity [unit]; decide what each\n"
           "issue means: fix it, or accept with a reason"),
    (2, 3, "Add inputs and models;\nmark what is known ahead"),
    (4, 4, "Explain results;\na person approves"),
    (5, 6, "Act on alerts: fix the\nsensor, or retrain"),
]


def box(ax, x, y, w, h, fc, ec, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=ec, lw=lw))


def arrow(ax, a, b, color=INK2, lw=1.0, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def main() -> None:
    n = len(STAGES)
    w, gap, x0 = 1.5, 0.25, 1.75
    xs = [x0 + i * (w + gap) for i in range(n)]
    right = xs[-1] + w
    fig, ax = plt.subplots(figsize=(12.0, 5.0))
    ax.set_xlim(0, right + 0.15)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    # Lanes and their labels
    box(ax, 0.05, 3.65, right + 0.05, 2.05, AGENT_FILL, AGENT_FILL)
    box(ax, 0.05, 1.0, right + 0.05, 2.4, PACKAGE_FILL, PACKAGE_FILL)
    ax.text(0.15, 4.67, "LLM agent\n(judgment)", ha="left", va="center", fontsize=9, color=AGENT, weight="bold")
    ax.text(0.15, 2.22, "bemlops\n(the same\nchecks every\ntime)", ha="left", va="center", fontsize=9,
            color=PACKAGE, weight="bold")
    ax.text(0.15, 3.62, "↓ declarations, decisions", ha="left", va="center", fontsize=6.5, color=AGENT)
    ax.text(0.15, 3.44, "↑ issues, results, alerts", ha="left", va="center", fontsize=6.5, color=INK2)

    # Package pipeline
    for i, (title, body) in enumerate(STAGES):
        box(ax, xs[i], 1.25, w, 1.95, "#ffffff", PACKAGE)
        ax.text(xs[i] + w / 2, 2.98, title, ha="center", va="center", fontsize=8, color=INK, weight="bold")
        ax.text(xs[i] + w / 2, 2.05, body, ha="center", va="center", fontsize=7, color=INK2, linespacing=1.25)
        if i < n - 1:
            arrow(ax, (xs[i] + w, 2.22), (xs[i + 1], 2.22), color=INK)
    # Retraining loops back to evaluation and the gates
    arrow(ax, (xs[6] + w / 2, 1.25), (xs[3] + w / 2, 1.25), color=INK, rad=-0.18)
    ax.text((xs[3] + xs[6] + w) / 2, 0.62, "new data: retrain, re-evaluate, re-gate", ha="center", va="center",
            fontsize=7, color=INK2)

    # Agent tasks over the stages they inform
    for a, b, text in AGENT_TASKS:
        left, rgt = xs[a], xs[b] + w
        box(ax, left + 0.04, 4.0, rgt - left - 0.08, 1.35, "#ffffff", AGENT)
        ax.text((left + rgt) / 2, 4.67, text, ha="center", va="center", fontsize=6.8, color=INK, linespacing=1.25)
        cx = (left + rgt) / 2
        arrow(ax, (cx - 0.12, 4.0), (cx - 0.12, 3.2), color=AGENT)
        arrow(ax, (cx + 0.12, 3.2), (cx + 0.12, 4.0), color=INK2)

    # Run record
    box(ax, xs[0], 0.02, right - xs[0], 0.42, "#ffffff", INK2, lw=0.8)
    ax.text((xs[0] + right) / 2, 0.23,
            "Run record for every run: declarations, notes, accepted issues, data fingerprints, settings, seeds, "
            "metrics, gates, code version  →  report, model card, registry events",
            ha="center", va="center", fontsize=7, color=INK)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
