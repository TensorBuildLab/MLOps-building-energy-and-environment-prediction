import sys, time, warnings, os, pickle
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
T0 = time.time()
if os.path.exists('work/Xy.pkl'):
    X, y = pickle.load(open('work/Xy.pkl', 'rb'))
else:
    import feats
    d = feats.read_raw('train.csv'); d5 = feats.clean5(d)
    bins, lc = feats.to_bins(d5)
    X, F, b = feats.build_frame(bins, lc)
    y = feats.target_series(d5).reindex(X.index)
    loc = X.index.tz_convert(feats.LOCAL_TZ).tz_localize(None)
    X.index = loc; y.index = loc
    pickle.dump((X, y), open('work/Xy.pkl', 'wb'))
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
print('loaded', time.time() - T0, flush=True)
base = X['f_co2']
ok = y.notna() & base.notna()
cuts = [pd.Timestamp('2023-03-27'), pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08')]
ends = [pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08'), pd.Timestamp('2023-06-02')]
folds = []
for c, e in zip(cuts, ends):
    tr = ok & (X.index + pd.Timedelta('15min') <= c)
    te = ok & (X.index >= c + pd.Timedelta('60min')) & (X.index < e)
    folds.append((tr, te))
store = {}
def run(make, cols, label, delta=True, shrink=None):
    res = []; allp = []; allt = []
    for tr, te in folds:
        m = make()
        tgt = (y - base) if delta else y
        m.fit(X.loc[tr, cols], tgt[tr])
        p = m.predict(X.loc[te, cols])
        p = p + base[te] if delta else p
        res.append(np.sqrt(np.mean((p - y[te]) ** 2)))
        allp.append(p); allt.append(y[te].to_numpy())
    P = np.concatenate(allp); T = np.concatenate(allt)
    store[label] = (P, T)
    print(f'{label:42s} folds ' + ' '.join(f'{r:6.2f}' for r in res) + f' | pooled {np.sqrt(np.mean((P-T)**2)):6.2f}', flush=True)
    return P, T
# persistence per fold
pr = [np.sqrt(np.mean((base[te] - y[te]) ** 2)) for tr, te in folds]
Tall = np.concatenate([y[te].to_numpy() for tr, te in folds]); Ball = np.concatenate([base[te].to_numpy() for tr, te in folds])
print('persistence', ' '.join(f'{r:6.2f}' for r in pr), '| pooled', np.sqrt(np.mean((Ball - Tall) ** 2)), flush=True)
Lall = np.concatenate([X['f_co2_last'][te].to_numpy() for tr, te in folds])
print('persistence last', np.sqrt(np.nanmean((Lall - Tall) ** 2)), flush=True)

small = ['f_co2', 'f_co2_d1', 'f_co2_d4', 'f_co2_above_bg', 'f_co2_min96', 'f_co2_max8', 'f_active', 'f_active_m4', 'f_active_m16', 'f_since_active',
         'f_flow', 'tod', 'weekend', 'act_prev5d_mean', 'act_prev1d_sm']
ridge = lambda a: (lambda: make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=a)))
run(ridge(100), small, 'ridge100 delta small')
run(ridge(1000), small, 'ridge1000 delta small')
hgbs = lambda **kw: (lambda: HistGradientBoostingRegressor(max_iter=120, learning_rate=0.05, max_leaf_nodes=6, min_samples_leaf=80, l2_regularization=5.0, **kw))
run(hgbs(), small, 'HGBsmall delta small')
allc = list(X.columns)
run(hgbs(), allc, 'HGBsmall delta all')
et = lambda: ExtraTreesRegressor(n_estimators=100, min_samples_leaf=30, max_features=0.5, n_jobs=1, random_state=0)
imp = lambda: make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(n_estimators=100, min_samples_leaf=30, max_features=0.5, n_jobs=1, random_state=0))
run(imp, small, 'ET delta small')
run(imp, allc, 'ET delta all')
# blends
for a in (0.3, 0.5, 0.7):
    for k in ('HGBsmall delta small', 'ET delta small', 'ridge100 delta small'):
        P, T = store[k]
        Pb = a * P + (1 - a) * Ball
        print(f'blend {a} {k:30s} pooled {np.sqrt(np.mean((Pb-T)**2)):6.2f}', flush=True)
print('done', time.time() - T0)
