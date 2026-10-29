# Paper

## v1 (2024, preliminary)

Khadka, S. and Zhang, L. *Scaling Data-Driven Building Energy Modelling
using Large Language Models.* arXiv:2407.03469.
<https://arxiv.org/abs/2407.03469>

A prompt template following MLOps steps (data preparation, feature
selection, splitting, model selection, tuning, evaluation, plots) had
ChatGPT-4 write modeling code for a simulated DOE small office in Tucson.
Bi-sequential prompting produced runnable code in 34 of 35 attempts.

What v2 must fix:

- Random train/validation/test split on time-series data (leakage)
- Feature selection on the full dataset before splitting (leakage)
- "Code accuracy" measured as "runs without error", not model correctness
- One simulated building, one LLM version, one beginner as the human baseline
- Results in ChatGPT share links that cannot be re-run

## v2 (planned)

**Thesis**: generalization from the LLM, reliability from domain guardrails.
LLM agents can handle the endless variety of real building data, but only
domain guardrails make the results trustworthy enough for industry use.

**Contributions** (draft):

1. A framework that splits building-prediction work between an LLM agent
   (judgment) and a domain package (guarantees), covering the full lifecycle:
   data checks, preparation, modeling, evaluation, deployment, drift monitoring
2. `bemlops`, an open-source implementation, with an Agent Skill
3. A benchmark on real buildings and many prediction targets (energy,
   load, temperature, CO2, humidity, occupancy), with a hidden test period
   and fault injection
4. Evidence comparing an agent alone, AutoML alone, and the agent with the
   framework, across several LLMs

**Outline** (draft):

1. Introduction: scaling data-driven building models; what changed since 2024
2. Related work: data-driven building prediction; AutoML; LLM agents for
   buildings (mostly simulation-based so far); data quality in BAS
3. Framework: the split, the guardrails, the lifecycle
4. Implementation: bemlops and the skill
5. Benchmark design: buildings, tasks, arms, hidden test, fault injection
6. Results
7. Discussion: where agents fail, where guardrails help, cost, limitations
8. Conclusion

Target venue: to be decided.
