# Model card: bdg2-Cockatoo_office_Jodie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:26:31 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `a11070de433818ac`, prepared `1998feaa19ed6974`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 27.4 to 100 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 6.813 | 10.844 |
| MAE (kWh) | 4.925 | 7.874 |
| CV(RMSE) % | 12.032 | 19.152 |
| NMBE % | 2.535 | 8.385 |
| R² | 0.698 | 0.234 |

Skill vs time_of_day_profile: 0.37.

90% prediction interval: ±5.68 kWh; it contained 67% of test values.

Main inputs: electricity (recent history) (60%), calendar (time of day, weekday) (32%), airTemperature (5%), dewTemperature (2%), windSpeed (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.372 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 12.0%, NMBE 2.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2394 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
