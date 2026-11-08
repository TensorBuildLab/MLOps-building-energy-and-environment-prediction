# Run report: bdg2-Bear_education_Wilton

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing. |

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
| train | 2016-01-01 00:00:00 | 2017-05-26 20:00:00 | 12268 |
| val | 2017-05-27 21:00:00 | 2017-09-13 09:00:00 | 2605 |
| test | 2017-09-14 10:00:00 | 2017-12-31 23:00:00 | 2606 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 98.157 | 70.990 | 5.980 | 1.473 | 0.700 |
| persistence | baseline | 103.518 | 72.082 | 6.307 | 0.210 | 0.667 |
| same_time_yesterday | baseline | 103.518 | 72.082 | 6.307 | 0.210 | 0.667 |
| gbm_change | ml | 105.308 | 71.487 | 6.416 | 2.251 | 0.655 |
| gbm | ml | 107.588 | 74.567 | 6.555 | 2.393 | 0.640 |
| time_of_day_profile | baseline | 172.281 | 120.861 | 10.496 | 6.923 | 0.077 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 111.449 | 128.364 |
| MAE (kWh) | 86.691 | 88.930 |
| CV(RMSE) % | 6.700 | 7.717 |
| NMBE % | 1.586 | -0.078 |
| R² | 0.581 | 0.444 |

Skill vs persistence: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.7% (limit 30%), NMBE 1.6% (limit ±10%): **passes**.

90% prediction interval: ±164 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.07 |
| 2017-08-07 to 2017-10-19 | 1753 | 0.13 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.10 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 82% |
| calendar (time of day, weekday) | 16% |
| windSpeed | 2% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
