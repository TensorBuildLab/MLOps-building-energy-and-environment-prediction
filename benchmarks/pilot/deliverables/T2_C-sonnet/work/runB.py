"""bemlops run on the cleaned 15-min grid with causal prepare options."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
import sys, warnings, time, json
import numpy as np, pandas as pd
import bemlops
from feat import *
warnings.filterwarnings("ignore")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)

df5 = clean5(load_raw("../train.csv"))
g = grid15(df5)
d = g.copy()
d[CW] = g["y"].where(g["y_complete"] == 1)       # strict: complete intervals only
d["minute_of_day"] = (d.index.hour * 60 + d.index.minute).astype(float)
d = d[g[["y", "ahu_fan_energy", "cooling_coil_valve_command"]].notna().any(axis=1)]  # drop pure-gap rows

columns = {
    CW: "energy [kWh]",
    "ahu_fan_energy": "energy [kWh]",
    "cooling_coil_valve_command": "position [%]",
    "ahu_fan_speed": "other",
    "offcoil_air_temp": "supply_air_temperature [degC]",
    "dry_bulb_temp": "outdoor_air_temperature [degC]",
    "global_horizontal_solar_radiation": "solar_irradiance [W/m2]",
    "outdoor_relative_humidity": "relative_humidity [%]",
    "air_temperature": "zone_air_temperature [degC]",
    "minute_of_day": {"quantity": "other", "known_ahead": True},
}
p = bemlops.Project(d, target=CW, columns=columns, horizon="1h", name="t2_cw_B",
                    intended_use="1 h ahead forecast of 15-min chilled water energy (AHU, library room)")
print(p.check_data(), flush=True)
p.note("chilled_water_energy: -999 placeholders and negative values set missing; zeros while cooling-coil valve command >15% "
       "(meter outage 2021-09-21..2021-10-26, 2021-11-17 15:15..18:35) and repeated identical non-zero readings (stuck, 2021-11-03/04) set missing in own code.")
p.note("air_temperature: values >45 are degF (from 2021-11-08), converted to degC.")
p.note("wifi/occupancy columns not used: stuck for hours and unreliable; supply_air_flow/damper_position mostly missing.")
p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
for s in p.prepare_log: print(s)
t = time.time()
res = p.fit(models=["ridge", "gbm"], n_iter=6)
print("fit secs", time.time() - t, flush=True)
print(res, flush=True)
print([a for a in dir(res) if not a.startswith("_")], flush=True)
folder = p.save_run("bem_runs/")
print("saved", folder, flush=True)
for f in sorted(os.listdir(folder)): print("  ", f)
