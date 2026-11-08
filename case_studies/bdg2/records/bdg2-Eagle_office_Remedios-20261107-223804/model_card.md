# Model card: bdg2-Eagle_office_Remedios

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:38:04 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ebe34ce362958b95`, prepared `63cc42b7fe2845f5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-01 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 17.6 to 155 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-02 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 7.265 | 6.747 |
| MAE (kWh) | 5.205 | 4.818 |
| CV(RMSE) % | 7.995 | 7.425 |
| NMBE % | 0.400 | 2.514 |
| R² | 0.695 | 0.737 |

Skill vs time_of_week_profile: -0.08.

90% prediction interval: ±11.2 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (60%), calendar (time of day, weekday) (40%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.077 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.0%, NMBE 0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2422 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than time_of_week_profile on test data (skill -0.08).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
