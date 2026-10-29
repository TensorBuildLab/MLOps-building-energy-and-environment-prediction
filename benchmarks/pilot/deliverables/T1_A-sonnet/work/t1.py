import time; t=time.time()
from cvlib import *
print('import', time.time()-t); t=time.time()
X,y,loc = get_data(); print('data', time.time()-t); t=time.time()
base = M._baseline(X); ok=y.notna()&base.notna()
tr = ok & (loc<'2023-04-17')
m = HistGradientBoostingRegressor(max_iter=50, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40, random_state=0)
m.fit(X.loc[tr], (y-base)[tr]); print('hgb fit 50it', time.time()-t, tr.sum())
