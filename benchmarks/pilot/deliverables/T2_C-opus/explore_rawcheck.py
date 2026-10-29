import pandas as pd, numpy as np, bemlops, warnings
warnings.filterwarnings("ignore")
# raw export straight into bemlops (only the column names shortened), to see what the checks catch
raw = pd.read_csv("train.csv")
raw.columns = [c.split(" [")[0] for c in raw.columns]
cols = {"chilled_water_energy": "energy [kWh]", "air_temperature": "zone_air_temperature [degC]",
        "dry_bulb_temp": "outdoor_air_temperature [degC]", "outdoor_relative_humidity": "relative_humidity [%]",
        "ahu_fan_speed": "other", "supply_air_flow": "airflow [m3/h]", "damper_position": "position [%]"}
p = bemlops.Project(raw[["timestamp"] + list(cols)], target="chilled_water_energy", columns=cols, horizon="1h",
                    timestamp="timestamp")
print(p.check_data())
