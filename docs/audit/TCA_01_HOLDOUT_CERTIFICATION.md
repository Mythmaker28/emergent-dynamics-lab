# TCA-01 — Longitudinal Holdout Certification

Frozen longitudinal tracker (spec: TCA_01_TRACKER_SPEC.md; uses only geometric overlap, never h1/h2/M/labels).
Holdout = **untouched sealed seeds 38502/38503/38504** (seed 38501 was the incident/development seed and is
EXCLUDED as primary). 12 sealed histories × 3 seeds = 36 tracks. Executed once. Raw: results/observer/tca_holdout_raw.pkl.

## Track survival
- 36/36 tracks survived to step 800 (0 lost, 0 censored, 0 ambiguous, **0 reassignment switches**).
- M reached: step 650 mean M=0.25 (61% of tracks ≤0.25); step 800 mean M=0.19 (94% ≤0.25, min 0.14).
- So a continuously tracked entity reaches deep turnover (M≤0.25) with full survival.

## h1 (grouped leave-history-out, 95% bootstrap CI)
- init (M~1.00): h1 = 0.92, CI [0.86, 0.99].
- **deep (M~0.19): h1 = 0.98, CI [0.97, 1.00]** → lower bound 0.97 ≫ 0.50 and > 0. **CERTIFIED.**

## h2 (longitudinal, recomputed)
- init 0.78; **deep 0.34** (< 0.50). The h2 negative result is UNCHANGED under the corrected tracker; the
  previously visible h2 discontinuity was the largest-reselection artefact (largest-deep h2 = −0.18), but even
  the clean longitudinal h2 fails the 0.50 gate. **h2 negative result: unchanged.**

## Sensitivity table (deep, step 800)
| tracker | h1 | h2 | mean M | switches |
|---|---|---|---|---|
| longitudinal (corrected) | 0.98 | 0.34 | 0.19 | 0 |
| largest-at-each-frame (historical) | 0.96 | −0.18 | 0.15 | (5 on seed 38501) |

h1 is tracker-independent because the imposed history is GLOBAL (written similarly into many blobs); this is
NOT evidence of individual memory. h2 is < 0.50 under either tracker.

## Verdict
h1 longitudinal holdout: **PASS** (deep R²=0.98, CI [0.97,1.00], 100% survival, untouched seeds).
h2: negative result confirmed under longitudinal tracking. Individual memory: NOT established.
