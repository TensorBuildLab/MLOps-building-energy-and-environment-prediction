## 3. Framework

### 3.1 Division of labour

Table 1 lists who does what. The agent may write any code it needs; the
package accepts any time-indexed table and never limits what the agent does
before handing data over. What the package controls is what happens after:
nothing reaches a model unless it has been declared, checked and prepared in
a logged, deterministic way, and nothing reaches production unless it has
passed explicit gates.

**Table 1.** Division of labour.

| The agent (judgment) | The guardrails (guarantees) |
|---|---|
| Clarify target, horizon and use with the human | Refuse to fit while data errors are unresolved |
| Load any export format | Accept any table with a time index |
| Decode point names and declare quantity and unit | Check every declaration against physical ranges and name the likely unit when it is wrong |
| Decide what faults and unusual periods mean | Detect stuck sensors, spikes, placeholder values, text, duplicates, gaps, cumulative meters |
| Design extra inputs | Build lags so that no input reaches past the forecast time; audit every input |
| Explain the results | Time-ordered evaluation, baselines, standard metrics, model card, full record |

### 3.2 Declarations as the interface

The interface between judgment and guarantees is a **declaration**: for each
column the agent wants to use, a physical quantity (zone air temperature,
electric power, CO2, occupancy status, and so on) and a unit. Point names
are ambiguous and vendor-specific; a declaration is explicit and checkable.
Each quantity carries a canonical unit, conversions, a physically plausible
range, a narrower typical range used to infer units, and behavioural flags
(for example, setpoints may legitimately stay constant for days, and solar
irradiance is legitimately zero all night). Only declared columns are used.
The target's quantity also fixes the task type: numeric quantities are
regression tasks; yes/no quantities (occupancy status, equipment status) are
classification tasks.

### 3.3 Guardrails

**Data checks.** Issues have three severities. *Errors* (a unit that does not
fit the values, a quantity that fits in no unit, a cumulative meter declared
as interval energy, an empty target) block fitting until the agent fixes the
data or declaration, or accepts the issue with a written reason. *Warnings*
(stuck sensors, spikes, placeholder values, text entries, duplicates,
disorder, gaps) are handled by a standard preparation step that logs every
action. *Information* covers the rest.

**Preparation.** Rows are sorted and de-duplicated, text is converted or set
missing, units are converted to canonical units, placeholder values,
impossible readings, stuck stretches and spikes are set missing, and the data
are resampled to a regular grid. Input gaps are filled forward only, up to a
limit, because interpolation uses future values that a live system does not
have. The target is never filled.

**Leakage-safe inputs.** For a forecast *h* steps ahead, the prediction for
interval *T* uses measured data from intervals up to *T − h* only. Target
lags, rolling means and measured inputs are shifted accordingly; only inputs
declared as known in advance (weather forecasts, schedules) may be used at
*T*. Every input records how far back it reaches, and an audit refuses any
that reaches forward. Inputs that are near-copies of the target are flagged.
In estimation mode (*h* = 0), the target is estimated from other inputs at the
same moment, as a virtual sensor, and never appears among its own inputs.

**Evaluation.** There is no random split. Data are split in time order into
training, validation and test sets with a gap of *h* steps between them, so
no forecast is scored by a model trained on later data. Hyperparameters are
tuned by random search with time-ordered cross-validation on the training set
only. Every task includes no-skill baselines: persistence (the latest known
value, and the value at the same time yesterday) for forecasts, the training
mean or the share of "yes" for estimates. The model with the lowest validation
error is chosen, even when that is a baseline. Accuracy is reported as skill
against the baseline (one minus the ratio of RMSE, or of the Brier score
[Brier 1950] for yes/no targets), together with errors in physical units and,
for energy-like targets at hourly or finer resolution, the ASHRAE Guideline 14
hourly criteria (CV(RMSE) ≤ 30%, |NMBE| ≤ 10%) [ASHRAE 2014].

**Promotion gates.** A model reaches production only through a registry that
evaluates five gates from the run record: data errors resolved, skill above a
minimum, Guideline 14 passed where it applies, no suspicious inputs, and
enough test data. Overriding a gate requires a written reason and is logged.

**Monitoring.** Every live prediction re-runs the data checks and compares
the live inputs with the training data; this catches failures that range
checks alone cannot, such as an outdoor-temperature feed switching units
(both readings are plausible outdoor temperatures). A drift check compares
recent accuracy with test-time accuracy, flags inputs outside the training
range, and reports new sensor faults, separating problems that retraining can
fix from those it cannot.

**Continuous training.** Retraining reuses the production model's
configuration on newer data, scores champion and challenger on the same rows
that neither has trained on, and promotes the challenger only if it passes
the gates and wins.

### 3.4 MLOps coverage

Table 2 maps the framework to the nine MLOps principles of Kreuzberger et al.
[2023]. Two components of their reference architecture are deliberately
absent: a shared feature store (features are rebuilt from the declared
configuration by the same code in training and serving, which removes the
training-serving skew a feature store guards against at single-building
scale) and an online serving endpoint (serving is batch or scheduled; a web
service is a thin wrapper).

**Table 2.** MLOps principles [Kreuzberger et al. 2023] and their implementation.

| Principle | Implementation |
|---|---|
| P1 CI/CD automation | Tests, including end-to-end model tests, run on every commit; models are delivered through gated promotion |
| P2 Workflow orchestration | `train`, `retrain`, `reproduce` and a command-line interface with exit codes, for any scheduler |
| P3 Reproducibility | Full configuration, seeds, versions, code commit and data fingerprints in every run record; `reproduce` re-runs a record and checks that every metric matches exactly |
| P4 Versioning | Code commit; numbered model versions; data fingerprints |
| P5 Collaboration | Report and model card per run; decisions and accepted issues recorded with reasons |
| P6 Continuous training and evaluation | Champion/challenger retraining on unseen data |
| P7 Metadata tracking | Run records and a registry event log |
| P8 Continuous monitoring | Live data validation, training-vs-live comparison, drift and fault monitoring |
| P9 Feedback loops | Monitoring triggers retraining; data checks feed back to the agent |

### 3.5 The agent's instructions

The agent learns the workflow from an Agent Skill [Anthropic 2025]: a short
instruction file, loaded on demand, that sets out the workflow (clarify the
task, inspect and load the data, declare columns, resolve every check,
prepare, fit, report, register, monitor), seven hard rules (for example,
never split building time series at random, never declare a measured value
as known in advance, never change a declaration to silence a check), a
playbook for messy data, and a reference for decoding BAS point names. The
skill is the successor of the 2024 prompt template: instead of prescribing
code, it prescribes conduct.
