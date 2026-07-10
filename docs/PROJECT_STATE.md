# Project State

## CURRENT QUESTION

Can CORE V0 local particle laws produce auditable high phenotype continuity under low material retention, beyond tracker and static-flux artefacts?

## CURRENT SUBSTRATE

Periodic 2D Particle Dynamics / Particle Life-like dynamics.

## CURRENT CORE VERSION

`CORE V0`, code version `0.1.0`.

## VALIDATED COMPONENTS

- Repaired local implementation: 29 tests pass after independent numerical/tracker audit findings.
- Deterministic engine and multi-step diagnostic-ID permutation fixture.
- Scalar and independent vectorized force paths on 32 controlled worlds.
- Periodic detector, ID/order/translation-invariant phenotype fixtures.
- Geometry/size tracker with explicit lifecycle and ambiguity events; no P/M association gate.
- Separate P and M plus orthogonal construct fixtures.
- ID-permutation and static-material-flux nulls.
- Conservative scheduled-run lock semantics.
- Baseline 001's original all-green claim is superseded by independent audits; repaired gates await baseline 002.

Independent numerical and tracker audits completed with `REQUEST CHANGES` / `STOP-REPAIR`; their findings are implemented locally and await exact-SHA re-audit.

## ACTIVE EXPERIMENT

`PIPELINE-REPAIR-20260710-001` — code repaired; next is commit, independent re-audit, then `BASELINE-COREV0-20260710-002`.

## LAST COMPLETED EXPERIMENT

`BASELINE-COREV0-20260710-001` from commit `5fa941bf7c0b757f5535965fad62c190a94fefa6`: completed but superseded for candidate interpretation after independent audits. `HOLDOUT-COREV0-20260710-001` was never run.

## OBSERVED

- Native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` is ACTIVE at an exact 30-minute recurrence.
- New private GitHub repository `Mythmaker28/emergent-dynamics-lab` exists and is the `origin` remote.
- Historical local branch and commit exist; isolated historical tests: 19/19 pass.
- Archived historical CSV: 7,079 rows, Pearson `0.675724`, 0 rows for `P>0.8,M<0.5`.
- Current implementation tests: 20/20 pass.
- Current independent baseline: 36 runs, 36,722 repeated measurement rows, descriptive Pearson `r(P,M)=0.733162`, P range `0.287298–0.999985`, M range `0–1`.
- The unchanged initial probe contains 384 rows. Candidate audit finds 115 rows on clean tracks with at least eight observations and 20 physical endpoint pairs probe-positive under at least two cadences.
- The frozen cross-cadence/multi-seed rule selects laws `{1,3,6,10}` for fresh-seed hold-out.
- Independent numerical audit: nominal force agreement passed 10,000 fixtures, but the old vector norm failed at `r≈1e-158`; half-box reach and non-finite specs were unconstrained.
- Independent tracker audit: direct P/M/ID separation passed, but sparse look-alike alias, false split/merge semantics, incomplete edge logs, and stale death timestamps failed the stronger lineage/audit gate.
- First re-audit found one residual subnormal ordering error in the scalar force path; the reference now normalizes direction before multiplying magnitude, with a smallest-positive-subnormal regression test.
- Local post-fix validation: 1,024 force/one-step fixtures pass exactly and all 167 radii from `1e-158` through the minimum positive subnormal pass with zero path disagreement. Independent final numerical re-audit is still required.
- Repaired code uses `hypot`, finite/domain guards, force/one-step validation, full association-edge records, correct current timestamps, measurement interval flags, expanded tracker/detector sensitivity, and an explicit sparse-alias null.

## INFERRED

- The historical code is useful as audited reference behavior but its per-run P calibration and incomplete provenance should not be copied.
- The current tracker removes the historical hard dependency on shared IDs, reducing a central false-negative risk.
- Probe occupancy rises from `0.68%` at cadence 10 to `2.37%` at cadence 60, so sparse-observer effects remain a serious alternative explanation.

## OPEN HYPOTHESES

- CORE V0 may still couple loss of material to loss of morphology.
- Sparse snapshots or tracker thresholds may erase rare fast-turnover lineages.
- Density preference and orbital interactions may shift the joint P/M distribution if CORE V0 remains negative.

## KNOWN MEASUREMENT RISKS

- Tracker selection and ambiguous crossings.
- Connected-component bridge artefacts.
- P feature scaling and feature dominance.
- Repeated track/tau rows are pseudoreplicates, not independent trials.
- Right-censoring at the finite observation horizon.
- Static material-flux false positives.

## NEXT ACTION

Commit/push the repaired pipeline with both audit journals, obtain bounded independent re-audits of the exact SHA, then execute a new baseline ID. Do not run the superseded hold-out.

## DO NOT RESURRECT

- Historical Hopfield/CA claims or legacy memory scores.
- `theseus_score`, composite `memory_score`, or post-hoc threshold relaxation.
- Mutation, neighbor contagion/type transition, or particle recycling before the causal ladder authorizes them.
- Claims that the historical 7,079-row experiment was independently reproduced.
