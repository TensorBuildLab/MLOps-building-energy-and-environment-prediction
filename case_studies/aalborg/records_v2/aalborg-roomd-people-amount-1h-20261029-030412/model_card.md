# Model card: aalborg-roomd-people-amount-1h

## Model

- **Task:** forecast RoomD:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T03:04:12 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `3bacffe076b8350c`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-11-13 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomD:Sensor__CO2` (co2, ppm), `RoomD:Sensor__room_temperature` (zone_air_temperature, degC), `RoomD:Room__active` (occupancy_status, binary), `RoomD:Damper__position` (position, %), `RoomD:Radiator__control_signal__motor_valve` (position, %), `RoomD:Light__level__ceiling` (illuminance, lux), `RoomD:Light__on_off_signal` (equipment_status, binary), `RoomD:Window__opened_closed` (equipment_status, binary), `RoomD:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomD:Control__heating_limit` (temperature_setpoint, degC), `RoomD:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 4.67 count

## Performance (held-out test period, time-ordered)

Test period 2023-11-13 20:15:00+01:00 to 2023-12-11 17:15:00+01:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 0.507 | 0.501 |
| MAE (count) | 0.273 | 0.259 |
| CV(RMSE) % | 133.988 | 132.534 |
| NMBE % | 0.838 | 7.270 |
| R² | 0.522 | 0.532 |

Skill vs time_of_day_profile: -0.01.

90% prediction interval: ±0.741 count; it contained 87% of test values.

Main inputs: calendar (time of day, weekday) (49%), RoomD:People__amount (recent history) (43%), RoomD:Light__on_off_signal (4%), RoomD:Room__active (1%), Ventilation:EL_meter__power (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.011 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2677 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill -0.01).
- Data issues accepted as-is: `missing:RoomD:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
