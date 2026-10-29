"""Causality check: truncating or corrupting the file at cutoff C must not change any
forecast for intervals T with T - 45min <= C."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import numpy as np, pandas as pd
import model as M

CSV = os.path.join(ROOT, "train.csv")
t0 = time.time()
full = M.predict(CSV)
print("full predict %.1fs, n=%d, NaN=%d, range %s .. %s" % (time.time() - t0, len(full), full.isna().sum(),
                                                            full.index.min(), full.index.max()), flush=True)

with open(CSV, "r", encoding="utf-8-sig") as f:
    lines = f.read().splitlines()
header, body = lines[0], lines[1:]
ts = pd.to_datetime(pd.Series([l.split(";", 1)[0] for l in body]), utc=True, format="%Y-%m-%dT%H:%M:%S%z")

cutoffs = [pd.Timestamp(x, tz="UTC") for x in sys.argv[1:]] or [
    pd.Timestamp("2023-04-18 06:55", tz="UTC"), pd.Timestamp("2023-05-25 10:10", tz="UTC")]
worst = 0.0
for C in cutoffs:
    # 1) truncation: keep rows with timestamp < C (original row order kept)
    keep = [l for l, t in zip(body, ts) if t < C]
    p = os.path.join(HERE, "_trunc.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join([header] + keep) + "\n")
    pt = M.predict(p)
    lim = C + pd.Timedelta("45min")
    common = full.index[(full.index <= lim)].intersection(pt.index)
    diff = (full[common] - pt[common]).abs().max()
    missing = full.index[(full.index <= lim)].difference(pt.index)
    print(f"trunc  C={C}: compared {len(common)} intervals up to {lim}, max|diff|={diff:.3g}, "
          f"missing={len(missing)}, last pred index={pt.index.max()}", flush=True)
    worst = max(worst, diff)
    # 2) corruption: rows with timestamp >= C get garbage values
    rng = np.random.default_rng(0)
    out = []
    for l, t in zip(body, ts):
        if t >= C:
            parts = l.split(";")
            parts[1:] = [str(rng.uniform(-50, 3000)) for _ in parts[1:]]
            l = ";".join(parts)
        out.append(l)
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join([header] + out) + "\n")
    pc = M.predict(p)
    common = full.index[full.index <= lim]
    diff = (full[common] - pc[common]).abs().max()
    nxt = full.index[(full.index > lim)][:3]
    print(f"corrupt C={C}: max|diff| up to T={lim}: {diff:.3g}; first changed after: "
          f"{(full[nxt] - pc[nxt]).abs().round(1).tolist()}", flush=True)
    worst = max(worst, diff)
os.remove(os.path.join(HERE, "_trunc.csv"))
print("WORST", worst)
