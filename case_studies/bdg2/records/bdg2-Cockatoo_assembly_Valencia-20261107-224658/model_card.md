# Model card: bdg2-Cockatoo_assembly_Valencia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** persistence 
- **Trained:** 2026-11-07T22:46:58 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `adbb86d575fd75ee`, prepared `bc2c85e56093859c`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 7.1 to 256 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 33.489 | 33.489 |
| MAE (kWh) | 23.355 | 23.355 |
| CV(RMSE) % | 23.486 | 23.486 |
| NMBE % | -0.160 | -0.160 |
| R² | 0.168 | 0.168 |

Skill vs persistence: 0.00.

90% prediction interval: ±14.3 kWh; it contained 49% of test values.

Main inputs: electricity (recent history) (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 23.5%, NMBE -0.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2395 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
