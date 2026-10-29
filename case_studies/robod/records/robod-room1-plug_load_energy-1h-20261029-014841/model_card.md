# Model card: robod-room1-plug_load_energy-1h

## Model

- **Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T01:48:41 with bemlops 0.2.0.dev0 (code b253e59)
- **Data fingerprint:** raw `f3fcdd4922287b47`, prepared `06c758b9fd28072a`

## Intended use

Forecast plug-load energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 8.36 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 16:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.702 | 0.864 |
| MAE (kWh) | 0.360 | 0.298 |
| CV(RMSE) % | 225.468 | 277.725 |
| NMBE % | -5.820 | 21.943 |
| R² | 0.382 | 0.063 |

Skill vs time_of_day_profile: 0.19.

90% prediction interval: ±0.511 kWh; it contained 82% of test values.

Main inputs: plug_load_energy (recent history) (36%), air_temperature (21%), pm2.5 (15%), calendar (time of day, weekday) (13%), global_horizontal_solar_radiation (5%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.188 vs required 0.05 |
| guideline14 | no | CV(RMSE) 217.9%, NMBE -5.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 415 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
