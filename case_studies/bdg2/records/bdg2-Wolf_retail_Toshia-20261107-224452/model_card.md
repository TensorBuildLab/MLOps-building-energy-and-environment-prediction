# Model card: bdg2-Wolf_retail_Toshia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:44:52 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `457b192928654f8e`, prepared `b61912253b524286`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 7.29 to 206 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 25.471 | 32.417 |
| MAE (kWh) | 15.816 | 21.147 |
| CV(RMSE) % | 38.679 | 49.227 |
| NMBE % | -2.120 | -6.337 |
| R² | 0.737 | 0.573 |

Skill vs towt: 0.21.

90% prediction interval: ±45.8 kWh; it contained 92% of test values.

Main inputs: calendar (time of day, weekday) (64%), electricity (recent history) (36%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.214 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 38.7%, NMBE -2.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
