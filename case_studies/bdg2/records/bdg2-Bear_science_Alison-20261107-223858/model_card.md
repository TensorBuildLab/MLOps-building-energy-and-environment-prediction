# Model card: bdg2-Bear_science_Alison

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:38:58 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `313c6a02a35c13f0`, prepared `c8a6c6b42c08c3f0`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-12 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 49.5 to 133 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.554 | 4.904 |
| MAE (kWh) | 2.673 | 3.970 |
| CV(RMSE) % | 3.394 | 4.684 |
| NMBE % | -0.566 | 2.330 |
| R² | 0.765 | 0.553 |

Skill vs towt: 0.28.

90% prediction interval: ±6.15 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (71%), calendar (time of day, weekday) (26%), airTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.275 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 3.4%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
