# Model card: robod-room4-occupant_presence-30min

## Model

- **Task:** forecast yes/no occupant_presence (occupancy_status, binary) 30 min ahead (2 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T03:38:43 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `c4e63a6827d3a927`

## Intended use

Forecast whether the room is occupied 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:15:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Share of 'yes' in training:** 0.66

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 23:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.046 | 0.046 |
| Accuracy | 0.947 | 0.947 |
| Balanced accuracy | 0.944 | 0.944 |
| F1 | 0.955 | 0.955 |
| ROC AUC | 0.958 | 0.958 |

Skill vs persistence: 0.00.

Main inputs: occupant_presence (recent history) (100%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 676 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
