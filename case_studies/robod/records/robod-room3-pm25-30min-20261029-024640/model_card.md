# Model card: robod-room3-pm25-30min

## Model

- **Task:** forecast pm2.5 (pm25, ug/m3) 30 min ahead (2 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:46:40 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `e8caed10850b801f`, prepared `043a89b651640ec7`

## Intended use

Forecast PM2.5 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 14:45:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0.148 to 45.5 ug/m3

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ug/m3) | 0.472 | 0.404 |
| MAE (ug/m3) | 0.325 | 0.211 |
| CV(RMSE) % | 16.445 | 14.079 |
| NMBE % | -4.919 | 0.296 |
| R² | 0.511 | 0.642 |

Skill vs persistence: -0.17.

90% prediction interval: ±0.774 ug/m3; it contained 91% of test values.

Main inputs: pm2.5 (recent history) (67%), calendar (time of day, weekday) (10%), chilled_water_energy (6%), supply_air_flow (5%), air_temperature (5%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.168 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 416 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -0.17).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
