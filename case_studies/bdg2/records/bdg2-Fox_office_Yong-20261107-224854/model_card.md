# Model card: bdg2-Fox_office_Yong

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:54 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `284f1667a792be96`, prepared `0a65b81d879bf32c`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 4.4 to 304 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 16.781 | 20.539 |
| MAE (kWh) | 10.598 | 11.575 |
| CV(RMSE) % | 13.912 | 17.028 |
| NMBE % | -2.649 | 1.652 |
| R² | 0.818 | 0.727 |

Skill vs same_time_last_week: 0.18.

90% prediction interval: ±13.8 kWh; it contained 76% of test values.

Main inputs: electricity (recent history) (49%), calendar (time of day, weekday) (49%), airTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.183 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.9%, NMBE -2.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
