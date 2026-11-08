# Model card: bdg2-Bull_lodging_Leonard

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:45:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `278aa207004bf54b`, prepared `6e5f3b6eeaedb946`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 4 to 114 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.855 | 4.961 |
| MAE (kWh) | 2.591 | 3.286 |
| CV(RMSE) % | 10.479 | 13.485 |
| NMBE % | 2.031 | -0.298 |
| R² | 0.640 | 0.404 |

Skill vs persistence: 0.22.

90% prediction interval: ±3.59 kWh; it contained 75% of test values.

Main inputs: electricity (recent history) (69%), calendar (time of day, weekday) (31%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.223 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.5%, NMBE 2.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2544 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
