import sys, time, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import feats, pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge

d = feats.read_raw('train.csv'); d5 = feats.clean5(d)
bins, lc = feats.to_bins(d5)
X, F, b = feats.build_frame(bins, lc)
y = feats.target_series(d5).reindex(X.index)
loc = X.index.tz_convert(feats.LOCAL_TZ).tz_localize(None)
X.index = loc; y.index = loc
base = X['f_co2']
ok = y.notna() & base.notna()

cuts = [pd.Timestamp('2023-03-27'), pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08')]
ends = [pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08'), pd.Timestamp('2023-06-02')]

def run(make, cols, delta=True, label=''):
    res = []; allp = []; allt = []; allb=[]
    for c, e in zip(cuts, ends):
        tr = ok & (X.index + pd.Timedelta('15min') <= c)
        te = ok & (X.index >= c + pd.Timedelta('60min')) & (X.index < e)
        m = make()
        tgt = (y - base) if delta else y
        m.fit(X.loc[tr, cols], tgt[tr])
        p = m.predict(X.loc[te, cols])
        p = p + base[te] if delta else p
        res.append(np.sqrt(np.mean((p - y[te]) ** 2)))
        allp.append(p); allt.append(y[te]); allb.append(base[te])
    P = np.concatenate(allp); T = np.concatenate(allt); B = np.concatenate(allb)
    print(f'{label:40s} folds ' + ' '.join(f'{r:6.2f}' for r in res) + f' | pooled {np.sqrt(np.mean((P-T)**2)):6.2f}  persist {np.sqrt(np.mean((B-T)**2)):6.2f}')
    return P, T

allc = list(X.columns)
hgb = lambda **kw: (lambda: HistGradientBoostingRegressor(max_iter=300, learning_rate=0.04, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, **kw))
run(hgb(), allc, True, 'HGB delta all')
run(hgb(), allc, False, 'HGB direct all')
co2cols = [c for c in allc if c.startswith('f_co2')] + ['tod','dow','weekend']
run(hgb(), co2cols, True, 'HGB delta co2+time')
noprev = [c for c in allc if not c.startswith('act_prev') and c not in ('co2_prev1d','flow_prev1d')]
run(hgb(), noprev, True, 'HGB delta no schedule memory')
nowin = [c for c in allc if c not in ('f_window',)]
run(hgb(), nowin, True, 'HGB delta no window')
