# Run report: bdg2-Cockatoo_education_Nelda

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
| train | 2016-01-01 00:00:00 | 2017-06-10 02:00:00 | 11275 |
| val | 2017-06-11 03:00:00 | 2017-09-21 21:00:00 | 2392 |
| test | 2017-09-22 22:00:00 | 2017-12-31 23:00:00 | 2393 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 8.154 | 6.055 | 7.776 | -2.163 | 0.634 |
| gbm | ml | 9.617 | 7.499 | 9.171 | -5.623 | 0.491 |
| gbm_change | ml | 9.747 | 7.640 | 9.295 | -5.747 | 0.477 |
| same_time_last_week | baseline | 10.396 | 7.200 | 9.913 | -1.005 | 0.405 |
| same_time_yesterday | baseline | 11.772 | 7.737 | 11.226 | -0.198 | 0.237 |
| persistence | baseline | 11.772 | 7.737 | 11.226 | -0.198 | 0.237 |
| time_of_day_profile | baseline | 25.514 | 24.281 | 24.330 | -23.142 | -2.583 |
| time_of_week_profile | baseline | 25.539 | 24.299 | 24.354 | -23.161 | -2.590 |
| towt | baseline | 25.990 | 24.768 | 24.785 | -23.615 | -2.718 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 7.367 | 8.583 |
| MAE (kWh) | 5.624 | 6.197 |
| CV(RMSE) % | 6.766 | 7.882 |
| NMBE % | -0.942 | -0.029 |
| R² | 0.620 | 0.484 |

Skill vs same_time_last_week: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.8% (limit 30%), NMBE -0.9% (limit ±10%): **passes**.

90% prediction interval: ±12.8 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1611 | 0.24 |
| 2017-08-19 to 2017-10-25 | 1611 | 0.14 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.17 |

Pooled skill: **0.19**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 72% |
| calendar (time of day, weekday) | 25% |
| airTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
