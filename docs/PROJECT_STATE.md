# Project State

## CURRENT QUESTION

Can CORE V0 local particle laws produce auditable high phenotype continuity under low material retention, beyond tracker and static-flux artefacts?

## CURRENT SUBSTRATE

Periodic 2D Particle Dynamics / Particle Life-like dynamics.

## CURRENT CORE VERSION

`CORE V0`, code version `0.1.0`.

## VALIDATED COMPONENTS

- Local implementation: 20 tests passed before the first repository commit.
- Deterministic engine and multi-step diagnostic-ID permutation fixture.
- Scalar and independent vectorized force paths on 32 controlled worlds.
- Periodic detector, ID/order/translation-invariant phenotype fixtures.
- Geometry/size tracker with explicit lifecycle and ambiguity events; no P/M association gate.
- Separate P and M plus orthogonal construct fixtures.
- ID-permutation and static-material-flux nulls.
- Conservative scheduled-run lock semantics.
- Current independent baseline: every first kill-switch gate green.

Independent post-implementation numerical and tracker audits are active and not yet integrated.

## ACTIVE EXPERIMENT

`HOLDOUT-COREV0-20260710-001` — protocol frozen before fresh-seed execution; laws `{1,3,6,10}`, seeds `{404,505,606,707,808}`.

## LAST COMPLETED EXPERIMENT

`BASELINE-COREV0-20260710-001` from commit `5fa941bf7c0b757f5535965fad62c190a94fefa6`: 12 laws × 3 seeds, 36 runs, 600 steps, cadences 10/30/60.

## OBSERVED

- Native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` is ACTIVE at an exact 30-minute recurrence.
- New private GitHub repository `Mythmaker28/emergent-dynamics-lab` exists and is the `origin` remote.
- Historical local branch and commit exist; isolated historical tests: 19/19 pass.
- Archived historical CSV: 7,079 rows, Pearson `0.675724`, 0 rows for `P>0.8,M<0.5`.
- Current implementation tests: 20/20 pass.
- Current independent baseline: 36 runs, 36,722 repeated measurement rows, descriptive Pearson `r(P,M)=0.733162`, P range `0.287298–0.999985`, M range `0–1`.
- The unchanged initial probe contains 384 rows. Candidate audit finds 115 rows on clean tracks with at least eight observations and 20 physical endpoint pairs probe-positive under at least two cadences.
- The frozen cross-cadence/multi-seed rule selects laws `{1,3,6,10}` for fresh-seed hold-out.

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

Commit/push the baseline and frozen hold-out protocol, reproduce the candidate audit from its committed code, then execute the 20 fresh-seed hold-out runs without changing thresholds or tracker settings.

## DO NOT RESURRECT

- Historical Hopfield/CA claims or legacy memory scores.
- `theseus_score`, composite `memory_score`, or post-hoc threshold relaxation.
- Mutation, neighbor contagion/type transition, or particle recycling before the causal ladder authorizes them.
- Claims that the historical 7,079-row experiment was independently reproduced.
