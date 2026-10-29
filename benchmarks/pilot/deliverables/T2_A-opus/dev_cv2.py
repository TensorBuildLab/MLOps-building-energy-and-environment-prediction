"""CV round 2: ungated model predictions per config, then gate variants (dev only)."""
import sys
import numpy as np
import pandas as pd
import model as M
from train import make_gbm, rmse

pd.set_option("display.width", 250)
D = pd.read_pickle("dev_dataset.pkl")
D["week"] = D.index.to_period("W").start_time
weeks = sorted(D["week"].unique())
fwd_weeks = [w for w in weeks if w >= pd.Timestamp("2021-10-25")]


class Fixed:
    def __init__(self, p):
        self.p = p

    def predict(self, X):
        return self.p


def gate(p, te, Z=6, off_cap=0.3, age=72.0):
    art = dict(model=Fixed(p), features=[], off_cap=off_cap, dead_meter_streak=Z, dead_meter_max_age_h=age)
    return M.apply_model(art, te).values


def cv_preds(feats, folds="FWD", **kw):
    out = []
    if folds == "FWD":
        splits = [(D["week"] == w, D.index < D.index[D["week"] == w].min()) for w in fwd_weeks]
    else:
        splits = []
        for w in weeks:
            te = D["week"] == w
            lo = D.index[te].min() - pd.Timedelta("1D")
            hi = D.index[te].max() + pd.Timedelta("1D")
            splits.append((te, (D.index < lo) | (D.index > hi)))
    for te_m, tr_m in splits:
        tr = D[tr_m & D["clean"].notna() & ~D["dead"]]
        te = D[te_m]
        m = make_gbm(**kw).fit(tr[feats].astype(float), tr["clean"].values)
        out.append(pd.Series(m.predict(te[feats].astype(float)), index=te.index))
    return pd.concat(out)


def score(p, label):
    te = D.loc[p.index]
    ok = ~te["dead"] & te["clean"].notna()
    okr = te["raw"].notna() & ~te["pulse"]
    on = ok & (te["sched_frac"] > 0)
    rc = rmse(p[ok].values, te.loc[ok, "clean"].values)[0]
    rr = rmse(p[okr].values, te.loc[okr, "raw"].values)[0]
    ro = rmse(p[on].values, te.loc[on, "clean"].values)[0]
    print(f"{label:55s} clean {rc:.3f}  raw {rr:.3f}  on-hours {ro:.3f}", flush=True)
    return rc, rr


SMALL = ["chw_l1", "chw_l2", "chw_h_mean4", "chw_last", "valve_l1", "valve_last", "on_last",
         "started_today", "mins_since_start", "prev_day_level", "prev_day_same",
         "rel_start", "rel_end", "sched_frac", "zero_streak"]
WEATHER = ["air_temperature", "dry_bulb_temp", "global_horizontal_solar_radiation",
           "occupant_count", "indoor_co2", "outdoor_relative_humidity"]
AHU = ["valve_pos_l1", "sat_l1", "filter_dp_l1", "sa_press_l1", "offcoil_air_temp"]

CONFIGS = {
    "sw": (SMALL + WEATHER, dict(learning_rate=0.1, max_iter=150)),
    "sw_ahu": (SMALL + WEATHER + AHU, dict(learning_rate=0.1, max_iter=150)),
    "all": (M.FEATURES, dict(learning_rate=0.1, max_iter=150)),
    "sw_slow": (SMALL + WEATHER, dict(learning_rate=0.05, max_iter=300, min_samples_leaf=40)),
    "sw_shallow": (SMALL + WEATHER, dict(learning_rate=0.05, max_iter=300, max_leaf_nodes=7)),
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(CONFIGS)
    folds = "FWD"
    if names and names[0] in ("FWD", "LOWO"):
        folds, names = names[0], names[1:]
    for nm in names:
        feats, kw = CONFIGS[nm]
        p0 = cv_preds(feats, folds, **kw)
        p0.to_pickle(f"dev_p0_{folds}_{nm}.pkl")
        te = D.loc[p0.index]
        for Z in (3, 6, 12, 10**9):
            score(pd.Series(gate(p0.values, te, Z=Z), index=p0.index), f"{folds} {nm} Z={Z}")
