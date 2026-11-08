# Model card: robod-room3-chilled_water_energy-1h

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-10-29T04:41:25 with bemlops 0.2.0.dev0 (code ce6c40d)
- **Data fingerprint:** raw `693e4b3e9c8c9878`, prepared `3abb4002094d669c`

## Intended use

Forecast chilled-water energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-20 23:45:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 1.5 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-21 01:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.077 | 0.150 |
| MAE (kWh) | 0.047 | 0.064 |
| CV(RMSE) % | 36.026 | 70.479 |
| NMBE % | -6.958 | 0.000 |
| R² | 0.903 | 0.631 |

Skill vs persistence: 0.49.

90% prediction interval: ±0.194 kWh; it contained 96% of test values.

Main inputs: chilled_water_energy (recent history) (55%), calendar (time of day, weekday) (28%), supply_air_temperature (9%), global_horizontal_solar_radiation (2%), outdoor_relative_humidity (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.489 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 25.5%, NMBE -7.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 284 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
