# Model card: bdg2-Robin_office_Maryann

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-11-07T22:45:51 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4425cef8a8b50060`, prepared `99a3288a6da46264`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.36 to 388 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 24.630 | 24.630 |
| MAE (kWh) | 18.958 | 18.958 |
| CV(RMSE) % | 11.300 | 11.300 |
| NMBE % | -6.955 | -6.955 |
| R² | 0.648 | 0.648 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±196 kWh; it contained 100% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.3%, NMBE -7.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2609 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
