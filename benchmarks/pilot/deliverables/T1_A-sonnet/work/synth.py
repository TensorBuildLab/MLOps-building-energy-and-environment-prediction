import sys, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
import model as M
CSV = os.path.join(ROOT, 'train.csv')
txt = pd.read_csv(CSV, sep=';', dtype=str, encoding='utf-8-sig', keep_default_na=False)
ts = pd.to_datetime(txt.iloc[:,0], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
# later period: shift by 150 days -> crosses the Oct 29 2023 fall-back
sh = txt.copy()
new_ts = (ts + pd.Timedelta(days=160)).dt.tz_convert(ZoneInfo('Europe/Copenhagen'))
sh.iloc[:,0] = new_ts.dt.strftime('%Y-%m-%dT%H:%M:%S%z')
sh = sh[(ts >= ts.min()).to_numpy()]
# keep it unsorted/dup like the original; add some garbage tokens
sh.iloc[100:110, 11] = 'Bad'
sh.iloc[500:520, 11] = '-999'
full = pd.concat([txt, sh], ignore_index=True)
tmp = os.path.join(ROOT, 'work', '_synth.csv')
full.to_csv(tmp, sep=';', index=False, encoding='utf-8-sig')
print(full.iloc[:,0].iloc[[0, -1]].tolist(), len(full))
t = time.time(); p = M.predict(tmp); print('predict time', round(time.time()-t,1), 'n', len(p), 'unique', p.index.is_unique, 'monotonic', p.index.is_monotonic_increasing, 'nan', int(p.isna().sum()))
print(p['2023-10-29 00:30':'2023-10-29 04:00'].round(1).to_string())
print(p.index.min(), p.index.max(), p.min(), p.max())
os.remove(tmp)
