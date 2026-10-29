import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "2")
from cv import *
import time
P = dict(max_iter=150, learning_rate=0.1, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, early_stopping=False)
P2 = dict(max_iter=200, learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=100, l2_regularization=3.0, early_stopping=False)
DROP = ["damp", "damp_d1", "win", "lux", "rad", "tsup", "tout", "sol_s", "ppl", "ppl_1h", "fan", "dow"]
CORE = [f for f in ALL if f not in DROP]
W = week_starts[-5:]
job = sys.argv[1]
cfgs = {
 "1": [("all P", ALL, P, None), ("all P tau21", ALL, P, 21)],
 "2": [("core P", CORE, P, None), ("core P tau21", CORE, P, 21)],
 "3": [("all P2 tau21", ALL, P2, 21), ("core P2", CORE, P2, None)],
}[job]
print("n feats all", len(ALL), "core", len(CORE), flush=True)
for name, feats, prm, tau in cfgs:
    t = time.time()
    r, p = run(feats, prm, name, weeks=W, tau=tau, verbose=True)
    df[["y"]].assign(p=p).to_pickle("cv3_%s.pkl" % name.replace(" ", "_"))
    print("  %.0fs" % (time.time() - t), flush=True)
