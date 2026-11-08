# Model card: robod-room5-occupant_count-now

## Model

- **Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T04:21:06 with bemlops 0.2.0.dev0 (code a3aca57)
- **Data fingerprint:** raw `d853493f0f6e2df2`, prepared `892a5e92b8b5d3dd`

## Intended use

Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 15.7 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 22:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 0.971 | 2.063 |
| MAE (count) | 0.554 | 1.355 |
| CV(RMSE) % | 134.488 | 285.664 |
| NMBE % | -46.310 | -183.473 |
| R² | 0.114 | -2.996 |

Skill vs time_of_day_profile: 0.53.

90% prediction interval: ±3.42 count; it contained 98% of test values.

Main inputs: calendar (time of day, weekday) (36%), pm2.5 (23%), sound_pressure_level (12%), indoor_relative_humidity (9%), indoor_co2 (6%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.529 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 678 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
