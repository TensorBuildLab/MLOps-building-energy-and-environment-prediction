# Model card: bdg2-Bull_education_Matilda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:54 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `86e0d99c49dc694b`, prepared `5c4b9ab1bcc6e059`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-19 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5 to 2.35e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 70.795 | 73.052 |
| MAE (kWh) | 14.613 | 13.980 |
| CV(RMSE) % | 72.367 | 74.674 |
| NMBE % | -0.030 | -0.722 |
| R² | -0.105 | -0.176 |

Skill vs persistence: 0.03.

90% prediction interval: ±18.2 kWh; it contained 80% of test values.

Main inputs: electricity (recent history) (99%), calendar (time of day, weekday) (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.031 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 72.4%, NMBE -0.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2377 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
