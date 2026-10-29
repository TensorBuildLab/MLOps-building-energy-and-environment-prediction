# Model card: aalborg-roomc-sensor-roomtemperature-1h

## Model

- **Task:** forecast RoomC:Sensor__room_temperature (zone_air_temperature, degC) 1 h ahead (4 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T03:15:07 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `2c4e266526c9a5fa`

## Intended use

Forecast room temperature one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomC:Sensor__CO2` (co2, ppm), `RoomC:People__amount` (occupancy_count, count), `RoomC:Room__active` (occupancy_status, binary), `RoomC:Damper__position` (position, %), `RoomC:Radiator__control_signal__motor_valve` (position, %), `RoomC:Light__level__ceiling` (illuminance, lux), `RoomC:Light__on_off_signal` (equipment_status, binary), `RoomC:Window__opened_closed` (equipment_status, binary), `RoomC:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomC:Control__heating_limit` (temperature_setpoint, degC), `RoomC:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 20.2 to 29.3 degC

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.167 | 0.167 |
| MAE (degC) | 0.103 | 0.103 |
| CV(RMSE) % | 0.798 | 0.798 |
| NMBE % | 0.000 | 0.000 |
| R² | 0.926 | 0.926 |

Skill vs persistence: 0.00.

90% prediction interval: ±0.227 degC; it contained 90% of test values.

Main inputs: RoomC:Sensor__room_temperature (recent history) (100%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4432 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
