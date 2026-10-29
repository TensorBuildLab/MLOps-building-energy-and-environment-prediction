### 6.4 Deployment, monitoring and retraining over eight months (RQ4)

Both lifecycle tasks started from a model trained on late February to April
2023, the heating season, and promoted after it passed the gates. Table 13
gives the monthly RMSE of every arm, Table 14 the means over May to December,
and Figure 5 shows the trajectories.

**Table 13.** Monthly RMSE on each month (kW for district heating, ppm for CO2). "Monitored + gated" is the framework's production model; "(P)" marks months in which the fallback rule would have served persistence. Drift ratio: recent error over test-time error.

<!-- table: lifecycle -->

**Table 14.** Mean monthly RMSE, May to December 2023.

<!-- table: lifecycle_summary -->

![Figure 5. Monthly RMSE of the four arms. Dotted vertical lines mark a retrained model promoted at the end of a month and served from the next.](figures/lifecycle_rmse.png)

**District heating.** The drift check recommended retraining in May,
November and December, and each challenger was promoted. The December
challenger would have served from January, after the experiment ended:
- **May.** The drift check found the error 1.9 times its test-time level,
  and inputs outside their training range. A challenger trained on data to
  the end of May beat the champion on rows neither had seen (RMSE 0.58 vs
  1.01 kW) and was promoted.
- **November.** With the heating back on, the summer-trained model drifted
  (5.4 times its test-time error). It was replaced at the end of the month.

Monitoring with gated retraining cut the mean monthly RMSE from 2.28 kW
(static) to 1.53 kW. It did not beat persistence (1.56 kW), and it was worse
than persistence in five of the six months from May to October:
- With the heating off, the load barely changes, so "same as an hour ago"
  is nearly perfect.
- The drift check compared the model only with its own test-time error, not
  with persistence, so it never flagged this.

Retraining every month without gates did best, at 1.41 kW. The drift check
did not recommend retraining once between June and October: the drift ratio
stayed at 1.29–1.44, below its threshold of 1.5, through the slow loss of
skill over the summer.
The fallback rule added after this experiment (serve persistence after a
month in which the model lost to it) would have given 1.50 kW.

**Room A CO2.** Retraining was triggered in May and November by inputs
moving outside their training range, before accuracy had degraded, and both
challengers were promoted. The December challenger lost to the champion on
unseen rows (29.5 vs 28.7 ppm) and was not promoted, as designed.
- **Production model.** It averaged 33.5 ppm, against 37.4 ppm static and
  36.1 ppm for persistence, and beat persistence in six of the eight months.
- **Monthly retraining** reached 32.3 ppm.
- **The fallback rule** would have made CO2 worse (34.5 ppm), because a month
  lost to persistence was followed by a month won.

**Answer to RQ4.** Monitoring with gated retraining clearly beat a model left
alone. It did not beat persistence for district heating, and it did worse
than simple monthly retraining on both tasks. With clean data, how often a
model is retrained mattered more than the gates. The gates exist for the
months when a fault or an unusual period would otherwise be trained into
production, and two clean trajectories contain too few such months to show
their value.

The practical lesson is to schedule retraining (the framework's `retrain`
pipeline runs champion against challenger on any schedule) rather than wait
for a drift alarm. Persistence should be scored next to the model in every
monitoring window. That comparison has since been added to the drift check
(Appendix A), but it has not been evaluated here.
