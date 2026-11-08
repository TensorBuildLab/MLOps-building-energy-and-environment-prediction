# Run report: bdg2-Bear_education_Millie

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
| train | 2016-01-01 00:00:00 | 2017-05-29 06:00:00 | 12011 |
| val | 2017-05-30 07:00:00 | 2017-09-13 11:00:00 | 2549 |
| test | 2017-09-14 12:00:00 | 2017-12-31 23:00:00 | 2551 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 0.236 | 0.174 | 7.766 | -1.201 | 0.553 |
| gbm | ml | 0.247 | 0.189 | 8.124 | -1.888 | 0.510 |
| ridge | ml | 0.265 | 0.204 | 8.700 | -0.376 | 0.438 |
| persistence | baseline | 0.286 | 0.193 | 9.419 | 0.030 | 0.342 |
| same_time_yesterday | baseline | 0.286 | 0.193 | 9.419 | 0.030 | 0.342 |
| same_time_last_week | baseline | 0.328 | 0.256 | 10.777 | -0.126 | 0.138 |
| towt | baseline | 0.458 | 0.374 | 15.062 | -9.688 | -0.683 |
| time_of_day_profile | baseline | 0.601 | 0.531 | 19.751 | -17.103 | -1.894 |
| time_of_week_profile | baseline | 0.602 | 0.532 | 19.783 | -17.143 | -1.903 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.438 | 0.521 |
| MAE (kWh) | 0.314 | 0.298 |
| CV(RMSE) % | 14.145 | 16.813 |
| NMBE % | -6.419 | -0.365 |
| R² | 0.189 | -0.146 |

Skill vs persistence: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.1% (limit 30%), NMBE -6.4% (limit ±10%): **passes**.

90% prediction interval: ±0.38 kWh (width from validation errors); it contained 70% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-29 to 2017-08-08 | 1716 | 0.21 |
| 2017-08-08 to 2017-10-19 | 1716 | 0.02 |
| 2017-10-19 to 2017-12-31 | 1716 | 0.21 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 53% |
| calendar (time of day, weekday) | 46% |
| windSpeed | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
