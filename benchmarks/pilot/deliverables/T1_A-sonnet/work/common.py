import pandas as pd, numpy as np
def load(path='train.csv'):
    df = pd.read_csv(path, sep=';', na_values=['#N/A'], dtype=str, encoding='utf-8-sig')
    df['loc'] = pd.to_datetime(df.timestamp.str[:19])
    cols = list(df.columns[1:-1])
    for c in cols:
        df[c]=pd.to_numeric(df[c], errors='coerce')
    df = df.drop_duplicates('timestamp', keep='first').sort_values('loc').set_index('loc')
    return df
NAMES = ['Tout','Wind','SolE','SolS','SolW','ElVent','Flow','TSup','DH','HC','CO2','Troom','People','Active','Damper','Rad','LightLvl','LightOn','Window','Tset','Hlim','Clim']
def load2(path='train.csv'):
    df = load(path).drop(columns='timestamp'); df.columns = NAMES
    return df
