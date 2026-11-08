# Run report: bdg2-Bear_education_Irene

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 69 for 8 h (2017-09-04 22:00:00 to 2017-09-05 06:00:00); 4 such stretch(es), 1 d 4 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (8)
- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-25 11:00:00 | 12247 |
| val | 2017-05-26 12:00:00 | 2017-09-11 22:00:00 | 2600 |
| test | 2017-09-12 23:00:00 | 2017-12-31 23:00:00 | 2602 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 30.009 | 22.753 | 35.753 | -9.511 | 0.037 |
| gbm | ml | 30.235 | 20.049 | 36.022 | -6.434 | 0.023 |
| time_of_day_profile | baseline | 30.782 | 24.146 | 36.674 | -9.041 | -0.013 |
| gbm_change | ml | 32.006 | 21.326 | 38.132 | -9.867 | -0.095 |
| time_of_week_profile | baseline | 33.080 | 23.113 | 39.412 | -8.797 | -0.170 |
| towt | baseline | 33.189 | 23.388 | 39.542 | -9.206 | -0.178 |
| same_time_last_week | baseline | 36.506 | 16.867 | 43.494 | -0.278 | -0.425 |
| persistence | baseline | 45.099 | 24.675 | 53.731 | -0.097 | -1.175 |
| same_time_yesterday | baseline | 45.099 | 24.675 | 53.731 | -0.097 | -1.175 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 27.903 | 28.355 |
| MAE (kWh) | 21.088 | 22.119 |
| CV(RMSE) % | 34.773 | 35.337 |
| NMBE % | -13.137 | -12.446 |
| R² | -0.099 | -0.135 |

Skill vs time_of_day_profile: **0.02** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 34.8% (limit 30%), NMBE -13.1% (limit ±10%): **does not pass**.

90% prediction interval: ±53.7 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1750 | -0.03 |
| 2017-08-06 to 2017-10-18 | 1750 | 0.08 |
| 2017-10-18 to 2017-12-31 | 1750 | 0.01 |

Pooled skill: **0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 51% |
| electricity (recent history) | 49% |

> Warning: The model is barely better than time_of_day_profile on test data (skill 0.02).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
