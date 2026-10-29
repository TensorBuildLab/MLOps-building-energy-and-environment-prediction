"""Exploration: interaction features and regularisation strength (delta target)."""
import sys; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
src = open(HERE / "exp2.py").read().split("def rmse")[0]
src = src.replace('d = m.add_features(pd.read_pickle(HERE / "work_clean5.pkl"))', '''d = m.add_features(pd.read_pickle(HERE / "work_clean5.pkl"))
d["fan_change_exp"] = d["fan_on_24h"] - d["fan_on"]
d["excess_vent"] = (d["co2"] - 420) * d["fan_on_24h"]
d["excess_novent"] = (d["co2"] - 420) * (1 - d["fan_on_24h"])
d["active_novent"] = d["active_1h"] * (1 - d["fan_on_24h"])
d["active_vent"] = d["active_1h"] * d["fan_on_24h"]
''').replace('"co2_d30", "co2_d60", "active_1h"]', '"co2_d30", "co2_d60", "active_1h", "fan_change_exp", "excess_vent", "excess_novent", "active_novent", "active_vent"]')
exec(src)
def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
yd = y - last
inter = ["fan_change_exp__t-4", "excess_vent__t-4", "excess_novent__t-4", "active_novent__t-4", "active_vent__t-4"]
prev = [c for c in all_cols if c not in inter]
print("persistence", rmse(yd[va], 0), rmse(yd[te], 0))
for fs_name, fs in [("prev", prev), ("inter", all_cols), ("inter_nohour", [c for c in all_cols if c not in ("hour_sin","hour_cos")])]:
    for a in [1, 10, 100, 1000, 3000]:
        r = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=a)).fit(X.loc[tr, fs], yd[tr])
        print(fs_name, "ridge", a, round(rmse(yd[va], r.predict(X.loc[va, fs])),2), round(rmse(yd[te], r.predict(X.loc[te, fs])),2), flush=True)
    for lr, leaf, msl, l2, it in [(0.05, 7, 100, 1.0, 100), (0.05, 15, 50, 0.1, 200), (0.1, 7, 100, 1.0, 100), (0.05, 7, 50, 0.0, 200)]:
        h = HistGradientBoostingRegressor(learning_rate=lr, max_leaf_nodes=leaf, min_samples_leaf=msl, l2_regularization=l2, max_iter=it, random_state=0).fit(X.loc[tr, fs], yd[tr])
        print(fs_name, "hgb", (lr, leaf, msl, l2, it), round(rmse(yd[va], h.predict(X.loc[va, fs])),2), round(rmse(yd[te], h.predict(X.loc[te, fs])),2), flush=True)
