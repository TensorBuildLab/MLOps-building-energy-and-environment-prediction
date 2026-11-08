# Model card: bdg2-Robin_office_Antonina

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_week_profile 
- **Trained:** 2026-11-07T22:39:51 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7f6dc1d3b3827125`, prepared `71c0e8fe24d04cef`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2.25 to 687 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 40.296 | 40.296 |
| MAE (kWh) | 28.058 | 28.058 |
| CV(RMSE) % | 10.051 | 10.051 |
| NMBE % | -4.367 | -4.367 |
| R² | 0.693 | 0.693 |

Skill vs time_of_week_profile: 0.00.

90% prediction interval: ±130 kWh; it contained 98% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.1%, NMBE -4.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2609 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
