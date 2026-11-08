# Run report: bdg2-Eagle_lodging_Edgardo

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 38.09 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 7 such stretch(es), 5 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 7 stuck stretch(es) set to missing. (96)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-29 16:00:00 | 12088 |
| val | 2017-05-30 17:00:00 | 2017-09-14 22:00:00 | 2566 |
| test | 2017-09-15 23:00:00 | 2017-12-31 23:00:00 | 2567 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 6.071 | 4.148 | 14.664 | 0.357 | 0.451 |
| gbm_change | ml | 6.483 | 4.574 | 15.659 | -2.590 | 0.374 |
| gbm | ml | 6.780 | 4.778 | 16.378 | -3.475 | 0.315 |
| persistence | baseline | 7.193 | 4.776 | 17.375 | 0.494 | 0.229 |
| same_time_yesterday | baseline | 7.193 | 4.776 | 17.375 | 0.494 | 0.229 |
| same_time_last_week | baseline | 7.916 | 5.233 | 19.121 | 2.059 | 0.067 |
| towt | baseline | 10.456 | 8.665 | 25.258 | -15.830 | -0.629 |
| time_of_day_profile | baseline | 12.534 | 10.894 | 30.276 | -23.248 | -1.340 |
| time_of_week_profile | baseline | 12.536 | 10.890 | 30.281 | -23.240 | -1.341 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.242 | 9.131 |
| MAE (kWh) | 5.901 | 6.256 |
| CV(RMSE) % | 15.251 | 16.896 |
| NMBE % | -0.623 | -0.364 |
| R² | 0.772 | 0.721 |

Skill vs persistence: **0.10** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.3% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±9.72 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-29 to 2017-08-09 | 1727 | 0.17 |
| 2017-08-09 to 2017-10-21 | 1727 | 0.15 |
| 2017-10-21 to 2017-12-31 | 1727 | 0.07 |

Pooled skill: **0.12**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 97% |
| calendar (time of day, weekday) | 2% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
