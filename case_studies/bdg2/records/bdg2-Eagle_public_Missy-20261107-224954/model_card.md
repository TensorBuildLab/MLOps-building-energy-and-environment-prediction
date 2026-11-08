# Model card: bdg2-Eagle_public_Missy

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:49:54 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `97c47ddcf6c4fa7f`, prepared `cd195d242df8a78d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-06 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 15.1 to 143 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-07 02:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 5.918 | 7.095 |
| MAE (kWh) | 4.113 | 5.120 |
| CV(RMSE) % | 18.602 | 22.303 |
| NMBE % | 2.746 | 1.153 |
| R² | 0.657 | 0.508 |

Skill vs towt: 0.17.

90% prediction interval: ±9.11 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (85%), calendar (time of day, weekday) (15%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.166 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 18.6%, NMBE 2.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2525 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
