## 3. Framework

This section describes the version used for every result in Section 6
(package version 0.2.0.dev0, source fingerprint `f394d2e9ee9047c8`). Changes
made after the experiments are listed in Appendix A and are not evaluated.

### 3.1 Division of labour

Figure 1 and Table 2 show who does what. The agent may write any code it
needs. The package accepts any table with a time index and does not limit
what the agent does before handing data over. It controls what happens after
that point:
- nothing reaches a model unless it has been declared, checked and prepared
  in a logged, deterministic way;
- nothing reaches production unless it has passed explicit gates.

![Figure 1. Division of labour between the LLM agent and the package. Blue arrows carry the agent's declarations and decisions down; grey arrows carry issue reports, results and alerts back up. Every run leaves one record.](figures/framework.png)

**Table 2.** Division of labour.

| The agent (judgment) | The package (checks that are the same every time) |
|---|---|
| Clarify target, horizon and use with the person who asked | Refuse to fit while data errors are unresolved |
| Load any export format | Accept any table with a time index |
| Decode point names; declare quantity and unit | Check every declaration against physical ranges; name the likely unit when it is wrong |
| Decide what faults and unusual periods mean | Detect stuck sensors, spikes, placeholder values, text, duplicates, gaps, cumulative meters |
| Design extra inputs; mark what is known in advance | Shift every measured input by the horizon; audit how far each input reaches |
| Add own models if needed | Evaluate every model the same way: time-ordered, against the strongest no-ML baseline |
| Explain the results | Report, model card, gates, registry, monitoring; one record per run |

### 3.2 Declarations as the interface

The interface between the agent and the package is a **declaration**. For
each column the agent wants to use, it states a physical quantity (zone air
temperature, electric power, CO2, occupancy status, and so on) and a unit,
for example `"zone_air_temperature [degF]"`. Point names are ambiguous and
vendor-specific; a declaration is explicit and can be checked.

Each quantity carries:
- a canonical unit and conversions;
- a physically plausible range, and a narrower typical range used to infer
  the most likely unit when the declared one does not fit;
- behavioural flags. For example, setpoints may stay constant for days,
  solar irradiance is zero all night, and an idle meter may sit at zero.

Two shorthand flags let the agent record knowledge the package cannot infer:
- `flat_ok`: long flat stretches are normal for this sensor, for example a
  CO2 sensor floor;
- `known_ahead`: the value is known at forecast time, for example a schedule
  or a weather forecast.

Only declared columns are used. The target's quantity fixes the task type:
numeric quantities give regression tasks, and yes/no quantities (occupancy
status, equipment status) give classification tasks. The evaluated version
has 24 quantities, including a generic `other` for inputs without physical
checks.

### 3.3 Data checks and preparation

Issues have three severities:
- **Errors** block fitting until the agent fixes the data or the declaration,
  or accepts the issue with a written reason. Examples: a unit that does not
  fit the values, a unit that changes part-way through a series, a quantity
  that fits in no unit, a cumulative meter declared as interval energy,
  decimal commas, an empty target.
- **Warnings** are handled by the standard preparation step, which logs every
  action. Examples: stuck sensors, spikes, placeholder values, text entries,
  duplicates, rows out of order, gaps.
- **Information** covers everything else.

Preparation proceeds in this order:
1. Rows are sorted and de-duplicated, and text is converted or set missing.
2. Units are converted to canonical units.
3. Placeholder values and physically impossible readings are set missing.
4. Stuck stretches and spikes are set missing.
5. The data are resampled to a regular grid.

Cleaning is **causal**: a decision about a reading uses only that reading and
earlier ones. A spike is judged against the median of the four preceding
readings. A stretch of identical values is masked only from the point at
which it has lasted long enough to be detected (6 h by default), not from its
start. Stretches never span a gap in the data. An interval total, such as
energy per 15 minutes, is computed only when every reading in the interval is
present. Inputs are filled forward only, up to a limit, because interpolation
uses values a live system does not yet have. The target is never filled.

### 3.4 Inputs that cannot reach past the forecast time

For a forecast *h* steps ahead, the prediction for interval *T* uses measured
data from intervals up to *T* − *h* only. Target lags, rolling means and
measured inputs are shifted accordingly. Only inputs declared `known_ahead`
may be used at *T*. Every input records how far back it reaches, and an audit
refuses any input that reaches forward. Inputs whose correlation with the
target exceeds 0.995 are flagged as possible copies of it. In estimation mode
(*h* = 0), the target is estimated from other inputs at the same moment, as a
virtual sensor, and never appears among its own inputs. Day-of-year inputs
are added only when the training data cover a full year.

### 3.5 Evaluation

There is no random split.
- **Split.** Data are split in time order into training, validation and test
  sets (70/15/15 by default), with a gap of *h* steps between them.
- **Tuning.** Hyperparameters are tuned by random search with time-ordered
  cross-validation on the training set only.
- **Baselines.** Every task includes no-ML baselines:
  - for forecasts: persistence (the latest known value), the value at the same
    time the day before, and a time-of-day profile (the training mean for each
    time of day, separately for weekdays and weekends);
  - for estimates: the training mean, or the share of "yes".
- **Reference.** The strongest baseline on validation becomes the reference
  for that task.
- **Candidates.** For regression: ridge regression, a random forest, gradient
  boosting, and gradient boosting on the change from the latest known value
  (`gbm_change`). For classification: logistic regression, a random forest
  and gradient boosting. The agent can add its own.
- **Choice.** The candidate or baseline with the lowest validation error is
  chosen, even when it is a baseline.
- **Test.** The chosen model and the reference are refitted on training plus
  validation data and scored once on the test set.

Accuracy is reported as skill against the reference: one minus the ratio of
root-mean-square errors (RMSE), or of Brier scores [Brier 1950] for yes/no
targets. This is not the more common MSE skill score. An RMSE skill of 0.05
corresponds to an MSE skill of about 0.10.

The record also contains:
- errors in physical units;
- for energy-like targets, the ASHRAE Guideline 14 hourly criteria
  (CV(RMSE) ≤ 30% and |NMBE| ≤ 10%), computed on the test set at the task's
  resolution [ASHRAE 2014];
- a rolling-origin backtest: the period after training is cut into three
  blocks, and before each block the chosen configuration is refitted on all
  earlier data. The backtest overlaps the validation period that chose the
  model, so it is a check on stability, not an independent test;
- a 90% prediction interval. Its half-width is the 90th percentile of the
  absolute validation errors of the chosen model (trained on the training
  set only), in the manner of split conformal prediction. Its coverage is
  reported on the test set;
- grouped permutation importance of the inputs.

### 3.6 Promotion gates

A model reaches production only through a registry, which evaluates five
gates from the run record:
- every data error is resolved or accepted;
- test skill is at least 0.05;
- Guideline 14 is met, where it applies;
- no input is flagged as a possible copy of the target or as reaching
  forward;
- the test set has at least 200 rows.

The gates use the single test window, not the backtest. Overriding a gate
requires a written reason and is logged. Accepted issues from earlier runs
never approve errors on new data.

### 3.7 Monitoring and continuous training

Every live prediction does three things:
- re-runs the data checks;
- rebuilds every trained input with the training code;
- checks that the live time zone matches training.

A drift check on recent data recommends retraining in either of two cases:
- the recent primary error exceeds 1.5 times the test-time error;
- more than 20% of an input's recent values fall outside its training range,
  widened by 10% on each side.

The drift check also reports new sensor faults. It separates problems that
retraining can fix from those it cannot.

Retraining reuses the production configuration on newer data. The champion
and the challenger are scored on rows that start after both training periods
plus the horizon. The challenger is promoted only if it passes the gates and
has the lower error.

### 3.8 MLOps coverage

Table 3 maps the framework to the nine MLOps principles of Kreuzberger et al.
[2023]. Two components of their reference architecture are deliberately
absent:
- **A shared feature store.** Features are rebuilt from the declared
  configuration by the same code in training and serving. At single-building
  scale this removes the training-serving skew that a feature store guards
  against.
- **An online serving endpoint.** Serving is batch or scheduled; a web service
  would be a thin wrapper.

**Table 3.** MLOps principles [Kreuzberger et al. 2023] and their implementation.

| Principle | Implementation |
|---|---|
| P1 CI/CD automation | Tests, including end-to-end model tests, run on every commit; models are delivered through gated promotion |
| P2 Workflow orchestration | `train`, `retrain` and `reproduce` pipelines and a command-line interface with exit codes, for any scheduler |
| P3 Reproducibility | Configuration, declarations, notes, seeds, library versions, code commit, package fingerprint and data fingerprints in every run record; `reproduce` re-runs a record and checks that every metric matches |
| P4 Versioning | Code commit and package fingerprint; numbered model versions; data fingerprints |
| P5 Collaboration | Report and model card per run; decisions and accepted issues recorded with reasons |
| P6 Continuous training and evaluation | Champion/challenger retraining on rows neither model has seen |
| P7 Metadata tracking | Run records and a registry event log |
| P8 Continuous monitoring | Live data validation, training-serving comparison, drift and fault monitoring |
| P9 Feedback loops | Monitoring recommends retraining; data checks feed back to the agent |

Reproducibility here means re-executing the agent's frozen decisions (its
declarations, notes and accepted issues), not re-running the agent, which is
not deterministic.

### 3.9 The agent's instructions

The agent learns the workflow from an Agent Skill [Zhang et al. 2025a]: a
short instruction file loaded on demand. It contains:
- **the workflow:** clarify the task, inspect and load the data, declare
  columns, resolve every check, prepare, fit, report, register, monitor;
- **seven rules,** for example: never split building time series at random,
  never declare a measured value as known in advance, never change a
  declaration to silence a check;
- **a playbook** for messy data;
- **a reference** for decoding point names in building automation systems.

The skill is the successor of the 2024 prompt template. Instead of
prescribing code, it prescribes conduct.
