# Framework {#sec:framework}

This section describes the version used for every result in @sec:results (package version 0.2.0.dev0, source fingerprint *f394d2e9ee9047c8*). Changes made after the experiments are listed in the Supplementary Material and are not evaluated.

## Division of labor {#sec:division}

@fig:framework and @tbl:division show the division of labor. The agent may write any code it needs, and the package accepts any table with a time index without limiting what the agent does beforehand. The package controls what happens after that point: nothing reaches a model unless it has been declared, checked and prepared in a logged, deterministic way, and nothing reaches production unless it has passed explicit gates.

![Division of labor between the LLM agent and the package. The agent's declarations and decisions flow down to the package; issue reports, results and alerts flow back up. Every run leaves one record.](../figures/framework.png){#fig:framework width=100%}

Table: Division of labor between the agent and the package. {#tbl:division}

| The agent (judgment) | The package (checks that are the same for every model) |
|:---|:---|
| Clarify the target, horizon and intended use with the person who asked | Refuse to fit while data errors are unresolved |
| Load any export format | Accept any table with a time index |
| Decode point names; declare quantity and unit | Check every declaration against physical ranges and name the likely unit when it is wrong |
| Decide what faults and unusual periods mean | Detect stuck sensors, spikes, placeholder values, text, duplicates, gaps and cumulative meters |
| Design extra inputs; mark what is known in advance | Shift every measured input by the horizon and audit how far each input reaches |
| Add its own models if needed | Evaluate every model in the same way: in time order, against the strongest no-ML baseline |
| Explain the results | Report, model card, gates, registry, monitoring and one record per run |

## Declarations as the interface

The interface between the agent and the package is a declaration. For each column it wants to use, the agent states a physical quantity (zone air temperature, electric power, CO~2~ concentration, occupancy status and so on) and a unit, for example *zone_air_temperature [degF]*. Point names are ambiguous and vendor-specific, whereas a declaration is explicit and can be checked. Each quantity carries a canonical unit and its conversions, a physically plausible range, a narrower typical range from which the most likely unit is inferred when the declared one does not fit, and behavioral flags: setpoints may stay constant for days, solar irradiance is zero at night, and an idle meter may sit at zero. Two further flags record knowledge that the package cannot infer: *flat_ok* marks sensors whose long flat stretches are normal, such as a CO~2~ sensor at its floor, and *known_ahead* marks values that are known at forecast time, such as schedules or weather forecasts. Only declared columns are used. The quantity of the target fixes the task type: numeric quantities define regression tasks and binary quantities (occupancy status, equipment status) define classification tasks. The evaluated version has 24 quantities, including a generic *other* for inputs without physical checks.

## Data checks and preparation

The data check reports issues with three severities. Errors block fitting until the agent fixes the data or the declaration, or accepts the issue with a written reason; they include a unit that does not fit the values, a unit that changes part-way through a series, a quantity that fits no unit, a cumulative meter declared as interval energy, decimal commas and an empty target. Warnings, such as stuck sensors, spikes, placeholder values, text entries, duplicates, out-of-order rows and gaps, are handled by a standard preparation step that logs every action. Information covers everything else.

Preparation sorts and de-duplicates the rows, converts text or sets it missing, converts units to canonical units, sets placeholder values and physically impossible readings missing, masks stuck stretches and spikes, and resamples the data to a regular grid. Cleaning is causal: a decision about a reading uses only that reading and earlier ones. A spike is judged against the median of the four preceding readings, and a stretch of identical values is masked only from the point at which it has lasted long enough to be detected (6 h by default), never across a gap in the data. An interval total, such as the energy in 15 min, is computed only when every reading in the interval is present. Inputs are filled forward only, up to a limit, because interpolation uses values that a live system does not yet have, and the target is never filled.

## Inputs that cannot reach past the forecast time

For a forecast $h$ steps ahead, the prediction for interval $T$ uses measured data from intervals up to $T-h$ only. Lags and rolling means of the target and of measured inputs are shifted accordingly, and only inputs declared *known_ahead* may be used at $T$. Every input records how far back it reaches, and an audit refuses any input that reaches forward. Inputs whose correlation with the target exceeds 0.995 are flagged as possible copies of it. In estimation mode ($h=0$), the target is estimated from other inputs at the same moment, as a virtual sensor, and never appears among its own inputs. Day-of-year inputs are added only when the training data cover a full year.

## Evaluation {#sec:evaluation}

The data are split in time order into training, validation and test sets (70/15/15% by default), with a gap of $h$ steps between consecutive sets; there is no random split. Hyperparameters are tuned by random search with time-ordered cross-validation on the training set only. Every task includes baselines without machine learning. For forecasts these are persistence (the latest known value), the value at the same time on the previous day, and a time-of-day profile (the training mean for each time of day, separately for weekdays and weekends); for estimates they are the training mean or the share of positive labels. The strongest baseline on the validation set becomes the reference for the task. The candidate models are ridge regression, a random forest, gradient boosting, and gradient boosting on the change from the latest known value for regression, and logistic regression, a random forest and gradient boosting for classification; the agent can add its own. The candidate or baseline with the lowest validation error is chosen, even when it is a baseline, and the chosen model and the reference are refitted on the training and validation data and scored once on the test set.

Accuracy is reported as skill against the reference,

$$ S = 1 - \frac{\mathrm{RMSE}_{\mathrm{model}}}{\mathrm{RMSE}_{\mathrm{ref}}} $$ {#eq:skill}

where RMSE is replaced by the Brier score [@brier1950] for binary targets. @eq:skill is defined on RMSE rather than on mean square error, so a skill of 0.05 corresponds to a mean-square-error skill of about 0.10. Errors are also reported in physical units. For energy-like targets, the ASHRAE Guideline 14 hourly criteria [@ashrae2014] are evaluated on the test predictions aggregated to hours (hourly totals for energy and hourly means for power):

$$ \mathrm{CV(RMSE)} = \frac{100}{|\bar{y}|} \sqrt{\frac{\sum_{t=1}^{n} e_t^2}{n-1}} \le 30\% $$ {#eq:cvrmse}

$$ \left|\mathrm{NMBE}\right| = \frac{100}{|\bar{y}|} \left| \frac{\sum_{t=1}^{n} e_t}{n-1} \right| \le 10\% $$ {#eq:nmbe}

where $e_t = y_t - \hat{y}_t$. Each run also reports a rolling-origin backtest, in which the period after training is cut into three blocks and the chosen configuration is refitted on all earlier data before each block. Because the backtest overlaps the validation period that chose the model, it is a check on stability, not an independent test. A 90% prediction interval $\hat{y}_t \pm q_{0.9}$ is reported, where $q_{0.9}$ is the 90th percentile of the absolute validation errors of the chosen model trained on the training set only, in the manner of split conformal prediction; its coverage is measured on the test set. Finally, grouped permutation importance indicates which inputs the model relies on.

## Promotion gates, monitoring and retraining {#sec:gates}

A model reaches production only through a registry that evaluates five gates from the run record: every data error is resolved or accepted, the test skill is at least 0.05, Guideline 14 is met where it applies, no input is flagged as a possible copy of the target or as reaching forward, and the test set has at least 200 rows. The gates use the single test window, not the backtest. Overriding a gate requires a written reason and is logged, and issues accepted in earlier runs never approve errors on new data.

Every live prediction re-runs the data checks, rebuilds every trained input with the training code and checks that the time zone of the live data matches training. A drift check on recent data recommends retraining when the recent primary error exceeds 1.5 times the error at test time, or when more than 20% of the recent values of an input fall outside its training range widened by 10% on each side; it also reports new sensor faults and separates problems that retraining can fix from those it cannot. Retraining reuses the production configuration on newer data, scores the champion and the challenger on rows that start after both training periods plus the horizon, and promotes the challenger only if it passes the gates and has the lower error.

@tbl:mlops maps the framework to the nine MLOps principles of Kreuzberger et al. [@kreuzberger2023]. Two components of their reference architecture are deliberately absent. A shared feature store is unnecessary because features are rebuilt from the declared configuration by the same code in training and serving, which removes the training-serving skew that a feature store guards against at the scale of a single building. An online serving endpoint is unnecessary because building forecasts are produced in batches or on a schedule; a web service would be a thin wrapper. Reproducibility here means re-executing the agent's frozen decisions (its declarations, notes and accepted issues) with the same package version, not re-running the agent, which is not deterministic.

Table: MLOps principles [@kreuzberger2023] and their implementation in the framework. {#tbl:mlops}

| Principle | Implementation |
|:---|:---|
| P1 CI/CD automation | Tests, including end-to-end model tests, run on every commit; models are delivered through gated promotion |
| P2 Workflow orchestration | Train, retrain and reproduce pipelines, and a command-line interface with exit codes for any scheduler |
| P3 Reproducibility | Configuration, declarations, notes, seeds, library versions, code commit, package fingerprint and data fingerprints in every run record; reproduction checks that every metric matches |
| P4 Versioning | Code commit and package fingerprint; numbered model versions; data fingerprints |
| P5 Collaboration | Report and model card per run; decisions and accepted issues recorded with reasons |
| P6 Continuous training and evaluation | Champion–challenger retraining on rows that neither model has seen |
| P7 Metadata tracking | Run records and a registry event log |
| P8 Continuous monitoring | Live data validation, comparison of training and live inputs, drift and fault monitoring |
| P9 Feedback loops | Monitoring recommends retraining; data checks feed back to the agent |

## Implementation and agent instructions

bemlops is a Python package (BSD 3-Clause licence) built on pandas and scikit-learn; its modules are listed in the Supplementary Material. A typical session declares the columns, runs the data check, prepares the data, fits and saves the run, and registers and promotes the model, in about a dozen lines of code. The candidate models and the hyperparameter searches used here are deliberately conventional, because the claims of the framework concern the process around the model, not the model family. The evaluated version has 45 automated tests, including a test that perturbs every value after the forecast time and checks that no input changes, tests that every planted fault in a synthetic export is detected, regression tests for the defects found during the study, and tests of the full registry, retraining and reproduction loop. Every run record carries the git commit of the case-study code and a fingerprint of the package source.

The agent learns the workflow from an Agent Skill [@zhang2025a], a short instruction file loaded on demand. It sets out the workflow (clarify the task, inspect and load the data, declare columns, resolve every check, prepare, fit, report, register and monitor), seven rules (for example, never split building time series at random, never declare a measured value as known in advance, and never change a declaration to silence a check), a playbook for messy data and a reference for decoding BAS point names. The skill succeeds the prompt template of the preliminary study: instead of prescribing code, it prescribes conduct.
