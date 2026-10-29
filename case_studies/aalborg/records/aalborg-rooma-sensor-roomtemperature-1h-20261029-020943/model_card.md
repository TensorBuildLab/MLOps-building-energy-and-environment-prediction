# Model card: aalborg-rooma-sensor-roomtemperature-1h

## Model

- **Task:** forecast RoomA:Sensor__room_temperature (zone_air_temperature, degC) 1 h ahead (4 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-10-29T02:09:43 with bemlops 0.2.0.dev0 (code e85edf1)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `86e2b485eece819f`

## Intended use

Forecast room temperature one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:15:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomA:Sensor__CO2` (co2, ppm), `RoomA:People__amount` (occupancy_count, count), `RoomA:Room__active` (occupancy_status, binary), `RoomA:Damper__position` (position, %), `RoomA:Radiator__control_signal__motor_valve` (position, %), `RoomA:Light__level__ceiling` (illuminance, lux), `RoomA:Light__on_off_signal` (equipment_status, binary), `RoomA:Window__opened_closed` (equipment_status, binary), `RoomA:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomA:Control__heating_limit` (temperature_setpoint, degC), `RoomA:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 16.8 to 29.9 degC

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:30:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.355 | 0.382 |
| MAE (degC) | 0.215 | 0.194 |
| CV(RMSE) % | 1.695 | 1.825 |
| NMBE % | 0.313 | 0.001 |
| R² | 0.843 | 0.818 |

Skill vs persistence: 0.07.

90% prediction interval: ±0.622 degC; it contained 93% of test values.

Main inputs: RoomA:Sensor__room_temperature (recent history) (88%), Ventilation:Fan__air_flow__supply (4%), RoomA:Room__active (2%), calendar (time of day, weekday) (2%), RoomA:Control__cooling_limit (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.071 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4431 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
