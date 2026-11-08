# Model card: bdg2-Lamb_education_Maritza

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:44:33 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4e206806a8d298e7`, prepared `c64c4ce3a57f75d6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 03:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0033 to 22.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 04:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.355 | 3.339 |
| MAE (kWh) | 0.689 | 1.397 |
| CV(RMSE) % | 20.424 | 50.331 |
| NMBE % | -1.285 | -6.931 |
| R² | 0.926 | 0.551 |

Skill vs same_time_last_week: 0.59.

90% prediction interval: ±1.89 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (65%), calendar (time of day, weekday) (35%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.594 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 20.4%, NMBE -1.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2443 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
