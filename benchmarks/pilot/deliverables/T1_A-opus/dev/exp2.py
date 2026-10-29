import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
from cv import *
import time
P = dict(max_iter=150, learning_rate=0.1, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, early_stopping=False)
CORE = ["c0", "c0_med", "c0_last", "c0_max", "c0_min", "c_age", "d1", "d2", "d3", "d4", "d8", "d12", "d24",
        "roll4h_max", "roll4h_min", "roll24h_min", "roll24h_max", "roll24h_mean", "c0_above_min24",
        "y1d", "y1d_chg", "y7d", "y7d_chg", "act", "light", "fan_on", "troom", "act_1h", "act_4h", "act_24h",
        "troom_d4", "troom_d1", "fan_on_1d", "fan_on_7d", "act_1d", "act_7d", "fan_on_1d_prev", "act_1d_max",
        "hour", "dow", "workday"]
NOCAL = [f for f in CORE if f not in ("dow",)]
MIN = ["c0", "c0_last", "d1", "d4", "c0_above_min24", "y1d_chg", "y7d_chg", "act", "act_1h", "fan_on",
       "fan_on_1d", "act_1d", "hour", "workday", "troom_d4"]
for name, feats in (("core", CORE), ("core-no-dow", NOCAL), ("minimal", MIN)):
    t = time.time()
    r, p = run(feats, P, "HGB " + name)
    df[["y"]].assign(p=p).to_pickle(f"cv_preds_{name}.pkl")
    print("  %.0fs" % (time.time() - t), flush=True)
