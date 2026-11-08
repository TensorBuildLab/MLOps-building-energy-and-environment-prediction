# Model card: bdg2-Bear_education_Chana

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:36:35 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4cf66b5c1a1a5500`, prepared `3eca902e576a324d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-09 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 14 to 37.5 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-10 02:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.210 | 3.939 |
| MAE (kWh) | 1.498 | 2.477 |
| CV(RMSE) % | 9.834 | 17.533 |
| NMBE % | 0.699 | -1.057 |
| R² | 0.853 | 0.533 |

Skill vs same_time_last_week: 0.44.

90% prediction interval: ±3.33 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (61%), calendar (time of day, weekday) (39%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.439 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 9.8%, NMBE 0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2497 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
