# Run report: bdg2-Eagle_office_Elias

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 48.7229 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 7 such stretch(es), 6 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 7 stuck stretch(es) set to missing. (110)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-05 08:00:00 | 11663 |
| val | 2017-06-06 09:00:00 | 2017-09-17 20:00:00 | 2475 |
| test | 2017-09-18 21:00:00 | 2017-12-31 23:00:00 | 2476 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 10.269 | 7.423 | 11.697 | 4.280 | 0.814 |
| ridge | ml | 10.373 | 7.937 | 11.815 | 1.171 | 0.810 |
| gbm_change | ml | 10.511 | 7.542 | 11.972 | 4.433 | 0.805 |
| time_of_week_profile | baseline | 11.355 | 8.565 | 12.933 | 3.634 | 0.773 |
| time_of_day_profile | baseline | 11.513 | 8.659 | 13.114 | 3.673 | 0.766 |
| towt | baseline | 11.947 | 8.929 | 13.608 | 5.605 | 0.748 |
| same_time_last_week | baseline | 12.004 | 8.582 | 13.673 | -0.008 | 0.746 |
| persistence | baseline | 14.971 | 10.609 | 17.053 | -0.149 | 0.605 |
| same_time_yesterday | baseline | 14.971 | 10.609 | 17.053 | -0.149 | 0.605 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 9.320 | 11.029 |
| MAE (kWh) | 6.883 | 8.484 |
| CV(RMSE) % | 11.116 | 13.155 |
| NMBE % | 0.917 | -1.559 |
| R² | 0.821 | 0.750 |

Skill vs time_of_week_profile: **0.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.1% (limit 30%), NMBE 0.9% (limit ±10%): **passes**.

90% prediction interval: ±18.4 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-05 to 2017-08-14 | 1667 | 0.04 |
| 2017-08-14 to 2017-10-22 | 1666 | 0.10 |
| 2017-10-22 to 2017-12-31 | 1666 | 0.22 |

Pooled skill: **0.12**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 70% |
| calendar (time of day, weekday) | 30% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
