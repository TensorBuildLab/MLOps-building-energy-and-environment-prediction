# Run report: bdg2-Hog_services_Kerrie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 15.253 for 9 h (2017-02-15 00:00:00 to 2017-02-15 09:00:00); 6 such stretch(es), 1 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 6 stuck stretch(es) set to missing. (9)
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
| train | 2016-01-01 00:00:00 | 2017-05-26 18:00:00 | 12274 |
| val | 2017-05-27 19:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.414 | 2.370 | 16.904 | -0.058 | 0.690 |
| gbm_change | ml | 3.421 | 2.323 | 16.938 | 0.399 | 0.689 |
| ridge | ml | 3.614 | 2.621 | 17.892 | -1.454 | 0.653 |
| towt | baseline | 3.660 | 2.734 | 18.119 | 1.545 | 0.644 |
| time_of_week_profile | baseline | 3.747 | 2.795 | 18.553 | 3.257 | 0.627 |
| time_of_day_profile | baseline | 3.806 | 2.839 | 18.845 | 3.274 | 0.615 |
| same_time_last_week | baseline | 4.296 | 3.011 | 21.268 | -1.329 | 0.509 |
| persistence | baseline | 5.481 | 3.638 | 27.138 | 0.238 | 0.201 |
| same_time_yesterday | baseline | 5.481 | 3.638 | 27.138 | 0.238 | 0.201 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 2.720 | 3.079 |
| MAE (kWh) | 1.880 | 2.245 |
| CV(RMSE) % | 14.791 | 16.742 |
| NMBE % | -2.401 | -5.846 |
| R² | 0.689 | 0.601 |

Skill vs towt: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.8% (limit 30%), NMBE -2.4% (limit ±10%): **passes**.

90% prediction interval: ±5.45 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.09 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.00 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.13 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 58% |
| electricity (recent history) | 42% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
