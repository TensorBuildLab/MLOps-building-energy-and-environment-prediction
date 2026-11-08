# Model card: bdg2-Bear_education_Arnold

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:43:16 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7a80d3902452eacc`, prepared `d31d5d4466cb2a27`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.205 to 2.43 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.413 | 0.419 |
| MAE (kWh) | 0.238 | 0.246 |
| CV(RMSE) % | 72.770 | 73.846 |
| NMBE % | 5.841 | 5.834 |
| R² | 0.065 | 0.037 |

Skill vs time_of_day_profile: 0.01.

90% prediction interval: ±0.233 kWh; it contained 75% of test values.

Main inputs: electricity (recent history) (72%), calendar (time of day, weekday) (26%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.015 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 72.8%, NMBE 5.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2543 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_day_profile on test data (skill 0.01).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
