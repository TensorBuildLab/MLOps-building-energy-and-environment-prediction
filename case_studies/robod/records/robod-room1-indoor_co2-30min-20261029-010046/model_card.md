# Model card: robod-room1-indoor_co2-30min

## Model

- **Task:** forecast indoor_co2 (co2, ppm) 30 min ahead (2 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T01:00:46 with bemlops 0.2.0.dev0 (code b253e59)
- **Data fingerprint:** raw `f3fcdd4922287b47`, prepared `68c595cdb079db92`

## Intended use

Forecast CO2 30 min ahead to pre-ventilate.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:15:00+08:00 (train + validation)
- **Inputs:** `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 400 to 745 ppm

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 16:00:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 20.254 | 20.254 |
| MAE (ppm) | 9.571 | 9.571 |
| CV(RMSE) % | 4.377 | 4.377 |
| NMBE % | 0.004 | 0.004 |
| R² | 0.854 | 0.854 |

Skill vs persistence: 0.00.

90% prediction interval: ±29.6 ppm; it contained 90% of test values.

Main inputs: indoor_co2 (recent history) (100%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 415 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
