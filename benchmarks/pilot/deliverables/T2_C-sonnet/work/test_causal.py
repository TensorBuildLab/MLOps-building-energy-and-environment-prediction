"""Causality tests for predict(): (1) truncation, (2) perturbation of everything at/after T-45min."""
import os, sys, time, importlib.util, tempfile
import numpy as np, pandas as pd
path = sys.argv[1]
spec = importlib.util.spec_from_file_location("mdl", path); mdl = importlib.util.module_from_spec(spec); spec.loader.exec_module(mdl)
csv = sys.argv[2]
raw = pd.read_csv(csv)
ts = pd.to_datetime(raw["timestamp"].str.replace(r"\s*[+-]\d\d:?\d\d$", "", regex=True), format="%Y-%m-%d %H:%M")
t0 = time.time(); full = mdl.predict(csv); print("full predict secs", round(time.time() - t0, 1), "n", len(full), flush=True)
print(full.head(3)); print(full.index.dtype, full.index.tz)
rng = np.random.default_rng(0)
cand = full.index[(full.index >= "2021-10-27") & (full.index.isin(pd.DatetimeIndex(ts).floor("15min")))]
# choose T around transitions and random ones
T_list = list(pd.to_datetime(["2021-11-02 08:00", "2021-11-02 08:15", "2021-11-02 09:00", "2021-11-02 18:30", "2021-11-02 18:45",
                              "2021-11-16 10:30", "2021-11-15 01:10", "2021-10-28 21:15", "2021-10-28 23:45", "2021-12-09 12:00", "2021-12-09 23:45"]))
T_list += list(rng.choice(cand, 14, replace=False))
tmp = tempfile.mkdtemp()
bad = 0
for T in T_list:
    T = pd.Timestamp(T)
    cut = T - pd.Timedelta("45min")
    sub = raw[ts < cut]
    f1 = os.path.join(tmp, "trunc.csv"); sub.to_csv(f1, index=False)
    p1 = mdl.predict(f1)
    v_full = full.get(T, np.nan); v_tr = p1.get(T, np.nan)
    # perturbation: garble all rows at/after cut
    pert = raw.copy()
    m = (ts >= cut).values
    num = pert.columns[1:]
    for c in num:
        pert[c] = pd.to_numeric(pert[c], errors="coerce").astype(float)
    pert.loc[m, num] = rng.normal(500, 300, size=(m.sum(), len(num)))
    f2 = os.path.join(tmp, "pert.csv"); pert.to_csv(f2, index=False)
    p2 = mdl.predict(f2)
    v_pe = p2.get(T, np.nan)
    ok = np.isclose(v_full, v_tr, atol=1e-9) and np.isclose(v_full, v_pe, atol=1e-9)
    bad += (not ok)
    print(f"T={T}  full={v_full:.6f} trunc={v_tr:.6f} perturbed={v_pe:.6f}  {'OK' if ok else 'MISMATCH'}", flush=True)
print("mismatches:", bad)
