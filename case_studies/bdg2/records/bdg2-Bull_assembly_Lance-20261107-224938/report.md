# Run report: bdg2-Bull_assembly_Lance

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 01:00:00 | 12061 |
| val | 2017-05-28 02:00:00 | 2017-09-11 19:00:00 | 2560 |
| test | 2017-09-12 20:00:00 | 2017-12-31 23:00:00 | 2562 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 40.563 | 19.476 | 8.764 | -0.545 | 0.401 |
| same_time_last_week | baseline | 49.910 | 21.110 | 10.783 | 0.715 | 0.093 |
| same_time_yesterday | baseline | 52.349 | 22.237 | 11.310 | 0.084 | 0.003 |
| persistence | baseline | 52.349 | 22.237 | 11.310 | 0.084 | 0.003 |
| gbm | ml | 52.679 | 25.563 | 11.382 | -0.808 | -0.010 |
| time_of_day_profile | baseline | 53.312 | 32.843 | 11.518 | 3.824 | -0.034 |
| towt | baseline | 53.339 | 25.301 | 11.524 | 0.347 | -0.035 |
| time_of_week_profile | baseline | 55.843 | 33.644 | 12.065 | 3.834 | -0.135 |
| gbm_change | ml | 56.942 | 26.476 | 12.303 | -0.180 | -0.180 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 307.172 | 495.345 |
| MAE (kWh) | 34.899 | 54.874 |
| CV(RMSE) % | 65.371 | 105.418 |
| NMBE % | 2.540 | -1.009 |
| R² | 0.237 | -0.983 |

Skill vs same_time_last_week: **0.38** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 65.4% (limit 30%), NMBE 2.5% (limit ±10%): **does not pass**.

90% prediction interval: ±37.7 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1724 | 0.14 |
| 2017-08-06 to 2017-10-17 | 1723 | 0.20 |
| 2017-10-17 to 2017-12-31 | 1723 | 0.38 |

Pooled skill: **0.38**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 99% |
| calendar (time of day, weekday) | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
