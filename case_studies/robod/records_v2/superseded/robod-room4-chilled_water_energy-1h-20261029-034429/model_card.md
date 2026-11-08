# Model card: robod-room4-chilled_water_energy-1h

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** random_forest {'model__min_samples_leaf': 10, 'model__max_features': 0.6, 'model__max_depth': 16}
- **Trained:** 2026-10-29T03:44:29 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `e447f58bb3c81ee2`

## Intended use

Forecast chilled-water energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 23:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 10.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-15 00:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.735 | 0.982 |
| MAE (kWh) | 0.358 | 0.530 |
| CV(RMSE) % | 63.287 | 84.641 |
| NMBE % | 16.580 | 40.253 |
| R² | 0.764 | 0.578 |

Skill vs time_of_day_profile: 0.25.

90% prediction interval: ±1.14 kWh; it contained 91% of test values.

Main inputs: calendar (time of day, weekday) (38%), chilled_water_energy (recent history) (30%), global_horizontal_solar_radiation (27%), supply_air_temperature (3%), damper_position (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.252 vs required 0.05 |
| guideline14 | no | CV(RMSE) 55.4%, NMBE 16.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 670 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
