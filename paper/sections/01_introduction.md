## 1. Introduction

Buildings account for roughly 30% of global final energy use [IEA]. Data-driven
prediction sits behind many of the ways that use is managed in operation:
model predictive control needs load and temperature forecasts, demand
response needs hour-ahead power forecasts, fault detection needs expected
values to compare against, and indoor-environment management needs to know
where CO2 or temperature is heading. Machine-learning models for these tasks
are well studied [Amasyali and El-Gohary 2018]. They are rarely deployed at
scale, because each building needs its own model, and building one takes a
data scientist days of work on data that is different every time: point names
such as `RM204_ZN_T` or `AI-3.PV`, mixed units, text in number columns,
placeholder values, stuck sensors, gaps, and export formats that vary by vendor.

Our preliminary study [Khadka and Zhang 2024] asked whether large language
models (LLMs) could remove that bottleneck by writing the modeling code. A
prompt template following the steps of a machine-learning operations (MLOps)
lifecycle let GPT-4 produce runnable code for a simulated small office in 34
of 35 attempts. Three problems limit what that result means. First, code that
runs is not the same as a model that is right. Second, the generated
pipelines split the time series at random and selected features on the full
dataset, both of which let test information leak into training and inflate
accuracy [Bergmeir and Benítez 2012; Kapoor and Narayanan 2023]. Third, the
study used one simulated building and stopped before deployment, so it said
nothing about messy real data or about operating a model over time.

LLM agents have since become able to write and run analysis code on their own,
so generating a modeling script is no longer the hard part. The hard part is
trust: can a model that an agent built from a real building's trend logs be
relied on in operation, by an engineer who did not watch it being built? Our
answer is a division of labour. The agent provides **generalization**: it
reads whatever export it is given, works out what the points mean, and makes
the judgment calls that no fixed pipeline can anticipate. A domain package
provides **reliability**: it checks every declaration the agent makes against
physics, makes leakage structurally impossible, evaluates every model against
a no-skill baseline with standard metrics, gates promotion to production,
monitors the deployed model, and records every decision.

This paper makes four contributions:

1. **A framework** that divides building-prediction work between an LLM agent
   (judgment) and domain guardrails (guarantees), covering the whole MLOps
   lifecycle from data validation to monitoring and retraining, and checked
   principle by principle against a published MLOps definition
   [Kreuzberger et al. 2023].
2. **An open-source implementation**, `bemlops`, with an Agent Skill that
   teaches LLM agents the workflow, for any numeric or yes/no target in a
   building: energy, power, thermal load, temperature, CO2, humidity,
   occupancy and equipment state.
3. **Case studies on real buildings** across many prediction targets, in which
   an LLM agent drove the workflow and every decision it made is part of the
   published record.
4. **Measurements of what the guardrails change**: how much a 2024-style
   evaluation overstates accuracy on real data, how many injected faults the
   checks detect, how unguarded training degrades on faulty data, and how the
   monitoring and retraining loop behaves over months of operation.

All code, configurations, run records and results are public
(https://github.com/TensorBuildLab/MLOps-building-energy-and-environment-prediction).
