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
