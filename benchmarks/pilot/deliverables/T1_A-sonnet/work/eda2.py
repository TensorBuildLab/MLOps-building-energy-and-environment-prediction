import pandas as pd, numpy as np
df = pd.read_csv('train.csv', sep=';', na_values=['#N/A'], dtype=str, encoding='utf-8-sig')
ts = df.timestamp
loc = pd.to_datetime(ts.str[:19])
d = loc.diff()
idx = d[(d != pd.Timedelta('5min'))].index[1:]
for i in idx:
    print(i, ts[i-1], ts[i], d[i])
