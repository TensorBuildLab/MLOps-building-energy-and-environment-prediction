# Model card: bdg2-Bull_assembly_Lance

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:49:38 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `064740faf4c6dd91`, prepared `1369ca6415d3f728`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 4 to 1.07e+04 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 307.172 | 495.345 |
| MAE (kWh) | 34.899 | 54.874 |
| CV(RMSE) % | 65.371 | 105.418 |
| NMBE % | 2.540 | -1.009 |
| R² | 0.237 | -0.983 |

Skill vs same_time_last_week: 0.38.

90% prediction interval: ±37.7 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (99%), calendar (time of day, weekday) (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.380 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 65.4%, NMBE 2.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2562 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
