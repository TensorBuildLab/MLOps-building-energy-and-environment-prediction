# Model card: bdg2-Bobcat_other_Howard

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:45:39 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `e618db8c3e4931d8`, prepared `3973f56a59902919`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.16 to 1.56e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 78.351 | 91.009 |
| MAE (kWh) | 34.363 | 47.720 |
| CV(RMSE) % | 234.072 | 271.889 |
| NMBE % | -21.329 | -30.544 |
| R² | -0.044 | -0.409 |

Skill vs towt: 0.14.

90% prediction interval: ±156 kWh; it contained 98% of test values.

Main inputs: electricity (recent history) (79%), calendar (time of day, weekday) (13%), airTemperature (6%), windSpeed (2%), dewTemperature (2%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.139 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 234.1%, NMBE -21.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2407 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
