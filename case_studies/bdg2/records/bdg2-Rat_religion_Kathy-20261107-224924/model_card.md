# Model card: bdg2-Rat_religion_Kathy

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:49:24 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `24db22ccfa7995bb`, prepared `6e1c42e776c80ba2`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.6 to 17.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.812 | 1.816 |
| MAE (kWh) | 1.433 | 1.444 |
| CV(RMSE) % | 39.986 | 40.075 |
| NMBE % | -8.588 | -10.131 |
| R² | 0.260 | 0.257 |

Skill vs towt: 0.00.

90% prediction interval: ±3.13 kWh; it contained 92% of test values.

Main inputs: calendar (time of day, weekday) (51%), electricity (recent history) (35%), airTemperature (13%), dewTemperature (1%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.002 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 40.0%, NMBE -8.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2600 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than towt on test data (skill 0.00).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
