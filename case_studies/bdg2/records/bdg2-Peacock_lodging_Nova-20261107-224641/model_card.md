# Model card: bdg2-Peacock_lodging_Nova

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:46:41 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `1a71c4aa8ec11d3f`, prepared `c2165b55d425b8bd`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.83 to 52.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.847 | 5.024 |
| MAE (kWh) | 2.896 | 3.617 |
| CV(RMSE) % | 19.691 | 25.714 |
| NMBE % | -1.193 | -0.402 |
| R² | 0.606 | 0.328 |

Skill vs persistence: 0.23.

90% prediction interval: ±4.88 kWh; it contained 80% of test values.

Main inputs: electricity (recent history) (74%), calendar (time of day, weekday) (25%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.234 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 19.7%, NMBE -1.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
