# Model card: bdg2-Gator_public_Jayme

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-11-07T22:38:54 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `fb75141d89251d23`, prepared `f1e0119028f0f8cc`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 4.17 to 236 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 01:00:00 to 2017-12-31 05:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 25.102 | 25.102 |
| MAE (kWh) | 17.413 | 17.413 |
| CV(RMSE) % | 33.699 | 33.699 |
| NMBE % | -20.683 | -20.683 |
| R² | 0.287 | 0.287 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±22.4 kWh; it contained 74% of test values.

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 33.7%, NMBE -20.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 671 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
