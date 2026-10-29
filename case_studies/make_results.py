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


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    """Wilson score interval for a proportion [Wilson 1927]."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def share(mask) -> str:
    """'k/n (p%, 95% CI lo-hi%)' for a boolean series."""
    m = pd.Series(mask).dropna().astype(bool)
    k, n = int(m.sum()), len(m)
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.0%}; {lo:.0%}–{hi:.0%})"


def dm_results() -> pd.DataFrame:
    f = HERE / "dm_tests.csv"
    return pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["task", "model_better_p05"])


# ----- Table: results by target type ----------------------------------------------------
def table_targets(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    dm = dm_results().set_index("task")["model_better_p05"] if not dm_results().empty else pd.Series(dtype=bool)
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
            "Skill, median [IQR]": iqr(fit["skill"]),
            "Model chosen over baseline": f"{(fit['chosen'] != fit['baseline']).sum()}/{len(fit)}",
            "Skill > 0": share(fit["skill"] > 0),
            "Better than baseline, DM p < 0.05": share(fit["task"].map(dm).fillna(False))
            if len(dm) else "n/a",
            "Backtest skill, median": f"{fit['backtest_skill'].median():.2f}"
            if "backtest_skill" in fit and fit["backtest_skill"].notna().any() else "n/a",
            "90% interval coverage, median [range]":
                f"{fit['interval_coverage'].median():.0%} [{fit['interval_coverage'].min():.0%}–"
                f"{fit['interval_coverage'].max():.0%}]"
            if "interval_coverage" in fit and fit["interval_coverage"].notna().any() else "n/a",
            "Passed all gates": share(fit["gates_passed"]),
            "Typical test error (median)": err,
        })
    return pd.DataFrame(rows)


def table_datasets(df: pd.DataFrame) -> pd.DataFrame:
    """Headline proportions per dataset, with Wilson intervals."""
    dm = dm_results().set_index("task")["model_better_p05"] if not dm_results().empty else pd.Series(dtype=bool)
    rows = []
    for ds, d in list(df.groupby("dataset", sort=False)) + [("All", df)]:
        fit = d[d["status"] == "fitted"]
        g14 = fit["g14_pass"].dropna() if "g14_pass" in fit else pd.Series(dtype=bool)
        rows.append({
            "Dataset": ds, "Tasks": len(d), "Fitted": len(fit),
            "Skill, median [IQR]": iqr(fit["skill"]),
            "Baseline kept (chosen on validation)": f"{(fit['chosen'] == fit['baseline']).sum()}/{len(fit)}",
            "Skill > 0": share(fit["skill"] > 0),
            "Better than baseline, DM p < 0.05": share(fit["task"].map(dm).fillna(False)) if len(dm) else "n/a",
            "Guideline 14 met (energy tasks)": share(g14) if len(g14) else "n/a",
            "Passed all gates": share(fit["gates_passed"]),
            "Test and backtest skill disagree in sign": share(
                (np.sign(fit["skill"]) != np.sign(fit["backtest_skill"]))[fit["backtest_skill"].notna()])
            if fit["backtest_skill"].notna().any() else "n/a",
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
            "Shuffled + selection on all rows / shuffled, median":
                f"{(d['rmse_shuffled_cv_selection'] / d['rmse_shuffled_cv']).median():.2f}",
            "Time-ordered holdout / blocked CV, median [range]":
                (lambda r: f"{r.median():.2f} [{r.min():.2f}–{r.max():.2f}]")(
                    d["rmse_time_ordered_holdout"] / d["rmse_blocked_cv"]),
        })
    return pd.DataFrame(rows)


def table_protocol_tasks(p: pd.DataFrame) -> pd.DataFrame:
    """Per-task protocol results (appendix)."""
    t = p[["dataset", "task", "rmse_shuffled_cv", "rmse_shuffled_cv_selection", "rmse_blocked_cv",
           "rmse_time_ordered_holdout", "optimism_ratio"]].copy()
    for c in t.columns[2:]:
        t[c] = t[c].map(lambda v: f"{v:.3g}")
    return t.rename(columns={"rmse_shuffled_cv": "Shuffled CV", "rmse_shuffled_cv_selection": "Shuffled + selection",
                             "rmse_blocked_cv": "Blocked CV", "rmse_time_ordered_holdout": "Time-ordered holdout",
                             "optimism_ratio": "Blocked / shuffled"})


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
    tests_file = HERE / "aalborg" / "results" / "fault_tests.csv"
    t3 = None
    if tests_file.exists():
        t3 = pd.read_csv(tests_file)
        t3["comparison"] = t3["comparison"].str.replace("faulty data, ", "").str.replace(" vs bemlops",
                                                                                          " minus bemlops")
        t3["median_difference"] = t3["median_difference"].map(lambda v: f"{v:+.2f}")
        t3["p_value"] = t3["p_value"].map(lambda v: f"{v:.3f}")
        t3 = t3.rename(columns={"comparison": "Paired difference (same seed)", "metric": "Metric",
                                "median_difference": "Median (ppm)", "p_value": "Wilcoxon p",
                                "n_pairs": "Pairs"})
    return t1, t2, t3


# ----- Lifecycle -------------------------------------------------------------------------------
LIFECYCLE_ARMS = {  # column -> (label, colour, line style)
    "static_rmse": ("static (never retrained)", COLORS["Aalborg"], "-"),
    "naive_rmse": ("retrained every month", COLORS["BDG2"], "-"),
    "production_rmse": ("monitored, gated retraining", COLORS["ROBOD"], "-"),
    "persistence_rmse": ("persistence", INK2, "--"),
}


def lifecycle_frame() -> pd.DataFrame:
    """Monthly RMSE of every arm on the same month, plus the causal fallback-rule counterfactual.

    Fallback rule (added to the drift check after this experiment): in month m, serve persistence
    instead of the production model if the production model was worse than persistence in month m-1.
    The decision uses only month m-1, so it could have been taken in operation.
    """
    lc = pd.read_csv(HERE / "aalborg" / "results" / "lifecycle.csv")
    lc["persistence_rmse"] = lc["production_persistence_rmse"]
    naive = HERE / "aalborg" / "results" / "lifecycle_naive.csv"
    if naive.exists():
        lc = lc.merge(pd.read_csv(naive)[["task", "month", "naive_rmse", "naive_persistence_rmse"]],
                      on=["task", "month"], how="left")
    else:
        lc["naive_rmse"] = np.nan
    parts = []
    for _, d in lc.groupby("task", sort=False):
        d = d.sort_values("month").copy()
        worse_last_month = (d["production_skill"] < 0).shift(1, fill_value=False).astype(bool)
        d["fallback_uses_persistence"] = worse_last_month
        d["fallback_rmse"] = np.where(worse_last_month, d["persistence_rmse"], d["production_rmse"])
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def lifecycle():
    lc = lifecycle_frame()
    tasks = list(dict.fromkeys(lc["task"]))
    fig, axes = plt.subplots(1, len(tasks), figsize=(3.6 * len(tasks), 3.0))
    axes = np.atleast_1d(axes)
    for ax, task in zip(axes, tasks):
        d = lc[lc["task"] == task]
        x = np.arange(len(d))
        for col, (label, color, ls) in LIFECYCLE_ARMS.items():
            if d[col].notna().any():
                ax.plot(x, d[col], color=color, lw=2 if ls == "-" else 1.2, ls=ls, marker="o" if ls == "-" else None,
                        ms=4, label=label, zorder=3 if col == "production_rmse" else 2)
        for xi, (_, r) in zip(x, d.iterrows()):
            if bool(r["promoted"]):
                ax.annotate("promoted", (xi + 0.5, ax.get_ylim()[1]), xytext=(0, -2), textcoords="offset points",
                            ha="center", va="top", fontsize=7, color=INK2)
                ax.axvline(xi + 0.5, color=GRID, lw=1.2, zorder=1)
        ax.set_xticks(x, [m[5:] for m in d["month"]])
        ax.set_xlabel("month of 2023")
        unit = "kW" if "heating" in task.lower() else "ppm"
        ax.set_ylabel(f"monthly RMSE ({unit})")
        ax.set_title(task, fontsize=9, color=INK, loc="left")
    axes[0].legend(loc="upper left", frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "lifecycle_rmse.png", dpi=200)
    plt.close(fig)
    t = lc[["task", "month", "production_version", "static_rmse", "naive_rmse", "production_rmse",
            "persistence_rmse", "fallback_rmse", "drift_ratio", "retrain_recommended", "promoted"]].copy()
    for c in ("static_rmse", "naive_rmse", "production_rmse", "persistence_rmse", "fallback_rmse"):
        t[c] = t[c].map(lambda v: f"{v:.3g}" if pd.notna(v) else "")
    t["fallback_rmse"] = [f"{v} (P)" if p else v for v, p in zip(t["fallback_rmse"], lc["fallback_uses_persistence"])]
    t["drift_ratio"] = t["drift_ratio"].map(lambda v: f"{v:.2f}")
    t = t.rename(columns={"production_version": "Version", "static_rmse": "Static", "naive_rmse": "Monthly retrain",
                          "production_rmse": "Monitored + gated", "persistence_rmse": "Persistence",
                          "fallback_rmse": "Gated + fallback rule", "drift_ratio": "Drift ratio",
                          "retrain_recommended": "Retrain advised", "promoted": "Promoted"})
    summary = []
    for task, d in lc.groupby("task", sort=False):
        row = {"Task": task}
        for col, label in (("static_rmse", "Static"), ("naive_rmse", "Monthly retrain"),
                           ("production_rmse", "Monitored + gated"), ("persistence_rmse", "Persistence"),
                           ("fallback_rmse", "Gated + fallback rule")):
            row[label] = f"{d[col].mean():.3g}" if d[col].notna().any() else ""
        row["Months monitored model beat persistence"] = f"{(d['production_rmse'] < d['persistence_rmse']).sum()}/{len(d)}"
        row["Retrains (promoted)"] = f"{int(d['retrain_recommended'].sum())} ({int(d['promoted'].sum())})"
        row["Monthly fits, naive arm"] = int(d["naive_rmse"].notna().sum())
        summary.append(row)
    return t, pd.DataFrame(summary)


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
        "Skill vs strongest baseline, median [IQR]": iqr(fit["skill"]),
        "Skill > 0": share(fit["skill"] > 0),
        "CV(RMSE) %, median [IQR]": iqr(fit["test_cvrmse_pct"]),
        "Met Guideline 14": share(fit["g14_pass"]),
        "Passed all gates": share(fit["gates_passed"]),
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
    stats_file = folder / "pilot_stats.csv"
    if stats_file.exists():
        s = s.merge(pd.read_csv(stats_file)[["run", "profile_rmse", "skill_vs_profile"]], on="run", how="left")
    s["actual / expected RMSE"] = s["rmse"] / s["expected_rmse"]
    cols = ["task", "condition", "model", "delivered", "rmse", "persistence_rmse", "skill", "profile_rmse",
            "skill_vs_profile", "expected_rmse", "actual / expected RMSE", "leak_failures", "leak_tests"]
    out = s[[c for c in cols if c in s.columns]].sort_values(["task", "condition", "model"]).copy()
    for c in ("rmse", "persistence_rmse", "profile_rmse", "expected_rmse"):
        if c in out:
            out[c] = out[c].map(lambda v: f"{v:.3g}" if pd.notna(v) else "")
    for c in ("skill", "skill_vs_profile", "actual / expected RMSE"):
        if c in out:
            out[c] = out[c].map(lambda v: f"{v:.3f}" if pd.notna(v) else "")
    out["leakage test"] = out.apply(lambda r: f"{int(r['leak_failures'])}/{int(r['leak_tests'])} changed"
                                    if pd.notna(r.get("leak_tests")) else "", axis=1)
    out = out.drop(columns=["leak_failures", "leak_tests"]).rename(columns={
        "rmse": "RMSE", "persistence_rmse": "Persistence RMSE", "skill": "Skill vs persistence",
        "profile_rmse": "Profile RMSE", "skill_vs_profile": "Skill vs profile", "expected_rmse": "Self-reported RMSE"})
    return out


def pilot_audit() -> pd.DataFrame:
    """What each agent found and built, and what it cost (manual audit + agent usage counters)."""
    pdir = HERE.parent / "benchmarks" / "pilot"
    a = pd.read_csv(pdir / "audit.csv")
    a["Task"] = a["run"].str[:2]
    a["Condition"] = a["run"].str[3].map({"A": "alone", "C": "+ bemlops"})
    a["Model"] = a["run"].str.split("-").str[-1].str.capitalize()
    a = a.sort_values(["Task", "Condition", "Model"])
    a["Tokens (thousands)"] = (a["tokens"] / 1000).round().astype(int)
    return a[["Task", "Condition", "Model", "faults_found", "own_causality_test", "final_model",
              "Tokens (thousands)", "tool_calls", "minutes"]].rename(columns={
        "faults_found": "Planted faults found", "own_causality_test": "Own causality test",
        "final_model": "Final model", "tool_calls": "Tool calls", "minutes": "Minutes"})


def pilot_pairs() -> pd.DataFrame:
    f = HERE.parent / "benchmarks" / "pilot" / "results" / "pilot_pairs.csv"
    if not f.exists():
        return pd.DataFrame()
    p = pd.read_csv(f)
    unit = p["task"].map({"T1": "ppm", "T2": "kWh"})
    return pd.DataFrame({
        "Task": p["task"], "Model": p["model"].str.capitalize(),
        "RMSE, + bemlops minus alone": [f"{v:+.2f} {u}" for v, u in zip(p["rmse_bemlops_minus_alone"], unit)],
        "95% day-block bootstrap interval": [f"[{lo:+.2f}, {hi:+.2f}]" for lo, hi in zip(p["ci95_low"], p["ci95_high"])],
        "Days": p["days"],
    })


def dm_table() -> pd.DataFrame:
    dm = dm_results()
    if dm.empty:
        return dm
    rows = []
    for ds, d in list(dm.groupby("dataset", sort=False)) + [("All", dm)]:
        rows.append({"Dataset": ds, "Fitted tasks tested": len(d),
                     "Model better than baseline (p < 0.05)": share(d["model_better_p05"]),
                     "Baseline better (p < 0.05)": share((d["dm_stat"] > 0) & (d["p_value"] < 0.05)),
                     "No significant difference": share(~(d["p_value"] < 0.05))})
    return pd.DataFrame(rows)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    df = load_summaries()
    df.to_csv(TABLES / "all_tasks.csv", index=False)
    write = lambda name, frame: (TABLES / f"{name}.md").write_text(md_table(frame), encoding="utf-8")  # noqa: E731
    write("targets", table_targets(df))
    write("datasets", table_datasets(df))
    write("data_issues", data_issue_table(df))
    fig_skill(df)
    dm = dm_table()
    if not dm.empty:
        write("dm_tests", dm)
    p = protocol()
    if not p.empty:
        write("protocol", table_protocol(p))
        write("protocol_tasks", table_protocol_tasks(p))
        fig_protocol(p)
    if (HERE / "aalborg" / "results" / "fault_detection_rate.csv").exists():
        t1, t2, t3 = tables_faults()
        write("fault_detection", t1)
        write("fault_cost", t2)
        if t3 is not None:
            write("fault_tests", t3)
    if (HERE / "aalborg" / "results" / "lifecycle.csv").exists():
        monthly, summary = lifecycle()
        write("lifecycle", monthly)
        write("lifecycle_summary", summary)
    t = bdg2(df)
    if t is not None:
        write("bdg2", t)
    pt = pilot()
    if not pt.empty:
        write("pilot", pt)
        write("pilot_audit", pilot_audit())
        pp = pilot_pairs()
        if not pp.empty:
            write("pilot_pairs", pp)
    counts = df.groupby("dataset").agg(tasks=("task", "count"), fitted=("status", lambda s: (s == "fitted").sum()))
    print(counts.to_string())
    print(f"Wrote {TABLES} and {FIGS}")


if __name__ == "__main__":
    main()
