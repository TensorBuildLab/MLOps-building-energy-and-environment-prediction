### 6.5 Deployment, monitoring and retraining over eight months

Both lifecycle tasks started with a model trained on late February to April 2023
(the heating season) and promoted after passing the gates. Each month, the
production model was monitored on that month; Table 10 and Figure 4 show the
outcome.

**District heating:**
- **May:** the drift check found the error 1.9 times its test-time level, and
  inputs outside their training range. A challenger trained on data to the end
  of May beat the champion on rows neither had seen (RMSE 0.58 vs 1.01 kW) and
  was promoted.
- **June to October:** the promoted model's error stayed at 0.75–0.83 kW, while
  the never-retrained static model's error rose to 1.5–2.2 kW.
- **November:** with heating back on, the summer-trained model drifted (5.4×)
  and was briefly worse than the static spring model. It was replaced at the end
  of the month, and the replacement beat the static model in December.
- **Over May to December:** the mean monthly RMSE was 1.53 kW with monitoring
  against 2.28 kW without, a third lower.

**Room A CO2:**
- **May:** retraining was triggered by inputs moving outside their training
  range, before accuracy had degraded.
- **Over May to December:** the mean monthly RMSE was 33.5 ppm against
  37.4 ppm (10% lower), and the mean monthly skill against persistence was 0.07
  against −0.05.
- **December:** a challenger lost to the champion on unseen rows (29.5 vs
  28.7 ppm) and was not promoted, as designed.

**The gap this experiment revealed:** for district heating in summer, even the
retrained model was worse than persistence (skill −0.3 to −0.45). With heating
off, the power barely changes, and "same as an hour ago" is nearly perfect.
The drift check compared the model with its own test-time error, not with the
baseline, so it never recommended falling back to persistence. Monitoring now
also scores the baseline on the same recent rows and flags a model that no
longer beats it (Section 6.7).

**Table 10.** Monthly monitoring and retraining (RMSE in kW for district heating, ppm for CO2; skill against persistence).

<!-- table: lifecycle -->
