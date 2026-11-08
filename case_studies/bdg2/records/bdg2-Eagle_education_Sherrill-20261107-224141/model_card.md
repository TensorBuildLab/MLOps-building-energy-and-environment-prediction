# Model card: bdg2-Eagle_education_Sherrill

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:41 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `a99a2d32285dcfa6`, prepared `162a56410eab3aba`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 220 to 877 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 22.527 | 27.907 |
| MAE (kWh) | 14.789 | 18.009 |
| CV(RMSE) % | 3.268 | 4.049 |
| NMBE % | 0.007 | -0.805 |
| R² | 0.873 | 0.805 |

Skill vs time_of_week_profile: 0.19.

90% prediction interval: ±36.9 kWh; it contained 95% of test values.

Main inputs: electricity (recent history) (59%), calendar (time of day, weekday) (40%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.193 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 3.3%, NMBE 0.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2579 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
