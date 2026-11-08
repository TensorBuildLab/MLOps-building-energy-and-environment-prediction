# Run report: bdg2-Moose_education_Rene

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 399.848 for 22 h (2016-05-13 23:00:00 to 2016-05-14 21:00:00); 210 such stretch(es), 66 d 1 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 210 stuck stretch(es) set to missing. (535)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-01 16:00:00 | 11883 |
| val | 2017-06-02 17:00:00 | 2017-09-15 18:00:00 | 2522 |
| test | 2017-09-16 19:00:00 | 2017-12-31 23:00:00 | 2523 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 73.080 | 39.590 | 16.177 | -2.174 | 0.941 |
| gbm_change | ml | 76.119 | 36.526 | 16.850 | -1.850 | 0.936 |
| ridge | ml | 96.387 | 53.831 | 21.337 | -2.568 | 0.898 |
| time_of_day_profile | baseline | 100.300 | 63.186 | 22.203 | -8.905 | 0.889 |
| persistence | baseline | 237.827 | 105.707 | 52.646 | -0.097 | 0.376 |
| same_time_yesterday | baseline | 237.827 | 105.707 | 52.646 | -0.097 | 0.376 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 90.524 | 101.948 |
| MAE (kWh) | 40.184 | 60.795 |
| CV(RMSE) % | 19.463 | 21.919 |
| NMBE % | -2.225 | -4.095 |
| R² | 0.920 | 0.898 |

Skill vs time_of_day_profile: **0.11** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 19.5% (limit 30%), NMBE -2.2% (limit ±10%): **passes**.

90% prediction interval: ±78 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-01 to 2017-08-11 | 1698 | 0.30 |
| 2017-08-11 to 2017-10-21 | 1698 | 0.31 |
| 2017-10-21 to 2017-12-31 | 1697 | 0.10 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 85% |
| calendar (time of day, weekday) | 15% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
