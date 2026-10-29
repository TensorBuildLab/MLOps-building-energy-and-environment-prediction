"""Exploration: compare feature sets / target forms on the bemlops time split.

Uses bemlops' own leakage-safe feature builder and the same train/val/test
boundaries that Project.fit() chose (train <= 2023-05-03, val 05-04..05-17,
test 05-18..05-31). Only for choosing inputs; final numbers come from fit().
"""
import sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np, pandas as pd
import bemlops
from bemlops.features import build_features
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import model as m

t0 = time.time()
d = m.add_features(pd.read_pickle(HERE / "work_clean5.pkl"))
BASE = {
    "co2": {"quantity": "co2", "unit": "ppm", "flat_ok": True},
    "room_temp": "zone_air_temperature [degC]",
    "room_active": "occupancy_status",
    "damper": "position [%]",
    "light_on": "equipment_status",
    "window": "equipment_status",
    "supply_flow": "airflow [m3/h]",
    "oat": "outdoor_air_temperature [degC]",
}
EXTRA = {k: "other" for k in ["fan_on_24h", "fan_on_7d", "active_24h", "active_7d",
                              "co2_d30", "co2_d60", "active_1h"]}
cols = dict(BASE, **EXTRA)
p = bemlops.Project(d, target="co2", columns=cols, horizon="1h")
p.check_data()
prep = p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
X, y, feats = build_features(prep, "co2", p.specs, 4, pd.Timedelta("15min"))
print("built", X.shape, time.time() - t0, flush=True)
ok = y.notna() & X["co2__t-4"].notna()
X, y = X[ok], y[ok]
tr = X.index <= "2023-05-03 23:00:00+02:00"
va = (X.index >= "2023-05-04 00:15:00+02:00") & (X.index <= "2023-05-17 23:15:00+02:00")
te = X.index >= "2023-05-18 00:30:00+02:00"
last = X["co2__t-4"]
base_cols = [f.name for f in feats if f.source in list(BASE) + ["calendar"]]
all_cols = list(X.columns)
no_cal = [c for c in all_cols if c not in ("hour_sin", "hour_cos", "dow_sin", "dow_cos")]


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


rows = [("persistence", "-", rmse(y[va], last[va]), rmse(y[te], last[te]))]
for fs_name, fs in [("base", base_cols), ("all", all_cols), ("all_no_hourdow", no_cal)]:
    for tgt in ["level", "delta"]:
        yt = y if tgt == "level" else y - last
        for mname, mk in [
            ("ridge", lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))),
            ("hgb", lambda: HistGradientBoostingRegressor(learning_rate=0.05, max_leaf_nodes=15,
                                                          min_samples_leaf=50, max_iter=200, random_state=0)),
        ]:
            est = mk().fit(X.loc[tr, fs], yt[tr])
            pv = est.predict(X.loc[va, fs]); pt = est.predict(X.loc[te, fs])
            if tgt == "delta":
                pv = pv + last[va].values; pt = pt + last[te].values
            rows.append((f"{mname}-{tgt}", fs_name, rmse(y[va], pv), rmse(y[te], pt)))
            print(rows[-1], flush=True)
print(pd.DataFrame(rows, columns=["model", "features", "val_rmse", "test_rmse"]).round(2))
print("elapsed", time.time() - t0)
