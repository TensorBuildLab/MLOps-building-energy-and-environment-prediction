# Run report: bdg2-Bull_services_Nadine

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 138 for 6 h (2016-04-23 23:00:00 to 2016-04-24 05:00:00); 4 such stretch(es), 1 d in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (4)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-26 22:00:00 | 12063 |
| val | 2017-05-27 23:00:00 | 2017-09-11 15:00:00 | 2560 |
| test | 2017-09-12 16:00:00 | 2017-12-31 23:00:00 | 2562 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 4.987 | 3.091 | 4.308 | -0.593 | 0.815 |
| gbm | ml | 5.159 | 3.236 | 4.456 | -0.644 | 0.803 |
| gbm_change | ml | 5.489 | 3.277 | 4.742 | -0.966 | 0.776 |
| persistence | baseline | 5.818 | 2.960 | 5.026 | -0.047 | 0.749 |
| same_time_yesterday | baseline | 5.818 | 2.960 | 5.026 | -0.047 | 0.749 |
| same_time_last_week | baseline | 6.591 | 3.903 | 5.694 | 0.122 | 0.678 |
| time_of_day_profile | baseline | 8.703 | 6.871 | 7.518 | -5.609 | 0.438 |
| time_of_week_profile | baseline | 8.736 | 6.888 | 7.547 | -5.599 | 0.434 |
| towt | baseline | 18.924 | 17.248 | 16.349 | -14.767 | -1.658 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 7.381 | 8.722 |
| MAE (kWh) | 4.123 | 3.670 |
| CV(RMSE) % | 6.576 | 7.771 |
| NMBE % | -0.084 | -0.200 |
| R² | 0.652 | 0.515 |

Skill vs persistence: **0.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.6% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±6.37 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-06 | 1724 | 0.02 |
| 2017-08-06 to 2017-10-17 | 1723 | 0.14 |
| 2017-10-17 to 2017-12-31 | 1723 | 0.18 |

Pooled skill: **0.15**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 68% |
| calendar (time of day, weekday) | 32% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
