# Model card: bdg2-Gator_public_Natasha

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:45:16 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c8646433137108df`, prepared `2820ce0dc9291580`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.75 to 469 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 03:00:00 to 2017-12-30 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 45.181 | 45.181 |
| MAE (kWh) | 33.678 | 33.678 |
| CV(RMSE) % | 39.988 | 39.988 |
| NMBE % | 3.613 | 3.613 |
| R² | 0.624 | 0.624 |

Skill vs towt: 0.00.

90% prediction interval: ±88.2 kWh; it contained 94% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 40.0%, NMBE 3.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 627 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
