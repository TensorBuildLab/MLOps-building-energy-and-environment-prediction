"""Refit the model chosen by bemlops (same estimator, same hyper-parameters, same features) on all
valid rows of train.csv, including the validation and test periods, for deployment.

bemlops' fit() keeps the estimator trained on train+validation only (data up to 2021-11-12), so the
last ~6 operating days, the most recent ones, would otherwise never be used. The honest accuracy
estimate stays the one from fit() (test period 2021-11-12 .. 2021-12-09, not seen in training).
"""
import shutil
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

import bemlops
from bemlops import features
from model import HERE, TARGET, COLUMNS, PREPARE_OPTIONS, load

warnings.filterwarnings("ignore")

src = HERE / "model_holdout.joblib"
if not src.exists():
    shutil.copy(HERE / "model.joblib", src)
m = bemlops.load_model(src)
print("chosen:", m.model_name, "trained", m.train_start, "to", m.train_end)

df = load(str(HERE / "train.csv"))
p = bemlops.Project(df[list(COLUMNS)], target=TARGET, columns=COLUMNS, horizon="1h")
p.check_data()
prep = p.prepare(freq="15min", **PREPARE_OPTIONS)
X, y, feats = features.build_features(prep, TARGET, p.specs, horizon=m.horizon, step=m.step,
                                      target_lags=m.target_lags, include_doy=m.include_doy)
features.audit(feats, TARGET, m.horizon)  # refuses any feature that reaches into the future
X = X[m.feature_names]
rows = y.notna()
print("rows with a valid target:", int(rows.sum()), "of", len(y))

# sanity check: same features + same estimator reproduce the saved model's predictions
fc = m.predict(df[list(COLUMNS)], future=False, validate=False)
same = np.allclose(fc["predicted"].reindex(X.index).values, m.estimator.predict(X), equal_nan=True)
print("feature rebuild matches the saved model:", same)
assert same

est = clone(m.estimator)
est.fit(X[rows], y[rows])
m.estimator = est
m.train_end = y[rows].index.max()
m.save(HERE / "model.joblib")
print("refit on all rows; saved model.joblib (train_end", m.train_end, ")")
