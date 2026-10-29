"""T2: 1-hour-ahead forecast of 15-min chilled_water_energy (kWh).

Model: weekday clock profile (mean energy per minute-of-day, learned on training weekdays) +
ridge correction on the *recent deviation from that profile* and a few lagged outdoor / AHU signals.
Everything the forecast for interval T uses is computed from 15-min intervals that START at or before
T - 60 min (i.e. raw rows with timestamps < T - 45 min) plus the calendar.

predict(csv_path) does not train: it loads model_artifacts.json next to this file.
"""
import json
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ART_PATH = os.path.join(HERE, "model_artifacts.json")
CW = "chilled_water_energy"
H = 4  # forecast horizon in 15-min steps (1 h)

EXOG = ["dry_bulb_temp", "global_horizontal_solar_radiation", "outdoor_relative_humidity",
        "air_temperature", "offcoil_air_temp", "cooling_coil_valve_command"]
MEANCOLS = EXOG + ["ahu_fan_speed"]
DEFAULT_CFG = dict(on_thr=2.0, nl=[4, 5, 6, 7, 8], win=8, alpha=30.0, clip=3.0, rd3=True, exog_lags=[4])


# ----------------------------------------------------------------------------- loading and cleaning
def load_raw(csv_path):
    """Read the trend export: any row order, duplicates, text in number columns, '+08:00' suffix."""
    df = pd.read_csv(csv_path)
    tcol = "timestamp" if "timestamp" in df.columns else df.columns[0]
    ts = df[tcol].astype(str).str.replace(r"\s*(Z|[+-]\d\d:?\d\d)$", "", regex=True).str.strip()
    t = pd.to_datetime(ts, format="%Y-%m-%d %H:%M", errors="coerce")
    if t.isna().mean() > 0.5:
        t = pd.to_datetime(ts, errors="coerce")
    df = df.drop(columns=tcol)
    df.columns = [re.sub(r"\s*\[.*\]\s*$", "", c).strip() for c in df.columns]
    df["ts"] = t
    df = df[df["ts"].notna()].drop_duplicates("ts", keep="last").set_index("ts").sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")   # 'OFFLINE' etc. -> NaN
    for c in [CW, "cooling_coil_valve_command"] + MEANCOLS:
        if c not in df.columns:
            df[c] = np.nan
    return df


def _f_to_c(s, thr):
    return pd.Series(np.where(s > thr, (s - 32.0) / 1.8, s), index=s.index)


def clean5(df):
    """Row-wise / previous-sample-only cleaning (causal) of the 5-min data."""
    df = df.copy()
    cw = df[CW].where(df[CW] > -900)          # -999 placeholder
    cw = cw.where(cw >= 0)
    valve = df["cooling_coil_valve_command"]
    # meter outage / dropout: reads (almost) zero although the cooling-coil valve is commanded open;
    # with the valve open the real 5-min energy is never below ~1.2 kWh
    fault0 = (cw < 0.5) & (valve > 15)
    # stuck meter: exactly the same non-zero reading as the previous sample
    stuck = (cw > 0) & (cw == cw.shift(1))
    df[CW] = cw.mask(fault0 | stuck)
    # unit switches (some points start reporting degF)
    df["air_temperature"] = _f_to_c(df["air_temperature"], 45.0)
    df["offcoil_air_temp"] = _f_to_c(df["offcoil_air_temp"], 45.0)
    df["dry_bulb_temp"] = _f_to_c(df["dry_bulb_temp"], 60.0)
    df.loc[df["outdoor_relative_humidity"] > 100, "outdoor_relative_humidity"] = np.nan
    return df


def grid15(df5):
    """15-min grid labelled by interval start. Energy = sum of the three 5-min values
    (one missing value scaled up, two or more missing -> NaN)."""
    r = df5.resample("15min")
    n = r[CW].count()
    y = r[CW].sum(min_count=1) * 3.0 / n.replace(0, np.nan)
    y = y.where(n >= 2)
    g = r[MEANCOLS].mean()
    g["y"] = y
    return g


# ----------------------------------------------------------------------------- features
def _mod_dow(index):
    mod = pd.Series(index.hour * 60 + index.minute, index=index)
    wk = pd.Series(index.dayofweek < 5, index=index)
    return mod, wk


def build_features(g, prof, cfg):
    """Feature matrix, one row per grid interval T. Only grid rows <= T-4 steps (and calendar) are used."""
    mod, wk = _mod_dow(g.index)
    pm = mod.map(prof).where(wk, np.nan)                     # profile at T (weekdays only)
    on_thr = cfg["on_thr"]
    r = (g["y"] - pm).where(pm > on_thr)                      # deviation from profile inside the on-window
    if cfg.get("clip"):
        r = r.clip(-cfg["clip"], cfg["clip"])
    F = pd.DataFrame(index=g.index)
    for k in cfg["nl"]:
        F[f"r{k}"] = r.shift(k)
    F["rm"] = r.shift(H).rolling(cfg["win"], min_periods=1).mean()
    F["cnt"] = r.shift(H).rolling(cfg["win"], min_periods=1).count()
    if cfg.get("rd3"):
        F["rd3"] = r.shift(H).rolling(288, min_periods=8).mean()
        F["rd1"] = r.shift(H).rolling(96, min_periods=8).mean()
    F = F.fillna(0.0)
    for c in EXOG:
        for k in cfg["exog_lags"]:
            F[f"{c}_l{k}"] = g[c].shift(k)
    F["pT"] = pm
    return F


def fit_artifacts(g, train_mask=None, cfg=None, trim=0.0):
    """Fit profile + ridge on grid g (rows with valid y). train_mask: boolean Series on g.index."""
    cfg = dict(DEFAULT_CFG, **(cfg or {}))
    mod, wk = _mod_dow(g.index)
    ok = g["y"].notna() if train_mask is None else (g["y"].notna() & train_mask)
    sel = ok & wk
    grp = g.loc[sel, "y"].groupby(mod[sel])
    if trim > 0:
        def tm(v):
            v = np.sort(v.values); k = int(len(v) * trim)
            return float(v[k:len(v) - k].mean()) if len(v) - 2 * k > 0 else float(v.mean())
        prof = grp.apply(tm)
    else:
        prof = grp.mean()
    prof = prof.reindex(range(0, 1440, 15))
    prof = prof.fillna(0.0)
    F = build_features(g, prof, cfg)
    rows = ok & wk & (F["pT"] > cfg["on_thr"])
    X = F.loc[rows].drop(columns="pT")
    cols = list(X.columns)
    mu = X.mean(); sd = X.std().replace(0, 1.0).fillna(1.0)
    Z = ((X - mu) / sd).fillna(0.0).clip(-5, 5).values
    t = (g.loc[rows, "y"] - F.loc[rows, "pT"]).values
    # ridge with intercept (closed form)
    zm = Z.mean(0); tm_ = t.mean()
    A = (Z - zm).T @ (Z - zm) + cfg["alpha"] * np.eye(Z.shape[1])
    coef = np.linalg.solve(A, (Z - zm).T @ (t - tm_))
    icpt = tm_ - zm @ coef
    return dict(cfg=cfg, prof={int(k): float(v) for k, v in prof.items()}, cols=cols,
                mu=[float(v) for v in mu], sd=[float(v) for v in sd], coef=[float(v) for v in coef],
                intercept=float(icpt), n_train=int(rows.sum()))


def predict_grid(g, art):
    cfg = art["cfg"]
    prof = pd.Series({int(k): v for k, v in art["prof"].items()})
    F = build_features(g, prof, cfg)
    mu = pd.Series(art["mu"], index=art["cols"]); sd = pd.Series(art["sd"], index=art["cols"])
    Z = ((F[art["cols"]] - mu) / sd).fillna(0.0).clip(-5, 5)
    res = pd.Series(Z.values @ np.array(art["coef"]) + art["intercept"], index=g.index)
    pT = F["pT"]
    out = pT.fillna(0.0) + res.where(pT > cfg["on_thr"], 0.0)
    # Not a weekday (no such days in the training data): persistence of the last usable value (>= 1 h old)
    _, wk = _mod_dow(g.index)
    out = out.where(wk, g["y"].shift(H).fillna(0.0))
    return out.clip(lower=0.0, upper=40.0)


# ----------------------------------------------------------------------------- public API
def predict(csv_path):
    with open(ART_PATH) as f:
        art = json.load(f)
    df = load_raw(csv_path)
    if len(df) == 0:
        return pd.Series(dtype=float, name="chilled_water_energy_forecast")
    df5 = clean5(df)
    g = grid15(df5)
    present = df5.resample("15min")[CW].size()
    present = present[present > 0].index         # 15-min intervals that exist in the file
    # complete 15-min grid (so that shift(k) means "k intervals earlier"), extended 1 h beyond the data
    # so that the live forecast for the next hour is returned as well
    last = present.max()
    full = pd.date_range(present.min().floor("D"), last + pd.Timedelta(minutes=15 * H), freq="15min")
    g = g.reindex(full)
    out = predict_grid(g, art)
    keep = present.union(pd.date_range(last + pd.Timedelta(minutes=15), periods=H, freq="15min"))
    out = out.loc[keep]
    out.name = "chilled_water_energy_forecast"
    out.index.name = "timestamp"
    return out.astype(float)
