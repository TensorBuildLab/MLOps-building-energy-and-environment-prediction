# MLOps for building energy and environment prediction

**`bemlops`** is a Python package for building trustworthy prediction models
for buildings from real, messy BAS/BMS data: energy, electric power, cooling
and heating load, zone temperature, CO2, humidity, occupancy, or any other
point you trend. Numeric targets are forecast or estimated (regression);
yes/no targets such as "occupied" or "equipment on" are handled as
classification. It covers the full MLOps lifecycle, from data checks to
gated deployment, monitoring and retraining ([checklist](docs/mlops.md)).

It is built for a world where an AI agent does much of the data-science work:

> **The AI agent handles the mess. The package guarantees the parts that must never go wrong.**

Real building data is messy in endless ways: cryptic point names, mixed
units, text in number columns, stuck sensors, odd export formats. No fixed
set of rules can anticipate all of it, but an LLM agent can reason through
each case and write the code it needs. Some mistakes, though, must be
impossible no matter who writes the code: wrong units, a time series split
at random, future values leaking into inputs, a model reported without a
baseline. `bemlops` makes those impossible, and records every decision.

| The agent (or engineer) | bemlops |
|---|---|
| Loads any export format, in its own code | Accepts any pandas table with a time index |
| Works out what `RM204_ZN_T` or `AI-3.PV` means | Requires every used column to be declared, and checks each declaration against physics |
| Decides what to do about faults and odd periods | Detects stuck sensors, spikes, `-999` placeholders, wrong units, duplicates, gaps |
| Designs extra features | Builds lags so that nothing comes from the future |
| Explains the results | Splits by time, compares with baselines, applies ASHRAE Guideline 14, writes a full run record |

## A quick look

```python
import bemlops

p = bemlops.Project(
    df, target="AHU1_CLG_KW", horizon="1h",
    columns={
        "AHU1_CLG_KW": "electric_power [kW]",
        "OAT":         "outdoor_air_temperature [degF]",
        "RM204_ZN_T":  "zone_air_temperature [degC]",   # wrong: the BAS trends it in degF
        "RM204_CO2":   "co2 [ppm]",
        "RM204_OCC":   "occupancy_count",
    })

print(p.check_data())
# [ERROR] unit_mismatch:RM204_ZN_T: Declared in degC, but only 0% of values are plausible for
#         zone_air_temperature in degC, while 100% are plausible in degF (median value 75.4).
# [WARNING] stuck:RM204_CO2: Sensor repeats exactly 619 for 4 d 23 h 55 min ...
# [WARNING] sentinel:AHU1_CLG_KW: 20 readings are placeholder values (-999) ...

p.fit()        # refuses: the unit error needs a decision first
p.update(columns={"RM204_ZN_T": "zone_air_temperature [degF]"}, note="degF per BAS point config")
p.prepare(freq="15min")
print(p.fit())
# Chosen: random_forest. Test: RMSE 0.118 kW, CV(RMSE) 20.0%, NMBE -8.8%.
# Skill vs persistence: 0.58
# ASHRAE Guideline 14 (hourly): CV(RMSE) 17.9% (limit 30%), NMBE -8.9% (limit +/-10%): passes.
folder = p.save_run("runs/")   # report, model card, full audit record, model, predictions, plots

reg = bemlops.Registry("models/")
v = reg.register(folder)["version"]   # promotion gates evaluated and stored
reg.promote(p.name, v, reason="First production model.")   # refused if a gate fails

model = reg.load(p.name)
model.predict(latest_data)            # checks the live data first, then forecasts
model.check_drift(last_two_weeks)     # accuracy, input shift, new sensor faults
bemlops.retrain(history, reg, p.name) # challenger vs champion on unseen data; promotes only if better
```

The same steps run from the command line for scheduled jobs:
`bemlops train | predict | monitor | retrain | reproduce`.

Run the full example on a synthetic messy BAS export: `python examples/quickstart.py`.

## What the checks catch

- **Units**: a column declared in degC that holds 68-75 (and which unit it really is), RH stored as 0-1 fractions, cumulative meter readings declared as interval energy
- **Physically impossible values**: negative power, CO2 below 250 ppm, zone temperatures of 60 degC
- **Sensor faults**: stuck/flatlined sensors (but not setpoints, which are allowed to be constant), single-sample spikes, placeholder values like `-999`, `9999`, `32767`
- **Export problems**: text in number columns (`OFFLINE`, `N/A`, `72.5 °F`, `1,234`), status words (`On`/`Off`), duplicate timestamps, out-of-order rows, irregular change-of-value logging, gaps
- **Leakage**: any input that would use information not available at prediction time; inputs that are near-copies of the target
- **Live data** (every prediction): the same checks, plus a comparison with the training data that catches what range checks cannot, such as an outdoor-temperature feed that switched from degF to degC

Errors block fitting (and live predictions) until they are fixed or accepted
with a written reason. Warnings are handled by a standard, logged preparation step.

## MLOps, end to end

| Stage | What bemlops does |
|---|---|
| Data validation | Blocking checks; same checks on live data |
| Preparation and features | Logged, deterministic, identical in training and serving |
| Training and tuning | Time-ordered splits and cross-validation; baselines always included |
| Evaluation | Skill vs baseline, Guideline 14, physical-unit errors, Brier/F1/AUC for yes/no |
| Versioning and metadata | Data fingerprints, code commit, full config and results in every run |
| Registry and deployment | Versions, stages, promotion gates, rollback |
| Monitoring | Accuracy drift, input shift, new sensor faults |
| Continuous training | Champion vs challenger on unseen data |
| Reproducibility | `reproduce()` re-runs a record and checks every metric matches |

See [docs/mlops.md](docs/mlops.md) for the principle-by-principle checklist
against a published MLOps definition.

## Use it with an AI agent

The [`skills/building-prediction`](skills/building-prediction/SKILL.md) folder
is an [Agent Skill](https://agentskills.io): instructions that teach an AI
agent the workflow, the hard rules, and a playbook for messy data, plus a
[guide to BAS point names](skills/building-prediction/reference/bas-point-names.md).
Copy the folder into your agent's skills directory (for Claude Code:
`~/.claude/skills/` or `.claude/skills/` in your project). Then ask in plain
language, for example: *"Forecast tomorrow's hourly cooling load for this building from these trend logs."*

## Install

Not on PyPI yet. From a clone of this repository:

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+ with numpy, pandas, scikit-learn, scipy and joblib.
matplotlib is optional (plots in run reports).

## Repository layout

```
src/bemlops/        the package
skills/             the Agent Skill (SKILL.md + point-name reference)
examples/           runnable examples
tests/              tests, including leakage and fault-detection tests
docs/design.md      why the package works the way it does
benchmarks/         protocol for the agent-vs-AutoML-vs-agent+bemlops study
case_studies/       synthetic demo, v1 reproduction, real buildings
paper/              the research paper (v1 and the v2 plan)
```

## Research

This repository continues the preliminary study
[*Scaling Data-Driven Building Energy Modelling using Large Language Models*](https://arxiv.org/abs/2407.03469)
(Khadka and Zhang, 2024), which used prompt templates following MLOps steps to
have an LLM write modeling code. The next study tests the claim behind this
package on real buildings: **generalization from the LLM, reliability from
domain guardrails**. See [`benchmarks/`](benchmarks/README.md) and [`paper/`](paper/README.md).

## Status and roadmap

Early development (`0.1.0.dev0`). Working today: data checks, logged
preparation, leakage-safe features, time-ordered splits, baselines, tuned
ridge / random forest / gradient boosting, Guideline 14 metrics, run records,
deployment with drift checks, the Agent Skill.

Planned: real-building case studies; Brick Schema / Project Haystack metadata
import; holiday calendars; probabilistic (interval) forecasts; more model
families; an MCP server for chat-based use, once there is demand.

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

BSD 3-Clause. See [`LICENSE`](LICENSE).
