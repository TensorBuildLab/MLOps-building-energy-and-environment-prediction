"""Exploration helpers: causal cleaning of the raw export."""
import numpy as np
import pandas as pd

CW = "chilled_water_energy"


def load_raw(csv_path):
    df = pd.read_csv(csv_path)
    ts = df["timestamp"].astype(str).str.replace(r"\s*[+-]\d\d:?\d\d$", "", regex=True)
    df["ts"] = pd.to_datetime(ts, format="%Y-%m-%d %H:%M")
    df = df.drop(columns="timestamp")
    df.columns = [c.split(" [")[0] if c != "ts" else c for c in df.columns]
    df = df.drop_duplicates("ts", keep="last").set_index("ts").sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def clean5(df):
    """Per-row (causal) cleaning of the 5-min data."""
    df = df.copy()
    cw = df[CW].where(df[CW] > -900)
    cw = cw.where(cw >= 0)
    # meter outage: reads exactly 0 while the cooling coil valve is commanded open
    fault0 = (cw == 0) & (df["cooling_coil_valve_command"] > 15)
    # stuck: exactly the same non-zero value as the previous sample
    stuck = (cw > 0) & (cw == cw.shift(1))
    df["cw_fault"] = (fault0 | stuck).astype(float)
    df[CW] = cw.mask(fault0 | stuck)
    t = df["air_temperature"]
    df["air_temperature"] = np.where(t > 45, (t - 32) / 1.8, t)
    return df
