"""Training / evaluation script (not used by predict). Run from this folder."""
import json
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

import model as M

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 50)


def targets(g):
    """15-min targets from the 5-minute grid g (cleaned rows, not yet target-cleaned).

    raw    : sum of the 3 raw readings (-999 removed, must have 3 readings)
    clean  : physically cleaned target for the 'healthy meter' model (NaN where unusable)
    dead   : interval affected by a dead meter / comm-loss (AHU on, meter reads 0)
    """
    y = g[M.TARGET]
    fan = g["ahu_fan_speed"]
    valve = g["cooling_coil_valve_command"]
    on_row = (fan > 5) & (valve > 10)
    yc = M.clean_chw_causal(g)            # pulses / frozen -> NaN, shut valve -> 0
    # catch-up pulses: invalidate the pulse and the zero run before it
    pulse = y > 7.0
    zero_on = on_row & (y.fillna(-1) == 0)
    run_id = (~zero_on).cumsum()
    run_len = zero_on.groupby(run_id).transform("sum")
    dead_row = zero_on & (run_len >= 3)
    bad = pulse.copy()
    for t in np.where(pulse.values)[0]:
        k = t - 1
        while k >= 0 and zero_on.iloc[k]:
            bad.iloc[k] = True
            k -= 1
    yc = yc.mask(bad | dead_row)
    origin = g.index[0]
    rs = lambda s, f: getattr(s.resample("15min", origin=origin), f)()
    raw = rs(y, "sum").where(rs(y, "count") == 3)
    n_c = rs(yc, "count")
    clean = (rs(yc, "mean") * 3).where(n_c >= 2)
    dead = rs(dead_row.astype(float), "max") > 0
    pulse_b = rs(pulse.astype(float), "max") > 0
    return pd.DataFrame({"raw": raw, "clean": clean, "dead": dead, "pulse": pulse_b})


def rmse(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2))), int(m.sum())


def make_gbm(**kw):
    p = dict(loss="squared_error", learning_rate=0.05, max_iter=400, max_leaf_nodes=15,
             min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    p.update(kw)
    return HistGradientBoostingRegressor(**p)


def export_hgb(m):
    """Convert a fitted HistGradientBoostingRegressor into plain numpy arrays."""
    trees = []
    for it in m._predictors:
        for pr in it:
            nd = pr.nodes
            if np.any(nd["is_categorical"]):
                raise ValueError("categorical splits not supported")
            trees.append(dict(feature=nd["feature_idx"].astype(np.int64),
                              threshold=nd["num_threshold"].astype(float),
                              missing_left=nd["missing_go_to_left"].astype(bool),
                              left=nd["left"].astype(np.int64), right=nd["right"].astype(np.int64),
                              is_leaf=nd["is_leaf"].astype(bool), value=nd["value"].astype(float)))
    base = float(np.ravel(m._baseline_prediction)[0])
    return dict(kind="trees", baseline=base, trees=trees)


SMALL = ["chw_l1", "chw_l2", "chw_h_mean4", "chw_last", "valve_l1", "valve_last", "on_last",
         "started_today", "mins_since_start", "prev_day_level", "prev_day_same",
         "rel_start", "rel_end", "sched_frac", "zero_streak"]
WEATHER = ["air_temperature", "dry_bulb_temp", "global_horizontal_solar_radiation",
           "occupant_count", "indoor_co2", "outdoor_relative_humidity"]
FINAL_FEATURES = SMALL + WEATHER
FINAL_MEMBERS = [dict(learning_rate=0.1, max_iter=150),
                 dict(learning_rate=0.05, max_iter=300, max_leaf_nodes=7)]


def build_dataset(csv="train.csv"):
    g, F = M.prepare(csv)
    Y = targets(g).reindex(F.index)
    D = F.join(Y)
    D["date"] = D.index.normalize()
    return D[D["raw"].notna() | D["clean"].notna()]


if __name__ == "__main__":
    D = build_dataset()
    print(D.shape, D["clean"].notna().sum(), D["dead"].sum(), D["pulse"].sum(), flush=True)
    D.to_pickle("dev_dataset.pkl")
    if "--final" in sys.argv:
        tr = D[D["clean"].notna() & ~D["dead"]]
        X = tr[FINAL_FEATURES].astype(float)
        members = []
        for kw in FINAL_MEMBERS:
            m = make_gbm(**kw).fit(X, tr["clean"].values)
            ens = export_hgb(m)
            diff = np.abs(M.trees_predict(ens, X.to_numpy()) - m.predict(X)).max()
            print("member", kw, "trees", len(ens["trees"]), "numpy/sklearn max diff", diff, flush=True)
            members.append(ens)
        art = dict(model=dict(kind="ensemble", members=members), features=FINAL_FEATURES,
                   off_cap=0.3, dead_meter_streak=3, dead_meter_max_age_h=72.0, clip_max=20.0,
                   trained_on=f"{tr.index.min()} .. {tr.index.max()} ({len(tr)} intervals)")
        joblib.dump(art, M.MODEL_FILE, compress=3)
        print("saved", M.MODEL_FILE, flush=True)
