"""Exploration: bemlops fit (ridge + gbm) with derived inputs, level target; inspect deployed model."""
import sys, time; from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import numpy as np, pandas as pd, bemlops
import model as m
t0 = time.time()
d = m.add_features(pd.read_pickle(HERE / "work_clean5.pkl"))
cols = {
    "co2": {"quantity": "co2", "unit": "ppm", "flat_ok": True},
    "room_temp": "zone_air_temperature [degC]", "room_active": "occupancy_status",
    "damper": "position [%]", "light_on": "equipment_status", "window": "equipment_status",
    "supply_flow": "airflow [m3/h]", "oat": "outdoor_air_temperature [degC]",
}
cols.update({k: "other" for k in m.DERIVED})
p = bemlops.Project(d, target="co2", columns=cols, horizon="1h")
p.check_data()
p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
fr = eval(sys.argv[1]) if len(sys.argv) > 1 else None
res = p.fit(models=["ridge", "gbm"], n_iter=10, random_state=0, fractions=fr)
print(res)
print(res.split)
print(res.validation.to_string())
mdl = res.model
print({k: (v if not hasattr(v, "shape") else v.shape) for k, v in vars(mdl).items() if k not in ("estimator",)})
print("elapsed", time.time() - t0)
