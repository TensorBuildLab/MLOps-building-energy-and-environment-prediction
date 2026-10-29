"""Checks for predict(): runtime, output shape, accuracy on train.csv, and that every forecast
only depends on data with timestamps before T - 45 min (truncate the file and compare)."""
import sys
import time
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model  # noqa: E402

csv = HERE / "train.csv"
t = time.time()
full = model.predict(str(csv))
print(f"predict(train.csv): {time.time() - t:.1f} s, {len(full)} forecasts, "
      f"{full.index.min()} .. {full.index.max()}, NaN {full.isna().sum()}, freq {full.index.freq}")
assert isinstance(full.index, pd.DatetimeIndex) and full.index.is_monotonic_increasing and full.index.is_unique

# accuracy against the 15-min target (raw, faults not masked, and masked)
raw15 = model.to_15min(model.clean(model.read_raw(str(csv))), mask_target_faults=False)[model.TARGET]
cln15 = model.to_15min(model.clean(model.read_raw(str(csv))), mask_target_faults=True)[model.TARGET]
for name, y in [("clean target", cln15), ("raw target (faults kept)", raw15)]:
    m = y.notna() & full.reindex(y.index).notna()
    e = full.reindex(y.index)[m] - y[m]
    print(f"in-sample RMSE vs {name}: {np.sqrt((e ** 2).mean()):.3f} kWh on {m.sum()} intervals")

# causality: truncate the raw file at several cut times and compare
lines = csv.read_text().splitlines()
header, rows = lines[0], lines[1:]
stamps = pd.to_datetime([r.split(",")[0] for r in rows], format="%Y-%m-%d %H:%M %z").tz_convert(
    "Asia/Singapore").tz_localize(None)
cuts = sys.argv[1:] or ["2021-09-08 07:40", "2021-10-27 08:05", "2021-11-09 12:10", "2021-11-12 18:20",
                        "2021-11-16 17:55", "2021-12-09 08:35"]
worst = 0.0
with tempfile.TemporaryDirectory(dir=HERE) as td:
    for c in cuts:
        C = pd.Timestamp(c)
        keep = [r for r, s in zip(rows, stamps) if s < C]
        f = Path(td) / "cut.csv"
        f.write_text("\n".join([header] + keep) + "\n")
        part = model.predict(str(f))
        # forecasts for T may use data with timestamps < T - 45 min; all of it is in the cut file
        # whenever T - 45 min <= C
        idx = full.index[full.index <= C + pd.Timedelta("45min")]
        common = idx.intersection(part.index)
        missing = len(idx) - len(common)
        d = (part.reindex(common) - full.reindex(common)).abs()
        worst = max(worst, float(d.max()))
        print(f"cut {c}: compared {len(common)} forecasts (missing in cut output: {missing}); "
              f"max |diff| = {d.max():.2e}; last compared {common.max()}; cut output ends {part.index.max()}")
        if d.max() > 0:
            print(d[d > 1e-9].tail(10))
print("CAUSALITY", "OK" if worst == 0 else "FAILED", worst)
