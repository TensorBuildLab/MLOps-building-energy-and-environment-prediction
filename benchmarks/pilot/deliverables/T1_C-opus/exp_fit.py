"""Experiment: first bemlops fit (exploration only)."""
import sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pandas as pd
import train

t = time.time()
p = train.build()
r = p.check_data()
prep = p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
for s in p.prepare_log:
    print(s)
print(prep.shape, prep.index[:3])
res = p.fit(random_state=0)
print(res)
for f in res.features:
    print(f)
print(res.split)
print(res.validation)
print(res.predictions.head())
print("elapsed", time.time() - t)
res.predictions.to_pickle(HERE / "work_preds_v1.pkl")
