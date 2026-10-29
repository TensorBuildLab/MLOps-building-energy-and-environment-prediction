| Task | Condition | Model | Planted faults found | Own causality test | Final model | Tokens (thousands) | Tool calls | Minutes |
|---|---|---|---|---|---|---|---|---|
| T1 | + bemlops | Opus | 7/8 | yes (check_causal.py) | bemlops gradient boosting on the change from the last value + own lagged inputs | 265 | 97 | 152 |
| T1 | + bemlops | Sonnet | 7/8 | yes (work/verify.py) | own (ExtraTrees on change from last value); bemlops used for checks | 279 | 179 | 60 |
| T1 | alone | Opus | 7/8 | yes (dev/leak_test.py) | own (gradient boosting on change from last value) | 174 | 57 | 70 |
| T1 | alone | Sonnet | 7/8 | yes (work/verify.py) | own (ExtraTrees + boosting on change from last value) | 228 | 136 | 57 |
| T2 | + bemlops | Opus | 8/8 | yes (test_predict.py; test_stress.py) | bemlops random forest + own known-ahead schedule and holiday inputs | 239 | 94 | 96 |
| T2 | + bemlops | Sonnet | 7/8 | yes (work/test_causal.py) | own (time-of-day profile + ridge); bemlops used for checks | 281 | 134 | 68 |
| T2 | alone | Opus | 8/8 | yes (dev_leak.py) | own (boosting + meter-fault rules) | 211 | 67 | 68 |
| T2 | alone | Sonnet | 8/8 | no (causality stated in docstring only) | own (time-of-day profile + ridge + rules) | 267 | 71 | 82 |
