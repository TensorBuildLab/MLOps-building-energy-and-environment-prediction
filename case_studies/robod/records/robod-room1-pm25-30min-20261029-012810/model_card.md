# Model card: robod-room1-pm25-30min

## Model

- **Task:** forecast pm2.5 (pm25, ug/m3) 30 min ahead (2 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(0.348280208702833)}
- **Trained:** 2026-10-29T01:28:10 with bemlops 0.2.0.dev0 (code b253e59)
- **Data fingerprint:** raw `f3fcdd4922287b47`, prepared `fec6c39c8a936677`

## Intended use

Forecast PM2.5 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0.833 to 44.3 ug/m3

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ug/m3) | 4.358 | 5.049 |
| MAE (ug/m3) | 1.830 | 2.155 |
| CV(RMSE) % | 36.546 | 42.335 |
| NMBE % | 3.079 | 0.342 |
| R² | 0.853 | 0.803 |

Skill vs persistence: 0.14.

90% prediction interval: ±2.05 ug/m3; it contained 78% of test values.

Main inputs: pm2.5 (recent history) (99%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.137 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 416 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
