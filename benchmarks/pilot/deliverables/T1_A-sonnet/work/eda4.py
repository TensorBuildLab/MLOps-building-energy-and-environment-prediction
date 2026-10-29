import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_rows',200)
df = pd.read_csv('train.csv', sep=';', na_values=['#N/A'], dtype=str, encoding='utf-8-sig')
df['loc'] = pd.to_datetime(df.timestamp.str[:19])
for c in df.columns[1:-1]:
    df[c]=pd.to_numeric(df[c], errors='coerce')
df = df.drop_duplicates('timestamp', keep='first').sort_values('loc').set_index('loc')
df.columns = [c.replace('fa\xe7ade','facade') if False else c for c in df.columns]
co2='RoomB:Sensor__CO2'
print(df.index.min(), df.index.max(), len(df))
# NA by day
na = df.drop(columns='timestamp').isna().groupby(df.index.date).mean()
print(na[[co2,'RoomB:People__amount','Outdoor:Temperature_air','RoomB:Room__active','RoomB:Sensor__room_temperature']].round(2).to_string())
