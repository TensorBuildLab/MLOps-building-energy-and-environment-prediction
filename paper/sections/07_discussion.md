## 7. Discussion

### 7.1 Where the guardrails mattered, and where they did not

The experiments separate four places where checks can make a difference.

**Evaluation protocol: large effect.** A random split understated error on
every task tested (Section 6.1), by a margin larger than most differences
between models in this study. This is the protocol of our 2024 study and a
common one in published building-ML work. None of the pilot agents used it:
all eight split in time order unprompted, although their prompts announced a
leakage check. The framework's contribution here is to make the time-ordered
protocol, and the strongest baseline, the default for whoever uses it,
including less careful users and agents.

**Baselines and gates: large effect on what gets deployed.** Across 92 tasks
the strongest no-ML rule was often hard to beat (Section 6.2). The framework
kept the baseline in 20 tasks, and 41 models failed the promotion gates. A
pipeline that always reports its best model would have deployed all of them. For an operator, a forecast that is no better than
"same as an hour ago" adds maintenance without adding value.

**Fault handling: small, consistent effect.** On real data with planted
faults, the framework's standard handling made the result on faulty data
match the result on clean data. A quick script was 1.6–1.9 ppm worse in MAE,
and three to five times less stable between seeds (Section 6.3). The
difference is real but small in absolute terms. The detectors also miss
things: a stuck meter at its idle floor half the time, and a dead meter that
only a cross-sensor check could reveal.

**Capable agents: no measurable effect on accuracy.** Capable agents, told
that their work would be checked for leakage, built equally accurate,
leak-free models with or without the framework (Section 6.5). They found as
many planted faults, and wrote their own causality tests. The framework arm
cost more tokens, tool calls and time. For RQ5, the answer is that with
capable, primed agents the framework did not change accuracy or leakage.

Taken together, these results place the framework's measured value in four
things:
- **making the time-ordered protocol and the strongest baseline the default**,
  rather than something that depends on a careful prompt;
- **making work comparable.** The eight pilot agents produced eight different
  pipelines with eight different evaluation designs, which an operator would
  have to audit one by one. The framework gives every model the same record,
  baselines, gates and monitoring;
- **supporting the lifecycle after the first model** (Section 6.4);
- **recording decisions**, so that they can be re-executed.

Whether the defaults matter more for weaker or unprimed agents is the main
open question. The pilot was not designed to answer it.

### 7.2 Lifecycle: monitoring helps; persistence is the bar

Monitoring with gated retraining clearly beat a model left alone (Section
6.4). It did not beat persistence for district heating, and simple monthly
retraining did better on both tasks. Three lessons follow.

**A drift check must compare with a baseline, not only with the model's own
past error.** In summer the district-heating load barely changes, so
persistence was nearly perfect, and every model looked poor next to it. The
check in the evaluated version compared only with test-time error and never
recommended falling back to persistence. The fallback rule we added
afterwards would have helped for district heating and hurt slightly for CO2
in this one trajectory. That is why it is a recommendation to the operator,
not an automatic switch.

**Retrain on a schedule, not only on an alarm.** The drift alarm compared
recent error with test-time error, with a tolerance of 1.5. Over the summer,
district heating lost skill slowly and never crossed that threshold, so the
production model was not retrained from June to October, while a monthly
model kept adapting. The framework's `retrain` pipeline can run on any schedule.
The evidence here favours using it monthly, with the drift check as a second
line of defence.

**Gates cost little, but their value was not tested.** Monthly retraining
without gates did well here because the data were clean enough that
retraining rarely made things worse. The gates exist for the months when a
fault or an unusual period would otherwise be trained into production. Two
clean trajectories over eight months do not contain enough such months to
measure that benefit.

### 7.3 Judgment stays with the agent

The checks directed judgment rather than replacing it. On the real data,
every judgment call in the case studies was prompted by a warning and
settled with evidence that is now in the record. Examples:
- a CO2 sensor floor;
- change-of-value logging, recognised from the share of unchanged steps;
- outdoor humidity saturating on tropical nights;
- gaps in the camera counts.

A fixed pipeline would have had two bad options. It could mask those
stretches and lose most nights of CO2 data. Or it could ignore stuck sensors
and train on a weather station that repeated one value for 37 hours.

The dead chilled-water meter shows the limit of this division of labour. The
case-study agent, following the skill, did not look for contradictions
between related points. The independent pilot agents, without the framework's
checks to lean on, all did. A guardrail that reports no problem can make an
agent less curious. The skill now asks the agent to check related points
against each other, and cross-sensor checks are the natural next guardrail.

### 7.4 Threats to validity

**Internal validity.**
- **The same agent built the framework and ran the case studies.** The
  framework is therefore not an independent tool tested by a neutral user.
  Several detectors were revised on ROBOD and Aalborg (Appendix A), so the
  data checks are partly in-sample on those datasets. The fault-injection
  detection rates are optimistic for the same reason. BDG2 is closer to held
  out but not strictly so (Section 5.2).
- **The agent missed a real fault, and independent agents caught it.** We
  report the affected tasks before and after the fix.
- **The fault-cost comparison uses a fix written by the authors.** The unit
  fix in E3 was coded by the authors, who knew what had been planted. We gave
  the same fix to the unguarded arm, and it made no difference.

**Construct validity.**
- **Skill is defined on RMSE**, and the promotion threshold of 0.05 depends
  on that choice.
- **Fault detection is counted per column and type**, not per located
  sample.
- **The pilot prompts announced a leakage check and asked for rigour**, and
  only the framework arm was asked for a usability report. Its cost figures
  include that extra reporting.
- **The pilot's framework arm used an earlier package version** than the case
  studies.
- **Guideline 14 criteria were written for measurement and verification.** We
  use them as a familiar reference for forecasts, not as a claim of
  compliance.

**Statistical conclusion validity.**
- **Each E1 task was run once and scored on one test window.** The
  Diebold–Mariano tests and the backtest address this partly. Where test and
  backtest disagreed in sign, the gates followed the test window.
- **The pilot has one run per cell**, two tasks, and two models of one
  family, the same family as the agent that built the framework.
- **The lifecycle experiment is one trajectory for each of two tasks.**

**External validity.**
- **The three datasets are public, documented, and partly curated by their
  authors.** Commercial BAS exports are messier.
- **The records are short.** ROBOD covers 29–47 weekdays per room, and
  Aalborg ten months.
- **There were no weather forecasts.** Day-ahead tasks used measured weather
  up to the forecast time only.
- **The models and searches were deliberately ordinary.** Stronger models,
  including probabilistic, deep and foundation models [Emami et al. 2023],
  would beat the baselines more often.

### 7.5 What the error gaps mean in operation

In the protocol comparison, a random split understated RMSE by a median of
about a quarter (Section 6.1). For a model predictive controller sized on
the reported error, that means comfort or demand constraints tighter than
the evidence supports. For demand response, it means overstated confidence
in hour-ahead load. For measurement and verification, it means a baseline
model that looks compliant when it is not.

The prediction intervals were too narrow wherever the test period differed
from the period they were calibrated on. District heating is the clearest
case: calibrated on October to mid-November, its intervals covered only about
a quarter of the values from mid-November to December, when the heating load
was larger and more variable. Intervals of this kind should be recalibrated as part of
monitoring.

### 7.6 Implications

- **For researchers:** building time series should not be evaluated with a
  random split. Results should be reported against the strongest simple
  baseline, with a test of the difference.
- **For practitioners:** the framework turns a building-specific modeling
  project into a configuration that can be reviewed, re-run, monitored and
  retrained. Its gates will often recommend a simple rule. That is a result,
  not a failure.
- **For agent developers:** domain checks are worth building, but capable
  agents can already reproduce much of what such checks do. What they do not
  provide by default is a common record and a lifecycle. Agents are also
  effective testers of the checks.
