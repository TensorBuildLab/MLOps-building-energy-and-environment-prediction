# Run report: bdg2-Moose_education_Marina

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 33.3584 for 7 d 18 h (2016-12-04 17:00:00 to 2016-12-12 11:00:00); 249 such stretch(es), 101 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 249 stuck stretch(es) set to missing. (1192)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 21:00:00 | 11423 |
| val | 2017-06-10 22:00:00 | 2017-09-19 20:00:00 | 2423 |
| test | 2017-09-20 21:00:00 | 2017-12-31 23:00:00 | 2425 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 2.851 | 2.170 | 7.369 | -1.623 | 0.933 |
| gbm | ml | 3.075 | 2.336 | 7.947 | -2.437 | 0.923 |
| ridge | ml | 3.362 | 2.532 | 8.691 | -0.215 | 0.907 |
| same_time_last_week | baseline | 3.733 | 2.620 | 9.649 | -0.270 | 0.886 |
| towt | baseline | 3.820 | 3.184 | 9.873 | -3.957 | 0.880 |
| time_of_week_profile | baseline | 4.159 | 3.521 | 10.748 | -5.828 | 0.858 |
| time_of_day_profile | baseline | 4.177 | 3.509 | 10.795 | -5.835 | 0.857 |
| persistence | baseline | 8.577 | 4.832 | 22.167 | 0.358 | 0.397 |
| same_time_yesterday | baseline | 8.577 | 4.832 | 22.167 | 0.358 | 0.397 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.315 | 5.730 |
| MAE (kWh) | 2.987 | 3.997 |
| CV(RMSE) % | 10.565 | 14.027 |
| NMBE % | -0.313 | 0.180 |
| R² | 0.770 | 0.594 |

Skill vs same_time_last_week: **0.25** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.6% (limit 30%), NMBE -0.3% (limit ±10%): **passes**.

90% prediction interval: ±4.53 kWh (width from validation errors); it contained 79% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-16 | 1632 | 0.31 |
| 2017-08-16 to 2017-10-23 | 1632 | 0.26 |
| 2017-10-23 to 2017-12-31 | 1632 | 0.25 |

Pooled skill: **0.27**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 68% |
| calendar (time of day, weekday) | 31% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
