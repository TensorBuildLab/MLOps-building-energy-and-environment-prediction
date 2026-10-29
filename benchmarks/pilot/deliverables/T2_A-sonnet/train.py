"""Offline training for model.py (run once; predict() only loads the saved bundle).

    python train.py                       -> fits on all valid history of train.csv, writes model_bundle.joblib
    python train.py --until 2021-11-15    -> fits on days before the date (used for honest hold-out tests)

Steps
  1. read + clean the raw export with model.read_clean / model.add_fault_flags (same code as predict()).
  2. drop stretches where the chilled-water meter is known to be unusable (found in the EDA):
       2021-09-20 18:40 .. 2021-10-26 10:30   meter reads 0 while the AHU runs (flow sensor stuck too)
       2021-11-03 18:30 .. 2021-11-04 10:30   meter frozen at 0.48 kWh
       2021-11-17 14:00 .. end of day         meter dropping out (spikes / zeros)
  3. typical 5-min chilled-water profile by time of day (p5) from the remaining healthy rows.
  4. per segment (start-up 08:00-08:45, steady 09:00-18:00, shut-down 18:15-18:30) a ridge regression
     predicts the anomaly of the 15-min energy vs. the typical profile from anomaly/weather/AHU features
     observed up to T - 50 min.
"""
import argparse
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M  # noqa: E402

EXCL = [("2021-09-20 18:40", "2021-10-26 10:30"),
        ("2021-11-03 18:30", "2021-11-04 10:30"),
        ("2021-11-17 14:00", "2021-11-18 00:00")]

B_F = ["a_b0", "a_b1", "a_b2", "a_b3", "a_12", "a_36", "a_today", "a_prev1", "a_prev3",
       "dbt_12", "ghi_12", "orh_6"]
CFG = {"A": (["a_prev1", "a_prev3", "dbt_36", "ghi_36"], 30.0),
       "B": (B_F, 30.0),
       "C": (["a_12", "vc_12", "a_b0"], 10.0)}


def excluded_rows(index):
    ex = pd.Series(False, index=index)
    for a, b in EXCL:
        ex |= (index >= pd.Timestamp(a)) & (index < pd.Timestamp(b) + pd.Timedelta(hours=1))
    return ex


def fit_bundle(csv_path, until=None, out=None, verbose=True):
    G = M.add_fault_flags(M.read_clean(csv_path))
    ex = excluded_rows(G.index)
    keep = ~ex
    if until is not None:
        keep &= G.index < pd.Timestamp(until)
    p5 = M.make_p5(G, keep)
    X = M.interval_frame(G, p5)
    y = M.target_series(G).reindex(X.index)
    ok = y.notna() & ~ex.reindex(X.index)
    if until is not None:
        ok &= X.index < pd.Timestamp(until)
    Xs = M.scaled_features(X)
    resid = y - X["p15"]
    bundle = {"p5": p5, "ridge": {}, "features": {}, "clip": {}, "cap": 15.0}
    for seg, (lo, hi) in M.SEGMENTS.items():
        feats, alpha = CFG[seg]
        m = ok & (X["tod"] >= lo) & (X["tod"] < hi) & (X["p15"] > 0.5)
        pipe = make_pipeline(SimpleImputer(strategy="mean"), StandardScaler(), Ridge(alpha=alpha))
        pipe.fit(Xs.loc[m, feats], resid[m])
        bundle["ridge"][seg] = pipe
        bundle["features"][seg] = feats
        lo, hi = Xs.loc[m, feats].min(), Xs.loc[m, feats].max()          # guard band = 50 % of the training range
        bundle["clip"][seg] = {f: (float(lo[f] - 0.5 * (hi[f] - lo[f])), float(hi[f] + 0.5 * (hi[f] - lo[f]))) for f in feats}
        if verbose:
            print(f"segment {seg}: {int(m.sum())} training intervals, features={feats}")
    if verbose:
        print("training days:", len(set(X.index[ok].date)), "intervals:", int(ok.sum()))
    if out:
        joblib.dump(bundle, out)
    return bundle


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(HERE, "train.csv"))
    ap.add_argument("--until", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "model_bundle.joblib"))
    a = ap.parse_args()
    fit_bundle(a.csv, a.until, a.out)
    print("saved", a.out)
