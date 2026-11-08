# Model card: bdg2-Crow_education_Winston

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-10-29T02:29:18 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `a296f36a7e8603d0`, prepared `84ac81eef690deb5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-12 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 9.5 to 658 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-13 13:00:00 to 2017-11-23 22:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 42.050 | 50.302 |
| MAE (kWh) | 30.317 | 31.674 |
| CV(RMSE) % | 11.831 | 14.153 |
| NMBE % | -1.772 | -0.403 |
| R² | 0.888 | 0.839 |

Skill vs persistence: 0.16.

90% prediction interval: ±71 kWh; it contained 92% of test values.

Main inputs: electricity (recent history) (89%), calendar (time of day, weekday) (8%), airTemperature (3%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.164 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 11.8%, NMBE -1.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2458 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
