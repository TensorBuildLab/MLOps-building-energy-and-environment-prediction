# Model card: bdg2-Fox_education_Tamika

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:43:43 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `6a5bde65af3edb25`, prepared `cc0d1ed63a9a9358`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 05:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 13.2 to 339 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 06:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 15.860 | 18.501 |
| MAE (kWh) | 11.978 | 13.830 |
| CV(RMSE) % | 12.984 | 15.146 |
| NMBE % | -2.916 | -3.333 |
| R² | 0.656 | 0.531 |

Skill vs same_time_last_week: 0.14.

90% prediction interval: ±43.9 kWh; it contained 99% of test values.

Main inputs: electricity (recent history) (76%), calendar (time of day, weekday) (16%), airTemperature (6%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.143 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.0%, NMBE -2.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
