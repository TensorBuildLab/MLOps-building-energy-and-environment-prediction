# Model card: bdg2-Lamb_education_Felicia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:28 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f84d74b42c453fb8`, prepared `bd6df5c55593b9bd`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-19 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0036 to 27.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.008 | 1.986 |
| MAE (kWh) | 0.538 | 0.724 |
| CV(RMSE) % | 53.842 | 106.134 |
| NMBE % | -14.398 | -20.480 |
| R² | 0.912 | 0.656 |

Skill vs same_time_last_week: 0.49.

90% prediction interval: ±1.93 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (73%), calendar (time of day, weekday) (25%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.493 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 53.8%, NMBE -14.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2440 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
