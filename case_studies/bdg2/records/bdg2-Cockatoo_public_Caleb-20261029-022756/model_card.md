# Model card: bdg2-Cockatoo_public_Caleb

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:27:56 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `bb0a2f2a10bf2525`, prepared `ff3cdfffbd3cc7da`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 83.3 to 316 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 21.403 | 30.320 |
| MAE (kWh) | 14.334 | 18.426 |
| CV(RMSE) % | 14.106 | 19.983 |
| NMBE % | -4.127 | -0.598 |
| R² | 0.720 | 0.437 |

Skill vs persistence: 0.29.

90% prediction interval: ±30.9 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (82%), calendar (time of day, weekday) (18%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.294 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 14.1%, NMBE -4.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2393 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
