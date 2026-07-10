# HOLDOUT-COREV0-20260710-001 — Frozen Fresh-seed Protocol

**Frozen before any hold-out trajectory is executed.**

## Disposition appended after independent audits

**SUPERSEDED — NEVER EXECUTED.** Independent tracker and numerical audits found a silent sparse look-alike alias, compatibility alternatives mislabeled as resolved split/merge, incomplete association-edge persistence, subnormal norm underflow, and an unconstrained half-box domain. The project stopped before running these hold-out seeds. The rule below remains intact as a historical preregistration; a repaired baseline must produce a new candidate rule and new protocol ID.

## Parent screening artefact

- Experiment: `BASELINE-COREV0-20260710-001`.
- Physics/measurement commit: `5fa941bf7c0b757f5535965fad62c190a94fefa6`.
- 12 Halton LawSpecs, screening seeds `{101,202,303}`, 600 steps, `dt=0.02`, cadences `{10,30,60}`.
- Initial probe was not changed: `P > 0.8, M < 0.5`.

## Observed screening trigger

The baseline contains 384 probe-positive measurement rows. Because rows overlap in track, time, lag, and cadence, they are not independent evidence. The candidate audit identifies 20 physical endpoint pairs that remain probe-positive at the same start/end steps under at least two cadences after excluding tracks with any logged split, merge, or ambiguous association and requiring at least eight observations.

## Frozen LawSpec selection rule

A screening LawSpec enters hold-out only if all conditions hold:

1. at least one row satisfies the unchanged initial probe;
2. its cadence-scoped track has at least eight observations;
3. that track has no logged split, merge, or `ambiguous_association` anywhere;
4. the same physical start/end step pair is probe-positive under at least two of the three observer cadences;
5. conditions 1–4 occur in at least two distinct screening seeds.

This selects exactly baseline law indices:

`{1, 3, 6, 10}`.

No coefficient, phenotype feature, tracker gate, or P/M threshold was changed to obtain this set.

## Hold-out execution

- Law indices: `{1,3,6,10}` with their exact deterministic Halton mapping.
- Fresh seeds: `{404,505,606,707,808}`.
- Runs: 20.
- World: 64 particles, 3 types, unit periodic box, initial speed 0.04.
- Dynamics: `dt=0.02`, 600 steps, vectorized backend already validated against scalar reference.
- Observer cadences: `{10,30,60}`.
- Detector, phenotype, tracker, lag grid, and nulls: unchanged from the parent manifest.

## Frozen evaluation rule

Apply the exact LawSpec selection rule above to each fresh seed. Report the number of qualifying fresh seeds per law. A law is retained for controlled perturbation preparation only if at least two of five fresh seeds qualify.

This `2/5` rule is a robustness gate, **not** an estimate of `P(event | law)` and not a claim of 40% probability.

## Secondary outputs

- full continuous joint P/M distribution;
- probe occupancy by cadence and tau;
- lineage event counts;
- number of clean long tracks;
- same-endpoint cross-cadence consistency;
- raw descriptors and manifests.

## Interpretation contract

### OBSERVED

Only values directly calculated from the new seeds.

### INFERRED

Whether a screening signal survived the frozen fresh-seed gate.

### HYPOTHESIS

Even a retained law may still be a static material-flux or look-alike-stitching mechanism.

### WHAT WOULD FALSIFY THIS?

- Fewer than two qualifying fresh seeds rejects a law for perturbation preparation under this protocol.
- A retained law that fails direct trajectory audit or controlled perturbation is not evidence of persistent dynamical individuality.
