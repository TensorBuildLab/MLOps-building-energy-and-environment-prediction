# Model card: robod-room4-air_temperature-30min

## Model

- **Task:** forecast air_temperature (zone_air_temperature, degC) 30 min ahead (2 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 0.1}
- **Trained:** 2026-10-29T03:15:09 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `e34811be9ddfab1c`

## Intended use

Forecast room temperature 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 25.1 to 28.5 degC

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.170 | 0.227 |
| MAE (degC) | 0.097 | 0.116 |
| CV(RMSE) % | 0.616 | 0.821 |
| NMBE % | 0.008 | -0.010 |
| R² | 0.788 | 0.623 |

Skill vs persistence: 0.25.

90% prediction interval: ±0.226 degC; it contained 92% of test values.

Main inputs: air_temperature (recent history) (89%), calendar (time of day, weekday) (8%), illuminance (1%), indoor_relative_humidity (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.250 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 675 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
