# Model card: bdg2-Robin_education_Audrea

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:43:52 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `7bd4bc6357896b48`, prepared `2651f4e320fa4f5b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 11:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 71 to 588 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 12:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 21.844 | 22.624 |
| MAE (kWh) | 15.303 | 14.919 |
| CV(RMSE) % | 9.635 | 9.979 |
| NMBE % | -2.463 | -1.037 |
| R² | 0.864 | 0.854 |

Skill vs persistence: 0.03.

90% prediction interval: ±27 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (94%), calendar (time of day, weekday) (6%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.034 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 9.6%, NMBE -2.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2184 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
