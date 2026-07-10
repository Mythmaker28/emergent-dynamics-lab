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
