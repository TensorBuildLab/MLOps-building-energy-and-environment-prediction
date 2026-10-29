# Paper

**Where domain guardrails matter for LLM-agent-built prediction models in buildings:
an open MLOps framework evaluated on real data** (draft, version 2 of arXiv:2407.03469).

- [`manuscript.md`](manuscript.md): the assembled draft (generated; do not edit by hand).
- `sections/`: the sections, edited by hand.
- `tables/`, `figures/`: generated from the results by `case_studies/make_results.py` and
  `paper/figure_framework.py`. Every number in the text comes from these tables or from the
  result files in `case_studies/` and `benchmarks/pilot/`.
- `references.md`: the reference list, checked against Crossref, arXiv or the publisher.

Rebuild everything after the case studies have run:

```bash
python case_studies/stats.py           # Diebold-Mariano tests, pilot statistics
python case_studies/make_results.py    # tables and figures
python paper/figure_framework.py       # Figure 1
python paper/build.py                  # paper/manuscript.md
```

## What changed from v1 (2024)

| v1 | v2 |
|---|---|
| Random train/test split on time series | Time-ordered split with a horizon gap; random-split error measured as a protocol comparison (RQ2) |
| Feature selection on the full dataset | Inputs shifted by the horizon and audited; selection effect measured |
| "Accuracy" = code runs without error | Skill against the strongest no-ML baseline, tests of the difference, promotion gates |
| One simulated building, energy only | 92 tasks in 3 public real-building datasets (energy, thermal load, temperature, CO2, humidity, PM2.5, occupancy), including a 20-building portfolio |
| No deployment | Registry, monitoring, gated retraining over eight months (RQ4) |
| One LLM, results in chat links | Independent Claude Opus 5.5 and Sonnet 5.5 agents with and without the framework; prompts, deliverables and scores in the repository (RQ5) |

## Before submission (authors)

- Confirm the author list, affiliations and the Acknowledgements.
- Choose the venue and run its author guidelines (highlights, abstract length, declarations).
- Tag a release and archive it on Zenodo; put the DOI in the data-availability statement.
