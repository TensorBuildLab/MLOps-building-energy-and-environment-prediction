# Run report: bdg2-Bear_education_Gavin

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
| train | 2016-01-01 00:00:00 | 2017-05-26 18:00:00 | 12273 |
| val | 2017-05-27 19:00:00 | 2017-09-13 08:00:00 | 2605 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 4.612 | 3.512 | 4.882 | 0.940 | 0.650 |
| gbm_change | ml | 4.701 | 3.559 | 4.976 | 1.038 | 0.636 |
| ridge | ml | 4.877 | 3.682 | 5.163 | 0.121 | 0.608 |
| towt | baseline | 6.295 | 5.305 | 6.663 | 4.644 | 0.348 |
| same_time_last_week | baseline | 6.372 | 4.761 | 6.745 | 0.125 | 0.331 |
| persistence | baseline | 6.710 | 4.926 | 7.103 | 0.084 | 0.259 |
| same_time_yesterday | baseline | 6.710 | 4.926 | 7.103 | 0.084 | 0.259 |
| time_of_day_profile | baseline | 6.955 | 5.964 | 7.362 | 5.575 | 0.203 |
| time_of_week_profile | baseline | 6.965 | 5.978 | 7.372 | 5.578 | 0.201 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.402 | 5.750 |
| MAE (kWh) | 3.355 | 4.353 |
| CV(RMSE) % | 4.962 | 6.481 |
| NMBE % | -1.138 | -0.890 |
| R² | 0.769 | 0.605 |

Skill vs towt: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 5.0% (limit 30%), NMBE -1.1% (limit ±10%): **passes**.

90% prediction interval: ±7.09 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.22 |
| 2017-08-07 to 2017-10-19 | 1753 | 0.25 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.24 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 67% |
| calendar (time of day, weekday) | 32% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
