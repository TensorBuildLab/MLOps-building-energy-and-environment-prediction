# Model card: robod-room3-occupant_presence-30min

## Model

- **Task:** forecast yes/no occupant_presence (occupancy_status, binary) 30 min ahead (2 step(s) of 15 min)
- **Model:** random_forest {'model__min_samples_leaf': 10, 'model__max_features': 0.6, 'model__max_depth': 16}
- **Trained:** 2026-10-29T02:56:09 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `e8caed10850b801f`, prepared `d97da2176b0f51a5`

## Intended use

Forecast whether the room is occupied 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Share of 'yes' in training:** 0.43

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.045 | 0.041 |
| Accuracy | 0.962 | 0.959 |
| Balanced accuracy | 0.943 | 0.945 |
| F1 | 0.918 | 0.914 |
| ROC AUC | 0.991 | 0.947 |

Skill vs persistence: -0.09.

Main inputs: occupant_presence (recent history) (44%), calendar (time of day, weekday) (25%), occupant_count (25%), damper_position (3%), plug_load_energy (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.092 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 417 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -0.09).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
