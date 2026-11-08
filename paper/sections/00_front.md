# Where domain guardrails matter for LLM-agent-built prediction models in buildings: an open MLOps framework evaluated on real data

*Draft manuscript, version 2 of the work first reported in arXiv:2407.03469. Author list and affiliations to be confirmed by the authors.*

**Keywords:** building energy; indoor environmental quality; occupancy; machine learning operations (MLOps); large language model agents; data quality; time-series evaluation

## Highlights

- An LLM agent reads messy building data; a domain package applies fixed checks.
- On 92 real-building tasks, ML beat the strongest simple rule in about half.
- A random split understated prediction error by a median 27% on the same rows.
- Monitoring beat a static model, but scheduled retraining did better still.
- In a small pilot, agents told to be rigorous did as well without the framework.

## Abstract

Large language model (LLM) agents can now write code for building
prediction models; their reliability depends on what surrounds that code. We
present bemlops, an open-source framework in which an agent supplies
building-specific judgment (reading exports, decoding point names, declaring
quantities and units) and a domain package applies the same checks every
time: physical plausibility, causal cleaning, inputs that cannot reach past
the forecast time, time-ordered evaluation against the strongest no-ML
baseline, promotion gates, monitoring and retraining. We evaluated it on 92
energy, indoor-environment and occupancy tasks in three public real-building
datasets, and in a pilot with eight separate agent runs. Ordinary models
beat the strongest simple rule significantly in 52% of tasks, and 45% failed
the promotion gates. A random split, the protocol of our 2024 study,
understated error by a median of 27% on the same rows. With faults planted in
one CO2 task, the framework reproduced clean-data accuracy, whereas a quick
script was 9% worse in mean absolute error, though not in RMSE. Over eight
months, monitoring with gated retraining cut error by 10–33% against a static
model, but monthly retraining did better and persistence matched it for
district heating. In the pilot, agents told to be rigorous built leak-free
models of similar accuracy with or without the framework, at higher cost with
it, and found a dead meter our own agent had missed. The framework's value
lies in making rigorous evaluation the default, in comparable records and in
the lifecycle, not in out-modeling a capable agent.
