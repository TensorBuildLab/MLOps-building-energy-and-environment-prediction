"""Own causal feature builder on the 15-min grid (for experiments)."""
import numpy as np
import pandas as pd
from prep import *

SUMCOLS = [CW, "ahu_fan_energy"]
MEANCOLS = ["cooling_coil_valve_command", "ahu_fan_speed", "offcoil_air_temp", "dry_bulb_temp",
            "global_horizontal_solar_radiation", "outdoor_relative_humidity", "air_temperature",
            "wind_speed", "indoor_co2"]


def grid15(df5):
    r = df5.resample("15min")
    n = r[CW].count()
    # CW: sum of the three 5-min values; scale up if exactly one slot is missing; NaN otherwise
    s = r[CW].sum(min_count=1)
    y = s * 3.0 / n.replace(0, np.nan)
    y = y.where(n >= 2)
    g = pd.concat([r[["ahu_fan_energy"]].sum(min_count=1), r[MEANCOLS].mean()], axis=1)
    g["y"] = y
    g["y_complete"] = (n == 3).astype(float)
    full = pd.date_range(g.index.min().floor("D"), g.index.max().floor("D") + pd.Timedelta("23h45min"), freq="15min")
    return g.reindex(full)


def build(g, lags_y=(4, 5, 6, 7, 8, 12, 16), lags_x=(4, 5, 6), day_lag=True):
    X = pd.DataFrame(index=g.index)
    mod = g.index.hour * 60 + g.index.minute
    X["mod"] = mod
    X["wkday"] = (g.index.dayofweek < 5).astype(float)
    for k in lags_y:
        X[f"y_l{k}"] = g["y"].shift(k)
    for c in ["cooling_coil_valve_command", "ahu_fan_speed", "offcoil_air_temp", "dry_bulb_temp",
              "global_horizontal_solar_radiation", "outdoor_relative_humidity", "air_temperature"]:
        for k in lags_x:
            X[f"{c}_l{k}"] = g[c].shift(k)
    # rolling mean of y over the last 2h available at forecast time (lags 4..11), only when AHU was on
    on = (g["y"] > 1.0).astype(float)
    yon = g["y"].where(g["y"] > 1.0)
    X["y_on_mean"] = yon.shift(4).rolling(8, min_periods=1).mean()
    X["n_on"] = on.shift(4).rolling(8, min_periods=1).sum()
    if day_lag:
        X["y_d1"] = g["y"].shift(96)
        X["y_d1_mean"] = yon.shift(96).rolling(12, min_periods=1, center=False).mean()
    return X
