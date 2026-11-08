# Run report: bdg2-Bobcat_office_Alma

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 3 for 10 h (2017-05-05 22:00:00 to 2017-05-06 08:00:00); 24 such stretch(es), 6 d 21 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 24 stuck stretch(es) set to missing. (45)
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
| train | 2016-01-01 00:00:00 | 2017-06-09 12:00:00 | 11395 |
| val | 2017-06-10 13:00:00 | 2017-09-19 09:00:00 | 2417 |
| test | 2017-09-20 10:00:00 | 2017-12-31 23:00:00 | 2420 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 1.638 | 1.263 | 30.407 | 2.283 | 0.396 |
| gbm_change | ml | 1.710 | 1.297 | 31.754 | 1.587 | 0.341 |
| gbm | ml | 1.730 | 1.315 | 32.123 | 0.348 | 0.326 |
| towt | baseline | 1.735 | 1.344 | 32.220 | 3.239 | 0.322 |
| same_time_yesterday | baseline | 2.026 | 1.488 | 37.608 | 0.310 | 0.076 |
| persistence | baseline | 2.026 | 1.488 | 37.608 | 0.310 | 0.076 |
| time_of_day_profile | baseline | 2.120 | 1.699 | 39.358 | 18.576 | -0.012 |
| time_of_week_profile | baseline | 2.120 | 1.696 | 39.367 | 18.594 | -0.013 |
| same_time_last_week | baseline | 2.339 | 1.758 | 43.422 | 0.287 | -0.232 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(4.135997393839888)}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.117 | 1.299 |
| MAE (kWh) | 0.843 | 1.033 |
| CV(RMSE) % | 31.891 | 37.088 |
| NMBE % | -4.053 | -17.592 |
| R² | 0.265 | 0.006 |

Skill vs towt: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 31.9% (limit 30%), NMBE -4.1% (limit ±10%): **does not pass**.

90% prediction interval: ±2.66 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-16 | 1628 | 0.05 |
| 2017-08-16 to 2017-10-23 | 1628 | 0.07 |
| 2017-10-23 to 2017-12-31 | 1628 | 0.15 |

Pooled skill: **0.08**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 62% |
| calendar (time of day, weekday) | 31% |
| airTemperature | 6% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
