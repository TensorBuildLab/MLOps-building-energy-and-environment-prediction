import os, sys, glob, warnings
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, pandas as pd
sys.path.insert(0, ".."); import model as m
warnings.filterwarnings("ignore")
bp = pd.read_csv(glob.glob("bem_runs/*/test_predictions.csv")[0], index_col=0, parse_dates=True)
df5 = m.clean5(m.load_raw("../train.csv")); g0 = m.grid15(df5)
full = pd.date_range(g0.index.min().floor("D"), g0.index.max().floor("D") + pd.Timedelta("23h45min"), freq="15min")
g = g0.reindex(full)
te0 = bp.index.min()
trm = pd.Series(g.index < te0 - pd.Timedelta("1h"), index=g.index)
art = m.fit_artifacts(g, trm); p = m.predict_grid(g, art)
d = bp.copy(); d["profres"] = p.reindex(d.index)
r = lambda a, b: float(np.sqrt(((a - b) ** 2).mean()))
print("n", len(d), "actual NaN", int(d.actual.isna().sum()), "profres NaN", int(d.profres.isna().sum()))
print("bemlops gbm", round(r(d.actual, d.predicted), 3), " profres", round(r(d.actual, d.profres), 3), " persistence", round(r(d.actual, d.persistence), 3))
for w in [0.25, 0.5, 0.75]:
    print("blend w_profres=%.2f" % w, round(r(d.actual, w * d.profres + (1 - w) * d.predicted), 3))
# by day
e = d.assign(eb=(d.actual - d.predicted) ** 2, ep=(d.actual - d.profres) ** 2, ee=(d.actual - (d.profres + d.predicted) / 2) ** 2)
print(e.groupby(e.index.date)[["eb", "ep", "ee"]].mean().pow(0.5).round(2).to_string())
