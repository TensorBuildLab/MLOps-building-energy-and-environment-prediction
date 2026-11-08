# Run report: bdg2-Robin_public_Cami

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 85.6602 for 44 d 10 h (2016-03-08 13:00:00 to 2016-04-21 23:00:00); 20 such stretch(es), 100 d 23 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 20 stuck stretch(es) set to missing. (2323)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-11 22:00:00 | 10654 |
| val | 2017-06-12 23:00:00 | 2017-09-17 07:00:00 | 2259 |
| test | 2017-09-18 08:00:00 | 2017-12-31 23:00:00 | 2260 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 6.950 | 5.241 | 11.516 | -4.682 | 0.820 |
| same_time_last_week | baseline | 8.201 | 6.037 | 13.588 | -1.149 | 0.749 |
| gbm | ml | 8.648 | 6.859 | 14.329 | -9.513 | 0.721 |
| gbm_change | ml | 9.006 | 6.835 | 14.924 | -9.533 | 0.697 |
| same_time_yesterday | baseline | 9.565 | 6.559 | 15.849 | -0.552 | 0.659 |
| persistence | baseline | 9.565 | 6.559 | 15.849 | -0.552 | 0.659 |
| time_of_day_profile | baseline | 16.024 | 14.254 | 26.552 | -23.476 | 0.042 |
| time_of_week_profile | baseline | 16.101 | 14.397 | 26.679 | -23.638 | 0.033 |
| towt | baseline | 23.002 | 21.810 | 38.114 | -36.065 | -0.974 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 8.615 | 13.269 |
| MAE (kWh) | 5.880 | 7.641 |
| CV(RMSE) % | 15.964 | 24.588 |
| NMBE % | -3.083 | -5.972 |
| R² | 0.781 | 0.481 |

Skill vs same_time_last_week: **0.35** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.0% (limit 30%), NMBE -3.1% (limit ±10%): **passes**.

90% prediction interval: ±10.8 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-11 to 2017-08-16 | 1523 | 0.20 |
| 2017-08-16 to 2017-10-19 | 1522 | 0.12 |
| 2017-10-19 to 2017-12-31 | 1522 | 0.36 |

Pooled skill: **0.29**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 84% |
| calendar (time of day, weekday) | 13% |
| airTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
