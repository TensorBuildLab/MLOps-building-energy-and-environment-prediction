# Model card: aalborg-roome-room-active-1h

## Model

- **Task:** forecast yes/no RoomE:Room__active (occupancy_status, binary) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T03:01:21 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `072ef792a2c591bd`

## Intended use

Forecast whether the room will be in use one hour ahead (motion sensor).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomE:Sensor__CO2` (co2, ppm), `RoomE:Sensor__room_temperature` (zone_air_temperature, degC), `RoomE:People__amount` (occupancy_count, count), `RoomE:Damper__position` (position, %), `RoomE:Radiator__control_signal__motor_valve` (position, %), `RoomE:Light__level__ceiling` (illuminance, lux), `RoomE:Light__on_off_signal` (equipment_status, binary), `RoomE:Window__opened_closed` (equipment_status, binary), `RoomE:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomE:Control__heating_limit` (temperature_setpoint, degC), `RoomE:Control__cooling_limit` (temperature_setpoint, degC)
- **Share of 'yes' in training:** 0.18

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.059 | 0.085 |
| Accuracy | 0.917 | 0.907 |
| Balanced accuracy | 0.873 | 0.805 |
| F1 | 0.730 | 0.665 |
| ROC AUC | 0.955 | 0.835 |

Skill vs persistence: 0.31.

Main inputs: calendar (time of day, weekday) (65%), RoomE:Room__active (recent history) (32%), Outdoor:Solar__direct_radiation__south_façade (2%), Ventilation:EL_meter__power (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.306 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4432 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
