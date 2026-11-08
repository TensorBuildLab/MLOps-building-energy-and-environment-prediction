# Model card: bdg2-Hog_office_Patrick

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:42:47 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7d604a4f1c7d6709`, prepared `de6e51354b5d3f5d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.65 to 28.9 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 1.637 | 3.023 |
| MAE (kWh) | 1.078 | 2.420 |
| CV(RMSE) % | 18.114 | 33.456 |
| NMBE % | -2.803 | -23.589 |
| R² | 0.734 | 0.094 |

Skill vs time_of_week_profile: 0.46.

90% prediction interval: ±2.64 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (61%), calendar (time of day, weekday) (38%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.459 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 18.1%, NMBE -2.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
