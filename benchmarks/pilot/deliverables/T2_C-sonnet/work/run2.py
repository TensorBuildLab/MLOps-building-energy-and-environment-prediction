import sys, warnings
import numpy as np, pandas as pd
import bemlops
from prep import *

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)

df5 = clean5(load_raw("../train.csv"))
SUMCOLS = [CW, "ahu_fan_energy", "lighting_energy", "plug_load_energy", "ceiling_fan_energy"]
MEANCOLS = ["cooling_coil_valve_command", "cooling_coil_valve_position", "ahu_fan_speed", "offcoil_air_temp",
            "supply_air_temperature", "dry_bulb_temp", "global_horizontal_solar_radiation", "outdoor_relative_humidity",
            "wind_speed", "air_temperature", "indoor_relative_humidity", "indoor_co2", "occupant_count",
            "wifi_connected_devices", "temp_setpoint", "baromatic_pressure"]
r = df5.resample("15min")
d15 = pd.concat([r[SUMCOLS].sum(min_count=3), r[MEANCOLS].mean()], axis=1)
d15 = d15[r[CW].count() > 0]  # drop pure-gap intervals
# calendar features (known ahead)
mod = d15.index.hour * 60 + d15.index.minute
d15["minute_of_day"] = mod
d15["weekday"] = (d15.index.dayofweek < 5).astype(float)

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
    "wifi_connected_devices": "occupancy_count",
    "minute_of_day": {"quantity": "other", "known_ahead": True},
}
p = bemlops.Project(d15, target=CW, columns=columns, horizon="1h", name="t2_cw",
                    intended_use="1 h ahead forecast of 15-min chilled water energy")
rep = p.check_data()
print(rep)

p.prepare(freq="15min")
for s in p.prepare_log: print(s)
import time; t=time.time()
res = p.fit(models=['ridge','gbm'], n_iter=4)
print('fit secs', time.time()-t)
print(res)
