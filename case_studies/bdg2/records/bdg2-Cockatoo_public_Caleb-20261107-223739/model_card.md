# Model card: bdg2-Cockatoo_public_Caleb

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:37:39 with bemlops 0.3.1 (code a89b059)
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

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 21.403 | 26.343 |
| MAE (kWh) | 14.334 | 14.147 |
| CV(RMSE) % | 14.106 | 17.362 |
| NMBE % | -4.127 | -2.881 |
| R² | 0.720 | 0.575 |

Skill vs same_time_last_week: 0.19.

90% prediction interval: ±30.9 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (82%), calendar (time of day, weekday) (18%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.188 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.1%, NMBE -4.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2393 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
