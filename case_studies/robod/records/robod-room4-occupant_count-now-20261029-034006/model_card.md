# Model card: robod-room4-occupant_count-now

## Model

- **Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T03:40:06 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `eb6e671f4a45f8f2`, prepared `e38c905457ed6e01`

## Intended use

Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-14 22:30:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `damper_position` (position, %), `supply_air_flow` (airflow, m3/h), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 17 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-14 22:45:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 1.359 | 1.360 |
| MAE (count) | 1.009 | 0.928 |
| CV(RMSE) % | 49.189 | 49.210 |
| NMBE % | -11.076 | -23.829 |
| R² | 0.783 | 0.783 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±3.29 count; it contained 96% of test values.

Main inputs: calendar (time of day, weekday) (41%), chilled_water_energy (24%), supply_air_flow (18%), supply_air_temperature (7%), illuminance (2%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 677 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill 0.00).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
