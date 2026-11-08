# Model card: bdg2-Wolf_education_Miguel

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:40:25 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `3a0f345ce1c54e4a`, prepared `462c759e56d5b57d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5.77 to 110 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 10.540 | 12.798 |
| MAE (kWh) | 6.440 | 8.102 |
| CV(RMSE) % | 29.348 | 35.638 |
| NMBE % | 0.240 | 2.741 |
| R² | 0.673 | 0.518 |

Skill vs time_of_day_profile: 0.18.

90% prediction interval: ±16.9 kWh; it contained 90% of test values.

Main inputs: calendar (time of day, weekday) (58%), electricity (recent history) (41%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.176 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 29.3%, NMBE 0.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
