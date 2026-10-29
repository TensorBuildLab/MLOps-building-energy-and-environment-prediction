"""Exploration: where do errors come from; blends; training window."""
import sys; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
exec(open(HERE / "exp2.py").read().split("def rmse")[0])
def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
ev = va | te
yd = y - last
ridge = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)).fit(X.loc[tr, all_cols], yd[tr])
hgb = HistGradientBoostingRegressor(learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=100, max_iter=150, random_state=0).fit(X.loc[tr, all_cols], yd[tr])
pr = pd.Series(ridge.predict(X.loc[ev, all_cols]), X.index[ev]); ph = pd.Series(hgb.predict(X.loc[ev, all_cols]), X.index[ev])
print("hgb small val/test", rmse(yd[va], ph[va[ev]]), rmse(yd[te], ph[te[ev]]))
for a in [0.25, 0.5, 0.75, 1.0]:
    print("alpha", a, "ridge", rmse(yd[va], a*pr[va[ev]]), rmse(yd[te], a*pr[te[ev]]), "hgb", rmse(yd[va], a*ph[va[ev]]), rmse(yd[te], a*ph[te[ev]]), "avg", rmse(yd[va], a*(pr+ph)[va[ev]]/2), rmse(yd[te], a*(pr+ph)[te[ev]]/2))
coef = pd.Series(ridge[-1].coef_, all_cols).sort_values(); print(coef.round(2))
t = pd.DataFrame({"h": X.index[ev].hour, "wd": X.index[ev].day_of_week < 5, "p": yd[ev]**2, "r": (yd[ev]-pr)**2, "g": (yd[ev]-ph)**2})
print(t.groupby(["wd", "h"]).sum().round(0).query("p > 20000"))
# recent-only training
for start in ["2023-03-15", "2023-04-01", "2023-04-15"]:
    trr = tr & (X.index >= pd.Timestamp(start, tz="Europe/Copenhagen"))
    r2 = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)).fit(X.loc[trr, all_cols], yd[trr])
    h2 = HistGradientBoostingRegressor(learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=100, max_iter=150, random_state=0).fit(X.loc[trr, all_cols], yd[trr])
    print(start, "ridge", rmse(yd[va], r2.predict(X.loc[va, all_cols])), rmse(yd[te], r2.predict(X.loc[te, all_cols])), "hgb", rmse(yd[va], h2.predict(X.loc[va, all_cols])), rmse(yd[te], h2.predict(X.loc[te, all_cols])))
