# Model card: robod-room4-plug_load_energy-1h

## Model

- **Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}
- **Trained:** 2026-10-29T03:48:21 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `186872782d203f28`

## Intended use

Forecast plug-load energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 1.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.087 | 0.086 |
| MAE (kWh) | 0.067 | 0.062 |
| CV(RMSE) % | 34.211 | 33.766 |
| NMBE % | 1.908 | 6.811 |
| R² | 0.006 | 0.032 |

Skill vs time_of_day_profile: -0.01.

90% prediction interval: ±0.129 kWh; it contained 83% of test values.

Main inputs: plug_load_energy (recent history) (51%), lighting_energy (28%), supply_air_flow (11%), indoor_relative_humidity (6%), calendar (time of day, weekday) (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.013 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 13.5%, NMBE 1.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 674 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill -0.01).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
