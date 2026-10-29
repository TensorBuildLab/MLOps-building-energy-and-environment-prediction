import time; T0=time.time()
from cvlib import *
import warnings; warnings.filterwarnings('ignore')
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
X,y,loc = get_data(step=5)
allf = list(X.columns)
print('loaded', time.time()-T0, X.shape, flush=True)
envf = [c for c in allf if c.startswith(('tout','wind','sol'))]
statf = [c for c in allf if c.startswith(('active','window','lighton','light','damper','flow'))]
noenv = [c for c in allf if c not in envf]
base_f = [c for c in noenv if c not in statf]
def hgb(**kw):
    params = dict(max_iter=150, learning_rate=0.05, max_leaf_nodes=12, min_samples_leaf=60, l2_regularization=1.0, random_state=0); params.update(kw)
    return lambda: [HistGradientBoostingRegressor(**params)]
def et(**kw):
    params = dict(n_estimators=150, min_samples_leaf=20, max_features=0.5, n_jobs=1, random_state=0); params.update(kw)
    return lambda: [make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(**params))]
def go(name, mk, feats, residual=True, **kw):
    t=time.time(); print('==', name, len(feats), flush=True)
    r = run_cv(X,y,loc,mk,feats,residual,**kw); print('   time', round(time.time()-t,1), flush=True); return r
go('ET aug5 base_f leaf20', et(), base_f)
go('ET aug5 base_f leaf10', et(min_samples_leaf=10), base_f)
go('ET aug5 noenv leaf20', et(), noenv)
go('ET aug5 allf leaf20', et(), allf)
go('ET aligned-only base_f leaf10', et(min_samples_leaf=10), base_f, train_aligned_only=True)
go('HGB aug5 base_f', hgb(), base_f)
go('HGB aug5 noenv', hgb(), noenv)
go('HGB aug5 base_f slow', hgb(max_iter=300, learning_rate=0.025, max_leaf_nodes=8, min_samples_leaf=100), base_f)
print('done', time.time()-T0, flush=True)
