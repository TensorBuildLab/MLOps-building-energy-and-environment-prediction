# Model card: aalborg-roome-sensor-co2-1h

## Model

- **Task:** forecast RoomE:Sensor__CO2 (co2, ppm) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T03:14:07 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `b17e66b13510ca5b`

## Intended use

Forecast room CO2 one hour ahead for demand-controlled ventilation.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:15:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomE:Sensor__room_temperature` (zone_air_temperature, degC), `RoomE:People__amount` (occupancy_count, count), `RoomE:Room__active` (occupancy_status, binary), `RoomE:Damper__position` (position, %), `RoomE:Radiator__control_signal__motor_valve` (position, %), `RoomE:Light__level__ceiling` (illuminance, lux), `RoomE:Light__on_off_signal` (equipment_status, binary), `RoomE:Window__opened_closed` (equipment_status, binary), `RoomE:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomE:Control__heating_limit` (temperature_setpoint, degC), `RoomE:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 375 to 991 ppm

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:30:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 22.555 | 26.479 |
| MAE (ppm) | 10.114 | 9.617 |
| CV(RMSE) % | 4.921 | 5.777 |
| NMBE % | -0.252 | 0.006 |
| R² | 0.793 | 0.715 |

Skill vs persistence: 0.15.

90% prediction interval: ±48.3 ppm; it contained 94% of test values.

Main inputs: RoomE:Sensor__CO2 (recent history) (86%), RoomE:Light__on_off_signal (5%), calendar (time of day, weekday) (3%), Ventilation:Fan__air_flow__supply (2%), RoomE:Room__active (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.148 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4430 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
