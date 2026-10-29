import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
import model as M

pd.set_option("display.width", 200)
CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "train.csv")

t0 = time.time()
d = M.load_clean(CSV)
F, a = M.make_features(d)
y = a["c_mean"]                       # cleaned 15-min mean (target)
# raw target as an evaluator might compute it (sentinels included)
raw = pd.read_csv(CSV, sep=";", encoding="utf-8-sig", na_values=["#N/A", "OFFLINE"])
rt = pd.to_datetime(raw["timestamp"], utc=True)
rc = pd.Series(raw["RoomB:Sensor__CO2"].values, index=rt)
rc = rc[~rc.index.duplicated()].sort_index()
y_raw = rc.resample("15min").mean().reindex(F.index)
print("features built in %.1fs, shape %s" % (time.time() - t0, F.shape))

df = F.copy()
df["y"] = y
df["y_raw"] = y_raw
df["r"] = df["y"] - df["c0"]
ok = df["y"].notna() & df["c0"].notna()
df = df[ok]
loc = df.index.tz_convert(M.LOCAL_TZ)

ALL = [c for c in F.columns]
def rmse(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2)))

# weekly expanding-window folds (Mon 00:00 local)
week_starts = pd.date_range("2023-04-03", "2023-05-29", freq="7D", tz=M.LOCAL_TZ)

def run(feats, params, label, target="r", n_seeds=1, verbose=False, weeks=None, tau=None):
    res = []
    allp = []
    for ws in (week_starts if weeks is None else weeks):
        we = ws + pd.Timedelta(days=7)
        tr = df[df.index < ws.tz_convert("UTC")]
        te = df[(df.index >= ws.tz_convert("UTC")) & (df.index < we.tz_convert("UTC"))]
        if len(te) == 0:
            continue
        p = np.zeros(len(te))
        for sd in range(n_seeds):
            m = HistGradientBoostingRegressor(random_state=sd, **params)
            sw = None
            if tau is not None:
                age_d = (ws.tz_convert("UTC") - tr.index).total_seconds().values / 86400.0
                sw = np.exp(-age_d / tau)
            m.fit(tr[feats], tr[target], sample_weight=sw)
            p += m.predict(te[feats]) / n_seeds
        pred = te["c0"].values + p if target == "r" else p
        res.append((ws.date(), rmse(te["y"].values, te["c0"].values), rmse(te["y"].values, pred),
                    rmse(te["y_raw"].values, pred)))
        allp.append(pd.Series(pred, index=te.index))
    r = pd.DataFrame(res, columns=["week", "persist", "model", "model_rawtarget"])
    if verbose:
        print(r.round(2).to_string())
    allp = pd.concat(allp)
    yy = df.loc[allp.index, "y"].values
    tot = rmse(yy, allp.values)
    totp = rmse(yy, df.loc[allp.index, "c0"].values)
    last4 = allp.index >= week_starts[-4].tz_convert("UTC")
    if last4.sum() == 0: last4[:] = True
    print(f"{label:40s} pooled RMSE model {tot:6.2f} persist {totp:6.2f} | last4w model "
          f"{rmse(yy[last4], allp.values[last4]):6.2f} persist {rmse(yy[last4], df.loc[allp.index, 'c0'].values[last4]):6.2f}")
    return r, allp

if __name__ == "__main__":
    base_params = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40,
                       l2_regularization=1.0)
    r, _ = run(ALL, base_params, "all feats", verbose=True)
