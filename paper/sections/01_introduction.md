## 1. Introduction

Buildings account for about 30% of global final energy use [IEA 2023], and
data-driven prediction sits behind many of the ways that use is managed in
operation:
- model predictive control needs load and temperature forecasts;
- demand response needs hour-ahead power forecasts;
- fault detection needs expected values to compare against;
- indoor-environment management needs to know where CO2 or temperature is heading.

Machine-learning models for these tasks are well studied [Amasyali and
El-Gohary 2018]. They are rarely deployed at scale, because each building needs
its own model, and building one takes a data scientist days of work on data
that is different every time. Point names such as `RM204_ZN_T` or `AI-3.PV`
must be decoded. Units are mixed. Exports contain text in number columns,
placeholder values, stuck sensors and gaps, in formats that vary by vendor.

Our preliminary study [Khadka and Zhang 2024] asked whether large language
models (LLMs) could remove that bottleneck by writing the modeling code. A
prompt template following the steps of a machine-learning operations (MLOps)
lifecycle let GPT-4 produce runnable code for a simulated small office in 34 of
35 attempts. Three problems limit what that result means:
- code that runs is not the same as a model that is right;
- the generated pipelines split the time series at random and selected features
  on the full dataset, both of which can let test information leak into
  training [Bergmeir and Benítez 2012; Kapoor and Narayanan 2023];
- the study used one simulated building and stopped before deployment.

LLM agents have since become able to write and run analysis code on their own,
so generating a modeling script is no longer the hard part. The open question
is when such a model can be relied on in operation, and what has to surround
the agent's code for that. This paper studies one answer, a division of labour:
- **The agent** reads whatever export it is given, works out what the points
  mean, and makes the judgment calls that no fixed pipeline anticipates.
- **A domain package** applies checks that are the same every time:
  - every declared column is checked against physical plausibility;
  - inputs are built so that they cannot reach past the forecast time;
  - every model is evaluated in time order against the strongest simple
    baseline;
  - promotion to production is gated;
  - deployed models are monitored and retrained;
  - every decision is recorded.

We call these checks guardrails, in the software-engineering sense of checks
that a workflow passes through, not in the sense of LLM output filtering. We
ask five questions, one per experiment:

- **RQ1.** Can one agent-plus-guardrails workflow produce defensible models
  across the targets that matter in buildings (energy, thermal load,
  temperature, CO2, humidity, particulates, occupancy) and across many
  buildings? How often does machine learning beat the strongest simple rule?
- **RQ2.** How much does the evaluation protocol of the 2024 study (a random
  split) change the reported error on real building data?
- **RQ3.** Which data faults do the checks detect on real data, and what does
  automatic handling buy compared with a quick script given the same fix?
- **RQ4.** Over months of operation, does monitoring with gated retraining
  beat a static model, persistence, and naive scheduled retraining?
- **RQ5.** Does the framework change what independent LLM agents deliver?

The contributions are:
1. **A framework** for building prediction that divides work between an agent
   and domain guardrails, covering the MLOps lifecycle from data validation to
   monitoring and retraining. It is mapped to the nine principles of
   Kreuzberger et al. [2023]. Its building-specific parts are:
   - physical-quantity declarations with unit inference as the interface
     between agent and package;
   - fault semantics of building automation systems (BAS): change-of-value
     logging, equipment idling, sensor floors;
   - gates based on the strongest no-ML baseline and ASHRAE Guideline 14.
2. **An open-source implementation**, `bemlops`, with an Agent Skill that
   teaches LLM agents the workflow. It handles any numeric or yes/no target.
3. **An evaluation on three public real-building datasets**: 72 tasks in 11
   rooms and their building systems, plus a 20-building portfolio, answering
   RQ1–RQ4.
4. **A formative pilot with eight independent agent runs**, answering RQ5. It
   found no accuracy, leakage or fault-finding advantage from the framework for
   capable agents told to be rigorous, at a higher cost in tokens and time. The
   framework's measured value therefore lies elsewhere: in default rigour, in
   comparable and maintainable records, and in the lifecycle. The pilot agents
   also exposed defects that were then fixed.

All code, configurations, run records and pilot deliverables are public
(https://github.com/TensorBuildLab/MLOps-building-energy-and-environment-prediction).
