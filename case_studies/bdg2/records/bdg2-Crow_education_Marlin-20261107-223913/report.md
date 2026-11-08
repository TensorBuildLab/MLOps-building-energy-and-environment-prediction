# Run report: bdg2-Crow_education_Marlin

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-14 08:00:00 | 2017-05-04 02:00:00 | 11415 |
| val | 2017-05-05 03:00:00 | 2017-08-14 00:00:00 | 2422 |
| test | 2017-08-15 01:00:00 | 2017-11-23 23:00:00 | 2423 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 44.463 | 31.849 | 15.051 | 1.206 | 0.763 |
| persistence | baseline | 49.929 | 33.983 | 16.901 | 0.528 | 0.701 |
| same_time_yesterday | baseline | 49.929 | 33.983 | 16.901 | 0.528 | 0.701 |
| gbm_change | ml | 62.497 | 47.724 | 21.155 | -10.044 | 0.531 |
| gbm | ml | 66.679 | 50.186 | 22.571 | -11.585 | 0.467 |
| towt | baseline | 66.793 | 53.741 | 22.609 | -6.900 | 0.465 |
| same_time_last_week | baseline | 80.243 | 57.416 | 27.162 | 4.739 | 0.228 |
| time_of_week_profile | baseline | 126.624 | 115.842 | 42.862 | 32.931 | -0.923 |
| time_of_day_profile | baseline | 126.950 | 115.932 | 42.972 | 32.926 | -0.933 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 35.449 | 36.286 |
| MAE (kWh) | 23.319 | 21.991 |
| CV(RMSE) % | 14.120 | 14.454 |
| NMBE % | -1.734 | -0.697 |
| R² | 0.899 | 0.894 |

Skill vs persistence: **0.02** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.1% (limit 30%), NMBE -1.7% (limit ±10%): **passes**.

90% prediction interval: ±77.6 kWh (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-04 to 2017-07-11 | 1631 | 0.07 |
| 2017-07-11 to 2017-09-17 | 1631 | 0.15 |
| 2017-09-17 to 2017-11-23 | 1631 | 0.00 |

Pooled skill: **0.08**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 89% |
| airTemperature | 5% |
| calendar (time of day, weekday) | 3% |
| dewTemperature | 1% |
| windSpeed | 1% |

> Warning: The model is barely better than persistence on test data (skill 0.02).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
