# Model card: bdg2-Eagle_education_Samantha

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-10-29T02:30:26 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `f1dcebaf0770d7c5`, prepared `f525b64d3e9f4158`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 21:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 85.8 to 431 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 22:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 24.640 | 24.640 |
| MAE (kWh) | 19.276 | 19.276 |
| CV(RMSE) % | 9.729 | 9.729 |
| NMBE % | -6.393 | -6.393 |
| R² | -0.293 | -0.293 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±26.5 kWh; it contained 73% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 9.7%, NMBE -6.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2593 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
