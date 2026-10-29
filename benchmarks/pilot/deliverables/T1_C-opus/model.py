"""1-hour-ahead forecast of the 15-minute mean CO2 in Room B (ppm).

predict(csv_path) loads a raw trend export in the same format as train.csv,
cleans it with strictly row-wise (causal) rules, and runs the saved bemlops
model. Every forecast for the interval starting at T uses only rows with
timestamps before T - 45 min.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MODEL_FILE = HERE / "bemlops_model" / "model.joblib"
TZ = "Europe/Copenhagen"
TARGET = "co2"

# raw point name (ASCII-folded) -> short name used in the model
POINTS = {
    "RoomB:Sensor__CO2": "co2",
    "RoomB:Sensor__room_temperature": "room_temp",
    "RoomB:Room__active": "room_active",
    "RoomB:Damper__position": "damper",
    "RoomB:Light__on_off_signal": "light_on",
    "RoomB:Light__level__ceiling": "light_level",
    "RoomB:Window__opened_closed": "window",
    "RoomB:People__amount": "people",
    "RoomB:Radiator__control_signal__motor_valve": "radiator_valve",
    "Ventilation:Fan__air_flow__supply": "supply_flow",
    "Ventilation:EL_meter__power": "vent_power",
    "Ventilation:Sensor__air_temperature__supply": "supply_temp",
    "Outdoor:Temperature_air": "oat",
    "Outdoor:Wind__velocity": "wind",
    "Outdoor:Solar__direct_radiation__south_facade": "sol_south",
    "Outdoor:Solar__direct_radiation__east_facade": "sol_east",
    "Outdoor:Solar__direct_radiation__west_facade": "sol_west",
}


def _fold(name: str) -> str:
    return (name.replace("ç", "c").replace("﻿", "").strip())


def load_clean(csv_path) -> pd.DataFrame:
    """Raw export -> one row per timestamp (tz-aware local time), cleaned row by row.

    Every rule here looks at one reading at a time, so a value never depends
    on later rows (safe for forecasting).
    """
    raw = pd.read_csv(csv_path, sep=";", dtype=str, encoding="utf-8-sig",
                      keep_default_na=False)
    raw.columns = [_fold(c) for c in raw.columns]
    ts_col = raw.columns[0]
    # Offsets change with daylight saving (+0100 / +0200): parse to UTC, then local.
    ts = pd.to_datetime(raw[ts_col], utc=True, errors="coerce", format="ISO8601")
    out = pd.DataFrame(index=pd.DatetimeIndex(ts).tz_convert(TZ))
    for rawname, short in POINTS.items():
        if rawname in raw.columns:
            # '#N/A', 'OFFLINE' and any other text -> missing
            vals = pd.to_numeric(raw[rawname].str.strip().str.replace(",", ".", regex=False),
                                 errors="coerce").to_numpy(dtype=float)
        else:
            vals = np.full(len(raw), np.nan)
        out[short] = vals
    out = out[out.index.notna()]

    # placeholders such as -999 / 9999 in any point
    out = out.mask(out.isin([-999.0, -9999.0, 9999.0, 32767.0, -32768.0]))

    # CO2: physically plausible indoor range only
    out["co2"] = out["co2"].where((out["co2"] >= 250) & (out["co2"] <= 5000))
    # Room temperature: the BAS switched this point to degF on 2023-05-12.
    # A room reading above 50 can only be degF; convert it reading by reading.
    rt = out["room_temp"]
    out["room_temp"] = rt.where(rt <= 50, (rt - 32.0) * 5.0 / 9.0)
    out["room_temp"] = out["room_temp"].where(out["room_temp"].between(5, 45))
    # Outdoor temperature: isolated readings of 57-73 degC are glitches.
    out["oat"] = out["oat"].where(out["oat"].between(-40, 45))
    out["wind"] = out["wind"].where(out["wind"].between(0, 60))
    for c in ["sol_south", "sol_east", "sol_west"]:
        out[c] = out[c].where(out[c].between(0, 1500))
    for c in ["damper", "radiator_valve"]:
        out[c] = out[c].where(out[c].between(0, 100))
    for c in ["room_active", "light_on", "window"]:
        out[c] = out[c].where(out[c].isin([0.0, 1.0]))
    for c in ["supply_flow", "vent_power", "people", "light_level"]:
        out[c] = out[c].where(out[c] >= 0)

    # exact duplicate rows (a day was exported twice) and out-of-order blocks:
    # average rows that share a timestamp, then sort.
    out = out.groupby(level=0).mean().sort_index()
    out.index.name = "timestamp"
    return out


def _past(s: pd.Series, ago: str, index) -> pd.Series:
    """Value of `s` measured `ago` before each timestamp (purely backward-looking)."""
    return s.shift(freq=ago).reindex(index)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derived inputs, each computed from past and present readings only.

    bemlops lags every measured input by the 1 h horizon, so a column built
    here from data 23 h old ends up describing the same time of day 24 h
    before the target interval.
    """
    df = df.copy()
    fan_on = (df["supply_flow"] > 1000).astype(float).where(df["supply_flow"].notna())
    df["fan_on"] = fan_on
    # ventilation schedule seen at the target's time of day yesterday / last week
    df["fan_on_24h"] = _past(fan_on, "23h", df.index)
    df["fan_on_7d"] = _past(fan_on, "167h", df.index)
    # occupancy at the target's time of day yesterday / last week
    df["active_24h"] = _past(df["room_active"], "23h", df.index)
    df["active_7d"] = _past(df["room_active"], "167h", df.index)
    # recent CO2 trend (reading now minus 30 min / 60 min earlier)
    df["co2_d30"] = df["co2"] - _past(df["co2"], "30min", df.index)
    df["co2_d60"] = df["co2"] - _past(df["co2"], "60min", df.index)
    # share of the last hour with the room marked active (trailing window)
    df["active_1h"] = df["room_active"].rolling("60min", min_periods=1).mean()
    # mass-balance style interactions: will the fan run at the target time
    # (judged from yesterday's schedule), and how far CO2 is above outdoor level
    df["fan_change_exp"] = df["fan_on_24h"] - df["fan_on"]
    df["excess_vent"] = (df["co2"] - 420.0) * df["fan_on_24h"]
    df["excess_novent"] = (df["co2"] - 420.0) * (1.0 - df["fan_on_24h"])
    df["active_vent"] = df["active_1h"] * df["fan_on_24h"]
    df["active_novent"] = df["active_1h"] * (1.0 - df["fan_on_24h"])
    return df


DERIVED = ["fan_on_24h", "fan_on_7d", "active_24h", "active_7d", "co2_d30", "co2_d60",
           "active_1h", "fan_change_exp", "excess_vent", "excess_novent", "active_vent",
           "active_novent"]


STEP = pd.Timedelta("15min")
FALLBACK_PPM = 467.0  # training median of the 15-min CO2 mean; used only if no CO2 was ever seen


def to_15min(df5: pd.DataFrame) -> pd.DataFrame:
    """15-min means labelled by interval start, plus the modelling target.

    co2_chg(T) = mean CO2 of interval T minus mean CO2 of interval T-60 min,
    i.e. the change over the forecast horizon. It is only ever a target; bemlops
    uses it as an input only lagged by >= 1 h (= c(T-1h) - c(T-2h)).
    """
    q = df5.resample("15min").mean()
    q["co2_chg"] = q["co2"] - q["co2"].shift(4)
    q.index.name = "timestamp"
    return q


def predict(csv_path: str) -> pd.Series:
    """One forecast per 15-min interval (index = interval start, Europe/Copenhagen).

    The value for interval T uses only rows stamped before T - 45 min.
    """
    import bemlops

    df5 = add_features(load_clean(csv_path))
    if df5.empty:
        return pd.Series(dtype=float, name="co2_forecast")
    data = to_15min(df5)
    model = bemlops.load_model(MODEL_FILE)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # The live-data check still runs (result in model.last_check_), but a
        # failed check must not stop the batch of forecasts.
        out = model.predict(data, future=True, validate=True, on_error="warn")
    try:
        rep = model.last_check_
        if rep is not None and "ERROR" in str(rep):
            print("[model.py] live data check reported errors:\n" + str(rep), file=sys.stderr)
    except Exception:
        pass

    # Every 15-min interval from the first one in the file to the last one whose
    # inputs are complete: the interval starting at T needs the readings up to
    # T - 50 min (5-min logging), i.e. the bin [T-60, T-45) must have ended.
    first = df5.index.min().floor("15min")
    last_ok = (df5.index.max() + pd.Timedelta("5min")).floor("15min") + pd.Timedelta("45min")
    grid = pd.date_range(first, last_ok, freq=STEP, tz=df5.index.tz, name="timestamp")
    chg = out["predicted"].astype(float).reindex(grid)

    # Level = last 15-min CO2 mean known at forecast time (interval T-60 min,
    # carried forward over gaps) + predicted change. No model output -> no change.
    base = data["co2"].reindex(grid).ffill().shift(4)
    pred = (base + chg.fillna(0.0)).fillna(FALLBACK_PPM)
    pred.name = "co2_forecast"
    return pred


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "train.csv")
    s = predict(p)
    print(s.tail())
