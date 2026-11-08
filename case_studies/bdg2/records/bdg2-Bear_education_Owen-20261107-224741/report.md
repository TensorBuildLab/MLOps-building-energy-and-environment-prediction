# Run report: bdg2-Bear_education_Owen

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 81.216 for 7 h (2016-01-10 20:00:00 to 2016-01-11 03:00:00); 9 such stretch(es), 2 d 9 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 9 stuck stretch(es) set to missing. (12)
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
| train | 2016-01-01 00:00:00 | 2017-05-26 16:00:00 | 12267 |
| val | 2017-05-27 17:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2606 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 13.953 | 7.722 | 9.936 | -2.649 | 0.938 |
| gbm_change | ml | 15.225 | 7.954 | 10.842 | -2.802 | 0.926 |
| ridge | ml | 17.830 | 11.324 | 12.697 | -0.293 | 0.899 |
| same_time_last_week | baseline | 19.340 | 9.477 | 13.773 | 0.034 | 0.881 |
| time_of_week_profile | baseline | 19.553 | 12.873 | 13.924 | -8.620 | 0.878 |
| towt | baseline | 19.816 | 13.231 | 14.112 | -8.881 | 0.875 |
| time_of_day_profile | baseline | 21.866 | 14.601 | 15.572 | -8.614 | 0.848 |
| persistence | baseline | 32.970 | 16.766 | 23.479 | 0.069 | 0.653 |
| same_time_yesterday | baseline | 32.970 | 16.766 | 23.479 | 0.069 | 0.653 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 16.821 | 24.104 |
| MAE (kWh) | 9.617 | 11.614 |
| CV(RMSE) % | 11.409 | 16.349 |
| NMBE % | -2.543 | -2.068 |
| R² | 0.915 | 0.825 |

Skill vs same_time_last_week: **0.30** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.4% (limit 30%), NMBE -2.5% (limit ±10%): **passes**.

90% prediction interval: ±15.5 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.28 |
| 2017-08-07 to 2017-10-19 | 1753 | 0.25 |
| 2017-10-19 to 2017-12-31 | 1752 | 0.37 |

Pooled skill: **0.33**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 79% |
| calendar (time of day, weekday) | 21% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
