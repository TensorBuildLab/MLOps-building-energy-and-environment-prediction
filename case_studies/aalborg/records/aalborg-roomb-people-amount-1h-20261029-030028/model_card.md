# Model card: aalborg-roomb-people-amount-1h

## Model

- **Task:** forecast RoomB:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-10-29T03:00:28 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `a6ebf9fad9cdf068`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-09-17 22:15:00+02:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomB:Sensor__CO2` (co2, ppm), `RoomB:Sensor__room_temperature` (zone_air_temperature, degC), `RoomB:Room__active` (occupancy_status, binary), `RoomB:Damper__position` (position, %), `RoomB:Radiator__control_signal__motor_valve` (position, %), `RoomB:Light__level__ceiling` (illuminance, lux), `RoomB:Light__on_off_signal` (equipment_status, binary), `RoomB:Window__opened_closed` (equipment_status, binary), `RoomB:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomB:Control__heating_limit` (temperature_setpoint, degC), `RoomB:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 4 count

## Performance (held-out test period, time-ordered)

Test period 2023-09-17 23:30:00+02:00 to 2023-10-24 01:00:00+02:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.291 | 0.360 |
| MAE (count) | 0.141 | 0.118 |
| CV(RMSE) % | 289.809 | 357.818 |
| NMBE % | -17.026 | -1.092 |
| R² | 0.222 | -0.186 |

Skill vs persistence: 0.19.

90% prediction interval: ±0.259 count; it contained 84% of test values.

Main inputs: Ventilation:Fan__air_flow__supply (34%), Ventilation:EL_meter__power (29%), RoomB:People__amount (recent history) (27%), RoomB:Room__active (5%), Outdoor:Temperature_air (3%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.190 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2045 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Oct, Nov, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- Data issues accepted as-is: `missing:RoomB:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
