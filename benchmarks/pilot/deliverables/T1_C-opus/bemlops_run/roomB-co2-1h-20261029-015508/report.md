# Run report: roomB-co2-1h

**Task:** forecast co2_chg (other, None) 1 h ahead (4 step(s) of 15 min)

## Data check

9020 raw rows from 2023-02-27 00:00:00+01:00 to 2023-05-31 23:45:00+02:00, typical step 15 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `columns:undeclared` | 10 column(s) are not declared and will be ignored: light_level, people, radiator_valve, vent_power, supply_temp, wind, sol_south, sol_east .... | Declare any you want the model to use. |
| warning | `spikes:co2` | 1 single-sample spike(s), e.g. 893 at 2023-04-21 16:00:00+02:00. | prepare() treats them as missing. |
| warning | `stuck:oat` | Sensor repeats exactly 7.16995 for 9 h 15 min (2023-03-21 21:15:00+01:00 to 2023-03-22 06:30:00+01:00); 5 such stretch(es), 1 d 14 h 30 min in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Timestamps carry +0100/+0200 offsets (DST); parsed to UTC and converted to Europe/Copenhagen.
- One day (2023-05-24 23:05 to 2023-05-25 23:00) was exported twice with identical values; duplicate timestamps averaged.
- Rows 2023-04-24 13:05-15:30 were exported in reverse order; sorted by time.
- 12 h gap 2023-04-02 07:40-19:45 left missing (inputs forward-filled at most 1 h, target never).
- RoomB:Sensor__room_temperature switched from degC to degF on 2023-05-12 (values 72-83). Readings above 50 converted from degF reading by reading in the loader (causal).
- Outdoor temperature has 8 isolated readings of 57-73 degC; masked in the loader as impossible.
- CO2 has 16 placeholder readings of -999; masked. Wind speed has 'OFFLINE' text; not used.
- CO2 sensor reports on change of value with ~50 ppm steps, so it is flat for days when the room is empty; declared flat_ok=True rather than masking those stretches.
- Stuck and spike masking in prepare() disabled: both look at later readings to decide whether a reading is bad, which a live 1 h forecast cannot do; all cleaning is row-by-row in the loader.
- RoomB:People__amount missing 62% (absent from 2023-04-18 on); not used.
- Setpoints (22 / 20.5 / 23.5 degC) never change; not used. Heating, solar, lighting level and wind not used (no clear link to room CO2 at 1 h).
- Operation change on 2023-05-04: ventilation schedule moved from 08:00-16:15 to 05:00-21:00 (plus 23:00 night flushing) and the window is open most of the time from 2023-05-08. Derived inputs describe the fan schedule seen 24 h / 7 d earlier at the target time of day.
- Split fractions 0.8/0.1/0.1 instead of 0.7/0.15/0.15: with the default split the training set ends on 2023-05-03 and contains none of the summer ventilation schedule, so no model can learn it; persistence then wins validation. With 0.8/0.1/0.1 training includes ~9 days of it.
- Target is the 1 h change of the 15-min mean CO2 (forecast = last known 15-min mean + predicted change). Tree models on the level could not reproduce flat periods exactly; on the same split the change target gave lower RMSE. NOTE: bemlops' 'persistence' baseline for this target means 'the last hour's change repeats'; the honest baseline is zero change (= CO2 persistence), computed separately in report.json.
- random_forest left out: tuning it took >30 min on this (shared) machine and it did not beat ridge or gbm in a first run.

## Preparation

- convert_units `supply_flow`: Converted m3/h to m3/s.
- resample: Resampled to a regular 15 min grid (9020 rows). (9020)
- forward_fill `co2`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `room_temp`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `room_active`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `damper`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `light_on`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `window`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `supply_flow`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `oat`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `fan_on_24h`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `fan_on_7d`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `active_24h`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `active_7d`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `co2_d30`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `co2_d60`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `active_1h`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `fan_change_exp`: Filled input gaps up to 1h with the last known value. (10)
- forward_fill `excess_vent`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `excess_novent`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `active_vent`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `active_novent`: Filled input gaps up to 1h with the last known value. (9)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2023-02-27 02:00:00+01:00 | 2023-05-13 07:15:00+02:00 | 7164 |
| val | 2023-05-13 08:30:00+02:00 | 2023-05-22 15:30:00+02:00 | 891 |
| test | 2023-05-22 16:45:00+02:00 | 2023-05-31 23:45:00+02:00 | 893 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 17.413 | 9.870 | 10488.722 | -990.610 | 0.237 |
| ridge | ml | 19.891 | 12.399 | 11981.684 | -467.189 | 0.005 |
| same_time_yesterday | baseline | 25.349 | 12.288 | 15269.129 | 14.630 | -0.616 |
| persistence | baseline | 27.752 | 12.016 | 16716.611 | -67.657 | -0.937 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE | 27.177 | 47.978 |
| MAE | 15.033 | 22.802 |
| CV(RMSE) % | -101177.065 | -178616.501 |
| NMBE % | 8670.066 | -0.000 |
| R² | 0.345 | -1.042 |

Skill vs persistence: **0.43** (1 = perfect, 0 = no better than the baseline).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
