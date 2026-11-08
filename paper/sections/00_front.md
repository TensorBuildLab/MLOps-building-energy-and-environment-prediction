---
title: Domain guardrails for data-driven building energy prediction: an agent-ready MLOps framework evaluated on real buildings
author: Liang Zhang | a | corresponding
affiliation: a | Department of Civil and Architectural Engineering and Mechanics, The University of Arizona, Tucson, AZ 85721, USA
email: liangzhang1@arizona.edu
keywords: building energy prediction; M&V baselines; machine learning operations; model retraining; time-series validation; large language model agents
bibliography: ../refs.ris
endnote-style: Numbered
---

# Highlights {-}

- Agents declare building data; one package applies the same checks to every model
- Day-ahead models beat strong rules, including TOWT, in 66% of 200 real buildings
- As M&V baselines, models matched but did not beat TOWT on annual savings error
- Shuffled validation passed 32 M&V baselines that failed in the reporting year
- Monthly retraining beat drift-triggered retraining at the default tolerance

# Abstract {-}

Data-driven building energy models support control, demand response and measurement and verification (M&V), but their reliability depends on how they are evaluated and maintained. This paper presents bemlops, an open-source machine learning operations (MLOps) framework in which a large language model agent or analyst declares each data column as a physical quantity and a package applies the same checks to every model: plausibility, causal cleaning, leakage-safe inputs, time-ordered evaluation against the strongest baseline without machine learning, including time-of-week-and-temperature (TOWT) regression, promotion gates, monitoring and retraining. In a pre-specified evaluation on 200 public buildings and 72 room and system tasks, routinely configured day-ahead models beat their reference significantly in 66% of the buildings. As M&V baselines, they matched but did not beat TOWT (median annual error 5.3% versus 5.2%). Shuffled cross-validation understated the error of forward use by a median of 41% and accepted 32 M&V baselines that missed the ASHRAE Guideline 14 limits in the reporting year, against 13 for a time-ordered split. Over a year in 50 buildings, monthly retraining outperformed drift-triggered retraining at the default tolerance, and 86% of promoted models kept a skill (relative error reduction against the strongest baseline) of at least 0.05. The checks found site-wide meter faults in cleaned benchmark data but missed months of zero readings.

# Nomenclature {-}

| | | | |
|---|---|---|---|
| *Symbols* | | | |
| $d_t$ | loss differential (model minus baseline) | $e_t$ | prediction error at time $t$ |
| $h$ | forecast horizon (time steps) | $n$ | number of test observations |
| $q_{0.9}$ | 90th percentile of absolute validation errors | $S$ | skill against the reference baseline (–) |
| $y_t$, $\hat{y}_t$ | measured and predicted value | $\bar{y}$ | mean of the measured values |
| $\bar{d}$ | mean of $d_t$ over the test window | $R^2$ | coefficient of determination (–) |
| *Abbreviations* | | | |
| AHU | air-handling unit | BAS | building automation system |
| BDG2 | Building Data Genome Project 2 | CI | confidence interval |
| CI/CD | continuous integration and continuous delivery | CV | cross-validation |
| CV(RMSE) | coefficient of variation of the RMSE | DM | Diebold–Mariano test |
| IQR | interquartile range | LLM | large language model |
| M&V | measurement and verification | MAE | mean absolute error |
| ML | machine learning | MLOps | machine learning operations |
| NMBE | normalized mean bias error | PM2.5 | particulate matter below 2.5 µm |
| RMSE | root mean square error | RQ | research question |
| TOWT | time-of-week-and-temperature regression |  |  |
