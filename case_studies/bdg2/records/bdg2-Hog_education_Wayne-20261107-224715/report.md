# Run report: bdg2-Hog_education_Wayne

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

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
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12274 |
| val | 2017-05-27 18:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_week_profile | baseline | 18.238 | 14.284 | 10.888 | 0.189 | 0.725 |
| gbm_change | ml | 18.260 | 13.579 | 10.901 | -2.491 | 0.725 |
| time_of_day_profile | baseline | 18.473 | 14.437 | 11.028 | 0.186 | 0.718 |
| ridge | ml | 19.066 | 14.291 | 11.382 | 0.648 | 0.700 |
| gbm | ml | 19.997 | 15.181 | 11.938 | -4.507 | 0.670 |
| same_time_last_week | baseline | 23.479 | 17.723 | 14.017 | 0.655 | 0.545 |
| towt | baseline | 26.101 | 20.604 | 15.582 | -10.993 | 0.438 |
| persistence | baseline | 27.993 | 18.679 | 16.712 | 0.363 | 0.353 |
| same_time_yesterday | baseline | 27.993 | 18.679 | 16.712 | 0.363 | 0.353 |

## Test result

Chosen model: **time_of_week_profile** 

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 23.310 | 23.310 |
| MAE (kWh) | 20.061 | 20.061 |
| CV(RMSE) % | 15.430 | 15.430 |
| NMBE % | -10.670 | -10.670 |
| R² | 0.554 | 0.554 |

Skill vs time_of_week_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.4% (limit 30%), NMBE -10.7% (limit ±10%): **does not pass**.

90% prediction interval: ±26.8 kWh (width from validation errors); it contained 80% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.00 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.00 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
