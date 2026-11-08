# Run report: bdg2-Peacock_education_Forest

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
| train | 2016-01-01 00:00:00 | 2017-05-27 03:00:00 | 12252 |
| val | 2017-05-28 04:00:00 | 2017-09-13 12:00:00 | 2601 |
| test | 2017-09-14 13:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 8.066 | 5.557 | 9.855 | -1.523 | 0.705 |
| gbm_change | ml | 8.725 | 6.203 | 10.660 | -3.194 | 0.655 |
| gbm | ml | 8.814 | 6.256 | 10.769 | -3.005 | 0.648 |
| persistence | baseline | 9.663 | 6.554 | 11.807 | 0.286 | 0.577 |
| same_time_yesterday | baseline | 9.663 | 6.554 | 11.807 | 0.286 | 0.577 |
| same_time_last_week | baseline | 10.248 | 7.141 | 12.521 | 0.295 | 0.524 |
| time_of_day_profile | baseline | 12.027 | 9.474 | 14.695 | -9.275 | 0.345 |
| time_of_week_profile | baseline | 12.053 | 9.457 | 14.728 | -9.254 | 0.342 |
| towt | baseline | 13.552 | 10.943 | 16.559 | -11.691 | 0.168 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 9.502 | 10.645 |
| MAE (kWh) | 6.819 | 7.190 |
| CV(RMSE) % | 10.428 | 11.682 |
| NMBE % | 0.923 | 0.120 |
| R² | 0.662 | 0.576 |

Skill vs persistence: **0.11** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.4% (limit 30%), NMBE 0.9% (limit ±10%): **passes**.

90% prediction interval: ±11.7 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1751 | 0.15 |
| 2017-08-08 to 2017-10-20 | 1751 | 0.27 |
| 2017-10-20 to 2017-12-31 | 1750 | -0.02 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 86% |
| calendar (time of day, weekday) | 13% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
