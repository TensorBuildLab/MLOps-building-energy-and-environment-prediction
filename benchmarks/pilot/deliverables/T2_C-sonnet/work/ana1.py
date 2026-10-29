import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
d = pd.read_csv("cv4_preds.csv", index_col=0, parse_dates=True)
d["e"] = d.y - d.p3
big = d[d.e.abs() > 3]
print(big[["y", "p3", "e"]].round(2).to_string())
print(len(big), len(d))
raw = pd.read_csv("../train.csv")
raw["ts"] = pd.to_datetime(raw.timestamp.str.replace(" +08:00", ""), format="%Y-%m-%d %H:%M")
raw = raw.drop_duplicates("ts").set_index("ts").sort_index()
c = raw["chilled_water_energy [kWh]"]
for day in ["2021-10-28", "2021-11-12"]:
    x = c[f"{day} 17:45":f"{day} 18:50"]
    print(day, x.round(2).tolist())
