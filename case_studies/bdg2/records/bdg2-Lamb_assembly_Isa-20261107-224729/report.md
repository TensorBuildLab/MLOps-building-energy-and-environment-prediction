# Run report: bdg2-Lamb_assembly_Isa

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
| train | 2016-01-01 00:00:00 | 2017-05-25 21:00:00 | 12217 |
| val | 2017-05-26 22:00:00 | 2017-09-13 20:00:00 | 2594 |
| test | 2017-09-14 21:00:00 | 2017-12-31 23:00:00 | 2595 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 0.775 | 0.389 | 62.532 | -2.454 | 0.741 |
| gbm_change | ml | 0.812 | 0.358 | 65.560 | -4.063 | 0.716 |
| ridge | ml | 0.895 | 0.569 | 72.273 | -3.331 | 0.655 |
| persistence | baseline | 0.996 | 0.358 | 80.401 | -0.440 | 0.573 |
| same_time_yesterday | baseline | 0.996 | 0.358 | 80.401 | -0.440 | 0.573 |
| same_time_last_week | baseline | 1.185 | 0.510 | 95.680 | -0.286 | 0.395 |
| time_of_day_profile | baseline | 1.909 | 1.422 | 154.081 | -82.974 | -0.570 |
| time_of_week_profile | baseline | 1.918 | 1.422 | 154.807 | -83.359 | -0.585 |
| towt | baseline | 1.922 | 1.430 | 155.161 | -82.178 | -0.592 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.150 | 0.000 |
| MAE (kWh) | 0.082 | 0.000 |
| CV(RMSE) % | 150379.102 | 0.000 |
| NMBE % | -49777.901 | 0.000 |
| R² | -123074197210482408683463799426091319296.000 | 1.000 |

Skill vs persistence: **nan** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 150379.1% (limit 30%), NMBE -49777.9% (limit ±10%): **does not pass**.

90% prediction interval: ±1.04 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-07 | 1746 | 0.25 |
| 2017-08-07 to 2017-10-20 | 1746 | -1.21 |
| 2017-10-20 to 2017-12-31 | 1745 | nan |

Pooled skill: **-0.01**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 60% |
| dewTemperature | 23% |
| airTemperature | 12% |
| windSpeed | 4% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
