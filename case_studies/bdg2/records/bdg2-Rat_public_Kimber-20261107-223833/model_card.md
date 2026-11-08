# Model card: bdg2-Rat_public_Kimber

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-11-07T22:38:33 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `39f976d17060881c`, prepared `f63a8295f78fa43d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.89 to 934 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 39.160 | 44.424 |
| MAE (kWh) | 28.853 | 29.816 |
| CV(RMSE) % | 34.733 | 39.402 |
| NMBE % | 0.722 | -0.705 |
| R² | 0.403 | 0.231 |

Skill vs same_time_yesterday: 0.12.

90% prediction interval: ±99.7 kWh; it contained 97% of test values.

Main inputs: electricity (recent history) (77%), calendar (time of day, weekday) (22%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.118 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 34.7%, NMBE 0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
