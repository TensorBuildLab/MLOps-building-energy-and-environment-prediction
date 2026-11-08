# Run report: bdg2-Bobcat_lodging_Nickolas

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 19 stuck stretch(es) set to missing. (38)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (35)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (122)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-08 10:00:00 | 11550 |
| val | 2017-06-09 11:00:00 | 2017-09-19 16:00:00 | 2451 |
| test | 2017-09-20 17:00:00 | 2017-12-31 23:00:00 | 2451 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 4.343 | 3.334 | 10.955 | -4.404 | 0.645 |
| persistence | baseline | 4.535 | 3.154 | 11.441 | -0.430 | 0.613 |
| same_time_yesterday | baseline | 4.535 | 3.154 | 11.441 | -0.430 | 0.613 |
| gbm | ml | 8.513 | 7.501 | 21.477 | -17.324 | -0.365 |
| gbm_change | ml | 8.594 | 7.545 | 21.679 | -17.431 | -0.391 |
| time_of_day_profile | baseline | 13.607 | 12.337 | 34.325 | -30.462 | -2.486 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.951 | 5.186 |
| MAE (kWh) | 3.726 | 3.477 |
| CV(RMSE) % | 14.450 | 15.136 |
| NMBE % | -6.490 | 0.053 |
| R² | 0.103 | 0.015 |

Skill vs persistence: **0.05** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.4% (limit 30%), NMBE -6.5% (limit ±10%): **passes**.

90% prediction interval: ±6.66 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-08 to 2017-08-16 | 1650 | 0.04 |
| 2017-08-16 to 2017-10-24 | 1650 | 0.02 |
| 2017-10-24 to 2017-12-31 | 1650 | 0.10 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 91% |
| calendar (time of day, weekday) | 5% |
| airTemperature | 5% |

> Warning: The model is barely better than persistence on test data (skill 0.05).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
