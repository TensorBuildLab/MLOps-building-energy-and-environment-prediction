"""E4 (v3): deployment, monitoring and retraining across BDG2 buildings, with a gate audit (ANALYSIS_PLAN_v3.md).

Buildings: the first 50 of the pre-specified sample with >= 90% of hourly electricity in both 2016 and 2017.
Task: hourly electricity 24 h ahead. For each month m of 2017, one model is fitted on all data before that month
(same settings for every month), so model 0 is trained on 2016 only. Every model's hourly predictions, and its
reference baseline's, are saved from September 2016 to December 2017; the retraining policies are then simulated
from these predictions (`simulate`), which is equivalent to running each policy because a model trained on the
same data with the same settings and seed is the same model whichever policy asked for it.

Run:  python case_studies/bdg2/lifecycle_v3.py fit <part>/<parts>     (fits; saves runs/v3/lifecycle_bdg2/)
      python case_studies/bdg2/lifecycle_v3.py simulate             (policies and gate audit -> results_v3/)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import mv_v3  # noqa: E402
import run as bdg  # noqa: E402

import bemlops  # noqa: E402
from bemlops.governance import check_gates  # noqa: E402
from bemlops.report import build_record, package_fingerprint  # noqa: E402

WORK = bdg.REPO / "runs" / "v3" / "lifecycle_bdg2"
OUT = HERE.parent / "results_v3"
MONTHS = pd.date_range("2017-01-01", "2017-12-01", freq="MS")
SAVE_FROM = pd.Timestamp("2016-08-24")
N_BUILDINGS = 50
TOLERANCES = (1.1, 1.25, 1.5, 2.0)


def buildings():
    picks, elec, weather, _ = bdg.sample(200, 0)
    return mv_v3.eligible(picks, elec).head(N_BUILDINGS), elec, weather


def fit_building(b, elec, weather) -> None:
    bid, site = b["building_id"], b["site_id"]
    out_csv, out_json = WORK / f"{bid}.csv", WORK / f"{bid}.json"
    if out_json.exists():
        return
    df = bdg.building_frame(bid, site, elec, weather)
    df = df[df.index < pd.Timestamp("2018-01-01")]
    window = df[df.index >= SAVE_FROM - pd.Timedelta(days=8)]
    preds = pd.DataFrame({"actual": df["electricity"]})
    preds["persistence"] = df["electricity"].shift(24)
    meta = {"building": bid, "site": site, "models": [], "package_fingerprint": package_fingerprint()}
    for k, start in enumerate(MONTHS):
        t0 = time.time()
        p = bemlops.Project(df[df.index < start], "electricity", bdg.COLUMNS, horizon="24h", name=f"lc-{bid}-{k}")
        p.check_data()
        if p.unresolved():
            meta["models"].append({"k": k, "status": "blocked"})
            continue
        p.prepare(freq="1h")
        r = p.fit(n_iter=3, models=("ridge", "gbm", "gbm_change"), backtest_blocks=0)
        rec = build_record(p, f"lc{k}")
        rec["gates"] = check_gates(rec)
        for col, model in ((f"m{k}", r.model), (f"r{k}", r.reference_model)):
            out = model.predict(window, future=False, validate=False)
            preds[col] = out["predicted"].reindex(preds.index)
        meta["models"].append({
            "k": k, "status": "fitted", "start": str(start), "chosen": r.chosen, "reference": r.baseline_name,
            "test_error": float(r.model.test_error), "train_end": str(r.model.train_end),
            "test_start": rec["split"]["bounds"]["test"][0], "skill": float(r.skill),
            "gates_passed": all(g["passed"] for g in rec["gates"].values()),
            "failed_gates": [g for g, v in rec["gates"].items() if not v["passed"]],
            "input_ranges": {c: list(v) for c, v in r.model.input_ranges.items()},
            "seconds": round(time.time() - t0, 1)})
        print(f"{bid} model {k}: {r.chosen} vs {r.baseline_name}, skill {r.skill:.3f}, "
              f"gates {'passed' if meta['models'][-1]['gates_passed'] else 'refused'} ({time.time() - t0:.0f} s)",
              flush=True)
    WORK.mkdir(parents=True, exist_ok=True)
    preds[preds.index >= SAVE_FROM].to_csv(out_csv)
    out_json.write_text(json.dumps(meta, indent=1), encoding="utf-8")


def fit_all(part: int, parts: int) -> None:
    todo, elec, weather = buildings()
    for i, (_, b) in enumerate(todo.iterrows()):
        if i % parts == part:
            fit_building(b, elec, weather)


# ----- simulation ---------------------------------------------------------------------------
def rmse(a, p) -> float:
    ok = np.isfinite(a) & np.isfinite(p)
    return float(np.sqrt(np.mean((a[ok] - p[ok]) ** 2))) if ok.sum() > 24 else float("nan")


def out_of_range(raw: pd.DataFrame, ranges: dict, lo: pd.Timestamp, hi: pd.Timestamp) -> bool:
    w = raw[(raw.index >= lo) & (raw.index < hi)]
    for c, (a, b) in ranges.items():
        if c in w.columns:
            v = w[c].dropna()
            margin = 0.1 * (b - a) if b > a else 0.0
            if len(v) and ((v < a - margin) | (v > b + margin)).mean() > 0.2:
                return True
    return False


def simulate_building(bid: str, raw: pd.DataFrame) -> tuple:
    preds = pd.read_csv(WORK / f"{bid}.csv", index_col=0, parse_dates=True)
    meta = json.loads((WORK / f"{bid}.json").read_text(encoding="utf-8"))
    models = {m["k"]: m for m in meta["models"] if m["status"] == "fitted"}
    a = preds["actual"].to_numpy(float)
    bounds = [(s, s + pd.offsets.MonthBegin(1)) for s in MONTHS]
    idx = preds.index

    def month_mask(m):
        lo, hi = bounds[m]
        return ((idx >= lo) & (idx < hi))

    def err(col, m):
        mask = month_mask(m)
        return rmse(a[mask], preds[col].to_numpy(float)[mask])

    served = {}
    n = len(MONTHS)
    served["static"] = [0] * n
    served["monthly"] = list(range(n))
    served["quarterly"] = [3 * (m // 3) for m in range(n)]

    def drift_policy(tol, gated):
        champ, out, advised, promoted = 0, [], 0, 0
        for m in range(n):
            out.append(champ)
            if m == n - 1 or champ not in models:
                continue
            ratio = err(f"m{champ}", m) / models[champ]["test_error"]
            oor = out_of_range(raw, models[champ]["input_ranges"], *bounds[m])
            if not (ratio > tol or oor):
                continue
            advised += 1
            ch = m + 1
            if ch not in models:
                continue
            if gated:
                if not models[ch]["gates_passed"]:
                    continue
                lo = pd.Timestamp(models[ch]["test_start"])
                mask = (idx >= lo) & (idx < MONTHS[ch])
                if rmse(a[mask], preds[f"m{ch}"].to_numpy(float)[mask]) >= rmse(a[mask], preds[f"m{champ}"].to_numpy(float)[mask]):
                    continue
            champ = ch
            promoted += 1
        return out, advised, promoted

    extra = {}
    for tol in TOLERANCES:
        served[f"drift_{tol}"], adv, pro = drift_policy(tol, gated=False)
        extra[f"drift_{tol}"] = (adv, pro)
    served["gated_1.5"], adv, pro = drift_policy(1.5, gated=True)
    extra["gated_1.5"] = (adv, pro)

    rows = []
    for arm, ks in served.items():
        monthly = [err(f"m{k}", m) for m, k in enumerate(ks)]
        rows.append({"building": bid, "arm": arm, "monthly_rmse": monthly,
                     "advised": extra.get(arm, (np.nan, np.nan))[0], "promoted": extra.get(arm, (np.nan, np.nan))[1]})
    pers = [err("persistence", m) for m in range(n)]
    rows.append({"building": bid, "arm": "persistence", "monthly_rmse": pers})
    # gated with persistence fallback: serve persistence in month m if the gated model lost to it in month m-1
    g = rows[[r["arm"] for r in rows].index("gated_1.5")]["monthly_rmse"]
    fb = [g[0]] + [pers[m] if g[m - 1] > pers[m - 1] else g[m] for m in range(1, n)]
    rows.append({"building": bid, "arm": "gated_1.5_fallback", "monthly_rmse": fb})
    # pooled RMSE per arm over 2017
    for r in rows:
        r["mean_monthly_rmse"] = float(np.nanmean(r["monthly_rmse"]))
        r["mean_load"] = float(np.nanmean(a[(idx >= MONTHS[0])]))

    # gate audit: each monthly model's decision against its realized skill vs its own reference, next 3 months
    audit = []
    for k, m in models.items():
        mask = (idx >= MONTHS[k]) & (idx < MONTHS[min(k + 3, n) - 1] + pd.offsets.MonthBegin(1))
        e_m = rmse(a[mask], preds[f"m{k}"].to_numpy(float)[mask])
        e_r = rmse(a[mask], preds[f"r{k}"].to_numpy(float)[mask])
        audit.append({"building": bid, "k": k, "chosen": m["chosen"], "reference": m["reference"],
                      "test_skill": m["skill"], "gates_passed": m["gates_passed"],
                      "failed_gates": ";".join(m["failed_gates"]),
                      "realized_skill_3m": 1 - e_m / e_r if e_r else np.nan})
    return rows, audit


def simulate() -> None:
    _, elec, weather = buildings()
    rows, audits = [], []
    for f in sorted(WORK.glob("*.json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        raw = bdg.building_frame(meta["building"], meta["site"], elec, weather)
        r, a = simulate_building(meta["building"], raw)
        rows += r
        audits += a
    df = pd.DataFrame(rows)
    df["monthly_rmse"] = df["monthly_rmse"].map(lambda v: ";".join(f"{x:.5g}" for x in v))
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "lifecycle_bdg2.csv", index=False)
    pd.DataFrame(audits).to_csv(OUT / "gate_audit_bdg2.csv", index=False)
    print(f"Simulated {df['building'].nunique()} buildings")


if __name__ == "__main__":
    if sys.argv[1] == "fit":
        i, k = map(int, sys.argv[2].split("/"))
        fit_all(i, k)
    else:
        simulate()
