import re
p = 'model.py'
s = open(p, encoding='utf-8').read()
a = s.index('def _bin_target(g):')
b = s.index('# --------------------------------------------------------------------------------------\n# prediction')
new = '''def _bin_mean5(g):
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


'''
s = s[:a] + new + s[b:]
s = s.replace('''    X, T_index, B = feature_table(clean)
    pred = predict_X(X, bundle)
    return pd.Series(pred, index=T_index, name="CO2_forecast"), B''','''    X, T_index, y = feature_table(clean, 15)
    pred = predict_X(X, bundle)
    return pd.Series(pred, index=T_index, name="CO2_forecast"), y''')
open(p,'w',encoding='utf-8').write(s)
