# Model card: bdg2-Crow_education_Marlin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-11-07T22:39:13 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `b303699dcde78a60`, prepared `fbdb0216b926135f`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-14 08:00:00 to 2017-08-14 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 64.2 to 711 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-15 01:00:00 to 2017-11-23 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 35.449 | 36.286 |
| MAE (kWh) | 23.319 | 21.991 |
| CV(RMSE) % | 14.120 | 14.454 |
| NMBE % | -1.734 | -0.697 |
| R² | 0.899 | 0.894 |

Skill vs persistence: 0.02.

90% prediction interval: ±77.6 kWh; it contained 95% of test values.

Main inputs: electricity (recent history) (89%), airTemperature (5%), calendar (time of day, weekday) (3%), dewTemperature (1%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.023 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.1%, NMBE -1.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2423 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.02).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
