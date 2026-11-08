# Model card: bdg2-Hog_office_Catharine

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:48:23 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `48801bc9ec24114c`, prepared `a658dda9829ecf87`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 17:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 172 to 1.06e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 18:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 83.058 | 94.653 |
| MAE (kWh) | 55.839 | 72.617 |
| CV(RMSE) % | 19.952 | 22.738 |
| NMBE % | -4.829 | -6.724 |
| R² | 0.333 | 0.134 |

Skill vs time_of_week_profile: 0.12.

90% prediction interval: ±249 kWh; it contained 98% of test values.

Main inputs: calendar (time of day, weekday) (39%), electricity (recent history) (30%), airTemperature (23%), dewTemperature (8%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.122 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 20.0%, NMBE -4.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2540 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
