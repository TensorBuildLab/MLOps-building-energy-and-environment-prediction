# Model card: bdg2-Bobcat_lodging_Melaine

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:39:58 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f04bdec98a100727`, prepared `8d71a5ad60c1ae8f`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5.88 to 84 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 5.058 | 5.832 |
| MAE (kWh) | 3.487 | 3.902 |
| CV(RMSE) % | 11.471 | 13.225 |
| NMBE % | -0.635 | 0.187 |
| R² | 0.412 | 0.219 |

Skill vs same_time_yesterday: 0.13.

90% prediction interval: ±7.29 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (96%), calendar (time of day, weekday) (2%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.133 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.5%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2452 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
