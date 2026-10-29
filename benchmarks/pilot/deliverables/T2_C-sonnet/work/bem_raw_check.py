"""What does bemlops.check_data say about the RAW export (only timestamps parsed; no cleaning of values)?"""
import warnings
import numpy as np, pandas as pd, bemlops
warnings.filterwarnings("ignore")
raw = pd.read_csv("../train.csv")
raw["timestamp"] = raw["timestamp"].str.replace(" +08:00", "", regex=False)
cols = {
    "chilled_water_energy [kWh]": "energy [kWh]",
    "cooling_coil_valve_command [%]": "position [%]",
    "air_temperature [Celsius]": "zone_air_temperature [degC]",
    "dry_bulb_temp [Celsius]": "outdoor_air_temperature [degC]",
    "outdoor_relative_humidity [%]": "relative_humidity [%]",
    "wifi_connected_devices [number]": "occupancy_count",
}
try:
    p = bemlops.Project(raw, target="chilled_water_energy [kWh]", columns=cols, horizon="1h",
                        timestamp="timestamp", timestamp_format="%Y-%m-%d %H:%M")
    print(p.check_data())
except Exception as e:
    import traceback; traceback.print_exc()
# same with the duplicate/unsorted timestamps already removed, to see value-level checks
raw2 = raw.drop_duplicates("timestamp", keep="last").sort_values("timestamp")
p = bemlops.Project(raw2, target="chilled_water_energy [kWh]", columns=cols, horizon="1h",
                    timestamp="timestamp", timestamp_format="%Y-%m-%d %H:%M")
print("=== de-duplicated and sorted ===")
print(p.check_data())
