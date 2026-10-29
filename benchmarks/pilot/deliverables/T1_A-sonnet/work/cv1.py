import sys, time; sys.path.insert(0,'.')
import numpy as np, pandas as pd
import model as M
t0=time.time()
raw = M._read_raw('train.csv')
print('raw', raw.shape, raw.index.min(), raw.index.max(), time.time()-t0)
clean = M._clean(raw)
X, T, B = M.feature_table(clean)
print(X.shape, time.time()-t0)
y = B.reindex(T)
print('nan frac per col'); print(X.isna().mean().round(3).sort_values(ascending=False).head(20))
base = M._baseline(X)
ok = y.notna() & base.notna()
print('n ok', ok.sum())
def rmse(a,b): return float(np.sqrt(np.mean((a-b)**2)))
cal,loc = M._calendar(T)
for name, start, end in [('Mar27-Apr30','2023-03-27','2023-05-01'),('May','2023-05-01','2023-06-01'),('all','2023-02-27','2023-06-01')]:
    m = ok & (loc>=start) & (loc<end)
    print(name, m.sum(), 'persist15', round(rmse(y[m], base[m]),2), 'persist5', round(rmse(y[m], X['co2'][m]),2), 'std', round(float(y[m].std()),2))
