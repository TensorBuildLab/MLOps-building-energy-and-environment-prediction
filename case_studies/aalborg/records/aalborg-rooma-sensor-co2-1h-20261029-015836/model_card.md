# Model card: aalborg-rooma-sensor-co2-1h

## Model

- **Task:** forecast RoomA:Sensor__CO2 (co2, ppm) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T01:58:36 with bemlops 0.2.0.dev0 (code e85edf1)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `bcc383851c71f5f6`

## Intended use

Forecast room CO2 one hour ahead for demand-controlled ventilation.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:15:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomA:Sensor__room_temperature` (zone_air_temperature, degC), `RoomA:People__amount` (occupancy_count, count), `RoomA:Room__active` (occupancy_status, binary), `RoomA:Damper__position` (position, %), `RoomA:Radiator__control_signal__motor_valve` (position, %), `RoomA:Light__level__ceiling` (illuminance, lux), `RoomA:Light__on_off_signal` (equipment_status, binary), `RoomA:Window__opened_closed` (equipment_status, binary), `RoomA:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomA:Control__heating_limit` (temperature_setpoint, degC), `RoomA:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 366 to 919 ppm

## Performance (held-out test period, time-ordered)

Test period 2023-11-15 20:30:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 28.688 | 34.935 |
| MAE (ppm) | 14.614 | 14.059 |
| CV(RMSE) % | 6.245 | 7.605 |
| NMBE % | -0.062 | 0.005 |
| R² | 0.855 | 0.785 |

Skill vs persistence: 0.18.

90% prediction interval: ±52.6 ppm; it contained 92% of test values.

Main inputs: RoomA:Sensor__CO2 (recent history) (88%), calendar (time of day, weekday) (7%), RoomA:Room__active (4%), Ventilation:Fan__air_flow__supply (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.179 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4428 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
