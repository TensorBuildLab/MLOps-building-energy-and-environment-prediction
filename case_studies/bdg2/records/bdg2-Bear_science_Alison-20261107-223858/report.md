# Run report: bdg2-Bear_science_Alison

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 05:00:00 | 12257 |
| val | 2017-05-27 06:00:00 | 2017-09-12 20:00:00 | 2602 |
| test | 2017-09-13 21:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 4.571 | 2.950 | 4.326 | 0.433 | 0.643 |
| ridge | ml | 4.794 | 3.149 | 4.537 | 0.102 | 0.607 |
| gbm_change | ml | 4.928 | 3.068 | 4.665 | 0.476 | 0.585 |
| towt | baseline | 5.362 | 3.777 | 5.076 | 0.922 | 0.509 |
| same_time_last_week | baseline | 6.202 | 4.065 | 5.871 | 0.424 | 0.343 |
| persistence | baseline | 6.233 | 3.972 | 5.900 | 0.111 | 0.336 |
| same_time_yesterday | baseline | 6.233 | 3.972 | 5.900 | 0.111 | 0.336 |
| time_of_day_profile | baseline | 6.552 | 4.626 | 6.202 | 2.869 | 0.267 |
| time_of_week_profile | baseline | 6.596 | 4.640 | 6.243 | 2.870 | 0.257 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.554 | 4.904 |
| MAE (kWh) | 2.673 | 3.970 |
| CV(RMSE) % | 3.394 | 4.684 |
| NMBE % | -0.566 | 2.330 |
| R² | 0.765 | 0.553 |

Skill vs towt: **0.28** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.4% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±6.15 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1751 | 0.03 |
| 2017-08-07 to 2017-10-19 | 1751 | 0.30 |
| 2017-10-19 to 2017-12-31 | 1751 | 0.30 |

Pooled skill: **0.21**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 26% |
| airTemperature | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
