# Model card: bdg2-Mouse_lodging_Vicente

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:39:34 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `b2da205ca453d844`, prepared `4b9743cf3518a487`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-07-24 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 10 to 100 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-07-25 01:00:00 to 2017-10-23 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 7.682 | 7.688 |
| MAE (kWh) | 6.078 | 5.968 |
| CV(RMSE) % | 16.057 | 16.071 |
| NMBE % | -2.215 | 4.411 |
| R² | 0.741 | 0.740 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±14.2 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (69%), calendar (time of day, weekday) (31%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.001 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 16.1%, NMBE -2.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2151 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill 0.00).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
