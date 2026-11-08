"""Compact tables for the journal manuscript (portrait page, short headers) and the supplementary material.

Run after make_results.py:  python case_studies/journal_tables.py
Writes paper/tables/j_*.md (main text) and paper/tables/s_*.md (supplementary material).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_results as mr  # noqa: E402

T = mr.TABLES
MINUS = "−"


def num(v, fmt=".2f") -> str:
    """Format a number with a true minus sign."""
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return format(v, fmt).replace("-", MINUS)


def pct_ci(mask) -> str:
    """'65 [55–74]': percentage with its 95% Wilson interval."""
    m = pd.Series(mask).dropna().astype(bool)
    if m.empty:
        return "–"
    lo, hi = mr.wilson(int(m.sum()), len(m))
    return f"{100 * m.mean():.0f} ({100 * lo:.0f}–{100 * hi:.0f})"


def iqr(s: pd.Series) -> str:
    s = s.dropna()
    return f"{num(s.median())} ({num(s.quantile(.25))} to {num(s.quantile(.75))})" if len(s) else "–"


def write(name: str, frame: pd.DataFrame) -> None:
    (T / f"{name}.md").write_text(mr.md_table(frame), encoding="utf-8")


# ----- main text ----------------------------------------------------------------------------
def j_protocol(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ds, d in list(p.groupby("dataset")) + [("All", p)]:
        ratio = d["optimism_ratio"]
        rows.append({
            "Dataset": ds, "Tasks": len(d),
            "Blocked / shuffled RMSE, median (IQR)": iqr(ratio),
            "Error understated, median": f"{100 * (1 - 1 / ratio).median():.0f}%",
            "R² shuffled / blocked, median": f"{num(d['r2_shuffled_cv'].median())} / {num(d['r2_blocked_cv'].median())}",
            "Selection on all rows / shuffled, median": num((d["rmse_shuffled_cv_selection"] / d["rmse_shuffled_cv"]).median()),
        })
    return pd.DataFrame(rows)


def j_datasets(df: pd.DataFrame, dm: pd.Series) -> pd.DataFrame:
    rows = []
    for ds, d in list(df.groupby("dataset", sort=False)) + [("All", df)]:
        fit = d[d["status"] == "fitted"]
        g14 = fit["g14_pass"].dropna() if "g14_pass" in fit else pd.Series(dtype=bool)
        rows.append({
            "Dataset": ds, "Tasks": len(fit),
            "Skill, median (IQR)": iqr(fit["skill"]),
            "Baseline kept": int((fit["chosen"] == fit["baseline"]).sum()),
            "Skill > 0, % (95% CI)": pct_ci(fit["skill"] > 0),
            "Better than baseline (DM), % (95% CI)": pct_ci(fit["task"].map(dm).fillna(False)),
            "Passed all gates, % (95% CI)": pct_ci(fit["gates_passed"]),
            "Guideline 14 met": f"{int(g14.sum())}/{len(g14)}" if len(g14) else "–",
        })
    return pd.DataFrame(rows)


def j_targets(df: pd.DataFrame, dm: pd.Series) -> pd.DataFrame:
    rows = []
    for cat in mr.CATEGORY_ORDER:
        d = df[(df["category"] == cat) & (df["status"] == "fitted")]
        if d.empty:
            continue
        if cat == "Occupancy (yes/no)":
            err = f"Brier {d['test_brier'].median():.3f}"
        else:
            units = d["unit"].dropna().unique()
            err = (f"MAE {d['test_mae'].median():.3g} {units[0]}" if len(units) == 1
                   else f"CV(RMSE) {d['test_cvrmse_pct'].median():.0f}%")
        cov = d["interval_coverage"].dropna()
        rows.append({
            "Target": cat.replace("Occupancy count (virtual sensor)", "People count, estimated now"),
            "Tasks": len(d),
            "Skill, median (IQR)": iqr(d["skill"]),
            "Skill > 0": f"{int((d['skill'] > 0).sum())}",
            "Better (DM)": f"{int(d['task'].map(dm).fillna(False).sum())}",
            "90% interval coverage, median": f"{100 * cov.median():.0f}%" if len(cov) else "–",
            "Typical test error": err.replace("ug/m3", "µg m⁻³").replace("degC", "°C"),
        })
    return pd.DataFrame(rows)


def j_bdg2(df: pd.DataFrame, dm: pd.Series) -> pd.DataFrame:
    d = df[(df["dataset"] == "BDG2") & (df["status"] == "fitted")]
    rows = [
        ("Buildings (sites; primary uses)", f"{len(d)} ({d['site'].nunique()}; {d['primary_use'].nunique()})"),
        ("Baseline kept on validation", f"{int((d['chosen'] == d['baseline']).sum())}"),
        ("Skill vs strongest baseline, median (IQR)", iqr(d["skill"])),
        ("Skill > 0", f"{int((d['skill'] > 0).sum())}/{len(d)}"),
        ("Better than baseline (DM, p < 0.05)", f"{int(d['task'].map(dm).fillna(False).sum())}/{len(d)}"),
        ("CV(RMSE), median (IQR)", "{:.1f}% ({:.1f}% to {:.1f}%)".format(d["test_cvrmse_pct"].median(),
                                                                         d["test_cvrmse_pct"].quantile(.25),
                                                                         d["test_cvrmse_pct"].quantile(.75))),
        ("ASHRAE Guideline 14 met", f"{int(d['g14_pass'].sum())}/{len(d)}"),
        ("Passed all promotion gates", f"{int(d['gates_passed'].sum())}/{len(d)}"),
        ("90% interval coverage, median (range)",
         f"{100 * d['interval_coverage'].median():.0f}% ({100 * d['interval_coverage'].min():.0f}–"
         f"{100 * d['interval_coverage'].max():.0f}%)"),
        ("Run time per building, median", f"{d['seconds'].median():.0f} s"),
    ]
    return pd.DataFrame(rows, columns=["Measure", "Value"])


def j_faults() -> pd.DataFrame:
    cost = pd.read_csv(HERE / "aalborg" / "results" / "fault_cost.csv")
    tests = pd.read_csv(HERE / "aalborg" / "results" / "fault_tests.csv")
    names = {"clean data (reference)": "Clean data (random-forest seed only)",
             "faulty data, unguarded script": "Faulty data, quick script",
             "faulty data, unguarded script + same unit fix": "Faulty data, quick script + unit fix",
             "faulty data, bemlops": "Faulty data, framework"}
    rows = []
    for arm, d in cost.groupby("pipeline", sort=False):
        row = {"Pipeline": names.get(arm, arm),
               "RMSE (ppm), mean ± SD": f"{d['rmse_ppm'].mean():.1f} ± {d['rmse_ppm'].std():.1f}",
               "MAE (ppm), mean ± SD": f"{d['mae_ppm'].mean():.1f} ± {d['mae_ppm'].std():.1f}"}
        for metric, label in (("rmse_ppm", "ΔRMSE"), ("mae_ppm", "ΔMAE")):
            t = tests[(tests["comparison"] == f"{arm} vs bemlops") & (tests["metric"] == metric)]
            row[f"{label} vs framework, median (p)"] = (
                f"{num(t['median_difference'].iat[0], '+.2f')} ({t['p_value'].iat[0]:.2f})" if len(t) else "–")
        rows.append(row)
    return pd.DataFrame(rows)


def j_lifecycle() -> pd.DataFrame:
    lc = mr.lifecycle_frame()
    rows = []
    for task, d in lc.groupby("task", sort=False):
        unit = "kW" if "heating" in task.lower() else "ppm"
        f = (lambda c: f"{d[c].mean():#.3g}")
        rows.append({"Task": f"{task.replace(', 1 h ahead', '')} ({unit})", "Static": f("static_rmse"),
                     "Monthly retrain": f("naive_rmse"), "Monitored + gated": f("production_rmse"),
                     "Persistence": f("persistence_rmse"), "Gated + fallback rule": f("fallback_rmse"),
                     "Months gated model beat persistence": f"{int((d['production_rmse'] < d['persistence_rmse']).sum())}/{len(d)}",
                     "Retrains advised (promoted)": f"{int(d['retrain_recommended'].sum())} ({int(d['promoted'].sum())})"})
    return pd.DataFrame(rows)


SHORT_MODEL = {
    "T1_A-opus": "Own: boosting on change from last value",
    "T1_A-sonnet": "Own: extra trees + boosting on change",
    "T1_C-opus": "Framework boosting on change + own lags",
    "T1_C-sonnet": "Own: extra trees on change; framework for checks",
    "T2_A-opus": "Own: boosting + meter-fault rules",
    "T2_A-sonnet": "Own: time-of-day profile + ridge + rules",
    "T2_C-opus": "Framework random forest + own schedule inputs",
    "T2_C-sonnet": "Own: profile + ridge; framework for checks",
}


def j_pilot() -> pd.DataFrame:
    folder = HERE.parent / "benchmarks" / "pilot" / "results"
    s = pd.concat([pd.read_csv(f) for f in sorted(folder.glob("score_T*.csv"))], ignore_index=True)
    s = s.merge(pd.read_csv(folder / "pilot_stats.csv")[["run", "skill_vs_profile"]], on="run")
    s["Arm"] = s["run"].str[3].map({"A": "Alone", "C": "+ framework"})
    s["Model"] = s["run"].str.split("-").str[-1].str.capitalize()
    s = s.sort_values(["task", "run", "Model"])
    unit = s["task"].map({"T1": "ppm", "T2": "kWh"})
    return pd.DataFrame({
        "Task": s["task"], "Arm": s["Arm"], "Model": s["Model"],
        "RMSE": [f"{v:.3g} {u}" for v, u in zip(s["rmse"], unit)],
        "Skill vs persistence": s["skill"].map(lambda v: num(v)),
        "Skill vs profile": s["skill_vs_profile"].map(lambda v: num(v)),
        "Achieved / self-reported RMSE": (s["rmse"] / s["expected_rmse"]).map(lambda v: num(v)),
        "Forecasts changed by leakage test": [f"{int(a)}/{int(b)}" for a, b in zip(s["leak_failures"], s["leak_tests"])],
    })


def j_pilot_audit() -> pd.DataFrame:
    a = pd.read_csv(HERE.parent / "benchmarks" / "pilot" / "audit.csv")
    a["Task"] = a["run"].str[:2]
    a["Arm"] = a["run"].str[3].map({"A": "Alone", "C": "+ framework"})
    a["Model"] = a["run"].str.split("-").str[-1].str.capitalize()
    a = a.sort_values(["Task", "run", "Model"])
    return pd.DataFrame({
        "Task": a["Task"], "Arm": a["Arm"], "Model": a["Model"],
        "Planted faults found": a["faults_found"],
        "Own causality test": a["own_causality_test"].str.split(" ").str[0],
        "Final model": a["run"].map(SHORT_MODEL),
        "Tokens (×10³)": (a["tokens"] / 1000).round().astype(int),
        "Tool calls": a["tool_calls"], "Minutes": a["minutes"],
    })


# ----- supplementary material -------------------------------------------------------------
def s_lifecycle_monthly(task_word: str) -> pd.DataFrame:
    lc = mr.lifecycle_frame()
    d = lc[lc["task"].str.contains(task_word)]
    f = (lambda v: f"{v:#.3g}")
    return pd.DataFrame({
        "Month": d["month"], "Served version": d["production_version"],
        "Static": d["static_rmse"].map(f), "Monthly retrain": d["naive_rmse"].map(f),
        "Monitored + gated": d["production_rmse"].map(f), "Persistence": d["persistence_rmse"].map(f),
        "Fallback rule": [f(v) + (" (P)" if u else "") for v, u in zip(d["fallback_rmse"], d["fallback_uses_persistence"])],
        "Drift ratio": d["drift_ratio"].map(lambda v: f"{v:.2f}"),
        "Retrain advised": d["retrain_recommended"].map({True: "yes", False: "no"}),
        "Promoted": d["promoted"].map({True: "yes", False: "no"}),
    })


def s_protocol_tasks(p: pd.DataFrame) -> pd.DataFrame:
    unit = {"co2": "ppm"}
    return pd.DataFrame({
        "Task": p["task"].str.replace("aalborg-", "Aalborg ").str.replace("robod-", "ROBOD "),
        "Shuffled CV": p["rmse_shuffled_cv"].map(lambda v: f"{v:.3g}"),
        "Shuffled + selection": p["rmse_shuffled_cv_selection"].map(lambda v: f"{v:.3g}"),
        "Blocked CV": p["rmse_blocked_cv"].map(lambda v: f"{v:.3g}"),
        "Time-ordered holdout": p["rmse_time_ordered_holdout"].map(lambda v: f"{v:.3g}"),
        "Blocked / shuffled": p["optimism_ratio"].map(lambda v: f"{v:.2f}"),
    })


def s_all_tasks(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["status"] == "fitted"].copy()
    name = (d["task"].str.replace(r"^(robod|aalborg|bdg2)-", "", regex=True))
    return pd.DataFrame({
        "Dataset": d["dataset"], "Task": name,
        "Chosen": d["chosen"].str.replace("_", " "), "Reference": d["baseline"].str.replace("_", " "),
        "Skill": d["skill"].map(lambda v: num(v)),
        "Backtest skill": d["backtest_skill"].map(lambda v: num(v)),
        "90% coverage": d["interval_coverage"].map(lambda v: f"{100 * v:.0f}%" if pd.notna(v) else "–"),
        "Gates": d["gates_passed"].map({True: "passed", False: "refused"}),
    })


def main() -> None:
    df = mr.load_summaries()
    dmr = mr.dm_results()
    dm = dmr.set_index("task")["model_better_p05"] if not dmr.empty else pd.Series(dtype=bool)
    p = mr.protocol()
    write("j_protocol", j_protocol(p))
    write("j_datasets", j_datasets(df, dm))
    write("j_targets", j_targets(df, dm))
    write("j_bdg2", j_bdg2(df, dm))
    write("j_faults", j_faults())
    write("j_lifecycle", j_lifecycle())
    write("j_pilot", j_pilot())
    write("j_pilot_audit", j_pilot_audit())
    write("s_lifecycle_dh", s_lifecycle_monthly("heating"))
    write("s_lifecycle_co2", s_lifecycle_monthly("CO2"))
    write("s_protocol_tasks", s_protocol_tasks(p))
    write("s_all_tasks", s_all_tasks(df))
    print("Wrote journal tables to", T)


if __name__ == "__main__":
    main()
