# Model card: bdg2-Peacock_education_Joshua

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:49:14 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c877a43c236092f9`, prepared `52f817239cf3e1d3`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 313 to 589 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 14.998 | 18.555 |
| MAE (kWh) | 10.838 | 13.518 |
| CV(RMSE) % | 3.203 | 3.963 |
| NMBE % | 0.841 | 0.273 |
| R² | 0.768 | 0.645 |

Skill vs towt: 0.19.

90% prediction interval: ±23.3 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (62%), calendar (time of day, weekday) (37%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.192 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 3.2%, NMBE 0.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2595 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
