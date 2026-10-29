# Model card: aalborg-roomb-sensor-co2-1h

## Model

- **Task:** forecast RoomB:Sensor__CO2 (co2, ppm) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T03:07:55 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `00fc54c11b2eec7a`

## Intended use

Forecast room CO2 one hour ahead for demand-controlled ventilation.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomB:Sensor__room_temperature` (zone_air_temperature, degC), `RoomB:People__amount` (occupancy_count, count), `RoomB:Room__active` (occupancy_status, binary), `RoomB:Damper__position` (position, %), `RoomB:Radiator__control_signal__motor_valve` (position, %), `RoomB:Light__level__ceiling` (illuminance, lux), `RoomB:Light__on_off_signal` (equipment_status, binary), `RoomB:Window__opened_closed` (equipment_status, binary), `RoomB:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomB:Control__heating_limit` (temperature_setpoint, degC), `RoomB:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 382 to 1.02e+03 ppm

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 25.499 | 27.574 |
| MAE (ppm) | 13.001 | 10.752 |
| CV(RMSE) % | 5.487 | 5.933 |
| NMBE % | 0.144 | 0.003 |
| R² | 0.837 | 0.810 |

Skill vs persistence: 0.08.

90% prediction interval: ±46.8 ppm; it contained 92% of test values.

Main inputs: RoomB:Sensor__CO2 (recent history) (91%), RoomB:Room__active (6%), calendar (time of day, weekday) (2%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.075 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4430 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
