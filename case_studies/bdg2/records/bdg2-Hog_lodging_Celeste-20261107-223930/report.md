# Run report: bdg2-Hog_lodging_Celeste

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 108.337 for 1 d 1 h (2017-12-13 11:00:00 to 2017-12-14 12:00:00); 1 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 1 stuck stretch(es) set to missing. (20)
- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 01:00:00 | 12265 |
| val | 2017-05-27 02:00:00 | 2017-09-12 13:00:00 | 2604 |
| test | 2017-09-13 14:00:00 | 2017-12-31 23:00:00 | 2605 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 9.115 | 6.050 | 10.594 | -0.595 | 0.624 |
| gbm_change | ml | 9.148 | 6.056 | 10.632 | -0.132 | 0.622 |
| ridge | ml | 9.497 | 6.188 | 11.038 | 0.704 | 0.592 |
| persistence | baseline | 10.290 | 6.624 | 11.959 | 0.597 | 0.521 |
| same_time_yesterday | baseline | 10.290 | 6.624 | 11.959 | 0.597 | 0.521 |
| same_time_last_week | baseline | 13.944 | 10.456 | 16.207 | 4.249 | 0.121 |
| towt | baseline | 16.980 | 13.329 | 19.735 | -7.055 | -0.304 |
| time_of_day_profile | baseline | 18.835 | 15.193 | 21.891 | -12.004 | -0.604 |
| time_of_week_profile | baseline | 18.930 | 15.205 | 22.002 | -12.008 | -0.620 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 9.058 | 10.393 |
| MAE (kWh) | 6.611 | 7.728 |
| CV(RMSE) % | 8.797 | 10.092 |
| NMBE % | -0.347 | -0.390 |
| R² | 0.826 | 0.771 |

Skill vs persistence: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.8% (limit 30%), NMBE -0.3% (limit ±10%): **passes**.

90% prediction interval: ±13.3 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.14 |
| 2017-08-07 to 2017-10-19 | 1752 | 0.15 |
| 2017-10-19 to 2017-12-31 | 1752 | 0.13 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 85% |
| calendar (time of day, weekday) | 15% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
