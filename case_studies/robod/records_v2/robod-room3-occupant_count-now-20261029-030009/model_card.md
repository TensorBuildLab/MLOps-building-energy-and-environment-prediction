# Model card: robod-room3-occupant_count-now

## Model

- **Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-10-29T03:00:09 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `e8caed10850b801f`, prepared `7e9ef27740fbe459`

## Intended use

Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 12.7 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 2.110 | 2.249 |
| MAE (count) | 1.251 | 1.390 |
| CV(RMSE) % | 527.944 | 562.600 |
| NMBE % | -300.957 | -341.831 |
| R² | -4.393 | -5.125 |

Skill vs time_of_day_profile: 0.06.

90% prediction interval: ±1.95 count; it contained 71% of test values.

Main inputs: damper_position (87%), global_horizontal_solar_radiation (4%), dry_bulb_temp (3%), sound_pressure_level (2%), supply_air_flow (2%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.062 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 419 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
