import pandas as pd, numpy as np
def load(path='train.csv'):
    df = pd.read_csv(path, sep=';', na_values=['#N/A','OFFLINE'], encoding='utf-8-sig')
    df['t'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Copenhagen')
    df = df.drop_duplicates('t').sort_values('t').set_index('t').drop(columns='timestamp')
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df
