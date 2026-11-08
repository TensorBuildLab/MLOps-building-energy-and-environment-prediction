# Model card: bdg2-Hog_lodging_Celeste

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:30 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `3a1e5e4220b5c75f`, prepared `0df2c47bb520f4a1`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-12 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 41.9 to 179 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 9.058 | 10.393 |
| MAE (kWh) | 6.611 | 7.728 |
| CV(RMSE) % | 8.797 | 10.092 |
| NMBE % | -0.347 | -0.390 |
| R² | 0.826 | 0.771 |

Skill vs persistence: 0.13.

90% prediction interval: ±13.3 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (85%), calendar (time of day, weekday) (15%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.128 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.8%, NMBE -0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2605 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
