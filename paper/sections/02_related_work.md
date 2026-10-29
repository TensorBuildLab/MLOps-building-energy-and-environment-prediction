## 2. Related work

**Data-driven prediction in buildings.** Machine-learning models for building
energy use are well established [Amasyali and El-Gohary 2018], and are a
standard ingredient of data-driven control [Maddalena et al. 2020]. Indoor
environment and occupancy are predicted with the same tools: occupancy from
light, temperature, humidity and CO2 [Candanedo and Feldheim 2016], and
indoor CO2 a few hours ahead from a year of office data [Kallio et al. 2021].
Large benchmarks now exist for load forecasting [Emami et al. 2023; Miller et
al. 2020]. What remains expensive is the work around each model: understanding
a new building's data, cleaning it, and evaluating and maintaining the model.
Reviews of building operational data preprocessing [Fan et al. 2021] and of
fault detection [Kim and Katipamula 2018] show how much of that work is about
faulty sensors and data problems rather than modeling.

**Automating the modeling.** Automated machine learning (AutoML) frameworks
have been benchmarked for building load prediction [Zhang et al. 2023], and
end-to-end automated forecasting frameworks have been proposed [Zhang et al.
2024a]. AutoML searches over models and settings, but it assumes a clean,
correctly labelled table; it does not know that a column is in the wrong unit
or that a sensor froze for a week.

**LLMs and agents for building data.** Since 2023, LLMs have been used to
generate data-mining and modeling code for building energy management
[Zhang et al. 2024b], to automate load-prediction pipelines end to end
[Zhang et al. 2025], to analyse unstructured building data with multiple
agents [Xiao and Xu 2024], and to coordinate specialist agents with dozens of
tools for building operations [Jiang et al. 2026]. Our preliminary study used
MLOps-structured prompt templates to have an LLM write modeling code
[Khadka and Zhang 2024]. Agents that interleave reasoning with tool use
[Yao et al. 2023] are the common pattern. Evaluations so far focus on whether
generated code runs, whether tools are selected correctly, or on simulated
buildings. Two questions are largely open: how to make an agent's results
on real, messy data trustworthy, and how to operate the resulting models over
time.

**MLOps and evaluation pitfalls.** Machine-learning systems accumulate hidden
technical debt [Sculley et al. 2015]. Production readiness can be scored with
test rubrics [Breck et al. 2017], data should be validated as rigorously as
code [Breck et al. 2019], and models should be documented with model cards
[Mitchell et al. 2019]. Kreuzberger et al. [2023] synthesise MLOps into nine
principles and nine components, which we use as a checklist. On evaluation,
cross-validation for time series must respect temporal dependence [Bergmeir
and Benítez 2012], and data leakage, including from random splits and
preprocessing on the full dataset, is a leading cause of irreproducible
machine-learning results across sciences [Kapoor and Narayanan 2023].

**Metadata.** Brick [Balaji et al. 2016] standardises building metadata, and
with it the meaning of points. Where Brick models exist, they can supply the
declarations our framework requires. Each quantity in our framework names its
nearest Brick class for this reason. Most real exports, including the three
datasets used here, carry no such model, so the agent infers declarations from
names, documentation and values.

**Position of this work.** We combine an LLM agent's flexibility with
building-specific guardrails, cover the full MLOps lifecycle, and evaluate on
real buildings across many prediction targets, with every agent decision
recorded.
