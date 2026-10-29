# Model card: bdg2-Gator_public_Dionna

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-10-29T02:33:17 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `40171199286a6115`, prepared `9682f0a3fd58be20`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-31 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.17 to 38.3 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-01 03:00:00 to 2017-12-30 05:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.933 | 5.933 |
| MAE (kWh) | 4.582 | 4.582 |
| CV(RMSE) % | 46.842 | 46.842 |
| NMBE % | -33.206 | -33.206 |
| R² | -0.230 | -0.230 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±3.59 kWh; it contained 44% of test values.

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | no | CV(RMSE) 46.8%, NMBE -33.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 561 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
