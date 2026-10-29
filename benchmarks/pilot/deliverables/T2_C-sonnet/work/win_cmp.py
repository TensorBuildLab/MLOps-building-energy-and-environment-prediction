import os, sys, warnings
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, pandas as pd
sys.path.insert(0, ".."); import model as m
warnings.filterwarnings("ignore")
df5 = m.clean5(m.load_raw("../train.csv")); g0 = m.grid15(df5)
full = pd.date_range(g0.index.min().floor("D"), g0.index.max().floor("D") + pd.Timedelta("23h45min"), freq="15min")
g = g0.reindex(full); y = g["y"]
valid = y.dropna().index
print("valid rows", len(valid))
# bemlops split in run2: train 2086, val 443, test 444 (time ordered, gap 1h) of the valid-target rows
n_tr, n_val, n_te = 2086, 443, 444
# approximate with the same fractions on the current valid rows (different cleaning -> slightly different count)
N = len(valid); te0 = valid[N - n_te]; va0 = valid[N - n_te - n_val]
print("test window starts", te0, "val starts", va0)
trm = pd.Series(y.index < te0 - pd.Timedelta("1h"), index=y.index)
art = m.fit_artifacts(g, trm)
p = m.predict_grid(g, art)
te = (y.index >= te0) & y.notna().values
e = (y[te] - p[te])
print("ProfRes on bemlops-like test window: n", int(te.sum()), "RMSE", round(float(np.sqrt((e**2).mean())), 3),
      "MAE", round(float(e.abs().mean()), 3), "persistence RMSE", round(float(np.sqrt(((y[te]-y.shift(4)[te].fillna(0))**2).mean())), 3))
trm2 = pd.Series(y.index < va0 - pd.Timedelta("1h"), index=y.index)
art2 = m.fit_artifacts(g, trm2); p2 = m.predict_grid(g, art2)
va = (y.index >= va0) & (y.index < te0) & y.notna().values
e2 = y[va] - p2[va]
print("ProfRes on validation-like window: n", int(va.sum()), "RMSE", round(float(np.sqrt((e2**2).mean())), 3))
