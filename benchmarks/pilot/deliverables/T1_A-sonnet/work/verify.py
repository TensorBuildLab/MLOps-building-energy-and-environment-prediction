import sys, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
import numpy as np, pandas as pd
t0 = time.time()
import model as M
print('import', round(time.time()-t0,1), flush=True)
CSV = os.path.join(ROOT, 'train.csv')
t = time.time(); full = M.predict(CSV); dt = time.time()-t
print('predict(train.csv) took', round(dt,1), 's; n =', len(full), 'type', type(full.index).__name__, 'tz', full.index.tz, flush=True)
print(full.index.min(), full.index.max(), 'nan', int(full.isna().sum()), 'unique idx', full.index.is_unique, 'min/max', full.min(), full.max())
print(full.head(3)); print(full.tail(3))
# in-sample check vs realised bins
raw = M._read_raw(CSV); clean = M._clean(raw)
X, T, y = M.feature_table(clean, 15)
yy = pd.Series(y.to_numpy(), index=M._local_naive(T))
yy = yy[~yy.index.duplicated()]
j = pd.concat([full.rename('p'), yy.rename('y')], axis=1).dropna()
print('in-sample RMSE (not an estimate of future error):', round(float(np.sqrt(((j.p-j.y)**2).mean())),2), 'n', len(j))

# raw text for corruption tests
txt = pd.read_csv(CSV, sep=';', dtype=str, encoding='utf-8-sig', keep_default_na=False)
ts = pd.to_datetime(txt.iloc[:,0], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
tmp = os.path.join(ROOT, 'work', '_tmp_test.csv')
def write(df): df.to_csv(tmp, sep=';', index=False, encoding='utf-8-sig')
rng = np.random.default_rng(0)
cuts = pd.to_datetime(['2023-04-12 09:05','2023-04-26 13:20','2023-05-03 07:50','2023-05-17 15:35','2023-05-24 10:10'], utc=True)
bad = 0
for cut in cuts:
    # (a) truncated file: rows with timestamp < cut only  -> forecasts for T with T-45min <= cut (i.e. T <= cut+45min)
    tr = txt[ts < cut]
    write(tr)
    p_tr = M.predict(tmp)
    # (b) future rows (>= cut) replaced by garbage
    pt = txt.copy()
    m = (ts >= cut).to_numpy()
    for c in pt.columns[1:]:
        vals = pd.to_numeric(pt.loc[m, c], errors='coerce')
        pt.loc[m, c] = (vals * rng.uniform(0.2, 5, size=m.sum()) + rng.normal(0, 50, size=m.sum())).round(3).astype(str)
    write(pt)
    p_pt = M.predict(tmp)
    # forecasts for intervals T with T - 45 min <= cut : T <= cut + 45 min (local naive index)
    lim = M._local_naive(pd.DatetimeIndex([cut + pd.Timedelta(minutes=45)]))[0]
    idx = full.index[full.index <= lim]
    a = full.loc[idx]; b = p_tr.reindex(idx); c = p_pt.reindex(idx)
    d1 = np.nanmax(np.abs(a.to_numpy()-b.to_numpy())); d2 = np.nanmax(np.abs(a.to_numpy()-c.to_numpy()))
    print(f'cut {cut}: compared {len(idx)} forecasts (trunc has {int(b.notna().sum())} non-null); max|full-trunc|={d1:.3g}  max|full-garbage|={d2:.3g}  last common T={idx[-1]}', flush=True)
    bad += (d1 > 1e-6) or (d2 > 1e-6) or int(b.notna().sum()) < len(idx)
print('LEAK TEST', 'FAILED' if bad else 'PASSED', ' total time', round(time.time()-t0,1))
os.remove(tmp)
