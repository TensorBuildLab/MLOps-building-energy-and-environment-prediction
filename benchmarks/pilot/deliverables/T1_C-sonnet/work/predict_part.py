

# =====================================================================================
# Serving
# =====================================================================================
import os as _os

_ARTIFACT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "model_artifact.joblib")
_CACHE = {}


def _load_artifact():
    if "art" not in _CACHE:
        import joblib
        _CACHE["art"] = joblib.load(_ARTIFACT)
    return _CACHE["art"]


def _profile_value(art, loc_index):
    """Fallback when no usable CO2 history exists: typical CO2 by weekday/weekend and hour."""
    prof = art["profile"]
    hr = np.asarray(loc_index.hour)
    wk = (np.asarray(loc_index.dayofweek) >= 5).astype(int)
    return np.array([prof.get((int(w), int(h)), art["global_median"]) for w, h in zip(wk, hr)], dtype=float)


def predict(csv_path):
    """Forecast of the 15-min mean CO2 (ppm) for every 15-min interval, 1 h ahead.

    The value for the interval starting at T uses only 15-min bins that end at or before
    T - 45 min (bins starting at T - 60 min or earlier). The returned index runs from the
    first interval in the file up to one hour after the last COMPLETE 15-min bin, so the
    live forecast beyond the end of the file is included. Index = interval start in local
    time (naive), as in the file.
    """
    art = _load_artifact()
    d = read_raw(csv_path)
    d5 = clean5(d)
    bins, last_complete = to_bins(d5)
    X, F, b = build_frame(bins, last_complete)
    cols = art["cols"]
    Xm = X[cols]
    base = X["f_co2"]
    have = base.notna().to_numpy()
    delta = np.zeros(len(X), dtype=float)
    if have.any():
        for w, est in art["models"]:
            delta[have] += w * est.predict(Xm[have])
    pred = base.to_numpy(dtype=float) + delta
    loc_index = X.index.tz_convert(LOCAL_TZ)
    fb = _profile_value(art, loc_index)
    pred = np.where(have, pred, fb)
    pred = np.clip(pred, art["clip"][0], art["clip"][1])
    out = pd.Series(pred, index=loc_index.tz_localize(None), name="co2_forecast_1h")
    out.index.name = "timestamp"
    # wall-clock duplicates (autumn DST): keep the first occurrence only (it is the causal one)
    out = out[~out.index.duplicated(keep="first")]
    return out
