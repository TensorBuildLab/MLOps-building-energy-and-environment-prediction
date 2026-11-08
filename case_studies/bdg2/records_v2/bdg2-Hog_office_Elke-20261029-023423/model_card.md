# Model card: bdg2-Hog_office_Elke

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:34:23 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `34025968f34ab0ec`, prepared `da04c24f5234a8d9`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3 to 141 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.929 | 11.990 |
| MAE (kWh) | 3.994 | 8.068 |
| CV(RMSE) % | 9.472 | 19.155 |
| NMBE % | -1.594 | -3.980 |
| R² | 0.954 | 0.813 |

Skill vs time_of_day_profile: 0.51.

90% prediction interval: ±12.5 kWh; it contained 97% of test values.

Main inputs: electricity (recent history) (61%), calendar (time of day, weekday) (39%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.506 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 9.5%, NMBE -1.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2605 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
