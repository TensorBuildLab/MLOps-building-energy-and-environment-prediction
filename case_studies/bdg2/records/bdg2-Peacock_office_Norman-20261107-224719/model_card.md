# Model card: bdg2-Peacock_office_Norman

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c68d10551aa4c946`, prepared `7badc3673dbde18c`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 16 to 72.3 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 5.377 | 8.359 |
| MAE (kWh) | 3.982 | 6.000 |
| CV(RMSE) % | 14.324 | 22.266 |
| NMBE % | -0.129 | -0.072 |
| R² | 0.647 | 0.148 |

Skill vs same_time_last_week: 0.36.

90% prediction interval: ±7.37 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (51%), calendar (time of day, weekday) (48%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.357 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.3%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2606 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
