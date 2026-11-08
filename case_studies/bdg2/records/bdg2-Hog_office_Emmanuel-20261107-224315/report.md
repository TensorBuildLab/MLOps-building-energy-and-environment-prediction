# Run report: bdg2-Hog_office_Emmanuel

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 58.293 for 12 h (2016-06-09 13:00:00 to 2016-06-10 01:00:00); 2 such stretch(es), 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 2 stuck stretch(es) set to missing. (9)
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
| train | 2016-01-01 00:00:00 | 2017-05-27 23:00:00 | 12181 |
| val | 2017-05-29 00:00:00 | 2017-09-14 04:00:00 | 2586 |
| test | 2017-09-15 05:00:00 | 2017-12-31 23:00:00 | 2587 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 2.339 | 1.567 | 8.732 | -0.714 | 0.881 |
| gbm | ml | 2.388 | 1.601 | 8.915 | -0.625 | 0.876 |
| ridge | ml | 2.405 | 1.662 | 8.978 | 0.509 | 0.875 |
| towt | baseline | 2.617 | 1.788 | 9.770 | -1.154 | 0.852 |
| same_time_yesterday | baseline | 2.930 | 1.992 | 10.940 | 0.218 | 0.814 |
| persistence | baseline | 2.930 | 1.992 | 10.940 | 0.218 | 0.814 |
| time_of_week_profile | baseline | 3.074 | 2.383 | 11.476 | -5.390 | 0.795 |
| time_of_day_profile | baseline | 3.120 | 2.408 | 11.650 | -5.386 | 0.789 |
| same_time_last_week | baseline | 3.197 | 2.058 | 11.934 | 0.363 | 0.779 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.891 | 2.310 |
| MAE (kWh) | 1.356 | 1.736 |
| CV(RMSE) % | 6.769 | 8.268 |
| NMBE % | -0.188 | -1.935 |
| R² | 0.915 | 0.873 |

Skill vs towt: **0.18** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.8% (limit 30%), NMBE -0.2% (limit ±10%): **passes**.

90% prediction interval: ±3.44 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-08 | 1741 | 0.11 |
| 2017-08-09 to 2017-10-20 | 1740 | 0.11 |
| 2017-10-20 to 2017-12-31 | 1740 | 0.22 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 80% |
| calendar (time of day, weekday) | 20% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
