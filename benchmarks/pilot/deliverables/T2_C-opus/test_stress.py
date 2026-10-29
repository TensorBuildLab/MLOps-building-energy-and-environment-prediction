"""Robustness: a longer file (train + two synthetic 'later' copies shifted by 14 and 28 weeks, with
extra corruptions) must run quickly, return finite forecasts and stay causal."""
import sys, time, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model
raw = pd.read_csv(HERE / "train.csv", dtype=str)
ts = pd.to_datetime(raw["timestamp"], format="%Y-%m-%d %H:%M %z")
parts = [raw]
rng = np.random.default_rng(0)
for k, weeks in enumerate([14, 28]):
    c = raw.copy()
    c["timestamp"] = (ts + pd.Timedelta(weeks=weeks)).dt.strftime("%Y-%m-%d %H:%M +08:00")
    n = len(c)
    i = rng.choice(n, 30, replace=False); c.loc[i, "chilled_water_energy [kWh]"] = "-999"
    i = rng.choice(n, 30, replace=False); c.loc[i, "dry_bulb_temp [Celsius]"] = "OFFLINE"
    i = rng.choice(n, 30, replace=False); c.loc[i, "ahu_fan_speed [Hz]"] = "N/A"
    db = pd.to_numeric(c["dry_bulb_temp [Celsius]"], errors="coerce")
    sl = slice(2000, 4000)
    c.loc[c.index[sl], "dry_bulb_temp [Celsius]"] = (db.iloc[sl] * 9 / 5 + 32).round(2).astype(str)
    if k == 1:
        c = c.drop(columns=[]).iloc[::-1]  # whole block reversed
    parts.append(c)
big = pd.concat(parts, ignore_index=True)
with tempfile.TemporaryDirectory(dir=HERE) as td:
    f = Path(td) / "big.csv"; big.to_csv(f, index=False)
    t = time.time(); out = model.predict(str(f)); dt = time.time() - t
    print(f"{len(big)} raw rows -> {len(out)} forecasts in {dt:.1f} s; NaN {out.isna().sum()}, "
          f"min {out.min():.3f}, max {out.max():.3f}, range {out.index.min()} .. {out.index.max()}")
    cut = pd.Timestamp("2022-03-29 13:20")
    loc = pd.to_datetime(big["timestamp"], format="%Y-%m-%d %H:%M %z").dt.tz_convert("Asia/Singapore").dt.tz_localize(None)
    f2 = Path(td) / "cut.csv"; big[loc < cut].to_csv(f2, index=False)
    part = model.predict(str(f2))
    idx = out.index[out.index <= cut + pd.Timedelta("45min")].intersection(part.index)
    print("causality on the synthetic later data: max |diff| =", float((part[idx] - out[idx]).abs().max()), "over", len(idx))
    d = out["2022-03-28":"2022-03-29"]
    print(d.between_time("07:30", "09:00").round(2).to_dict())
