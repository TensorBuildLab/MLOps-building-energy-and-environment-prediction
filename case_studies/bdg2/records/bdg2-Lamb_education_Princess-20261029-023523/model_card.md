# Model card: bdg2-Lamb_education_Princess

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** persistence 
- **Trained:** 2026-10-29T02:35:23 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `622d56cd093220a2`, prepared `5b49d3b2e520f6e7`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 18:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0005 to 52.5 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 19:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.160 | 4.160 |
| MAE (kWh) | 1.068 | 1.068 |
| CV(RMSE) % | 99.003 | 99.003 |
| NMBE % | 1.396 | 1.396 |
| R² | 0.753 | 0.753 |

Skill vs persistence: 0.00.

90% prediction interval: ±0 kWh; it contained 69% of test values.

Main inputs: electricity (recent history) (100%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | no | CV(RMSE) 99.0%, NMBE 1.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2597 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
