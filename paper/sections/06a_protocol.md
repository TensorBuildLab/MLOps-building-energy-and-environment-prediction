## 6. Results

### 6.1 Evaluation protocol (RQ2)

Table 6 and Figure 2 compare the three protocols on 22 regression tasks: 16
from ROBOD Rooms 4 and 5, and 6 from Aalborg Room A and its building systems.
The model, inputs and scored rows are the same in all three; only the
protocol differs. The per-task results are in Table B1 (Appendix B).

**Table 6.** The same random forest, inputs and rows, evaluated with shuffled and blocked five-fold cross-validation.

<!-- table: protocol -->

![Figure 2. R² of the same model on the same rows with shuffled and with blocked cross-validation. Every point lies above the diagonal: shuffling made every model look better than it is.](figures/protocol_r2.png)

**Shuffling understated error on every task.** Blocked cross-validation gave
a higher RMSE than shuffled cross-validation on all 22 tasks. The median
ratio was 1.36 (interquartile range 1.26–1.44; range 1.02–2.46). In other
words, the random split of our 2024 study would have understated RMSE by a
median of 27%, and by more than 10% on 21 of the 22 tasks. The median R²
fell from 0.92 to 0.86. The largest gaps were for:
- the virtual people counters in both rooms (ratios 2.46 and 1.86). Their
  inputs at the same moment make neighbouring rows near-duplicates; R² fell
  from 0.89 to 0.32 in Room 5;
- the Room 5 plug load (2.23) and the Aalborg ventilation power (1.94),
  which follow schedules.

With shuffling, a test row's neighbours a few minutes earlier and later are
in the training set, so the model only has to interpolate between them. The
smallest gap (1.02) was for a plug load the model could hardly predict under
either protocol (R² 0.13 and 0.10).

**Feature selection on all rows added no measurable optimism.** In the full
2024 recipe, features are first selected on all rows. On these tasks that
made shuffled cross-validation slightly *less* optimistic (median ratio to
shuffled alone 1.04; range 1.00–1.31), because dropping features removed
information the forest could otherwise interpolate from. Selection leakage
remains a risk in principle [Kapoor and Narayanan 2023], but here the random
split did all the damage.

**One time-ordered holdout is not ground truth.** The framework's own test
score comes from a single later window. Compared with blocked
cross-validation over the whole record, it was lower on some tasks and
higher on others (median ratio 0.90; range 0.30–2.38). A single window can
be unusually quiet, like June for Room B CO2 in the pilot, or unusually
hard, like the start of the heating season for district heating. This is why
the framework also reports a rolling-origin backtest (Section 6.2) and why
the lifecycle needs monitoring (Section 6.4).

**Answer to RQ2.** On real building data the protocol of the 2024 study
understated error by about a quarter. That is more than the typical gain of
a model over the strongest baseline in Section 6.2.
