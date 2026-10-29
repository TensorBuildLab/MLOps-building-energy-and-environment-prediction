import pandas as pd, numpy as np, bemlops, warnings
warnings.filterwarnings("ignore")
from model import read_raw
d = read_raw("train.csv")[["chilled_water_energy", "ahu_fan_speed", "dry_bulb_temp"]]
d = d.loc["2021-11-01":"2021-11-05"]
cols = {"chilled_water_energy": "energy [kWh]", "ahu_fan_speed": "other", "dry_bulb_temp": "outdoor_air_temperature [degC]"}
def prep(data):
    p = bemlops.Project(data, target="chilled_water_energy", columns=cols, horizon="1h"); p.check_data()
    return p.prepare(freq="5min")  # default options: stuck + spike masking on
full = prep(d)
cut = pd.Timestamp("2021-11-03 23:00")
part = prep(d[d.index < cut])
a = full.loc[full.index < cut, "chilled_water_energy"]; b = part.loc[part.index < cut, "chilled_water_energy"]
diff = a.isna() != b.isna()
print("target readings before the cut whose masking changes when later data is added:", int(diff.sum()),
      "from", a.index[diff].min(), "to", a.index[diff].max())
