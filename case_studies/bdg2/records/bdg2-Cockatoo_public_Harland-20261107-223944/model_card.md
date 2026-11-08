# Model card: bdg2-Cockatoo_public_Harland

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:44 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `34d81a6d7fc4dbb2`, prepared `280e8da3f471eb4b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 22.9 to 85.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.311 | 10.002 |
| MAE (kWh) | 3.029 | 5.817 |
| CV(RMSE) % | 8.960 | 20.789 |
| NMBE % | -2.741 | -6.681 |
| R² | 0.876 | 0.330 |

Skill vs towt: 0.57.

90% prediction interval: ±5.09 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (57%), calendar (time of day, weekday) (42%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.569 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 9.0%, NMBE -2.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2393 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
