# Run report: bdg2-Moose_education_Marlon

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 165.714 for 3 d (2016-11-11 05:00:00 to 2016-11-14 05:00:00); 262 such stretch(es), 131 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 262 stuck stretch(es) set to missing. (1852)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-18 03:00:00 | 10961 |
| val | 2017-06-19 04:00:00 | 2017-09-23 23:00:00 | 2324 |
| test | 2017-09-25 00:00:00 | 2017-12-31 23:00:00 | 2326 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 15.739 | 11.209 | 8.543 | 2.477 | 0.958 |
| gbm | ml | 15.764 | 11.104 | 8.556 | 2.631 | 0.958 |
| same_time_last_week | baseline | 19.675 | 14.428 | 10.679 | -0.023 | 0.934 |
| ridge | ml | 22.242 | 17.149 | 12.072 | 5.542 | 0.916 |
| time_of_week_profile | baseline | 22.674 | 18.374 | 12.307 | -1.674 | 0.912 |
| time_of_day_profile | baseline | 22.914 | 18.541 | 12.437 | -1.667 | 0.910 |
| towt | baseline | 29.552 | 22.788 | 16.040 | 9.607 | 0.851 |
| persistence | baseline | 60.561 | 30.396 | 32.871 | 0.027 | 0.374 |
| same_time_yesterday | baseline | 60.561 | 30.396 | 32.871 | 0.027 | 0.374 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 23.712 | 28.792 |
| MAE (kWh) | 15.780 | 19.111 |
| CV(RMSE) % | 13.031 | 15.823 |
| NMBE % | -2.281 | -1.774 |
| R² | 0.887 | 0.833 |

Skill vs same_time_last_week: **0.18** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.0% (limit 30%), NMBE -2.3% (limit ±10%): **passes**.

90% prediction interval: ±25.1 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-18 to 2017-08-22 | 1566 | 0.21 |
| 2017-08-22 to 2017-10-26 | 1566 | 0.29 |
| 2017-10-26 to 2017-12-31 | 1566 | 0.07 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 64% |
| calendar (time of day, weekday) | 35% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
