# Run report: bdg2-Peacock_assembly_Socorro

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 19:00:00 | 12272 |
| val | 2017-05-27 20:00:00 | 2017-09-13 08:00:00 | 2605 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 11.211 | 7.004 | 28.863 | 0.446 | 0.612 |
| gbm | ml | 11.349 | 7.414 | 29.219 | 9.583 | 0.602 |
| gbm_change | ml | 11.490 | 7.195 | 29.579 | 8.698 | 0.593 |
| same_time_last_week | baseline | 12.191 | 7.471 | 31.384 | -0.199 | 0.541 |
| same_time_yesterday | baseline | 13.816 | 7.669 | 35.569 | 0.304 | 0.411 |
| persistence | baseline | 13.816 | 7.669 | 35.569 | 0.304 | 0.411 |
| time_of_day_profile | baseline | 28.249 | 23.693 | 72.726 | 60.980 | -1.463 |
| time_of_week_profile | baseline | 28.263 | 23.698 | 72.762 | 60.989 | -1.465 |
| towt | baseline | 30.738 | 25.737 | 79.134 | 66.271 | -1.916 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 7.857 | 12.158 |
| MAE (kWh) | 5.513 | 8.581 |
| CV(RMSE) % | 21.128 | 32.694 |
| NMBE % | 0.313 | -0.675 |
| R² | 0.692 | 0.262 |

Skill vs same_time_last_week: **0.35** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 21.1% (limit 30%), NMBE 0.3% (limit ±10%): **passes**.

90% prediction interval: ±21.8 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.12 |
| 2017-08-07 to 2017-10-19 | 1753 | 0.26 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.38 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 95% |
| calendar (time of day, weekday) | 4% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
