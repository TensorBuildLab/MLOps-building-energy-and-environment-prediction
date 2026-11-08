# Run report: bdg2-Peacock_lodging_Terrie

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
| train | 2016-01-01 00:00:00 | 2017-05-27 04:00:00 | 12252 |
| val | 2017-05-28 05:00:00 | 2017-09-13 13:00:00 | 2601 |
| test | 2017-09-14 14:00:00 | 2017-12-31 23:00:00 | 2602 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 5.956 | 4.647 | 16.332 | -1.837 | 0.431 |
| gbm_change | ml | 5.993 | 4.676 | 16.433 | -1.384 | 0.424 |
| gbm | ml | 6.174 | 4.814 | 16.930 | -1.732 | 0.389 |
| persistence | baseline | 7.146 | 5.313 | 19.594 | -0.158 | 0.181 |
| same_time_yesterday | baseline | 7.146 | 5.313 | 19.594 | -0.158 | 0.181 |
| same_time_last_week | baseline | 8.495 | 6.291 | 23.294 | -2.021 | -0.157 |
| towt | baseline | 8.975 | 6.845 | 24.609 | -9.136 | -0.291 |
| time_of_day_profile | baseline | 9.888 | 7.907 | 27.112 | -16.556 | -0.567 |
| time_of_week_profile | baseline | 9.891 | 7.885 | 27.120 | -16.545 | -0.568 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 6.349 | 7.869 |
| MAE (kWh) | 5.070 | 5.827 |
| CV(RMSE) % | 19.115 | 23.692 |
| NMBE % | -4.528 | -0.073 |
| R² | 0.236 | -0.175 |

Skill vs persistence: **0.19** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 19.1% (limit 30%), NMBE -4.5% (limit ±10%): **passes**.

90% prediction interval: ±9.52 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1751 | 0.19 |
| 2017-08-08 to 2017-10-20 | 1750 | 0.16 |
| 2017-10-20 to 2017-12-31 | 1750 | 0.19 |

Pooled skill: **0.18**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 84% |
| calendar (time of day, weekday) | 15% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
