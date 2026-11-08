# Model card: bdg2-Gator_public_Kendall

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_week_profile 
- **Trained:** 2026-11-07T22:46:17 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f172f261279b6037`, prepared `518df6394d65e545`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 03:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.167 to 45.1 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 04:00:00 to 2017-12-31 05:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 4.288 | 4.288 |
| MAE (kWh) | 2.949 | 2.949 |
| CV(RMSE) % | 28.955 | 28.955 |
| NMBE % | -2.289 | -2.289 |
| R² | 0.555 | 0.555 |

Skill vs time_of_week_profile: 0.00.

90% prediction interval: ±4.16 kWh; it contained 85% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 29.0%, NMBE -2.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
