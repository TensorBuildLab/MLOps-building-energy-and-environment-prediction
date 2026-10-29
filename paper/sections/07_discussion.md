## 7. Discussion

### 7.1 What the division of labour buys

The checks did not replace judgment; they directed it. On the real data, every
judgment call the agent made was prompted by a specific warning, and every one
was settled with evidence that is now part of the record. Examples: a CO2
sensor floor, change-of-value logging recognised from the share of unchanged
steps, saturation of outdoor humidity, and gaps in camera counts. A fixed
pipeline would have had to either mask these stretches (and lose most
nights of CO2 data) or ignore stuck sensors (and train on a weather station that
repeated one value for 37 hours). An agent without checks would not have been
asked the question. The converse also held. Several warnings on real data
were wrong at first: stuck runs and spikes counted across gaps, and cloud
transients flagged as spikes. They were corrected in the package, with tests,
because the agent challenged them with evidence. The guardrails improved by
being used.

### 7.2 Choosing the baseline is a feature

In a substantial share of tasks the best model on validation data was a
baseline, and the framework deployed nothing more complex. Promotion gates
also refused models that beat persistence on validation but not on test. In
the 2024 setting, every task produced a model and a mean squared error,
with nothing to say whether that error was any good. A building operator
needs the opposite default: a model that does not clearly beat "same as an
hour ago" should not be deployed.

### 7.3 Limitations

- **One agent, which also built the package.** The case studies show the
  framework operated by an LLM agent; they do not measure how different
  agents, or agents without the framework, perform. That requires the
  multi-agent, multi-LLM benchmark with hidden test periods described in the
  repository (`benchmarks/`), which is the next study.
- **Public datasets.** All three datasets are public, documented and partly
  curated by their authors. Commercial BAS exports are messier. The
  fault-injection study mitigates this, but planted faults are simpler than
  real ones.
- **Short records.** ROBOD covers 29–47 weekdays per room, and Aalborg ten
  months. Effects of season are only partly visible, and test periods are
  short.
- **No weather forecasts.** Day-ahead tasks use measured weather up to the
  forecast time only. With forecasts declared as known in advance, accuracy
  would be higher.
- **Conventional models and point forecasts.** The framework's claims concern
  the process, not the model family. Probabilistic forecasts, deep and
  foundation models [Emami et al. 2023] are natural additions.
- **MLOps scope.** Feature stores and online serving endpoints are out of
  scope at single-building scale (Section 3.4).
- **Guideline 14.** Its criteria were written for measurement-and-verification
  baselines. We use them as a familiar reference for forecasts, not as a claim
  of compliance.

### 7.4 Implications

For researchers, the evaluation results argue that a random split should
not be accepted for building time series in any paper, and that results
should come with a no-skill baseline. For practitioners, the framework turns a
building-specific modeling project into a configuration that can be
reviewed, re-run, monitored and retrained. For agent developers, it suggests a
pattern beyond building data: let the agent write code freely, but route its
results through domain-specific checks that it cannot skip.
