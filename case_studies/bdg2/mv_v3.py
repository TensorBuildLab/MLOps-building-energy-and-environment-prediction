"""E5 (v3): measurement-and-verification pseudo-savings test on BDG2 (ANALYSIS_PLAN_v3.md).

For each building of the pre-specified sample with >= 90% of hourly electricity present in both 2016 and 2017:
baseline period 2016, reporting period 2017, no efficiency measure installed (so the true savings are zero).
  framework   bemlops in estimation mode (h = 0: concurrent weather and calendar, no target lags), its usual
              time-ordered selection within 2016 among ridge, gradient boosting and the no-ML baselines
              (training mean, profiles, TOWT); the chosen configuration is refitted on all of 2016
  towt        time-of-week-and-temperature regression fitted on all of 2016
Outcomes in 2017: normalized annual pseudo-savings error (NASE = (sum predicted - sum metered) / sum metered),
hourly CV(RMSE) and NMBE. Protocol link (TOWT): baseline-period CV(RMSE) estimated in-sample, by shuffled and
blocked 5-fold CV and by the time-ordered split (last 15% of 2016), against the realized 2017 value.

Run:  python case_studies/bdg2/mv_v3.py <part>/<parts>   then   python case_studies/bdg2/mv_v3.py merge
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import run as bdg  # noqa: E402

import bemlops  # noqa: E402
from bemlops.metrics import regression_metrics  # noqa: E402
from bemlops.models import TOWTBaseline  # noqa: E402
from bemlops.governance import check_gates  # noqa: E402
from bemlops.report import build_record, package_fingerprint  # noqa: E402

OUT = HERE.parent / "results_v3"
Y0, Y1 = pd.Timestamp("2016-01-01"), pd.Timestamp("2017-01-01")
Y2 = pd.Timestamp("2018-01-01")
LIMITS = (30.0, 10.0)  # hourly CV(RMSE) and |NMBE| limits used as a familiar threshold


def verdict(m) -> bool:
    return bool(m["cvrmse_pct"] <= LIMITS[0] and abs(m["nmbe_pct"]) <= LIMITS[1])


def outcome(y: pd.Series, p) -> dict:
    p = pd.Series(np.asarray(p, dtype=float), index=y.index)
    ok = y.notna() & p.notna()
    m = regression_metrics(y[ok], p[ok])
    return {"cvrmse": m["cvrmse_pct"], "nmbe": m["nmbe_pct"], "nase": float((p[ok].sum() - y[ok].sum()) / y[ok].sum()),
            "hours": int(ok.sum())}


def towt_cv(X: pd.DataFrame, y: pd.Series, folds) -> dict:
    pred = pd.Series(np.nan, index=y.index)
    for tr, te in folds:
        pred.iloc[te] = TOWTBaseline("airTemperature").fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])
    m = regression_metrics(y, pred)
    return {"cvrmse": m["cvrmse_pct"], "nmbe": m["nmbe_pct"]}


def eligible(picks: pd.DataFrame, elec: pd.DataFrame) -> pd.DataFrame:
    cov16 = elec[(elec.index >= Y0) & (elec.index < Y1)].notna().mean()
    cov17 = elec[(elec.index >= Y1) & (elec.index < Y2)].notna().mean()
    ok = picks["building_id"].map(lambda b: cov16[b] >= 0.9 and cov17[b] >= 0.9)
    return picks[ok]


def one(b, elec, weather) -> dict:
    bid, site = b["building_id"], b["site_id"]
    df = bdg.building_frame(bid, site, elec, weather)
    base, rep = df[df.index < Y1], df[(df.index >= Y1) & (df.index < Y2)]
    t0 = time.time()
    p = bemlops.Project(base, "electricity", bdg.COLUMNS, horizon=0, name=f"mv-{bid}",
                        intended_use="M&V baseline: hourly electricity from concurrent weather and calendar.")
    for n in bdg.NOTES:
        p.note(n)
    p.check_data()
    if p.unresolved():
        return {"building": bid, "status": "blocked"}
    p.prepare(freq="1h")
    r = p.fit(n_iter=3, models=("ridge", "gbm"), backtest_blocks=0, refit_all=True)
    rec = build_record(p, "mv")
    rec["gates"] = check_gates(rec)
    window = df[(df.index >= Y1 - pd.Timedelta(days=8)) & (df.index < Y2)]
    pf = r.model.predict(window, future=False, validate=False)
    pf = pf[(pf.index >= Y1) & (pf.index < Y2)]
    y17 = pf["actual"]
    fw = outcome(y17, pf["predicted"])
    # TOWT on hourly data (temperature gaps filled forward up to 3 h, as preparation would)
    Xb = base[["airTemperature"]].ffill(limit=3)
    yb = base["electricity"]
    okb = yb.notna()
    Xb, yb = Xb[okb], yb[okb]
    towt = TOWTBaseline("airTemperature").fit(Xb, yb)
    Xr = rep[["airTemperature"]].ffill(limit=3).reindex(y17.index)
    tw = outcome(y17, towt.predict(Xr))
    insample = regression_metrics(yb, towt.predict(Xb))
    n = len(yb)
    shuffled = towt_cv(Xb, yb, list(KFold(5, shuffle=True, random_state=0).split(Xb)))
    blocks = np.array_split(np.arange(n), 5)
    blocked = towt_cv(Xb, yb, [(np.setdiff1d(np.arange(n), te), te) for te in blocks])
    cut = int(0.85 * n)
    t_split = TOWTBaseline("airTemperature").fit(Xb.iloc[:cut], yb.iloc[:cut])
    timeord = regression_metrics(yb.iloc[cut:], t_split.predict(Xb.iloc[cut:]))
    g14 = rec["test"].get("guideline14") or {}
    out = {
        "building": bid, "site": site, "primary_use": b["primaryspaceusage"], "status": "fitted",
        "chosen": r.chosen, "reference": r.baseline_name,
        "fw_test_cvrmse_2016": g14.get("cvrmse_pct"), "fw_test_nmbe_2016": g14.get("nmbe_pct"),
        "fw_gates_passed": all(g["passed"] for g in rec["gates"].values()),
        "fw_failed_gates": ";".join(k for k, g in rec["gates"].items() if not g["passed"]),
        **{f"fw_{k}": v for k, v in fw.items()}, **{f"towt_{k}": v for k, v in tw.items()},
        "towt_insample_cvrmse": insample["cvrmse_pct"], "towt_insample_nmbe": insample["nmbe_pct"],
        "towt_shuffled_cvrmse": shuffled["cvrmse"], "towt_shuffled_nmbe": shuffled["nmbe"],
        "towt_blocked_cvrmse": blocked["cvrmse"], "towt_blocked_nmbe": blocked["nmbe"],
        "towt_timeordered_cvrmse": timeord["cvrmse_pct"], "towt_timeordered_nmbe": timeord["nmbe_pct"],
        "mean_2016": float(yb.mean()), "mean_2017": float(y17.mean()),
        "nonroutine_flag": bool(abs(y17.mean() / yb.mean() - 1) > 0.3),
        "package_fingerprint": package_fingerprint(), "seconds": round(time.time() - t0, 1),
    }
    return out


def main(part: int, parts: int) -> None:
    picks, elec, weather, _ = bdg.sample(200, 0)
    todo = eligible(picks, elec)
    OUT.mkdir(exist_ok=True)
    rows = []
    for i, (_, b) in enumerate(todo.iterrows()):
        if i % parts != part:
            continue
        try:
            r = one(b, elec, weather)
        except Exception as e:  # report and continue; every building is accounted for
            r = {"building": b["building_id"], "status": f"error: {type(e).__name__}: {e}"}
        r["order"] = int(b["order"])
        rows.append(r)
        print(f"{r['building']}: {r['status']} NASE fw {r.get('fw_nase', float('nan')):+.3f} "
              f"towt {r.get('towt_nase', float('nan')):+.3f}", flush=True)
        pd.DataFrame(rows).to_csv(OUT / f"mv_part{part}.csv", index=False)


def merge() -> None:
    parts = sorted(OUT.glob("mv_part*.csv"))
    pd.concat([pd.read_csv(f) for f in parts]).sort_values("order").to_csv(OUT / "mv.csv", index=False)
    for f in parts:
        f.unlink()
    print("merged", len(parts))


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge()
    else:
        i, k = map(int, sys.argv[1].split("/"))
        main(i, k)
