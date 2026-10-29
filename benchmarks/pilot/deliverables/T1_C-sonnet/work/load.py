import pandas as pd, numpy as np

def load_raw(csv_path):
    """Parse the raw export into a UTC-indexed, sorted, de-duplicated 5-min numeric frame."""
    df = pd.read_csv(csv_path, sep=';', dtype=str, encoding='utf-8-sig', na_values=['#N/A'])
    ts = pd.to_datetime(df['timestamp'], utc=True, format='%Y-%m-%dT%H:%M:%S%z')
    df = df.drop(columns='timestamp')
    df.columns = [c.encode('ascii', 'ignore').decode().strip() for c in df.columns]
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df.index = ts
    df = df[~df.index.duplicated(keep='first')].sort_index()
    return df
