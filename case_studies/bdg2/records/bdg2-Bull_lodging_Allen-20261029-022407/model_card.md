# Model card: bdg2-Bull_lodging_Allen

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** persistence 
- **Trained:** 2026-10-29T02:24:07 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `4ed589da6f3f36e2`, prepared `1ce620dd840cc292`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.24 to 58.3 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.121 | 3.121 |
| MAE (kWh) | 2.152 | 2.152 |
| CV(RMSE) % | 43.058 | 43.058 |
| NMBE % | -2.140 | -2.140 |
| R² | 0.587 | 0.587 |

Skill vs persistence: 0.00.

90% prediction interval: ±4.32 kWh; it contained 84% of test values.

Main inputs: electricity (recent history) (100%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | no | CV(RMSE) 43.1%, NMBE -2.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2562 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
