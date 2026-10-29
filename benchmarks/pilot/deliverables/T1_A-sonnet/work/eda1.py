import pandas as pd, numpy as np
df = pd.read_csv('train.csv', sep=';', na_values=['#N/A'], dtype=str)
print(df.shape)
print(df.timestamp.head(3).tolist(), df.timestamp.tail(3).tolist())
ts = df.timestamp
print(ts.str[-5:].value_counts())
print(ts.duplicated().sum())
# non-numeric values
for c in df.columns[1:]:
    s = pd.to_numeric(df[c], errors='coerce')
    bad = df[c][s.isna() & df[c].notna()]
    print(c, 'nonnum', bad.unique()[:10], 'na', df[c].isna().sum(), 'min', s.min(), 'max', s.max(), 'mean', round(s.mean(),2))
