# Model card: bdg2-Moose_education_Abbie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:44:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `1be807dc325eb550`, prepared `dc73a30e5570d417`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-25 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2.77 to 2.03e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-26 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 92.681 | 116.056 |
| MAE (kWh) | 47.096 | 49.222 |
| CV(RMSE) % | 7.952 | 9.958 |
| NMBE % | -2.029 | -0.267 |
| R² | 0.859 | 0.779 |

Skill vs same_time_last_week: 0.20.

90% prediction interval: ±72 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (64%), calendar (time of day, weekday) (36%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.201 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.0%, NMBE -2.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2289 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
