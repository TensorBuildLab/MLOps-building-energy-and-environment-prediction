# Run report: bdg2-Bull_education_Summer

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-25 10:00:00 | 11961 |
| val | 2017-05-26 11:00:00 | 2017-09-09 06:00:00 | 2539 |
| test | 2017-09-10 07:00:00 | 2017-12-31 23:00:00 | 2540 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.130 | 2.097 | 10.263 | -0.147 | 0.755 |
| gbm_change | ml | 3.169 | 2.057 | 10.392 | 0.537 | 0.749 |
| ridge | ml | 3.410 | 2.402 | 11.183 | 0.227 | 0.710 |
| same_time_last_week | baseline | 4.039 | 2.613 | 13.245 | 1.052 | 0.593 |
| time_of_day_profile | baseline | 4.193 | 3.025 | 13.752 | -2.473 | 0.561 |
| towt | baseline | 4.217 | 3.091 | 13.828 | -2.450 | 0.556 |
| time_of_week_profile | baseline | 4.263 | 3.071 | 13.980 | -2.438 | 0.546 |
| persistence | baseline | 5.450 | 3.341 | 17.873 | 0.227 | 0.258 |
| same_time_yesterday | baseline | 5.450 | 3.341 | 17.873 | 0.227 | 0.258 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.190 | 6.176 |
| MAE (kWh) | 2.650 | 3.943 |
| CV(RMSE) % | 13.005 | 19.167 |
| NMBE % | -0.066 | -2.792 |
| R² | 0.777 | 0.516 |

Skill vs same_time_last_week: **0.32** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.0% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±4.38 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-04 | 1709 | 0.27 |
| 2017-08-04 to 2017-10-14 | 1709 | 0.20 |
| 2017-10-14 to 2017-12-31 | 1709 | 0.35 |

Pooled skill: **0.30**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 67% |
| calendar (time of day, weekday) | 33% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
