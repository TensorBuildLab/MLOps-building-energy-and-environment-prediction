"""Fit the final model on ALL of train.csv and save model_artifact.joblib (run once; predict() never retrains)."""
import sys, os, json, warnings, time
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, joblib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import feats
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer

t0 = time.time()
d = feats.read_raw(os.path.join(HERE, 'train.csv'))
d5 = feats.clean5(d)
bins, lc = feats.to_bins(d5)
X, F, b = feats.build_frame(bins, lc)
y = feats.target_series(d5).reindex(X.index)
base = X['f_co2']
ok = y.notna() & base.notna()

DROP = ['f_oat', 'f_sol', 'f_wind', 'f_vent_el', 'f_dh', 'f_hc', 'f_sat', 'f_rt', 'f_lux', 'f_lux_m4', 'f_oat_d8', 'f_window']
cols = [c for c in X.columns if c not in DROP]
print(len(cols), 'features; training rows', int(ok.sum()))
est = make_pipeline(SimpleImputer(strategy='median'),
                    ExtraTreesRegressor(n_estimators=300, min_samples_leaf=15, max_features=0.5, n_jobs=1, random_state=0))
est.fit(X.loc[ok, cols], (y - base)[ok])

loc = y.index.tz_convert(feats.LOCAL_TZ)
yy = y.dropna()
li = yy.index.tz_convert(feats.LOCAL_TZ)
prof = yy.groupby([(li.dayofweek >= 5).astype(int), li.hour]).median()
profile = {(int(k[0]), int(k[1])): float(v) for k, v in prof.items()}
art = {'models': [(1.0, est)], 'cols': cols, 'profile': profile, 'global_median': float(yy.median()),
       'clip': (300.0, 2500.0),
       'meta': {'trained_rows': int(ok.sum()), 'train_start': str(y.index.min()), 'train_end': str(y.index.max())}}
joblib.dump(art, os.path.join(HERE, 'model_artifact.joblib'), compress=3)
print('saved', time.time() - t0)
