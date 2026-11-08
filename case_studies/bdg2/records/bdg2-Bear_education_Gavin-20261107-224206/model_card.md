# Model card: bdg2-Bear_education_Gavin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:42:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `6190e1d679b18270`, prepared `d5473839afca6a6b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 64.9 to 120 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.402 | 5.750 |
| MAE (kWh) | 3.355 | 4.353 |
| CV(RMSE) % | 4.962 | 6.481 |
| NMBE % | -1.138 | -0.890 |
| R² | 0.769 | 0.605 |

Skill vs towt: 0.23.

90% prediction interval: ±7.09 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (67%), calendar (time of day, weekday) (32%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.234 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 5.0%, NMBE -1.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
