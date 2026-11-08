# Model card: robod-room5-pm25-30min

## Model

- **Task:** forecast pm2.5 (pm25, ug/m3) 30 min ahead (2 step(s) of 15 min)
- **Model:** random_forest {'model__min_samples_leaf': 10, 'model__max_features': 0.6, 'model__max_depth': 16}
- **Trained:** 2026-10-29T04:08:00 with bemlops 0.2.0.dev0 (code a3aca57)
- **Data fingerprint:** raw `d853493f0f6e2df2`, prepared `b85e8ea1f142788e`

## Intended use

Forecast PM2.5 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 1 to 16 ug/m3

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 22:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ug/m3) | 0.479 | 0.528 |
| MAE (ug/m3) | 0.299 | 0.322 |
| CV(RMSE) % | 11.574 | 12.748 |
| NMBE % | 0.199 | 0.141 |
| R² | 0.920 | 0.903 |

Skill vs persistence: 0.09.

90% prediction interval: ±0.688 ug/m3; it contained 91% of test values.

Main inputs: pm2.5 (recent history) (97%), calendar (time of day, weekday) (2%), illuminance (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.092 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 675 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
