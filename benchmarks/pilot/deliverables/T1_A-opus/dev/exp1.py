import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
from cv import *
import time
P = dict(max_iter=150, learning_rate=0.1, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, early_stopping=False)
t=time.time()
r, p_all = run(ALL, P, "HGB all feats", verbose=True); print(time.time()-t, flush=True)
df[["y","y_raw","c0"]].assign(p=p_all).to_pickle("cv_preds_all.pkl")
