# Model card: bdg2-Bear_education_Millie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:50:21 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c2011407c9a5483b`, prepared `002af6b4ac980189`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 11:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2.12 to 5.75 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 12:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.438 | 0.521 |
| MAE (kWh) | 0.314 | 0.298 |
| CV(RMSE) % | 14.145 | 16.813 |
| NMBE % | -6.419 | -0.365 |
| R² | 0.189 | -0.146 |

Skill vs persistence: 0.16.

90% prediction interval: ±0.38 kWh; it contained 70% of test values.

Main inputs: electricity (recent history) (53%), calendar (time of day, weekday) (46%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.159 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.1%, NMBE -6.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2551 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
