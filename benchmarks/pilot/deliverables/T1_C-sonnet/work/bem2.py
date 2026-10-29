import sys, warnings, time, os
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, bemlops
import feats
t0 = time.time()

# ---- Cleaned 5-min frame in local (wall-clock) time, built with the same code as model.py -----------
d = feats.read_raw('train.csv')
d5 = feats.clean5(d)
loc = d5.copy()
loc.index = loc.index.tz_convert(feats.LOCAL_TZ).tz_localize(None)
loc = loc[~loc.index.duplicated(keep='first')]
loc['sol'] = loc[['sol_e', 'sol_s', 'sol_w']].mean(axis=1)

columns = {
    'co2': {'quantity': 'co2', 'unit': 'ppm', 'flat_ok': True},
    'oat': 'outdoor_air_temperature [degC]',
    'rt': 'zone_air_temperature [degC]',
    'active': 'occupancy_status',
    'light': 'equipment_status',
    'flow': 'airflow [m3/h]',
    'damper': 'position [%]',
    'sol': 'solar_irradiance [W/m2]',
}
p = bemlops.Project(loc, target='co2', columns=columns, horizon='1h',
                    name='co2_forecast_1h_roomB', intended_use='1 h ahead CO2 forecast for ventilation planning')
rep = p.check_data()
print(rep)
p.note('co2 is change-of-value logged (deadband ~50 ppm): flat stretches are normal, declared flat_ok. '
       'Room temperature switched to degF on 2023-05-12 10:00; converted per sample (>45 -> degF) before bemlops. '
       'Duplicate day (2023-05-25) and a reversed block (2023-04-24) removed in the loader. -999 CO2 and outdoor temperature spikes masked.')
p.prepare(freq='15min')
for s in p.prepare_log:
    print(s)
res = p.fit(models=['ridge', 'gbm'], n_iter=4)
print(res)
folder = p.save_run('work/bemruns')
print('saved', folder)
print('elapsed', time.time() - t0)
