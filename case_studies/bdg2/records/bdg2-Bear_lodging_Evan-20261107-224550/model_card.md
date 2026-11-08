# Model card: bdg2-Bear_lodging_Evan

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:45:50 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `966f939f36f3397c`, prepared `3daea64c67520a96`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 23:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 94.2 to 287 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 00:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.931 | 24.096 |
| MAE (kWh) | 8.924 | 14.583 |
| CV(RMSE) % | 8.034 | 13.897 |
| NMBE % | -0.754 | -2.415 |
| R² | 0.920 | 0.760 |

Skill vs same_time_last_week: 0.42.

90% prediction interval: ±17.1 kWh; it contained 87% of test values.

Main inputs: electricity (recent history) (88%), calendar (time of day, weekday) (11%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.422 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.0%, NMBE -0.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
