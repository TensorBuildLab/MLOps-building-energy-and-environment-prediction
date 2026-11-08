# Model card: robod-room2-chilled_water_energy-1h

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T02:29:47 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `47a2f3ce81aae624`

## Intended use

Forecast chilled-water energy one hour ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 13 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 16:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.978 | 0.978 |
| MAE (kWh) | 0.379 | 0.379 |
| CV(RMSE) % | 126.931 | 126.931 |
| NMBE % | -5.470 | -5.470 |
| R² | 0.524 | 0.524 |

Skill vs persistence: 0.00.

90% prediction interval: ±0.0156 kWh; it contained 75% of test values.

Main inputs: chilled_water_energy (recent history) (100%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | no | CV(RMSE) 103.1%, NMBE -5.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 415 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
