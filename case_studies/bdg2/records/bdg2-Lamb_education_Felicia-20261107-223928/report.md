# Run report: bdg2-Lamb_education_Felicia

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 278 stuck stretch(es) set to missing. (1035)
- mask_stuck `windSpeed`: 4 stuck stretch(es) set to missing. (5)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (299)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (24)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (31)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-04-26 19:00:00 | 11494 |
| val | 2017-04-27 20:00:00 | 2017-09-19 09:00:00 | 2439 |
| test | 2017-09-20 10:00:00 | 2017-12-31 23:00:00 | 2440 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 1.426 | 0.807 | 37.860 | -5.281 | 0.778 |
| gbm_change | ml | 1.455 | 0.833 | 38.618 | -5.032 | 0.769 |
| ridge | ml | 1.862 | 1.348 | 49.424 | -2.374 | 0.622 |
| same_time_last_week | baseline | 2.294 | 1.231 | 60.879 | 0.107 | 0.426 |
| same_time_yesterday | baseline | 2.473 | 1.186 | 65.631 | -0.819 | 0.333 |
| persistence | baseline | 2.473 | 1.186 | 65.631 | -0.819 | 0.333 |
| towt | baseline | 2.659 | 1.548 | 70.577 | -19.898 | 0.229 |
| time_of_day_profile | baseline | 2.965 | 1.923 | 78.704 | -40.990 | 0.041 |
| time_of_week_profile | baseline | 2.969 | 1.923 | 78.797 | -41.016 | 0.039 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.008 | 1.986 |
| MAE (kWh) | 0.538 | 0.724 |
| CV(RMSE) % | 53.842 | 106.134 |
| NMBE % | -14.398 | -20.480 |
| R² | 0.912 | 0.656 |

Skill vs same_time_last_week: **0.49** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 53.8% (limit 30%), NMBE -14.4% (limit ±10%): **does not pass**.

90% prediction interval: ±1.93 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-26 to 2017-08-15 | 1643 | 0.38 |
| 2017-08-15 to 2017-10-23 | 1642 | 0.35 |
| 2017-10-23 to 2017-12-31 | 1642 | 0.62 |

Pooled skill: **0.44**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 73% |
| calendar (time of day, weekday) | 25% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
