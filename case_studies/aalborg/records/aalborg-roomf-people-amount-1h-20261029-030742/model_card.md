# Model card: aalborg-roomf-people-amount-1h

## Model

- **Task:** forecast RoomF:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T03:07:42 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `5ddedcd3f5f1dffd`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-10-21 02:45:00+02:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomF:Sensor__CO2` (co2, ppm), `RoomF:Sensor__room_temperature` (zone_air_temperature, degC), `RoomF:Room__active` (occupancy_status, binary), `RoomF:Damper__position` (position, %), `RoomF:Radiator__control_signal__motor_valve` (position, %), `RoomF:Light__level__ceiling` (illuminance, lux), `RoomF:Light__on_off_signal` (equipment_status, binary), `RoomF:Window__opened_closed` (equipment_status, binary), `RoomF:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomF:Control__heating_limit` (temperature_setpoint, degC), `RoomF:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 4 count

## Performance (held-out test period, time-ordered)

Test period 2023-10-21 04:00:00+02:00 to 2023-11-16 09:30:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.345 | 0.308 |
| MAE (count) | 0.240 | 0.089 |
| CV(RMSE) % | 366.640 | 327.482 |
| NMBE % | -168.481 | 1.686 |
| R² | -0.080 | 0.139 |

Skill vs persistence: -0.12.

90% prediction interval: ±0.385 count; it contained 85% of test values.

Main inputs: RoomF:People__amount (recent history) (56%), Ventilation:EL_meter__power (23%), RoomF:Control__heating_limit (10%), RoomF:Room__active (3%), Ventilation:Fan__air_flow__supply (3%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.120 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2523 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Nov, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -0.12).
- Data issues accepted as-is: `missing:RoomF:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
