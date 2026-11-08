# Model card: robod-room4-indoor_co2-30min

## Model

- **Task:** forecast indoor_co2 (co2, ppm) 30 min ahead (2 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 31, 'max_iter': 100, 'learning_rate': 0.05, 'l2_regularization': 0.0}
- **Trained:** 2026-10-29T03:08:35 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `b95328ebfd5a0b15`

## Intended use

Forecast CO2 30 min ahead to pre-ventilate.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:00:00+08:00 (train + validation)
- **Inputs:** `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 400 to 756 ppm

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 22:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 9.449 | 12.996 |
| MAE (ppm) | 6.895 | 8.964 |
| CV(RMSE) % | 2.104 | 2.894 |
| NMBE % | -0.162 | -0.072 |
| R² | 0.930 | 0.868 |

Skill vs persistence: 0.27.

90% prediction interval: ±17.3 ppm; it contained 93% of test values.

Main inputs: indoor_co2 (recent history) (93%), calendar (time of day, weekday) (6%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.273 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 675 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
