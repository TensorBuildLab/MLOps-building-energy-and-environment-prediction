# Model card: bdg2-Eagle_office_Elias

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:39:13 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `acf0f7db3807eaa5`, prepared `4baf04ba7511c0a0`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-17 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 39.1 to 149 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-18 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 9.320 | 11.029 |
| MAE (kWh) | 6.883 | 8.484 |
| CV(RMSE) % | 11.116 | 13.155 |
| NMBE % | 0.917 | -1.559 |
| R² | 0.821 | 0.750 |

Skill vs time_of_week_profile: 0.15.

90% prediction interval: ±18.4 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (70%), calendar (time of day, weekday) (30%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.155 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.1%, NMBE 0.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2476 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
