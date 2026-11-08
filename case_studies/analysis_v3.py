"""Statistics, tables and figures for the v3 paper (ANALYSIS_PLAN_v3.md).

Run after case_studies/run_v3.py:  python case_studies/analysis_v3.py
Writes case_studies/results_v3/{dm_tests,tasks_v3,key_numbers}.csv, paper/tables/v3_*.md and paper/figures/*.
"""

from __future__ import annotations

import json
import sys
from math import erf, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats as st  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
R3 = HERE / "results_v3"
RUNS = REPO / "runs" / "v3"
TABLES, FIGS = REPO / "paper" / "tables", REPO / "paper" / "figures"
sys.path.insert(0, str(HERE))
import make_results as mr  # noqa: E402  (palette, categories, md_table)

MINUS = "−"
RNG = np.random.default_rng(0)
B = 2000
KEY: list = []           # (name, value, unit, source)
COLORS = mr.COLORS
INK, INK2, GRID = mr.INK, mr.INK2, mr.GRID


CAT_ORDER = ["Whole-building electricity", "Plug-load electricity", "Fan electricity", "Heating/cooling energy", "CO2",
             "Room temperature", "Humidity", "PM2.5", "Occupancy count", "Occupancy count (virtual sensor)",
             "Occupancy (yes/no)"]
ENERGY = CAT_ORDER[:4]


def category(row) -> str:
    c = mr.category(row)
    if c != "Electricity":
        return c
    if row["dataset"] == "BDG2":
        return "Whole-building electricity"
    return "Plug-load electricity" if "plug" in str(row["target"]).lower() else "Fan electricity"


def key(name, value, unit="", source=""):
    KEY.append({"name": name, "value": value, "unit": unit, "source": source})
    return value


def num(v, fmt=".2f"):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return format(v, fmt).replace("-", MINUS)


def fmt_p(p):
    return f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


def write(name, frame):
    (TABLES / f"{name}.md").write_text(mr.md_table(frame), encoding="utf-8")


# ----- E1 ----------------------------------------------------------------------------------------
def load_tasks() -> pd.DataFrame:
    frames = []
    for ds in ("robod", "aalborg", "bdg2"):
        f = HERE / ds / "results" / "summary.csv"
        d = pd.read_csv(f)
        d["ds_dir"] = ds
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["category"] = df.apply(category, axis=1)
    df["cluster"] = np.where(df["dataset"] == "BDG2", df["building"],
                             np.where(df["dataset"] == "ROBOD", df["building"].str.extract(r"(Room \d)")[0],
                                      "Aalborg " + df["building"].astype(str)))
    df["group"] = np.where(df["dataset"] == "BDG2", "near-held-out (BDG2)", "development (ROBOD, Aalborg)")
    df["energy"] = df["category"].isin(ENERGY)
    return df


def _norm_sf(z):
    return 0.5 * (1 - erf(z / sqrt(2)))


def dm_hln(d: np.ndarray, h: int):
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 20 or np.allclose(d, 0):
        return np.nan, np.nan, np.nan
    lag = max(int(h), int(4 * (n / 100) ** (2 / 9)), 1)
    dc = d - d.mean()
    var = np.sum(dc * dc) / n
    for k in range(1, lag + 1):
        var += 2 * (1 - k / (lag + 1)) * np.sum(dc[k:] * dc[:-k]) / n
    if var <= 0:
        return np.nan, np.nan, np.nan
    stat = d.mean() / sqrt(var / n)
    p = 2 * _norm_sf(abs(stat))
    hh = max(h, 1)
    corr = sqrt(max((n + 1 - 2 * hh + hh * (hh - 1) / n) / n, 1e-12))
    p_hln = 2 * st.t.sf(abs(stat * corr), n - 1)
    return float(stat), float(p), float(p_hln)


def per_task_tests(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, t in df[df["status"] == "fitted"].iterrows():
        folder = RUNS / t["ds_dir"] / t["run"]
        rec = json.loads((folder / "run.json").read_text(encoding="utf-8"))
        p = pd.read_csv(folder / "test_predictions.csv", index_col=0)
        cls = rec["task"]["task_type"] == "classification"
        col = "probability" if cls else "predicted"
        base = rec["test"]["baseline"]["name"]
        bcol = p[base].clip(0, 1) if cls else p[base]
        lm, lb = (p["actual"] - p[col]) ** 2, (p["actual"] - bcol) ** 2
        stat, pv, phln = dm_hln((lm - lb).to_numpy(), int(rec["task"]["horizon_steps"]))
        # day-block bootstrap of skill on the test window
        days = pd.Index(p.index.astype(str).str[:10])  # local calendar day (offsets change at daylight saving)
        groups = [np.flatnonzero(days == d) for d in np.unique(days)]
        e_m, e_b = lm.to_numpy(), lb.to_numpy()
        sk = []
        for _ in range(500):
            take = np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])
            a, b = np.nanmean(e_m[take]), np.nanmean(e_b[take])
            sk.append(1 - (sqrt(a / b) if not cls else a / b) if b > 0 else np.nan)
        lo, hi = np.nanpercentile(sk, [2.5, 97.5]) if np.isfinite(sk).any() else (np.nan, np.nan)
        masked = sum(e.get("count", 0) for e in rec["prepare"]["log"]
                     if e.get("column") == rec["task"]["target"] and str(e.get("step", "")).startswith("mask"))
        rows.append({"task": t["task"], "dm_stat": stat, "p_value": pv, "p_hln": phln,
                     "skill_lo": lo, "skill_hi": hi, "test_days_rec": rec["split"].get("test_days"),
                     "masked_target": masked, "rows_raw": float(rec["data_check"]["summary"].get("rows", "nan")),
                     "issues": [i["id"] for i in rec["data_check"]["issues"] if i["severity"] in ("warning", "error")]})
    out = pd.DataFrame(rows)
    out["better"] = (out["dm_stat"] < 0) & (out["p_value"] < 0.05)
    out["better_hln"] = (out["dm_stat"] < 0) & (out["p_hln"] < 0.05)
    # Benjamini-Hochberg over the tests actually run
    ok = out["p_value"].notna()
    pv = out.loc[ok, "p_value"].to_numpy()
    order = np.argsort(pv)
    ranks = np.empty(len(pv)); ranks[order] = np.arange(1, len(pv) + 1)
    q = np.minimum.accumulate((pv[order] * len(pv) / np.arange(1, len(pv) + 1))[::-1])[::-1]
    qv = np.empty(len(pv)); qv[order] = np.minimum(q, 1)
    out.loc[ok, "q_bh"] = qv
    out["better_bh"] = (out["dm_stat"] < 0) & (out["q_bh"] < 0.05)
    return out


def cluster_ci(mask: pd.Series, clusters: pd.Series):
    """Share with a cluster-bootstrap 95% interval (clusters resampled with replacement)."""
    d = pd.DataFrame({"m": mask.astype(float).to_numpy(), "c": clusters.to_numpy()})
    g = d.groupby("c")["m"].agg(["sum", "count"])
    s, n = g["sum"].to_numpy(), g["count"].to_numpy()
    est = s.sum() / n.sum()
    boots = []
    for _ in range(B):
        i = RNG.integers(0, len(g), len(g))
        boots.append(s[i].sum() / n[i].sum())
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return est, lo, hi


def fmt_ci(t):
    e, lo, hi = t
    return f"{100 * e:.0f} ({100 * lo:.0f}–{100 * hi:.0f})"


def table_e1(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = [("ROBOD", df["dataset"] == "ROBOD"), ("Aalborg", df["dataset"] == "Aalborg"),
              ("BDG2", df["dataset"] == "BDG2"), ("All", df["dataset"].notna())]
    for name, sel in groups:
        d = df[sel & (df["status"] == "fitted")]
        kept = d["chosen"] == d["baseline"]
        rows.append({
            "Dataset": name, "Tasks": len(d), "Clusters": d["cluster"].nunique(),
            "Test days, median (range)": f"{d['test_days'].median():.0f} ({d['test_days'].min():.0f}–{d['test_days'].max():.0f})",
            "Skill, median (IQR)": f"{num(d['skill'].median())} ({num(d['skill'].quantile(.25))} to {num(d['skill'].quantile(.75))})",
            "Baseline kept": int(kept.sum()),
            "Better than baseline (DM), % (95% CI)": fmt_ci(cluster_ci(d["better"], d["cluster"])),
            "Machine-learning model refused by gates": f"{int((~kept & ~d['gates_passed']).sum())}/{int((~kept).sum())}",
        })
        key(f"e1_{name}_tasks", len(d))
        key(f"e1_{name}_better_dm_pct", round(100 * d["better"].mean(), 1), "%", "dm_tests")
        key(f"e1_{name}_baseline_kept", int(kept.sum()))
        key(f"e1_{name}_ml_refused", int((~kept & ~d["gates_passed"]).sum()))
        key(f"e1_{name}_ml_chosen", int((~kept).sum()))
        key(f"e1_{name}_skill_median", round(float(d["skill"].median()), 3))
    return pd.DataFrame(rows)


def table_targets(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cat in CAT_ORDER:
        d = df[(df["category"] == cat) & (df["status"] == "fitted")]
        if d.empty:
            continue
        rows.append({"Target": cat.replace("Occupancy count (virtual sensor)", "People count, estimated now"),
                     "Tasks": len(d), "Skill, median (IQR)":
                     f"{num(d['skill'].median())} ({num(d['skill'].quantile(.25))} to {num(d['skill'].quantile(.75))})",
                     "Better (DM)": int(d["better"].sum()),
                     "Promoted": int(d["gates_passed"].astype(bool).sum()),
                     "Most frequent reference": d["baseline"].value_counts().index[0].replace("_", " "),
                     "90% coverage, median": f"{100 * d['interval_coverage'].median():.0f}%" if d["interval_coverage"].notna().any() else "–"})
    return pd.DataFrame(rows)


def table_references(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["status"] == "fitted"]
    t = pd.crosstab(d["baseline"], d["dataset"]).reindex(columns=["ROBOD", "Aalborg", "BDG2"]).fillna(0).astype(int)
    t["All"] = t.sum(axis=1)
    t = t.sort_values("All", ascending=False).reset_index().rename(columns={"baseline": "Strongest baseline on validation"})
    t["Strongest baseline on validation"] = t["Strongest baseline on validation"].str.replace("_", " ")
    return t


def gate_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["status"] == "fitted"]
    ml = d["chosen"] != d["baseline"]
    other = d["failed_gates"].fillna("").str.replace("beats_baseline", "").str.strip(";") == ""
    rows = []
    for thr in (0.0, 0.05, 0.10):
        base = ml & (d["skill"] >= thr) & other
        rows.append({"Rule": f"Skill ≥ {thr:.2f} on the test window (as evaluated)" if thr == 0.05 else f"Skill ≥ {thr:.2f}",
                     "Promoted": int(base.sum())})
    variants = {
        "Skill ≥ 0.05 and significant DM result": ml & (d["skill"] >= 0.05) & other & d["better"],
        "Skill ≥ 0.05 and ≥ 7 test days": ml & (d["skill"] >= 0.05) & other & (d["test_days"] >= 7),
        "Skill ≥ 0.05 and lower bootstrap bound > 0": ml & (d["skill"] >= 0.05) & other & (d["skill_lo"] > 0),
        "Skill ≥ 0.05 on test and backtest": ml & (d["skill"] >= 0.05) & other & (d["backtest_skill"] >= 0.05),
    }
    for k, v in variants.items():
        rows.append({"Rule": k, "Promoted": int(v.sum())})
    out = pd.DataFrame(rows)
    out["Promoted"] = out["Promoted"].astype(str) + f"/{len(d)}"
    return out


def fig_skill(df: pd.DataFrame) -> None:
    fit = df[df["status"] == "fitted"].copy()
    cats = [c for c in CAT_ORDER if c in set(fit["category"])]
    fig, ax = plt.subplots(figsize=(7.0, 0.42 * len(cats) + 1.4))
    for ds, color in COLORS.items():
        d = fit[fit["dataset"] == ds]
        if d.empty:
            continue
        y = d["category"].map({c: i for i, c in enumerate(cats)}) + RNG.uniform(-0.2, 0.2, len(d))
        x = d["skill"].clip(-0.5, 1)
        sig = d["better"].to_numpy()
        clipped = (d["skill"] < -0.5).to_numpy()
        ax.scatter(x[sig & ~clipped], y[sig & ~clipped], s=16, color=color, edgecolor="white", linewidth=0.5,
                   zorder=3, label=f"{ds} ({len(d)} tasks)")
        ax.scatter(x[~sig & ~clipped], y[~sig & ~clipped], s=16, facecolor="white", edgecolor=color, linewidth=0.9,
                   zorder=3)
        ax.scatter(np.full(clipped.sum(), -0.5), y[clipped], marker="<", s=26, facecolor="white", edgecolor=color,
                   linewidth=0.9, zorder=4)
    ax.axvline(0, color=INK2, lw=1, zorder=2)
    ax.set_yticks(range(len(cats)), [c.replace("Occupancy count (virtual sensor)", "People count, estimated now")
                                     .replace("CO2", "CO$_2$") for c in cats])
    ax.invert_yaxis()
    ax.set_xlim(-0.55, 1.0)
    ax.set_xlabel("Test skill against the strongest baseline without machine learning")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"skill_by_target.{ext}")
    plt.close(fig)


def fig_bdg2(df: pd.DataFrame) -> None:
    d = df[(df["dataset"] == "BDG2") & (df["status"] == "fitted") & (df["base_cvrmse_pct"] > 0)]
    fig, ax = plt.subplots(figsize=(4.6, 4.3))
    lim = 80
    ml = d["chosen"] != d["baseline"]
    groups = ((ml & d["gates_passed"].astype(bool), COLORS["BDG2"], "model promoted"),
              (ml & ~d["gates_passed"].astype(bool), COLORS["Aalborg"], "model refused"),
              (~ml, INK2, "baseline kept"))
    for sel, color, label in groups:
        s = d[sel]
        x, y = s["base_cvrmse_pct"], s["test_cvrmse_pct"]
        inside = (x <= lim) & (y <= lim)
        ax.scatter(x[inside], y[inside], s=14, color=color, edgecolor="white", linewidth=0.5,
                   label=f"{label} ({len(s)})", zorder=3)
        ax.scatter(x[~inside].clip(upper=lim), y[~inside].clip(upper=lim), s=24, marker="^", facecolor="white",
                   edgecolor=color, linewidth=0.9, zorder=4, clip_on=False)
    key("fig_bdg2_plotted", len(d))
    ax.plot([0, lim], [0, lim], color=INK2, lw=1, ls="--")
    ax.axhline(30, color=GRID, lw=1); ax.axvline(30, color=GRID, lw=1)
    ax.set_xlabel("Reference baseline CV(RMSE), % (hourly, test window)")
    ax.set_ylabel("Chosen model CV(RMSE), %")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"bdg2_cvrmse.{ext}")
    plt.close(fig)


# ----- E2 ----------------------------------------------------------------------------------------
def protocol_tables():
    p = pd.read_csv(R3 / "protocol.csv")
    p["cluster"] = np.where(p["dataset"] == "BDG2", p["task"],
                            np.where(p["dataset"] == "ROBOD", p["task"].str.extract(r"(room\d)")[0], "Aalborg A"))
    rows = []
    for name, d in list(p.groupby("dataset", sort=False)) + [("All", p)]:
        def med_ci(col):
            v = d[col].to_numpy()
            c = d["cluster"].to_numpy()
            u = np.unique(c)
            if len(u) < 5:  # too few rooms or systems for a meaningful cluster interval
                return f"{num(np.median(v))} (range {num(v.min())}–{num(v.max())})", float(np.median(v))
            boots = []
            for _ in range(B):
                take = RNG.choice(u, len(u))
                boots.append(np.median(np.concatenate([v[c == k] for k in take])))
            lo, hi = np.percentile(boots, [2.5, 97.5])
            return f"{num(np.median(v))} ({num(lo)}–{num(hi)})", float(np.median(v))
        bs, bsv = med_ci("ratio_blocked_shuffled")
        fs, fsv = med_ci("ratio_forward_shuffled_f2")
        sel = (d["rmse_selection_all_rows"] / d["rmse_selection_in_fold"]).median()  # per task, then median
        rows.append({"Dataset": name, "Tasks": len(d),
                     "Blocked / shuffled, median (95% CI or range)": bs,
                     "Forward chaining / shuffled (same rows), median (95% CI or range)": fs,
                     "Tasks with forward > shuffled": f"{int((d['ratio_forward_shuffled_f2'] > 1).sum())}/{len(d)}",
                     "Selection on all rows / in-fold selection, median": num(sel)})
        key(f"e2_{name}_blocked_shuffled_median", round(bsv, 3))
        key(f"e2_{name}_forward_shuffled_median", round(fsv, 3))
        key(f"e2_{name}_tasks", len(d))
        key(f"e2_{name}_forward_gt_shuffled", int((d["ratio_forward_shuffled_f2"] > 1).sum()))
        r = d["ratio_forward_shuffled_f2"]
        key(f"e2_{name}_shuffled_understates_forward_median_pct", round(100 * (1 - 1 / r.median()), 1), "%")
        key(f"e2_{name}_shuffled_understates_forward_min_pct", round(100 * (1 - 1 / r.min()), 1), "%")
        key(f"e2_{name}_shuffled_understates_forward_max_pct", round(100 * (1 - 1 / r.max()), 1), "%")
        key(f"e2_{name}_blocked_shuffled_min", round(float(d["ratio_blocked_shuffled"].min()), 3))
        key(f"e2_{name}_blocked_shuffled_max", round(float(d["ratio_blocked_shuffled"].max()), 3))
        key(f"e2_{name}_forward_shuffled_min", round(float(d["ratio_forward_shuffled_f2"].min()), 3))
        key(f"e2_{name}_forward_shuffled_max", round(float(d["ratio_forward_shuffled_f2"].max()), 3))
        key(f"e2_{name}_selection_all_vs_infold_median", round(float(sel), 3))
        key(f"e2_{name}_r2_shuffled_median", round(float(d["r2_shuffled_cv"].median()), 3))
        key(f"e2_{name}_r2_blocked_median", round(float(d["r2_blocked_cv"].median()), 3))
    write("v3_protocol", pd.DataFrame(rows))
    # G14 verdicts on BDG2 under each protocol, against the forward-chaining (deployment-like) verdict
    b = p[p["dataset"] == "BDG2"]
    if len(b):
        ok = lambda cv, nm: (cv <= 30) & (nm.abs() <= 10)  # noqa: E731
        # all three on the same rows (blocked folds 2-5), so only the protocol differs
        v_sh, v_bl, v_fw = (ok(b["cvrmse_pct_shuffled_cv_f2"], b["nmbe_pct_shuffled_cv_f2"]),
                            ok(b["cvrmse_pct_blocked_cv_f2"], b["nmbe_pct_blocked_cv_f2"]),
                            ok(b["cvrmse_pct_forward_chaining_f2"], b["nmbe_pct_forward_chaining_f2"]))
        for name, col in (("shuffled", "shuffled_cv_f2"), ("blocked", "blocked_cv_f2"), ("forward", "forward_chaining_f2")):
            key(f"e2_bdg2_cvrmse_{name}_median", round(float(b[f"cvrmse_pct_{col}"].median()), 1), "%")
        key("e2_bdg2_g14_blocked_pass", int(v_bl.sum())); key("e2_bdg2_g14_blocked_contradicted", int((v_bl & ~v_fw).sum()))
        g = pd.DataFrame([{"Protocol": "Shuffled CV", "Meets limits": int(v_sh.sum()),
                           "Contradicted by forward chaining": int((v_sh & ~v_fw).sum())},
                          {"Protocol": "Blocked CV", "Meets limits": int(v_bl.sum()),
                           "Contradicted by forward chaining": int((v_bl & ~v_fw).sum())},
                          {"Protocol": "Forward chaining", "Meets limits": int(v_fw.sum()),
                           "Contradicted by forward chaining": 0}])
        g["Meets limits"] = g["Meets limits"].astype(str) + f"/{len(b)}"
        write("v3_protocol_g14", g)
        key("e2_bdg2_g14_shuffled_pass", int(v_sh.sum())); key("e2_bdg2_g14_forward_pass", int(v_fw.sum()))
        key("e2_bdg2_g14_shuffled_contradicted", int((v_sh & ~v_fw).sum()))
    # figure: R2 shuffled vs blocked
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    for ds, color in COLORS.items():
        d = p[p["dataset"] == ds]
        if len(d):
            ax.scatter(d["r2_blocked_cv"], d["r2_shuffled_cv"], s=16, color=color, edgecolor="white", linewidth=0.5,
                       label=f"{ds} ({len(d)} tasks)", zorder=3)
    lo = min(0.0, float(np.nanmin(p[["r2_blocked_cv", "r2_shuffled_cv"]].to_numpy())))
    ax.plot([lo, 1], [lo, 1], color=INK2, lw=1, ls="--")
    ax.set_xlabel("R² with blocked cross-validation"); ax.set_ylabel("R² with shuffled cross-validation")
    ax.legend(loc="lower right", frameon=False, fontsize=8)  # every point lies above the diagonal
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"protocol_r2.{ext}")
    plt.close(fig)
    t = p[["dataset", "task", "rmse_shuffled_cv", "rmse_selection_all_rows", "rmse_selection_in_fold", "rmse_blocked_cv",
           "rmse_shuffled_cv_f2", "rmse_forward_chaining_f2", "ratio_blocked_shuffled", "ratio_forward_shuffled_f2"]].copy()
    for c in t.columns[2:]:
        t[c] = t[c].map(lambda v: f"{v:.3g}")
    write("s_protocol_v3", t.rename(columns={
        "rmse_shuffled_cv": "Shuffled", "rmse_selection_all_rows": "Selection all rows",
        "rmse_selection_in_fold": "Selection in fold", "rmse_blocked_cv": "Blocked",
        "rmse_shuffled_cv_f2": "Shuffled (folds 2–5)", "rmse_forward_chaining_f2": "Forward (folds 2–5)",
        "ratio_blocked_shuffled": "Blocked/shuffled", "ratio_forward_shuffled_f2": "Forward/shuffled"}))


# ----- E5 M&V -------------------------------------------------------------------------------------
def mv_tables():
    m = pd.read_csv(R3 / "mv.csv")
    m = m[m["status"] == "fitted"]
    key("mv_buildings", len(m)); key("mv_nonroutine", int(m["nonroutine_flag"].sum()))
    rows = []
    for name, d in (("All buildings", m), ("Without flagged non-routine change", m[~m["nonroutine_flag"]])):
        for arm, label in (("towt", "TOWT regression"), ("fw", "Framework (estimation mode)")):
            nase = d[f"{arm}_nase"].abs()
            rows.append({"Buildings": f"{name} ({len(d)})", "Baseline model": label,
                         "Absolute pseudo-savings error, median (IQR)": f"{100 * nase.median():.1f}% ({100 * nase.quantile(.25):.1f}–{100 * nase.quantile(.75):.1f}%)",
                         "Within ±5%": f"{int((nase <= 0.05).sum())}/{len(d)}",
                         "CV(RMSE) 2017, median": f"{d[f'{arm}_cvrmse'].median():.1f}%",
                         "Meets 30%/±10% in 2017": f"{int(((d[f'{arm}_cvrmse'] <= 30) & (d[f'{arm}_nmbe'].abs() <= 10)).sum())}/{len(d)}"})
            if name == "All buildings":
                key(f"mv_{arm}_abs_nase_median_pct", round(100 * nase.median(), 2), "%")
                key(f"mv_{arm}_within5", int((nase <= 0.05).sum()))
    write("v3_mv", pd.DataFrame(rows))
    diff = (m["fw_nase"].abs() - m["towt_nase"].abs())
    w = st.wilcoxon(m["fw_nase"].abs(), m["towt_nase"].abs())
    key("mv_fw_minus_towt_abs_nase_median", round(100 * diff.median(), 2), "pp"); key("mv_wilcoxon_p", round(w.pvalue, 4))
    for name, n in m["chosen"].value_counts().items():
        key(f"mv_fw_chose_{name}", int(n))
    gp = m["fw_gates_passed"].astype(bool)
    key("mv_fw_gates_passed", int(gp.sum()))
    key("mv_fw_abs_nase_median_gates_passed_pct", round(100 * float(m.loc[gp, "fw_nase"].abs().median()), 2), "%")
    key("mv_fw_abs_nase_median_gates_refused_pct", round(100 * float(m.loc[~gp, "fw_nase"].abs().median()), 2), "%")
    for f, n in m.loc[~gp, "fw_failed_gates"].fillna("").str.split(";").explode().value_counts().items():
        if f:
            key(f"mv_fw_failed_{f}", int(n))
    r = m[~m["nonroutine_flag"]]
    key("mv_routine_buildings", len(r))
    for arm in ("towt", "fw"):
        key(f"mv_routine_{arm}_abs_nase_median_pct", round(100 * float(r[f"{arm}_nase"].abs().median()), 2), "%")
        key(f"mv_routine_{arm}_within5", int((r[f"{arm}_nase"].abs() <= 0.05).sum()))
        key(f"mv_{arm}_cvrmse_median", round(float(m[f"{arm}_cvrmse"].median()), 1), "%")
        key(f"mv_{arm}_nase_median_signed_pct", round(100 * float(m[f"{arm}_nase"].median()), 2), "%")
    # protocol link: estimated baseline-period CV(RMSE) vs realized 2017
    real = m["towt_cvrmse"]
    rows = []
    for est, label in (("towt_insample", "In-sample fit"), ("towt_shuffled", "Shuffled CV"),
                       ("towt_blocked", "Blocked CV"), ("towt_timeordered", "Time-ordered split")):
        ratio = m[f"{est}_cvrmse"] / real
        says_ok = (m[f"{est}_cvrmse"] <= 30) & (m[f"{est}_nmbe"].abs() <= 10)
        real_ok = (real <= 30) & (m["towt_nmbe"].abs() <= 10)
        rows.append({"Estimate of baseline-model error (2016)": label,
                     "Estimated / realized 2017 CV(RMSE), median (IQR)": f"{num(ratio.median())} ({num(ratio.quantile(.25))}–{num(ratio.quantile(.75))})",
                     "Estimate meets limits": f"{int(says_ok.sum())}/{len(m)}",
                     "…but 2017 does not": f"{int((says_ok & ~real_ok).sum())}"})
        key(f"mv_{est}_ratio_median", round(float(ratio.median()), 3))
        key(f"mv_{est}_false_pass", int((says_ok & ~real_ok).sum()))
    write("v3_mv_protocol", pd.DataFrame(rows))
    # figures: one graph per file (Elsevier artwork rule), savings error and estimated vs realized error
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    data = [100 * m["towt_nase"], 100 * m["fw_nase"]]
    ax.boxplot(data, orientation="horizontal", widths=0.5, showfliers=False, medianprops={"color": INK})
    nr = m["nonroutine_flag"].astype(bool).to_numpy()
    for i, (d, c) in enumerate(zip(data, (INK2, COLORS["BDG2"])), start=1):
        y = i + RNG.uniform(-0.18, 0.18, len(d))
        x = d.clip(-40, 40).to_numpy()
        ax.scatter(x[~nr], y[~nr], s=6, color=c, alpha=0.6, zorder=3)
        ax.scatter(x[nr], y[nr], s=9, facecolor="white", edgecolor=c, linewidth=0.7, zorder=3,
                   label="flagged non-routine change" if i == 2 else None)
    ax.legend(frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.0), borderaxespad=0.2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks([1, 2], ["TOWT", "Framework"]); ax.set_xlim(-40, 40)
    ax.set_xlabel("2017 pseudo-savings error, % (values clipped at ±40)")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"mv_savings.{ext}")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    for est, label, c in (("towt_shuffled", "shuffled cross-validation", COLORS["Aalborg"]),
                          ("towt_blocked", "blocked cross-validation", COLORS["ROBOD"]),
                          ("towt_timeordered", "time-ordered split", COLORS["BDG2"])):
        ax.scatter(real.clip(upper=100), m[f"{est}_cvrmse"].clip(upper=100), s=6, color=c, alpha=0.7, label=label)
    ax.plot([0, 100], [0, 100], color=INK2, lw=0.8, ls="--")
    ax.set_xlabel("Realized 2017 CV(RMSE), %"); ax.set_ylabel("CV(RMSE) estimated from 2016, %")
    ax.set_ylim(-3, 132); ax.set_yticks(range(0, 101, 20))  # headroom above the clipped values for the legend
    ax.legend(frameon=False, fontsize=8, loc="upper left", title="Estimate from", title_fontsize=8, alignment="left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"mv_estimate.{ext}")
    plt.close(fig)


# ----- E4 lifecycle (BDG2) ----------------------------------------------------------------------
ARM_LABEL = {"static": "Static", "monthly": "Monthly", "quarterly": "Quarterly", "drift_1.1": "Drift 1.1",
             "drift_1.25": "Drift 1.25", "drift_1.5": "Drift 1.5", "drift_2.0": "Drift 2.0",
             "gated_1.5": "Gated 1.5", "gated_1.5_fallback": "Gated + fallback", "persistence": "Persistence"}


def lifecycle_tables():
    lc = pd.read_csv(R3 / "lifecycle_bdg2.csv")
    lc["cv"] = 100 * lc["mean_monthly_rmse"] / lc["mean_load"]
    piv = lc.pivot(index="building", columns="arm", values="mean_monthly_rmse")
    key("lc_buildings", len(piv))
    rows = []
    for arm in ARM_LABEL:
        if arm not in piv or arm == "monthly":
            continue
        rel = piv[arm] / piv["monthly"] - 1
        boots = [np.median(rel.to_numpy()[RNG.integers(0, len(rel), len(rel))]) for _ in range(B)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        sub = lc[lc["arm"] == arm]
        rows.append({"Policy": ARM_LABEL[arm],
                     "Mean monthly RMSE vs monthly retraining, median (95% CI)": f"{100 * rel.median():+.1f}% ({100 * lo:+.1f} to {100 * hi:+.1f})".replace("-", MINUS),
                     "Buildings worse than monthly": f"{int((rel > 0.001).sum())}/{len(rel)}",
                     "Retrains advised (promoted), median": (f"{sub['advised'].median():.0f} ({sub['promoted'].median():.0f})"
                                                              if sub["advised"].notna().any() else "–")})
        key(f"lc_{arm}_vs_monthly_median_pct", round(100 * rel.median(), 2), "%")
        key(f"lc_{arm}_vs_monthly_lo_pct", round(100 * lo, 2), "%"); key(f"lc_{arm}_vs_monthly_hi_pct", round(100 * hi, 2), "%")
        key(f"lc_{arm}_worse_than_monthly", int((rel > 0.001).sum()))
        if sub["advised"].notna().any():
            key(f"lc_{arm}_advised_total", int(sub["advised"].sum())); key(f"lc_{arm}_promoted_total", int(sub["promoted"].sum()))
        if "pooled_rmse" in lc:
            pp = lc.pivot(index="building", columns="arm", values="pooled_rmse")
            relp = pp[arm] / pp["monthly"] - 1
            key(f"lc_{arm}_pooled_vs_monthly_median_pct", round(100 * relp.median(), 2), "%")
            rows[-1]["Pooled RMSE vs monthly, median"] = f"{100 * relp.median():+.1f}%".replace("-", MINUS)
    write("v3_lifecycle", pd.DataFrame(rows))
    a = pd.read_csv(R3 / "gate_audit_bdg2.csv")
    key("audit_all_models", len(a)); key("audit_baseline_chosen", int((a["chosen"] == a["reference"]).sum()))
    # a kept baseline is its own reference (realized skill 0 by definition): audit machine-learning models only
    a = a[(a["chosen"] != a["reference"]) & a["realized_skill_3m"].notna()]
    prom, real = a["gates_passed"].astype(bool), a["realized_skill_3m"]
    rows = []
    for thr in (0.0, 0.05, 0.10):
        rows.append({"Realized-skill threshold": f"{thr:.2f}",
                     "Promoted, realized ≥ threshold": f"{int((prom & (real >= thr)).sum())}/{int(prom.sum())}",
                     "Promoted, realized < 0": f"{int((prom & (real < 0)).sum())}/{int(prom.sum())}",
                     "Refused, realized ≥ threshold": f"{int((~prom & (real >= thr)).sum())}/{int((~prom).sum())}"})
        key(f"audit_false_refusal_{thr}", int((~prom & (real >= thr)).sum()))
        key(f"audit_true_promotion_{thr}", int((prom & (real >= thr)).sum()))
    key("audit_models", len(a)); key("audit_promoted", int(prom.sum())); key("audit_refused", int((~prom).sum()))
    key("audit_false_promotion", int((prom & (real < 0)).sum()))
    key("audit_promoted_realized_median", round(float(real[prom].median()), 3))
    key("audit_true_promotion_share_0.05_pct", round(100 * float((prom & (real >= 0.05)).sum() / prom.sum()), 1), "%")
    key("audit_false_refusal_share_0.05_pct", round(100 * float((~prom & (real >= 0.05)).sum() / (~prom).sum()), 1), "%")
    key("audit_refused_realized_median", round(float(real[~prom].median()), 3))
    key("audit_test_realized_spearman", round(float(st.spearmanr(a["test_skill"], real, nan_policy="omit").statistic), 3))
    write("v3_gate_audit", pd.DataFrame(rows))
    # figure
    order = [k for k in ARM_LABEL if k in piv and k != "monthly"]
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for i, arm in enumerate(order):
        rel = 100 * (piv[arm] / piv["monthly"] - 1)
        ax.scatter(rel.clip(-30, 60), i + RNG.uniform(-0.18, 0.18, len(rel)), s=7, color=COLORS["BDG2"], alpha=0.6)
        ax.plot([rel.median()] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(order)), [ARM_LABEL[a] for a in order]); ax.invert_yaxis()
    ax.set_xlabel("Mean monthly RMSE relative to monthly retraining, % (per building; bar: median; clipped −30 to 60)")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"lifecycle_bdg2.{ext}")
    plt.close(fig)


# ----- E4 lifecycle (Aalborg, illustrative case) ------------------------------------------------
def aalborg_lifecycle():
    folder = R3 / "lifecycle_aalborg"
    lc = pd.read_csv(folder / "lifecycle.csv")
    lc["persistence_rmse"] = lc["production_persistence_rmse"]
    naive = folder / "lifecycle_naive.csv"
    if naive.exists():
        lc = lc.merge(pd.read_csv(naive)[["task", "month", "naive_rmse"]], on=["task", "month"], how="left")
    else:
        lc["naive_rmse"] = np.nan
    parts = []
    for _, d in lc.groupby("task", sort=False):
        d = d.sort_values("month").copy()
        worse = (d["production_skill"] < 0).shift(1, fill_value=False).astype(bool)
        d["fallback_uses_persistence"] = worse
        d["fallback_rmse"] = np.where(worse, d["persistence_rmse"], d["production_rmse"])
        parts.append(d)
    lc = pd.concat(parts, ignore_index=True)
    summary = []
    for task, d in lc.groupby("task", sort=False):
        row = {"Task": task}
        for col, label in (("static_rmse", "Static"), ("naive_rmse", "Monthly retrain"),
                           ("production_rmse", "Monitored + gated"), ("persistence_rmse", "Persistence"),
                           ("fallback_rmse", "Gated + fallback")):
            row[label] = f"{d[col].mean():#.3g}" if d[col].notna().any() else "–"
        row["Months gated model beat persistence"] = f"{int((d['production_rmse'] < d['persistence_rmse']).sum())}/{len(d)}"
        row["Retrains advised (promoted)"] = f"{int(d['retrain_recommended'].sum())} ({int(d['promoted'].sum())})"
        summary.append(row)
        slug = "dh" if "heating" in task.lower() else "co2"
        for col, label in (("static_rmse", "static"), ("naive_rmse", "monthly"), ("production_rmse", "gated"),
                           ("persistence_rmse", "persistence"), ("fallback_rmse", "fallback")):
            if d[col].notna().any():
                key(f"lc_aalborg_{slug}_{label}_mean_rmse", round(float(d[col].mean()), 3))
        key(f"lc_aalborg_{slug}_promoted", int(d["promoted"].sum()))
        key(f"lc_aalborg_{slug}_advised", int(d["retrain_recommended"].sum()))
        key(f"lc_aalborg_{slug}_months_beat_persistence", int((d["production_rmse"] < d["persistence_rmse"]).sum()))
    write("v3_lifecycle_aalborg", pd.DataFrame(summary))
    tab = lc[["task", "month", "production_version", "static_rmse", "naive_rmse", "production_rmse",
              "persistence_rmse", "fallback_rmse", "drift_ratio", "retrain_recommended", "promoted"]].copy()
    for c in ("static_rmse", "naive_rmse", "production_rmse", "persistence_rmse", "fallback_rmse"):
        tab[c] = tab[c].map(lambda v: f"{v:#.3g}" if pd.notna(v) else "")
    tab["fallback_rmse"] = [f"{v} (P)" if u else v for v, u in zip(tab["fallback_rmse"], lc["fallback_uses_persistence"])]
    for c in ("retrain_recommended", "promoted"):
        tab[c] = tab[c].map({True: "yes", False: "no"}).fillna(tab[c])
    tab["drift_ratio"] = tab["drift_ratio"].map(lambda v: f"{v:.2f}")
    tab = tab.rename(columns={"task": "Task", "month": "Month", "production_version": "Version", "static_rmse": "Static",
                              "naive_rmse": "Monthly retrain", "production_rmse": "Monitored + gated",
                              "persistence_rmse": "Persistence", "fallback_rmse": "Gated + fallback",
                              "drift_ratio": "Drift ratio", "retrain_recommended": "Retrain advised",
                              "promoted": "Promoted"})
    for slug, sel in (("dh", tab["Task"].str.contains("heating", case=False)),
                      ("co2", ~tab["Task"].str.contains("heating", case=False))):
        write(f"s_lifecycle_aalborg_{slug}", tab[sel].drop(columns=["Task"]))


# ----- Supplementary: every task, issue types ---------------------------------------------------
def all_tasks_table(df: pd.DataFrame):
    d = df[df["status"] == "fitted"].copy()
    d["order"] = d["dataset"].map({"BDG2": 0, "ROBOD": 1, "Aalborg": 2})
    d = d.sort_values(["order", "task"])
    out = pd.DataFrame({
        "Task": d["task"].str.replace("bdg2-", "", regex=False),
        "Chosen": d["chosen"].str.replace("_", " "),
        "Reference": d["baseline"].str.replace("_", " "),
        "Skill (95% CI)": [f"{num(s)} ({num(lo)} to {num(hi)})" if pd.notna(lo) else num(s)
                           for s, lo, hi in zip(d["skill"], d["skill_lo"], d["skill_hi"])],
        "DM": np.where(d["better"], "better", ""),
        "Backtest": d["backtest_skill"].map(lambda v: num(v)),
        "Coverage": d["interval_coverage"].map(lambda v: f"{100 * v:.0f}%" if pd.notna(v) else "–"),
        "Test days": d["test_days"].map(lambda v: f"{v:.0f}" if pd.notna(v) else "–"),
        "Gates": np.where(d["gates_passed"].astype(bool), "passed",
                          "refused: " + d["failed_gates"].fillna("").str.replace(";", ", ")),
    })
    write("s_all_tasks_v3", out)


def issue_types(tests: pd.DataFrame, df: pd.DataFrame):
    """Warnings and errors raised on the untouched data, by type (an issue on a column counts once per dataset)."""
    fit = df[df["status"] == "fitted"][["task", "dataset", "cluster", "site", "target"]].merge(
        tests[["task", "issues"]], on="task")
    rows = {}
    for ds, d in fit.groupby("dataset"):
        ids = set()
        for _, r in d.iterrows():
            for i in r["issues"]:
                kind, col = (i.split(":", 1) + [""])[:2]
                if ds == "BDG2":
                    src = r["cluster"] if col == r["target"] else f"site {r['site']}"
                else:
                    src = r["cluster"] if ds == "ROBOD" else "Aalborg"
                ids.add((src, col, kind))
        kinds = pd.Series([k for _, _, k in ids]).value_counts()
        rows[ds] = kinds
        key(f"issues_{ds}_distinct", len(ids))
        if ds == "BDG2":
            meters = {s for s, c, k in ids if not s.startswith("site ")}
            key("issues_BDG2_meters_flagged", len(meters))
            key("issues_BDG2_meters_stuck", len({s for s, c, k in ids if not s.startswith("site ") and k == "stuck"}))
            key("issues_BDG2_sites_flagged", len({s for s, c, k in ids if s.startswith("site ")}))
    t = pd.DataFrame(rows).reindex(columns=["BDG2", "ROBOD", "Aalborg"]).fillna(0).astype(int)
    t = t.sort_values("BDG2", ascending=False).reset_index().rename(columns={"index": "Issue type"})
    write("v3_issue_types", t)


# ----- Exploratory (not in the pre-specified plan): daily peak demand on BDG2 --------------------
def peak_exploratory(df: pd.DataFrame):
    """Error of the day-ahead forecast of each day's peak hourly demand, model vs its reference baseline."""
    rows = []
    for _, t in df[(df["dataset"] == "BDG2") & (df["status"] == "fitted")].iterrows():
        rec = json.loads((RUNS / "bdg2" / t["run"] / "run.json").read_text(encoding="utf-8"))
        p = pd.read_csv(RUNS / "bdg2" / t["run"] / "test_predictions.csv", index_col=0)
        base = rec["test"]["baseline"]["name"]
        day = p.index.astype(str).str[:10]
        g = p.groupby(day)
        full = g["actual"].count() >= 20
        peak = g["actual"].max()[full]
        if len(peak) < 7 or (peak <= 0).any():
            continue
        e_m = (g["predicted"].max()[full] - peak).abs() / peak
        e_b = (g[base].max()[full] - peak).abs() / peak
        rows.append({"building": t["building"], "ml": t["chosen"] != t["baseline"], "days": len(peak),
                     "model": e_m.mean(), "reference": e_b.mean()})
    r = pd.DataFrame(rows)
    ml = r[r["ml"]]
    key("peak_buildings", len(r)); key("peak_ml_buildings", len(ml))
    key("peak_model_mape_median_pct", round(100 * ml["model"].median(), 1), "%")
    key("peak_reference_mape_median_pct", round(100 * ml["reference"].median(), 1), "%")
    key("peak_model_better", int((ml["model"] < ml["reference"]).sum()))
    write("v3_peak", pd.DataFrame([{
        "Buildings with a machine-learning model": len(ml),
        "Daily-peak error, model, median": f"{100 * ml['model'].median():.1f}%",
        "Daily-peak error, reference, median": f"{100 * ml['reference'].median():.1f}%",
        "Model better": f"{int((ml['model'] < ml['reference']).sum())}/{len(ml)}"}]))


# ----- Exploratory (not in the plan): whole-building meters that read zero for a week or more ------
def zero_stretches(df: pd.DataFrame) -> pd.DataFrame:
    """Per BDG2 building: hours in stretches of >= 168 h below 1% of the building's median reading,
    over 2016-2017 and inside the test window. A whole-building meter does not idle at zero for a week."""
    b = df[(df["dataset"] == "BDG2") & (df["status"] == "fitted")]
    raw = pd.read_csv(REPO / "data" / "raw" / "bdg2" / "electricity_cleaned.csv", parse_dates=["timestamp"],
                      index_col="timestamp", usecols=["timestamp"] + list(b["building"]))
    rows = []
    for _, r in b.iterrows():
        s = raw[r["building"]]
        low = (s <= 0.01 * s[s > 0].median()) & s.notna()
        run_id = (low != low.shift()).cumsum()
        lengths = low.groupby(run_id).transform("size")
        dead = low & (lengths >= 168)
        rec = json.loads((RUNS / "bdg2" / r["run"] / "run.json").read_text(encoding="utf-8"))
        t0, t1 = (pd.Timestamp(x) for x in rec["split"]["bounds"]["test"])
        rows.append({"building": r["building"], "dead_hours": int(dead.sum()),
                     "dead_hours_test": int(dead[t0:t1].sum()), "dead_hours_2017": int(dead["2017"].sum()),
                     "dead_hours_2016": int(dead["2016"].sum())})
    z = pd.DataFrame(rows)
    z.to_csv(R3 / "bdg2_zero_stretches.csv", index=False)
    key("zero_buildings_any", int((z["dead_hours"] > 0).sum()))
    key("zero_buildings_test", int((z["dead_hours_test"] > 0).sum()))
    key("zero_buildings_sites", int(b.set_index("building").loc[z.loc[z["dead_hours"] > 0, "building"], "site"].nunique()))
    return z


PIPELINE_LABEL = {
    "clean data (reference)": "Clean data, framework preparation",
    "clean data, unguarded script": "Clean data, quick script",
    "faulty data, unguarded script": "Faulty data, quick script",
    "faulty data, unguarded script + same unit fix": "Faulty data, quick script + unit fix",
    "faulty data, competent script + same unit fix": "Faulty data, competent script + unit fix",
    "faulty data, bemlops": "Faulty data, framework (after unit fix)",
}


# ----- E3 faults and false alarms ----------------------------------------------------------------
def fault_tables(tests: pd.DataFrame, df: pd.DataFrame):
    f = R3 / "faults"
    rate = pd.read_csv(f / "fault_detection_rate.csv")
    det = pd.read_csv(f / "fault_detection.csv")
    how = det[det["detected"]].groupby("fault")["as"].agg(lambda s: s.mode().iat[0] if len(s) else "")
    rate["Detected as"] = rate["fault"].map(how).fillna("").str.replace(r"\s*\(\w+\)$", "", regex=True)
    rate["Detection rate"] = rate["detection_rate"].map(lambda v: f"{v:.0%}")
    write("v3_fault_detection", rate[["fault", "Detected as", "Detection rate"]].rename(columns={"fault": "Planted fault"}))
    cost = pd.read_csv(f / "fault_cost.csv")
    t = pd.read_csv(f / "fault_tests.csv")
    rows = []
    for arm, d in cost.groupby("pipeline", sort=False):
        r = {"Pipeline": PIPELINE_LABEL.get(arm, arm), "RMSE (ppm)": f"{d['rmse_ppm'].mean():.1f} ± {d['rmse_ppm'].std():.1f}",
             "MAE (ppm)": f"{d['mae_ppm'].mean():.1f} ± {d['mae_ppm'].std():.1f}"}
        for metric, lab in (("mae_ppm", "ΔMAE vs framework (p)"), ("rmse_ppm", "ΔRMSE vs framework (p)")):
            s = t[(t["comparison"] == f"{arm} vs bemlops") & (t["metric"] == metric)]
            r[lab] = f"{num(s['median_difference'].iat[0], '+.2f')} ({fmt_p(s['p_value'].iat[0])})" if len(s) else "–"
        rows.append(r)
        key(f"faults_{arm}_mae_mean", round(d["mae_ppm"].mean(), 2), "ppm")
        key(f"faults_{arm}_rmse_mean", round(d["rmse_ppm"].mean(), 2), "ppm")
        for metric in ("mae_ppm", "rmse_ppm"):
            s = t[(t["comparison"] == f"{arm} vs bemlops") & (t["metric"] == metric)]
            if len(s):
                key(f"faults_{arm}_minus_framework_{metric}_median", round(float(s["median_difference"].iat[0]), 2), "ppm")
                key(f"faults_{arm}_minus_framework_{metric}_p", round(float(s["p_value"].iat[0]), 4))
    write("v3_fault_cost", pd.DataFrame(rows))
    # false alarms on untouched data: warning/error issues per series-month
    fa = []
    for _, r in df[df["status"] == "fitted"].iterrows():
        tt = tests.set_index("task").loc[r["task"]]
        n_cols = max(1, len(set(i.split(":", 1)[1] for i in tt["issues"] if ":" in i)) or 1)
        fa.append({"dataset": r["dataset"], "task": r["task"], "issues": len(tt["issues"])})
    fa = pd.DataFrame(fa)
    write("v3_issue_counts", fa.groupby("dataset")["issues"].describe()[["count", "50%", "max"]].reset_index()
          .rename(columns={"count": "Tasks", "50%": "Warnings per task, median", "max": "Max"}))


# ----- main --------------------------------------------------------------------------------------
def main() -> None:
    # 1100 dpi keeps full-width charts above the 7480 px Elsevier asks for bitmap line art; TrueType fonts in PDFs
    plt.rcParams.update({"font.family": "Arial", "font.size": 9, "savefig.dpi": 1100, "pdf.fonttype": 42})
    TABLES.mkdir(exist_ok=True); FIGS.mkdir(exist_ok=True); R3.mkdir(exist_ok=True)
    df = load_tasks()
    tests = per_task_tests(df)
    tests.drop(columns=["issues"]).to_csv(R3 / "dm_tests.csv", index=False)
    df = df.merge(tests[["task", "better", "better_hln", "better_bh", "p_value", "skill_lo", "skill_hi",
                         "masked_target", "rows_raw"]], on="task", how="left")
    df["better"] = df["better"].fillna(False).astype(bool)
    df.to_csv(R3 / "tasks_v3.csv", index=False)
    write("v3_e1", table_e1(df))
    write("v3_targets", table_targets(df))
    write("v3_references", table_references(df))
    write("v3_gates", gate_sensitivity(df))
    fig_skill(df)
    fig_bdg2(df)
    fit = df[df["status"] == "fitted"]
    key("e1_better_hln", int(fit["better_hln"].fillna(False).sum())); key("e1_better_bh", int(fit["better_bh"].fillna(False).sum()))
    key("e1_better", int(fit["better"].sum())); key("e1_tasks", len(fit))
    e = fit[fit["energy"] & fit["g14_pass"].notna()]
    key("e1_energy_g14_model", int(e["g14_pass"].astype(bool).sum())); key("e1_energy_g14_base", int(e["base_g14_pass"].fillna(False).astype(bool).sum()))
    key("e1_energy_tasks", len(e))
    b = fit[fit["dataset"] == "BDG2"]
    key("bdg2_g14_model", int(b["g14_pass"].astype(bool).sum())); key("bdg2_g14_base", int(b["base_g14_pass"].fillna(False).astype(bool).sum()))
    key("bdg2_masked_share_median", round(float((b["masked_target"] / b["rows_raw"]).median()), 4))
    key("bdg2_masked_any", int((b["masked_target"] > 0).sum()))
    share = b["masked_target"] / b["rows_raw"]
    key("bdg2_masked_share_median_if_any_pct", round(100 * float(share[b["masked_target"] > 0].median()), 2), "%")
    key("bdg2_masked_share_max_pct", round(100 * float(share.max()), 2), "%")
    all_tasks_table(df)
    try:
        z = zero_stretches(df)
        dead = set(z.loc[z["dead_hours_test"] > 0, "building"])
        mostly_masked = set(b.loc[b["masked_target"] / b["rows_raw"] > 0.5, "building"])
        key("bdg2_mostly_masked", len(mostly_masked))
        key("bdg2_mostly_masked_sites", int(b[b["building"].isin(mostly_masked)]["site"].nunique()))
        clean = b[~b["building"].isin(dead | mostly_masked)]
        key("e1_bdg2_fit_tasks", len(clean))
        key("e1_bdg2_fit_better_dm_pct", round(100 * clean["better"].mean(), 1), "%")
        lo_hi = cluster_ci(clean["better"], clean["cluster"])
        key("e1_bdg2_fit_better_dm_lo", round(100 * lo_hi[1], 1), "%"); key("e1_bdg2_fit_better_dm_hi", round(100 * lo_hi[2], 1), "%")
        key("e1_bdg2_fit_skill_median", round(float(clean["skill"].median()), 3))
        key("e1_bdg2_fit_promoted", int(clean["gates_passed"].astype(bool).sum()))
        key("e1_bdg2_fit_baseline_kept", int((clean["chosen"] == clean["baseline"]).sum()))
    except FileNotFoundError as err:
        print(f"zero stretches: skipped ({err})")
    peak_exploratory(df)
    issue_types(tests, df)
    for name, fn in (("protocol", protocol_tables), ("mv", mv_tables), ("lifecycle", lifecycle_tables),
                     ("lifecycle_aalborg", aalborg_lifecycle)):
        try:
            fn()
        except FileNotFoundError as err:
            print(f"{name}: skipped ({err})")
    try:
        fault_tables(tests, df)
    except FileNotFoundError as err:
        print(f"faults: skipped ({err})")
    pd.DataFrame(KEY).to_csv(R3 / "key_numbers.csv", index=False)
    print(f"Wrote {len(KEY)} key numbers, tables and figures")


if __name__ == "__main__":
    main()
