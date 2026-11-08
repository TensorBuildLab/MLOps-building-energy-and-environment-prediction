# Model card: bdg2-Bear_education_Irene

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:44:02 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f9c6cacb5ecc74a4`, prepared `f02b3f78b47bf3bf`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 46.6 to 198 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 27.903 | 28.355 |
| MAE (kWh) | 21.088 | 22.119 |
| CV(RMSE) % | 34.773 | 35.337 |
| NMBE % | -13.137 | -12.446 |
| R² | -0.099 | -0.135 |

Skill vs time_of_day_profile: 0.02.

90% prediction interval: ±53.7 kWh; it contained 91% of test values.

Main inputs: calendar (time of day, weekday) (51%), electricity (recent history) (49%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.016 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 34.8%, NMBE -13.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2602 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill 0.02).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
