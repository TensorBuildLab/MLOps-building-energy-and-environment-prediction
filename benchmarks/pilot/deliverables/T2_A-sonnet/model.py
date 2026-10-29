"""T2 - 1-hour-ahead forecast of 15-minute chilled-water energy (kWh).

Public API:  predict(csv_path) -> pandas.Series   (index = 15-min interval start, naive local time)

Causality contract
------------------
The forecast for the interval starting at T uses only 5-minute rows with timestamp <= T - 50 min
(i.e. strictly before T - 45 min).  Every feature below is computed at a 5-minute row t with
trailing (backward-looking) windows only, and is then attached to the target T = t + 50 min.
Nothing in the pipeline looks at a file-wide statistic, a future row, a centred window, a
back-fill or a global scaler, so changing any row with timestamp >= T - 45 min cannot change
the forecast for T.  (The only forward-looking operation, `target_series`, builds the training
target / the "same time on earlier days" profile from intervals that finished >= 24 h before T.)

The model itself (gradient boosting + a small rule layer) is trained offline by work/train.py
and stored in model_bundle.joblib next to this file.  predict() never retrains.
"""
import os
import re

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_BUNDLE = os.path.join(_HERE, "model_bundle.joblib")

LEAD_ROWS = 10          # T - 50 min = last usable 5-minute row (10 rows of 5 min before T)
EXTEND_H = 72           # forecasts are also issued up to 72 h after the last record in the file
CW_MAX_5MIN = 8.0       # larger single readings are catch-up spikes after meter drop-outs

# canonical short name -> raw column prefix (text before " [")
_COLS = {
    "cw": "chilled_water_energy",
    "fan": "ahu_fan_speed",
    "vc": "cooling_coil_valve_command",
    "vp": "cooling_coil_valve_position",
    "sat": "supply_air_temperature",
    "oat": "offcoil_air_temp",
    "filt": "pressure_across_filter",
    "fane": "ahu_fan_energy",
    "dbt": "dry_bulb_temp",
    "ghi": "global_horizontal_solar_radiation",
    "orh": "outdoor_relative_humidity",
    "wind": "wind_speed",
    "iat": "air_temperature",
    "irh": "indoor_relative_humidity",
    "co2": "indoor_co2",
    "occ": "occupant_count",
    "wifi": "wifi_connected_devices",
}


# --------------------------------------------------------------------------------------
# 1. reading / cleaning
# --------------------------------------------------------------------------------------
def _parse_ts(s):
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\s*(Z|[+-]\d{2}:?\d{2})$", "", regex=True)   # keep local wall-clock time
    return pd.to_datetime(s, errors="coerce")


def read_clean(csv_path):
    """Raw trend export -> regular 5-minute grid of cleaned signals (NaN = unusable).

    Handles: unordered / reversed rows, replayed (duplicate) timestamps, -999 sentinels,
    text such as 'OFFLINE' in numeric columns, Fahrenheit readings in the indoor
    temperature column, physically impossible values, catch-up spikes, gaps (left as NaN,
    never filled).
    """
    raw = pd.read_csv(csv_path, dtype=str)
    raw.columns = [str(c).strip() for c in raw.columns]
    tcol = raw.columns[0]
    for c in raw.columns:
        if c.lower().startswith("timestamp"):
            tcol = c
            break
    ts = _parse_ts(raw[tcol]).dt.floor("5min")
    base = {}
    for c in raw.columns:
        base[re.split(r"\s*\[", c)[0].strip().lower()] = c

    d = pd.DataFrame({"ts": ts})
    for short, prefix in _COLS.items():
        if prefix in base:
            d[short] = pd.to_numeric(raw[base[prefix]], errors="coerce")
        else:
            d[short] = np.nan
    d = d[d["ts"].notna()]
    # file order is not trusted: stable sort by time, keep the first record of a replayed timestamp
    d = d.sort_values("ts", kind="stable").drop_duplicates("ts", keep="first").set_index("ts")

    num = list(d.columns)
    d[num] = d[num].where(d[num] > -900.0)                  # -999 sentinel (and anything alike)
    d["cw"] = d["cw"].where((d["cw"] >= 0.0) & (d["cw"] <= CW_MAX_5MIN))
    d["iat"] = d["iat"].where(d["iat"] < 45.0, (d["iat"] - 32.0) / 1.8)   # Fahrenheit rows
    d["iat"] = d["iat"].where((d["iat"] > 10) & (d["iat"] < 45))
    d["dbt"] = d["dbt"].where((d["dbt"] > 15) & (d["dbt"] < 40))
    d["ghi"] = d["ghi"].where((d["ghi"] >= 0) & (d["ghi"] < 1500))
    d["orh"] = d["orh"].where((d["orh"] >= 0) & (d["orh"] <= 100))
    d["irh"] = d["irh"].where((d["irh"] >= 0) & (d["irh"] <= 100))
    d["co2"] = d["co2"].where((d["co2"] >= 300) & (d["co2"] < 5000))
    d["wind"] = d["wind"].where((d["wind"] >= 0) & (d["wind"] < 30))

    if len(d) == 0:
        return d
    # the grid runs EXTEND_H hours past the last row so that intervals T after the end of the data (or inside
    # a data gap, e.g. the first intervals after a weekend) can still be forecast from the last known state
    grid = pd.date_range(d.index.min().floor("15min"), (d.index.max() + pd.Timedelta(hours=EXTEND_H + 1)).floor("15min"), freq="5min")
    out = d.reindex(grid)
    out.attrs["last_row"] = d.index.max()
    return out


# --------------------------------------------------------------------------------------
# 2. meter-fault detection (causal, row-wise)
# --------------------------------------------------------------------------------------
def _run_length(flag):
    """Number of consecutive True values ending at each row (0 where False). Causal."""
    f = np.asarray(flag.fillna(False), dtype=bool)
    out = np.zeros(len(f), dtype=np.int32)
    run = 0
    for i in range(len(f)):
        run = run + 1 if f[i] else 0
        out[i] = run
    return pd.Series(out, index=flag.index)


def _latch(set_flag, clear_flag):
    """State that turns on at `set_flag`, off at `clear_flag`, otherwise keeps its value."""
    ev = pd.Series(np.nan, index=set_flag.index)
    ev[clear_flag.to_numpy()] = 0.0
    ev[set_flag.to_numpy()] = 1.0
    return ev.ffill().fillna(0.0) > 0.5


def add_fault_flags(G):
    """Detect chilled-water meter faults from the history (all rules are backward-looking).

    dead  : meter reads exactly 0 although the AHU is running hard with the cooling valve open
            (fan > 20 Hz, valve command > 20 %) -> meter offline / reporting zero.
    stuck : meter repeats exactly the same positive value (frozen register).
    Faulty readings are removed from the cw signal (NaN).  Two latched states are kept:
    `dead_state` (on after 1 h of dead readings, off at the first healthy working reading) and
    `stuck_state` (on after 1 h of identical readings, off at the next different value).
    """
    G = G.copy()
    cw = G["cw"]
    working = (G["fan"] > 20.0) & (G["vc"] > 20.0)
    dead = (cw == 0.0) & working
    same = (cw > 0.05) & (cw == cw.shift(1))
    dead_run = _run_length(dead)
    stuck_run = _run_length(same)
    alive = working & (cw > 0.3)
    # a latched fault expires after 3 days without any data (weekends are fine, long outages are not)
    expire = _run_length(G["fan"].isna() & cw.isna()) >= 864
    G["dead_state"] = _latch(dead_run >= 12, alive | expire)
    G["stuck_state"] = _latch(stuck_run >= 12, (cw.notna() & ~same) | expire)
    G["stuck_val"] = cw.where(same).ffill(limit=2)
    bad = dead | (stuck_run >= 5)
    G["cw"] = cw.where(~bad)
    return G


# --------------------------------------------------------------------------------------
# 3. features (row-wise causal at t, later attached to T = t + 50 min)
# --------------------------------------------------------------------------------------
def _rmean(s, w, mp=1):
    return s.rolling(w, min_periods=mp).mean()


def tod5(idx):
    return np.asarray((idx.hour * 60 + idx.minute) // 5, dtype=int)


def make_p5(G, rowmask=None):
    """Typical 5-minute chilled-water energy by time of day (288 values) from healthy history."""
    c = G["cw"] if rowmask is None else G["cw"].where(rowmask)
    p = c.groupby(tod5(G.index)).mean().reindex(range(288))
    p = p.fillna(0.0).to_numpy(dtype=float, copy=True)
    p[p < 0.05] = 0.0
    return p


def row_features(G, p5):
    """Causal features evaluated at every 5-minute row t (uses rows <= t only)."""
    F = pd.DataFrame(index=G.index)
    cw, fan, vc = G["cw"], G["fan"], G["vc"]
    prof = pd.Series(p5[tod5(G.index)], index=G.index)
    work = (prof > 0.5) & ~(fan <= 5.0)                # normally working hours, and the AHU is not seen switched off
    an = (cw - prof).where(work)                       # chilled-water anomaly vs typical profile (5-min kWh)
    F["a_0"] = an.ffill(limit=3)
    for k in range(4):
        F[f"a_b{k}"] = an.shift(3 * k).rolling(3, min_periods=2).mean()
    F["a_6"] = _rmean(an, 6)
    F["a_12"] = _rmean(an, 12)
    F["a_36"] = _rmean(an, 36)
    # today's mean anomaly so far (date of t) and recent days' mean anomaly
    date = G.index.normalize()
    av = an.notna()
    F["a_today"] = an.where(av, 0.0).groupby(date).cumsum() / av.astype(float).groupby(date).cumsum().replace(0, np.nan)
    F["n_today"] = av.astype(float).groupby(date).cumsum()
    dsum = an.where(av, 0.0).groupby(date).sum()
    dcnt = av.astype(float).groupby(date).sum()
    dm = (dsum / dcnt.replace(0, np.nan)).where(dcnt >= 60)       # complete working days only
    F["a_prev1"] = dm.shift(1).ffill().reindex(date).to_numpy()
    F["a_prev3"] = dm.rolling(3, min_periods=1).mean().shift(1).ffill().reindex(date).to_numpy()
    # raw level of chilled water, running state of the AHU
    F["cw_12"] = _rmean(cw, 12)
    F["cw_b0"] = cw.rolling(3, min_periods=2).mean()
    F["fan_0"] = fan
    F["fan_3"] = _rmean(fan, 3)
    F["fan_12"] = _rmean(fan, 12)
    F["vc_0"] = vc
    F["vc_3"] = _rmean(vc, 3)
    F["vc_12"] = _rmean(vc, 12)
    F["vp_3"] = _rmean(G["vp"], 3)
    F["sat_3"] = _rmean(G["sat"], 3)
    F["oat_3"] = _rmean(G["oat"], 3)
    F["filt_3"] = _rmean(G["filt"], 3)
    F["fane_3"] = _rmean(G["fane"], 3)
    on = fan > 5.0
    F["on_dur"] = _run_length(on) * 5.0
    F["off_dur"] = _run_length((~on) & fan.notna()) * 5.0
    # weather
    F["dbt_0"] = G["dbt"].ffill(limit=6)
    F["dbt_12"] = _rmean(G["dbt"], 12)
    F["dbt_36"] = _rmean(G["dbt"], 36)
    F["ghi_3"] = _rmean(G["ghi"], 3)
    F["ghi_12"] = _rmean(G["ghi"], 12)
    F["ghi_36"] = _rmean(G["ghi"], 36)
    F["orh_6"] = _rmean(G["orh"], 6)
    F["wind_12"] = _rmean(G["wind"], 12)
    # indoor
    F["iat_3"] = _rmean(G["iat"], 3)
    F["irh_3"] = _rmean(G["irh"], 3)
    F["co2_3"] = _rmean(G["co2"], 3)
    F["occ_12"] = _rmean(G["occ"], 12)
    F["wifi_12"] = _rmean(G["wifi"], 12)
    return F


def target_series(G):
    """15-minute total chilled-water energy per interval start (NaN if any reading unusable)."""
    c = G["cw"]
    tot = c + c.shift(-1) + c.shift(-2)
    return tot[(tot.index.minute % 15) == 0]


def interval_frame(G, p5):
    """Feature matrix indexed by 15-min interval start T (all grid intervals)."""
    F = row_features(G, p5)
    Fs = F.shift(LEAD_ROWS)                         # row t = T - 50 min  ->  T
    keep = (Fs.index.minute % 15) == 0
    X = Fs.loc[keep].copy()
    T = X.index
    X["tod"] = (T.hour * 60 + T.minute).astype(float)
    X["dow"] = np.asarray(T.day_of_week, dtype=float)
    k = tod5(T)
    X["p15"] = p5[k] + p5[(k + 1) % 288] + p5[(k + 2) % 288]       # typical energy of this interval
    return X


def fault_state(G):
    """Latched meter-fault states, seen from forecast time (row T - 50 min)."""
    S = pd.DataFrame(index=G.index)
    S["dead"] = G["dead_state"].astype(float)
    S["stuck"] = G["stuck_state"].astype(float)
    S["stuck_val"] = G["stuck_val"]
    Ss = S.shift(LEAD_ROWS)
    return Ss.loc[(Ss.index.minute % 15) == 0]


# --------------------------------------------------------------------------------------
# 4. prediction = typical profile + per-segment ridge on the anomaly + rule layer
# --------------------------------------------------------------------------------------
P_REF = 6.7                                   # typical steady-state 15-min energy (scaling of anomalies)
SEGMENTS = {"A": (480, 540), "B": (540, 1095), "C": (1095, 1140)}   # start-up / steady / shut-down (minutes of day of T)


def scaled_features(X):
    """Anomaly features are expressed relative to the size of the typical interval energy."""
    X = X.copy()
    k = (X["p15"] / P_REF).to_numpy()
    for c in X.columns:
        if c.startswith("a_"):
            X[c] = X[c] * k
    return X


def residual_predict(bundle, X):
    """Anomaly forecast (kWh) added to the typical interval energy `p15`."""
    Xs = scaled_features(X)
    out = pd.Series(0.0, index=X.index)
    for seg, (lo, hi) in SEGMENTS.items():
        m = ((X["tod"] >= lo) & (X["tod"] < hi) & (X["p15"] > 0.5)).to_numpy()
        if m.any():
            feats = bundle["features"][seg]
            Z = Xs.loc[m, feats]
            if "clip" in bundle:                      # keep inputs inside the range seen in training
                lo = pd.Series({f: bundle["clip"][seg][f][0] for f in feats})
                hi = pd.Series({f: bundle["clip"][seg][f][1] for f in feats})
                Z = Z.clip(lower=lo, upper=hi, axis=1)
            out[m] = bundle["ridge"][seg].predict(Z)
    return out


def apply_rules(bundle, X, S, pred):
    cap = bundle.get("cap", 15.0)
    pred = pred.clip(lower=0.0, upper=cap).copy()
    tod = X["tod"].to_numpy()
    fan_known = X["fan_0"].notna().to_numpy()
    off_seen = (fan_known & (X["fan_0"].to_numpy() < 5.0) & (X["off_dur"].to_numpy() >= 15.0))
    working = ((X["fan_3"].to_numpy() > 20.0) & (X["vc_3"].to_numpy() > 20.0))
    # (a) AHU confirmed off for >= 15 min although it should have been started long ago: no start-up expected
    late_off = off_seen & (tod >= 540) & (tod < 1140)
    pred[late_off] = 0.0
    # (b) weekends: no weekend history exists, so do not invent a start-up unless the AHU is seen running
    wk = (X["dow"].to_numpy() >= 5) & ~(X["fan_3"].to_numpy() > 5.0)
    pred[wk] = 0.0
    # (c) AHU seen working outside its usual hours (before 08:00 / from 18:45): persist the recent level
    t_tod = (tod - 50.0) % 1440.0
    odd = working & ((t_tod < 480) | (t_tod >= 1125))
    persist = 3.0 * X["cw_b0"].to_numpy()
    use = odd & ~np.isnan(persist)
    pred[use] = np.minimum(np.maximum(pred.to_numpy()[use], persist[use]), cap)
    # (d) persistent chilled-water meter faults (dead meter reads 0, frozen meter repeats its value)
    dead = S["dead"].reindex(pred.index).fillna(0).to_numpy() > 0.5
    pred[dead] = 0.0
    sval = S["stuck_val"].reindex(pred.index).to_numpy()
    stuck = (S["stuck"].reindex(pred.index).fillna(0).to_numpy() > 0.5) & ~np.isnan(sval)
    pred[stuck] = np.minimum(3.0 * sval[stuck], cap)
    return pred.fillna(X["p15"]).fillna(0.0)


def predict(csv_path):
    import joblib
    bundle = joblib.load(_BUNDLE)
    G = read_clean(csv_path)
    if len(G) == 0:
        return pd.Series(dtype=float, name="chilled_water_energy_15min")
    last_row = G.attrs["last_row"]                # timestamp of the last record in the file
    G = add_fault_flags(G)
    X = interval_frame(G, bundle["p5"])
    S = fault_state(G)
    base = X["p15"] + residual_predict(bundle, X)
    pred = apply_rules(bundle, X, S, base)
    # one forecast per 15-minute interval from the start of the file to EXTEND_H hours after its last record
    pred = pred[pred.index <= (last_row + pd.Timedelta(hours=EXTEND_H))]
    pred = pred.astype(float)
    pred.name = "chilled_water_energy_15min"
    pred.index.name = "timestamp"
    return pred
