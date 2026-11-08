# Run report: bdg2-Hog_office_Shawna

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2609 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 26.783 | 16.831 | 19.987 | 0.678 | 0.848 |
| gbm | ml | 27.691 | 17.985 | 20.664 | 0.477 | 0.838 |
| time_of_week_profile | baseline | 28.676 | 20.760 | 21.400 | -6.847 | 0.826 |
| ridge | ml | 28.990 | 19.325 | 21.634 | 0.395 | 0.822 |
| towt | baseline | 31.430 | 24.171 | 23.455 | -9.919 | 0.791 |
| time_of_day_profile | baseline | 31.654 | 23.258 | 23.622 | -6.904 | 0.788 |
| same_time_last_week | baseline | 33.276 | 20.579 | 24.832 | 0.738 | 0.766 |
| persistence | baseline | 49.611 | 29.741 | 37.022 | 0.436 | 0.479 |
| same_time_yesterday | baseline | 49.611 | 29.741 | 37.022 | 0.436 | 0.479 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 18.211 | 23.631 |
| MAE (kWh) | 10.117 | 16.262 |
| CV(RMSE) % | 12.632 | 16.392 |
| NMBE % | 0.453 | 1.701 |
| R² | 0.945 | 0.907 |

Skill vs time_of_week_profile: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 12.6% (limit 30%), NMBE 0.5% (limit ±10%): **passes**.

90% prediction interval: ±37.5 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.09 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.09 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.35 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 29% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
