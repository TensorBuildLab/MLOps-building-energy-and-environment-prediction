import sys, time, warnings, pickle
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
X, y = pickle.load(open('work/Xy.pkl', 'rb'))
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
base = X['f_co2']; ok = y.notna() & base.notna()
cuts = [pd.Timestamp('2023-03-27'), pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08')]
ends = [pd.Timestamp('2023-04-17'), pd.Timestamp('2023-05-08'), pd.Timestamp('2023-06-02')]
rows = []
for c, e in zip(cuts, ends):
    tr = ok & (X.index + pd.Timedelta('15min') <= c)
    te = ok & (X.index >= c + pd.Timedelta('60min')) & (X.index < e)
    m = make_pipeline(SimpleImputer(strategy='median'), ExtraTreesRegressor(n_estimators=100, min_samples_leaf=30, max_features=0.5, n_jobs=1, random_state=0))
    m.fit(X[tr], (y - base)[tr])
    p = m.predict(X[te]) + base[te]
    df = pd.DataFrame({'y': y[te], 'base': base[te], 'p': p, 'act': X.loc[te, 'f_active'], 'tod': X.loc[te, 'tod'], 'dow': X.loc[te, 'dow'], 'hold': X.loc[te,'f_co2_hold']})
    rows.append(df)
R = pd.concat(rows)
R['e_p'] = R.p - R.y; R['e_b'] = R.base - R.y
R['hr'] = R.tod.astype(int)
g = R.groupby('hr').agg(n=('y', 'size'), sse_b=('e_b', lambda s: (s**2).sum()), sse_p=('e_p', lambda s: (s**2).sum()))
g['share_b'] = g.sse_b / g.sse_b.sum(); g['rmse_b'] = np.sqrt(g.sse_b / g.n); g['rmse_p'] = np.sqrt(g.sse_p / g.n)
print(g.round(2).to_string())
R['wk'] = (R.dow >= 5)
print(R.groupby('wk').apply(lambda d: pd.Series({'n': len(d), 'rmse_b': np.sqrt((d.e_b**2).mean()), 'rmse_p': np.sqrt((d.e_p**2).mean())})))
print(R.groupby(R.act.round(1)).apply(lambda d: pd.Series({'n': len(d), 'rmse_b': np.sqrt((d.e_b**2).mean()), 'rmse_p': np.sqrt((d.e_p**2).mean())})))
# largest errors
big = R.reindex(R.e_p.abs().sort_values(ascending=False).index).head(25)
print(big.round(1).to_string())
print('total sse share of top 2%:', (R.e_p**2).sort_values(ascending=False).head(int(len(R)*0.02)).sum() / (R.e_p**2).sum())
