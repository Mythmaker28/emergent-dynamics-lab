# EXP-RD-01 — Frozen Protocol: blind matched OPEN vs EXACT-CLOSED Gray-Scott map

Status: **FROZEN before screening.** Preregistered by `RUN-20260710-2345-EXPRD00B` (continuation). Authorized by
D-028 (open RD substrate qualified) and D-029 (temporal-feed-cohort tracer qualified and frozen).

## QUESTION
Do any open Gray-Scott regimes produce persistent organization with HIGH field P under LOW cohort field M
(persistence under CONTINUED constituent turnover), compared with the EXACT CLOSED limit?

## LAW PARAMETERIZATION (blind Halton, 4 dims)
`rd_law_from_halton(i)`: F in [0.010, 0.060], k in [0.040, 0.070], Du in [0.10, 0.20], Dv in [0.04, 0.10].

## MATCHED CONTROL — the EXACT CLOSED LIMIT
For each law, CLOSED = the SAME Du, Dv with **F = 0 and k = 0**: no feed, no removal, U+V conserved exactly. Same
seed, same tracer, same stack. This is the exact controlled limit of the substrate, not a separate model.

## FROZEN TRACER / P / M / THRESHOLDS
Tracer `TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250)` (D-029): rotating temporal feed cohorts, strictly
passive, exact partitions. Detector on V; frozen geometry LineageTracker; RD phenotype (geometry + open-system
rates production/removal/activity) with P = exp(-RMS dPhi) UNCHANGED; M = cohort mass Jaccard. Probe P>0.8, M<0.5
UNCHANGED. **No composite score. No visual selection. No threshold relaxation.**

## SAMPLING
24 laws x {CLOSED, OPEN} x 3 seeds {10001,10002,10003} = 144 runs. Steps 1500 at cadence 50 (within the tracer
cycle of 2000, so temporal cohorts do not wrap).

## GATE
Eligible (law, condition, seed) = a probe-positive endpoint on a clean (no split/merge/ambiguous) long (>=8 obs)
track. SCREENING PERMISSION at >= 2/3 seeds. Permission is NOT a candidate.

## FIVE EVIDENCE LEVELS (kept separate)
1 distributional shift (P, M, production/activity, tracks) | 2 screening signal (permitted laws) |
3 fresh-seed recurrence | 4 alias rejection | 5 causal re-establishment. Only 1-2 in this screen.

## MANDATORY DOWNSTREAM CHAIN FOR ANY SURVIVOR (frozen, unchanged)
frozen fresh-seed hold-out (>=2/5 unseen seeds) -> direct alias audit INCLUDING the imposed-pattern / occupancy
check (a structure that reappears at the OLD site after displacement is an externally maintained spatial slot, not
individuality; and the imposed-pattern negative control must be separated by the open-system rates) -> same-state
CONTROL/SHAM/PERTURBED/PLACEBO causal intervention **WITH the continued-turnover requirement** (a re-established
frozen lump is NOT a success) -> observer (cadence/tracker) sensitivity -> adversarial re-audit. Explicit
denominators, censored seeds, effect sizes and Wilson CIs.

## FALSIFIERS
F1 OPEN does not exceed CLOSED in permitted laws. F2 any OPEN permission is explained by fragmentation /
dissolution-reformation / imposed pattern / occupancy rather than continued-turnover individuality. F3 permitted
laws fail the fresh-seed hold-out. F4 survivors are alias-compatible. F5 observer artefact.
