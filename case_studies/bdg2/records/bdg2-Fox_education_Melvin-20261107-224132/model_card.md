# Model card: bdg2-Fox_education_Melvin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:32 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `bd097c92c3b538f7`, prepared `8736f547cc14f40c`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 03:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 7.35 to 141 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 04:00:00 to 2017-12-28 05:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 12.398 | 18.478 |
| MAE (kWh) | 7.665 | 10.053 |
| CV(RMSE) % | 22.666 | 33.782 |
| NMBE % | -1.306 | -2.777 |
| R² | 0.791 | 0.535 |

Skill vs same_time_last_week: 0.33.

90% prediction interval: ±21.3 kWh; it contained 89% of test values.

Main inputs: electricity (recent history) (64%), calendar (time of day, weekday) (36%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.329 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 22.7%, NMBE -1.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2498 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
