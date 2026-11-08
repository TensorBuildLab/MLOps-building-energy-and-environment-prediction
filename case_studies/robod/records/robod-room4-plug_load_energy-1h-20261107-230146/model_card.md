# Model card: robod-room4-plug_load_energy-1h

## Model

- **Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}
- **Trained:** 2026-11-07T23:01:46 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `900edcc8cf978a95`, prepared `7e0f3849ba4fe6b5`

## Intended use

Forecast plug-load energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 1.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 0.086 | 0.117 |
| MAE (kWh) | 0.066 | 0.076 |
| CV(RMSE) % | 33.773 | 46.174 |
| NMBE % | 1.949 | -0.254 |
| R² | 0.031 | -0.811 |

Skill vs same_time_last_week: 0.27.

90% prediction interval: ±0.129 kWh; it contained 84% of test values.

Main inputs: plug_load_energy (recent history) (50%), lighting_energy (24%), calendar (time of day, weekday) (7%), supply_air_flow (6%), indoor_relative_humidity (5%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.269 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.4%, NMBE 2.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 674 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
