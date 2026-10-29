import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "2")
from cv import *
import time
P2 = dict(max_iter=200, learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=100, l2_regularization=3.0, early_stopping=False)
P3 = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=5, min_samples_leaf=150, l2_regularization=5.0, early_stopping=False)
DROP = ["damp", "damp_d1", "win", "lux", "rad", "tsup", "tout", "sol_s", "ppl", "ppl_1h", "fan", "dow"]
CORE = [f for f in ALL if f not in DROP]
LEAN = [f for f in CORE if f not in ("troom", "troom_d1", "troom_d4", "act_24h", "roll24h_mean", "roll24h_max",
                                     "y7d", "y7d_chg", "act_7d", "fan_on_7d", "fan_on_1d", "act_1d", "y1d", "y1d_chg")]
W = week_starts[-5:]
job = sys.argv[1]
cfgs = {
 "1": [("core P3", CORE, P3, W)],
 "2": [("lean P2", LEAN, P2, W)],
 "3": [("core P2 9folds", CORE, P2, None)],
}[job]
print("lean", LEAN, flush=True)
for name, feats, prm, weeks in cfgs:
    t = time.time()
    r, p = run(feats, prm, name, weeks=weeks, verbose=True)
    df[["y"]].assign(p=p).to_pickle("cv4_%s.pkl" % name.replace(" ", "_"))
    print("  %.0fs" % (time.time() - t), flush=True)
