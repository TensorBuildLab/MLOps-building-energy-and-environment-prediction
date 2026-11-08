# Model card: bdg2-Moose_education_Clark

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:23 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `dfb9197f440305da`, prepared `eff75763b98f40a8`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 199 to 1.46e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 90.871 | 112.877 |
| MAE (kWh) | 60.770 | 75.760 |
| CV(RMSE) % | 11.236 | 13.958 |
| NMBE % | -0.749 | -5.194 |
| R² | 0.900 | 0.845 |

Skill vs towt: 0.19.

90% prediction interval: ±99.1 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (63%), calendar (time of day, weekday) (37%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.195 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.2%, NMBE -0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2549 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
