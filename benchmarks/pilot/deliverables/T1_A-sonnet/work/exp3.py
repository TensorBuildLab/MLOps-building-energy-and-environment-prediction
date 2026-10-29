import time; T0=time.time()
from cvlib import *
import warnings; warnings.filterwarnings('ignore')
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
X,y,loc = get_data(step=5)
allf = list(X.columns)
envf = [c for c in allf if c.startswith(('tout','wind','sol'))]
statf = [c for c in allf if c.startswith(('active','window','lighton','light','damper','flow'))]
base_f = [c for c in allf if c not in envf and c not in statf]
print('loaded', time.time()-T0, flush=True)
def et(**kw):
    params = dict(n_estimators=200, min_samples_leaf=20, max_features=0.5, n_jobs=2, random_state=0); params.update(kw)
    return make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(**params))
def hgb(**kw):
    params = dict(max_iter=150, learning_rate=0.05, max_leaf_nodes=12, min_samples_leaf=60, l2_regularization=1.0, random_state=0); params.update(kw)
    return HistGradientBoostingRegressor(**params)
store = {}
def go(name, mk, feats=base_f, **kw):
    t=time.time(); print('==', name, len(feats), flush=True)
    tot,totb,p = run_cv(X,y,loc,mk,feats,True,return_preds=True,train_aligned_only=True,**kw); store[name]=p; print('   time', round(time.time()-t,1), flush=True)
go('ET20', lambda:[et()])
go('ET40', lambda:[et(min_samples_leaf=40)])
go('ET40 mf0.3', lambda:[et(min_samples_leaf=40, max_features=0.3)])
go('ET80', lambda:[et(min_samples_leaf=80)])
go('HGB', lambda:[hgb()])
go('HGB slow', lambda:[hgb(max_iter=300, learning_rate=0.025, max_leaf_nodes=8, min_samples_leaf=100)])
# blends
base = M._baseline(X); ok = y.notna() & base.notna()
aligned = pd.Series((np.asarray(X.index.minute) % 15)==0, index=X.index)
m = pd.Series(False, index=X.index)
for a,b in FOLDS: m |= ok & aligned & (loc>=a) & (loc<b)
def pooled(p): return rmse(y[m], p[m])
for combo in [('ET20','HGB'),('ET40','HGB'),('ET40','HGB slow'),('ET80','HGB slow'),('ET20','ET40','HGB','HGB slow')]:
    p = sum(store[k] for k in combo)/len(combo); print('blend', combo, round(pooled(p),2), flush=True)
p = store['ET40']
for w in (0.0,0.25,0.5,0.75,1.0,1.25):
    q = base + w*(p-base); print('shrink w', w, round(pooled(q),2), flush=True)
# error by hour of day (local)
hr = pd.Series(loc.hour, index=X.index)
pb = 0.5*(store['ET40']+store['HGB slow'])
for h in range(0,24,2):
    mm = m & (hr>=h) & (hr<h+2)
    print('hour', h, 'n', mm.sum(), 'model', round(rmse(y[mm], pb[mm]),1), 'persist', round(rmse(y[mm], base[mm]),1))
print('done', time.time()-T0, flush=True)
