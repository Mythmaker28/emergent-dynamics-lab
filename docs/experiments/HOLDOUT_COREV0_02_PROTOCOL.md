# HOLDOUT-COREV0-20260710-002 — Diagnostic Fresh-seed Protocol

**Frozen before any hold-out trajectory is executed.**

## Disposition appended after execution

**INVALIDATED_SELECTION_BUG.** The analysis implementation counted a second cadence before requiring that cadence's track to be clean and long. The intended rule therefore selected only law 3, not `{1,3,6,10}`. All 20 executed runs and artefacts are preserved, but no hold-out disposition is accepted from this experiment. A new protocol uses new unseen seeds and the corrected clean-cadence join.

## Interpretation boundary

This hold-out tests whether a high-P/low-M **occupancy regime** recurs under fresh seeds. It cannot by itself distinguish persistent dynamical organization from the live `STATIC_MOTIF_WITH_MATERIAL_FLUX` or `SPARSE_LOOKALIKE_ALIAS` nulls. Survival is not scientific promotion.

## Parent baseline

- Experiment: `BASELINE-COREV0-20260710-002`.
- Audited physics/measurement commit: `eebd7fa8292aa3bc089f0c2a991e451888f7ebe3`.
- 12 Halton LawSpecs, screening seeds `{101,202,303}`, 600 steps, `dt=0.02`, cadences `{10,30,60}`.
- Initial probe unchanged: `P > 0.8, M < 0.5`.
- Raw probe rows: 384; all retain explicit unresolved sparse-alias risk.

## Frozen LawSpec selection rule

A LawSpec enters diagnostic hold-out only if:

1. a row satisfies the unchanged initial probe;
2. its track has at least eight observations;
3. the track has no logged split, merge, or ambiguous association anywhere;
4. the same physical start/end steps are probe-positive under at least two observer cadences;
5. conditions 1–4 occur in at least two distinct screening seeds.

Selected baseline law indices: `{1,3,6,10}`. No physical coefficient, feature, tracker gate, or threshold changed.

## Execution

- Law indices: `{1,3,6,10}`.
- Fresh seeds: `{404,505,606,707,808}`.
- Runs: 20.
- World/run/detector/phenotype/tracker/lags/backends: exactly the parent configuration.
- Required artefacts include association edges and measurement interval ambiguity flags.

## Frozen diagnostic gate

Apply the exact rule above per fresh seed. A law is retained only for direct trajectory/static-flux audit and perturbation design if at least two of five fresh seeds qualify.

`2/5` is a robustness disposition, not an estimate of event probability.

## OBSERVED / INFERRED / HYPOTHESIS / FALSIFICATION

### OBSERVED

Report fresh-seed counts, full P/M distributions, lineage flags, cadences, taus, and raw descriptors.

### INFERRED

Only whether the occupancy-regime screening condition recurs.

### HYPOTHESIS

Any survivor may still be static material flux, sparse look-alike stitching, or tracker-sensitive occupancy.

### WHAT WOULD FALSIFY THIS?

- Fewer than two qualifying fresh seeds rejects a law under this diagnostic gate.
- Direct dense-trajectory audit showing occupancy replacement supports the null explanation.
- Failure under a frozen controlled perturbation rejects persistent organization.
