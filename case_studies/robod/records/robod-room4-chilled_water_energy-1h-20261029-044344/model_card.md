# Model card: robod-room4-chilled_water_energy-1h

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** random_forest {'model__min_samples_leaf': 10, 'model__max_features': 0.6, 'model__max_depth': 16}
- **Trained:** 2026-10-29T04:43:44 with bemlops 0.2.0.dev0 (code ce6c40d)
- **Data fingerprint:** raw `900edcc8cf978a95`, prepared `13cb3c79bdf79c82`

## Intended use

Forecast chilled-water energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-15 02:45:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 10.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-15 04:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.736 | 0.974 |
| MAE (kWh) | 0.363 | 0.528 |
| CV(RMSE) % | 62.068 | 82.133 |
| NMBE % | 16.228 | 38.719 |
| R² | 0.765 | 0.589 |

Skill vs time_of_day_profile: 0.24.

90% prediction interval: ±1.13 kWh; it contained 90% of test values.

Main inputs: calendar (time of day, weekday) (38%), chilled_water_energy (recent history) (29%), global_horizontal_solar_radiation (29%), supply_air_temperature (3%), supply_air_flow (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.244 vs required 0.05 |
| guideline14 | no | CV(RMSE) 54.1%, NMBE 16.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 656 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
