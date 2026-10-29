"""Exploration on the 0.8/0.1/0.1 bemlops split: level vs change target, and blends."""
import sys; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import numpy as np, pandas as pd, bemlops
from bemlops.features import build_features
from sklearn.ensemble import HistGradientBoostingRegressor
import model as m
d = m.add_features(pd.read_pickle(HERE / "work_clean5.pkl"))
import train as T
p = bemlops.Project(d, target="co2", columns=T.COLUMNS, horizon="1h")
p.check_data(); prep = p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
X, y, feats = build_features(prep, "co2", p.specs, 4, pd.Timedelta("15min"))
ok = y.notna(); X, y = X[ok], y[ok]
last = X["co2__t-4"]
tz = "Europe/Copenhagen"
tr = X.index <= pd.Timestamp("2023-05-13 07:00", tz=tz)
va = (X.index >= pd.Timestamp("2023-05-13 08:15", tz=tz)) & (X.index <= pd.Timestamp("2023-05-22 15:15", tz=tz))
te = X.index >= pd.Timestamp("2023-05-22 16:30", tz=tz)
print("sizes", tr.sum(), va.sum(), te.sum())
lastf = last.fillna(method=None) if False else last
def rmse(a, b): return float(np.sqrt(np.nanmean((np.asarray(a) - np.asarray(b)) ** 2)))
print("persistence val/test", rmse(y[va], last[va]), rmse(y[te], last[te]))
P = dict(learning_rate=0.1, max_leaf_nodes=7, min_samples_leaf=100, l2_regularization=0.1, max_iter=100, random_state=0)
for tgt in ["level", "delta"]:
    for params in [P, dict(P, learning_rate=0.05, max_iter=200), dict(P, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=50, max_iter=200)]:
        yt = y if tgt == "level" else y - last
        okk = yt.notna()
        h1 = HistGradientBoostingRegressor(**params).fit(X[tr & okk], yt[tr & okk])
        h2 = HistGradientBoostingRegressor(**params).fit(X[(tr | va) & okk], yt[(tr | va) & okk])
        add = 0 if tgt == "level" else last
        pv = h1.predict(X[va]) + (0 if tgt == "level" else last[va].values)
        pt = h2.predict(X[te]) + (0 if tgt == "level" else last[te].values)
        print(tgt, {k: params[k] for k in ("learning_rate", "max_leaf_nodes", "min_samples_leaf", "max_iter")}, "val", round(rmse(y[va], pv), 2), "test", round(rmse(y[te], pt), 2), flush=True)
