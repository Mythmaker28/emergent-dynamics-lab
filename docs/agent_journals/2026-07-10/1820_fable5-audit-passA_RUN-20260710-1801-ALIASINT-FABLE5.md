# Fable 5 Audit — PASS A (enrollment / tracker challenge)

- Auditor: Claude **Fable 5** (self-audit; no Opus 4.8, no subagent).
- Parent run: `RUN-20260710-1801-ALIASINT-FABLE5`.
- Target: `docs/experiments/ALIAS_INTERVENTION_COREV0_01_PROTOCOL.md` + `edlab/experiments/causal_intervention.py`.
- Question: **Can a positive "recovery" be manufactured by construction of the tracker, enrollment, or matching?**

## Objections raised and disposition

A1. *Enrollment could cherry-pick candidates.* — Enrollment reuses the EXACT frozen cross-cadence
    clean-long probe-positive eligibility (`audit_candidates` rule). It is not a new, looser rule. Verified by
    `test_enroll_reproduces_holdout04_disposition`: my independent implementation enrolls precisely law 0
    seeds {3002,3004} and law 52 seeds {3001,3003} and censors the rest — identical to the frozen HOLDOUT04
    disposition. First-eligible-endpoint-per-seed; deterministic tie-break (most observations then smallest
    track id). No visual selection. **Resolved.**

A2. *Following constituents by diagnostic IDs could smuggle IDs into the result.* — IDs are used ONLY to
    define the carrier readout (which detected entity holds the most of the original constituents). Physics,
    detection, and tracker association remain geometry/size only (`test_diagnostic_ids_never_affect_physics`
    passes: permuting IDs leaves every physical array bit-for-bit identical). carrier_P is measured against the
    frozen phenotype phi*, carrier_M is raw Jaccard; both are logged, not thresholded into a composite. **Resolved.**

A3. *Tracker greedy association could stitch a false continuity.* — The PRIMARY carrier readout is
    **tracker-independent**: it is per-snapshot detection + constituent-ID overlap, so the greedy centroid/size
    matcher cannot fabricate the primary signal. The tracker is run only to EXPOSE alias structure
    (births/ambiguous/split/merge, old-site look-alike), never to define recovery. This is a deliberate design
    strength: the alias we fear is tracker-induced, and the primary readout bypasses the tracker. **Resolved.**

A4. *Rigid translation makes short-term carrier persistence trivial (inertia).* — TRUE and important. Because
    the perturbation preserves internal geometry, the displaced blob is intact at t*+0, so carrier_P>0.8 for the
    first snapshots is near-automatic for ANY clump, individual or not. Therefore **absolute carrier persistence
    is NOT evidence of individuality.** The decision must be COMPARATIVE: PERTURBED carrier persistence must
    exceed the PLACEBO (a matched displaced non-candidate clump with identical inertia and identical new-site
    collision risk), AND the old site must not regenerate the phenotype. The protocol decision rule is written
    comparatively for exactly this reason. **Mitigated by design; folded into the frozen decision rule.**

A5. *Right-censoring / pseudoreplication.* — Seeds with no eligible endpoint before the horizon are recorded as
    censored (not deleted). One experimental unit per seed per law (first eligible endpoint). **Resolved.**

## PASS A verdict

The enrollment and matching cannot manufacture a positive because enrollment = the frozen rule, the primary
readout is tracker-independent, and the decision is comparative against a matched placebo. The one real hazard
— inertial persistence under rigid translation — is neutralized by requiring PERTURBED to exceed PLACEBO and by
treating old-site regeneration as an occupancy signature. **No blocking objection. Proceed after the decision
rule is stated comparatively (done in the frozen protocol).**
