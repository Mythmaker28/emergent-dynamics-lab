# EXP-REF-01 — Frozen Protocol: tracer-labeled dynamical reference benchmark (measurement positive control)

Status: **FROZEN.** Preregistered by `RUN-20260710-2015-EXPREF01`. Decision rule is user-specified. Gate that
must be resolved BEFORE any Particle Dynamics substrate decision (D-017..D-020 are all negative).

## QUESTION
Can the FROZEN detector/tracker/P/M stack (a) recognize a KNOWN persistent dissipative organization under
constituent turnover, and (b) separate it from the existing static-flux null? This is a POSITIVE CONTROL for the
measurement: it asks whether the observers can see persistent organization when it is present by construction, so
that the EXP03 negatives can be attributed to the substrate rather than to measurement blindness.

## REFERENCE (known persistent dissipative organization under turnover)
A stationary rotating packet: K=10 particles on a ring (radius 0.045) about a fixed centre, rotating at omega=2.0
rad/unit so each has a real tangential velocity (-> internal circulation and velocity dispersion). Membership
turns over gradually: the K ring slots are filled from a 20-ID pool whose window shifts by one ID per snapshot, so
constituents cycle out/in while the packet's shape and motion persist. The remaining 54 particles form a dilute
background grid (spacing 0.12 > connection_radius 0.11) that forms no component. Scripted kinematically over
steps 0..600 (snapshot cadence 10). "Dissipative" in the sense of a non-equilibrium structure maintained under
throughput (constituent turnover), not a closed conservative system.

## STATIC-FLUX NULL (matched)
The identical packet with rotation OFF (omega=0) and zero velocity, same gradual membership turnover — i.e. the
frozen STATIC_MOTIF_WITH_MATERIAL_FLUX regime (fixed morphology, fresh constituents, zero velocity).

## PASSIVE TRACERS / NO P RECALIBRATION
Positions are scripted, so diagnostic ID labels cannot affect the (scripted) dynamics; by the frozen
ParticleState/detector/tracker invariant they never affect detection/tracking/phenotype, only the ID-based M. P is
the frozen `phenotype_similarity` with `PhenotypeSpec(0.11,0.25)`; it is NOT recalibrated to make the reference
pass. Detector `DetectionSpec(0.11,4)`, tracker `TrackerSpec(0.16,0.25)` frozen.

## PRE-DECLARED METRICS (frozen observables only)
Per input (reference, null): single-entity detection, continuous track length, P range on the main track, minimum
M on the main track, probe-positive (P>0.8, M<0.5) row count and lags, and the packet phenotype's mean
|internal_circulation|, mean velocity_dispersion, mean |center_velocity|.

## DECISION RULE (user-specified; pre-declared)
- **RECOGNIZED** iff the reference is detected as a single continuous track with P>0.8 and at least one
  probe-positive endpoint (P>0.8, M<0.5) at some lag (persistence recognized under turnover).
- **SEPARATED** iff the reference's frozen dynamical observables exceed the static-flux null's by a decisive
  margin: reference mean |circulation| > 0.02 AND mean velocity_dispersion > 0.02, while the static-flux null has
  both < 1e-6 (the null is zero-velocity by construction). (Raw P/M are expected to be identical for both, which
  alone does not separate them — the separation must come from the frozen dynamical observables.)
- **VERDICT:**
  - If RECOGNIZED AND SEPARATED -> the frozen measurement stack is adequate to detect a persistent dissipative
    organization and to distinguish it from static flux; the EXP03 negatives are SUBSTRATE results. Formally
    RETIRE Particle Dynamics for the current question and propose the next substrate, with **Flow-Lenia as a
    candidate (not an assumption)**.
  - If NOT RECOGNIZED (or NOT SEPARATED) -> the measurement is blind to real organization; STOP substrate
    switching and AUDIT the measurement stack.

## HONEST SCOPE CAVEAT (pre-declared, does not change the verdict)
Separation here is against the ZERO-VELOCITY static-flux null. The harder sparse-look-alike / spatial-occupancy
alias in which replacement particles carry matched velocities is NOT resolvable by observers alone (that is why
the same-state matched-branch causal intervention exists). EXP-REF-01 tests observer adequacy for recognising
persistent dissipative organization vs the static-flux null, exactly as specified; it does not claim observers
resolve the flowing-occupancy alias.

## FALSIFIERS
- F1: reference not detected / not a single continuous track / P not high -> observers cannot represent the
  organization -> NOT RECOGNIZED.
- F2: reference dynamical observables do not exceed the null -> observers cannot separate real organization from
  static flux -> NOT SEPARATED.

## VALIDATION / REPRODUCTION
`pytest tests/test_exp_ref_01.py`; run via `edlab.experiments.exp_ref_01`.
