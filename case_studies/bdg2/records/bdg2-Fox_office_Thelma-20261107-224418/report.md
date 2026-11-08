# Run report: bdg2-Fox_office_Thelma

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
| train | 2016-01-01 00:00:00 | 2017-05-26 16:00:00 | 12279 |
| val | 2017-05-27 17:00:00 | 2017-09-13 07:00:00 | 2607 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 18.783 | 10.885 | 15.186 | -0.561 | 0.853 |
| gbm_change | ml | 18.947 | 10.701 | 15.319 | -1.424 | 0.850 |
| towt | baseline | 19.591 | 14.741 | 15.839 | -2.488 | 0.840 |
| time_of_week_profile | baseline | 19.644 | 14.741 | 15.883 | -0.512 | 0.839 |
| time_of_day_profile | baseline | 19.684 | 14.682 | 15.915 | -0.531 | 0.839 |
| ridge | ml | 21.190 | 13.173 | 17.132 | 0.404 | 0.813 |
| same_time_last_week | baseline | 24.050 | 12.762 | 19.445 | 0.770 | 0.759 |
| persistence | baseline | 38.187 | 20.562 | 30.874 | 0.417 | 0.392 |
| same_time_yesterday | baseline | 38.187 | 20.562 | 30.874 | 0.417 | 0.392 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 17.333 | 20.525 |
| MAE (kWh) | 10.238 | 14.226 |
| CV(RMSE) % | 13.960 | 16.531 |
| NMBE % | -1.902 | 0.874 |
| R² | 0.885 | 0.839 |

Skill vs towt: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.0% (limit 30%), NMBE -1.9% (limit ±10%): **passes**.

90% prediction interval: ±26.1 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.15 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.07 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.17 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 56% |
| calendar (time of day, weekday) | 43% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
