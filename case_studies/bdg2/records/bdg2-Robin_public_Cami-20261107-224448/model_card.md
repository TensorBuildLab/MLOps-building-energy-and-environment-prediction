# Model card: bdg2-Robin_public_Cami

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:44:48 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `481e4adf742dc0f2`, prepared `eb0b45cffe3669ec`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-17 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 12.6 to 126 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-18 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 8.615 | 13.269 |
| MAE (kWh) | 5.880 | 7.641 |
| CV(RMSE) % | 15.964 | 24.588 |
| NMBE % | -3.083 | -5.972 |
| R² | 0.781 | 0.481 |

Skill vs same_time_last_week: 0.35.

90% prediction interval: ±10.8 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (84%), calendar (time of day, weekday) (13%), airTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.351 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 16.0%, NMBE -3.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2260 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
