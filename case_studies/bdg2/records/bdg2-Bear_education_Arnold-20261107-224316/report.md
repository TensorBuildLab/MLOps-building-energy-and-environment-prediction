# Run report: bdg2-Bear_education_Arnold

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
| train | 2016-01-01 00:00:00 | 2017-05-26 02:00:00 | 11974 |
| val | 2017-05-27 03:00:00 | 2017-09-11 19:00:00 | 2543 |
| test | 2017-09-12 20:00:00 | 2017-12-31 23:00:00 | 2543 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 0.239 | 0.136 | 50.680 | -6.882 | 0.027 |
| time_of_day_profile | baseline | 0.252 | 0.163 | 53.362 | -16.047 | -0.079 |
| time_of_week_profile | baseline | 0.252 | 0.164 | 53.535 | -16.085 | -0.086 |
| towt | baseline | 0.254 | 0.163 | 53.861 | -15.434 | -0.099 |
| gbm_change | ml | 0.270 | 0.156 | 57.293 | -10.835 | -0.244 |
| gbm | ml | 0.276 | 0.155 | 58.578 | -11.926 | -0.300 |
| same_time_yesterday | baseline | 0.306 | 0.118 | 64.965 | -0.038 | -0.599 |
| persistence | baseline | 0.306 | 0.118 | 64.965 | -0.038 | -0.599 |
| same_time_last_week | baseline | 0.313 | 0.128 | 66.471 | 0.385 | -0.674 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.413 | 0.419 |
| MAE (kWh) | 0.238 | 0.246 |
| CV(RMSE) % | 72.770 | 73.846 |
| NMBE % | 5.841 | 5.834 |
| R² | 0.065 | 0.037 |

Skill vs time_of_day_profile: **0.01** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 72.8% (limit 30%), NMBE 5.8% (limit ±10%): **does not pass**.

90% prediction interval: ±0.233 kWh (width from validation errors); it contained 75% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-06 | 1711 | 0.09 |
| 2017-08-06 to 2017-10-19 | 1711 | 0.01 |
| 2017-10-19 to 2017-12-31 | 1710 | 0.01 |

Pooled skill: **0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 72% |
| calendar (time of day, weekday) | 26% |
| airTemperature | 1% |

> Warning: The model is barely better than time_of_day_profile on test data (skill 0.01).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
