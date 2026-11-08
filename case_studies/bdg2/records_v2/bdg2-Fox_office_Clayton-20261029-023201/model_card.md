# Model card: bdg2-Fox_office_Clayton

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:32:01 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `56299dd5d204564c`, prepared `c4557a4474aaf836`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8.65 to 216 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 9.088 | 13.748 |
| MAE (kWh) | 6.328 | 8.770 |
| CV(RMSE) % | 11.625 | 17.585 |
| NMBE % | -3.590 | -0.953 |
| R² | 0.940 | 0.862 |

Skill vs persistence: 0.34.

90% prediction interval: ±16.2 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (86%), calendar (time of day, weekday) (10%), airTemperature (4%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.339 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 11.6%, NMBE -3.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
