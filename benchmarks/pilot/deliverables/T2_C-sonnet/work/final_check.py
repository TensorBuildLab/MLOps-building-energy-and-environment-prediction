import time, sys, numpy as np, pandas as pd
sys.path.insert(0, ".")
import model
t = time.time(); p = model.predict("train.csv"); print("predict secs", round(time.time() - t, 1))
print(type(p), p.dtype, type(p.index).__name__, p.index.tz, len(p), p.index.min(), p.index.max(), p.isna().sum(), (p < 0).sum())
raw = pd.read_csv("train.csv").drop_duplicates("timestamp", keep="last")
ts = pd.to_datetime(raw.timestamp.str.replace(" +08:00", ""), format="%Y-%m-%d %H:%M")
c = raw["chilled_water_energy [kWh]"].where(raw["chilled_water_energy [kWh]"] > -900).groupby(ts.dt.floor("15min")).sum(min_count=3)
# truth restricted to the days where the meter works (exclude the 5-week outage)
ok = (c.index >= "2021-10-27") & ~((c.index >= "2021-11-03 18:30") & (c.index < "2021-11-04 10:30")) & ~((c.index >= "2021-11-17 14:00") & (c.index < "2021-11-18"))
cc = c[ok].dropna()
e = (cc - p.reindex(cc.index))
print("in-sample RMSE (alignment check only)", round(float(np.sqrt((e**2).mean())), 3), "n", int(e.notna().sum()))
print(p["2021-11-02 07:45":"2021-11-02 09:00"].round(2).to_dict())
d = pd.DataFrame({"y": cc, "p": p.reindex(cc.index)}); d["e"] = d.y - d.p
print(d.reindex(d.e.abs().sort_values(ascending=False).index).head(25).round(2).to_string())
print((d.e ** 2).groupby(d.index.date).sum().round(0).sort_values(ascending=False).head(10))
