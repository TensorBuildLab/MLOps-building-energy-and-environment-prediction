"""Exploration: level vs delta target when the summer weeks are in training."""
import sys; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
_s = open(HERE / "exp4.py").read(); exec(_s[:_s.index("exec(src)") + len("exec(src)")])
def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
trv = tr | va
fs = all_cols
for tgt in ["level", "delta"]:
    yt = y if tgt == "level" else y - last
    for params in [(0.05, 7, 100, 1.0, 100), (0.05, 15, 50, 0.1, 200), (0.1, 15, 20, 0.0, 200), (0.05, 31, 20, 0.1, 200)]:
        lr, leaf, msl, l2, it = params
        h = HistGradientBoostingRegressor(learning_rate=lr, max_leaf_nodes=leaf, min_samples_leaf=msl, l2_regularization=l2, max_iter=it, random_state=0).fit(X.loc[trv, fs], yt[trv])
        p = h.predict(X.loc[te, fs]) + (0 if tgt == "level" else last[te].values)
        print(tgt, params, round(rmse(y[te], p), 2), flush=True)
    r = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10)).fit(X.loc[trv, fs], yt[trv])
    print(tgt, "ridge10", round(rmse(y[te], r.predict(X.loc[te, fs]) + (0 if tgt == "level" else last[te].values)), 2))
