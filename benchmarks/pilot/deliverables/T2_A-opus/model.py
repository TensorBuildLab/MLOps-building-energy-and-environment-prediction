"""1-hour-ahead forecast of 15-minute chilled-water energy (kWh) for the library AHU.

predict(csv_path) -> pandas.Series indexed by 15-minute interval start (local time, UTC+08:00).

Causality: the forecast for the interval starting at T is built only from rows whose
timestamp is < T - 45 min (i.e. up to and including the 5-minute row at T - 50 min).
Every cleaning step applied to the inputs is strictly row-wise or backward-looking,
features are produced by shifting a regular grid backwards, and nothing is computed
from global statistics of the input file.
"""
import os
import datetime as _dt

import numpy as np
import pandas as pd
import joblib

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(HERE, "chw_model.joblib")

LOCAL_TZ = _dt.timezone(_dt.timedelta(hours=8))
STEP = pd.Timedelta("5min")
BLOCK = pd.Timedelta("15min")
LEAD = pd.Timedelta("45min")          # forecast for T may use rows with ts < T - 45 min
LAG_ROWS = 10                         # T - 50 min = 10 rows of 5 min before T
LAG_BLOCKS = 4                        # block [T-60, T-45) = 4 blocks of 15 min before T

TARGET = "chilled_water_energy"

# Singapore public holidays that fall on weekdays (observed dates), 2021-2023.
SG_HOLIDAYS = {
    "2021-01-01", "2021-02-12", "2021-04-02", "2021-05-13", "2021-05-26", "2021-07-20",
    "2021-08-09", "2021-11-04",
    "2022-01-31", "2022-02-01", "2022-02-02", "2022-04-15", "2022-05-02", "2022-05-03",
    "2022-05-16", "2022-07-11", "2022-08-09", "2022-10-24", "2022-12-26",
    "2023-01-02", "2023-01-23", "2023-01-24", "2023-04-07", "2023-05-01", "2023-06-02",
    "2023-06-29", "2023-08-09", "2023-11-13", "2023-12-25",
}
SG_HOLIDAYS.discard("2022-01-31")  # CNY eve is not a public holiday
# AHU schedule observed in the trend data (minutes after midnight of the first / last
# 5-minute row with the fan running): 08:05-18:40 on working days, 10:05-17:40 on the
# one public holiday in the data (Deepavali, 2021-11-04).
SCHED_NORMAL = (8 * 60 + 5, 18 * 60 + 40)
SCHED_HOLIDAY = (10 * 60 + 5, 17 * 60 + 40)

TEMP_COLS = ["air_temperature", "offcoil_air_temp", "supply_air_temperature", "dry_bulb_temp"]


# ----------------------------------------------------------------------------- loading
def _short(c):
    return str(c).split(" [")[0].strip()


def _parse_ts(s):
    s = s.astype(str).str.strip()
    has_off = s.str.contains(r"(?:[+-]\d{2}:?\d{2}|Z)$", regex=True)
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for mask, utc in ((has_off, True), (~has_off, False)):
        if not mask.any():
            continue
        sub = s[mask]
        fmt = "%Y-%m-%d %H:%M %z" if utc else "%Y-%m-%d %H:%M"
        t = pd.to_datetime(sub, errors="coerce", utc=utc, format=fmt)
        bad = t.isna()
        if bad.any():   # slow path for any other spelling
            t[bad] = pd.to_datetime(sub[bad], errors="coerce", utc=utc, format="mixed")
        if utc:   # convert to the building's local time (UTC+08:00), then drop tz
            t = (t + pd.Timedelta(hours=8)).dt.tz_localize(None)
        out.loc[mask] = t.astype("datetime64[ns]").values
    return out


def load_raw(csv_path):
    """Read the trend export: parse local timestamps, coerce numerics, sort, de-duplicate."""
    raw = pd.read_csv(csv_path, dtype=str)
    ts_col = "timestamp" if "timestamp" in raw.columns else raw.columns[0]
    ts = _parse_ts(raw[ts_col])
    df = raw.drop(columns=[ts_col])
    df.columns = [_short(c) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce")       # 'OFFLINE' etc. -> NaN
    df.index = ts.values
    df = df[~pd.isna(df.index)]
    df.index = pd.DatetimeIndex(df.index).floor("min")
    df = df.iloc[np.argsort(df.index.values, kind="mergesort")]
    df = df[~df.index.duplicated(keep="first")]
    return df


def _causal_spike_filter(x, window=12, k=6.0, floor=3.0):
    """NaN out values far from the median of the previous `window` rows (row t uses rows < t)."""
    med = x.shift(1).rolling(window, min_periods=3).median()
    mad = (x.shift(1) - med).abs().rolling(window, min_periods=3).median()
    thr = np.maximum(k * 1.4826 * mad.fillna(0.0), floor)
    bad = (x - med).abs() > thr
    return x.mask(bad & med.notna())


def clean_rows(df):
    """Row-wise / backward-looking cleaning of the 5-minute data (safe for forecasting)."""
    df = df.copy()
    df = df.mask(df <= -900)                              # -999 style sentinels
    for c in TEMP_COLS:
        if c in df:
            x = df[c]
            x = x.where(x <= 50, (x - 32.0) * 5.0 / 9.0)  # Fahrenheit rows -> Celsius
            df[c] = x
    for c in ["dry_bulb_temp", "air_temperature"]:
        if c in df:
            df[c] = _causal_spike_filter(df[c])
    for c in ["outdoor_relative_humidity", "indoor_relative_humidity", "supply_air_humidity"]:
        if c in df:
            df[c] = df[c].where((df[c] >= 0) & (df[c] <= 100))
    for c in df.columns:
        if c.endswith("_energy"):
            df[c] = df[c].where(df[c] >= 0)
    return df


def to_grid(df, start, end):
    idx = pd.date_range(start, end, freq=STEP)
    return df.reindex(idx)


def clean_chw_causal(g):
    """Chilled-water reading cleaned using only the current and earlier rows."""
    y = g[TARGET].copy()
    valve = g.get("cooling_coil_valve_command")
    fan = g.get("ahu_fan_speed")
    # meter "catch-up" pulses after communication loss (>> physical max ~6 kWh / 5 min)
    y = y.where(~(y > 7.0))
    # frozen value: same non-zero reading as the two previous rows
    frozen = (y > 0) & (y == y.shift(1)) & (y == y.shift(2))
    # valve shut for >= 10 min and fan off -> no chilled water can flow
    if valve is not None and fan is not None:
        shut = (valve.fillna(0) < 1) & (valve.shift(1).fillna(0) < 1) & (fan.fillna(0) < 1)
        y = y.mask(shut & y.notna(), 0.0)
        y = y.mask(shut & y.isna() & valve.notna(), 0.0)
        frozen = frozen & ~shut
    y = y.mask(frozen)
    return y


# ----------------------------------------------------------------------------- features
def _sched(dates_str, tod):
    hol = np.isin(dates_str, list(SG_HOLIDAYS))
    s0 = np.where(hol, SCHED_HOLIDAY[0], SCHED_NORMAL[0])
    s1 = np.where(hol, SCHED_HOLIDAY[1], SCHED_NORMAL[1])
    return hol, s0, s1


def build_features(g):
    """g: regular 5-minute grid (cleaned).  Returns features indexed by 15-min interval start T.

    All features for T are derived from rows with timestamp <= T - 50 min.
    """
    out_idx = g.index[(g.index.minute % 15) == 0]
    out_idx = out_idx[out_idx >= g.index[0]]
    F = pd.DataFrame(index=out_idx)

    chw = clean_chw_causal(g)
    fan = g["ahu_fan_speed"]
    valve = g["cooling_coil_valve_command"]
    on_row = (fan > 5) & (valve > 10)

    # --- meter health (as of each row, from on-rows up to that row)
    on_valid = on_row & chw.notna()
    zr = (chw[on_valid] < 0.05).astype(float)
    if len(zr):
        grp = (zr == 0).cumsum()
        streak = zr.groupby(grp.values).cumsum()
        frac_nz = 1.0 - zr.rolling(24, min_periods=1).mean()
        streak_g = streak.reindex(g.index).ffill().fillna(0.0)
        last_on = pd.Series(zr.index, index=zr.index).reindex(g.index).ffill()
        frac_g = frac_nz.reindex(g.index).ffill().fillna(1.0)
    else:
        streak_g = pd.Series(0.0, index=g.index)
        frac_g = pd.Series(1.0, index=g.index)
        last_on = pd.Series(pd.NaT, index=g.index, dtype="datetime64[ns]")
    healthy_chw = chw.where(~(on_row & (streak_g >= 3)))   # drop readings inside a dead-meter run

    # --- 15-minute block aggregates (block start S covers rows S, S+5, S+10)
    blk = lambda s, how="mean": getattr(s.resample(BLOCK, origin=out_idx[0]), how)()
    B = pd.DataFrame(index=out_idx)
    B["chw"] = (blk(chw) * 3).reindex(out_idx)
    B["chw_h"] = (blk(healthy_chw) * 3).reindex(out_idx)
    B["valve"] = blk(valve).reindex(out_idx)
    B["fan"] = blk(fan).reindex(out_idx)
    extra = {"valve_pos": "cooling_coil_valve_position", "sat": "supply_air_temperature",
             "filter_dp": "pressure_across_filter", "sa_press": "supply_air_pressure"}
    for k, c in extra.items():
        if c in g:
            B[k] = blk(g[c]).reindex(out_idx)
    for c in ["air_temperature", "indoor_relative_humidity", "indoor_co2", "occupant_count",
              "wifi_connected_devices", "dry_bulb_temp", "outdoor_relative_humidity",
              "global_horizontal_solar_radiation", "offcoil_air_temp", "lighting_energy",
              "plug_load_energy"]:
        if c in g:
            B[c] = blk(g[c]).reindex(out_idx)

    def lagb(col, k):  # value of block (T - 45 - 15k)
        return B[col].shift(LAG_BLOCKS + k - 1)

    for k in (1, 2, 3, 4, 8):
        F[f"chw_l{k}"] = lagb("chw", k)
    F["chw_h_l1"] = lagb("chw_h", 1)
    F["chw_h_mean4"] = pd.concat([lagb("chw_h", k) for k in (1, 2, 3, 4)], axis=1).mean(axis=1)
    F["valve_l1"] = lagb("valve", 1)
    F["valve_l2"] = lagb("valve", 2)
    F["fan_l1"] = lagb("fan", 1)
    for k in ("valve_pos", "sat", "filter_dp", "sa_press"):
        if k in B:
            F[k + "_l1"] = lagb(k, 1)
    for c in ["air_temperature", "indoor_relative_humidity", "indoor_co2", "occupant_count",
              "wifi_connected_devices", "dry_bulb_temp", "outdoor_relative_humidity",
              "global_horizontal_solar_radiation", "offcoil_air_temp", "lighting_energy",
              "plug_load_energy"]:
        if c in B:
            F[c] = lagb(c, 1).ffill(limit=2)
    F["dry_bulb_trend"] = F["dry_bulb_temp"] - lagb("dry_bulb_temp", 4)

    # --- last row (T - 50 min) states
    def lastrow(s, limit=6):
        if limit:
            s = s.ffill(limit=limit)
        return s.shift(LAG_ROWS).reindex(out_idx)

    F["chw_last"] = lastrow(chw, limit=1)
    F["fan_last"] = lastrow(fan)
    F["valve_last"] = lastrow(valve)
    F["on_last"] = lastrow(on_row.astype(float).where(fan.notna()))
    F["zero_streak"] = streak_g.shift(LAG_ROWS).reindex(out_idx).fillna(0.0)
    F["meter_frac_nz"] = frac_g.shift(LAG_ROWS).reindex(out_idx).fillna(1.0)
    lo = pd.DatetimeIndex(last_on.shift(LAG_ROWS).reindex(out_idx))
    F["on_age_h"] = ((out_idx - LAG_ROWS * STEP) - lo).total_seconds().values / 3600.0

    # --- actual start today (from rows <= T-50)
    day = g.index.normalize()
    on_f = on_row.astype(float)
    started = on_f.groupby(day).cummax()
    is_first = (started > 0) & (started.groupby(day).shift(1).fillna(0) == 0)
    first_on = pd.Series(pd.NaT, index=g.index, dtype="datetime64[ns]")
    first_on[is_first.values] = g.index[is_first.values]
    first_on = first_on.groupby(day).ffill()
    started_T = started.shift(LAG_ROWS).reindex(out_idx)
    same_day = (out_idx - LAG_ROWS * STEP).normalize() == out_idx.normalize()
    F["started_today"] = np.where(same_day, started_T.fillna(0.0), 0.0)
    fo = pd.to_datetime(first_on.shift(LAG_ROWS).reindex(out_idx))
    mins_since = (out_idx - pd.DatetimeIndex(fo)).total_seconds() / 60.0
    F["mins_since_start"] = np.where(same_day & (F["started_today"] > 0), mins_since, -1.0)

    # --- previous operating day (fully before T - 45)
    blk_date = out_idx.normalize()
    tod = (out_idx.hour * 60 + out_idx.minute).values
    Bh = pd.DataFrame({"chw": B["chw_h"].values, "date": blk_date, "tod": tod}, index=out_idx)
    piv = Bh.pivot_table(index="date", columns="tod", values="chw", aggfunc="mean")
    on_cols = [c for c in piv.columns if 9 * 60 <= c < 18 * 60]
    day_level = piv[on_cols].mean(axis=1)
    day_level = day_level[piv[on_cols].notna().sum(axis=1) >= 12]
    day_level = day_level[day_level > 1.0]                 # skip off / dead-meter days
    dates_all = pd.DatetimeIndex(np.unique(blk_date))
    prev_level = pd.Series(day_level.values, index=day_level.index).reindex(dates_all)
    prev_level = prev_level.shift(1).ffill()               # last valid day strictly before
    F["prev_day_level"] = prev_level.reindex(blk_date).values
    # same interval on the previous date that had data
    piv_valid = piv.dropna(how="all").reindex(columns=np.arange(0, 1440, 15))
    pv = piv_valid.to_numpy(dtype=float)
    pos = np.searchsorted(piv_valid.index.values, blk_date.values, side="left") - 1
    col = (tod // 15).astype(int)
    prev_same = np.full(len(tod), np.nan)
    ok = pos >= 0
    if len(pv):
        prev_same[ok] = pv[pos[ok], col[ok]]
    F["prev_day_same"] = prev_same

    # --- calendar / schedule
    dstr = blk_date.strftime("%Y-%m-%d").values
    hol, s0, s1 = _sched(dstr, tod)
    F["holiday"] = hol.astype(float)
    F["rel_start"] = tod - s0
    F["rel_end"] = s1 - tod
    # fraction of the interval's 3 rows inside the cooling window [start, stop-10min]
    fr = np.zeros(len(tod))
    for k in range(3):
        m = tod + 5 * k
        fr += ((m >= s0) & (m <= s1 - 10)).astype(float)
    F["sched_frac"] = fr / 3.0
    F["dow"] = out_idx.dayofweek.values.astype(float)
    return F


FEATURES = [
    "chw_l1", "chw_l2", "chw_l3", "chw_l4", "chw_l8", "chw_h_l1", "chw_h_mean4",
    "valve_l1", "valve_l2", "fan_l1",
    "air_temperature", "indoor_relative_humidity", "indoor_co2", "occupant_count",
    "wifi_connected_devices", "dry_bulb_temp", "outdoor_relative_humidity",
    "global_horizontal_solar_radiation", "offcoil_air_temp", "lighting_energy", "plug_load_energy",
    "dry_bulb_trend", "chw_last", "fan_last", "valve_last", "on_last",
    "zero_streak", "meter_frac_nz", "started_today", "mins_since_start",
    "valve_pos_l1", "sat_l1", "filter_dp_l1", "sa_press_l1",
    "prev_day_level", "prev_day_same", "holiday", "rel_start", "rel_end", "sched_frac",
]


def prepare(csv_path):
    """Load + clean + grid + features. Returns (grid, features)."""
    df = clean_rows(load_raw(csv_path))
    first = df.index.min().floor("15min")
    last = df.index.max()
    t_max = (last + pd.Timedelta("50min")).floor("15min")   # last T whose inputs end at `last`
    g = to_grid(df, first, t_max + BLOCK - STEP)
    F = build_features(g)
    F = F[F.index <= t_max]
    return g, F


# ----------------------------------------------------------------------------- predict
def trees_predict(ens, X):
    """Evaluate exported gradient-boosted trees (numpy only, same rules as sklearn HGB)."""
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    out = np.full(n, float(ens["baseline"]))
    rows = np.arange(n)
    for t in ens["trees"]:
        feat, thr, mleft = t["feature"], t["threshold"], t["missing_left"]
        left, right, leaf, val = t["left"], t["right"], t["is_leaf"], t["value"]
        node = np.zeros(n, dtype=np.int64)
        for _ in range(64):
            active = ~leaf[node]
            if not active.any():
                break
            nd = node[active]
            x = X[rows[active], feat[nd]]
            go_left = np.where(np.isnan(x), mleft[nd], x <= thr[nd])
            node[active] = np.where(go_left, left[nd], right[nd])
        out += val[node]
    return out


def model_predict(art, X):
    m = art["model"]
    if isinstance(m, dict) and m.get("kind") == "trees":
        return trees_predict(m, X)
    if isinstance(m, dict) and m.get("kind") == "ensemble":
        return np.mean([model_predict({"model": s}, X) for s in m["members"]], axis=0)
    return np.asarray(m.predict(X), dtype=float)


def apply_model(art, F):
    cols = art["features"]
    X = F.reindex(columns=cols).astype(float).to_numpy()
    p = model_predict(art, X)
    p = np.clip(p, 0.0, art.get("clip_max", 20.0))
    # outside the AHU schedule window chilled water is ~0 unless the AHU is actually running
    off = (F["sched_frac"].values == 0) & ~(F["on_last"].fillna(0).values > 0)
    p = np.where(off, np.minimum(p, art.get("off_cap", 0.3)), p)
    # AHU did not start at its scheduled time (weekend / closure / unlisted holiday) -> stays off
    not_started = ((F["rel_start"].values >= 60) & (F["started_today"].values == 0)
                   & ~(F["on_last"].fillna(0).values > 0))
    p = np.where(not_started, np.minimum(p, art.get("off_cap", 0.3)), p)
    # dead meter (AHU running but meter reading zero for a sustained period) -> meter keeps reading 0
    zs = art.get("dead_meter_streak", None)
    if zs is not None:
        recent = F["on_age_h"].fillna(1e9).values <= art.get("dead_meter_max_age_h", 72.0)
        p = np.where((F["zero_streak"].values >= zs) & recent, 0.0, p)
    return pd.Series(p, index=F.index)


def predict(csv_path: str) -> pd.Series:
    art = joblib.load(MODEL_FILE)
    _, F = prepare(csv_path)
    p = apply_model(art, F)
    p = p.fillna(0.0)
    p.index = pd.DatetimeIndex(p.index).tz_localize(LOCAL_TZ)
    p.index.name = "timestamp"
    p.name = "chilled_water_energy_kWh_forecast"
    return p
