### 6.3 Planted faults (RQ3)

**Detection.** Table 10 shows how often each planted fault was detected over
ten seeds on real Aalborg data.
- Six of the eight fault types were detected in every seed. The unit change
  was always a blocking error.
- Spikes were detected in nine seeds of ten.
- The three-day stuck ventilation meter was detected in five of ten. When the
  frozen value lies at the meter's night-time floor, a stuck meter looks the
  same as equipment that is switched off. This is the price of the rule that
  stops idle equipment, and solar irradiance at night, from being flagged as
  stuck.

These rates are optimistic in one respect: several detectors were revised on
this dataset (Section 5.2).

**Table 10.** Detection of planted faults (Aalborg Room A, ten seeds). A fault counts as detected when the check reports a new issue of that type on that column.

<!-- table: fault_detection -->

**Cost.** Table 11 compares the same random forest on the same inputs,
trained four ways. Table 12 gives paired tests.

- **Framework.** Trained on faulty data with the framework, after the agent's
  one fix to the blocking unit error, the model reproduced the clean-data
  result in every seed. Its MAE was 19.8 ± 0.2 ppm, against 19.9 ± 0.3 ppm on
  clean data.
- **Quick script.** The same model trained by a quick script had an MAE of
  21.6 ± 1.7 ppm, 1.9 ppm worse in the median paired seed (Wilcoxon
  *p* = 0.010).
- **Quick script with the same unit fix.** Giving the script the agent's unit
  fix changed almost nothing: MAE 21.6 ± 1.8 ppm, 1.6 ppm worse than the
  framework (*p* = 0.010).

The gain therefore came from the framework's standard handling of the other
faults: masking the placeholder values, text, spikes and stuck stretches, and
not filling the outage. It did not come from the one decision the agent made.
The unit fix mattered little here, probably because room temperature carries
little information about CO2 an hour ahead. On a target that depends on the
switched input, it would matter more.

**RMSE.** The effect did not appear in RMSE, the metric used everywhere else
in this paper. All three faulty-data arms averaged 34.4–34.5 ppm, against
34.8 ppm on clean data, and the paired differences were not significant
(*p* ≥ 0.92). RMSE here is dominated by large errors when occupants arrive or
leave, which no arm predicts. The planted placeholders probably bias many
ordinary predictions by a few ppm instead: they corrupt a few training
targets, and those targets pull down the averages in the trees' leaves. This
moves MAE but hardly moves RMSE.

**Spread between seeds.** What did change in RMSE was its spread. The script's
RMSE varied by ± 1.3 ppm between seeds, against ± 0.3 ppm with the framework
and ± 0.4 ppm from the random seed alone on clean data.

In short, the framework made the result on faulty data match the result on
clean data. On this task, the difference from a quick script is small in
absolute terms.

**Table 11.** The same random forest on the same inputs, scored against the clean target over the same test period (mean ± standard deviation over ten seeds).

<!-- table: fault_cost -->

**Table 12.** Paired Wilcoxon signed-rank tests against the framework arm (same seed, so same planted faults; positive = framework better).

<!-- table: fault_tests -->
