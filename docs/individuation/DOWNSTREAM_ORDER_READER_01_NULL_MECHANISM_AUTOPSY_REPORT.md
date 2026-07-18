# DOWNSTREAM-ORDER-READER-01 — null-mechanism autopsy

Status: **RAW_INSUFFICIENT**

Roadmap: **UNRESOLVED_RAW_INSUFFICIENT**

Accepted prospective result: `d71c7ebb14cb74d47bbaac7858f4ec0286240bdb`.

This is a bounded, post hoc, raw-only audit. It does not reclassify, rescue or reinterpret the preregistered
result. No engine or runner was imported and no scientific world was initialized or reconstructed.

## Immutable raw audit

| Check | Result |
|---|---|
| prospective raw collection SHA-256 | PASS — `8d4baaac198cf5e5526359ad723d4cebd0c0614ffa2441fead41144ef573adf1` |
| committed raw-only reproduction SHA-256 | PASS — `35616172409424d28d765acecb2c29ac1f2527fb7acd48196a9113e85081b679` |
| manifest SHA-256 | PASS — `0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4` |
| ordered raw records | PASS — W001-W048, seeds 58001-58048 |
| stored complete-world contrasts | PASS — all 35 exact |
| frozen classification object | PASS — exact `NO_ACCESS_ESTABLISHED` |
| parent manifest bindings | PASS — all 15 bound files exact |
| manipulation or numerical failure | PASS — none recorded |
| raw-only parent reproduction rerun | PASS — byte-identical to the committed reproduction |
| audit determinism | PASS — two independent audit outputs byte-identical |
| engine/world activity | PASS — zero imports, initializations and reconstructions |

The frozen prospective result remains: 35/48 complete original worlds; primary mean
`5.0871520880175235e-08`; median `8.55489855591438e-11`; two-sided 95% Student-t interval
`[-3.874958897076355e-09, 1.0561800065742683e-07]`; 21 positive and 14 negative signs; positive direct source
calibration in 34/35 worlds; no manipulation or numerical failure. Its classification remains exactly
`NO_ACCESS_ESTABLISHED`.

## Plan frozen before the sufficiency result

The equation-based decomposition and fail-closed raw-sufficiency gate were committed first as `130be74`. The
plan freezes the exact `cbar`, `dc`, `chi`, upwind, capacity, advective-flux, linearized saturation, signed face
contribution, absolute sum, cancellation-index and boundary-partition formulas. It also freezes the
zero-denominator rule and the requirement that the original world remain the only inferential unit.

Only after that commit did the audit inspect whether the persisted raw could evaluate those formulas.

## Why the raw is insufficient

Each complete arm persists the signed internal aggregate `J_internal_x`, aggregate `flux_abs_sum`, internal-face
count, `dt`, core mass, and identity hashes such as `flux_x_sha256`. It does not persist the numerical face arrays
or source-state quantities required by the mission:

- source-conditioned core `c` values;
- internal-face `c_i`, `c_p`, `rho_i` and `rho_p`;
- exact per-face `cbar`, `dc`, `chi`, upwind choice and free capacity;
- executed numerical internal +x face-flux values;
- numerical boundary-face flux values.

A hash establishes identity, not numerical values. The stored signed and absolute aggregates cannot recover
individual face contributions, their signs, or their covariance with the nonlinear equation terms. Therefore
they cannot distinguish local buffering, signed cancellation, saturation-regime heterogeneity, or
gradient/upwind gating. The boundary object contains hashes and frame labels but no numerical boundary flux, so
the internal/boundary partition is also unavailable.

Reconstructing any missing value would require initializing or replaying a scientific world, which this mission
explicitly prohibits. The fail-closed gate therefore prevented every requested decomposition estimate. No
face-level or world-level mechanism statistic was computed.

## World-level mechanism table

`DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_WORLD_TABLE.csv` includes all 35 complete original worlds without
exclusion. It carries the already-stored `delta_A_O` solely as an immutable accounting check and marks each
required numerical family unavailable. Faces are never treated as statistical units.

## Post hoc diagnosis

**RAW_INSUFFICIENT**

No candidate failure mode is labelled compatible, supported or confirmed. This is a statement about persisted
instrumentation, not about the mechanism and not about the scientific effect.

## Roadmap

**UNRESOLVED_RAW_INSUFFICIENT**

The audit identifies no unique equation-derived failure mode, so it does not recommend a new probe. It also
cannot close the order-reader line on mechanistic grounds. Any future scientific proposal would require a new
human decision and a new pre-data design; none is authorized here.

## Exact claim boundary

The only mechanistic conclusion is that the immutable raw files do not contain enough numerical information to
perform the prerequested face-level decomposition. `NO_ACCESS_ESTABLISHED` remains failure to establish the
preregistered one-update downstream interaction under this probe. It is not evidence of absence, equivalence,
ownership, identity, memory, active reconstruction, or any particular failure mechanism.
