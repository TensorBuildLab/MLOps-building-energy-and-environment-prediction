# Model card: bdg2-Hog_office_Emmanuel

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:43:15 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `56812f759c5cdd9b`, prepared `1c6eadd8dd744641`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 04:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.83 to 70.5 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 05:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.891 | 2.310 |
| MAE (kWh) | 1.356 | 1.736 |
| CV(RMSE) % | 6.769 | 8.268 |
| NMBE % | -0.188 | -1.935 |
| R² | 0.915 | 0.873 |

Skill vs towt: 0.18.

90% prediction interval: ±3.44 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (80%), calendar (time of day, weekday) (20%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.181 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.8%, NMBE -0.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2587 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
