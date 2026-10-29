import sys, os; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
import numpy as np, pandas as pd
import model as M
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

def get_data(path=None, step=5):
    path = path or os.path.join(ROOT,'train.csv')
    raw = M._read_raw(path)
    clean = M._clean(raw)
    X, T, y = M.feature_table(clean, step)
    cal, loc = M._calendar(T)
    return X, y, loc

FOLDS = [('2023-04-03','2023-04-17'),('2023-04-17','2023-05-01'),('2023-05-01','2023-05-15'),('2023-05-15','2023-06-01')]

def rmse(a,b): return float(np.sqrt(np.mean((np.asarray(a)-np.asarray(b))**2)))

def run_cv(X, y, loc, make_models, feats, residual=True, folds=FOLDS, winsor=None, verbose=True, return_preds=False, train_aligned_only=False, sample_weight=None):
    base = M._baseline(X)
    ok = y.notna() & base.notna()
    aligned = pd.Series((np.asarray(X.index.minute) % 15)==0, index=X.index)
    preds = pd.Series(np.nan, index=X.index)
    res=[]
    for (a,b) in folds:
        te = ok & aligned & (loc>=a) & (loc<b)
        tr = ok & (loc< pd.Timestamp(a) - pd.Timedelta(hours=1))
        if train_aligned_only: tr = tr & aligned
        Xtr = X.loc[tr, feats]; ytr = y[tr] - (base[tr] if residual else 0)
        if winsor is not None:
            ytr = ytr.clip(-winsor, winsor) if residual else ytr.clip(upper=winsor)
        p = np.zeros(te.sum())
        ms = make_models()
        for m in ms:
            m.fit(Xtr, ytr)
            p += m.predict(X.loc[te, feats]) / len(ms)
        p = p + (base[te].to_numpy() if residual else 0)
        preds[te] = p
        r = rmse(y[te], p); rb = rmse(y[te], base[te])
        res.append((a, te.sum(), r, rb))
    allm = preds.notna()
    tot = rmse(y[allm], preds[allm]); totb = rmse(y[allm], base[allm])
    if verbose:
        print('  ' + ' | '.join(f'{a[5:]} {r:.1f}/{rb:.1f}' for a,n,r,rb in res) + f' || POOLED {tot:.2f} (persist {totb:.2f})', flush=True)
    if return_preds: return tot, totb, preds
    return tot, totb
