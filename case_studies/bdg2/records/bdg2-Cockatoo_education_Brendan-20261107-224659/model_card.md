# Model card: bdg2-Cockatoo_education_Brendan

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:46:59 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ca87372d05294bf8`, prepared `007ab47187f7b93d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 48.3 to 111 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.167 | 6.660 |
| MAE (kWh) | 3.179 | 4.888 |
| CV(RMSE) % | 6.010 | 9.606 |
| NMBE % | 0.056 | -0.750 |
| R² | 0.871 | 0.669 |

Skill vs same_time_last_week: 0.37.

90% prediction interval: ±7.6 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (70%), calendar (time of day, weekday) (30%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.374 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.0%, NMBE 0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2394 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
