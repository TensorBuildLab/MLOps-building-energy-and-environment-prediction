| Task | Condition | Model | Ran | RMSE | Persistence RMSE | Skill vs persistence | Profile RMSE | Skill vs profile | Self-reported RMSE | Achieved / self-reported | Leakage test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | agent + bemlops | Opus | yes | 19.7 | 20.9 | 0.058 | 73.7 | 0.732 | 27 | 0.731 | 0/15 changed |
| T1 | agent + bemlops | Sonnet | yes | 21.7 | 20.9 | -0.037 | 73.7 | 0.705 | 35 | 0.621 | 0/15 changed |
| T1 | agent alone | Opus | yes | 21.2 | 20.9 | -0.011 | 73.7 | 0.713 | 26 | 0.815 | 0/15 changed |
| T1 | agent alone | Sonnet | yes | 19.9 | 20.9 | 0.049 | 73.7 | 0.730 | 34 | 0.586 | 0/15 changed |
| T2 | agent + bemlops | Opus | yes | 0.538 | 2.24 | 0.760 | 0.664 | 0.190 | 0.8 | 0.673 | 0/15 changed |
| T2 | agent + bemlops | Sonnet | yes | 0.559 | 2.24 | 0.750 | 0.664 | 0.159 | 0.85 | 0.657 | 0/15 changed |
| T2 | agent alone | Opus | yes | 0.559 | 2.24 | 0.750 | 0.664 | 0.159 | 0.85 | 0.658 | 0/15 changed |
| T2 | agent alone | Sonnet | yes | 0.526 | 2.24 | 0.765 | 0.664 | 0.208 | 0.8 | 0.658 | 0/15 changed |
