## 5. Case studies

### 5.1 Data

Three public datasets of measured data were chosen to cover many prediction
targets, different climates and data quality, and building portfolios
(Table 4). All can be downloaded by a script without an account, which makes
every result reproducible from the repository. Raw data are not redistributed.
A fourth dataset, the three-year LBNL Building 59 record [Luo et al. 2022], was
reviewed but left out because its repository does not allow scripted download.

**Table 4.** Datasets.

| | ROBOD [Tekler et al. 2022] | Aalborg offices [Melgaard et al. 2024] | BDG2 [Miller et al. 2020] |
|---|---|---|---|
| Location, climate | Singapore, tropical | Aalborg, Denmark, temperate | 19 sites, North America and Europe |
| Buildings / spaces | 5 rooms (2 lecture rooms, 2 offices, library) | 6 office rooms + building systems | 40 buildings sampled from 1,256 eligible |
| Period, resolution | Sep–Dec 2021 (weekdays, in blocks), 5 min | Feb–Dec 2023, 5 min | 2016–2017, 1 h |
| Targets used | CO2, temperature, humidity, PM2.5, people count, presence, chilled-water and plug energy | CO2, temperature, people count, room in use, ventilation electricity, district heating | Electricity |
| Licence | CC BY 4.0 | CC BY 4.0 | CC BY-SA 4.0 (results only) |

### 5.2 The agent's role

All loading, point decoding, declarations and judgment calls were made by an
LLM agent (Claude Opus 5.5 working in Claude Code), following the Agent Skill
in the repository. The agent's decisions are in the case-study scripts as
declarations and as notes, and in every run record. Examples:
- reading Aalborg's undocumented units from value magnitudes (power in W, air
  flow in m³/h);
- converting UTC-offset timestamps to local time with the zone kept, so that
  daylight-saving hours are handled exactly;
- excluding ROBOD's presence flag from the people-count virtual sensor, because
  it derives from the same camera ground truth;
- accepting missing camera counts in Aalborg as documented gaps.

Section 6.2 examines the judgment calls the data checks prompted.

The same agent also wrote the package. The case studies therefore show the
framework operated by an agent, not an independent test of agents; Section 7
discusses this.

### 5.3 Tasks

**ROBOD**: nine tasks per room, for five rooms (45 tasks). These were forecasts
30 min ahead of CO2, temperature, humidity, PM2.5, people count and presence
(yes/no); a virtual people counter estimating the current count from Wi-Fi
connections, CO2, sound, light and plug loads; and forecasts one hour ahead of
chilled-water and plug-load energy.

**Aalborg**: four tasks per room, for six rooms. These were forecasts one hour
ahead of CO2, temperature, people count and whether the room is in use (motion
sensor, yes/no). Three building-level tasks were added: ventilation electric
power one hour ahead, and district-heating power one hour and 24 hours ahead
(27 tasks).

**BDG2**: hourly electricity 24 hours ahead for 40 buildings. One
configuration, decided once for the dataset, was applied to every building.
Weather enters only up to the forecast time, because no weather forecasts are
available.

All tasks used 15-minute resolution (hourly for BDG2), the default 70/15/15
time-ordered split, and the default candidates. Hyperparameter search used 4–6
candidates per model. BDG2 used ridge and gradient boosting only, to keep the
40-building run short.

### 5.4 Experiments

**E1. Many targets.** All tasks were run through the full workflow. We report
skill against the strongest no-ML baseline (persistence, the value at the same
time yesterday, or the time-of-day profile for weekdays and weekends; the
training mean for estimates), errors in physical units, a rolling-origin
backtest over three later blocks, the coverage of the 90% prediction interval,
Guideline 14 results for energy, and promotion gates.

**E2. Evaluation protocol.** For the regression tasks of ROBOD and of Aalborg's
Room A and building systems, the same random forest on the same inputs was
evaluated three ways over the same rows:
- five-fold cross-validation with shuffled rows (equivalent to the 2024 random
  split);
- the same with features selected on all rows first (the 2024 recipe);
- five-fold blocked cross-validation, which removes from training a buffer
  (longest input look-back plus horizon) around each test block.

Because all three score the same rows, differences come from the protocol
alone. The time-ordered holdout used by the framework is reported alongside.

**E3. Fault injection.** Eight known faults were planted in Aalborg Room A
data (February–June) at random positions, with 10 random seeds:
- a change from degC to degF in the last 40% of the zone temperature;
- a three-day stuck sensor;
- ten spikes;
- twenty −999 placeholder values in the target;
- twenty "OFFLINE" text entries;
- a 12-hour outage;
- a day of duplicated rows;
- thirty rows out of order.

Detection compares the data check on clean and faulty data. Cost compares the
same random forest on the same leakage-safe inputs, trained on faulty data by
a quick unguarded script or by the framework (with the agent fixing the one
blocking error), and on clean data. All three are scored against the clean
target over the same test period.

**E4. Lifecycle.** A model trained on late February to April 2023 was put into
production for two Aalborg tasks (district heating and Room A CO2, one hour
ahead). Each month from May to December, the production model was monitored
on that month. When the drift check recommended it, a challenger was trained
on all data to date and promoted only if it passed the gates and beat the
champion on data neither had trained on. A static model that was never
retrained was scored on the same months.

**E5. Pilot: independent agents with and without the framework.** To
separate the framework from the agent that built it, fresh agent instances
were given a task folder containing only a raw export with planted faults and
a task description. Each had to deliver `model.py` with a `predict(csv_path)`
function and a `report.json` stating the RMSE it expected on future data.

- **Tasks:** two tasks, one hour ahead at 15-minute resolution. T1 is Aalborg
  Room B CO2, training to May 2023, with June hidden. T2 is ROBOD Room 5
  chilled-water energy, with the last fifth of the days hidden.
- **Conditions:** *agent alone* (pandas and scikit-learn only, bemlops
  forbidden) and *agent + bemlops* (told to follow the Agent Skill).
- **Models:** each condition ran with two models, Claude Opus 5.5 and Claude
  Sonnet 5.5, giving eight runs in total.
- **Isolation:** the agents could not see the hidden data or the evaluation code.

The evaluator then measured four things for each deliverable:
- whether it ran;
- its RMSE and skill against persistence on the hidden period, using the
  clean target;
- an automatic leakage test, which perturbs every value at or after T − 45 min
  for 15 random hidden-period times T and checks that the forecast for T is
  unchanged;
- the ratio of achieved to self-reported RMSE.

With one run per cell this is a pilot, not a benchmark. It tests whether the
effects the framework is designed for show up at all with agents that did not
write it.
