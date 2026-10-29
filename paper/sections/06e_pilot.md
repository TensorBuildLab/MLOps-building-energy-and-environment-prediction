### 6.5 Formative pilot: independent agents with and without the framework (RQ5)

**Delivery and leakage.** All eight deliverables ran on the hidden data. All
passed the leakage test: no forecast changed when every later value was
perturbed (Table 15).

**Table 15.** Pilot results on the hidden periods.

<!-- table: pilot -->

**T1 (Room B CO2, June hidden).** No agent beat persistence by a meaningful
margin: skills ranged from −0.037 to 0.058. June was quiet. Persistence RMSE
was 21 ppm, against 29–48 ppm in the spring blocks the agents had validated
on. Against the time-of-day profile, every agent had a skill of 0.71–0.73,
because CO2 depends on who happens to be in the room more than on the hour.

**T2 (chilled-water energy).** All agents reached a skill of 0.75–0.76
against persistence. Against the time-of-day profile, the stronger baseline
for this scheduled load, their skill was 0.65–0.67.

**With and without bemlops.** Within each task and model, the framework made
no consistent difference to accuracy (Table 16):
- T1 with Opus: the framework run was better by 1.4 ppm. The day-block
  bootstrap interval excludes zero.
- T1 with Sonnet: the framework run was worse by 1.8 ppm. The interval also
  excludes zero.
- T2: both differences were within 0.04 kWh, and both intervals include
  zero.

With one run per cell, these signs reflect run-to-run variation as much as
the condition.

**Table 16.** RMSE difference, agent + bemlops minus agent alone, for the same task and model (paired day-block bootstrap, 2,000 resamples).

<!-- table: pilot_pairs -->

**Self-reported error.** Every agent overestimated its own error. The ratio
of achieved to expected RMSE was 0.59–0.82: the agents were cautious, not
optimistic.

**What the agents found and built.** Table 17 summarises the manual audit.
- **Faults.** The agents found 7–8 of the 8 planted faults with or without
  the framework: 29 of 32 with it and 30 of 32 without. All T1 agents missed
  the three-day stuck ventilation meter, an input none of them used.
- **A fault we had not planted.** Every T2 agent found the dead chilled-water
  meter described in Section 5.2. They also found catch-up readings after
  communication losses. The framework's checks flagged neither.
- **Causality tests.** Seven of the eight agents wrote their own test that
  forecasts do not use later data. All four framework agents did, even though
  the framework already audits its own inputs.

**Table 17.** What each agent found and built, and what it cost (manual audit of the code and reports; usage counters of the agent runs).

<!-- table: pilot_audit -->

**Use of the framework.** Two of the four framework agents (both Sonnet) used
its checks but replaced its model with their own. One of them turned off the
framework's masking, judging it to look ahead, which it did in that version.
The other two (both Opus) kept a framework model but had to bend it:
- the T1 agent made it predict the change from the latest value, and moved
  the split so that training covered a new ventilation schedule;
- the T2 agent added its own known-ahead schedule and holiday inputs.

The four gave the same reasons: they could not add their own inputs or
models, there was no model of the change from the latest value, there was
only one test window, and persistence was the only reference for a scheduled
load. Their reports, and the defects they found, led to the changes in
Appendix A. Those changes were made before E1–E4 were run. The framework arm
of the pilot therefore used an earlier package version (git commit `5c575a6`)
than the case studies.

**Cost.** The framework arm used more tokens than the agent-alone arm in all
four pairs (5–52% more) and more tool calls in all four (32–89% more). It
took more time in three of the four (Table 17). We cannot say how much of
this came from the usability report that only the framework arm was asked
for, how much from reading the skill, and how much from working around the
earlier version's defects.
