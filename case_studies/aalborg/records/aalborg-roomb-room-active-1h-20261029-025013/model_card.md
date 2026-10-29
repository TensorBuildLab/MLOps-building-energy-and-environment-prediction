# Model card: aalborg-roomb-room-active-1h

## Model

- **Task:** forecast yes/no RoomB:Room__active (occupancy_status, binary) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:50:13 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `4aed5cd18402c2a6`

## Intended use

Forecast whether the room will be in use one hour ahead (motion sensor).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomB:Sensor__CO2` (co2, ppm), `RoomB:Sensor__room_temperature` (zone_air_temperature, degC), `RoomB:People__amount` (occupancy_count, count), `RoomB:Damper__position` (position, %), `RoomB:Radiator__control_signal__motor_valve` (position, %), `RoomB:Light__level__ceiling` (illuminance, lux), `RoomB:Light__on_off_signal` (equipment_status, binary), `RoomB:Window__opened_closed` (equipment_status, binary), `RoomB:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomB:Control__heating_limit` (temperature_setpoint, degC), `RoomB:Control__cooling_limit` (temperature_setpoint, degC)
- **Share of 'yes' in training:** 0.19

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.054 | 0.072 |
| Accuracy | 0.926 | 0.922 |
| Balanced accuracy | 0.827 | 0.828 |
| F1 | 0.709 | 0.702 |
| ROC AUC | 0.955 | 0.859 |

Skill vs persistence: 0.25.

Main inputs: RoomB:Room__active (recent history) (71%), calendar (time of day, weekday) (20%), RoomB:Light__on_off_signal (3%), RoomB:Sensor__room_temperature (1%), Outdoor:Temperature_air (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.248 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4432 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
