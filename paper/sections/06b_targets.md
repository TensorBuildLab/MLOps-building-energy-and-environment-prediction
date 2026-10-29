### 6.2 Many targets, many buildings (RQ1)

All 92 tasks ran through the full workflow to a fitted, evaluated and gated
result, with no manual step beyond the declarations and notes in the
case-study scripts. Table 7 summarises the results by dataset and Table 8 by
target. Figure 3 shows every task.

**Table 7.** Results by dataset. Proportions with 95% Wilson intervals. DM: Diebold–Mariano test of the model against the strongest baseline on the test period.

<!-- table: datasets -->

**Table 8.** Results by target type (all datasets).

<!-- table: targets -->

![Figure 3. Skill against the strongest no-ML baseline on the held-out test period, for every task. Zero means no better than the baseline; a skill of exactly zero means the baseline itself was kept.](figures/skill_by_target.png)

**How often machine learning beat the strongest simple rule.** The median
skill across the 92 tasks was 0.10 (interquartile range 0.00–0.25):
- The model had a lower test RMSE than the baseline in 60 tasks (65%; 95%
  interval 55–74%).
- The difference was significant (Diebold–Mariano, *p* < 0.05) in 48 (52%;
  42–62%).
- The baseline was significantly better in 5.
- In 20 tasks a baseline had the lowest validation error and was kept.
- 51 tasks (55%; 45–65%) passed all five promotion gates.

With deliberately ordinary models and no weather forecasts (Section 5.3),
a model was worth deploying in only about half of the tasks. In the rest,
the framework recommended the simple rule.

**By target.** The pattern follows the physics of each target:
- **CO2** was the most consistently predictable (skill > 0 in 9 of 11 tasks,
  8 significant). Its changes lag occupancy and ventilation, which the inputs
  measure.
- **The virtual people counter**, which estimates the current count from
  Wi-Fi, CO2, sound and plug loads, had the highest skill (median 0.36).
- **Humidity** forecasts reached a median skill of 0.36.
- **Occupancy-count forecasts 30 minutes or one hour ahead** barely beat
  persistence (median 0.02): who walks in next is not in the data.
- **Room temperature** had a median skill of 0.06. Persistence is hard to
  beat for a slow, well-controlled variable.
- **Energy targets** had median skills of 0.12. 23 of 33 met the Guideline 14
  hourly criteria: all 3 Aalborg building-level meters, 16 of 20 BDG2
  buildings, but only 4 of 10 ROBOD room meters. The six ROBOD failures are
  room-level chilled-water and plug meters with small, intermittent loads,
  for which CV(RMSE) is large whatever the model (127–570% in the worst
  three).

**By dataset.** Aalborg had the highest share of models significantly better
than the baseline (20 of 27), and ROBOD the lowest (17 of 45). ROBOD's rooms
have 29–47 weekdays of data each. Its lecture rooms are often empty, and in
Room 1 the framework kept persistence for 5 of the 9 tasks.

**Backtest and test.** The rolling-origin backtest and the single test window
disagreed in the sign of the skill in 7 of 92 tasks. The clearest case was
Aalborg Room E temperature. Its test skill was −1.03, against a backtest skill
of +0.05. The test model, trained to mid-November, probably met a heating
regime it had not seen. The backtest refits before each of its blocks, so by
its last block it had seen the start of the heating season. The gates follow
the test window and refused the model. The two numbers
together tell an operator more than either alone.

**Prediction intervals.** The nominal 90% intervals covered a median of
90–96% of test values for the indoor-environment and occupancy targets. Coverage was poor
wherever the test period differed from the validation period on which the
intervals were calibrated:
- 26–28% for Aalborg district heating (October to mid-November against
  mid-November to December);
- 47% for Room E temperature;
- 37% for the BDG2 building whose consumption collapsed (below).

Global, single-period intervals are a weak point of the current version
(Section 7.5).

**The dead chilled-water meter changed the results in both directions.**
After the dead-meter days were set to missing (Section 5.2):
- **Room 3.** The task went from "persistence kept" (skill 0) to a model with
  skill 0.49 that passed all gates: the false zeros had made the series
  unpredictable.
- **Room 5.** The task went the other way, from skill 0.60 to 0.00 (the
  time-of-day profile kept). The false zeros had dragged the profile baseline
  down, so the model looked far better than it was.
- **Room 4,** with one dead day, hardly changed (0.25 to 0.24).

The earlier results are kept in the repository. A fault that a single-column
check cannot see can therefore inflate, or hide, a model's value.

#### One configuration across twenty buildings

The BDG2 study applied one configuration to 20 buildings at 16 sites (Table
9, Figure 4). The buildings were in education, office, lodging, public
services and other uses. The agent decided the configuration once for the
whole dataset. The task was hourly electricity 24 hours ahead, with weather
used only up to the forecast time.

**Table 9.** BDG2: one configuration, 20 buildings.

<!-- table: bdg2 -->

![Figure 4. CV(RMSE) of the day-ahead hourly electricity forecasts on the held-out test period, BDG2 (20 buildings). The vertical line is the Guideline 14 hourly limit.](figures/bdg2_cvrmse.png)

Every building was fitted with no manual step, in a median of 77 s on a
laptop while other studies were running. The median skill against the
strongest baseline was 0.12:
- 14 of 20 models beat that baseline on the test period, and 11 did so
  significantly;
- 16 of 20 met Guideline 14;
- 11 of 20 passed all gates.

The table hides two practical lessons.

**Simple rules often win.** In five buildings a baseline won on validation
(persistence in two, the time-of-day profile in three), and the framework kept
it. In three more, the model beat the baseline by less than the 0.05 skill
required for promotion. A pipeline that always reports its best model would
have deployed all eight.

**The gates catch broken test periods.** At one education building
(Rat_education_Colin), consumption in the test period fell far below anything
in training (NMBE −110%). The model's error was about six times the
baseline's (skill −5.15), and the gates refused it. The data check had found
nothing wrong with the individual readings. What had changed was the
building.

**Answer to RQ1.** One workflow, with one configuration per dataset, produced
an evaluated and gated result for every target we tried. Ordinary models
beat the strongest simple rule significantly in about half of the tasks. The
framework's main practical output is often the decision not to deploy.
