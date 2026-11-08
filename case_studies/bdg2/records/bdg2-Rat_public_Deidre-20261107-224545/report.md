# Run report: bdg2-Rat_public_Deidre

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 51 stuck stretch(es) set to missing. (107)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (60)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (12)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (16)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-25 23:00:00 | 12261 |
| val | 2017-05-27 00:00:00 | 2017-09-13 10:00:00 | 2603 |
| test | 2017-09-14 11:00:00 | 2017-12-31 23:00:00 | 2604 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 1.801 | 1.417 | 15.653 | 2.125 | 0.544 |
| gbm_change | ml | 1.820 | 1.430 | 15.816 | 1.046 | 0.534 |
| ridge | ml | 1.894 | 1.472 | 16.456 | 2.307 | 0.496 |
| towt | baseline | 2.095 | 1.677 | 18.205 | 8.658 | 0.383 |
| same_time_yesterday | baseline | 2.138 | 1.660 | 18.575 | 0.380 | 0.358 |
| persistence | baseline | 2.138 | 1.660 | 18.575 | 0.380 | 0.358 |
| same_time_last_week | baseline | 2.897 | 2.274 | 25.171 | 0.616 | -0.179 |
| time_of_day_profile | baseline | 3.923 | 3.301 | 34.090 | 25.720 | -1.163 |
| time_of_week_profile | baseline | 3.927 | 3.305 | 34.125 | 25.720 | -1.168 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.441 | 1.692 |
| MAE (kWh) | 1.110 | 1.333 |
| CV(RMSE) % | 17.000 | 19.961 |
| NMBE % | 3.538 | 2.357 |
| R² | 0.202 | -0.100 |

Skill vs towt: **0.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 17.0% (limit 30%), NMBE 3.5% (limit ±10%): **passes**.

90% prediction interval: ±2.89 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1752 | 0.13 |
| 2017-08-08 to 2017-10-19 | 1752 | 0.10 |
| 2017-10-20 to 2017-12-31 | 1751 | 0.22 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 94% |
| airTemperature | 6% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
