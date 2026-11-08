# Run report: bdg2-Wolf_retail_Toshia

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
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 28.861 | 17.950 | 37.261 | 1.836 | 0.638 |
| gbm | ml | 29.265 | 18.437 | 37.782 | 1.866 | 0.627 |
| ridge | ml | 30.564 | 21.585 | 39.460 | 0.565 | 0.594 |
| towt | baseline | 31.681 | 19.883 | 40.901 | 3.617 | 0.563 |
| time_of_day_profile | baseline | 32.028 | 20.097 | 41.349 | 9.038 | 0.554 |
| time_of_week_profile | baseline | 32.206 | 20.228 | 41.579 | 9.016 | 0.549 |
| same_time_yesterday | baseline | 38.470 | 21.538 | 49.666 | -0.079 | 0.356 |
| persistence | baseline | 38.470 | 21.538 | 49.666 | -0.079 | 0.356 |
| same_time_last_week | baseline | 41.046 | 24.935 | 52.992 | 0.879 | 0.267 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 25.471 | 32.417 |
| MAE (kWh) | 15.816 | 21.147 |
| CV(RMSE) % | 38.679 | 49.227 |
| NMBE % | -2.120 | -6.337 |
| R² | 0.737 | 0.573 |

Skill vs towt: **0.21** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 38.7% (limit 30%), NMBE -2.1% (limit ±10%): **does not pass**.

90% prediction interval: ±45.8 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.11 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.06 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.24 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 64% |
| electricity (recent history) | 36% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
