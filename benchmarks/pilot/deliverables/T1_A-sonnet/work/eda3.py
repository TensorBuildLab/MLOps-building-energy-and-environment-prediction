import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df = pd.read_csv('train.csv', sep=';', na_values=['#N/A'], dtype=str, encoding='utf-8-sig')
df['loc'] = pd.to_datetime(df.timestamp.str[:19])
co2c='RoomB:Sensor__CO2'
for c in df.columns[1:-1]:
    df[c]=pd.to_numeric(df[c], errors='coerce')
# duplicated day
a = df.iloc[:25177]; 
print(df.loc[25170:25180,['timestamp',co2c,'Outdoor:Temperature_air']])
d = df[df.timestamp.duplicated(keep=False)]
print(len(d), d.timestamp.min(), d.timestamp.max())
g = d.groupby('timestamp')
# compare copies
cols=[c for c in df.columns[1:-1]]
first = d.drop_duplicates('timestamp', keep='first').set_index('timestamp')[cols]
last = d.drop_duplicates('timestamp', keep='last').set_index('timestamp')[cols]
diff = ((first!=last) & ~(first.isna()&last.isna())).sum()
print(diff)
print('rows after dup start', len(df)-25177)
# reversed block
print(df.loc[16125:16135,['timestamp',co2c]])
print(df.loc[16155:16163,['timestamp',co2c]])
