# HOLDOUT-COREV0-20260710-004 — Frozen Fresh-seed Hold-out

## HISTORICAL AGENT-REPORTED

- 7079 measurements; r(P,M)=0.68; 0/7079 for P>0.8 and M<0.5.
- These values were not used as reproduced data in this experiment.

## OBSERVED

- Executed runs: 45.
- Measurement rows: 41889 (repeated tracks/lags; not independent replicates).
- P range: 0.25749258479322 to 0.9996760880409855.
- M range: 0.0 to 1.0.
- Descriptive r(P,M): 0.698845738595648.
- Initial exploratory probe raw count P>0.8, M<0.5: 502.
- Probe rows without logged ambiguity/split/merge inside the interval: 338.
- Every probe row retains unresolved sparse look-alike/static-flux alias risk.
- Kill-switch gates: `{"cadence_control_nonempty": true, "id_permutation_null": true, "material_retention_varies": true, "phenotype_continuity_varies": true, "second_force_path": true, "sparse_lookalike_alias_null_live": true, "static_flux_false_positive_null": true, "tracker_auditable": true, "tracker_cadence_sensitivity_null": true}`.

## INFERRED

- The technical P/M pipeline is eligible for EXP02 only if every kill-switch gate above is true.
- The static-flux null remains a known false positive even when it enters the initial probe.

## HYPOTHESIS

- Any association between P and M may reflect physical coupling, tracker selection, or repeated-measure structure; this baseline alone does not distinguish them.

## WHAT WOULD FALSIFY THIS?

- Failure of ID permutation, independent force-path agreement, cadence sensitivity, or held-out reruns invalidates interpretation of rare candidates.
- A candidate that disappears under frozen tracker settings or fresh seeds is not robust evidence.
