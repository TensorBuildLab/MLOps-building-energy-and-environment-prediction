"""Check that predict() is causal and fast.

1. Runs predict() on the full train.csv (timed).
2. Writes truncated copies of train.csv (rows with timestamp < cutoff, original
   row order and text kept) and checks that every forecast for an interval T
   with T - 45 min <= cutoff is identical to the forecast from the full file.
"""
import sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import pandas as pd

t0 = time.time()
import model as m  # noqa: E402

full = m.predict(str(HERE / "train.csv"))
print(f"full predict: {time.time() - t0:.1f} s, {len(full)} forecasts, "
      f"{int(full.isna().sum())} NaN, index tz={full.index.tz}, "
      f"{full.index.min()} .. {full.index.max()}")
assert isinstance(full.index, pd.DatetimeIndex)
assert full.index.is_unique and full.index.is_monotonic_increasing

lines = (HERE / "train.csv").read_text(encoding="utf-8-sig").splitlines()
header, body = lines[0], lines[1:]
stamps = pd.to_datetime(pd.Series([b.split(";", 1)[0] for b in body]), utc=True)

cutoffs = sys.argv[1:] or [
    "2023-03-26 02:10+01:00",   # around the spring DST jump
    "2023-04-02 08:00+02:00",   # inside the 12 h gap
    "2023-04-24 14:07+02:00",   # inside the block exported in reverse order
    "2023-05-12 10:00+02:00",   # just after room temperature switched to degF
    "2023-05-25 10:43+02:00",   # inside the day exported twice
    "2023-05-31 17:22+02:00",   # mid-afternoon, not on a 15-min boundary
]
tmp = HERE / "_trunc_tmp.csv"
worst = 0.0
for c in cutoffs:
    cut = pd.Timestamp(c).tz_convert("UTC")
    keep = [b for b, s in zip(body, stamps) if s < cut]
    tmp.write_text("﻿" + "\n".join([header] + keep) + "\n", encoding="utf-8")
    t1 = time.time()
    part = m.predict(str(tmp))
    lim = cut + pd.Timedelta("45min")
    idx = part.index[part.index <= lim]
    a, b = part.loc[idx], full.reindex(idx)
    diff = float(np.nanmax(np.abs(a.values - b.values))) if len(idx) else 0.0
    extra = part.index[part.index > lim]
    worst = max(worst, diff)
    print(f"cutoff {c}: {len(idx)} comparable forecasts, max |diff| = {diff:.3g} ppm, "
          f"NaN mismatch = {int((a.isna() != b.isna()).sum())}, "
          f"forecasts beyond cutoff+45min = {len(extra)}, {time.time() - t1:.1f} s")
tmp.unlink(missing_ok=True)
print("WORST", worst, "total", round(time.time() - t0, 1), "s")
