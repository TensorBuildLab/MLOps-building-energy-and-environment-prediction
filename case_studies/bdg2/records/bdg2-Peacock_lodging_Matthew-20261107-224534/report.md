# Run report: bdg2-Peacock_lodging_Matthew

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
| train | 2016-01-01 00:00:00 | 2017-05-26 18:00:00 | 12273 |
| val | 2017-05-27 19:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 5.200 | 3.871 | 10.181 | -0.918 | 0.385 |
| gbm_change | ml | 5.292 | 3.998 | 10.361 | 0.032 | 0.363 |
| gbm | ml | 5.631 | 4.365 | 11.024 | -1.278 | 0.279 |
| persistence | baseline | 5.731 | 4.132 | 11.220 | -0.034 | 0.253 |
| same_time_yesterday | baseline | 5.731 | 4.132 | 11.220 | -0.034 | 0.253 |
| same_time_last_week | baseline | 9.466 | 6.667 | 18.532 | -1.866 | -1.037 |
| towt | baseline | 9.541 | 7.732 | 18.680 | -11.694 | -1.069 |
| time_of_day_profile | baseline | 12.602 | 11.284 | 24.673 | -20.844 | -2.610 |
| time_of_week_profile | baseline | 12.607 | 11.290 | 24.682 | -20.858 | -2.613 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.194 | 4.888 |
| MAE (kWh) | 3.308 | 3.732 |
| CV(RMSE) % | 7.235 | 8.432 |
| NMBE % | -1.004 | -0.090 |
| R² | 0.580 | 0.429 |

Skill vs persistence: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.2% (limit 30%), NMBE -1.0% (limit ±10%): **passes**.

90% prediction interval: ±8.17 kWh (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.12 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.10 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.12 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 93% |
| calendar (time of day, weekday) | 6% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
