# Run report: bdg2-Fox_education_Tamika

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
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12275 |
| val | 2017-05-27 16:00:00 | 2017-09-13 05:00:00 | 2606 |
| test | 2017-09-14 06:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 27.127 | 20.361 | 15.257 | -1.928 | 0.762 |
| gbm | ml | 28.554 | 21.266 | 16.060 | -1.535 | 0.736 |
| gbm_change | ml | 31.638 | 22.311 | 17.794 | -3.044 | 0.676 |
| same_time_last_week | baseline | 31.882 | 23.404 | 17.931 | -0.136 | 0.671 |
| towt | baseline | 36.214 | 29.044 | 20.368 | -5.956 | 0.576 |
| time_of_day_profile | baseline | 43.864 | 34.506 | 24.670 | 15.140 | 0.378 |
| time_of_week_profile | baseline | 44.058 | 34.590 | 24.779 | 15.173 | 0.372 |
| persistence | baseline | 49.171 | 29.661 | 27.655 | 0.175 | 0.218 |
| same_time_yesterday | baseline | 49.171 | 29.661 | 27.655 | 0.175 | 0.218 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 15.860 | 18.501 |
| MAE (kWh) | 11.978 | 13.830 |
| CV(RMSE) % | 12.984 | 15.146 |
| NMBE % | -2.916 | -3.333 |
| R² | 0.656 | 0.531 |

Skill vs same_time_last_week: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.0% (limit 30%), NMBE -2.9% (limit ±10%): **passes**.

90% prediction interval: ±43.9 kWh (width from validation errors); it contained 99% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.09 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.26 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.10 |

Pooled skill: **0.15**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 76% |
| calendar (time of day, weekday) | 16% |
| airTemperature | 6% |
| windSpeed | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
