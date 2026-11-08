# Run report: bdg2-Fox_education_Melvin

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 56.47 for 10 d 13 h (2016-10-05 07:00:00 to 2016-10-15 20:00:00); 7 such stretch(es), 27 d 23 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 7 stuck stretch(es) set to missing. (636)
- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-01 02:00:00 | 11766 |
| val | 2017-06-02 03:00:00 | 2017-09-14 03:00:00 | 2497 |
| test | 2017-09-15 04:00:00 | 2017-12-28 05:00:00 | 2498 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 12.206 | 8.237 | 21.185 | 2.922 | 0.828 |
| gbm | ml | 12.890 | 8.829 | 22.372 | 2.638 | 0.808 |
| ridge | ml | 13.303 | 9.788 | 23.089 | 1.645 | 0.795 |
| same_time_last_week | baseline | 15.675 | 10.168 | 27.205 | 2.539 | 0.716 |
| towt | baseline | 17.007 | 11.991 | 29.517 | 0.844 | 0.666 |
| time_of_week_profile | baseline | 17.321 | 12.886 | 30.062 | -8.713 | 0.653 |
| time_of_day_profile | baseline | 17.348 | 12.800 | 30.109 | -8.749 | 0.652 |
| persistence | baseline | 23.349 | 14.055 | 40.524 | 0.540 | 0.370 |
| same_time_yesterday | baseline | 23.349 | 14.055 | 40.524 | 0.540 | 0.370 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 12.398 | 18.478 |
| MAE (kWh) | 7.665 | 10.053 |
| CV(RMSE) % | 22.666 | 33.782 |
| NMBE % | -1.306 | -2.777 |
| R² | 0.791 | 0.535 |

Skill vs same_time_last_week: **0.33** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 22.7% (limit 30%), NMBE -1.3% (limit ±10%): **passes**.

90% prediction interval: ±21.3 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-01 to 2017-08-10 | 1681 | 0.20 |
| 2017-08-10 to 2017-10-19 | 1681 | 0.31 |
| 2017-10-19 to 2017-12-28 | 1681 | 0.34 |

Pooled skill: **0.28**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 64% |
| calendar (time of day, weekday) | 36% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
