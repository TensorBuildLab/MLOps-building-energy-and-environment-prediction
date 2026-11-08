# Model card: bdg2-Bobcat_other_Jovita

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:48:33 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `a2f9006c790dc0bc`, prepared `27ab92655cfa0175`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-18 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1 to 680 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-19 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.947 | 10.298 |
| MAE (kWh) | 6.107 | 4.347 |
| CV(RMSE) % | 98.086 | 112.895 |
| NMBE % | -19.745 | -16.454 |
| R² | 0.290 | 0.060 |

Skill vs persistence: 0.13.

90% prediction interval: ±62.3 kWh; it contained 100% of test values.

Main inputs: electricity (recent history) (80%), dewTemperature (9%), airTemperature (9%), windSpeed (2%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.131 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 98.1%, NMBE -19.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2364 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
