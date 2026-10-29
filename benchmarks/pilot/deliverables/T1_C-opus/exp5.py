"""Exploration: does adding the summer-schedule weeks to training help on the last 2 weeks?"""
import sys; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
_s = open(HERE / "exp4.py").read(); exec(_s[:_s.index("exec(src)") + len("exec(src)")])
def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
yd = y - last; inter = ["fan_change_exp__t-4", "excess_vent__t-4", "excess_novent__t-4", "active_novent__t-4", "active_vent__t-4"]; prev = [c for c in all_cols if c not in inter]
trv = tr | va
print("persistence test", rmse(yd[te], 0))
for fs_name, fs in [("prev", prev), ("inter", all_cols)]:
    for trn_name, trn in [("train", tr), ("train+val", trv)]:
        r = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=1000)).fit(X.loc[trn, fs], yd[trn])
        h = HistGradientBoostingRegressor(learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=100, l2_regularization=1.0, max_iter=100, random_state=0).fit(X.loc[trn, fs], yd[trn])
        pr, ph = r.predict(X.loc[te, fs]), h.predict(X.loc[te, fs])
        out = [fs_name, trn_name, "ridge", round(rmse(yd[te], pr), 2), "hgb", round(rmse(yd[te], ph), 2)]
        for a in [0.5, 0.75, 1.0]:
            out += [f"avg*{a}", round(rmse(yd[te], a * (pr + ph) / 2), 2)]
        print(out, flush=True)
