# Run report: bdg2-Mouse_health_Modesto

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 864.617 for 8 d 22 h (2016-01-06 01:00:00 to 2016-01-14 23:00:00); 23 such stretch(es), 49 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
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
| train | 2016-01-01 00:00:00 | 2017-04-12 06:00:00 | 10368 |
| val | 2017-04-13 07:00:00 | 2017-07-23 08:00:00 | 2197 |
| test | 2017-07-24 09:00:00 | 2017-10-23 23:00:00 | 2199 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 83.948 | 62.351 | 18.803 | -3.055 | 0.308 |
| persistence | baseline | 93.657 | 62.917 | 20.977 | -1.093 | 0.138 |
| same_time_yesterday | baseline | 93.657 | 62.917 | 20.977 | -1.093 | 0.138 |
| gbm_change | ml | 98.692 | 75.777 | 22.105 | -0.185 | 0.043 |
| gbm | ml | 120.189 | 79.178 | 26.920 | -2.959 | -0.419 |
| same_time_last_week | baseline | 126.960 | 97.854 | 28.437 | -0.898 | -0.584 |
| time_of_week_profile | baseline | 149.351 | 126.453 | 33.452 | -27.224 | -1.191 |
| time_of_day_profile | baseline | 149.383 | 126.451 | 33.459 | -27.188 | -1.192 |
| towt | baseline | 165.217 | 141.696 | 37.005 | -31.237 | -1.682 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 56.405 | 68.021 |
| MAE (kWh) | 41.955 | 45.794 |
| CV(RMSE) % | 14.445 | 17.420 |
| NMBE % | -0.554 | -0.338 |
| R² | 0.618 | 0.444 |

Skill vs persistence: **0.17** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.4% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±143 kWh (width from validation errors); it contained 97% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-12 to 2017-06-21 | 1482 | 0.12 |
| 2017-06-21 to 2017-08-23 | 1481 | 0.12 |
| 2017-08-23 to 2017-10-23 | 1481 | 0.15 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 83% |
| calendar (time of day, weekday) | 15% |
| dewTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
