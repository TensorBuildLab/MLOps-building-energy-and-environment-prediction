import time; T0=time.time()
from cvlib import *
import warnings; warnings.filterwarnings('ignore')
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
X,y,loc = get_data()
allf = list(X.columns)
print('loaded', time.time()-T0, flush=True)
def hgb(**kw):
    params = dict(max_iter=150, learning_rate=0.05, max_leaf_nodes=12, min_samples_leaf=40, l2_regularization=1.0, random_state=0)
    params.update(kw)
    return lambda: [HistGradientBoostingRegressor(**params)]
envf = [c for c in allf if c.startswith(('tout','wind','sol'))]
statf = [c for c in allf if c.startswith(('active','window','lighton','light','damper','flow'))]
noenv = [c for c in allf if c not in envf]
noenv_nostat = [c for c in noenv if c not in statf]
co2_cal = [c for c in allf if c.startswith(('co2','B_','dchg')) or c in ('tod','tod_sin','tod_cos','dow','hol','hol_prev','hol_next','workday','prev_workday')]
def go(name, mk, feats, residual=True, **kw):
    t=time.time(); print('==', name, len(feats), flush=True)
    r = run_cv(X,y,loc,mk,feats,residual,**kw); print('   time', round(time.time()-t,1), flush=True)
go('hgb residual all', hgb(), allf)
go('hgb direct all', hgb(), allf, False)
go('hgb residual noenv', hgb(), noenv)
go('hgb residual noenv_nostat', hgb(), noenv_nostat)
go('hgb residual co2+cal', hgb(), co2_cal)
go('hgb residual all winsor150', hgb(), allf, True, winsor=150)
go('hgb residual all shallow', hgb(max_leaf_nodes=6, min_samples_leaf=80, max_iter=200), allf)
def ridge(): return [make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=300))]
go('ridge residual noenv', ridge, noenv)
def et(): return [ExtraTreesRegressor(n_estimators=150, min_samples_leaf=10, max_features=0.5, n_jobs=1, random_state=0)]
def et_pipe(): return [make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(n_estimators=150, min_samples_leaf=10, max_features=0.5, n_jobs=1, random_state=0))]
go('ET residual noenv', et_pipe, noenv)
print('done', time.time()-T0, flush=True)
