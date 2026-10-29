# Model card: robod-room3-indoor_co2-30min

## Model

- **Task:** forecast indoor_co2 (co2, ppm) 30 min ahead (2 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}
- **Trained:** 2026-10-29T02:37:41 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `e8caed10850b801f`, prepared `7fb74e851d3bbe62`

## Intended use

Forecast CO2 30 min ahead to pre-ventilate.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 14:45:00+08:00 (train + validation)
- **Inputs:** `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 400 to 833 ppm

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 10.757 | 11.172 |
| MAE (ppm) | 6.266 | 5.854 |
| CV(RMSE) % | 2.336 | 2.426 |
| NMBE % | 0.076 | 0.074 |
| R² | 0.918 | 0.911 |

Skill vs persistence: 0.04.

90% prediction interval: ±17.7 ppm; it contained 95% of test values.

Main inputs: indoor_co2 (recent history) (96%), calendar (time of day, weekday) (2%), sound_pressure_level (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.037 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 416 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.04).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
