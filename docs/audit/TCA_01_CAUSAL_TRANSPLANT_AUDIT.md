# TCA-01 — Causal / Transplant Claim Code-Path Audit

For each causal claim: does it depend on largest-component RESELECTION across a turnover trajectory?

| Claim | Code path | Uses turnover reselection? | Status |
|---|---|---|---|
| h1 causal transplant (Phase C, R_full 0.61) | `causal_runner.py`: donor = entity-MEAN from ONE post-history state (single `largest()` call), transplanted into a COMMON erased body B0; response read once | NO (single-timepoint donor + standardized common body; no trajectory) | UNAFFECTED |
| h1 in-place causal (0.50) | `causal_inplace.py`: full vs both-ablated on the SAME post-history state | NO (single timepoint) | UNAFFECTED |
| memory-inert necessity (collapse) | same state, coupling toggled | NO | UNAFFECTED |
| uptake-readout ablation (lam_plus→0) | single-timepoint engine variant | NO | UNAFFECTED |
| MCM order contrast (70×/73×) | mean-transplant into common body B0, single-timepoint memory | NO | UNAFFECTED |
| erase control (ablate-all→0) | single-timepoint | NO | UNAFFECTED |
| exact-clone ceiling | single-timepoint stochastic clones | NO | UNAFFECTED |
| h1 trivial-baseline (memory 0.93 vs size 0.64 @ deep) | checkpoint decode via `largest()` across turnover | YES (reselection) | QUALIFIED → conclusion holds: longitudinal h1=0.98 ≫ any body baseline |
| h1 deep-turnover survival (0.93) | checkpoint decode via `largest()` | YES (reselection) | REPLACED by longitudinal certification (0.98, CI[0.97,1.00], 100% survival) |
| old-material M / entity-size trajectory | `largest()` per checkpoint | YES | REPLACED by longitudinal (M continuous to 0.19, 100% survival) |
| h2 storage/turnover failure | checkpoint decode via `largest()` | YES | UNCHANGED under longitudinal (deep h2=0.34<0.5) |

Conclusion: every SINGLE-TIMEPOINT / COMMON-BODY causal & transplant claim is UNAFFECTED (they never tracked a
turnover trajectory). Only the TURNOVER-TRAJECTORY claims used reselection; those are re-certified longitudinally
(h1 PASS) or unchanged (h2 FAIL). No causal claim is invalidated.
