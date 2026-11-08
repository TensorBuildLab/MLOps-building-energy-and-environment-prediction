# Model card: bdg2-Bobcat_office_Alma

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(4.135997393839888)}
- **Trained:** 2026-11-07T22:46:46 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `137e6fd1245e1d30`, prepared `d45167ae2df1ae60`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1 to 14 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.117 | 1.299 |
| MAE (kWh) | 0.843 | 1.033 |
| CV(RMSE) % | 31.891 | 37.088 |
| NMBE % | -4.053 | -17.592 |
| R² | 0.265 | 0.006 |

Skill vs towt: 0.14.

90% prediction interval: ±2.66 kWh; it contained 98% of test values.

Main inputs: electricity (recent history) (62%), calendar (time of day, weekday) (31%), airTemperature (6%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.140 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 31.9%, NMBE -4.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2420 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
