# Model card: bdg2-Robin_education_So

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:48 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `59e411dee3194e2e`, prepared `abf22da5ca50b186`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-24 03:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 186 to 711 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-25 04:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 15.084 | 32.639 |
| MAE (kWh) | 10.795 | 20.131 |
| CV(RMSE) % | 3.088 | 6.683 |
| NMBE % | -0.481 | -1.569 |
| R² | 0.960 | 0.811 |

Skill vs same_time_last_week: 0.54.

90% prediction interval: ±22.9 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (74%), calendar (time of day, weekday) (26%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.538 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 3.1%, NMBE -0.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2348 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
