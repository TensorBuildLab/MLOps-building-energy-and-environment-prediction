# Run report: bdg2-Bear_education_Lorie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

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
| train | 2016-01-01 00:00:00 | 2017-05-25 11:00:00 | 12241 |
| val | 2017-05-26 12:00:00 | 2017-09-12 01:00:00 | 2599 |
| test | 2017-09-13 02:00:00 | 2017-12-31 23:00:00 | 2600 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 30.049 | 20.701 | 7.124 | 1.897 | 0.731 |
| gbm_change | ml | 32.115 | 21.266 | 7.614 | 2.699 | 0.693 |
| gbm | ml | 32.255 | 21.294 | 7.647 | 2.830 | 0.690 |
| persistence | baseline | 34.887 | 23.815 | 8.271 | 0.294 | 0.637 |
| same_time_yesterday | baseline | 34.887 | 23.815 | 8.271 | 0.294 | 0.637 |
| towt | baseline | 37.878 | 26.987 | 8.980 | 4.979 | 0.572 |
| same_time_last_week | baseline | 45.334 | 33.406 | 10.748 | 0.935 | 0.387 |
| time_of_day_profile | baseline | 45.566 | 32.176 | 10.803 | 6.425 | 0.381 |
| time_of_week_profile | baseline | 45.816 | 32.282 | 10.862 | 6.439 | 0.374 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 28.337 | 35.052 |
| MAE (kWh) | 20.559 | 23.701 |
| CV(RMSE) % | 6.958 | 8.607 |
| NMBE % | -0.281 | 0.022 |
| R² | 0.772 | 0.651 |

Skill vs persistence: **0.19** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.0% (limit 30%), NMBE -0.3% (limit ±10%): **passes**.

90% prediction interval: ±46.5 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1749 | 0.19 |
| 2017-08-06 to 2017-10-18 | 1749 | 0.13 |
| 2017-10-18 to 2017-12-31 | 1749 | 0.19 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 74% |
| calendar (time of day, weekday) | 24% |
| airTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
