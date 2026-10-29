# Model card: t2_cw_B

## Model

- **Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 31, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 0.0}
- **Trained:** 2026-10-29T00:29:18 with bemlops 0.1.0.dev0 (code 5c575a6)
- **Data fingerprint:** raw `a4f4efaf843604cf`, prepared `e9cbcd42078e3b18`

## Intended use

1 h ahead forecast of 15-min chilled water energy (AHU, library room)

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00 to 2021-11-12 03:00:00 (train + validation)
- **Inputs:** `ahu_fan_energy` (energy, kWh), `cooling_coil_valve_command` (position, %), `ahu_fan_speed` (other), `offcoil_air_temp` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %), `air_temperature` (zone_air_temperature, degC), `minute_of_day` (other, known ahead)
- **Target range seen:** 0 to 15 kWh

## Performance (held-out test period, time-ordered)

Test period 2021-11-12 04:15:00 to 2021-12-09 23:45:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.798 | 2.552 |
| MAE (kWh) | 0.420 | 1.122 |
| CV(RMSE) % | 24.306 | 77.691 |
| NMBE % | 5.065 | 0.427 |
| R² | 0.956 | 0.551 |

Skill vs persistence: 0.69.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.687 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 17.6%, NMBE 5.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 444 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
