"""Feature construction shared by training (train_model.py) and serving (model.py).

All features for the forecast of the 15-min interval starting at T are computed from
15-min bins that END at or before T - 45 min, i.e. bins starting at T - 60 min or earlier
(lag >= 4 bins). Nothing centred, nothing back-filled, no interpolation.
"""
import numpy as np
import pandas as pd

LOCAL_TZ = "Europe/Copenhagen"
STEP = pd.Timedelta("15min")
H = 4  # horizon in 15-min bins (1 hour)

RAW_MAP = {
    "Outdoor:Temperature_air": "oat",
    "Outdoor:Wind__velocity": "wind",
    "Outdoor:Solar__direct_radiation__east_fa": "sol_e",
    "Outdoor:Solar__direct_radiation__south_fa": "sol_s",
    "Outdoor:Solar__direct_radiation__west_fa": "sol_w",
    "Ventilation:EL_meter__power": "vent_el",
    "Ventilation:Fan__air_flow__supply": "flow",
    "Ventilation:Sensor__air_temperature__supply": "sat",
    "Heating:DH__power": "dh",
    "Ventilation:HC__power": "hc",
    "RoomB:Sensor__CO2": "co2",
    "RoomB:Sensor__room_temperature": "rt",
    "RoomB:People__amount": "people",
    "RoomB:Room__active": "active",
    "RoomB:Damper__position": "damper",
    "RoomB:Radiator__control_signal__motor_valve": "rad",
    "RoomB:Light__level__ceiling": "lux",
    "RoomB:Light__on_off_signal": "light",
    "RoomB:Window__opened_closed": "window",
}


def _short_name(col):
    c = col.encode("ascii", "ignore").decode().strip()
    for k, v in RAW_MAP.items():
        if c == k or c.startswith(k):
            return v
    return None


def read_raw(csv_path):
    """Read the raw export into a numeric 5-min frame indexed by UTC time.

    Handles: BOM, ';' separator, '#N/A' and 'OFFLINE' text, UTC offsets in the timestamp
    (DST), out-of-order rows and exact duplicate blocks (re-logged days).
    """
    df = pd.read_csv(csv_path, sep=";", dtype=str, encoding="utf-8-sig")
    tcol = df.columns[0]
    ts = pd.to_datetime(df[tcol], utc=True, errors="coerce", format="ISO8601")
    keep = ts.notna().to_numpy()
    df = df.loc[keep].drop(columns=tcol)
    ts = ts[keep]
    out = {}
    for c in df.columns:
        n = _short_name(c)
        if n is not None:
            out[n] = pd.to_numeric(df[c], errors="coerce").to_numpy()
    out = pd.DataFrame(out, index=pd.DatetimeIndex(ts))
    out = out[~out.index.duplicated(keep="first")].sort_index()
    return out


def clean5(d):
    """Cleaning of the 5-min frame. Only rules that use the sample itself (no look-ahead)."""
    d = d.copy()
    # CO2: -999 placeholders and anything physically impossible (< 250 ppm) -> missing
    if "co2" in d:
        d.loc[(d["co2"] < 250) | (d["co2"] > 10000), "co2"] = np.nan
    # Room temperature: unit changed from degC to degF part-way through (values > 45 are degF)
    if "rt" in d:
        rt = d["rt"]
        d["rt"] = np.where(rt > 45, (rt - 32.0) / 1.8, rt)
        d.loc[(d["rt"] < 5) | (d["rt"] > 45), "rt"] = np.nan
    # Outdoor temperature: isolated spikes of +40..+60 degC (glitches) -> missing
    if "oat" in d:
        d.loc[(d["oat"] > 35) | (d["oat"] < -35), "oat"] = np.nan
    for c in ("active", "light", "window"):
        if c in d:
            d.loc[~d[c].isin([0, 1]), c] = np.nan
    if "damper" in d:
        d.loc[(d["damper"] < 0) | (d["damper"] > 100), "damper"] = np.nan
    return d


def to_bins(d):
    """Aggregate 5-min -> 15-min bins (UTC, labelled by interval start).

    Returns (bins, last_complete) where last_complete is the start of the last bin whose
    three 5-min slots all lie at or before the last timestamp in the file.
    """
    g = d.resample("15min", label="left", closed="left")
    b = g.mean()
    co2 = d["co2"] if "co2" in d else None
    if co2 is not None:
        b["co2_last"] = co2.resample("15min").last()
        b["co2_med"] = g["co2"].median()
        b["co2_max"] = g["co2"].max()
        b["co2_min"] = g["co2"].min()
    b["sol"] = b[[c for c in ("sol_e", "sol_s", "sol_w") if c in b]].mean(axis=1)
    last_ts = d.index.max()
    last_complete = (last_ts - pd.Timedelta("10min")).floor("15min")
    return b, last_complete


STATE_COLS = ["active", "damper", "light", "window", "flow", "lux", "rt", "oat", "sol", "wind",
              "vent_el", "dh", "hc", "sat"]


def _ffill_limit(s, n):
    return s.ffill(limit=n)


def build_frame(bins, last_complete):
    """Build the feature frame indexed by the forecast interval start T (UTC)."""
    b = bins.copy()
    idx = b.index
    # extend the grid by H bins so forecasts for the hour after the last complete bin exist
    full = pd.date_range(idx.min(), last_complete + H * STEP, freq="15min", tz="UTC")
    b = b.reindex(full)
    # a bin is usable only if complete
    b.loc[b.index > last_complete, :] = np.nan

    # --- state variables, short gaps forward-filled (causal) ---
    S = pd.DataFrame(index=b.index)
    for c in STATE_COLS:
        if c in b:
            S[c] = _ffill_limit(b[c], 8)
    co2 = b["co2"]
    co2f = co2.ffill(limit=16)          # short-gap fill for the *input* only
    co2_last = b["co2_last"].ffill(limit=16)
    co2_med = b["co2_med"].ffill(limit=16)

    F = {}
    # CO2 history (all measured at bin t, will be shifted by H below)
    F["co2"] = co2f
    F["co2_last"] = co2_last
    F["co2_med"] = co2_med
    F["co2_d1"] = co2f - co2f.shift(1)
    F["co2_d2"] = co2f - co2f.shift(2)
    F["co2_d4"] = co2f - co2f.shift(4)
    F["co2_d8"] = co2f - co2f.shift(8)
    F["co2_lag1"] = co2f.shift(1)
    F["co2_lag2"] = co2f.shift(2)
    F["co2_lag4"] = co2f.shift(4)
    F["co2_lag8"] = co2f.shift(8)
    for w in (4, 8, 24, 96):
        F[f"co2_max{w}"] = co2f.rolling(w, min_periods=1).max()
        F[f"co2_min{w}"] = co2f.rolling(w, min_periods=1).min()
    F["co2_mean8"] = co2f.rolling(8, min_periods=1).mean()
    F["co2_mean24"] = co2f.rolling(24, min_periods=1).mean()
    F["co2_above_bg"] = co2f - F["co2_min96"]
    F["co2_rel_max24"] = co2f - F["co2_max24"]
    # time since CO2 last changed (bins), capped
    chg = (co2f.diff().abs() > 0).astype(float)
    grp = chg.cumsum()
    F["co2_hold"] = (chg.groupby(grp).cumcount()).clip(upper=96).astype(float)

    # state features
    act = S["active"] if "active" in S else pd.Series(0.0, index=b.index)
    F["active"] = act
    F["active_m4"] = act.rolling(4, min_periods=1).mean()
    F["active_m16"] = act.rolling(16, min_periods=1).mean()
    F["active_m96"] = act.rolling(96, min_periods=1).mean()
    # hours since active last 1 (causal), capped at 14 days
    a1 = act.fillna(0.0)
    last_on = pd.Series(np.where(a1 > 0.5, np.arange(len(a1)), np.nan), index=a1.index).ffill()
    F["since_active"] = ((np.arange(len(a1)) - last_on) / 4.0).clip(upper=24 * 14)
    # consecutive-on run length so far (hours)
    on_run = (a1 > 0.5).astype(int)
    rid = (on_run != on_run.shift()).cumsum()
    F["active_run"] = on_run.groupby(rid).cumcount().where(on_run == 1, 0) / 4.0

    for c in ("damper", "light", "window", "flow", "lux", "rt", "oat", "sol", "wind", "vent_el", "dh", "hc", "sat"):
        if c in S:
            F[c] = S[c]
    for c in ("flow", "damper", "lux"):
        if c in S:
            F[c + "_m4"] = S[c].rolling(4, min_periods=1).mean()
    if "rt" in S:
        F["rt_d4"] = S["rt"] - S["rt"].shift(4)
    if "oat" in S:
        F["oat_d8"] = S["oat"] - S["oat"].shift(8)

    F = pd.DataFrame(F, index=b.index)
    # --- shift: everything in F is known at the END of bin t; forecast for T uses bin T-H ---
    X = F.shift(H)
    X.columns = ["f_" + c for c in X.columns]

    # --- features known ahead: calendar + schedule memory (>= 1 day old) ---
    Tidx = X.index
    loc = Tidx.tz_convert(LOCAL_TZ)
    hod = loc.hour + loc.minute / 60.0
    X["tod"] = hod
    X["tod_sin"] = np.sin(2 * np.pi * hod / 24)
    X["tod_cos"] = np.cos(2 * np.pi * hod / 24)
    dow = loc.dayofweek
    X["dow"] = dow
    X["weekend"] = (dow >= 5).astype(int)
    # active at the same local time on previous days (all >= 24 h before T)
    a = act.copy()
    # same wall-clock time yesterday: shift by 96 bins (DST shifts by 1 h twice a year: negligible)
    for k in (1, 2, 7):
        X[f"act_prev{k}d"] = a.shift(96 * k)
    X["act_prev5d_mean"] = pd.concat([a.shift(96 * k) for k in range(1, 6)], axis=1).mean(axis=1)
    X["act_prev7d_mean"] = pd.concat([a.shift(96 * k) for k in range(1, 8)], axis=1).mean(axis=1)
    # smoothed (+-1 bin) previous-day activity
    X["act_prev1d_sm"] = pd.concat([a.shift(95), a.shift(96), a.shift(97)], axis=1).mean(axis=1)
    # CO2 same time yesterday above its own daily minimum
    X["co2_prev1d"] = co2f.shift(96)
    X["flow_prev1d"] = S["flow"].shift(96) if "flow" in S else np.nan
    return X, F, b


def target_series(d5):
    """15-min mean of 5-min CO2 (cleaned), indexed by interval start (UTC)."""
    return d5["co2"].resample("15min", label="left", closed="left").mean()
