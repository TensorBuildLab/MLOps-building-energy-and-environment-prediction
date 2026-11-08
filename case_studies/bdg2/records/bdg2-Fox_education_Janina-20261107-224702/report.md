# Run report: bdg2-Fox_education_Janina

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12251 |
| val | 2017-05-27 16:00:00 | 2017-09-13 00:00:00 | 2601 |
| test | 2017-09-14 01:00:00 | 2017-12-31 23:00:00 | 2602 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 11.912 | 7.021 | 10.367 | 0.675 | 0.704 |
| same_time_last_week | baseline | 13.310 | 6.038 | 11.584 | 0.198 | 0.630 |
| gbm | ml | 14.035 | 8.246 | 12.215 | 3.438 | 0.589 |
| gbm_change | ml | 14.823 | 8.358 | 12.901 | 3.313 | 0.542 |
| towt | baseline | 15.188 | 11.338 | 13.218 | 5.602 | 0.519 |
| persistence | baseline | 16.264 | 9.054 | 14.154 | 0.148 | 0.448 |
| same_time_yesterday | baseline | 16.264 | 9.054 | 14.154 | 0.148 | 0.448 |
| time_of_week_profile | baseline | 16.965 | 13.010 | 14.765 | -9.788 | 0.400 |
| time_of_day_profile | baseline | 17.056 | 13.031 | 14.843 | -9.791 | 0.393 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 22.515 | 29.368 |
| MAE (kWh) | 14.150 | 14.910 |
| CV(RMSE) % | 15.863 | 20.691 |
| NMBE % | 0.699 | 1.128 |
| R² | 0.628 | 0.367 |

Skill vs same_time_last_week: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.9% (limit 30%), NMBE 0.7% (limit ±10%): **passes**.

90% prediction interval: ±17.1 kWh (width from validation errors); it contained 73% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1751 | 0.10 |
| 2017-08-07 to 2017-10-19 | 1750 | 0.17 |
| 2017-10-19 to 2017-12-31 | 1750 | 0.24 |

Pooled skill: **0.21**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 90% |
| calendar (time of day, weekday) | 10% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
