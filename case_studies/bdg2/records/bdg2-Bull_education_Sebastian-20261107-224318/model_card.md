# Model card: bdg2-Bull_education_Sebastian

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:43:18 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `046347369d50e279`, prepared `2b1e6c6434edf209`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3 to 127 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 4.676 | 7.104 |
| MAE (kWh) | 2.403 | 4.639 |
| CV(RMSE) % | 11.653 | 17.703 |
| NMBE % | -0.147 | 4.456 |
| R² | 0.880 | 0.724 |

Skill vs time_of_week_profile: 0.34.

90% prediction interval: ±5.08 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (71%), calendar (time of day, weekday) (29%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.342 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.7%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2549 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
