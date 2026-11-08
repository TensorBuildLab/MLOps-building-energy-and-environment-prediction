# Run report: bdg2-Lamb_assembly_Librada

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
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2609 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 8.692 | 3.521 | 82.280 | -0.057 | 0.836 |
| gbm_change | ml | 8.832 | 3.772 | 83.605 | -1.548 | 0.831 |
| ridge | ml | 10.393 | 6.021 | 98.383 | 11.160 | 0.766 |
| same_time_last_week | baseline | 11.073 | 3.800 | 104.817 | 24.117 | 0.734 |
| same_time_yesterday | baseline | 12.540 | 3.349 | 118.707 | 4.522 | 0.659 |
| persistence | baseline | 12.540 | 3.349 | 118.707 | 4.522 | 0.659 |
| towt | baseline | 32.764 | 22.120 | 310.141 | -146.231 | -1.325 |
| time_of_day_profile | baseline | 34.996 | 24.796 | 331.270 | -193.505 | -1.652 |
| time_of_week_profile | baseline | 35.269 | 24.691 | 333.860 | -194.181 | -1.694 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 17.261 | 19.597 |
| MAE (kWh) | 10.805 | 9.725 |
| CV(RMSE) % | 32.694 | 37.119 |
| NMBE % | 6.360 | -0.583 |
| R² | 0.848 | 0.804 |

Skill vs same_time_last_week: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 32.7% (limit 30%), NMBE 6.4% (limit ±10%): **does not pass**.

90% prediction interval: ±7.25 kWh (width from validation errors); it contained 55% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | nan |
| 2017-08-07 to 2017-10-19 | 1755 | 0.15 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.18 |

Pooled skill: **0.16**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 82% |
| calendar (time of day, weekday) | 17% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
