### 6.2 One configuration across twenty buildings

The BDG2 study applied one configuration, decided once by the agent for the
whole dataset, to 20 buildings at 16 sites: education, office, lodging,
public services and other uses (Table 6, Figure 3). The task was hourly
electricity forecast 24 hours ahead, with weather used only up to the forecast
time.

- **Fitted:** every building, with no manual step.
- **Skill against the strongest no-ML baseline:** median 0.12. That baseline was
  persistence (the value 24 hours earlier) or the time-of-day profile, whichever
  was better on validation. 70% of buildings beat it on the test period.
- **ASHRAE Guideline 14:** 80% met the hourly criteria.
- **All promotion gates:** 55% passed. For the others, the framework recommended
  the simple rule rather than a model.
- **Run time:** about one to two minutes per building on a laptop, while other
  studies were running.

The table hides two practical lessons.

**Simple rules often win.** In five buildings a baseline won on validation
(persistence in two, the time-of-day profile in three), and the framework kept
it. In three more, the model beat the baseline by less than the 5% skill
required for promotion. A pipeline that always reports its best model would
have deployed all eight.

**The gates catch broken test periods.** At one education building
(Rat_education_Colin), consumption in the test period fell far below anything
in training (NMBE −110%). The model's error was five times the baseline's, and
the gates refused it. The data check had found nothing wrong with the
individual readings. What changed was the building.

The 90% prediction intervals covered a median 87% of test values: slightly
too narrow. The intervals are global (one width for every hour) and calibrated
on a single validation period; Section 7.4 discusses this.

**Table 6.** BDG2: one configuration, 20 buildings.

<!-- table: bdg2 -->
