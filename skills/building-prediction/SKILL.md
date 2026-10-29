---
name: building-prediction
description: Build, check and deploy prediction models for buildings from real BAS/BMS trend data with the bemlops Python package. Covers energy, electric power, cooling and heating load, zone temperature, CO2, humidity, occupancy and other sensor targets, in both forecasting and virtual-sensor (estimation) modes. Use when someone asks to predict, forecast or estimate anything in a building from sensor, meter or trend-log data, to clean BAS exports for modeling, or to check whether a building model is trustworthy.
---

# Building prediction with bemlops

You are the data scientist; `bemlops` is your referee. You handle the messy,
building-specific parts by writing whatever code the data needs. The package
checks your work and owns the steps that must never go wrong: units checked
against physics, time-ordered splits, no leakage, honest baselines, standard
metrics, and a full record of every run.

Install: `pip install bemlops` (or `pip install -e .` from this repository).

## Who does what

| You (the agent) | bemlops |
|---|---|
| Ask what decision the prediction supports | Refuses to fit until errors are dealt with |
| Load any export format (write a loader) | Accepts any pandas table with a time index |
| Work out what cryptic point names mean | Requires every used column to be declared |
| Decide how to handle faults and odd periods | Detects stuck sensors, spikes, -999s, bad units |
| Design extra features if they help | Builds lags so nothing comes from the future |
| Explain results to the human | Splits by time, compares with baselines, writes the run record |

## Workflow

### 1. Pin down the task with the human

Before touching data, make sure you know:
- **Target**: which point, and in what unit. Any trended point works: energy,
  power, loads, temperatures, CO2, humidity, occupancy counts. Yes/no points
  (occupied, equipment on) become classification tasks automatically when
  declared as `occupancy_status` or `equipment_status`.
- **Horizon**: how far ahead (e.g. 15 min for control, 1 h or 24 h for energy
  planning), or 0 for a virtual sensor (estimating a value from other sensors
  at the same moment).
- **Use**: what the prediction is for. That decides the time step and which
  error matters.

If any of these is unclear, ask. Do not guess the target.

### 2. Look at the data yourself and load it

Print `df.head()`, `df.dtypes`, `df.describe()`, and the full list of column
names. Then write a loader for whatever you find. See *Messy data playbook*
below. The goal is one table, one row per timestamp, one column per point,
with a `DatetimeIndex` (or a timestamp column you pass as `timestamp=`).

### 3. Declare the columns

Decode the point names (see [reference/bas-point-names.md](reference/bas-point-names.md))
and declare every column you want to use, as `"<quantity> [<unit>]"`:

```python
import bemlops
print(bemlops.quantities())          # every quantity you can declare, with units

columns = {
    "AHU1_CLG_KW": "electric_power [kW]",
    "OAT":         "outdoor_air_temperature [degF]",
    "RM204_ZN_T":  "zone_air_temperature [degF]",
    "RM204_ZN_SP": "temperature_setpoint [degF]",
    "RM204_OCC":   "occupancy_count",
    "SOL_RAD":     "solar_irradiance [W/m2]",
}
p = bemlops.Project(df, target="AHU1_CLG_KW", columns=columns, horizon="1h",
                    timestamp="Timestamp", timestamp_format="%m/%d/%Y %I:%M:%S %p")
```

- Undeclared columns are ignored. Leave out points you cannot identify, and
  say so to the human.
- Use `{"quantity": ..., "unit": ..., "known_ahead": True}` only for values
  truly known in advance: weather *forecasts*, occupancy *schedules*,
  *planned* setpoints. A measured value is never known ahead.
- Use quantity `other` for features you derived yourself.
- Shorthand flags work too: `"co2 [ppm] flat_ok"`, `"outdoor_air_temperature [degC] known_ahead"`.
- Timestamps with UTC offsets that change at daylight saving (`+0100`/`+0200`): pass
  `tz="Europe/Copenhagen"` (the building's zone) so calendar inputs use local hours.

### 4. Check the data and read every issue

```python
report = p.check_data()
print(report)
```

- **Errors** block fitting. Resolve each one:
  - The data or your declaration is wrong: fix it in your own code or the
    declaration, then `p.update(data=..., columns=..., note="why")`.
  - The data is fine as it is: `p.accept("issue-id", reason="...")` with a
    concrete reason the human could check. Never accept an issue just to make
    the error go away.
- **Warnings** are handled by `prepare()`. Still read them: a stuck sensor for
  a month or a large gap may change what the model can learn.
- Ask the human before decisions that change results materially: dropping
  weeks of data, excluding a season, or picking a unit when the evidence is
  ambiguous.

Record every judgment call with `p.note("...")`. Notes go into the run record.

### 5. Prepare

```python
p.prepare(freq="15min")      # or "1h"; match the decision the prediction supports
for step in p.prepare_log: print(step)
```

Standard and logged: unit conversion, masking of placeholders, impossible
values, stuck stretches and spikes, resampling, and forward-fill of short
input gaps. The target is never filled, and interval totals (energy) with
missing readings become missing rather than too small. Every step only uses
the past, so live serving cleans data exactly as training did.

### 6. Fit

```python
results = p.fit()            # ridge, random forest, gradient boosting, "change from last value" vs baselines
print(results)
```

Read the result before reporting it:
- **Skill** is measured against the strongest no-ML baseline on validation data:
  persistence, same time yesterday, or the time-of-day profile (for estimates,
  the training mean). If the skill is near 0 or negative, more model tuning will
  not help. Look for missing inputs, a data problem, or a horizon that is too long.
- **The backtest** refits the chosen model before each of three later blocks. If
  the single test period and the backtest disagree, say so: one period can be
  unusual (a holiday, a schedule change).
- **The 90% interval** and its test coverage, and **the main drivers** (which
  inputs the model relies on), belong in your explanation to the human.

**Your own features and models.** Compute extra inputs (rolling statistics, time
since the last change, a schedule flag) as ordinary columns from past and present
values only, declare them as `other`, and pass them in: bemlops lags them by the
horizon like any measured input, so they cannot leak. A model of your own goes in
through `p.fit(custom_models={"my_model": (estimator, search_space)})`, and is
judged by exactly the same split, baselines and gates.
- **Validation much better than test** usually means the test period differs
  (season, occupancy, operation change). Say so; consider more history.
- **Warnings** in the results must be passed on to the human.

### 7. Save and report

```python
folder = p.save_run("runs/")   # report.md, run.json, model.joblib, predictions, plots
```

Tell the human, in plain language:
1. What the data problems were and what was done about each (including your notes).
2. Accuracy in physical units (e.g. "MAE 0.4 degC", "CV(RMSE) 18%"), next to the baseline.
3. ASHRAE Guideline 14 verdict for energy-like targets.
4. Limitations: period covered, seasons not seen, inputs missing.

### 8. Register, promote, use and monitor

Production models go through the registry. Promotion is refused unless the
run passes the gates: data errors resolved, beats the baseline, Guideline 14
where it applies, no suspicious inputs, enough test data.

```python
reg = bemlops.Registry("models/")
entry = reg.register(folder)                   # candidate version, gates evaluated
reg.promote(p.name, entry["version"], reason="First model.")

model = reg.load(p.name)                       # the production model
forecast = model.predict(last_eight_days)      # validates the live data first; last rows = live forecast
# columns: predicted, lower/upper (90%), forecast_available_at, inputs_missing (>0: imputed inputs)
# known-ahead inputs (weather forecasts, schedules) for the future rows: predict(..., future_inputs=df)
print(model.check_drift(last_two_weeks))       # accuracy, input shift, new sensor faults
bemlops.retrain(all_data, reg, p.name)         # challenger vs champion on unseen data; promotes only if better
```

Never force a promotion past failed gates unless the human asks; if they
do, `promote(..., force=True, reason="...")` records it.

Suggest a retraining schedule (for example monthly, `bemlops retrain` from a
scheduler) rather than retraining only on a drift alarm: slow loss of skill
can stay below the alarm threshold for months. The gates and the
champion/challenger comparison keep a bad retrain out of production. If
`check_drift` reports that the model no longer beats persistence, tell the
human and suggest serving persistence until a retrained model wins again.

If `predict` raises `InvalidInputData`, the live feed has a problem (a unit
changed, a sensor died, a column vanished). Report it; do not silence it with
`on_error="warn"` unless the human agrees.

## Hard rules

1. Never split building time series randomly, and never write your own split
   (no `train_test_split`). `fit()` already splits by time with a gap.
2. Never use future information in features you build yourself: no centred
   rolling windows, no back-fill, no interpolation across a gap. Compute
   derived columns from past and present values only.
3. Never declare a measured value `known_ahead`.
4. Never change a declaration just to silence a check. If the check is
   wrong for this building, accept the issue with a reason.
5. Never report accuracy without its unit and the baseline next to it.
6. Never invent target values. Missing targets stay missing.
7. Keep raw building data local. Do not paste large raw extracts into
   messages or send them to outside services unless the human says so.

## Messy data playbook

**Long ("tidy") exports**: columns like `timestamp, point, value`. Pivot:
`df.pivot_table(index="timestamp", columns="point", values="value", aggfunc="mean")`.

**One file per point, each with its own timestamps** (change-of-value
logs): parse each, `pd.concat(series_list, axis=1)` on the union of
timestamps, and let `prepare()` resample. For status points, forward-fill
within your loader if the log only records changes.

**Excel exports**: skip title rows with `header=`/`skiprows=`; watch for a
units row under the header (read it, use it for the declarations, drop it).

**Timestamps**:
- Always pass `timestamp_format` when you can; `03/04` is March 4 in the US
  and April 3 elsewhere.
- UTC exports, or offsets that change at daylight saving: pass `tz=` with the
  building's time zone; the index is converted to local time with the zone kept.
- Unreadable timestamps above 1% stop the project: that is nearly always a
  wrong format (day-first vs month-first), not bad rows.
- Daylight saving: duplicate hour in autumn (averaged by `prepare()`),
  missing hour in spring (a gap). Arizona and Hawaii do not change clocks.

**Decimal commas** (`21,5`): European exports read without `decimal=","` are
reported as an error, never guessed. Re-read the file with `decimal=","`.

**Units**:
- A `unit_mismatch` error lists which unit the values fit. Check the BAS point
  configuration if you can; otherwise use the unit that fits and record a note.
- W vs kW cannot be told apart by range. Sanity-check magnitudes against the
  building (an office zone AHU drawing 5,000 kW is W).
- Relative humidity as 0-1 fractions: declare `relative_humidity [fraction]`.
- A `cumulative` error means a meter reading that only goes up: difference
  it, set negative jumps (meter resets or replacements) to missing, then
  declare it `energy`.

**Faults and odd periods**:
- Stuck sensors and spikes are masked by `prepare()`. A sensor stuck for
  most of the period should be dropped instead; note it.
- Commissioning, retrofits, holidays, overrides and occupancy changes (e.g. a
  semester break) change behaviour. Ask the human whether to exclude or keep
  them; never silently drop data.
- A zone that is always in alarm, or a setpoint that never changes, is still
  information. A constant column is dropped automatically.
- **Cross-check related points.** No single-column check sees a meter that
  reads exactly 0 for weeks while its valve is open and the fan runs, or a
  people count stuck at 1 overnight while the lights are off. Look for these
  contradictions yourself, set the faulty stretch to missing in your loader,
  and note why.
- A unit that changes part-way through (`out_of_range` error naming the
  switch time and unit): convert the later readings in your own code, then
  `p.update(data=...)`.

**Derived features** that often help: degree-hours, supply-minus-zone
temperature difference, occupied-mode flags from setpoint changes, holiday
flags. Declare them as `other`, and mark them `known_ahead` only if computed
from known-ahead inputs (calendars, schedules, forecasts).

## Choosing metrics

| Target | Headline metric | Notes |
|---|---|---|
| Energy, electric power, cooling/heating load | CV(RMSE), NMBE | Guideline 14 hourly: CV(RMSE) <= 30%, NMBE within +/-10% |
| Zone, supply, water temperature | MAE in degC | CV(RMSE) is meaningless for temperatures |
| CO2 | MAE in ppm | Look at occupied hours separately if comfort is the goal |
| Relative humidity | MAE in % RH | |
| Occupancy count | MAE in people | Many zeros: also check occupied hours |
| Yes/no (occupied, equipment on) | Brier score, balanced accuracy | Skill is the Brier skill score vs "same as before" |

Always compare with the baseline in the same unit.
