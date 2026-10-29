import pandas as pd, numpy as np, bemlops, warnings, sys
warnings.filterwarnings("ignore")
from bemlops import features
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from model import load
df = load("train.csv")
base = {
    "chilled_water_energy": "energy [kWh]",
    "ahu_fan_speed": "other",
    "cooling_coil_valve_command": "position [%]",
    "cooling_coil_valve_position": "position [%]",
    "offcoil_air_temp": "supply_air_temperature [degC]",
    "supply_air_temperature": "supply_air_temperature [degC]",
    "air_temperature": "zone_air_temperature [degC]",
    "indoor_relative_humidity": "relative_humidity [%]",
    "indoor_co2": "co2 [ppm]",
    "occupant_count": "occupancy_count [count]",
    "wifi_connected_devices": "other",
    "dry_bulb_temp": "outdoor_air_temperature [degC]",
    "outdoor_relative_humidity": "relative_humidity [%]",
    "global_horizontal_solar_radiation": "solar_irradiance [W/m2]",
    "ahu_fan_energy": "energy [kWh]",
    "lighting_energy": "energy [kWh]",
    "plug_load_energy": "energy [kWh]",
    "tod_min": {"quantity": "other", "known_ahead": True},
    "sched_window": {"quantity": "other", "known_ahead": True},
    "holiday": {"quantity": "other", "known_ahead": True},
    "cw_level_prev": "other",
}
p = bemlops.Project(df[list(base)], target="chilled_water_energy", columns=base, horizon="1h")
p.check_data()
prep = p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
X, y, feats = features.build_features(prep, "chilled_water_energy", p.specs, horizon=4, step=pd.Timedelta("15min"))
print(list(X.columns))
m = y.notna()
folds = [("2021-10-26", "2021-11-06"), ("2021-11-08", "2021-12-31")]
default = [c for c in X.columns if not c.startswith(("tod_min", "sched_window", "holiday", "cw_level_prev"))]
sets = {
    "bemlops default": default,
    "+tod": default + ["tod_min"],
    "+tod+sched+hol": default + ["tod_min", "sched_window", "holiday"],
    "+tod+sched+hol+level": default + [c for c in X.columns if c.startswith(("tod_min", "sched_window", "holiday", "cw_level_prev"))],
}
small = [c for c in X.columns if c.startswith(("chilled_water_energy", "ahu_fan_speed", "cooling_coil_valve_command", "dry_bulb_temp", "global_horizontal", "air_temperature", "occupant_count", "hour_", "dow_", "tod_min", "sched_window", "holiday", "cw_level_prev"))]
sets["small+all derived"] = small
def models():
    return {"hgb": HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20, random_state=0),
            "rf": RandomForestRegressor(n_estimators=200, min_samples_leaf=3, max_features=0.5, n_jobs=3, random_state=0)}
for name, cols in sets.items():
    line = f"{name:28s}"
    for a, b in folds:
        tr = m & (X.index < pd.Timestamp(a) - pd.Timedelta("1h"))
        te = m & (X.index >= pd.Timestamp(a)) & (X.index < pd.Timestamp(b))
        for mn, mdl in models().items():
            Xt = X.loc[tr, cols]
            if mn == "rf": Xt = Xt.fillna(Xt.median()); Xe = X.loc[te, cols].fillna(Xt.median())
            else: Xe = X.loc[te, cols]
            mdl.fit(Xt, y[tr]); pr = np.clip(mdl.predict(Xe), 0, None)
            line += f" | {a[5:]} {mn} {np.sqrt(((pr - y[te]) ** 2).mean()):.3f}"
        pers = X.loc[te, "chilled_water_energy__t-4"]
        line += f" (pers {np.sqrt(((pers-y[te])**2).mean()):.2f}, n={te.sum()})"
    print(line, flush=True)
