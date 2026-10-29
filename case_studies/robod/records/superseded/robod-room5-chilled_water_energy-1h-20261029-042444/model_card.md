# Model card: robod-room5-chilled_water_energy-1h

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T04:24:44 with bemlops 0.2.0.dev0 (code d64a019)
- **Data fingerprint:** raw `d853493f0f6e2df2`, prepared `616f6047a5bc146d`

## Intended use

Forecast chilled-water energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 23:45:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 15 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-15 01:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.639 | 1.588 |
| MAE (kWh) | 0.350 | 0.996 |
| CV(RMSE) % | 19.939 | 49.508 |
| NMBE % | 0.277 | 30.548 |
| R² | 0.969 | 0.808 |

Skill vs time_of_day_profile: 0.60.

90% prediction interval: ±1.53 kWh; it contained 97% of test values.

Main inputs: calendar (time of day, weekday) (56%), chilled_water_energy (recent history) (40%), global_horizontal_solar_radiation (3%), damper_position (1%), supply_air_temperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.597 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 14.3%, NMBE 0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 668 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
