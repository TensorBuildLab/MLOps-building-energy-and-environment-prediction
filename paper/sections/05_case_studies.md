## 5. Study design

### 5.1 Data

We chose three public datasets of measured data (Table 5). Together they
cover many prediction targets, three climates, different levels of data
quality, and a building portfolio. All three can be downloaded by a script
without an account, and the script verifies checksums, so every result can
be reproduced from the repository. Raw data are not redistributed.

We reviewed a fourth dataset, the three-year LBNL Building 59 record [Luo et
al. 2022], and left it out because its repository does not allow scripted
download.

**Table 5.** Datasets.

| | ROBOD [Tekler et al. 2022] | Aalborg offices [Melgaard et al. 2024] | BDG2 [Miller et al. 2020] |
|---|---|---|---|
| Location, climate | Singapore; tropical | Aalborg, Denmark; temperate | 16 sites in North America and Europe |
| Buildings / spaces | 5 rooms (2 lecture rooms, 2 offices, 1 library) | 6 office rooms and building systems | 20 buildings drawn from 1,256 eligible |
| Period, resolution | Sep–Dec 2021 (weekdays, in blocks); 5 min | Feb–Dec 2023; 5 min | 2016–2017; 1 h |
| Targets used | CO2, temperature, humidity, PM2.5, people count, presence, chilled-water and plug energy | CO2, temperature, people count, room in use, ventilation electricity, district heating | Electricity |
| Role in this study | Development and evaluation | Development and evaluation | Closer to held out (see Section 5.2) |
| Licence | CC BY 4.0 | CC BY 4.0 | CC BY-SA 4.0 (results only) |

### 5.2 Who did what

**The agent's work.** An LLM agent (Claude Opus 5.5 in Claude Code) followed
the Agent Skill in the repository and did all of the following:
- loading the data and decoding point names;
- writing the declarations;
- making the judgment calls.

These decisions are frozen in the case-study scripts, as declarations and
written notes, and copied into every run record. Examples:
- reading Aalborg's undocumented units from the size of the values (power in
  W, air flow in m³/h);
- converting timestamps with a UTC offset to local time with the time zone
  kept, so that daylight-saving hours are handled exactly;
- excluding ROBOD's presence flag from the people-count virtual sensor,
  because it comes from the same camera ground truth;
- accepting missing camera counts in Aalborg as documented gaps.

**What the record does not contain.** The agent's conversation transcripts
are not archived, so the record shows its decisions but not its reasoning.

**Human oversight.** The authors set the research questions and the
datasets, and reviewed the code, results and text.

**Development versus evaluation data.** The same agent also wrote the
package, so the case studies show the framework operated by an agent, not an
independent test of agents. Section 7.4 discusses this threat to validity.
Several detectors were revised on ROBOD and Aalborg data (Appendix A), so on
those two datasets the data checks are partly in-sample. BDG2 prompted none
of those revisions. Its declarations and notes were set before its first run
and not changed. Between runs we changed two things:
- the building sample, to 20 buildings drawn round-robin across sites, to
  save time;
- the candidate list, adding `gbm_change`, which had been added to the package
  for the pilot.

BDG2 is therefore closer to held-out data, but it is not strictly held out.

**A fault our agent missed.** ROBOD's chilled-water meters in three rooms
read exactly zero for whole days while the air-handling unit's fan was
running and its cooling-coil valve was open: 9 days in Room 3, 1 in Room 4
and 10 in Room 5. Each day counts as an outage if the fan ran above 5 Hz with
the valve above 15% for at least an hour, and no chilled-water energy was
recorded in those hours. This is physically implausible. No single-column
check can flag it, because zero is a normal reading for an idle meter.

Our case-study agent missed it. All four independent pilot agents that worked
on Room 5 found it (Section 6.5). The case-study loader now sets those days
to missing. The three affected tasks were re-run, and the earlier results
are kept in the repository for comparison.

### 5.3 Tasks

**ROBOD** had nine tasks per room for five rooms, 45 tasks in all:
- forecasts 30 min ahead of CO2, temperature, humidity, PM2.5, people count
  and presence (yes/no);
- a virtual people counter, estimating the current count from Wi-Fi
  connections, CO2, sound, light and plug loads;
- forecasts one hour ahead of chilled-water and plug-load energy.

**Aalborg** had 27 tasks:
- four per room for six rooms: forecasts one hour ahead of CO2, temperature,
  people count, and whether the room is in use (motion sensor, yes/no);
- three building-level tasks: ventilation electric power one hour ahead, and
  district-heating power one hour and 24 hours ahead.

**BDG2** had one task per building, 20 tasks in all: hourly electricity 24
hours ahead. The agent decided one configuration for the whole dataset and
applied it unchanged to every building. Weather enters only up to the
forecast time, because the dataset contains no weather forecasts.

All tasks used 15-minute resolution (hourly for BDG2), the default 70/15/15
time-ordered split and the default candidates. Hyperparameter searches were
small, at 3–6 settings per model. BDG2 used ridge regression and both kinds
of gradient boosting, and Aalborg omitted the random forest, both to save
time. With small searches and no weather forecasts, the models are
deliberately ordinary. A strong baseline therefore has a real chance to win,
and the results show how often a typical, untuned model is worth deploying,
not how good the best possible model is.

### 5.4 Research questions and experiments

Each experiment answers one research question from Section 1.

**E1 (RQ1): many targets, many buildings.** Every task was run through the
full workflow. We report:
- skill against the strongest baseline;
- a Diebold–Mariano test of each model against that baseline on the test set
  [Diebold and Mariano 1995];
- errors in physical units;
- the rolling-origin backtest;
- the coverage of the 90% interval;
- Guideline 14 results for energy;
- the gate decisions.

The Diebold–Mariano test uses squared-error loss (Brier loss for yes/no
targets) and a heteroskedasticity- and autocorrelation-consistent variance
with a Bartlett kernel. Its lag is the larger of the horizon and the
Newey–West rule-of-thumb bandwidth. Proportions are reported with 95% Wilson
intervals [Wilson 1927].

**E2 (RQ2): evaluation protocol.** The same random forest, on the same inputs
and the same rows, was evaluated in three ways:
1. five-fold cross-validation with shuffled rows, equivalent to the random
   split of the 2024 study;
2. the same, with features first selected on all rows (the full 2024 recipe);
3. five-fold blocked cross-validation, which removes from training a buffer
   around each test block equal to the longest input look-back plus the
   horizon.

E2 used the regression tasks of ROBOD Rooms 4 and 5 (the rooms with the most
data), plus Aalborg Room A and its building systems. Because all three
protocols score the same rows, differences come from the protocol alone. The
framework's own time-ordered holdout scores different rows. It is reported
alongside for reference, not as ground truth.

**E3 (RQ3): fault injection.** Eight known faults were planted in Aalborg
Room A data (February–June 2023) at random positions, with ten random seeds:
- a change from degC to degF in the last 40% of the zone temperature;
- a three-day stuck sensor;
- ten spikes;
- twenty −999 placeholder values in the target;
- twenty "OFFLINE" text entries;
- a 12-hour outage;
- a day of duplicated rows;
- thirty rows out of order.

A fault counts as *detected* when the data check on the faulty data reports
an issue, for the column and type of that fault, that it did not report on
the clean data. Detection is per column and type, not per located sample.

For the cost of the faults, the same random forest on the same leakage-safe
inputs was trained in four ways:
1. on clean data;
2. on faulty data prepared by a quick script that coerces text, sorts,
   averages duplicates, resamples and fills forward;
3. by the same script after the same unit fix the agent applied;
4. by the framework, after the agent's one fix to the blocking unit error.

All four are scored against the clean target over the same test period. To
show how much a different random seed moves the result, the clean-data model
was refitted with each of the ten seeds. Paired Wilcoxon signed-rank tests
compare arms that share a seed, and so share the same planted faults.

**E4 (RQ4): lifecycle.** The task was to forecast two Aalborg series one hour
ahead: district heating, and Room A CO2. A model trained on late February to
April 2023 was promoted to production. Each month from May to December, the
production model was scored on that month and the drift check was run (Section
3.7). When the check recommended retraining, a challenger was trained on all
data to date, and it was promoted only if it passed the gates and beat the
champion. Four other arms were scored on the same months:
- a static model that was never retrained;
- a model retrained every month on all earlier data, without gates;
- persistence;
- a counterfactual fallback rule: serve persistence in month *m* if the
  production model was worse than persistence in month *m* − 1.

The fallback rule uses only past months, so it could have run in operation.

**E5 (RQ5): formative pilot with independent agents.** To separate the
framework from the agent that built it, fresh agent instances were each given
a task folder. The folder held only a raw export with planted faults and a
task description. Each agent had to deliver:
- `model.py`, with a `predict(csv_path)` function;
- `report.json`, stating the RMSE it expected on future data.

The design:
- **Tasks.** There were two tasks, each one hour ahead at 15-minute
  resolution. T1 was Aalborg Room B CO2, with training data up to May 2023 and
  June hidden. T2 was ROBOD Room 5 chilled-water energy, with the last fifth
  of the days hidden.
- **Conditions.** In the *agent alone* condition, the agent had pandas and
  scikit-learn only, and bemlops was forbidden. In the *agent + bemlops*
  condition, the agent was told to follow the Agent Skill.
- **Models.** Each condition ran with Claude Opus 5.5 and with Claude Sonnet
  5.5, in Claude Code, giving eight runs.
- **Isolation.** The agents could not see the hidden data or the evaluation
  code. Their launch prompts are in the repository (`benchmarks/pilot/`).

The evaluator scored each deliverable in four ways:
- whether it ran;
- its RMSE on the hidden period against the clean target, as skill against
  both persistence and the time-of-day profile;
- an automatic leakage test, which perturbs every value at or after T − 45 min
  for 15 random hidden-period times T and checks that the forecast for T is
  unchanged;
- the ratio of achieved to self-reported RMSE.

Paired day-block bootstrap intervals (2,000 resamples of whole days) give the
RMSE difference between conditions for the same task and model. We also
audited each agent's code and report by hand, and we recorded its tokens,
tool calls and wall-clock time.

With one run per cell, E5 is a formative usability study, not a benchmark.
It asks whether the effects the framework is designed for show up at all
with agents that did not write it.
