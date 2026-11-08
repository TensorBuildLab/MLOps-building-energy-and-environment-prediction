# Model card: bdg2-Bobcat_other_Timothy

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:36:30 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `af560b725cda905d`, prepared `1dbba623151a9e8b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.6 to 101 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.768 | 6.852 |
| MAE (kWh) | 3.428 | 5.097 |
| CV(RMSE) % | 20.837 | 29.945 |
| NMBE % | 0.640 | 3.492 |
| R² | 0.640 | 0.257 |

Skill vs same_time_last_week: 0.30.

90% prediction interval: ±3.44 kWh; it contained 61% of test values.

Main inputs: electricity (recent history) (58%), calendar (time of day, weekday) (41%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.304 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 20.8%, NMBE 0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2448 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
