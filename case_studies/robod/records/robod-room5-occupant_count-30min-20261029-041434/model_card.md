# Model card: robod-room5-occupant_count-30min

## Model

- **Task:** forecast occupant_count (occupancy_count, count) 30 min ahead (2 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}
- **Trained:** 2026-10-29T04:14:34 with bemlops 0.2.0.dev0 (code a3aca57)
- **Data fingerprint:** raw `d853493f0f6e2df2`, prepared `cb14e0963d50a699`

## Intended use

Forecast the number of people 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 15.7 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.486 | 0.535 |
| MAE (count) | 0.249 | 0.191 |
| CV(RMSE) % | 67.084 | 73.814 |
| NMBE % | -21.525 | -0.846 |
| R² | 0.779 | 0.732 |

Skill vs persistence: 0.09.

90% prediction interval: ±1.57 count; it contained 98% of test values.

Main inputs: occupant_count (recent history) (57%), calendar (time of day, weekday) (29%), occupant_presence (4%), lighting_energy (4%), sound_pressure_level (2%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.091 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 676 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
