"""
1-hour-ahead forecast of the 15-minute mean of RoomB:Sensor__CO2 (ppm).

predict(csv_path) -> pandas.Series indexed by the 15-min interval start time
(tz-aware DatetimeIndex, Europe/Copenhagen, i.e. the building's local time).

Causality: the forecast for the interval starting at T is built only from rows whose
timestamp is < T - 45 min.  Concretely, every input feature is first aggregated to
15-min intervals (label = interval start) and then shifted by 4 intervals, so the most
recent information used for T is the interval [T-60, T-45).  All cleaning steps are
row-wise or backward-looking (ffill / trailing windows only); nothing is interpolated,
back-filled, centred or normalised with statistics of the input file.
"""
import os
import numpy as np
import pandas as pd
import joblib

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "co2_model.joblib")
LOCAL_TZ = "Europe/Copenhagen"
STEP = pd.Timedelta("15min")
H = 4  # horizon in 15-min steps: data of interval T-60min is the newest allowed for T

# substring -> short name (matched against the raw header, robust to encoding of "façade")
COLMAP = [
    ("Sensor__CO2", "co2"),
    ("Sensor__room_temperature", "troom"),
    ("People__amount", "ppl"),
    ("Room__active", "act"),
    ("Damper__position", "damp"),
    ("Radiator__control_signal", "rad"),
    ("Light__level__ceiling", "lux"),
    ("Light__on_off_signal", "light"),
    ("Window__opened_closed", "win"),
    ("Fan__air_flow__supply", "fan"),
    ("Sensor__air_temperature__supply", "tsup"),
    ("EL_meter__power", "elvent"),
    ("Outdoor:Temperature_air", "tout"),
    ("Wind__velocity", "wind"),
    ("radiation__south", "sol_s"),
    ("radiation__east", "sol_e"),
    ("radiation__west", "sol_w"),
]


# ----------------------------------------------------------------------------------------
# loading / cleaning (row-wise, causal)
# ----------------------------------------------------------------------------------------
def _to_num(s):
    if s.dtype == object or pd.api.types.is_string_dtype(s):
        s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def load_clean(csv_path):
    raw = pd.read_csv(csv_path, sep=";", dtype=str, encoding="utf-8-sig",
                      encoding_errors="replace", keep_default_na=False)
    tcol = [c for c in raw.columns if "timestamp" in c.lower()]
    tcol = tcol[0] if tcol else raw.columns[0]
    ts = pd.to_datetime(raw[tcol], utc=True, errors="coerce", format="%Y-%m-%dT%H:%M:%S%z")
    bad = ts.isna()
    if bad.any():  # fall back to a generic parser for odd rows
        ts[bad] = pd.to_datetime(raw.loc[bad, tcol], utc=True, errors="coerce", format="mixed")
    out = pd.DataFrame(index=raw.index)
    for key, name in COLMAP:
        cols = [c for c in raw.columns if key in c]
        out[name] = _to_num(raw[cols[0]]) if cols else np.nan
    out["t"] = ts
    out = out[out["t"].notna()]
    # duplicated export blocks / out-of-order rows: keep first occurrence, sort by time
    out = out.drop_duplicates("t", keep="first").sort_values("t").set_index("t")
    # snap to the 5-min grid (rows are 5-min samples)
    out.index = out.index.floor("5min")
    out = out[~out.index.duplicated(keep="first")]

    # --- physical-range cleaning (row-wise only) ---
    c = out["co2"]
    out["co2"] = c.where((c >= 250) & (c <= 5000))           # -999 sentinels etc.
    tr = out["troom"]
    tr = tr.where(tr < 45, (tr - 32.0) * 5.0 / 9.0)           # unit switch to deg F (2023-05-12)
    out["troom"] = tr.where((tr > 5) & (tr < 40))
    to = out["tout"]
    out["tout"] = to.where((to > -35) & (to < 40))           # isolated 57-73 degC spikes
    for k in ("act", "light", "win"):
        v = out[k]
        out[k] = v.where((v >= 0) & (v <= 1))
    for k in ("damp", "rad"):
        v = out[k]
        out[k] = v.where((v >= 0) & (v <= 100))
    v = out["ppl"]
    out["ppl"] = v.where((v >= 0) & (v <= 50))
    v = out["fan"]
    out["fan"] = v.where((v >= 0) & (v < 50000))
    for k in ("lux", "sol_s", "sol_e", "sol_w", "wind", "elvent"):
        v = out[k]
        out[k] = v.where(v >= 0)
    return out


def causal_despike(c, jump=300.0):
    """Remove single-sample CO2 spikes using past samples only.

    A sample that departs by more than `jump` ppm from the previous accepted value is
    rejected unless it is confirmed by the following accepted level -- but confirmation
    would need the future, so instead we accept a new level only once two consecutive
    samples agree with each other (the first of them is then lost, which is harmless).
    """
    vals = c.to_numpy(dtype=float)
    out = np.full_like(vals, np.nan)
    last = np.nan
    pending = np.nan
    for i, x in enumerate(vals):
        if np.isnan(x):
            continue
        if np.isnan(last) or abs(x - last) <= jump:
            out[i] = x
            last = x
            pending = np.nan
        elif not np.isnan(pending) and abs(x - pending) <= 60:
            out[i] = x  # level shift confirmed by two consecutive samples
            last = x
            pending = np.nan
        else:
            pending = x
    return pd.Series(out, index=c.index)


# ----------------------------------------------------------------------------------------
# calendar
# ----------------------------------------------------------------------------------------
def _easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return pd.Timestamp(y, month, day)


def danish_holidays(years):
    days = set()
    for y in years:
        e = _easter(y)
        for off in (-3, -2, 0, 1, 39, 49, 50):
            days.add((e + pd.Timedelta(days=off)).date())
        if y <= 2023:
            days.add((e + pd.Timedelta(days=26)).date())  # Store Bededag (abolished 2024)
        for md in ((1, 1), (6, 5), (12, 24), (12, 25), (12, 26), (12, 31)):
            days.add(pd.Timestamp(y, *md).date())
    return days


# ----------------------------------------------------------------------------------------
# features
# ----------------------------------------------------------------------------------------
def build_frame(d, grid_end=None):
    """15-min aggregates on a UTC grid; returns (grid index, aggregated frame)."""
    start = d.index.min().floor("15min")
    last = d.index.max().floor("15min")
    end = last + H * STEP if grid_end is None else grid_end
    grid = pd.date_range(start, end, freq="15min", tz="UTC")
    co2 = causal_despike(d["co2"])
    g = co2.resample("15min")
    a = pd.DataFrame({
        "c_mean": g.mean(), "c_med": g.median(), "c_last": g.last(),
        "c_max": g.max(), "c_min": g.min(), "c_n": g.count(),
    })
    other = d.drop(columns=["co2"]).resample("15min").mean()
    other["fan_on"] = (d["fan"] > 1000).astype(float).where(d["fan"].notna()).resample("15min").mean()
    a = a.join(other, how="outer").reindex(grid)
    return grid, a


def make_features(d, grid_end=None):
    grid, a = build_frame(d, grid_end)
    F = pd.DataFrame(index=grid)

    # persistence base: last valid interval value, carried forward (causal)
    cm = a["c_mean"]
    cf = cm.ffill()
    obs_pos = pd.Series(np.where(cm.notna(), np.arange(len(cm)), np.nan), index=grid).ffill()
    age = pd.Series(np.arange(len(cm)), index=grid) - obs_pos

    s = lambda x, k=H: x.shift(k)      # value of interval T - k*15min
    F["c0"] = s(cf)                     # mean of interval [T-60, T-45)
    F["c0_med"] = s(a["c_med"])
    F["c0_last"] = s(a["c_last"].ffill())
    F["c0_max"] = s(a["c_max"])
    F["c0_min"] = s(a["c_min"])
    F["c_age"] = s(age)
    for k in (1, 2, 3, 4, 8, 12, 24):
        F[f"d{k}"] = F["c0"] - s(cf, H + k)
    F["roll4h_max"] = s(cf.rolling(16, min_periods=1).max())
    F["roll4h_min"] = s(cf.rolling(16, min_periods=1).min())
    F["roll24h_min"] = s(cf.rolling(96, min_periods=1).min())
    F["roll24h_max"] = s(cf.rolling(96, min_periods=1).max())
    F["roll24h_mean"] = s(cf.rolling(96, min_periods=1).mean())
    F["c0_above_min24"] = F["c0"] - F["roll24h_min"]
    # same target interval yesterday / last week, and the change those days showed
    for name, lag in (("y1d", 96), ("y7d", 672)):
        F[f"{name}"] = s(cf, lag) - F["c0"]
        F[f"{name}_chg"] = s(cf, lag) - s(cf, lag + H)

    # other signals at the newest allowed interval
    for k in ("act", "light", "ppl", "damp", "win", "fan", "fan_on", "troom", "tsup",
              "tout", "sol_s", "lux", "rad"):
        F[k] = s(a[k])
    F["act_1h"] = s(a["act"].rolling(4, min_periods=1).mean())
    F["act_4h"] = s(a["act"].rolling(16, min_periods=1).mean())
    F["act_24h"] = s(a["act"].rolling(96, min_periods=1).mean())
    F["ppl_1h"] = s(a["ppl"].rolling(4, min_periods=1).mean())
    F["troom_d4"] = F["troom"] - s(a["troom"], H + 4)
    F["troom_d1"] = F["troom"] - s(a["troom"], H + 1)
    F["damp_d1"] = F["damp"] - s(a["damp"], H + 1)
    # what the schedules did at the target time one day / one week earlier
    for k in ("fan_on", "act"):
        F[f"{k}_1d"] = s(a[k], 96)
        F[f"{k}_7d"] = s(a[k], 672)
    F["fan_on_1d_prev"] = s(a["fan_on"], 96 + H)  # fan state yesterday at "now"
    F["act_1d_max"] = s(a["act"].rolling(9, min_periods=1).max(), 96 - 4)  # yesterday T-1h..T+1h

    # calendar of the target interval (known in advance)
    loc = grid.tz_convert(LOCAL_TZ)
    hol = danish_holidays(range(loc.year.min() - 1, loc.year.max() + 2))
    F["hour"] = loc.hour + loc.minute / 60.0
    F["dow"] = loc.day_of_week
    is_hol = pd.Index(loc.date).isin(list(hol))
    F["workday"] = ((loc.day_of_week < 5) & ~is_hol).astype(float)

    # how long CO2 has been flat (intervals since the last change > 5 ppm), at the base interval
    chg = cf.diff().abs() > 5
    last_chg = pd.Series(np.where(chg, np.arange(len(cf)), np.nan), index=grid).ffill()
    F["c_still"] = s((pd.Series(np.arange(len(cf)), index=grid) - last_chg).clip(upper=192))
    F["absd_2h"] = s(cf.diff().abs().rolling(8, min_periods=1).sum())

    # "same kind of day" analogues: most recent earlier day (1..7 days back) whose workday
    # flag equals that of the target day; values at the target time-of-day of that day.
    wd = F["workday"]
    fan_sd = pd.Series(np.nan, index=grid)
    act_sd = pd.Series(np.nan, index=grid)
    chg_sd = pd.Series(np.nan, index=grid)
    lvl_sd = pd.Series(np.nan, index=grid)
    for k in range(1, 8):
        lag = 96 * k
        m = fan_sd.isna() & (wd.shift(lag) == wd)
        fan_sd = fan_sd.where(~m, s(a["fan_on"], lag))
        act_sd = act_sd.where(~m, s(a["act"].rolling(3, min_periods=1).mean(), lag - 2))
        chg_sd = chg_sd.where(~m, s(cf, lag) - s(cf, lag + H))
        lvl_sd = lvl_sd.where(~m, s(cf, lag) - s(cf.rolling(96, min_periods=1).min(), lag + H))
    F["fan_sd"] = fan_sd                       # expected ventilation state at T
    F["fan_trans"] = fan_sd - F["fan_on"]      # expected switch between now and T
    F["act_sd"] = act_sd
    F["chg_sd"] = chg_sd
    F["lvl_sd"] = lvl_sd
    return F, a




def predict(csv_path: str) -> pd.Series:
    bundle = joblib.load(MODEL_PATH)
    d = load_clean(csv_path)
    F, _ = make_features(d)
    X = F[bundle["features"]]
    base = F["c0"]
    resid = np.zeros(len(F))
    for m in bundle["models"]:
        resid += m.predict(X) / len(bundle["models"])
    resid = np.clip(resid, -bundle["clip"], bundle["clip"])
    yhat = base.to_numpy() + resid
    # no CO2 history at all yet -> fall back to typical level
    yhat = np.where(np.isfinite(yhat), yhat, bundle["fallback"])
    yhat = np.clip(yhat, 300.0, 3000.0)
    idx = F.index.tz_convert(LOCAL_TZ)
    return pd.Series(yhat, index=idx, name="RoomB:Sensor__CO2_forecast")
