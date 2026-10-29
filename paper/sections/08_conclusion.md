## 8. Conclusion

Large language model agents can now write the code for a building prediction
model. Whether the result can be trusted in operation depends on what
surrounds that code. We divided the work: the agent provides the
generalization that messy, building-specific data demand, and domain
guardrails provide the guarantees that operation demands. The guarantees are:
- declarations checked against physics;
- causal cleaning and leakage-safe inputs;
- time-ordered evaluation against the strongest simple baseline;
- gated promotion, monitoring, champion/challenger retraining;
- a complete record.

On real buildings in three countries, the same workflow handled every kind of
target we tried: energy, thermal load, temperature, CO2, humidity, PM2.5,
people counts and occupancy. It kept the simple rule wherever a model could
not clearly beat it. Five measurements show what the guardrails change:
1. **Evaluation:** a random split, the protocol of our 2024 study, made errors
   look substantially smaller than they were.
2. **Faulty data:** with the guardrails, accuracy on faulty data matched clean
   data, while a quick unguarded script varied and was worse on average.
3. **Lifecycle:** over eight months, monitoring with gated retraining reduced
   monthly error by 10–33% against a model left alone.
4. **Pilot:** capable agents, told to be rigorous, built equally accurate and
   leak-free models with or without the framework. This places the
   framework's value in making rigour the default and the work auditable and
   maintainable, not in out-modeling a careful agent.
5. **Agents as testers:** the agents that used the framework found more of its
   defects than our own tests did.

Next steps are the full multi-agent benchmark with unprimed prompts,
cross-sensor consistency checks, conditional prediction intervals, metadata
from Brick models, and field deployment in an operating building.

## Data and code availability

All code, configurations, run records, case-study summaries and the pilot
benchmark are at
https://github.com/TensorBuildLab/MLOps-building-energy-and-environment-prediction
(BSD 3-Clause). The datasets are public: ROBOD (CC BY 4.0), the Aalborg offices
(CC BY 4.0) and BDG2 (CC BY-SA 4.0). They are downloaded and checksum-verified
by `case_studies/download.py`. Every result was produced by package version
0.2.0.dev0, and every run record carries the package's source fingerprint
(`f394d2e9ee9047c8` for all results reported here).

## Acknowledgements

The case studies, the pilot and parts of the software were carried out with
an LLM agent (Claude Opus 5.5, Anthropic) working under the authors'
direction. The pilot used independent instances of Claude Opus 5.5 and
Claude Sonnet 5.5. [Authors: confirm your review of the results here before submission.]
