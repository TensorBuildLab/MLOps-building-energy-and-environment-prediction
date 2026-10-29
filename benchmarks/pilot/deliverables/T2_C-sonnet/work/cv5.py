import os
os.environ["OMP_NUM_THREADS"] = "1"
import sys, warnings, json
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
mod_path = sys.argv[1] if len(sys.argv) > 1 else "model_draft"
m = __import__(mod_path)

df5 = m.clean5(m.load_raw("../train.csv"))
g0 = m.grid15(df5)
full = pd.date_range(g0.index.min().floor("D"), g0.index.max().floor("D") + pd.Timedelta("23h45min"), freq="15min")
g = g0.reindex(full)
y = g["y"]
folds = [("2021-10-26", "2021-11-01"), ("2021-11-02", "2021-11-08"), ("2021-11-09", "2021-11-14"),
         ("2021-11-15", "2021-11-17"), ("2021-12-09", "2021-12-09")]


def rmse(a, b):
    k = a.notna() & b.notna()
    return float(np.sqrt(((a[k] - b[k]) ** 2).mean())), int(k.sum())


def cv(name, cfg=None, trim=0.0, post=None):
    allp = pd.Series(np.nan, index=y.index); fr = []
    for a, b in folds:
        te = (y.index >= a) & (y.index < pd.Timestamp(b) + pd.Timedelta("1D"))
        trm = pd.Series(y.index < pd.Timestamp(a) - pd.Timedelta("1h"), index=y.index)
        art = m.fit_artifacts(g, trm, cfg, trim=trim)
        p = m.predict_grid(g, art)
        allp[te] = p[te]
        fr.append(rmse(y[te], p[te])[0])
    k = allp.notna() & y.notna()
    pooled = rmse(y[k], allp[k])
    print(f"{name:42s} folds={np.round(fr,3)} pooled={pooled[0]:.3f} n={pooled[1]}", flush=True)
    return allp


if __name__ == "__main__":
    pers = g["y"].shift(4).fillna(0)
    te = pd.Series(False, index=y.index)
    for a, b in folds: te |= (y.index >= a) & (y.index < pd.Timestamp(b) + pd.Timedelta("1D"))
    k = te & y.notna()
    print("persistence pooled", rmse(y[k], pers[k]), flush=True)
    base = cv("final cfg (rd3, clip3, a=30)")
    cv("trim 0.2 profile", trim=0.2)
    cv("no rd3", cfg=dict(rd3=False))
    cv("no clip", cfg=dict(clip=None))
    cv("alpha 100", cfg=dict(alpha=100.0))
    cv("alpha 10", cfg=dict(alpha=10.0))
    cv("win 12", cfg=dict(win=12))
    base.to_csv("cv5_preds.csv")
