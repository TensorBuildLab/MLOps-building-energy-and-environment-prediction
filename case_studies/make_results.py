"""Turn the case-study outputs into the paper's tables (Markdown) and figures (PNG).

Run after case_studies/run_all.py:  python case_studies/make_results.py
Writes paper/tables/*.md and paper/figures/*.png.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / "paper"
TABLES, FIGS = PAPER / "tables", PAPER / "figures"

# Reference categorical palette (first three slots validate for all pairs under colour-vision deficiency).
COLORS = {"ROBOD": "#2a78d6", "Aalborg": "#eb6834", "BDG2": "#1baf7a"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "figure.dpi": 150})

CATEGORY_ORDER = ["Electricity", "Heating/cooling energy", "CO2", "Room temperature", "Humidity", "PM2.5",
                  "Occupancy count", "Occupancy count (virtual sensor)", "Occupancy (yes/no)"]


def category(row) -> str:
    q, tgt = row["quantity"], str(row["target"]).lower()
    if row["task_type"] == "classification":
        return "Occupancy (yes/no)"
    if q == "occupancy_count":
        return "Occupancy count (virtual sensor)" if str(row["horizon"]) == "0" else "Occupancy count"
    if q == "co2":
        return "CO2"
    if q == "zone_air_temperature":
        return "Room temperature"
    if q == "relative_humidity":
        return "Humidity"
    if q == "pm25":
        return "PM2.5"
    if q == "thermal_power" or "chilled" in tgt or "dh__" in tgt:
        return "Heating/cooling energy"
    return "Electricity"


def load_summaries() -> pd.DataFrame:
    frames = []
    for ds in ("robod", "aalborg", "bdg2"):
        f = HERE / ds / "results" / "summary.csv"
        if f.exists():
            frames.append(pd.read_csv(f))
    df = pd.concat(frames, ignore_index=True)
    df["category"] = df.apply(category, axis=1)
    return df


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r.values) + " |")
    return "\n".join(lines) + "\n"


def iqr(s: pd.Series) -> str:
    s = s.dropna()
    if s.empty:
        return "n/a"
    return f"{s.median():.2f} [{s.quantile(.25):.2f}, {s.quantile(.75):.2f}]"


# ----- Table: results by target type ----------------------------------------------------
def table_targets(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cat in CATEGORY_ORDER:
        d = df[df["category"] == cat]
        if d.empty:
            continue
        fit = d[d["status"] == "fitted"]
        cls = cat == "Occupancy (yes/no)"
        if cls:
            err = f"Brier {fit['test_brier'].median():.3f}; balanced acc. {fit['test_balanced_accuracy'].median():.2f}"
        else:
            unit = fit["unit"].dropna().iloc[0] if fit["unit"].notna().any() else ""
            units = fit["unit"].dropna().unique()
            err = (f"MAE {fit['test_mae'].median():.3g} {unit}" if len(units) == 1
                   else f"CV(RMSE) {fit['test_cvrmse_pct'].median():.1f}%")
        rows.append({
            "Target": cat,
            "Datasets": ", ".join(sorted(d["dataset"].unique())),
            "Tasks": len(d),
            "Fitted": len(fit),
            "Skill vs baseline, median [IQR]": iqr(fit["skill"]),
            "Beat baseline (skill > 0)": f"{(fit['skill'] > 0).mean():.0%}",
            "Backtest skill, median": f"{fit['backtest_skill'].median():.2f}"
            if "backtest_skill" in fit and fit["backtest_skill"].notna().any() else "n/a",
            "90% interval coverage, median": f"{fit['interval_coverage'].median():.0%}"
            if "interval_coverage" in fit and fit["interval_coverage"].notna().any() else "n/a",
            "Passed all gates": f"{fit['gates_passed'].mean():.0%}",
            "Typical test error (median)": err,
        })
    return pd.DataFrame(rows)


def fig_skill(df: pd.DataFrame) -> None:
    fit = df[df["status"] == "fitted"].copy()
    cats = [c for c in CATEGORY_ORDER if c in set(fit["category"])]
    fig, ax = plt.subplots(figsize=(7.0, 0.42 * len(cats) + 1.2))
    rng = np.random.default_rng(0)
    for ds, color in COLORS.items():
        d = fit[fit["dataset"] == ds]
        if d.empty:
            continue
        y = d["category"].map({c: i for i, c in enumerate(cats)}) + rng.uniform(-0.18, 0.18, len(d))
        ax.scatter(d["skill"].clip(-0.5, 1), y, s=22, color=color, edgecolor="white", linewidth=0.8,
                   label=f"{ds} ({len(d)} tasks)", zorder=3)
    ax.axvline(0, color=INK2, lw=1, zorder=2)
    ax.set_yticks(range(len(cats)), cats)
    ax.invert_yaxis()
    ax.set_xlim(-0.55, 1.0)
    ax.set_xlabel("Skill vs no-ML baseline on the held-out test period (0 = no better; values below -0.5 shown at -0.5)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "skill_by_target.png", dpi=200)
    plt.close(fig)


# ----- Evaluation protocol -----------------------------------------------------------------
def protocol() -> pd.DataFrame:
    frames = [pd.read_csv(f) for f in (HERE / "robod" / "results" / "protocol_comparison.csv",
                                       HERE / "aalborg" / "results" / "protocol_comparison.csv") if f.exists()]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def table_protocol(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ds, d in list(p.groupby("dataset")) + [("All", p)]:
        under = 1 - d["rmse_shuffled_cv"] / d["rmse_blocked_cv"]
        rows.append({
            "Dataset": ds, "Tasks": len(d),
            "Blocked / shuffled CV RMSE, median [IQR]": iqr(d["optimism_ratio"]),
            "Error understated by shuffling, median": f"{under.median():.0%}",
            "Tasks understated by > 10%": f"{(d['optimism_ratio'] > 1.1).mean():.0%}",
            "R² shuffled vs blocked (median)": f"{d['r2_shuffled_cv'].median():.2f} vs {d['r2_blocked_cv'].median():.2f}",
            "Adding feature selection on all rows (median ratio to shuffled)":
                f"{(d['rmse_shuffled_cv_selection'] / d['rmse_shuffled_cv']).median():.2f}",
        })
    return pd.DataFrame(rows)


def fig_protocol(p: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    for ds, color in COLORS.items():
        d = p[p["dataset"] == ds]
        if d.empty:
            continue
        ax.scatter(d["r2_blocked_cv"], d["r2_shuffled_cv"], s=24, color=color, edgecolor="white",
                   linewidth=0.8, label=f"{ds} ({len(d)} tasks)", zorder=3)
    lo = min(0.0, float(np.nanmin(p[["r2_blocked_cv", "r2_shuffled_cv"]].to_numpy())))
    ax.plot([lo, 1], [lo, 1], color=INK2, lw=1, ls="--", zorder=2)
    ax.text(0.98, 0.02, "points above the line:\nshuffling looks better\nthan it is", transform=ax.transAxes,
            ha="right", va="bottom", color=INK2, fontsize=8)
    ax.set_xlabel("R² with blocked cross-validation")
    ax.set_ylabel("R² with shuffled cross-validation")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "protocol_r2.png", dpi=200)
    plt.close(fig)


# ----- Faults ------------------------------------------------------------------------------
def tables_faults():
    rate = pd.read_csv(HERE / "aalborg" / "results" / "fault_detection_rate.csv")
    det = pd.read_csv(HERE / "aalborg" / "results" / "fault_detection.csv")
    how = det[det["detected"]].groupby("fault")["as"].agg(lambda s: s.str.extract(r"^(\w+):?")[0].mode().iat[0]
                                                         if len(s) else "")
    sev = det[det["detected"]].groupby("fault")["as"].agg(lambda s: s.str.extract(r"\((\w+)\)$")[0].mode().iat[0])
    rate["Detected as"] = rate["fault"].map(how).fillna("")
    rate["Severity"] = rate["fault"].map(sev).fillna("")
    rate["Detection rate"] = rate["detection_rate"].map(lambda v: f"{v:.0%}")
    t1 = rate[["fault", "Detected as", "Severity", "Detection rate"]].rename(columns={"fault": "Planted fault"})
    cost = pd.read_csv(HERE / "aalborg" / "results" / "fault_cost.csv")
    g = cost.groupby("pipeline", sort=False)
    t2 = pd.DataFrame({
        "Pipeline": list(g.groups),
        "RMSE (ppm)": [f"{d['rmse_ppm'].mean():.1f} ± {d['rmse_ppm'].std():.1f}" if len(d) > 1
                       else f"{d['rmse_ppm'].mean():.1f}" for _, d in g],
        "MAE (ppm)": [f"{d['mae_ppm'].mean():.1f} ± {d['mae_ppm'].std():.1f}" if len(d) > 1
                      else f"{d['mae_ppm'].mean():.1f}" for _, d in g],
        "R²": [f"{d['r2'].mean():.2f}" for _, d in g],
        "Runs": [len(d) for _, d in g],
    })
    return t1, t2


# ----- Lifecycle -------------------------------------------------------------------------------
def lifecycle():
    lc = pd.read_csv(HERE / "aalborg" / "results" / "lifecycle.csv")
    tasks = list(dict.fromkeys(lc["task"]))
    fig, axes = plt.subplots(1, len(tasks), figsize=(3.6 * len(tasks), 3.0))
    axes = np.atleast_1d(axes)
    for ax, task in zip(axes, tasks):
        d = lc[lc["task"] == task]
        x = np.arange(len(d))
        ax.plot(x, d["static_skill"], color=COLORS["Aalborg"], lw=2, marker="o", ms=4,
                label="static (never retrained)")
        ax.plot(x, d["production_skill"], color=COLORS["ROBOD"], lw=2, marker="o", ms=4,
                label="monitored + retrained")
        for xi, (_, r) in zip(x, d.iterrows()):
            if bool(r["promoted"]):
                ax.annotate("new version\npromoted", (xi, r["production_skill"]), xytext=(0, -26),
                            textcoords="offset points", ha="center", fontsize=7, color=INK2,
                            arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6})
        ax.axhline(0, color=INK2, lw=0.8)
        ax.set_xticks(x, [m[5:] for m in d["month"]])
        ax.set_xlabel("month of 2023")
        ax.set_title(task, fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel("monthly skill vs persistence")
    axes[0].legend(loc="lower left", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "lifecycle_skill.png", dpi=200)
    plt.close(fig)
    t = lc[["task", "month", "production_version", "static_rmse", "production_rmse", "static_skill",
            "production_skill", "drift_ratio", "retrain_recommended", "promoted", "data_issues"]].copy()
    for c in ("static_rmse", "production_rmse"):
        t[c] = t[c].map(lambda v: f"{v:.3g}")
    for c in ("static_skill", "production_skill", "drift_ratio"):
        t[c] = t[c].map(lambda v: f"{v:.2f}")
    t["data_issues"] = t["data_issues"].fillna("").str.replace(";", ", ")
    return t


# ----- BDG2 --------------------------------------------------------------------------------------
def bdg2(df: pd.DataFrame):
    d = df[df["dataset"] == "BDG2"]
    if d.empty:
        return None
    fit = d[d["status"] == "fitted"]
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ax.hist(fit["test_cvrmse_pct"].clip(upper=100), bins=np.arange(0, 102.5, 5), color=COLORS["BDG2"],
            edgecolor="white", linewidth=1.5, zorder=3)
    ax.axvline(30, color=INK, lw=1, zorder=4)
    ax.text(31, ax.get_ylim()[1] * 0.92, "Guideline 14 hourly limit (30%)", fontsize=8, color=INK)
    ax.set_xlabel("CV(RMSE) on the held-out test period, % (day-ahead, hourly; >100% shown at 100%)")
    ax.set_ylabel("buildings")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(FIGS / "bdg2_cvrmse.png", dpi=200)
    plt.close(fig)
    t = pd.DataFrame([{
        "Buildings": len(d), "Sites": d["site"].nunique(), "Fitted": len(fit),
        "Primary uses": d["primary_use"].nunique(),
        "Skill vs persistence, median [IQR]": iqr(fit["skill"]),
        "CV(RMSE) %, median [IQR]": iqr(fit["test_cvrmse_pct"]),
        "Passed Guideline 14": f"{fit['g14_pass'].mean():.0%}",
        "Passed all gates": f"{fit['gates_passed'].mean():.0%}",
        "Seconds per building, median": f"{fit['seconds'].median():.0f}",
    }])
    return t


def data_issue_table(df: pd.DataFrame) -> pd.DataFrame:
    """Distinct data issues found per dataset (an issue on a column counts once, however many tasks used it)."""
    rows = []
    for ds, d in df.groupby("dataset"):
        ids = set()
        for col in ("errors", "warnings"):
            for v in d[col].dropna():
                ids.update(x for x in str(v).split(";") if x)
        kinds = pd.Series([i.split(":")[0] for i in ids]).value_counts()
        rows.append({"Dataset": ds, **kinds.to_dict()})
    return pd.DataFrame(rows).fillna(0).set_index("Dataset").astype(int).T.reset_index().rename(
        columns={"index": "Issue type"})


def pilot() -> pd.DataFrame:
    """Hidden-period scores of the independent agents, joined with the manual audit of their reports."""
    folder = HERE.parent / "benchmarks" / "pilot" / "results"
    files = sorted(folder.glob("score_T*.csv"))
    if not files:
        return pd.DataFrame()
    s = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    s["condition"] = s["run"].str.split("_").str[1].str.split("-").str[0].map(
        {"A": "agent alone", "C": "agent + bemlops"})
    s["model"] = s["run"].str.split("-").str[-1].str.capitalize()
    audit_file = folder.parent / "audit.csv"
    if audit_file.exists():
        s = s.merge(pd.read_csv(audit_file), on="run", how="left")
    s["actual / expected RMSE"] = s["rmse"] / s["expected_rmse"]
    cols = ["task", "condition", "model", "delivered", "rmse", "persistence_rmse", "skill", "expected_rmse",
            "actual / expected RMSE", "leak_failures", "leak_tests"] + \
           [c for c in ("faults_found", "final_model") if c in s.columns]
    out = s[cols].sort_values(["task", "condition", "model"]).copy()
    for c in ("rmse", "persistence_rmse", "expected_rmse"):
        out[c] = out[c].map(lambda v: f"{v:.3g}" if pd.notna(v) else "")
    for c in ("skill", "actual / expected RMSE"):
        out[c] = out[c].map(lambda v: f"{v:.2f}" if pd.notna(v) else "")
    out["leakage test"] = out.apply(lambda r: f"{int(r['leak_failures'])}/{int(r['leak_tests'])} changed"
                                    if pd.notna(r.get("leak_tests")) else "", axis=1)
    return out.drop(columns=["leak_failures", "leak_tests"])


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    df = load_summaries()
    df.to_csv(TABLES / "all_tasks.csv", index=False)
    (TABLES / "targets.md").write_text(md_table(table_targets(df)), encoding="utf-8")
    (TABLES / "data_issues.md").write_text(md_table(data_issue_table(df)), encoding="utf-8")
    fig_skill(df)
    p = protocol()
    if not p.empty:
        (TABLES / "protocol.md").write_text(md_table(table_protocol(p)), encoding="utf-8")
        fig_protocol(p)
    if (HERE / "aalborg" / "results" / "fault_detection_rate.csv").exists():
        t1, t2 = tables_faults()
        (TABLES / "fault_detection.md").write_text(md_table(t1), encoding="utf-8")
        (TABLES / "fault_cost.md").write_text(md_table(t2), encoding="utf-8")
    if (HERE / "aalborg" / "results" / "lifecycle.csv").exists():
        (TABLES / "lifecycle.md").write_text(md_table(lifecycle()), encoding="utf-8")
    t = bdg2(df)
    if t is not None:
        (TABLES / "bdg2.md").write_text(md_table(t), encoding="utf-8")
    pt = pilot()
    if not pt.empty:
        (TABLES / "pilot.md").write_text(md_table(pt), encoding="utf-8")
    counts = df.groupby("dataset").agg(tasks=("task", "count"), fitted=("status", lambda s: (s == "fitted").sum()))
    print(counts.to_string())
    print(f"Wrote {TABLES} and {FIGS}")


if __name__ == "__main__":
    main()
