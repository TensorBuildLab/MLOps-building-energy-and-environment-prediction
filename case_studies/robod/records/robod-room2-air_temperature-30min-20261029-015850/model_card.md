# Model card: robod-room2-air_temperature-30min

## Model

- **Task:** forecast air_temperature (zone_air_temperature, degC) 30 min ahead (2 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T01:58:50 with bemlops 0.2.0.dev0 (code e85edf1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `38f9d7a117608481`

## Intended use

Forecast room temperature 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 20.5 to 33.8 degC

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (degC) | 0.611 | 0.611 |
| MAE (degC) | 0.274 | 0.274 |
| CV(RMSE) % | 2.278 | 2.278 |
| NMBE % | 0.029 | 0.029 |
| R² | 0.817 | 0.817 |

Skill vs persistence: 0.00.

90% prediction interval: ±0.575 degC; it contained 86% of test values.

Main inputs: air_temperature (recent history) (100%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 417 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
