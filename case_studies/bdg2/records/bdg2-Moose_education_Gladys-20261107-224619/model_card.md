# Model card: bdg2-Moose_education_Gladys

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:46:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `d822f8b6ecbbe1d2`, prepared `ad0d9d8b6d85b414`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-15 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 584 to 1.67e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-16 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 84.981 | 120.030 |
| MAE (kWh) | 54.898 | 87.393 |
| CV(RMSE) % | 7.950 | 11.229 |
| NMBE % | -1.176 | -5.607 |
| R² | 0.914 | 0.828 |

Skill vs towt: 0.29.

90% prediction interval: ±70.8 kWh; it contained 76% of test values.

Main inputs: electricity (recent history) (71%), calendar (time of day, weekday) (28%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.292 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 7.9%, NMBE -1.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2462 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
