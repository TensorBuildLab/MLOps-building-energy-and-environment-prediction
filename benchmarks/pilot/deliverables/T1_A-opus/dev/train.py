"""Fit the final model on all of train.csv and save it next to model.py."""
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "2")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import numpy as np, pandas as pd, joblib
from sklearn.ensemble import HistGradientBoostingRegressor
import model as M

CFG = json.load(open(os.path.join(HERE, "final_cfg.json")))
t0 = time.time()
d = M.load_clean(os.path.join(ROOT, "train.csv"))
F, a = M.make_features(d)
y = a["c_mean"]
r = y - F["c0"]
ok = r.notna()
X = F.loc[ok, CFG["features"]]
models = []
for P in CFG["params"]:
    m = HistGradientBoostingRegressor(random_state=0, **P)
    m.fit(X, r[ok])
    models.append(m)
bundle = dict(models=models, features=CFG["features"], clip=float(CFG.get("clip", 600.0)),
              fallback=float(np.nanmedian(y)), trained_until=str(d.index.max()))
joblib.dump(bundle, M.MODEL_PATH, compress=3)
print("saved", M.MODEL_PATH, "n=%d, %.1fs" % (ok.sum(), time.time() - t0))
