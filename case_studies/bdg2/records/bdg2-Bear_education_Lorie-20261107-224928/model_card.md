# Model card: bdg2-Bear_education_Lorie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:49:28 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `1c75cf7afc315b70`, prepared `f17d25aa5fa958db`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-12 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 197 to 635 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 02:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 28.337 | 35.052 |
| MAE (kWh) | 20.559 | 23.701 |
| CV(RMSE) % | 6.958 | 8.607 |
| NMBE % | -0.281 | 0.022 |
| R² | 0.772 | 0.651 |

Skill vs persistence: 0.19.

90% prediction interval: ±46.5 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (74%), calendar (time of day, weekday) (24%), airTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.192 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 7.0%, NMBE -0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2600 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
