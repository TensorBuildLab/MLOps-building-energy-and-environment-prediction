# Run report: bdg2-Fox_education_Gayla

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-03 08:00:00 | 11424 |
| val | 2017-06-04 09:00:00 | 2017-09-20 21:00:00 | 2424 |
| test | 2017-09-21 22:00:00 | 2017-12-31 23:00:00 | 2424 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 9.360 | 5.738 | 15.025 | 1.434 | 0.835 |
| gbm_change | ml | 9.616 | 5.700 | 15.437 | 2.094 | 0.826 |
| ridge | ml | 10.742 | 6.801 | 17.243 | 1.260 | 0.783 |
| time_of_week_profile | baseline | 11.815 | 9.337 | 18.966 | -0.559 | 0.738 |
| time_of_day_profile | baseline | 11.880 | 9.250 | 19.071 | -0.503 | 0.735 |
| same_time_last_week | baseline | 13.315 | 7.037 | 21.373 | 1.689 | 0.667 |
| towt | baseline | 14.007 | 10.777 | 22.484 | 9.811 | 0.631 |
| persistence | baseline | 15.264 | 8.717 | 24.503 | 0.267 | 0.562 |
| same_time_yesterday | baseline | 15.264 | 8.717 | 24.503 | 0.267 | 0.562 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 10.452 | 14.912 |
| MAE (kWh) | 7.512 | 11.033 |
| CV(RMSE) % | 18.022 | 25.713 |
| NMBE % | -3.811 | -7.344 |
| R² | 0.825 | 0.644 |

Skill vs time_of_week_profile: **0.30** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 18.0% (limit 30%), NMBE -3.8% (limit ±10%): **passes**.

90% prediction interval: ±12 kWh (width from validation errors); it contained 81% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-03 to 2017-08-17 | 1632 | 0.21 |
| 2017-08-17 to 2017-10-24 | 1632 | 0.17 |
| 2017-10-24 to 2017-12-31 | 1632 | 0.34 |

Pooled skill: **0.26**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 28% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
