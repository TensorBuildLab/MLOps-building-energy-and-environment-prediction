# Run report: bdg2-Eagle_public_Preston

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 230 for 3 d 7 h (2017-06-18 08:00:00 to 2017-06-21 15:00:00); 5 such stretch(es), 8 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 5 stuck stretch(es) set to missing. (177)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 09:00:00 | 12095 |
| val | 2017-05-27 10:00:00 | 2017-09-14 19:00:00 | 2567 |
| test | 2017-09-15 20:00:00 | 2017-12-31 23:00:00 | 2569 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 29.473 | 21.380 | 9.640 | -0.538 | 0.799 |
| gbm_change | ml | 31.246 | 21.477 | 10.220 | -2.670 | 0.774 |
| same_time_last_week | baseline | 31.771 | 16.124 | 10.392 | 0.299 | 0.766 |
| gbm | ml | 32.824 | 24.176 | 10.736 | -1.872 | 0.751 |
| towt | baseline | 33.107 | 21.008 | 10.828 | -4.733 | 0.746 |
| time_of_week_profile | baseline | 34.192 | 22.357 | 11.183 | -5.448 | 0.729 |
| time_of_day_profile | baseline | 34.705 | 22.508 | 11.351 | -5.417 | 0.721 |
| persistence | baseline | 48.768 | 26.640 | 15.951 | -0.044 | 0.449 |
| same_time_yesterday | baseline | 48.768 | 26.640 | 15.951 | -0.044 | 0.449 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 36.073 | 51.693 |
| MAE (kWh) | 25.875 | 28.354 |
| CV(RMSE) % | 11.615 | 16.645 |
| NMBE % | -0.773 | -2.587 |
| R² | 0.760 | 0.507 |

Skill vs same_time_last_week: **0.30** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.6% (limit 30%), NMBE -0.8% (limit ±10%): **passes**.

90% prediction interval: ±47.2 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-09 | 1728 | 0.09 |
| 2017-08-09 to 2017-10-20 | 1728 | 0.05 |
| 2017-10-20 to 2017-12-31 | 1728 | 0.33 |

Pooled skill: **0.23**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 68% |
| calendar (time of day, weekday) | 29% |
| airTemperature | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
