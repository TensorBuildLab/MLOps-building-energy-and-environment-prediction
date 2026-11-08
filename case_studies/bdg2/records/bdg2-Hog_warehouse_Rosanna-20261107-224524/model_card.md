# Model card: bdg2-Hog_warehouse_Rosanna

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:45:24 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7308ec6e6c442c0b`, prepared `7f936de838d947f3`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-17 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8.62 to 52.6 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-18 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 4.523 | 5.268 |
| MAE (kWh) | 2.542 | 2.484 |
| CV(RMSE) % | 25.476 | 29.673 |
| NMBE % | -3.736 | 0.284 |
| R² | 0.390 | 0.172 |

Skill vs same_time_yesterday: 0.14.

90% prediction interval: ±18.6 kWh; it contained 98% of test values.

Main inputs: electricity (recent history) (97%), dewTemperature (2%), calendar (time of day, weekday) (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.141 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 25.5%, NMBE -3.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2477 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
