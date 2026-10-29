import sys, time, warnings, pickle
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
T0 = time.time()
X, y = pickle.load(open('work/Xy.pkl', 'rb'))
base = X['f_co2']; ok = y.notna() & base.notna()
cuts = [pd.Timestamp('2023-03-27'), pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08')]
ends = [pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08'), pd.Timestamp('2023-06-02')]
folds = []
for c, e in zip(cuts, ends):
    tr = ok & (X.index + pd.Timedelta('15min') <= c)
    te = ok & (X.index >= c + pd.Timedelta('60min')) & (X.index < e)
    folds.append((tr, te))
drop = ['f_oat', 'f_sol', 'f_wind', 'f_vent_el', 'f_dh', 'f_hc', 'f_sat', 'f_rt', 'f_lux', 'f_lux_m4', 'f_oat_d8', 'f_window']
mid = [c for c in X.columns if c not in drop]
mid2 = [c for c in mid if c not in ('f_light',)]
print(len(mid), flush=True)
store = {}
def run(make, cols, label):
    res = []; P = []; T = []
    for tr, te in folds:
        m = make(); m.fit(X.loc[tr, cols], (y - base)[tr])
        p = m.predict(X.loc[te, cols]) + base[te].to_numpy()
        res.append(np.sqrt(np.mean((p - y[te]) ** 2))); P.append(p); T.append(y[te].to_numpy())
    store[label] = (np.concatenate(P), np.concatenate(T))
    print(f'{label:36s} folds ' + ' '.join(f'{r:6.2f}' for r in res) + f' | pooled {np.sqrt(np.mean((store[label][0]-store[label][1])**2)):6.2f}  t={time.time()-T0:.0f}', flush=True)
et = lambda msl, mf: (lambda: make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(n_estimators=120, min_samples_leaf=msl, max_features=mf, n_jobs=1, random_state=0)))
hgb = lambda: HistGradientBoostingRegressor(max_iter=120, learning_rate=0.05, max_leaf_nodes=6, min_samples_leaf=80, l2_regularization=5.0, random_state=0)
run(et(30, 0.5), mid, 'ET30 mid')
run(et(15, 0.5), mid, 'ET15 mid')
run(et(60, 0.5), mid, 'ET60 mid')
run(et(30, 0.3), mid, 'ET30 mf.3 mid')
run(hgb, mid, 'HGB mid')
run(et(30, 0.5), mid2, 'ET30 mid no light')
for a, b in [('ET30 mid', 'HGB mid'), ('ET15 mid', 'HGB mid')]:
    P = 0.5 * store[a][0] + 0.5 * store[b][0]; T = store[a][1]
    print(f'avg {a}+{b}: {np.sqrt(np.mean((P-T)**2)):6.2f}', flush=True)
print('done', time.time() - T0, flush=True)
