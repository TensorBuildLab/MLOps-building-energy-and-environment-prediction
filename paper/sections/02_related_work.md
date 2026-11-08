# Related work {#sec:related}

## Data-driven prediction in building operation

Machine-learning models of building energy consumption are well established [@amasyali2018] and are a standard ingredient of data-driven control [@maddalena2020]. The indoor environment and occupancy are predicted with the same tools, for example occupancy from light, temperature, humidity and CO~2~ [@candanedo2016] and indoor CO~2~ up to 15 min ahead from a year of office data [@kallio2021]. Large benchmarks exist for load forecasting [@emami2023; @miller2020]. What remains expensive is the work around each model: understanding the data of a new building, cleaning them, and evaluating and maintaining the model. A review of preprocessing for building operational data [@fan2021] shows how much of that work concerns faulty sensors and data problems rather than modeling, and fault detection in building systems is a research field of its own [@kim2018].

## Automated and LLM-generated pipelines for buildings

Automated machine learning (AutoML) has been benchmarked for building load prediction [@zhang2023], and an end-to-end automated forecasting framework covering preprocessing, feature engineering and model selection has been proposed [@zhang2024a]; the latter also retrains on a sliding window so that the model adapts over time. Since 2023, LLMs have been used to generate data-mining code for building energy management [@zhang2024b], to automate load-prediction pipelines end to end [@zhang2025b], to analyze unstructured building data with multiple agents [@xiao2024], and to coordinate specialist agents with many tools for building operation [@jiang2026]. The authors' preliminary study used prompt templates structured by MLOps steps to have an LLM write modeling code [@khadka2024]. These studies mostly evaluate whether the generated code runs, how accurate the resulting model is on a held-out split, or whether tools are selected correctly. Two questions remain largely open: how to make an agent's result on real, messy data checkable, and how to monitor, gate and roll back the resulting models in operation.

## Agents for machine-learning engineering

Outside the building domain, agents that interleave reasoning with tool use [@yao2023] are evaluated on machine-learning engineering tasks. MLAgentBench [@huang2024] and MLE-bench [@chan2025] score agents on curated tasks against held-out test sets that the benchmark controls, and DS-Agent [@guo2024] reuses past solutions to plan data-science pipelines. In these settings the benchmark, not the agent, guarantees a sound evaluation. In a building, nobody holds back a clean test set: the agent's own split, cleaning and baseline determine whether the reported accuracy means anything.

## MLOps tools and evaluation pitfalls

Machine-learning systems accumulate hidden technical debt [@sculley2015]. Production readiness can be scored with test rubrics [@breck2017], data should be validated as rigorously as code [@breck2019], and models should be documented with model cards [@mitchell2019]. Kreuzberger et al. [@kreuzberger2023] synthesized MLOps into nine principles, which are used here as a checklist. Mature general-purpose tools cover parts of this lifecycle (@tbl:tools): data validation with Deequ [@schelter2018], Great Expectations [@gong2026] and pandera [@bantilan2020]; experiment tracking, versioning and model registries with MLflow [@zaharia2018] and DVC [@kuprieiev2026]; drift monitoring with Evidently [@evidently2026]; and time-series learning with backtesting and naive forecasters with sktime [@loning2019], Darts [@herzen2022] and AutoGluon–TimeSeries [@shchur2023]. Darts, for example, separates past from future covariates, which prevents one form of look-ahead.

On evaluation, Bergmeir and Benítez [@bergmeir2012] recommended blocked cross-validation for time series, although in their experiments the theoretical flaws of standard cross-validation had little practical effect, and standard k-fold cross-validation is valid for purely autoregressive models with uncorrelated errors [@bergmeir2018]. Data leakage, including leakage from random splits and from preprocessing on the full dataset, is a widespread cause of irreproducible machine-learning results across sciences [@kapoor2023]. Whether random splits mislead on building operational data, where neighboring readings and inputs measured at the same moment are strongly related, is therefore an empirical question, addressed in @sec:res-protocol.

Table: Capabilities of existing tools and of this work. "Partly": possible with rules or configuration that the user writes; "n.r.": not reported. {#tbl:tools}

| Capability | Data validation^a^ | Tracking and registries^b^ | Monitoring^c^ | Time-series ML^d^ | Building AutoML or LLM pipelines^e^ | This work |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Physical-quantity declarations with unit inference | no | no | no | no | n.r. | yes |
| Sensor-fault semantics of building automation systems | partly | no | no | no | n.r. | yes |
| Generic schema and range checks | yes | no | partly | no | partly | yes |
| Inputs that cannot reach past the forecast time, audited | no | no | no | partly | n.r. | yes |
| Time-ordered evaluation and backtesting | no | no | no | yes | n.r. | yes |
| Strongest no-ML baseline as reference and promotion gate | no | no | no | partly | no | yes |
| Model registry with gated promotion and rollback | no | yes | no | no | no | yes |
| Retraining over time | no | no | partly | partly | yes | yes |
| Drift and live-data monitoring | partly | no | yes | no | no | yes |
| Designed for an LLM agent to drive | no | no | no | no | partly | yes |
Note: ^a^ Deequ, Great Expectations, pandera. ^b^ MLflow, DVC. ^c^ Evidently. ^d^ sktime, Darts, AutoGluon–TimeSeries. ^e^ Refs. [@zhang2023; @zhang2024a; @zhang2025b].

None of the building-specific capabilities in @tbl:tools is technically difficult on its own. The contribution of this work is to combine them behind one small interface that an agent can use, and to measure their effect on real buildings.

Brick [@balaji2016] standardizes building metadata, and with it the meaning of points. Where a Brick model exists, it can supply the declarations that the framework requires, and each physical quantity in the framework names its nearest Brick class for this reason. Most real exports, including the three datasets used here, carry no such model, so the agent infers the declarations from names, documentation and values.
