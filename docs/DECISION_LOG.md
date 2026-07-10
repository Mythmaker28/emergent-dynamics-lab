# Decision Log

## D-001 — Autonomous repository instead of migration

**Date:** 2026-07-10  
**Decision:** Create a clean private `Mythmaker28/emergent-dynamics-lab` history. Treat `ising-life-lab` and local `9992e6c` as read-only reference.  
**Reason:** Preserve provenance and prevent legacy multi-domain claims or artefacts from silently entering the new protocol.

## D-002 — Exact 30-minute native heartbeat

**Date:** 2026-07-10  
**Decision:** Use native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` at 30-minute recurrence, not the obsolete one-hour line and not a custom daemon.  
**Reason:** Explicit user correction and native sub-hour continuation support.

## D-003 — Conservative explicit overlap lock

**Date:** 2026-07-10  
**Decision:** Use an atomic JSON lock that is never cleared by age alone and can only be released by its run ID.  
**Reason:** Native heartbeat overlap is not documented as a hard guarantee; experiments may legitimately exceed 30 minutes.

## D-004 — Tracker association is separate from evaluated P and M

**Date:** 2026-07-10  
**Decision:** Associate detections using periodic centroid distance and size ratio only. IDs/Jaccard M and final phenotype P are forbidden from association gates. Log all alternatives and explicit ambiguity.  
**Reason:** Avoid manufacturing high P or suppressing low M through correspondence selection; preserve orthogonal falsification fixtures.

## D-005 — Fixed dimensionless phenotype normalization

**Date:** 2026-07-10  
**Decision:** Use committed physical normalization scales rather than z-scoring and recalibrating P separately for each run.  
**Reason:** Historical per-run calibration made cross-run comparability uncertain.

## D-006 — Halton screening sampler

**Date:** 2026-07-10  
**Decision:** Use a deterministic Halton low-discrepancy sequence (skip 32) for the current baseline and eligible EXP02 sampling.  
**Reason:** It is a justified quasi-random design with no SciPy dependency and fully deterministic mapping to LawSpec.

## D-007 — Frozen same-endpoint, cross-cadence fresh-seed gate

**Date:** 2026-07-10

**Decision:** Hold out laws 1, 3, 6, and 10 using the exact rule in `docs/experiments/HOLDOUT_COREV0_01_PROTOCOL.md`, then retain only laws qualifying in at least two of five fresh seeds.

**Reason:** The baseline probe is populated but heavily pseudoreplicated and partly lineage-complex. Requiring clean long tracks, identical physical endpoints under multiple cadences, multiple screening seeds, and fresh-seed survival tests robustness without changing P/M thresholds. The count is not a probability estimate.

## D-008 — Stop hold-out and supersede candidate interpretation after independent audits

**Date:** 2026-07-10

**Decision:** Do not execute `HOLDOUT-COREV0-20260710-001`. Preserve baseline 001 as a technical exploratory artefact, but supersede its candidate selection. Repair numerical domain checks and lineage auditability, then run a new baseline under a new experiment ID.

**Reason:** Independent audits found (a) vector norm underflow for subnormal separations, (b) a non-unique periodic direction when reach meets half the box, (c) non-finite specs accepted, (d) compatibility alternatives mislabeled as split/merge, (e) stale disappearance timestamps, (f) incomplete candidate-edge persistence, and (g) a sparse look-alike exchange that yields clean `P=1,M=0` without a competing spatial edge. Proceeding would turn a known measurement failure into a narrative candidate.

**Repair:** Use scale-stable `hypot`; require all relevant reaches below half the box; reject non-finite specs; validate forces and one-step states; distinguish unique split/merge from many-to-many ambiguity; persist every accepted/rejected association edge; flag complex measurement intervals; extend tracker/detector sensitivity; keep the sparse alias as an explicit live unresolved null.

**Interpretation boundary:** A repaired diagnostic hold-out may later test reproducibility, but no survivor can be promoted scientifically without direct trajectory audit and an intervention that rejects static occupancy/look-alike flux.

## D-009 — Normalize pair direction before multiplying force magnitude

**Date:** 2026-07-10

**Decision:** In the scalar reference path, compute `magnitude*(dx/distance)` rather than `magnitude*dx/distance`.

**Reason:** Exact-SHA re-audit showed that `hypot` fixed distance underflow but the old multiplication order still quantized subnormal displacements, first failing at `1e-315` and reaching a 0.3 force error at the smallest positive float64. The new order agrees with the vector path across the full tested subnormal range and preserves the same nominal formula.

## D-010 — Invalidate hold-out 002 after clean-cadence join bug

**Date:** 2026-07-10

**Decision:** Preserve but invalidate `HOLDOUT-COREV0-20260710-002`. Correct the audit so every cadence contributing to same-endpoint consistency must itself be a clean long track. Freeze hold-out 003 with law 3 only and five unseen seeds.

**Reason:** The old join counted all probe-positive cadences first, then applied cleanliness only to the current row. This could label an endpoint cross-cadence-consistent when the corroborating cadence was complex. The corrected baseline rule selects law 3 only. Reusing results for the other laws or keeping the old selection would be post-hoc narrative rescue.

## D-011 — Reject baseline law 3 and advance to broad EXP02

**Date:** 2026-07-10

**Decision:** Reject law 3 for perturbation preparation because only one of five unseen seeds passes the frozen corrected gate, below the required two. Start no alternative baseline-law hold-out; proceed to the 300-law EXP02 regime map after implementing streaming storage.

**Reason:** Substituting another law from invalidated hold-out 002 or relaxing cross-cadence cleanliness would be post-hoc rescue. A negative 12-law path does not justify changing substrate because EXP02 and EXP03-A/B/C remain required.

## D-012 — Immutable run shards and last-published COMPLETE manifest for EXP02

**Date:** 2026-07-10

**Decision:** Store each `(law_index, seed)` as one immutable directory containing the four unchanged CSV tables and a per-run manifest. Publish that directory by same-parent atomic rename only after files and manifest are flushed. Quarantine any unpublished temporary directory after an interrupted process. Publish derived outputs atomically and `manifest.json` last with `status=COMPLETE` only after all 900 planned shards, row counts, indexes, hashes, and derived outputs verify.

**Reason:** Run-level shards bound memory to one simulation, make completed work independently verifiable, and avoid ambiguous append/truncate recovery. The projected few thousand local files are acceptable relative to the stronger fail-closed semantics. Byte-equivalence fixtures confirm that storage changed without changing trajectories, detection, tracking, P, or M.

**Falsification / rollback:** Any partial final shard, duplicate/lost run, accepted corruption, row/index inconsistency, premature `COMPLETE` manifest, or non-idempotent resume blocks EXP02. A real subprocess exit is injected after shard fsync and before publication to exercise this boundary on Windows.

## D-013 — Canonical lag keys use integer step deltas, not float equality

**Date:** 2026-07-10

**Decision:** Group all downstream cadence/lag analysis by `(snapshot_cadence, end_step-start_step)` and derive `lag_snapshots` and displayed `tau` from the integer step delta and frozen `dt`. Preserve the original EXP02 `measurement_aggregates.csv` and explicitly mark its float-string fragmentation; generate a separate corrected aggregate rather than silently rewriting the parent artefact.

**Reason:** Independent statistical QA found that mathematically identical `tau` values had multiple binary float strings, fragmenting 7,280 logical groups into 36,937 rows. Raw start/end steps, all row totals, P/M values, hashes, and scientific trajectories remain intact, so a raw rerun is neither necessary nor justified.

**Falsification:** Corrected integer-delta groups must reproduce all 648,740 rows, exactly nine global cadence/lag cells, and the independent per-cell counts. Any mismatch invalidates the corrected analysis.

## D-014 — Freeze all nine EXP02-eligible laws for one five-seed diagnostic hold-out

**Date:** 2026-07-10

**Decision:** Run laws `{0,12,35,52,73,94,209,225,298}` on unseen seeds `{3001,3002,3003,3004,3005}` with unchanged CORE V0 settings and the corrected whole-track-clean, same-endpoint cross-cadence gate. Retain a law only at `>=2/5` fresh seeds. Include all nine eligible laws; do not rank or filter them by raw probe rate or observational motion metrics.

**Reason:** Each law passed the frozen EXP02 `>=2/3` screening permission gate. Direct diagnostics reproduce P/M exactly and show no hidden compatible edge, but cannot reject static occupancy/look-alike alias. A common fresh-seed gate tests recurrence without narratively selecting attractive examples.

**Interpretation boundary:** Survival is diagnostic only and authorizes an intervention design; it is not a probability estimate or evidence of individuality. Failure is negative and cannot be rescued by a replacement law or relaxed threshold.

## D-015 — Freeze HOLDOUT04 survivors `{0,52}` for alias-rejecting intervention design

**Date:** 2026-07-10

**Decision:** Retain only laws `{0,52}` for `ALIAS-INTERVENTION-COREV0-20260710-001`. Law 0 qualifies in fresh seeds `{3002,3004}` and law 52 in `{3001,3003}` under the preregistered `>=2/5` gate. Reject laws `{12,35,73,94,209,225,298}` without replacement. Require an exact sham and a causal endpoint that can reject stationary spatial occupancy or sparse look-alike flux before any perturbation-recovery interpretation.

**Reason:** The 45-run hold-out used unseen seeds and unchanged thresholds, observer settings, tracker logic, laws, and simulation horizon. Recurrence passed for two laws, but every qualifying row still carries the mandatory alias null. Freezing the survivor set now prevents post-hoc ranking by motion, probe abundance, or visual appeal.

**Interpretation boundary:** `2/5` is a diagnostic recurrence gate, not a probability estimate. Laws 0 and 52 are not promoted scientific candidates by this decision. Any intervention implementation must preserve diagnostic-ID independence, keep P and M separate, and pass no-op/sham plus validated-reference controls before execution.

## D-016 — Correct the ALIAS-INTERVENTION readout to follow the displaced set and use robust re-establishment

**Date:** 2026-07-10 (RUN-20260710-1801-ALIASINT-FABLE5, Fable 5)

**Decision:** Before committing any causal result, self-review found two readout bugs in the first harness
implementation (both in derived measurement only; physics, enrollment, branches, and the frozen protocol design
were unaffected): (a) the PLACEBO branch followed the candidate constituents `C`, but in the placebo branch `C`
is not displaced (a matched non-candidate clump `C'` is), so placebo persistence wrongly measured the in-place
candidate; (b) `carrier_persist_consecutive` counted from the first post snapshot and was reset to zero by the
brief, expected post-displacement transient dip. Corrected: each branch follows the set it actually displaced
(candidate for control/sham/perturbed; `C'` for placebo), measured against that set's own reference phenotype
and its own origin/home site, with a robust late-window re-establishment metric. This makes the implementation
faithful to the already-frozen protocol decision rule (baf1fca §8–9: "PERTURBED must exceed PLACEBO; old site
does not regenerate"). Additionally, genuine "individuality under constituent turnover" is scored only when the
displaced candidate re-establishes phenotype **while** its material retention is not ~1.0 (a rigid cohesive
cluster translating with M→1.0 is trivial translation-covariance, not the target phenomenon).

**Reason:** The uncorrected placebo comparison was meaningless and the consecutive metric was fragile; both were
caught in self-review before any results were committed (no committed artefact is invalidated). The correction is
more conservative and matches the frozen preregistration, in the spirit of D-010/D-013.

**Falsification:** the corrected harness must still pass every validation gate (sham==control bit-for-bit,
conservation, off-site displacement, IDs-not-in-physics, determinism, HOLDOUT04 reproduction): 46/46 tests pass.
