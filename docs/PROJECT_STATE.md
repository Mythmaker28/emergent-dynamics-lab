# Project State

## CURRENT QUESTION

Can CORE V0 local particle laws produce auditable high phenotype continuity under low material retention, beyond tracker and static-flux artefacts?

## CURRENT SUBSTRATE

Periodic 2D Particle Dynamics / Particle Life-like dynamics.

## CURRENT CORE VERSION

`CORE V0`, code version `0.1.0`.

## VALIDATED COMPONENTS

- Repaired implementation plus the local EXP02 shard writer: 35 tests pass.
- Deterministic engine and multi-step diagnostic-ID permutation fixture.
- Scalar and independent vectorized force paths on 32 controlled worlds.
- Periodic detector, ID/order/translation-invariant phenotype fixtures.
- Geometry/size tracker with explicit lifecycle and ambiguity events; no P/M association gate.
- Separate P and M plus orthogonal construct fixtures.
- ID-permutation and static-material-flux nulls.
- Conservative scheduled-run lock semantics.
- Baseline 001's original all-green claim is superseded by independent audits; repaired baseline 002 and hold-out 003 are complete.
- Exact-SHA numerical re-audit `NUM3` passed all 29 then-current tests, 1,024 force/one-step fixtures, and 167 subnormal radii.
- EXP02 per-run shards are written through temporary directories and atomic rename, pinned to a plan hash, verified by SHA-256/size on resume, and summarized without retaining all runs in memory.
- The streaming fixture proves byte-for-byte equality of all four raw tables against the full runner, rejects plan drift/corruption, and resumes without recomputation.
- Recovery fault injection includes a real child-process `os._exit(73)` after shard fsync and before atomic publication; restart quarantines the unpublished directory and converges to one verified result.
- Final derived files are atomically published, `manifest.json` is last, and `COMPLETE` requires all planned identities, hashes, sizes, actual CSV row counts, raw-index/summary consistency, and an exact reproduction command.

## ACTIVE EXPERIMENT

`EXP02-COREV0-20260710-001` — COMPLETE and analyzed: 900/900 runs at launch SHA `6c59378`, chunk-aware analysis SHA `a2f536f`. Independent and primary calculations agree exactly on integrity, statistics, censoring, and nine eligible laws. Direct candidate diagnostics remain required before freezing the fresh-seed hold-out.

## LAST COMPLETED EXPERIMENT

`HOLDOUT-COREV0-20260710-003`: five unseen seeds for law 3; completed negative under the corrected frozen gate (one qualifying seed, required at least two).

## OBSERVED

- Native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` is ACTIVE at an exact 30-minute recurrence.
- New private GitHub repository `Mythmaker28/emergent-dynamics-lab` exists and is the `origin` remote.
- Historical local branch and commit exist; isolated historical tests: 19/19 pass.
- Archived historical CSV: 7,079 rows, Pearson `0.675724`, 0 rows for `P>0.8,M<0.5`.
- Current implementation tests: 35/35 pass.
- Current independent baseline: 36 runs, 36,722 repeated measurement rows, descriptive Pearson `r(P,M)=0.733162`, P range `0.287298–0.999985`, M range `0–1`.
- The unchanged initial probe contains 384 rows. Candidate audit finds 115 rows on clean tracks with at least eight observations and 20 physical endpoint pairs probe-positive under at least two cadences.
- The frozen cross-cadence/multi-seed rule selects laws `{1,3,6,10}` for fresh-seed hold-out.
- Independent numerical audit: nominal force agreement passed 10,000 fixtures, but the old vector norm failed at `r≈1e-158`; half-box reach and non-finite specs were unconstrained.
- Independent tracker audit: direct P/M/ID separation passed, but sparse look-alike alias, false split/merge semantics, incomplete edge logs, and stale death timestamps failed the stronger lineage/audit gate.
- First re-audit found one residual subnormal ordering error in the scalar force path; the reference now normalizes direction before multiplying magnitude, with a smallest-positive-subnormal regression test.
- Local post-fix validation: 1,024 force/one-step fixtures pass exactly and all 167 radii from `1e-158` through the minimum positive subnormal pass with zero path disagreement. Independent final numerical re-audit is still required.
- Repaired code uses `hypot`, finite/domain guards, force/one-step validation, full association-edge records, correct current timestamps, measurement interval flags, expanded tracker/detector sensitivity, and an explicit sparse-alias null.
- Final independent numerical re-audit `NUM3`: PASS exact; 29 tests, 1,024 fixtures, and 167 subnormal radii all pass.
- Repaired baseline 002 preserves 36,722 measurements, descriptive `r(P,M)=0.733162`, and 384 raw probe rows; 230 rows lack logged ambiguity/split/merge inside their interval, but all 384 retain unresolved alias risk.
- Candidate-audit join bug found after hold-out 002: corroborating cadences were not always independently clean. Hold-out 002 is invalidated with no accepted disposition.
- Corrected baseline selection yields only law 3, supported by screening seeds 101 and 303.
- Corrected hold-out 003: 5 runs, 5,885 repeated measurement rows, 30 raw probe rows; only seed 909 satisfies the clean-long cross-cadence endpoint rule. Frozen gate fails 1/5 < 2/5.
- EXP02: 648,740 measurements, descriptive `r(P,M)=0.731581`, 10,302 unchanged-probe rows, 7,186 interval-complexity-unflagged rows, 2,400 whole-track clean-long rows, and 94 same-endpoint cross-cadence endpoints.
- Independent candidate audit finds exactly nine laws eligible in two of three screening seeds: `{0,12,35,52,73,94,209,225,298}`. None qualifies in all three; all retain sparse-alias/static-flux risk and none is promoted.
- Independent statistical QA verified all 3,600 raw CSV hashes/sizes/row counts and found 10,101/86,573 tracks (11.67%) censored at time 12.
- The parent `measurement_aggregates.csv` fragmented nominally equal float `tau` keys. Raw data are intact; D-013 requires a separate integer-step corrected aggregate and preserves the flawed parent file unchanged.

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
- EXP02 raw shards are intentionally local/ignored; committed indexes and checksums prove integrity of present files but are not a remote raw-data backup.
- Crash recovery is fail-closed for missing, mismatched, or corrupt completed shards. Directory metadata fsync is not portable on this Windows path, so post-crash re-verification remains the durability boundary.

## NEXT ACTION

Compute direct descriptor/centroid/material-turnover/association-edge diagnostics for all 199 cross-cadence rows of the nine eligible laws, without inventing a post-hoc exclusion threshold. If source integrity remains green, freeze a five-unseen-seed hold-out for all nine laws under the unchanged gate; any survivor remains alias-unresolved pending intervention.

## DO NOT RESURRECT

- Historical Hopfield/CA claims or legacy memory scores.
- `theseus_score`, composite `memory_score`, or post-hoc threshold relaxation.
- Mutation, neighbor contagion/type transition, or particle recycling before the causal ladder authorizes them.
- Claims that the historical 7,079-row experiment was independently reproduced.
