# Model card: robod-room1-occupant_count-now

## Model

- **Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)
- **Model:** random_forest {'model__min_samples_leaf': 10, 'model__max_features': 1.0, 'model__max_depth': 16}
- **Trained:** 2026-10-29T01:39:22 with bemlops 0.2.0.dev0 (code b253e59)
- **Data fingerprint:** raw `f3fcdd4922287b47`, prepared `04069b2755ca6fa9`

## Intended use

Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 38 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | training_mean |
|---|---|---|
| RMSE (count) | 0.450 | 1.882 |
| MAE (count) | 0.155 | 1.881 |
| CV(RMSE) % | 9441.591 | 39470.012 |
| NMBE % | -3068.075 | -39499.563 |
| R² | -63.133 | -1119.791 |

Skill vs training_mean: 0.76.

90% prediction interval: ±1.02 count; it contained 99% of test values.

Main inputs: calendar (time of day, weekday) (54%), global_horizontal_solar_radiation (32%), air_temperature (7%), illuminance (4%), indoor_relative_humidity (2%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.761 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 419 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
