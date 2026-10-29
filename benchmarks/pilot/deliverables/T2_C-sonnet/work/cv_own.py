import sys, warnings, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from feat import *
warnings.filterwarnings("ignore")

df5 = clean5(load_raw("../train.csv"))
g = grid15(df5)
y = g["y"]

folds = [("2021-10-26", "2021-11-01"), ("2021-11-02", "2021-11-08"), ("2021-11-09", "2021-11-14"),
         ("2021-11-15", "2021-11-17"), ("2021-12-09", "2021-12-09")]


def rmse(a, b):
    m = a.notna() & b.notna()
    return float(np.sqrt(((a[m] - b[m]) ** 2).mean())), int(m.sum())


def run(name, make, X, folds=folds, verbose=True):
    out = []
    allp = pd.Series(np.nan, index=y.index)
    for (a, b) in folds:
        te = (y.index >= a) & (y.index < pd.Timestamp(b) + pd.Timedelta("1D"))
        tr = (y.index < pd.Timestamp(a) - pd.Timedelta("1h")) & y.notna().values
        # exclude test rows whose target is missing
        Xtr, ytr = X[tr], y[tr]
        m = make()
        m.fit(Xtr, ytr)
        p = pd.Series(m.predict(X[te]), index=y.index[te])
        allp[te] = p
        r, n = rmse(y[te], p)
        out.append(r)
    pooled = rmse(y[allp.notna()], allp[allp.notna()])
    if verbose:
        print(f"{name:35s} folds={np.round(out,3)} pooled={pooled[0]:.3f} n={pooled[1]}")
    return allp, pooled[0]


class Persist:
    def fit(self, X, y): return self
    def predict(self, X): return X["y_l4"].fillna(0).values


class Prof:
    """clock profile: mean y by minute of day on weekdays"""
    def fit(self, X, y):
        self.p = y.groupby(X["mod"]).mean(); return self
    def predict(self, X): return X["mod"].map(self.p).fillna(0).values


if __name__ == "__main__":
    X = build(g)
    run("persistence", Persist, X)
    run("clock profile", Prof, X)
    mk = lambda: HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_depth=4, min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    run("hgb all", mk, X)
    run("hgb no day lag", mk, build(g, day_lag=False))
    cols_small = ["mod", "wkday", "y_l4", "y_l5", "y_l6", "y_l8", "y_on_mean", "n_on"]
    run("hgb small", mk, X[cols_small])
    mk2 = lambda: RandomForestRegressor(n_estimators=200, min_samples_leaf=5, max_features=0.5, n_jobs=2, random_state=0)
    Xf = build(g, day_lag=False).fillna(-1)
    run("rf no day lag", mk2, Xf)
