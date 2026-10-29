"""Leakage self-test: truncating / corrupting the file after T-45min must not change forecast(T)."""
import os
import sys
import time
import numpy as np
import pandas as pd
import model as M

SRC = "train.csv"
TMP = "_leak_tmp.csv"

t0 = time.time()
full = M.predict(SRC)
print("full predict s:", round(time.time() - t0, 1), "n =", len(full), full.index[0], full.index[-1],
      "nan:", int(full.isna().sum()), flush=True)

lines = open(SRC, encoding="utf-8").read().splitlines()
header, body = lines[0], lines[1:]
ts = pd.to_datetime([l[:16] for l in body])

cuts = sys.argv[1:] or ["2021-09-13 08:10", "2021-09-21 09:05", "2021-10-26 10:35", "2021-10-28 22:00",
                        "2021-11-04 10:00", "2021-11-08 07:55", "2021-11-15 18:20", "2021-11-16 01:00",
                        "2021-12-09 12:40"]
worst = 0.0
for c in cuts:
    C = pd.Timestamp(c)
    keep = [l for l, t in zip(body, ts) if t < C]
    with open(TMP, "w", encoding="utf-8") as f:
        f.write("\n".join([header] + keep) + "\n")
    p = M.predict(TMP)
    lim = C + pd.Timedelta("45min")
    idx_full = full.index.tz_localize(None)
    idx_p = p.index.tz_localize(None)
    common = idx_p[(idx_p <= lim)].intersection(idx_full)
    a = p.copy(); a.index = idx_p
    b = full.copy(); b.index = idx_full
    d = (a.reindex(common) - b.reindex(common)).abs()
    last_needed = (C + pd.Timedelta("45min")).floor("15min")
    has_last = last_needed in idx_p
    print(f"cut {c}: compared {len(common)} intervals up to {common.max()}, max|diff| = {d.max():.2e}, "
          f"has T={last_needed.time()} -> {has_last}", flush=True)
    worst = max(worst, float(d.max()))

# corruption test: garble every row at/after T-45 and check forecast(T) is unchanged
rng = np.random.default_rng(0)
for c in ["2021-11-09 13:00", "2021-11-12 08:30"]:
    T = pd.Timestamp(c)
    out = [header]
    for l, t in zip(body, ts):
        if t >= T - pd.Timedelta("45min"):
            parts = l.split(",")
            parts[1:] = [str(rng.normal(0, 1000)) for _ in parts[1:]]
            l = ",".join(parts)
        out.append(l)
    with open(TMP, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    p = M.predict(TMP)
    a = p.copy(); a.index = a.index.tz_localize(None)
    b = full.copy(); b.index = b.index.tz_localize(None)
    sel = a.index[a.index <= T]
    d = (a.reindex(sel) - b.reindex(sel)).abs().max()
    print(f"garble from {T - pd.Timedelta('45min')}: forecast({T}) full={b[T]:.4f} garbled={a[T]:.4f}; "
          f"max|diff| for all T'<=T: {d:.2e}", flush=True)
    worst = max(worst, float(d))
os.remove(TMP)
print("WORST", worst)
