# Numerical reconciliation

The machine-readable row-level table is `numerical_reconciliation.csv`. Every
headline number is classified as `UNCHANGED`, `CORRECTED`, or `WITHDRAWN`.

## Headline comparison

| Quantity | V4.0 | V4.1 original-world analysis | Class |
|---|---:|---:|---|
| h1 deep-turnover R² | 0.8878 | 0.6947 | CORRECTED |
| h1 deep interval | [0.8366, 0.9581] history bootstrap | descriptive world-fold t interval [0.0513, 1.3381] | WITHDRAWN |
| h1 threshold verdict | CERTIFIED | threshold not established | WITHDRAWN |
| h2 deep-turnover R² | -0.2394 | -1.1183 | CORRECTED |
| h2 threshold verdict | not established | not established | UNCHANGED |
| track survival | 36/36 | 36/36 recorded | UNCHANGED |
| recorded switches | 0 | 0 | UNCHANGED |
| mean deep M | 0.1902 | 0.1902 | UNCHANGED |
| deep records with M <= 0.25 | 94% | 34/36 | UNCHANGED |
| deep h1, longitudinal / largest | 0.8878 / 0.9123 | 0.6947 / 0.6706 | CORRECTED |
| common-recipient transplant h1 | 0.61 | 0.6468 | CORRECTED |
| inert / erased response decode | -0.19 / -0.19 | 0 / 0 | CORRECTED |
| in-place response difference h1 | 0.50 | 0.7039, W=2 only | CORRECTED |
| deep memory / size+mass | 0.93 / 0.64 | 0.7692 / 0.4538 | CORRECTED |
| local-storage interpretation | stated as droplet memory | no local-specific estimate | WITHDRAWN |
| fusion-free continuity | implicit | not independently reconstructable | WITHDRAWN |

## Why the V4 interval is withdrawn

V4 resampled 12 histories with replacement and assigned each duplicate draw a
new fold identifier. When an original history was drawn twice, exact copies of
the same seed-history rows could occur in both training and testing. Under the
fixed V4 seed, all 3,000 bootstrap replicates contained at least one duplicate;
none was leakage-free.

## V4.1 uncertainty

The longitudinal artifact has only three original worlds. V4.1 therefore
reports the three held-out-world scores directly:

- seed 38502: 0.7454;
- seed 38503: 0.4141;
- seed 38504: 0.9246.

Their pooled and mean score is 0.6947. The descriptive t interval is wide, and
the exact world-block percentile interval [0.4859, 0.8858] has only 27 ordered
resamples. Neither is treated as a reliable nominal 95% confidence interval.
Both fail to support a lower bound above the 0.50 qualification threshold.
