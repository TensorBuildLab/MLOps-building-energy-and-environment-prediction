"""1-hour-ahead forecast of chilled-water energy (kWh per 15-min interval).

predict(csv_path) loads the raw trend export, applies the same row-wise
(causal) cleaning that was used in training, and runs the saved bemlops model.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TARGET = "chilled_water_energy"

# --------------------------------------------------------------------------
# Loading and cleaning. Everything here is row-wise or uses past/present values
# only, so a forecast never depends on data after its cut-off time.
# --------------------------------------------------------------------------


def read_raw(csv_path: str) -> pd.DataFrame:
    """Raw 5-min table: local-time DatetimeIndex, short column names, numbers."""
    raw = pd.read_csv(csv_path, dtype=str, keep_default_na=True)
    ts_col = raw.columns[0]
    ts = pd.to_datetime(raw[ts_col].str.strip(), format="%Y-%m-%d %H:%M %z", errors="coerce", utc=True)
    if ts.isna().mean() > 0.5:  # different offset style: fall back to a flexible parser
        ts = pd.to_datetime(raw[ts_col].str.strip(), errors="coerce", utc=True)
    # building local time (Singapore, UTC+8, no daylight saving), naive
    ts = ts.dt.tz_convert("Asia/Singapore").dt.tz_localize(None)
    df = raw.drop(columns=[ts_col])
    df.columns = [c.split(" [")[0].strip() for c in df.columns]
    df = df.apply(lambda s: pd.to_numeric(s.str.replace(",", "", regex=False).str.strip(), errors="coerce"))
    df.index = pd.DatetimeIndex(ts, name="timestamp")
    df = df[df.index.notna()]
    # exact duplicate timestamps (a block of 2021-11-15/16 was exported twice): keep the first
    df = df[~df.index.duplicated(keep="first")]
    # a block of 2021-10-28 rows is in reverse order: sort
    df = df.sort_index()
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Row-wise fixes for faults found in the training export."""
    df = df.copy()
    # placeholder values
    df = df.mask(df.isin([-999, -9999, 9999, 99999, 32767, -32768]))
    # Temperatures. The zone air temperature switched to degF on 2021-11-08 04:45
    # (values ~80-86). In this Singapore room/AHU every degC reading is 13-36, every
    # degF reading of the same quantities is 55-97, so a reading > 55 is degF. The
    # same row-wise rule protects the other temperature points against a similar switch.
    for c, lo, hi in [("air_temperature", 15, 40), ("offcoil_air_temp", 5, 40),
                      ("supply_air_temperature", 5, 45), ("dry_bulb_temp", 15, 40)]:
        if c in df:
            t = df[c]
            t = t.where(t <= 55, (t - 32.0) * 5.0 / 9.0)
            # impossible values (e.g. outdoor-temperature spikes to 41-51 degC) -> missing
            df[c] = t.where((t > lo) & (t < hi))
    # relative humidity stored as a 0-1 fraction (not seen in training; cheap guard)
    for c in ["indoor_relative_humidity", "outdoor_relative_humidity", "supply_air_humidity"]:
        if c in df:
            h = df[c]
            h = h.where(h > 1.5, h * 100.0)
            df[c] = h.where((h >= 0) & (h <= 100.5))
    if "voc" in df:
        df["voc"] = df["voc"].where(df["voc"] < 2000)
    # negative readings of quantities that cannot be negative
    for c in [c for c in df.columns if c.endswith("_energy")] + ["ahu_fan_speed", "occupant_count",
                                                                 "cooling_coil_valve_command"]:
        if c in df:
            df[c] = df[c].where(df[c] >= 0)
    return df


def target_faults(df: pd.DataFrame) -> pd.Series:
    """True where the 5-min chilled-water reading is a meter fault, using only
    readings at the same timestamp (or earlier)."""
    y = df[TARGET]
    fan = df.get("ahu_fan_speed", pd.Series(np.nan, index=df.index))
    vlv = df.get("cooling_coil_valve_command", pd.Series(np.nan, index=df.index))
    fan_on = fan > 5
    fan_off_now_and_before = (fan <= 5) & (fan.shift(1) <= 5)
    # meter reads 0 although the AHU runs with the chilled-water valve open
    dropout = (y == 0) & fan_on & (vlv > 5)
    # meter stuck at a non-zero value while the AHU is off (2021-11-03 18:40 to 11-04 10:00)
    stuck_off = (y > 0) & fan_off_now_and_before
    # catch-up dump after a dropout (5-min value far above anything physical for this coil)
    dump = y > 6.0
    return dropout | stuck_off | dump


def to_15min(df: pd.DataFrame, mask_target_faults: bool = True) -> pd.DataFrame:
    """15-min table labelled by interval start. Energy columns are summed (NaN unless
    all three 5-min readings are valid), state columns are averaged."""
    df = df.copy()
    if mask_target_faults:
        df.loc[target_faults(df), TARGET] = np.nan
    energy = [c for c in df.columns if c.endswith("_energy")]
    other = [c for c in df.columns if c not in energy]
    g = df.resample("15min", label="left", closed="left")
    e = g[energy].sum(min_count=3)
    n = g[energy].count()
    e = e.where(n == 3)
    o = g[other].mean()
    out = pd.concat([e, o], axis=1)[list(df.columns)]
    # keep only intervals that have at least one raw row (no invented rows in the long gaps)
    has = g[df.columns[0]].size() > 0
    return out[has]


# Singapore public holidays (incl. days in lieu), 2021-2023. Known in advance.
SG_HOLIDAYS = pd.to_datetime([
    "2021-01-01", "2021-02-12", "2021-02-13", "2021-04-02", "2021-05-01", "2021-05-13", "2021-05-26",
    "2021-07-20", "2021-08-09", "2021-11-04", "2021-12-25",
    "2022-01-01", "2022-02-01", "2022-02-02", "2022-04-15", "2022-05-01", "2022-05-02", "2022-05-03",
    "2022-05-15", "2022-05-16", "2022-07-10", "2022-07-11", "2022-08-09", "2022-10-24", "2022-12-25",
    "2022-12-26",
    "2023-01-01", "2023-01-02", "2023-01-22", "2023-01-23", "2023-01-24", "2023-04-07", "2023-04-22",
    "2023-05-01", "2023-06-02", "2023-06-29", "2023-08-09", "2023-09-01", "2023-11-12", "2023-11-13",
    "2023-12-25",
])


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derived columns on the 15-min table.

    Known ahead (calendar only): time of day in minutes, AHU schedule window, public holiday.
    Measured (bemlops lags them by the horizon, so only past values are used):
    the mean chilled-water energy of the last ~one operating day of normal operation,
    counted over valid intervals only so that weekend and data gaps are skipped.
    """
    df = df.copy()
    idx = df.index
    tod = idx.hour * 60 + idx.minute
    df["tod_min"] = tod.astype(float)
    df["sched_window"] = ((tod >= 8 * 60) & (tod < 18 * 60 + 45)).astype(float)
    df["holiday"] = idx.normalize().isin(SG_HOLIDAYS).astype(float)
    y = df[TARGET]
    core = (tod >= 8 * 60 + 15) & (tod < 18 * 60)  # inside the operating window, no transitions
    v = y.where(core & (y > 0.5)).dropna()
    lvl = v.rolling(39, min_periods=10).mean()  # ~one operating day of valid intervals
    df["cw_level_prev"] = lvl.reindex(idx).ffill()
    return df


def load(csv_path: str, mask_target_faults: bool = True) -> pd.DataFrame:
    return add_features(to_15min(clean(read_raw(csv_path)), mask_target_faults=mask_target_faults))


# Column declarations for bemlops (every used column, with quantity and unit).
COLUMNS = {
    TARGET: "energy [kWh]",
    "ahu_fan_speed": "other",                                   # Hz
    "cooling_coil_valve_command": "position [%]",
    "cooling_coil_valve_position": "position [%]",
    "offcoil_air_temp": "supply_air_temperature [degC]",        # air leaving the cooling coil
    "supply_air_temperature": "supply_air_temperature [degC]",
    "air_temperature": "zone_air_temperature [degC]",           # after the degF fix in clean()
    "indoor_relative_humidity": "relative_humidity [%]",
    "indoor_co2": "co2 [ppm]",
    "occupant_count": "occupancy_count [count]",
    "wifi_connected_devices": "other",                          # occupancy proxy (count)
    "dry_bulb_temp": "outdoor_air_temperature [degC]",
    "outdoor_relative_humidity": "relative_humidity [%]",
    "global_horizontal_solar_radiation": "solar_irradiance [W/m2]",
    "ahu_fan_energy": "energy [kWh]",
    "lighting_energy": "energy [kWh]",
    "plug_load_energy": "energy [kWh]",
    "tod_min": {"quantity": "other", "known_ahead": True},       # calendar
    "sched_window": {"quantity": "other", "known_ahead": True},  # calendar
    "holiday": {"quantity": "other", "known_ahead": True},       # public-holiday calendar
    "cw_level_prev": "other",                                    # measured -> lagged by bemlops
}

# Stuck and spike masking look at later readings to judge a reading, so they are off
# (faults are handled row-wise in clean()/target_faults() instead).
PREPARE_OPTIONS = dict(mask_stuck=False, mask_spikes=False)


# --------------------------------------------------------------------------
# Forecast
# --------------------------------------------------------------------------

_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        import bemlops
        _MODEL = bemlops.load_model(HERE / "model.joblib")
        # single-threaded prediction: the multi-threaded random forest adds the trees up in a
        # varying order, which makes repeated forecasts differ by ~1e-15
        try:
            _MODEL.estimator.set_params(model__n_jobs=1)
        except Exception:
            pass
    return _MODEL


def _fallback(index: pd.DatetimeIndex) -> pd.Series:
    prof = pd.read_json(HERE / "fallback_profile.json", typ="series")
    prof.index = prof.index.astype(int)
    tod = index.hour * 60 + index.minute
    return pd.Series(np.asarray(prof.reindex(tod).fillna(0.0)), index=index)


def predict(csv_path: str) -> pd.Series:
    """One forecast (kWh in the 15-min interval) per 15-min interval start, from the first interval
    in the file to the last. The forecast for T uses only data with timestamps < T - 45 min."""
    df15 = to_15min(clean(read_raw(csv_path)))
    # every 15-min interval from the first one in the file to one hour after the last one
    # (the last four are true forecasts beyond the data; they use only data in the file)
    grid = pd.date_range(df15.index.min(), df15.index.max() + pd.Timedelta("1h"), freq="15min",
                         name="timestamp")
    # add the four future intervals so that the known-ahead calendar inputs exist for them
    df = add_features(df15.reindex(df15.index.union(grid[grid > df15.index.max()])))
    out = None
    try:
        m = _model()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # validate=True re-runs the training-time checks on the live data; problems are
            # reported (stderr) but do not stop the forecast.
            fc = m.predict(df[list(COLUMNS)], future=False, validate=True, on_error="warn")
        rep = getattr(m, "last_check_", None)
        if rep is not None and not rep.ok:
            print(f"[model.predict] bemlops data check reported errors in the live data:\n{rep}",
                  file=sys.stderr)
        col = "predicted" if "predicted" in fc.columns else fc.columns[0]
        out = fc[col].astype(float).reindex(grid)
    except Exception as exc:  # never return nothing: fall back to the time-of-day profile
        print(f"[model.predict] bemlops model failed ({exc!r}); using the fallback profile",
              file=sys.stderr)
        out = pd.Series(np.nan, index=grid)
    fb = _fallback(grid)
    out = out.fillna(fb).clip(lower=0.0).round(6)
    out.name = TARGET
    return out
