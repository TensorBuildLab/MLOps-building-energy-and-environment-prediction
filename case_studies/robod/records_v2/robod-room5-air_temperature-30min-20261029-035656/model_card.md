# Model card: robod-room5-air_temperature-30min

## Model

- **Task:** forecast air_temperature (zone_air_temperature, degC) 30 min ahead (2 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-10-29T03:56:56 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `d853493f0f6e2df2`, prepared `e19e0c5cae04cf88`

## Intended use

Forecast room temperature 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 26.7 to 30.1 degC

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.123 | 0.175 |
| MAE (degC) | 0.080 | 0.099 |
| CV(RMSE) % | 0.434 | 0.617 |
| NMBE % | -0.014 | 0.008 |
| R² | 0.965 | 0.929 |

Skill vs persistence: 0.30.

90% prediction interval: ±0.177 degC; it contained 89% of test values.

Main inputs: air_temperature (recent history) (89%), calendar (time of day, weekday) (7%), illuminance (3%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.296 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 676 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
