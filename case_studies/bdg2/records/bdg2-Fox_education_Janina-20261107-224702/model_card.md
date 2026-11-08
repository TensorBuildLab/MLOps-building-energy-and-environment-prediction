# Model card: bdg2-Fox_education_Janina

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:47:02 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `de63668d546c135f`, prepared `2b7f355522412521`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.04 to 235 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 01:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 22.515 | 29.368 |
| MAE (kWh) | 14.150 | 14.910 |
| CV(RMSE) % | 15.863 | 20.691 |
| NMBE % | 0.699 | 1.128 |
| R² | 0.628 | 0.367 |

Skill vs same_time_last_week: 0.23.

90% prediction interval: ±17.1 kWh; it contained 73% of test values.

Main inputs: electricity (recent history) (90%), calendar (time of day, weekday) (10%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.233 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.9%, NMBE 0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2602 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
