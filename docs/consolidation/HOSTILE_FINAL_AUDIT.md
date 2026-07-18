# HOSTILE FINAL AUDIT

| # | objection | finding | disposition |
|---|---|---|---|
| 1 | Theorem tests had unexplained failures | resolved: 0 VALIDITY violations in 4000 trials; earlier rates were INFORMATIVENESS; all 14 refusals classified | resolved |
| 2 | Sign contracts came from ground truth (oracle) | **CONFIRMED**: all 8 point verdicts oracle-dependent; blind rerun → 0 points | **claim narrowed (C11 conditional)** |
| 3 | The 10-case prospective is too small to establish safety | **CONFIRMED**: N=2000 stratified hold-out found 541 invalid sets the 10-case run never saw | **claim C12 WITHDRAWN** |
| 4 | Instrument was patched on the hold-out | NO — `signsafe.py` hash-gated throughout; only the *harness* was corrected (documented erratum); failure preserved | resolved |
| 5 | Post-freeze modification | none: freeze 09016d7 verified before and after the hold-out | resolved |
| 6 | Docker/CI never actually run | **CONFIRMED** — no container runtime; Dockerfile unbuilt | **publication-blocking** |
| 7 | FHN quantitative inflation | Track A adopted; quantitative claim explicitly ctrans-specific | narrowed |
| 8 | Suppressed failed cases | all 2000 hold-out rows preserved in HOLDOUT_RESULTS.json incl. failures | resolved |
| 9 | Dependence in Monte-Carlo trials | moot — the primary endpoint FAILED outright; no CI needed to reject | n/a |
| 10 | Duplicated evidence as independent | second impl (replicate2) is numpy-only and agrees on status class only | resolved |

## Publication-blocking items
1. **The instrument fails its own primary safety endpoint at low SNR** (null-gate misfire). Until repaired on new
   development data and validated on a **fresh** hold-out, no safety claim can be made.
2. Docker/CI clean reproduction never executed.
3. No external human review.
