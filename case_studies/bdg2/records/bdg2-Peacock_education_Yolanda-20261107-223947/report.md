# Run report: bdg2-Peacock_education_Yolanda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12278 |
| val | 2017-05-27 18:00:00 | 2017-09-13 08:00:00 | 2607 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 2.589 | 1.704 | 7.299 | -2.495 | 0.874 |
| gbm | ml | 2.603 | 1.767 | 7.338 | -2.642 | 0.873 |
| ridge | ml | 2.623 | 1.798 | 7.396 | -0.042 | 0.871 |
| same_time_last_week | baseline | 3.265 | 2.082 | 9.206 | -0.305 | 0.800 |
| same_time_yesterday | baseline | 4.077 | 2.528 | 11.494 | 0.093 | 0.688 |
| persistence | baseline | 4.077 | 2.528 | 11.494 | 0.093 | 0.688 |
| time_of_day_profile | baseline | 4.314 | 3.423 | 12.162 | -8.703 | 0.651 |
| time_of_week_profile | baseline | 4.325 | 3.423 | 12.194 | -8.712 | 0.649 |
| towt | baseline | 4.886 | 3.992 | 13.776 | -10.787 | 0.552 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.095 | 3.551 |
| MAE (kWh) | 1.443 | 2.438 |
| CV(RMSE) % | 6.092 | 10.327 |
| NMBE % | -1.315 | -0.453 |
| R² | 0.914 | 0.752 |

Skill vs same_time_last_week: **0.41** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.1% (limit 30%), NMBE -1.3% (limit ±10%): **passes**.

90% prediction interval: ±3.39 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.24 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.25 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.42 |

Pooled skill: **0.31**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 76% |
| calendar (time of day, weekday) | 23% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
