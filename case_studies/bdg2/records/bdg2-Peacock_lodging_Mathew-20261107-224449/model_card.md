# Model card: bdg2-Peacock_lodging_Mathew

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** persistence 
- **Trained:** 2026-11-07T22:44:49 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `568905d98a4d00fa`, prepared `15c237094d3e7e99`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 14:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 7.95 to 102 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 15:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 7.269 | 7.269 |
| MAE (kWh) | 4.933 | 4.933 |
| CV(RMSE) % | 13.341 | 13.341 |
| NMBE % | -0.329 | -0.329 |
| R² | 0.506 | 0.506 |

Skill vs persistence: 0.00.

90% prediction interval: ±5.95 kWh; it contained 70% of test values.

Main inputs: electricity (recent history) (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.3%, NMBE -0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2601 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
