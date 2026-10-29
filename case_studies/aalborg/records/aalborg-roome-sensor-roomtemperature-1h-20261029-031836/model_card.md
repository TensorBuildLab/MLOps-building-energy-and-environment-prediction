# Model card: aalborg-roome-sensor-roomtemperature-1h

## Model

- **Task:** forecast RoomE:Sensor__room_temperature (zone_air_temperature, degC) 1 h ahead (4 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-10-29T03:18:36 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `9688400cc6709400`

## Intended use

Forecast room temperature one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomE:Sensor__CO2` (co2, ppm), `RoomE:People__amount` (occupancy_count, count), `RoomE:Room__active` (occupancy_status, binary), `RoomE:Damper__position` (position, %), `RoomE:Radiator__control_signal__motor_valve` (position, %), `RoomE:Light__level__ceiling` (illuminance, lux), `RoomE:Light__on_off_signal` (equipment_status, binary), `RoomE:Window__opened_closed` (equipment_status, binary), `RoomE:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomE:Control__heating_limit` (temperature_setpoint, degC), `RoomE:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 19.6 to 27.1 degC

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.475 | 0.234 |
| MAE (degC) | 0.378 | 0.152 |
| CV(RMSE) % | 2.279 | 1.124 |
| NMBE % | -1.591 | 0.005 |
| R² | 0.649 | 0.915 |

Skill vs persistence: -1.03.

90% prediction interval: ±0.318 degC; it contained 47% of test values.

Main inputs: RoomE:Sensor__room_temperature (recent history) (91%), RoomE:Control__setpoint_temperature_global (6%), Ventilation:EL_meter__power (2%), Outdoor:Temperature_air (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -1.028 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4432 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -1.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
