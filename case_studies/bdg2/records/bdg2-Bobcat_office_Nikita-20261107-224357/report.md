# Run report: bdg2-Bobcat_office_Nikita

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 24.5 for 6 h (2017-03-16 20:00:00 to 2017-03-17 02:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 1 stuck stretch(es) set to missing. (1)
- mask_stuck `airTemperature`: 19 stuck stretch(es) set to missing. (38)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (35)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (122)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-10 10:00:00 | 11442 |
| val | 2017-06-11 11:00:00 | 2017-09-20 15:00:00 | 2427 |
| test | 2017-09-21 16:00:00 | 2017-12-31 23:00:00 | 2429 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 9.431 | 5.998 | 21.538 | -3.745 | 0.825 |
| gbm_change | ml | 9.935 | 6.187 | 22.690 | -3.097 | 0.806 |
| same_time_last_week | baseline | 10.264 | 5.779 | 23.442 | -0.706 | 0.793 |
| ridge | ml | 10.670 | 7.535 | 24.369 | -0.998 | 0.776 |
| towt | baseline | 12.030 | 9.885 | 27.476 | -7.823 | 0.715 |
| time_of_week_profile | baseline | 13.464 | 9.476 | 30.750 | 10.612 | 0.643 |
| time_of_day_profile | baseline | 13.692 | 9.623 | 31.270 | 10.626 | 0.631 |
| persistence | baseline | 21.598 | 12.685 | 49.327 | 0.245 | 0.082 |
| same_time_yesterday | baseline | 21.598 | 12.685 | 49.327 | 0.245 | 0.082 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 5.294 | 6.336 |
| MAE (kWh) | 3.400 | 3.257 |
| CV(RMSE) % | 16.401 | 19.627 |
| NMBE % | -5.915 | -1.216 |
| R² | 0.744 | 0.633 |

Skill vs same_time_last_week: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.4% (limit 30%), NMBE -5.9% (limit ±10%): **passes**.

90% prediction interval: ±15 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-17 | 1635 | 0.07 |
| 2017-08-17 to 2017-10-24 | 1635 | 0.26 |
| 2017-10-24 to 2017-12-31 | 1634 | 0.16 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 50% |
| electricity (recent history) | 49% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
