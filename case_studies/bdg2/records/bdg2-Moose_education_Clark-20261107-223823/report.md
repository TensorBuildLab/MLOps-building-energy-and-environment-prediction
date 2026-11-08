# Run report: bdg2-Moose_education_Clark

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 730.801 for 1 d 1 h (2016-12-17 21:00:00 to 2016-12-18 22:00:00); 122 such stretch(es), 40 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 122 stuck stretch(es) set to missing. (364)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-30 12:00:00 | 12002 |
| val | 2017-05-31 13:00:00 | 2017-09-14 16:00:00 | 2548 |
| test | 2017-09-15 17:00:00 | 2017-12-31 23:00:00 | 2549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 81.190 | 51.456 | 10.042 | -1.549 | 0.922 |
| gbm_change | ml | 83.665 | 49.146 | 10.348 | -1.165 | 0.917 |
| ridge | ml | 104.435 | 70.182 | 12.916 | -1.633 | 0.871 |
| towt | baseline | 112.728 | 79.693 | 13.942 | -5.891 | 0.850 |
| same_time_last_week | baseline | 113.098 | 58.372 | 13.988 | 0.065 | 0.849 |
| time_of_week_profile | baseline | 115.060 | 82.912 | 14.230 | -6.724 | 0.844 |
| time_of_day_profile | baseline | 116.373 | 82.511 | 14.393 | -6.689 | 0.840 |
| persistence | baseline | 209.008 | 107.450 | 25.850 | -0.001 | 0.484 |
| same_time_yesterday | baseline | 209.008 | 107.450 | 25.850 | -0.001 | 0.484 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 90.871 | 112.877 |
| MAE (kWh) | 60.770 | 75.760 |
| CV(RMSE) % | 11.236 | 13.958 |
| NMBE % | -0.749 | -5.194 |
| R² | 0.900 | 0.845 |

Skill vs towt: **0.19** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.2% (limit 30%), NMBE -0.7% (limit ±10%): **passes**.

90% prediction interval: ±99.1 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-30 to 2017-08-09 | 1715 | 0.27 |
| 2017-08-10 to 2017-10-20 | 1715 | 0.20 |
| 2017-10-20 to 2017-12-31 | 1715 | 0.22 |

Pooled skill: **0.23**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 63% |
| calendar (time of day, weekday) | 37% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
