# GIMB00_FREEZE — master freeze

Written and hashed **before any numeric response array is loaded**. The GIMB00_PHASE2_LOCK may
later bind data-derived Phase-1 outputs; it may not revise anything below.

## Provenance bound before this freeze

| object | value |
|---|---|
| grandparent ancestor | `e912a1004c5b9732d12a8fcc417002bfd1135622` |
| WSFSCRP00 closure | `f81daf91dd70a05f34372fb85d2c3fba0dd5550b` |
| FSCMA00 | `f9e1e39170a746bc5d8c43a80bc878cf24180714` |
| FSCMA00 subtree | `27a62919b9664ab8fdb114f17e51016cfc3ccb46` |
| WSFSCRP00 subtree | `e9a7f5be474852c2ef01d6567303c6fe4ef6ff48` |

Ancestry is a first-parent chain of direct parents, verified on the device repository. Every raw
source is bound by its committed git blob object id, recomputed from local bytes.

## Endpoint (unchanged, inherited)

    delta_A[b,u,h] = sum_i M_A0[b,i]*rho[INT,b,u,h,i]/B_b - sum_i M_A0[b,i]*rho[SHAM,b,h,i]/B_b
    delta_B[b,u,h] = sum_i M_B0[b,i]*rho[INT,b,u,h,i]/B_b - sum_i M_B0[b,i]*rho[SHAM,b,h,i]/B_b

Response of rho integrated over two fixed grid regions. Not component identity, not material
provenance, not a Lagrangian body, not bath flux, not memory, not agency, not life.

## Gauge group

    for each founder b independently: (A_b, B_b) may be swapped ONCE
    the same swap applies to every scored time and every arm and dose of that founder

Not one swap per time, per operator, per dose or per row.

## Orthonormal channel transform

    u[b,o,h] = sqrt(w_h) * (delta_A + delta_B) / sqrt(2)      -> u  under a swap
    v[b,o,h] = sqrt(w_h) * (delta_A - delta_B) / sqrt(2)      -> -v under a swap
    ||u||^2 + ||v||^2 = sum_h w_h (delta_A^2 + delta_B^2)

Weights, exact: `w = [1/18, 1/9 x 8, 1/18]`, sum 1, over physical times 4.0 .. 40.0.

## Quotient object

    D_Q^2([i],[j]) = ||u_i-u_j||^2 + ||v_i||^2 + ||v_j||^2 - 2*|<v_i,v_j>|

applied to WHOLE-FOUNDER multi-arm blocks. The single-row form is a diagnostic only.

    PRIMARY_GAUGE_INVARIANT_OBJECT = GLOBAL_SWAP_QUOTIENT_METRIC
    COMPLETE_ALGEBRAIC_CROSSCHECK  = (u, WHOLE_FOUNDER_v_OUTER_v)
    COMMON_SECTOR_DIAGNOSTIC       = u
    DIFFERENTIAL_AMPLITUDE         = ||v||^2
    DIFFERENTIAL_PROJECTIVE        = v OUTER v
    LOSSY_SENSITIVITY_ONLY         = pointwise |v|, elementary symmetric functions
    NO_COORDINATE_SELECTION_BY_OUTCOME = true

## Panels and weights (frozen before numeric loading)

| panel | rows | alpha |
|---|---|---|
| CARRIER_BASIS | 6 WSFSCRP00 BASIS clusters x 2 carrier sentinels | 1/6 per cluster, split 1/2 per sentinel = 1/12 |
| CARRIER_LOCKED | 6 FSCMA00 LOCKED clusters x same 2 sentinels | 1/12 |
| ENV_PROBE | +0.5*N0 on the 6 BASIS clusters | 1/6 |
| ENV_LOCKED | +0.5*N0 on the 6 LOCKED clusters | 1/6 |
| ENV_DOSE_SECONDARY | +0.25*N0, diagnostic only | never primary |

`PRIMARY_CENTERING = SINGLE_AFFINE_MEAN_OVER_CARRIER_BASIS`. Fit only on CARRIER_BASIS.

## Solver, precision and tie rules

* Exhaustive enumeration of all `2^(F-1) = 32` linked founder-swap assignments; the
  lexicographically first founder is pinned to +1 to remove the global duplicate only.
* All Gram entries are **exactly rational**: `<z_i,z_j> = <u_i,u_j> + eps_i*eps_j*<v_i,v_j>`, and
  `sqrt(w)*sqrt(w) = w`, so no irrational ever enters a decision.
* Eigenvalues are enclosed by exact Sylvester inertia (exact LDL^T of `G - tI`), bisected to a
  relative width of `1e-24`.
* Co-optimum tolerance: two swap assignments are co-optimal when their certified enclosures for
  the same `R_k` overlap, or differ by less than `1e-18` relative.
* A heuristic orientation, the FSCMA00 rule, seed parity, or a solver chosen after seeing the
  landscape gives `QUOTIENT_OPTIMUM_UNCERTIFIED`.

## Gates

    QDIM0 = lower(R0) > FROZEN_BETWEEN_RESPONSE_MATERIALITY_ENERGY
    QDIM1 = lower(sqrt(L2)) > FROZEN_MODAL_MATERIALITY_AMPLITUDE
    QDIM2 = lower(sqrt(L2/L1)) > 0.10          (exactly 0.10 = FAIL)
    QDIM3 = lower(L2/R0) >= 0.05               (exactly 0.05 = PASS)
    ONE_AFFINE_FAMILY_AT_5_PERCENT_GATE: upper(R1/R0) < 0.05 AND upper(cell residual) < 0.10 each
    k=2 goodness: upper(R2/R0) < 0.05 AND upper(k=2 cell residual) < 0.10 each
    sector attribution: lower(P_PLUS) >= 0.95 COMMON; lower(P_MINUS) >= 0.95 DIFFERENTIAL;
                        both >= 0.05 MIXED; otherwise SECTOR_ATTRIBUTION_UNRESOLVED
    environmental separation: lower(OFF_ABS) > propagated bound, lower(OFF_FRAC) >= 0.05,
                        >= 5 of 6 cells, min env cell > upper(LOAO_TUBE_RADIUS),
                        stability >= 0.80, max single-founder share <= 1/3,
                        agreeing separately on ENV_PROBE and ENV_LOCKED and on every co-optimum

## Absolute materiality — compatibility criterion, frozen here

The inherited per-founder bound `ETA_b` bounds the parent's **weighted L1** statistic
`A_bu = sum_h w_h (|delta_A|+|delta_B|)`. The quotient works in **weighted L2**. The propagation
is derived in `MATERIALITY_BOUND_PROPAGATION.md`; the constant is `1/sqrt(min_h W_h) = sqrt(18)`.

A propagated bound is declared **COMPATIBLE** only if, applied to the parent's own per-cell
responses, it reproduces the material/immaterial status those cells were accepted with. A bound
that would retrospectively declare the parent's accepted material responses immaterial is not a
compatible restatement of the inherited threshold in the new units, and no tighter constant may be
improvised. In that case:

    ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE
    -> report relative structure only, PHASE2_LICENSE = NO, forbid the word material

This criterion is frozen before any response array is read, and it is decided by arithmetic, not
by preference.

## Zero and boundary rules

* `trace(v OUTER v) = 0` -> `UNDEFINED_ZERO_DIFFERENTIAL_SECTOR`; never add epsilon.
* ratio exactly 0.10 = FAIL; energy share exactly 0.05 = PASS; interval crossing = `NUMERICALLY_UNRESOLVED`.
* `upper(R0) <= 0` or `upper(L1) <= 0` = `DEGENERATE_QUOTIENT_SCATTER`.
* `upper(L2) <= 0` = `NO_SECOND_QUOTIENT_INCREMENT`.
* Never divide by, or take the square root of, an interval touching zero.

## Budget

    PHASE1_MAX_ENGINE_STARTS = 0   (literal; the engine counter is asserted equal before and after)
    PHASE2_MAX_ENGINE_STARTS = 96  (only on an exact PHASE2_LICENSE = YES)
    NEW_LAWSPEC / ENGINE_EQUATION_CHANGE / NEW_STATE_VARIABLE_OR_TRACER = false
    FIXED_SUPPORT_READER_CHANGE / CHECKPOINT_TIME_CHANGE / HORIZON_CHANGE = false
    SEEDS 62000-62009 = RESERVED_AND_UNREAD; SEEDS 64000-64011 = OUTCOME_EXPOSED
    PUSH_AUTHORIZED = false; DRAFT_PR_AUTHORIZED = false; WORKFLOW_TRIGGER_AUTHORIZED = false

## Append-only status of the parents

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    FSCMA00_H2_STATUS_IN_GIMB00     = REPORTED_PARENT_LABEL_REQUIRING_GAUGE_INVARIANT_QUALIFICATION
    GIMB00_PHASE1_DATA_STATUS       = POST_HOC_GAUGE_CORRECTIVE_REANALYSIS_OF_EXPOSED_DEV_ROWS

Every WSFSCRP00 and FSCMA00 row is exposed. Phase 1 is post hoc. The words held-out, confirmed,
blind and replicated are not available to it.
