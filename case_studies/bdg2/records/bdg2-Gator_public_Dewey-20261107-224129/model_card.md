# Model card: bdg2-Gator_public_Dewey

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-11-07T22:41:29 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4641070072bab1e8`, prepared `aab9856a81633abe`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.292 to 9.71 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-23 00:00:00 to 2017-12-31 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.321 | 1.136 |
| MAE (kWh) | 0.819 | 0.656 |
| CV(RMSE) % | 23.237 | 19.982 |
| NMBE % | 1.059 | 1.989 |
| R² | 0.556 | 0.672 |

Skill vs towt: -0.16.

90% prediction interval: ±1.75 kWh; it contained 92% of test values.

Main inputs: calendar (time of day, weekday) (80%), dewTemperature (15%), electricity (recent history) (4%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.163 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 23.2%, NMBE 1.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 642 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than towt on test data (skill -0.16).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
