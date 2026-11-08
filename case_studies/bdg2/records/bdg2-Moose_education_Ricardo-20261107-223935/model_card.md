# Model card: bdg2-Moose_education_Ricardo

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:35 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `1cc99e93ce4bf235`, prepared `ad2fb201eb1355c6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 202 to 459 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 18.811 | 32.044 |
| MAE (kWh) | 13.180 | 25.290 |
| CV(RMSE) % | 5.735 | 9.769 |
| NMBE % | 0.682 | 5.888 |
| R² | 0.878 | 0.645 |

Skill vs towt: 0.41.

90% prediction interval: ±21.1 kWh; it contained 82% of test values.

Main inputs: electricity (recent history) (67%), calendar (time of day, weekday) (32%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.413 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 5.7%, NMBE 0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2609 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
