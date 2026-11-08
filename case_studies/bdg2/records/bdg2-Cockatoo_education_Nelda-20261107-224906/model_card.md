# Model card: bdg2-Cockatoo_education_Nelda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-11-07T22:49:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4e621515c4e4f70b`, prepared `ee4d858b4701ece4`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 21:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 33.3 to 180 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 22:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 7.367 | 8.583 |
| MAE (kWh) | 5.624 | 6.197 |
| CV(RMSE) % | 6.766 | 7.882 |
| NMBE % | -0.942 | -0.029 |
| R² | 0.620 | 0.484 |

Skill vs same_time_last_week: 0.14.

90% prediction interval: ±12.8 kWh; it contained 92% of test values.

Main inputs: electricity (recent history) (72%), calendar (time of day, weekday) (25%), airTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.142 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.8%, NMBE -0.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2393 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
