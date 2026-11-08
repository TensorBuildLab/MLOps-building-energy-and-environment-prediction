# Run report: bdg2-Mouse_health_Justin

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 663.343 for 8 d 22 h (2016-01-06 01:00:00 to 2016-01-14 23:00:00); 23 such stretch(es), 49 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 23 stuck stretch(es) set to missing. (1069)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-12 04:00:00 | 10361 |
| val | 2017-04-13 05:00:00 | 2017-07-23 06:00:00 | 2196 |
| test | 2017-07-24 07:00:00 | 2017-10-23 23:00:00 | 2197 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 96.012 | 68.678 | 10.884 | 2.437 | 0.767 |
| towt | baseline | 103.174 | 80.691 | 11.696 | 6.617 | 0.730 |
| gbm_change | ml | 105.531 | 72.259 | 11.963 | 3.703 | 0.718 |
| gbm | ml | 105.741 | 76.351 | 11.987 | 4.779 | 0.717 |
| same_time_yesterday | baseline | 123.665 | 84.432 | 14.019 | 1.044 | 0.613 |
| persistence | baseline | 123.665 | 84.432 | 14.019 | 1.044 | 0.613 |
| same_time_last_week | baseline | 153.676 | 118.928 | 17.421 | 3.004 | 0.402 |
| time_of_week_profile | baseline | 189.148 | 150.550 | 21.442 | 14.574 | 0.094 |
| time_of_day_profile | baseline | 189.386 | 151.129 | 21.469 | 14.582 | 0.092 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 80.760 | 100.523 |
| MAE (kWh) | 60.892 | 79.548 |
| CV(RMSE) % | 9.590 | 11.937 |
| NMBE % | -0.748 | 1.693 |
| R² | 0.809 | 0.704 |

Skill vs towt: **0.20** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.6% (limit 30%), NMBE -0.7% (limit ±10%): **passes**.

90% prediction interval: ±159 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-12 to 2017-06-21 | 1481 | -0.03 |
| 2017-06-21 to 2017-08-23 | 1480 | 0.17 |
| 2017-08-23 to 2017-10-23 | 1480 | 0.22 |

Pooled skill: **0.12**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 67% |
| calendar (time of day, weekday) | 26% |
| airTemperature | 7% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
