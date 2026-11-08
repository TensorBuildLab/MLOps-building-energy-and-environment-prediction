# Run report: bdg2-Bobcat_education_Alissa

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

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
| train | 2016-01-01 00:00:00 | 2017-06-08 11:00:00 | 11552 |
| val | 2017-06-09 12:00:00 | 2017-09-19 16:00:00 | 2451 |
| test | 2017-09-20 17:00:00 | 2017-12-31 23:00:00 | 2453 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 8.221 | 5.117 | 14.558 | 0.100 | 0.787 |
| gbm_change | ml | 8.340 | 5.114 | 14.770 | 0.648 | 0.781 |
| ridge | ml | 9.456 | 6.826 | 16.745 | 0.517 | 0.719 |
| towt | baseline | 10.094 | 7.610 | 17.875 | 0.929 | 0.680 |
| same_time_last_week | baseline | 10.845 | 6.830 | 19.206 | 0.865 | 0.630 |
| time_of_week_profile | baseline | 11.004 | 7.786 | 19.486 | -8.381 | 0.619 |
| time_of_day_profile | baseline | 11.846 | 8.966 | 20.978 | -8.417 | 0.559 |
| persistence | baseline | 16.209 | 10.424 | 28.704 | 0.021 | 0.174 |
| same_time_yesterday | baseline | 16.209 | 10.424 | 28.704 | 0.021 | 0.174 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 10.405 | 11.072 |
| MAE (kWh) | 6.468 | 6.900 |
| CV(RMSE) % | 17.362 | 18.475 |
| NMBE % | -3.252 | -5.347 |
| R² | 0.775 | 0.745 |

Skill vs towt: **0.06** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 17.4% (limit 30%), NMBE -3.3% (limit ±10%): **passes**.

90% prediction interval: ±11 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-08 to 2017-08-16 | 1651 | 0.19 |
| 2017-08-16 to 2017-10-24 | 1651 | -0.04 |
| 2017-10-24 to 2017-12-31 | 1650 | 0.11 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 63% |
| calendar (time of day, weekday) | 36% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
