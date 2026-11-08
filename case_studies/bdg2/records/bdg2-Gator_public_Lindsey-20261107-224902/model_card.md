# Model card: bdg2-Gator_public_Lindsey

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:49:02 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7f735ec3bc0f0992`, prepared `f8adaa4553d77299`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-22 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2.08 to 75 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-23 03:00:00 to 2017-12-29 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 7.383 | 7.383 |
| MAE (kWh) | 4.427 | 4.427 |
| CV(RMSE) % | 33.016 | 33.016 |
| NMBE % | -12.116 | -12.116 |
| R² | 0.277 | 0.277 |

Skill vs towt: 0.00.

90% prediction interval: ±5.13 kWh; it contained 77% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 33.0%, NMBE -12.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 549 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
