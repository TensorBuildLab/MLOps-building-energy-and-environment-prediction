"""E2 (v3): evaluation protocol on the same model, inputs and rows (ANALYSIS_PLAN_v3.md).

Tasks: the regression tasks of ROBOD Rooms 4-5 and of Aalborg Room A and its building systems (22), and the
first 40 buildings of the pre-specified BDG2 sample (hourly electricity, 24 h ahead).
Arms (one random forest, k = 5):
  shuffled_cv              k-fold with shuffled rows (the random split of the preliminary study)
  selection_all_rows       shuffled CV after univariate feature selection on all rows (half the inputs)
  selection_in_fold        shuffled CV with the same selection fitted inside each training fold (control)
  blocked_cv               k contiguous blocks; training excludes a buffer (longest look-back + horizon) around
                           the test block
  forward_chaining         test blocks = blocked folds 2..k; training only on earlier rows, minus the buffer
Metrics: RMSE and R2 on all rows; RMSE of shuffled, blocked and forward on the identical rows of folds 2..k;
hourly CV(RMSE) and NMBE (BDG2); per-fold RMSE.

Run:  python case_studies/protocol_v3.py <part>/<parts>   then   python case_studies/protocol_v3.py merge
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

import bemlops  # noqa: E402
from bemlops.features import build_features, target_shifts  # noqa: E402
from bemlops.metrics import regression_metrics  # noqa: E402

OUT = HERE / "results_v3"
K = 5


def prepared(df, target, columns, horizon, name, notes=(), drop=(), freq="15min", accept=None):
    cols = {k: v for k, v in columns.items() if k in df.columns and k not in drop}
    p = bemlops.Project(df, target, cols, horizon=horizon, name=name)
    for n in notes:
        p.note(n)
    rep = p.check_data()
    for issue_id, reason in (accept or {}).items():
        if any(i.id == issue_id for i in rep.issues):
            p.accept(issue_id, reason)
    if p.unresolved():
        return None
    p.prepare(freq=freq)
    return p


def _metrics(y, pred) -> Dict[str, float]:
    m = regression_metrics(y, pred)
    return {k: m.get(k, np.nan) for k in ("rmse", "r2", "cvrmse_pct", "nmbe_pct")}


def compare(p, seed: int = 0) -> Dict[str, Any]:
    h, step = p.horizon_steps, p.step
    lags = target_shifts(h, step, len(p.data)) if h > 0 else []
    X, y, feats = build_features(p.data, p.target, p.specs, h, step, target_lags=lags)
    keep = y.notna().to_numpy()
    X, y = X[keep], y[keep]
    n = len(y)
    times = X.index
    lookback = max([f.shift for f in feats] + [h])
    buffer = (lookback + h + 1) * step
    out: Dict[str, Any] = {"rows": n, "features": X.shape[1]}
    k_sel = max(3, X.shape[1] // 2)

    def fit_predict(train_idx, test_idx, cols=None):
        Xc = X if cols is None else X[cols]
        m = common._rf(seed).fit(Xc.iloc[train_idx], y.iloc[train_idx])
        return m.predict(Xc.iloc[test_idx])

    preds = {a: pd.Series(np.nan, index=y.index) for a in
             ("shuffled_cv", "selection_all_rows", "selection_in_fold", "blocked_cv", "forward_chaining")}
    shuffled = list(KFold(K, shuffle=True, random_state=seed).split(X))
    Xf = pd.DataFrame(SimpleImputer(strategy="median").fit_transform(X), index=X.index, columns=X.columns)
    sel_all = X.columns[SelectKBest(f_regression, k=k_sel).fit(Xf, y).get_support()]
    for tr, te in shuffled:
        preds["shuffled_cv"].iloc[te] = fit_predict(tr, te)
        preds["selection_all_rows"].iloc[te] = fit_predict(tr, te, sel_all)
        imp = SimpleImputer(strategy="median").fit(X.iloc[tr])
        s = SelectKBest(f_regression, k=k_sel).fit(imp.transform(X.iloc[tr]), y.iloc[tr])
        preds["selection_in_fold"].iloc[te] = fit_predict(tr, te, X.columns[s.get_support()])
    blocks = np.array_split(np.arange(n), K)
    fold_rmse = {"blocked_cv": [], "forward_chaining": []}
    for i, te in enumerate(blocks):
        t0, t1 = times[te[0]], times[te[-1]]
        tr = np.flatnonzero((times < t0 - buffer) | (times > t1 + buffer))
        preds["blocked_cv"].iloc[te] = fit_predict(tr, te)
        fold_rmse["blocked_cv"].append(_metrics(y.iloc[te], preds["blocked_cv"].iloc[te])["rmse"])
        if i >= 1:
            trf = np.flatnonzero(times < t0 - buffer)
            if len(trf) >= 100:
                preds["forward_chaining"].iloc[te] = fit_predict(trf, te)
                fold_rmse["forward_chaining"].append(_metrics(y.iloc[te], preds["forward_chaining"].iloc[te])["rmse"])
    for a, s in preds.items():
        if a != "forward_chaining":
            out[a] = _metrics(y, s)
    later = np.concatenate(blocks[1:])
    ok = later[np.isfinite(preds["forward_chaining"].iloc[later].to_numpy())]
    for a in ("shuffled_cv", "blocked_cv", "forward_chaining"):
        out[f"{a}_folds2plus"] = _metrics(y.iloc[ok], preds[a].iloc[ok])
    out["fold_rmse"] = fold_rmse
    return out


def row(dataset, name, comp) -> Dict[str, Any]:
    r = {"dataset": dataset, "task": name, "rows": comp["rows"], "features": comp["features"]}
    for a in ("shuffled_cv", "selection_all_rows", "selection_in_fold", "blocked_cv"):
        for m, v in comp[a].items():
            r[f"{m}_{a}"] = v
    for a in ("shuffled_cv", "blocked_cv", "forward_chaining"):
        for m, v in comp[f"{a}_folds2plus"].items():
            r[f"{m}_{a}_f2"] = v
    r["blocked_fold_rmse"] = ";".join(f"{v:.4g}" for v in comp["fold_rmse"]["blocked_cv"])
    r["forward_fold_rmse"] = ";".join(f"{v:.4g}" for v in comp["fold_rmse"]["forward_chaining"])
    r["ratio_blocked_shuffled"] = r["rmse_blocked_cv"] / r["rmse_shuffled_cv"]
    r["ratio_forward_shuffled_f2"] = r["rmse_forward_chaining_f2"] / r["rmse_shuffled_cv_f2"]
    r["ratio_blocked_shuffled_f2"] = r["rmse_blocked_cv_f2"] / r["rmse_shuffled_cv_f2"]
    return r


def tasks():
    """(dataset, name, loader) for every task, in a fixed order."""
    sys.path.insert(0, str(HERE / "robod"))
    out = []
    import importlib.util

    def load_module(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    robod = load_module(HERE / "robod" / "run.py", "robod_run")
    for room in (4, 5):
        for target, horizon, drop, use in robod.TASKS:
            if target == "occupant_presence":
                continue
            mode = "now" if horizon == 0 else horizon
            name = f"robod-room{room}-{target.replace('.', '')}-{mode}"
            out.append(("ROBOD", name, lambda room=room, target=target, horizon=horizon, drop=drop, name=name:
                        prepared(robod.load(room), target, robod.COLUMNS, horizon, name, robod.NOTES, drop)))
    aal = load_module(HERE / "aalborg" / "run.py", "aalborg_run")
    for room, target, horizon, use in aal.TASKS:
        if room not in ("RoomA", None) or "Room__active" in target:
            continue
        cols = dict(aal.SYSTEM)
        if room:
            cols.update(aal.room_columns(room))
        short = target.replace(":", "-").replace("__", "-").replace("_", "").lower()
        name = f"aalborg-{short}-{horizon}"
        accept = {f"missing:{target}": aal.PEOPLE_REASON} if "People" in target else {}
        out.append(("Aalborg", name, lambda target=target, cols=cols, horizon=horizon, name=name, accept=accept:
                    prepared(aal.load(), target, cols, horizon, name, aal.NOTES, accept=accept)))
    bdg = load_module(HERE / "bdg2" / "run.py", "bdg2_run")
    picks, elec, weather, _ = bdg.sample(200, 0)
    for _, b in picks.head(40).iterrows():
        name = f"bdg2-{b['building_id']}"
        out.append(("BDG2", name, lambda b=b, name=name:
                    prepared(bdg.building_frame(b["building_id"], b["site_id"], elec, weather), "electricity",
                             bdg.COLUMNS, "24h", name, bdg.NOTES, freq="1h")))
    return out


def main(part: int, parts: int) -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    for i, (ds, name, make) in enumerate(tasks()):
        if i % parts != part:
            continue
        p = make()
        if p is None:
            print(f"{name}: blocked", flush=True)
            continue
        r = row(ds, name, compare(p))
        r["order"] = i
        rows.append(r)
        print(f"{name}: blocked/shuffled {r['ratio_blocked_shuffled']:.2f}, forward/shuffled (folds 2+) "
              f"{r['ratio_forward_shuffled_f2']:.2f}", flush=True)
        pd.DataFrame(rows).to_csv(OUT / f"protocol_part{part}.csv", index=False)


def merge() -> None:
    parts = sorted(OUT.glob("protocol_part*.csv"))
    pd.concat([pd.read_csv(f) for f in parts]).sort_values("order").to_csv(OUT / "protocol.csv", index=False)
    for f in parts:
        f.unlink()
    print("merged", len(parts))


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge()
    else:
        i, k = map(int, sys.argv[1].split("/"))
        main(i, k)
