# Run report: bdg2-Wolf_science_Alfreda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 16:00:00 | 12275 |
| val | 2017-05-27 17:00:00 | 2017-09-13 06:00:00 | 2606 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 8.409 | 6.306 | 11.451 | -3.112 | 0.363 |
| gbm_change | ml | 8.661 | 6.602 | 11.794 | -4.930 | 0.324 |
| gbm | ml | 8.859 | 7.082 | 12.064 | -6.044 | 0.293 |
| persistence | baseline | 8.965 | 5.703 | 12.208 | 0.074 | 0.275 |
| same_time_yesterday | baseline | 8.965 | 5.703 | 12.208 | 0.074 | 0.275 |
| towt | baseline | 12.041 | 10.642 | 16.397 | -10.365 | -0.307 |
| same_time_last_week | baseline | 13.516 | 8.976 | 18.405 | -0.292 | -0.647 |
| time_of_day_profile | baseline | 14.105 | 12.760 | 19.208 | -14.325 | -0.794 |
| time_of_week_profile | baseline | 14.124 | 12.778 | 19.233 | -14.334 | -0.798 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.159 | 9.241 |
| MAE (kWh) | 5.853 | 5.706 |
| CV(RMSE) % | 10.545 | 11.944 |
| NMBE % | -2.475 | -0.034 |
| R² | 0.438 | 0.279 |

Skill vs persistence: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.5% (limit 30%), NMBE -2.5% (limit ±10%): **passes**.

90% prediction interval: ±13.9 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.06 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.10 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.13 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 72% |
| calendar (time of day, weekday) | 28% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
