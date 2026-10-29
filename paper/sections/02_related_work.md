## 2. Related work

### 2.1 Data-driven prediction in buildings

Machine-learning models of building energy use are well established
[Amasyali and El-Gohary 2018] and are a standard ingredient of data-driven
control [Maddalena et al. 2020]. Indoor environment and occupancy are
predicted with the same tools: occupancy from light, temperature, humidity
and CO2 [Candanedo and Feldheim 2016], and indoor CO2 a few hours ahead from
a year of office data [Kallio et al. 2021]. Large benchmarks exist for load
forecasting [Emami et al. 2023; Miller et al. 2020]. What remains expensive is
the work around each model: understanding a new building's data, cleaning it,
and evaluating and maintaining the model. Reviews of preprocessing for
building operational data [Fan et al. 2021] and of fault detection [Kim and
Katipamula 2018] show how much of that work concerns faulty sensors and data
problems rather than modeling.

### 2.2 Automated and LLM-generated pipelines for buildings

Automated machine learning (AutoML) has been benchmarked for building load
prediction [Zhang et al. 2023], and an end-to-end automated forecasting
framework covering preprocessing, feature engineering and model selection
has been proposed [Zhang et al. 2024a]. Since 2023, LLMs have been used to
generate data-mining code for building energy management [Zhang et al. 2024b],
to automate load-prediction pipelines end to end [Zhang et al. 2025b], to
analyse unstructured building data with multiple agents [Xiao and Xu 2024],
and to coordinate specialist agents with many tools for building operations
[Jiang et al. 2026]. Our preliminary study used MLOps-structured prompt
templates to have an LLM write modeling code [Khadka and Zhang 2024]. These
studies mostly evaluate whether generated code runs, how accurate the
resulting model is on a held-out split, or whether tools are selected
correctly. They leave two questions largely open: how to make an agent's
result on real, messy data checkable, and how to operate the resulting
models over time.

### 2.3 Agents for machine-learning engineering

Outside buildings, agents that interleave reasoning with tool use [Yao et al.
2023] are evaluated on machine-learning engineering tasks: MLAgentBench
[Huang et al. 2024] and MLE-bench [Chan et al. 2025] score agents on curated
tasks against held-out test sets that the benchmark controls, and DS-Agent
[Guo et al. 2024] reuses past solutions to plan data-science pipelines. In
these settings the benchmark, not the agent, guarantees a sound evaluation.
In a building, nobody holds back a clean test set: the agent's own split,
cleaning and baseline decide whether the reported accuracy means anything.

### 2.4 MLOps tools and evaluation pitfalls

Machine-learning systems accumulate hidden technical debt [Sculley et al.
2015]. Production readiness can be scored with test rubrics [Breck et al.
2017], and data should be validated as rigorously as code [Breck et al.
2019]. Kreuzberger et al. [2023] synthesise MLOps into nine principles and
nine components, which we use as a checklist. Mature general-purpose tools
cover parts of this lifecycle (Table 1):
- data validation: Deequ [Schelter et al. 2018], Great Expectations [Gong and
  Campbell 2026] and pandera [Bantilan 2020];
- experiment tracking, versioning and model registries: MLflow [Zaharia et al.
  2018] and DVC [Kuprieiev et al. 2026];
- drift monitoring: Evidently [Evidently AI 2026];
- time-series learning with backtesting and naive forecasters: sktime [Löning
  et al. 2019], Darts [Herzen et al. 2022] and AutoGluon–TimeSeries [Shchur et
  al. 2023].

Darts, for example, separates past from future covariates, which prevents one
form of look-ahead. Model cards document a model's intended use and
evaluation [Mitchell et al. 2019]. On evaluation, cross-validation for time
series must respect temporal dependence [Bergmeir and Benítez 2012]. Data
leakage, including leakage from random splits and from preprocessing on the
full dataset, is a leading cause of irreproducible machine-learning results
across sciences [Kapoor and Narayanan 2023].

**Table 1.** What existing tools provide and what this work adds. "Partly":
possible with rules or configuration the user writes; "n.r.": not reported.

| Capability | Data validation (Deequ, Great Expectations, pandera) | Tracking and registries (MLflow, DVC) | Monitoring (Evidently) | Time-series ML (sktime, Darts, AutoGluon–TS) | Building AutoML / LLM pipelines [Zhang et al. 2023, 2024a, 2025b] | This work |
|---|---|---|---|---|---|---|
| Physical-quantity declarations with unit inference | no | no | no | no | n.r. | yes |
| BAS sensor-fault semantics (stuck vs change-of-value logging, idle equipment, sensor floors) | partly | no | no | no | n.r. | yes |
| Generic schema and range checks | yes | no | partly | no | partly | yes |
| Inputs that cannot reach past the forecast time, with an audit | no | no | no | partly | n.r. | yes |
| Time-ordered evaluation and backtesting | no | no | no | yes | n.r. | yes |
| Strongest no-ML baseline as the reference, and as a promotion gate | no | no | no | partly | no | yes |
| Model registry with gated promotion and rollback | no | yes | no | no | no | yes |
| Drift and live-data monitoring | partly | no | yes | no | no | yes |
| Written for an LLM agent to drive (declarations, skill file) | no | no | no | no | partly | yes |

None of the building-specific rows is technically difficult. The point of
this work is that they are combined behind one small interface that an agent
can use, and measured on real buildings.

### 2.5 Metadata

Brick [Balaji et al. 2016] standardises building metadata, and with it the
meaning of points. Where a Brick model exists, it can supply the declarations
our framework requires, and each quantity in the framework names its nearest
Brick class for this reason. Most real exports, including the three datasets
used here, carry no such model, so the agent infers declarations from names,
documentation and values.

### 2.6 What we mean by a guardrail

In the LLM-safety literature a guardrail filters a model's inputs or outputs.
We use the word in its software-engineering sense: a check that every run of
a workflow passes through, with a defined outcome (block, warn, mask, refuse
promotion) and a record of the result. The guardrails here are written in
ordinary code. They constrain what reaches a model and what reaches
production, not what the agent may write. An agent can bypass them: two pilot
agents replaced the package's model with their own (Section 6.5). The
guardrails then cover only the part of the work that went through the
package.
