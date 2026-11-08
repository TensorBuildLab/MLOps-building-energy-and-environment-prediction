# Run report: bdg2-Cockatoo_public_Leah

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -1.7 for 14 h (2017-01-28 16:00:00 to 2017-01-29 06:00:00); 57 such stretch(es), 16 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.6 for 8 h (2016-09-07 02:00:00 to 2016-09-07 10:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 57 stuck stretch(es) set to missing. (108)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (323)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (273)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (306)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 23:00:00 | 11282 |
| val | 2017-06-11 00:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2395 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 9.795 | 6.647 | 6.110 | 0.195 | 0.905 |
| gbm_change | ml | 10.171 | 6.744 | 6.345 | 0.014 | 0.897 |
| ridge | ml | 11.944 | 8.763 | 7.451 | 0.335 | 0.858 |
| towt | baseline | 12.308 | 8.965 | 7.677 | -0.205 | 0.850 |
| same_time_last_week | baseline | 13.703 | 8.629 | 8.547 | 0.596 | 0.814 |
| persistence | baseline | 15.953 | 10.222 | 9.951 | 0.106 | 0.747 |
| same_time_yesterday | baseline | 15.953 | 10.222 | 9.951 | 0.106 | 0.747 |
| time_of_week_profile | baseline | 16.195 | 12.866 | 10.102 | -5.844 | 0.740 |
| time_of_day_profile | baseline | 16.207 | 12.851 | 10.109 | -5.816 | 0.739 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 11.589 | 30.493 |
| MAE (kWh) | 8.400 | 18.144 |
| CV(RMSE) % | 6.987 | 18.383 |
| NMBE % | -0.917 | -3.355 |
| R² | 0.915 | 0.408 |

Skill vs towt: **0.62** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.0% (limit 30%), NMBE -0.9% (limit ±10%): **passes**.

90% prediction interval: ±13.8 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.17 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.33 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.65 |

Pooled skill: **0.53**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 68% |
| calendar (time of day, weekday) | 30% |
| dewTemperature | 1% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
