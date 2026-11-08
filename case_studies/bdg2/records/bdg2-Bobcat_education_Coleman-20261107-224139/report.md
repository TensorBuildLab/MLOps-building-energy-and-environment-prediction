# Run report: bdg2-Bobcat_education_Coleman

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
| train | 2016-01-01 00:00:00 | 2017-06-12 14:00:00 | 11310 |
| val | 2017-06-13 15:00:00 | 2017-09-21 16:00:00 | 2399 |
| test | 2017-09-22 17:00:00 | 2017-12-31 23:00:00 | 2401 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 17.522 | 11.873 | 14.988 | -2.157 | 0.829 |
| ridge | ml | 18.703 | 13.744 | 15.998 | -1.956 | 0.806 |
| gbm | ml | 19.271 | 14.825 | 16.484 | -5.958 | 0.794 |
| time_of_week_profile | baseline | 20.564 | 16.459 | 17.590 | -6.326 | 0.765 |
| time_of_day_profile | baseline | 21.684 | 17.502 | 18.549 | -6.297 | 0.739 |
| same_time_last_week | baseline | 21.790 | 14.293 | 18.639 | -0.274 | 0.736 |
| towt | baseline | 25.273 | 20.775 | 21.619 | -14.217 | 0.645 |
| persistence | baseline | 32.099 | 20.004 | 27.457 | 0.121 | 0.427 |
| same_time_yesterday | baseline | 32.099 | 20.004 | 27.457 | 0.121 | 0.427 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 18.562 | 19.943 |
| MAE (kWh) | 11.022 | 15.092 |
| CV(RMSE) % | 15.999 | 17.189 |
| NMBE % | 2.293 | -4.999 |
| R² | 0.827 | 0.800 |

Skill vs time_of_week_profile: **0.07** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.0% (limit 30%), NMBE 2.3% (limit ±10%): **passes**.

90% prediction interval: ±26.7 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-12 to 2017-08-19 | 1616 | 0.09 |
| 2017-08-19 to 2017-10-25 | 1616 | 0.17 |
| 2017-10-25 to 2017-12-31 | 1616 | 0.06 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 29% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
