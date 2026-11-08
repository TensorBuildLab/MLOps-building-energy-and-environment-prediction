# Run report: bdg2-Bear_lodging_Evan

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
| train | 2016-01-01 00:00:00 | 2017-05-25 14:00:00 | 12253 |
| val | 2017-05-26 15:00:00 | 2017-09-11 23:00:00 | 2601 |
| test | 2017-09-13 00:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 11.620 | 8.115 | 7.119 | -1.690 | 0.918 |
| gbm_change | ml | 11.712 | 7.981 | 7.175 | -1.324 | 0.917 |
| ridge | ml | 12.395 | 8.612 | 7.594 | -0.100 | 0.907 |
| same_time_last_week | baseline | 14.371 | 9.813 | 8.804 | 0.991 | 0.875 |
| same_time_yesterday | baseline | 15.659 | 10.300 | 9.593 | 0.154 | 0.851 |
| persistence | baseline | 15.659 | 10.300 | 9.593 | 0.154 | 0.851 |
| time_of_week_profile | baseline | 20.194 | 16.429 | 12.371 | -9.158 | 0.752 |
| time_of_day_profile | baseline | 20.206 | 16.416 | 12.379 | -9.181 | 0.752 |
| towt | baseline | 25.443 | 22.228 | 15.587 | -13.419 | 0.607 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.931 | 24.096 |
| MAE (kWh) | 8.924 | 14.583 |
| CV(RMSE) % | 8.034 | 13.897 |
| NMBE % | -0.754 | -2.415 |
| R² | 0.920 | 0.760 |

Skill vs same_time_last_week: **0.42** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.0% (limit 30%), NMBE -0.8% (limit ±10%): **passes**.

90% prediction interval: ±17.1 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1751 | 0.08 |
| 2017-08-06 to 2017-10-18 | 1751 | 0.28 |
| 2017-10-18 to 2017-12-31 | 1750 | 0.44 |

Pooled skill: **0.35**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 88% |
| calendar (time of day, weekday) | 11% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
