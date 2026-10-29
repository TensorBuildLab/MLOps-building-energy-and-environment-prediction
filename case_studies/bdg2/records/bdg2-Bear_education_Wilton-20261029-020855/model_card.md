# Model card: bdg2-Bear_education_Wilton

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:08:55 with bemlops 0.2.0.dev0 (code e85edf1)
- **Data fingerprint:** raw `60cd958efd5ab5c8`, prepared `e7ce2359909219f6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 225 to 2.34e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 111.449 | 128.364 |
| MAE (kWh) | 86.691 | 88.930 |
| CV(RMSE) % | 6.700 | 7.717 |
| NMBE % | 1.586 | -0.078 |
| R² | 0.581 | 0.444 |

Skill vs persistence: 0.13.

90% prediction interval: ±164 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (82%), calendar (time of day, weekday) (16%), windSpeed (2%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.132 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 6.7%, NMBE 1.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2606 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
