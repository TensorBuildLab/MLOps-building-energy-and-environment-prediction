# Model card: bdg2-Eagle_office_Randolph

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:40:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `36b9ad5e52a02d91`, prepared `09c490305e311207`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8.56 to 232 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 18.622 | 20.226 |
| MAE (kWh) | 11.801 | 12.927 |
| CV(RMSE) % | 16.651 | 18.086 |
| NMBE % | 3.913 | 1.795 |
| R² | 0.729 | 0.680 |

Skill vs time_of_week_profile: 0.08.

90% prediction interval: ±23.3 kWh; it contained 84% of test values.

Main inputs: electricity (recent history) (60%), calendar (time of day, weekday) (39%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.079 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 16.7%, NMBE 3.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2582 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
