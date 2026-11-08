# Model card: bdg2-Moose_education_Rene

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:38:29 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `fa230230660ea026`, prepared `bd18fc68cad93192`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-15 18:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 128 to 1.61e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-16 19:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 90.524 | 101.948 |
| MAE (kWh) | 40.184 | 60.795 |
| CV(RMSE) % | 19.463 | 21.919 |
| NMBE % | -2.225 | -4.095 |
| R² | 0.920 | 0.898 |

Skill vs time_of_day_profile: 0.11.

90% prediction interval: ±78 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (85%), calendar (time of day, weekday) (15%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.112 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 19.5%, NMBE -2.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2523 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
