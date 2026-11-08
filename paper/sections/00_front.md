---
title: Domain guardrails for agent-built building energy and indoor environment prediction: an MLOps framework evaluated on real buildings
author: Liang Zhang | 1 | corresponding
affiliation: 1 | Department of Civil and Architectural Engineering and Mechanics, The University of Arizona, Tucson, AZ 85721, USA
email: liangzhang1@arizona.edu
keywords: building energy prediction; machine learning operations; large language model agents; indoor environmental quality; sensor data quality; time-series validation
bibliography: ../refs.ris
endnote-style: Numbered
---

# Highlights {-}

- Language-model agents read messy building data; a domain package applies checks
- Across 92 real-building tasks, models beat the best simple rule in about half
- Random splits understated prediction error by a median of 27% on the same data
- Scheduled retraining outperformed drift-triggered retraining over eight months
- Agents told to be rigorous built similar models with or without the framework

# Abstract {-}

Large language model (LLM) agents can now write code for building energy and indoor environment prediction models, but their reliability in operation depends on what surrounds that code. This paper presents bemlops, an open-source framework in which an agent supplies building-specific judgment (reading exports, decoding point names, declaring quantities and units) while a domain package applies the same checks to every model: physical plausibility, causal cleaning, inputs that cannot reach past the forecast time, time-ordered evaluation against the strongest no-machine-learning baseline, promotion gates, monitoring and retraining. The framework was evaluated on 92 energy, indoor-environment and occupancy prediction tasks in three public datasets of real buildings, and in a pilot with eight independent agent runs. Ordinary models beat the strongest simple rule significantly in 52% of the tasks, and 45% failed the promotion gates. A random split, the protocol of the authors' earlier study, understated the prediction error by a median of 27%. With faults planted in one CO~2~ task, the framework reproduced the clean-data accuracy, whereas a quick script was 9% worse in mean absolute error but not in root mean square error. Over eight months, gated retraining reduced the error of a static model by 10–33%, but monthly retraining performed better, and for district heating the gated model only matched persistence. Agents told to be rigorous built models of similar accuracy with or without the framework. The value of the guardrails lies in making rigorous evaluation the default, in comparable records and in supporting the model lifecycle.

# Nomenclature {-}

| | | | |
|---|---|---|---|
| *Symbols* | | | |
| $e_t$ | prediction error at time $t$ | $h$ | forecast horizon (time steps) |
| $n$ | number of test observations | $q_{0.9}$ | 90th percentile of absolute validation errors |
| $S$ | skill against the reference baseline (–) | $y_t$, $\hat{y}_t$ | measured and predicted value |
| $\bar{y}$ | mean of the measured values | $d_t$ | loss differential (model minus baseline) |
| *Abbreviations* | | | |
| AHU | air-handling unit | BAS | building automation system |
| BDG2 | Building Data Genome Project 2 | CV(RMSE) | coefficient of variation of the RMSE |
| DM | Diebold–Mariano test | IQR | interquartile range |
| LLM | large language model | MAE | mean absolute error |
| MLOps | machine learning operations | NMBE | normalized mean bias error |
| PM2.5 | particulate matter below 2.5 µm | RMSE | root mean square error |
