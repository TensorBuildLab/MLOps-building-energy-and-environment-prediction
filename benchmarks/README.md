# Benchmark study (plan)

The question: **on messy real-building data, does an AI agent working with
domain guardrails beat an agent alone, and beat AutoML alone?**

This is the core experiment for the next paper. The protocol is drafted
here so that it is fixed before results come in.

## Arms

| Arm | Who does the work | What it tests |
|---|---|---|
| A. Agent alone | An LLM agent writes all the code from the raw export (the 2024 setting, with current agents) | Generalization without guardrails |
| B. AutoML alone | A general-purpose AutoML tool on the mechanically loaded export, no LLM, no domain checks | Reliability without judgment |
| C. Agent + bemlops | The same agent, with the `building-prediction` skill and the package | The combination |
| D. Human expert (optional) | A building data scientist, time-boxed | A realistic reference, replacing the single beginner in the 2024 study |

All agent arms use the same agent harness, the same task prompt, and the same
time and token budget.

## Tasks

Buildings × targets × horizons. Targets, each where the data allows:

- Whole-building electricity: 1 h and 24 h ahead
- AHU / chiller electric power, cooling load: 1 h ahead
- Zone temperature: 15 min and 1 h ahead
- Zone CO2: 30 min ahead
- Zone relative humidity, occupancy count: 1 h ahead
- Virtual sensors (horizon 0): e.g. cooling load from AHU trends (the 2024 task)

## Hidden test period

The evaluators keep the **last weeks of every dataset hidden**. Agents and
AutoML get only the data before it. Final scoring runs a separate script on
the hidden period. This removes any chance of a method grading itself on a
leaky test set.

## Fault injection

Real data has unknown faults, so detection cannot be scored directly. On top
of the real data, the evaluators inject known faults at recorded places:
unit swaps, stuck stretches, spikes, `-999` placeholders, duplicate and
shuffled rows, gaps, a cumulative meter. Detection recall and the effect of
each fault on accuracy are then measurable.

## Measures

1. End-to-end success: a usable model without human repair
2. Accuracy on the hidden period, in physical units, and skill vs persistence
3. ASHRAE Guideline 14 pass rate for energy-like targets
4. Leakage incidents: found by code audit and by validation-vs-hidden-test gaps
5. Injected faults detected and handled (recall)
6. Variation across repeated runs of the same task
7. Time, tokens and cost per task; number of human interventions

## Design details

- At least 3 frontier LLMs and 1 open-weight LLM, at least 10 runs per
  cell, since agents are not deterministic
- Report medians and interquartile ranges; paired tests across tasks
  (Wilcoxon signed-rank) for arm comparisons
- Every run's code, logs and outputs archived

## Layout (to build)

```
benchmarks/
  tasks/      one YAML per (building, target, horizon)
  inject/     fault-injection scripts and their ground-truth logs
  harness/    agent runner, AutoML runner, scoring script for the hidden period
  results/    archived runs (large files kept outside git)
```
