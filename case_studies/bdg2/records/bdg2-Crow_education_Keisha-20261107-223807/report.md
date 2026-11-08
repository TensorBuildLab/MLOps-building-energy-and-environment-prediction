# Run report: bdg2-Crow_education_Keisha

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-20 13:00:00 | 11390 |
| val | 2017-04-21 14:00:00 | 2017-07-31 05:00:00 | 2416 |
| test | 2017-08-01 06:00:00 | 2017-11-10 00:00:00 | 2418 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 12.446 | 8.852 | 4.310 | 0.562 | 0.919 |
| gbm_change | ml | 12.535 | 8.906 | 4.341 | 0.793 | 0.918 |
| ridge | ml | 14.327 | 11.067 | 4.962 | -0.359 | 0.893 |
| same_time_last_week | baseline | 19.000 | 13.924 | 6.580 | -0.668 | 0.812 |
| towt | baseline | 21.936 | 16.140 | 7.597 | 0.770 | 0.749 |
| persistence | baseline | 21.973 | 13.997 | 7.610 | -0.173 | 0.748 |
| same_time_yesterday | baseline | 21.973 | 13.997 | 7.610 | -0.173 | 0.748 |
| time_of_week_profile | baseline | 22.179 | 17.069 | 7.681 | -2.394 | 0.744 |
| time_of_day_profile | baseline | 22.342 | 17.055 | 7.737 | -2.406 | 0.740 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.571 | 18.814 |
| MAE (kWh) | 9.278 | 12.386 |
| CV(RMSE) % | 4.523 | 6.270 |
| NMBE % | 0.805 | 0.874 |
| R² | 0.930 | 0.865 |

Skill vs same_time_last_week: **0.28** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 4.5% (limit 30%), NMBE 0.8% (limit ±10%): **passes**.

90% prediction interval: ±18.7 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-20 to 2017-06-27 | 1628 | 0.37 |
| 2017-06-27 to 2017-09-03 | 1627 | 0.24 |
| 2017-09-03 to 2017-11-10 | 1627 | 0.31 |

Pooled skill: **0.32**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 83% |
| calendar (time of day, weekday) | 17% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
