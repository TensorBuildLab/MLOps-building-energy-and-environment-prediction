# Model card: bdg2-Bull_education_Summer

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:52 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ec5ef97e9208ccbf`, prepared `c1cf0b3b800fb450`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-09 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8 to 125 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-10 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.190 | 6.176 |
| MAE (kWh) | 2.650 | 3.943 |
| CV(RMSE) % | 13.005 | 19.167 |
| NMBE % | -0.066 | -2.792 |
| R² | 0.777 | 0.516 |

Skill vs same_time_last_week: 0.32.

90% prediction interval: ±4.38 kWh; it contained 82% of test values.

Main inputs: electricity (recent history) (67%), calendar (time of day, weekday) (33%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.321 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.0%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2540 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
