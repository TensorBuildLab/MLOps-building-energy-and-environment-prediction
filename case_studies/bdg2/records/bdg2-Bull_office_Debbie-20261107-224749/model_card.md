# Model card: bdg2-Bull_office_Debbie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:49 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ba297aecc112be30`, prepared `35cb12ec71d724e0`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3 to 108 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.298 | 7.025 |
| MAE (kWh) | 2.442 | 3.585 |
| CV(RMSE) % | 13.901 | 22.722 |
| NMBE % | 1.418 | -2.773 |
| R² | 0.885 | 0.691 |

Skill vs same_time_last_week: 0.39.

90% prediction interval: ±4.26 kWh; it contained 85% of test values.

Main inputs: electricity (recent history) (58%), calendar (time of day, weekday) (42%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.388 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.9%, NMBE 1.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2549 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
