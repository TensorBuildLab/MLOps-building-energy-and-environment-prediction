import sys, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import feats, pandas as pd, numpy as np, bemlops

# Load RAW (no cleaning other than parsing/sorting/dedup) so that bemlops sees the real problems
d = feats.read_raw('train.csv')
d.index = d.index.tz_convert(feats.LOCAL_TZ).tz_localize(None)
d = d[~d.index.duplicated(keep='first')]
print(d.shape)
columns = {
    'co2': 'co2 [ppm]',
    'oat': 'outdoor_air_temperature [degC]',
    'rt': 'zone_air_temperature [degC]',
    'active': 'occupancy_status',
    'flow': 'airflow [m3/h]',
    'damper': 'position [%]',
    'light': 'equipment_status',
    'lux': 'illuminance [lux]',
    'window': 'equipment_status',
    'wind': 'wind_speed [m/s]',
}
p = bemlops.Project(d, target='co2', columns=columns, horizon='1h')
rep = p.check_data()
print(rep)
