# Model card: bdg2-Eagle_education_Brooke

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:43:34 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7cbc7624fdea6faf`, prepared `0d0f0bd9e183b1c2`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-12 21:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 239 to 1.15e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 22:00:00 to 2017-12-31 17:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 43.067 | 43.067 |
| MAE (kWh) | 29.004 | 29.004 |
| CV(RMSE) % | 4.790 | 4.790 |
| NMBE % | -1.729 | -1.729 |
| R² | 0.377 | 0.377 |

Skill vs towt: 0.00.

90% prediction interval: ±33.8 kWh; it contained 69% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 4.8%, NMBE -1.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2514 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
