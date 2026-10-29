# Model card: bdg2-Bobcat_lodging_Nickolas

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:20:28 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `305b3519d530b64c`, prepared `3e621fee9c9aa7e2`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 6.5 to 94 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.951 | 5.186 |
| MAE (kWh) | 3.726 | 3.477 |
| CV(RMSE) % | 14.450 | 15.136 |
| NMBE % | -6.490 | 0.053 |
| R² | 0.103 | 0.015 |

Skill vs persistence: 0.05.

90% prediction interval: ±6.66 kWh; it contained 87% of test values.

Main inputs: electricity (recent history) (91%), calendar (time of day, weekday) (5%), airTemperature (5%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.045 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 14.4%, NMBE -6.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2451 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.05).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
