# Run report: bdg2-Hog_office_Catharine

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
| train | 2016-01-01 00:00:00 | 2017-05-25 17:00:00 | 11960 |
| val | 2017-05-26 18:00:00 | 2017-09-14 17:00:00 | 2538 |
| test | 2017-09-15 18:00:00 | 2017-12-31 23:00:00 | 2540 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 162.340 | 128.689 | 35.356 | -6.130 | 0.081 |
| time_of_week_profile | baseline | 163.116 | 110.923 | 35.525 | 4.156 | 0.072 |
| time_of_day_profile | baseline | 163.174 | 111.376 | 35.537 | 4.160 | 0.071 |
| towt | baseline | 166.805 | 139.328 | 36.328 | -8.176 | 0.030 |
| gbm | ml | 169.434 | 132.533 | 36.901 | -8.995 | -0.001 |
| gbm_change | ml | 178.519 | 136.954 | 38.879 | -9.160 | -0.112 |
| same_time_yesterday | baseline | 200.719 | 110.992 | 43.714 | 1.055 | -0.405 |
| persistence | baseline | 200.719 | 110.992 | 43.714 | 1.055 | -0.405 |
| same_time_last_week | baseline | 215.266 | 127.532 | 46.882 | 0.377 | -0.616 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 83.058 | 94.653 |
| MAE (kWh) | 55.839 | 72.617 |
| CV(RMSE) % | 19.952 | 22.738 |
| NMBE % | -4.829 | -6.724 |
| R² | 0.333 | 0.134 |

Skill vs time_of_week_profile: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 20.0% (limit 30%), NMBE -4.8% (limit ±10%): **passes**.

90% prediction interval: ±249 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1709 | -0.06 |
| 2017-08-06 to 2017-10-21 | 1709 | 0.05 |
| 2017-10-21 to 2017-12-31 | 1708 | 0.33 |

Pooled skill: **0.03**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 39% |
| electricity (recent history) | 30% |
| airTemperature | 23% |
| dewTemperature | 8% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
