# Run report: bdg2-Bobcat_lodging_Melaine

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

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
| train | 2016-01-01 00:00:00 | 2017-06-08 06:00:00 | 11550 |
| val | 2017-06-09 07:00:00 | 2017-09-19 12:00:00 | 2451 |
| test | 2017-09-20 13:00:00 | 2017-12-31 23:00:00 | 2452 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 4.845 | 3.512 | 11.046 | 1.312 | 0.817 |
| gbm_change | ml | 5.172 | 3.760 | 11.790 | -0.085 | 0.791 |
| same_time_yesterday | baseline | 5.194 | 3.727 | 11.840 | 0.055 | 0.790 |
| persistence | baseline | 5.194 | 3.727 | 11.840 | 0.055 | 0.790 |
| gbm | ml | 5.486 | 4.004 | 12.507 | -0.097 | 0.765 |
| towt | baseline | 8.074 | 6.199 | 18.407 | 1.167 | 0.491 |
| same_time_last_week | baseline | 8.490 | 6.199 | 19.354 | 0.915 | 0.438 |
| time_of_week_profile | baseline | 9.916 | 7.517 | 22.605 | 4.315 | 0.233 |
| time_of_day_profile | baseline | 9.920 | 7.514 | 22.614 | 4.305 | 0.232 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 5.058 | 5.832 |
| MAE (kWh) | 3.487 | 3.902 |
| CV(RMSE) % | 11.471 | 13.225 |
| NMBE % | -0.635 | 0.187 |
| R² | 0.412 | 0.219 |

Skill vs same_time_yesterday: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.5% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±7.29 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-08 to 2017-08-16 | 1651 | 0.09 |
| 2017-08-16 to 2017-10-23 | 1650 | 0.08 |
| 2017-10-23 to 2017-12-31 | 1650 | 0.13 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 96% |
| calendar (time of day, weekday) | 2% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
