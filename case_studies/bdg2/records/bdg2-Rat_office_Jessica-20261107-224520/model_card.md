# Model card: bdg2-Rat_office_Jessica

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:45:20 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `e2ec3ae0da0e0680`, prepared `81c66ca2d08774e6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 334 to 1.11e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 69.964 | 92.041 |
| MAE (kWh) | 47.212 | 62.243 |
| CV(RMSE) % | 10.664 | 14.029 |
| NMBE % | 0.563 | 0.682 |
| R² | 0.715 | 0.507 |

Skill vs same_time_last_week: 0.24.

90% prediction interval: ±65.3 kWh; it contained 77% of test values.

Main inputs: electricity (recent history) (70%), calendar (time of day, weekday) (29%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.240 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.7%, NMBE 0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2574 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
