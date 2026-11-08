# Run report: bdg2-Rat_health_Rosaria

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
| train | 2016-01-01 00:00:00 | 2017-05-26 07:00:00 | 12243 |
| val | 2017-05-27 08:00:00 | 2017-09-13 14:00:00 | 2599 |
| test | 2017-09-14 15:00:00 | 2017-12-31 23:00:00 | 2600 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 6.751 | 5.053 | 21.400 | -2.480 | 0.796 |
| gbm | ml | 6.785 | 5.098 | 21.508 | -2.145 | 0.794 |
| towt | baseline | 7.238 | 5.493 | 22.942 | 1.955 | 0.765 |
| ridge | ml | 7.908 | 5.881 | 25.065 | 1.053 | 0.720 |
| same_time_yesterday | baseline | 9.813 | 6.468 | 31.104 | 0.283 | 0.568 |
| persistence | baseline | 9.813 | 6.468 | 31.104 | 0.283 | 0.568 |
| same_time_last_week | baseline | 10.634 | 8.165 | 33.706 | 1.103 | 0.493 |
| time_of_day_profile | baseline | 11.286 | 9.197 | 35.775 | 2.723 | 0.429 |
| time_of_week_profile | baseline | 11.291 | 9.220 | 35.788 | 2.737 | 0.429 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 5.698 | 9.223 |
| MAE (kWh) | 4.023 | 7.277 |
| CV(RMSE) % | 17.800 | 28.810 |
| NMBE % | 3.540 | 6.215 |
| R² | 0.854 | 0.618 |

Skill vs towt: **0.38** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 17.8% (limit 30%), NMBE 3.5% (limit ±10%): **passes**.

90% prediction interval: ±11.1 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-08 | 1749 | 0.12 |
| 2017-08-08 to 2017-10-20 | 1749 | 0.05 |
| 2017-10-20 to 2017-12-31 | 1749 | 0.41 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 77% |
| calendar (time of day, weekday) | 21% |
| airTemperature | 1% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
