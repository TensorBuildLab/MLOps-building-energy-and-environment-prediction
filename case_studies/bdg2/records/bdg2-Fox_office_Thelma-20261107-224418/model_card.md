# Model card: bdg2-Fox_office_Thelma

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:44:18 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `0bfede64a55ce603`, prepared `7cc71ca047da1dda`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 9.5 to 222 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 17.333 | 20.525 |
| MAE (kWh) | 10.238 | 14.226 |
| CV(RMSE) % | 13.960 | 16.531 |
| NMBE % | -1.902 | 0.874 |
| R² | 0.885 | 0.839 |

Skill vs towt: 0.16.

90% prediction interval: ±26.1 kWh; it contained 92% of test values.

Main inputs: electricity (recent history) (56%), calendar (time of day, weekday) (43%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.156 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.0%, NMBE -1.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
