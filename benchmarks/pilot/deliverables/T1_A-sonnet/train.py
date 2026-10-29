"""Fits the final forecaster on train.csv and writes model.joblib (not called by predict())."""
import os
import sys
import time
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M  # noqa: E402

# feature set used by the main models: CO2 history + same-time-of-day history + calendar.
# (outdoor weather and room status signals were tested and gave no CV gain, so they are left out
#  to keep the model robust to seasonal drift of those variables)
EXCLUDE_PREFIX = ("tout", "wind", "sol", "active", "window", "lighton", "light", "damper", "flow")
FALLBACK_FEATURES = ["B_d1", "B_d2", "B_d7", "B_dmean5", "B_dmax5", "B_d1_nb", "tod", "tod_sin",
                     "tod_cos", "dow", "hol", "hol_prev", "hol_next", "workday", "prev_workday"]


def main(csv=None):
    t0 = time.time()
    csv = csv or os.path.join(HERE, "train.csv")
    raw = M._read_raw(csv)
    clean = M._clean(raw)
    X, T, y = M.feature_table(clean, 5)           # 5-min origin spacing = 3x more training rows
    feats = [c for c in X.columns if not c.startswith(EXCLUDE_PREFIX)]
    base = M._baseline(X)
    ok = y.notna() & base.notna() & X["co2"].notna() & X["co2_m60"].notna()
    Xtr, ytr = X.loc[ok, feats], (y - base)[ok]

    models = []
    for seed in (0, 1):
        models.append(make_pipeline(
            SimpleImputer(strategy="median"),
            ExtraTreesRegressor(n_estimators=200, min_samples_leaf=20, max_features=0.5,
                                n_jobs=2, random_state=seed)))
    models.append(HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.025, max_leaf_nodes=8, min_samples_leaf=100,
        l2_regularization=1.0, random_state=0))
    for m in models:
        m.fit(Xtr, ytr)

    okf = y.notna()
    fb = HistGradientBoostingRegressor(max_iter=100, learning_rate=0.05, max_leaf_nodes=8,
                                       min_samples_leaf=80, l2_regularization=1.0, random_state=0)
    fb.fit(X.loc[okf, FALLBACK_FEATURES], y[okf])

    bundle = dict(features=feats, models=models, weights=[0.25, 0.25, 0.5], residual=True,
                  fallback_features=FALLBACK_FEATURES, fallback_model=fb, clip=(300.0, 3000.0),
                  n_train=int(ok.sum()))
    joblib.dump(bundle, os.path.join(HERE, "model.joblib"), compress=3)
    print("trained on", int(ok.sum()), "rows,", len(feats), "features in", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
