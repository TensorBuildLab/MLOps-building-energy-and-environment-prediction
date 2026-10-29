"""
Forecast of the 15-minute mean of RoomB:Sensor__CO2, 1 hour ahead.

predict(csv_path) -> pandas.Series indexed by interval start (tz-naive local time).

Causality contract
------------------
The forecast for the interval starting at T uses only 5-minute rows whose (UTC) timestamp is
<= T - 50 min (i.e. strictly before T - 45 min).  Every feature is computed at an "origin"
o = T - 50 min from trailing (backward-looking) windows / lags / forward-fill only.  No centred
windows, no interpolation, no back-fill and no statistic computed over the whole file is used,
so changing any row at or after T - 45 min cannot change the forecast for T.
Calendar features (hour, weekday, Danish public holidays) are known in advance.
All fixed constants (validity ranges, etc.) are physical limits, not estimated from the input file.
"""
import os
import datetime as _dt

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(HERE, "model.joblib")

NAMES = ['Tout', 'Wind', 'SolE', 'SolS', 'SolW', 'ElVent', 'Flow', 'TSup', 'DH', 'HC', 'CO2',
         'Troom', 'People', 'Active', 'Damper', 'Rad', 'LightLvl', 'LightOn', 'Window',
         'Tset', 'Hlim', 'Clim']

# physical validity limits (values outside -> missing).  -999 is a sentinel in the CO2 column.
VALID = {
    'CO2': (250.0, 6000.0),
    'Tout': (-45.0, 45.0),          # train data contain isolated 57-73 degC spikes
    'Wind': (0.0, 60.0),
    'SolE': (0.0, 1500.0), 'SolS': (0.0, 1500.0), 'SolW': (0.0, 1500.0),
    'Flow': (0.0, 40000.0),
    'ElVent': (0.0, 50000.0),
    'Damper': (0.0, 100.0),
    'LightLvl': (0.0, 5000.0),
}
BINARY = ['Active', 'Window', 'LightOn']

LEAD = pd.Timedelta(minutes=50)     # last usable 5-min row is T - 50 min
STEP5 = pd.Timedelta(minutes=5)
BIN = pd.Timedelta(minutes=15)


# --------------------------------------------------------------------------------------
# reading / cleaning
# --------------------------------------------------------------------------------------
def _read_raw(csv_path):
    last_err = None
    df = None
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(csv_path, sep=";", na_values=["#N/A"], dtype=str, encoding=enc)
            break
        except Exception as e:  # pragma: no cover
            last_err = e
    if df is None:
        raise last_err
    df.columns = [str(c).lstrip("﻿").lstrip("ï»¿") for c in df.columns]
    tcol = df.columns[0]
    ts = pd.to_datetime(df[tcol], format="%Y-%m-%dT%H:%M:%S%z", utc=True, errors="coerce")
    if ts.isna().mean() > 0.5:  # unexpected format: generic parser
        ts = pd.to_datetime(df[tcol], utc=True, errors="coerce")
    body = df.drop(columns=[tcol])
    if body.shape[1] == len(NAMES):
        body.columns = NAMES              # same layout as train.csv (match by position)
    else:                                  # fall back to matching by the column name tail
        ren = {}
        for c in body.columns:
            tail = c.split(":")[-1]
            for n, full in zip(NAMES, _FULL_TAILS):
                if tail == full:
                    ren[c] = n
        body = body.rename(columns=ren)
        for n in NAMES:
            if n not in body.columns:
                body[n] = np.nan
        body = body[NAMES]
    body = body.apply(pd.to_numeric, errors="coerce")
    body.index = ts
    body = body[body.index.notna()]
    # file may contain duplicated blocks / out-of-order blocks: keep first occurrence, sort in time
    body = body[~body.index.duplicated(keep="first")].sort_index()
    return body


_FULL_TAILS = ['Temperature_air', 'Wind__velocity', 'Solar__direct_radiation__east_façade',
               'Solar__direct_radiation__south_façade', 'Solar__direct_radiation__west_façade',
               'EL_meter__power', 'Fan__air_flow__supply', 'Sensor__air_temperature__supply',
               'DH__power', 'HC__power', 'Sensor__CO2', 'Sensor__room_temperature',
               'People__amount', 'Room__active', 'Damper__position',
               'Radiator__control_signal__motor_valve', 'Light__level__ceiling',
               'Light__on_off_signal', 'Window__opened_closed',
               'Control__setpoint_temperature_global', 'Control__heating_limit',
               'Control__cooling_limit']


def _clean(df):
    out = pd.DataFrame(index=df.index)
    for c in ['CO2', 'Tout', 'Wind', 'SolE', 'SolS', 'SolW', 'Flow', 'ElVent', 'Damper', 'LightLvl']:
        lo, hi = VALID[c]
        s = df[c]
        out[c] = s.where((s >= lo) & (s <= hi))
    for c in BINARY:
        s = df[c]
        out[c] = s.where(s.isin([0.0, 1.0]))
    return out


# --------------------------------------------------------------------------------------
# calendar
# --------------------------------------------------------------------------------------
def _easter(year):
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return _dt.date(year, month, day + 1)


_HOL_CACHE = {}


def _holidays(year):
    if year in _HOL_CACHE:
        return _HOL_CACHE[year]
    e = _easter(year)
    td = _dt.timedelta
    hs = {_dt.date(year, 1, 1), e - td(days=3), e - td(days=2), e, e + td(days=1),
          e + td(days=39), e + td(days=49), e + td(days=50),
          _dt.date(year, 12, 25), _dt.date(year, 12, 26), _dt.date(year, 6, 5),
          _dt.date(year, 12, 24), _dt.date(year, 12, 31)}
    if year <= 2023:
        hs.add(e + td(days=26))          # Great Prayer Day (abolished from 2024)
    _HOL_CACHE[year] = hs
    return hs


def _is_holiday(dates):
    out = np.zeros(len(dates), dtype=float)
    for i, d in enumerate(dates):
        out[i] = 1.0 if d in _holidays(d.year) else 0.0
    return out


def _last_sunday(year, month):
    d = _dt.date(year, month + 1, 1) - _dt.timedelta(days=1) if month < 12 else _dt.date(year, 12, 31)
    return d - _dt.timedelta(days=(d.weekday() + 1) % 7)


def _local_naive(utc_index):
    """UTC DatetimeIndex -> naive Copenhagen local time (EU DST rule, 01:00 UTC switch)."""
    idx = pd.DatetimeIndex(utc_index)
    if idx.tz is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)
    off = np.ones(len(idx), dtype="int64")
    for y in range(int(idx.year.min()), int(idx.year.max()) + 1):
        s = pd.Timestamp(_last_sunday(y, 3)) + pd.Timedelta(hours=1)
        e = pd.Timestamp(_last_sunday(y, 10)) + pd.Timedelta(hours=1)
        off[(idx >= s) & (idx < e)] = 2
    return idx + pd.to_timedelta(off, unit="h")


def _calendar(T_utc):
    loc = _local_naive(T_utc)
    cal = pd.DataFrame(index=T_utc)
    mod = (loc.hour * 60 + loc.minute).to_numpy()
    cal["tod"] = mod / 60.0
    cal["tod_sin"] = np.sin(2 * np.pi * mod / 1440.0)
    cal["tod_cos"] = np.cos(2 * np.pi * mod / 1440.0)
    dow = loc.dayofweek.to_numpy()
    cal["dow"] = dow
    dates = [d.date() for d in loc.normalize()]
    hol = _is_holiday(dates)
    prev = _is_holiday([d - _dt.timedelta(days=1) for d in dates])
    nxt = _is_holiday([d + _dt.timedelta(days=1) for d in dates])
    cal["hol"] = hol
    cal["hol_prev"] = prev
    cal["hol_next"] = nxt
    cal["workday"] = ((dow < 5) & (hol == 0)).astype(float)
    cal["prev_workday"] = (((dow - 1) % 7 < 5) & (prev == 0)).astype(float)
    return cal, loc


# --------------------------------------------------------------------------------------
# features
# --------------------------------------------------------------------------------------
def _grid5(clean):
    start = clean.index.min().floor("15min")
    end = clean.index.max()
    idx = pd.date_range(start, end, freq="5min", tz="UTC")
    return clean.reindex(idx)


def _age_steps(valid):
    """steps since the last True in `valid` (0 at a True), NaN before the first True."""
    pos = np.arange(len(valid), dtype=float)
    last = pd.Series(np.where(valid.to_numpy(), pos, np.nan), index=valid.index).ffill()
    return pos - last.to_numpy()


def _origin_features(g):
    """Features available at origin time o (use data with timestamp <= o only)."""
    F = pd.DataFrame(index=g.index)
    c = g["CO2"]
    cf = c.ffill(limit=36)                       # at most 3 h of carried-forward value
    F["co2"] = cf
    for k, nm in [(1, "5"), (2, "10"), (3, "15"), (6, "30"), (9, "45"), (12, "60"), (24, "120")]:
        F["co2_d" + nm] = cf - cf.shift(k)
    for w, nm in [(3, "15"), (6, "30"), (12, "60"), (24, "120"), (48, "240")]:
        F["co2_m" + nm] = cf.rolling(w, min_periods=max(1, w // 2)).mean()
    F["co2_std60"] = cf.rolling(12, min_periods=6).std()
    F["co2_max60"] = cf.rolling(12, min_periods=6).max()
    F["co2_min60"] = cf.rolling(12, min_periods=6).min()
    F["co2_max24h"] = cf.rolling(288, min_periods=144).max()
    F["co2_min24h"] = cf.rolling(288, min_periods=144).min()
    F["co2_mean24h"] = cf.rolling(288, min_periods=144).mean()
    base = cf.rolling(2016, min_periods=576).quantile(0.10)
    F["co2_base7d"] = base
    F["co2_rel"] = cf - base
    F["co2_rel_m60"] = F["co2_m60"] - base
    F["co2_max7d_rel"] = cf.rolling(2016, min_periods=576).max() - base
    age = _age_steps(c.notna())
    F["co2_age"] = np.minimum(age, 72.0) * 5.0
    chg = (c.diff().abs() > 0) | c.isna()
    F["co2_hold"] = np.minimum(_age_steps(chg | (~c.notna())), 288.0) * 5.0
    # status signals
    for nm, lim in [("Active", 12), ("Window", 12), ("LightOn", 12)]:
        s = g[nm].ffill(limit=lim)
        F[nm.lower()] = s
        F[nm.lower() + "_m60"] = s.rolling(12, min_periods=4).mean()
        F[nm.lower() + "_m240"] = s.rolling(48, min_periods=12).mean()
    F["active_max24h"] = g["Active"].ffill(limit=12).rolling(288, min_periods=100).max()
    F["active_mean24h"] = g["Active"].ffill(limit=12).rolling(288, min_periods=100).mean()
    F["active_age"] = np.minimum(_age_steps(g["Active"].fillna(0.0) > 0.5), 288.0) * 5.0
    dm = g["Damper"].ffill(limit=12)
    F["damper"] = dm
    F["damper_m30"] = dm.rolling(6, min_periods=3).mean()
    F["flow"] = g["Flow"].ffill(limit=12)
    F["flow_m60"] = F["flow"].rolling(12, min_periods=4).mean()
    ll = np.log1p(g["LightLvl"].ffill(limit=12))
    F["light"] = ll
    F["light_m60"] = ll.rolling(12, min_periods=4).mean()
    F["tout"] = g["Tout"].ffill(limit=24)
    F["tout_m24h"] = F["tout"].rolling(288, min_periods=100).mean()
    F["wind"] = g["Wind"].ffill(limit=24)
    F["sol"] = (g["SolE"] + g["SolS"] + g["SolW"]).ffill(limit=24)
    F["sol_m60"] = F["sol"].rolling(12, min_periods=4).mean()
    return F


def _bin_mean5(g):
    """Mean of the valid 5-min CO2 samples in [t, t+15 min) for every 5-min grid point t.
    Only ever used (a) as a training target and (b) lagged by >= 1 day as a feature."""
    c = g["CO2"]
    return c.rolling(3, min_periods=1).mean().shift(-2)


def _daily_features(B5, T_index):
    """Same-time-of-day features from previous days (all windows end long before T - 45 min)."""
    D = pd.DataFrame(index=T_index)
    day = pd.Timedelta(days=1)
    q = pd.Timedelta(minutes=15)

    def at(shift):
        return B5.reindex(T_index - shift).to_numpy()

    lags = {d: pd.Series(at(d * day), index=T_index) for d in range(1, 8)}
    D["B_d1"] = lags[1]
    D["B_d2"] = lags[2]
    D["B_d7"] = lags[7]
    stack = pd.concat([lags[d] for d in range(1, 6)], axis=1)
    D["B_dmean5"] = stack.mean(axis=1, skipna=True)
    D["B_dmax5"] = stack.max(axis=1, skipna=True)
    # what happened on previous days between the origin-equivalent window (T-60 min) and the target window
    ref = {d: pd.Series(at(d * day + 4 * q), index=T_index) for d in range(1, 8)}
    ch = [lags[d] - ref[d] for d in range(1, 6)]
    chs = pd.concat(ch, axis=1)
    D["dchg_mean5"] = chs.mean(axis=1, skipna=True)
    D["dchg_d1"] = ch[0]
    D["dchg_d7"] = lags[7] - ref[7]
    nb = pd.concat([pd.Series(at(day - q), index=T_index), lags[1], pd.Series(at(day + q), index=T_index)], axis=1)
    D["B_d1_nb"] = nb.mean(axis=1, skipna=True)
    return D


def feature_table(df_clean, step_minutes=15):
    """Returns (X, T_index_utc, y) where X is the design matrix for every interval start T
    (every `step_minutes`) from the first bin up to the last T whose origin (T - 50 min) is inside
    the data; y is the realised 15-min mean for T (NaN where unknown / beyond the data)."""
    g = _grid5(df_clean)
    F = _origin_features(g)
    B5 = _bin_mean5(g)
    last = g.index.max()
    T_start = g.index.min().floor("15min")
    T_end = (last + LEAD).floor("15min")
    T_index = pd.date_range(T_start, T_end, freq="%dmin" % step_minutes, tz="UTC")
    origin = T_index - LEAD
    X = F.reindex(origin)
    X.index = T_index
    X = X.join(_daily_features(B5, T_index))
    cal, _ = _calendar(T_index)
    X = X.join(cal)
    X["co2_x_work"] = X["co2_rel"] * X["workday"]
    y = pd.Series(B5.reindex(T_index).to_numpy(), index=T_index)
    return X, T_index, y


# --------------------------------------------------------------------------------------
# prediction
# --------------------------------------------------------------------------------------
_MODEL = None


def _load():
    global _MODEL
    if _MODEL is None:
        import joblib
        _MODEL = joblib.load(MODEL_FILE)
    return _MODEL


def predict_from_frame(raw, bundle=None):
    bundle = bundle or _load()
    clean = _clean(raw)
    X, T_index, y = feature_table(clean, 15)
    pred = predict_X(X, bundle)
    return pd.Series(pred, index=T_index, name="CO2_forecast"), y


def predict_X(X, bundle):
    feats = bundle["features"]
    Xf = X.reindex(columns=feats)
    base = _baseline(X)                       # persistence level the models correct
    out = np.full(len(Xf), np.nan)
    pr_full = np.zeros(len(Xf))
    w = bundle.get("weights") or [1.0 / len(bundle["models"])] * len(bundle["models"])
    for wi, m in zip(w, bundle["models"]):
        pr_full += wi * m.predict(Xf)
    pr_full = pr_full + (base.to_numpy() if bundle["residual"] else 0.0)
    have_recent = X["co2"].notna().to_numpy() & X["co2_m60"].notna().to_numpy()
    out[have_recent] = pr_full[have_recent]
    if (~have_recent).any():
        cf = bundle["fallback_features"]
        Xc = X.reindex(columns=cf)
        pc = bundle["fallback_model"].predict(Xc)
        out[~have_recent] = pc[~have_recent]
    lo, hi = bundle["clip"]
    return np.clip(out, lo, hi)


def _baseline(X):
    return X["co2_m15"].fillna(X["co2"])


def _to_local_unique(s_utc):
    loc = _local_naive(s_utc.index)
    s = pd.Series(s_utc.to_numpy(), index=pd.DatetimeIndex(loc, name="timestamp"), name=s_utc.name)
    s = s[~s.index.duplicated(keep="first")]
    return s


def predict(csv_path):
    """Forecast of the 15-min mean CO2 (ppm) for every 15-min interval start (tz-naive local time)
    from the first interval in the file up to the last interval whose forecast origin (T - 50 min)
    lies inside the file."""
    try:                                   # keep runtime predictable on a busy machine
        from threadpoolctl import threadpool_limits
        ctx = threadpool_limits(limits=2)
    except Exception:  # pragma: no cover
        ctx = None
    raw = _read_raw(csv_path)
    pred_utc, _ = predict_from_frame(raw)
    out = _to_local_unique(pred_utc)
    if ctx is not None:
        ctx.unregister()
    return out
