# Run report: bdg2-Hog_warehouse_Rosanna

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 25.207 for 30 d 18 h (2016-11-28 12:00:00 to 2016-12-29 06:00:00); 1 such stretch(es), 30 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 1 stuck stretch(es) set to missing. (733)
- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-31 14:00:00 | 11666 |
| val | 2017-06-01 15:00:00 | 2017-09-17 16:00:00 | 2475 |
| test | 2017-09-18 17:00:00 | 2017-12-31 23:00:00 | 2477 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 10.375 | 7.647 | 35.357 | 4.361 | 0.245 |
| gbm_change | ml | 11.323 | 7.222 | 38.588 | 7.429 | 0.101 |
| same_time_yesterday | baseline | 11.809 | 7.385 | 40.245 | 2.955 | 0.022 |
| persistence | baseline | 11.809 | 7.385 | 40.245 | 2.955 | 0.022 |
| gbm | ml | 13.915 | 9.404 | 47.422 | 28.166 | -0.358 |
| towt | baseline | 14.475 | 9.856 | 49.330 | 30.778 | -0.469 |
| same_time_last_week | baseline | 14.489 | 10.040 | 49.377 | 6.823 | -0.472 |
| time_of_day_profile | baseline | 15.224 | 10.173 | 51.881 | 33.032 | -0.625 |
| time_of_week_profile | baseline | 15.226 | 10.177 | 51.889 | 33.034 | -0.626 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 4.523 | 5.268 |
| MAE (kWh) | 2.542 | 2.484 |
| CV(RMSE) % | 25.476 | 29.673 |
| NMBE % | -3.736 | 0.284 |
| R² | 0.390 | 0.172 |

Skill vs same_time_yesterday: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 25.5% (limit 30%), NMBE -3.7% (limit ±10%): **passes**.

90% prediction interval: ±18.6 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-31 to 2017-08-13 | 1667 | 0.12 |
| 2017-08-13 to 2017-10-23 | 1667 | 0.13 |
| 2017-10-23 to 2017-12-31 | 1666 | 0.12 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 97% |
| dewTemperature | 2% |
| calendar (time of day, weekday) | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
