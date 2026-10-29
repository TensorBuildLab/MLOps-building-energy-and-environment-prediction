import sys, os, time, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
HERE = os.path.abspath('.')
sys.path.insert(0, HERE)
import model as M

t = time.time()
full = M.predict(os.path.join(HERE, 'train.csv'))
print('full predict: %.1fs' % (time.time() - t), full.shape, full.index.min(), full.index.max(), 'NaN:', int(full.isna().sum()), 'dup idx:', int(full.index.duplicated().sum()))
print(full.describe().round(1).to_string())

raw = open('train.csv', encoding='utf-8-sig').read().splitlines()
hdr, rows = raw[0], raw[1:]
def trunc(cut_local):
    keep = [r for r in rows if r[:19] < cut_local]
    p = os.path.join(HERE, 'work', 'trunc.csv')
    open(p, 'w', encoding='utf-8-sig').write('\n'.join([hdr] + keep) + '\n')
    return p, keep[-1][:25]
bad = 0
for cut in ['2023-03-30T14:05:00', '2023-04-20T10:25:00', '2023-05-15T08:45:00', '2023-05-29T17:10:00']:
    p, last = trunc(cut)
    t = time.time()
    pr = M.predict(p)
    common = pr.index.intersection(full.index)
    diff = (pr[common] - full[common]).abs().max()
    # last forecast index vs file end
    print(f'cut {cut}: last row {last}; trunc idx {pr.index.min()}..{pr.index.max()} n={len(pr)} common={len(common)} max|diff|={diff:.3e} ({time.time()-t:.1f}s)')
    if not (diff < 1e-6): bad += 1
print('LEAK-CONSISTENCY FAILURES:', bad)
# the forecast for T must be independent of data at or after T-45 min: perturb data after a cut and check

# ---- perturbation test: corrupt every row with timestamp >= T0, forecasts for T <= T0+45min must not change ----
rawdf = pd.read_csv('train.csv', sep=';', dtype=str, encoding='utf-8-sig')
loc_ts = pd.to_datetime(rawdf['timestamp'].str[:19])
rng = np.random.default_rng(1)
pert_fail = 0
for T0s in ['2023-04-12 09:20:00', '2023-05-03 13:45:00', '2023-05-22 16:00:00']:
    T0 = pd.Timestamp(T0s)
    d2 = rawdf.copy()
    after = (loc_ts >= T0).to_numpy()
    before_idx = np.flatnonzero(~after)
    payload_cols = [c for c in d2.columns if c != 'timestamp']
    src = rng.choice(before_idx, size=int(after.sum()))
    d2.loc[after, payload_cols] = d2.iloc[src][payload_cols].to_numpy()
    p = os.path.join(HERE, 'work', 'pert.csv')
    d2.to_csv(p, sep=';', index=False, encoding='utf-8-sig')
    pr = M.predict(p)
    allowed = pr.index <= T0 + pd.Timedelta('45min')
    d_ok = (pr[allowed] - full.reindex(pr.index[allowed])).abs().max()
    later = pr.index >= T0 + pd.Timedelta('60min')
    d_later = (pr[later] - full.reindex(pr.index[later])).abs().max()
    print(f'perturb from {T0}: max|diff| for T<=T0+45min = {d_ok:.3e} (must be 0); for T>=T0+60min = {d_later:.2f} (sensitivity)')
    if not (d_ok < 1e-9): pert_fail += 1
print('PERTURBATION FAILURES:', pert_fail)
