# Model card: aalborg-roomc-people-amount-1h

## Model

- **Task:** forecast RoomC:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T03:02:35 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `4f027d0fefd9c843`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-11-13 01:45:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomC:Sensor__CO2` (co2, ppm), `RoomC:Sensor__room_temperature` (zone_air_temperature, degC), `RoomC:Room__active` (occupancy_status, binary), `RoomC:Damper__position` (position, %), `RoomC:Radiator__control_signal__motor_valve` (position, %), `RoomC:Light__level__ceiling` (illuminance, lux), `RoomC:Light__on_off_signal` (equipment_status, binary), `RoomC:Window__opened_closed` (equipment_status, binary), `RoomC:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomC:Control__heating_limit` (temperature_setpoint, degC), `RoomC:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 4 count

## Performance (held-out test period, time-ordered)

Test period 2023-11-13 03:00:00+01:00 to 2023-12-13 18:30:00+01:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 0.204 | 0.209 |
| MAE (count) | 0.102 | 0.088 |
| CV(RMSE) % | 337.490 | 345.899 |
| NMBE % | -75.570 | -5.978 |
| R² | 0.254 | 0.216 |

Skill vs time_of_day_profile: 0.02.

90% prediction interval: ±0.204 count; it contained 84% of test values.

Main inputs: calendar (time of day, weekday) (47%), RoomC:Light__on_off_signal (15%), RoomC:People__amount (recent history) (13%), RoomC:Sensor__room_temperature (11%), RoomC:Room__active (6%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.024 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2943 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill 0.02).
- Data issues accepted as-is: `missing:RoomC:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
