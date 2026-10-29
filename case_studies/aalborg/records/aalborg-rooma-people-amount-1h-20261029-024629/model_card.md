# Model card: aalborg-rooma-people-amount-1h

## Model

- **Task:** forecast RoomA:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:46:29 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `b7e89c892fdf3b26`

## Intended use

Forecast the number of people in the room one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 00:00:00+01:00 to 2023-10-27 06:30:00+02:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Heating:DH__power` (thermal_power, W), `Ventilation:HC__power` (thermal_power, W), `RoomA:Sensor__CO2` (co2, ppm), `RoomA:Sensor__room_temperature` (zone_air_temperature, degC), `RoomA:Room__active` (occupancy_status, binary), `RoomA:Damper__position` (position, %), `RoomA:Radiator__control_signal__motor_valve` (position, %), `RoomA:Light__level__ceiling` (illuminance, lux), `RoomA:Light__on_off_signal` (equipment_status, binary), `RoomA:Window__opened_closed` (equipment_status, binary), `RoomA:Control__setpoint_temperature_global` (temperature_setpoint, degC), `RoomA:Control__heating_limit` (temperature_setpoint, degC), `RoomA:Control__cooling_limit` (temperature_setpoint, degC)
- **Target range seen:** 0 to 8.67 count

## Performance (held-out test period, time-ordered)

Test period 2023-10-27 07:45:00+02:00 to 2023-11-21 17:30:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.595 | 0.713 |
| MAE (count) | 0.259 | 0.259 |
| CV(RMSE) % | 145.567 | 174.327 |
| NMBE % | 15.726 | 0.234 |
| R² | 0.576 | 0.392 |

Skill vs persistence: 0.16.

90% prediction interval: ±0.987 count; it contained 91% of test values.

Main inputs: RoomA:People__amount (recent history) (60%), calendar (time of day, weekday) (33%), RoomA:Room__active (1%), RoomA:Sensor__CO2 (1%), Ventilation:Sensor__air_temperature__supply (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.165 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2444 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Nov, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- Data issues accepted as-is: `missing:RoomA:People__amount` (Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.)

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
