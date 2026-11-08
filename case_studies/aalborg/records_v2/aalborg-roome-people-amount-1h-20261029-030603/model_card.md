# Model card: aalborg-roome-people-amount-1h

## Model

- **Task:** forecast RoomE:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** time_of_day_profile 
- **Trained:** 2026-10-29T03:06:03 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `3299ec8b38db05e2`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-10-15 19:15:00+02:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomE:Sensor__CO2` (co2, ppm), `RoomE:Sensor__room_temperature` (zone_air_temperature, degC), `RoomE:Room__active` (occupancy_status, binary), `RoomE:Damper__position` (position, %), `RoomE:Radiator__control_signal__motor_valve` (position, %), `RoomE:Light__level__ceiling` (illuminance, lux), `RoomE:Light__on_off_signal` (equipment_status, binary), `RoomE:Window__opened_closed` (equipment_status, binary), `RoomE:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomE:Control__heating_limit` (temperature_setpoint, degC), `RoomE:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 4 count

## Performance (held-out test period, time-ordered)

Test period 2023-10-15 20:30:00+02:00 to 2023-11-10 16:45:00+01:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 0.298 | 0.298 |
| MAE (count) | 0.140 | 0.140 |
| CV(RMSE) % | 149.796 | 149.796 |
| NMBE % | 29.000 | 29.000 |
| R² | 0.489 | 0.489 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±0.51 count; it contained 91% of test values.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2464 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Nov, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.
- Data issues accepted as-is: `missing:RoomE:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
