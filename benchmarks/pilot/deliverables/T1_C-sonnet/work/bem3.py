import sys, warnings, time
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, bemlops
import feats
# (a) neighbours of a flagged rt "spike"
d = feats.read_raw('train.csv'); d.index = d.index.tz_convert(feats.LOCAL_TZ).tz_localize(None)
d = d[~d.index.duplicated(keep='first')]
print(d['rt']['2023-03-05 12:35':'2023-03-05 13:05'].round(2).tolist())
# (b) raw frame with tz-aware strings straight into Project
raw = pd.read_csv('train.csv', sep=';', encoding='utf-8-sig', na_values=['#N/A'])
raw.columns = [c.encode('ascii', 'ignore').decode() for c in raw.columns]
cols = {'RoomB:Sensor__CO2': {'quantity': 'co2', 'unit': 'ppm', 'flat_ok': True},
        'RoomB:Sensor__room_temperature': 'zone_air_temperature [degC]',
        'Outdoor:Wind__velocity': 'wind_speed [m/s]'}
for fmt in ['%Y-%m-%dT%H:%M:%S%z', None]:
    try:
        p = bemlops.Project(raw, target='RoomB:Sensor__CO2', columns=cols, horizon='1h', timestamp='timestamp', timestamp_format=fmt)
        r = p.check_data()
        print('FORMAT', fmt, '->', str(r)[:1800])
    except Exception as e:
        print('FORMAT', fmt, 'EXC', type(e).__name__, str(e)[:400])
# (c) local naive string timestamps WITH duplicates / reversed block kept
raw2 = raw.copy(); raw2['timestamp'] = raw2['timestamp'].str[:19]
try:
    p = bemlops.Project(raw2, target='RoomB:Sensor__CO2', columns=cols, horizon='1h', timestamp='timestamp', timestamp_format='%Y-%m-%dT%H:%M:%S')
    print('NAIVE-LOCAL', str(p.check_data())[:2500])
except Exception as e:
    print('NAIVE-LOCAL EXC', type(e).__name__, str(e)[:400])
print('done')
