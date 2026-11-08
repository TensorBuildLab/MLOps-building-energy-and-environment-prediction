# Model card: robod-room2-plug_load_energy-1h

## Model

- **Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 0.1}
- **Trained:** 2026-10-29T02:33:14 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `57ef128ece28a677`

## Intended use

Forecast plug-load energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 3.58 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 16:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.310 | 0.370 |
| MAE (kWh) | 0.113 | 0.128 |
| CV(RMSE) % | 232.659 | 277.757 |
| NMBE % | 3.434 | 21.947 |
| R² | 0.342 | 0.063 |

Skill vs time_of_day_profile: 0.16.

90% prediction interval: ±0.261 kWh; it contained 94% of test values.

Main inputs: plug_load_energy (recent history) (44%), calendar (time of day, weekday) (21%), air_temperature (13%), temp_setpoint (10%), indoor_co2 (7%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.162 vs required 0.05 |
| guideline14 | no | CV(RMSE) 226.9%, NMBE 3.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 415 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
