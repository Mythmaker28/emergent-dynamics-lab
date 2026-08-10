# WL2SMF00_MASTER_FREEZE

Written and hashed **before any fresh numeric array exists**. No engine module is imported by this
file. Nothing below may be revised later under this programme id.

    PROGRAMME_TYPE = METHODS_AND_MEASUREMENT_QUALIFICATION_ONLY
    ACTIVE_CARRIER / ENVIRONMENTAL / FACTORIAL INTERVENTION STARTS = 0
    ALLOWED_POST_T0_ENGINE_STARTS = SHAM_0_AND_SHAM_1_ONLY

## 0. Bound parent chain

    e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61

Direct-parent at every arrow. The **corrected** gauge oracle `GIMB00/gimb_oracle_v2.py` is bound;
the vacuous first-pass oracle is explicitly not inherited.

## 1. Materiality semantics — three separate concepts, never merged

    ETA_ORACLE_L2[d]   deterministic upper bound on SCORING / RELOAD / SUBTRACTION arithmetic error
    TAU_DYNAMIC_L2[d]  one percent of native sham evolution, in the exact L2 norm
    TAU_SITE_L2[d]     one-percent representative baseline-site effect, in the exact L2 norm
    TAU_MATERIAL_L2[d] = max(ETA_ORACLE_L2, TAU_DYNAMIC_L2, TAU_SITE_L2)

Materiality here is an **operational minimum effect scale**. It is not a p-value, not a confidence
bound, not a fitted noise distribution and not a physical constant. The engine is bit-deterministic:
two identical shams validate determinism and estimate nothing. Sham discordance is an oracle
failure, never a sample of noise.

The coefficient `0.01` is inherited unchanged from WSFSCRP00's prospective scientific floor. No
coefficient scan, power optimisation or response-informed alternative is authorised.

## 2. Exact weighted-L2 estimand and the gauge

Raw reader, per arm, descendant and time — **undifferenced**:

    X_A[arm,d,h] = sum_i M_A0[d,i] * rho[arm,d,h,i] / B[d]
    X_B[arm,d,h] = sum_i M_B0[d,i] * rho[arm,d,h,i] / B[d]

This is exactly `wsfscrp_core.q_channels`. The `dA`/`dB` arrays stored in parent files are ALREADY
`arm - sham`; a sham is never subtracted twice.

Future active response, unchanged endpoint:

    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0,d,h]
    delta_B[d,o,h] = X_B[INT,d,o,h] - X_B[SHAM_0,d,h]

    z[d,o] = concat_h( sqrt(w_h)*delta_A , sqrt(w_h)*delta_B )
    M2[d,o] = ||z[d,o]||_2

    u = sqrt(w_h)*(delta_A+delta_B)/sqrt(2)      v = sqrt(w_h)*(delta_A-delta_B)/sqrt(2)
    M2^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

Gauge: ONE A/B exchange per descendant, shared across every scored time and every future arm.
`u -> u`, `v -> -v`, `M2` invariant. Per-time, per-arm or per-row swaps are a larger, non-physical
group and are rejected.

Weights, exact: `w = [1/18, 1/9 x 8, 1/18]`, all positive, sum exactly 1, over physical times
4.0 .. 40.0. `h0` (the intervention checkpoint) is **not** in the scored grid, so
`W_POST = sum_(h != h0) w_h = 1` exactly.

## 3. Descendant-specific threshold

`SHAM_0` is frozen as canonical by serialiser order **before either sham runs**. `SHAM_1` is an
identity oracle only: never averaged, never chosen for calmness, never a replication.

    g2[d]  = concat_h( sqrt(w_h)*(X_A[SHAM_0,d,h]-X_A[SHAM_0,d,h0]),
                       sqrt(w_h)*(X_B[SHAM_0,d,h]-X_B[SHAM_0,d,h0]) )
    G2[d]  = ||g2[d]||_2
    TAU_DYNAMIC_L2[d] = 0.01 * G2[d]

    RHO_MED[d]     = exact median of rho[d,i,h0] over i in M_A0 union M_B0
                     (even count -> exact arithmetic mean of the two central sorted values)
    TAU_SITE_L2[d] = 0.01 * RHO_MED[d] / B[d] * sqrt(W_POST)

`TAU_SITE_L2` means: one representative baseline-support site's rho changes by one percent, in one
channel, zero at `h0`, sustained at that amplitude over the later scored times. A declared
scientific scale, not an uncertainty estimate.

    ETA_ORACLE_L2[d] = sqrt( sum_h w_h * ( eps_delta_A^2 + eps_delta_B^2 ) )
    eps_delta_c >= eps_INT_c + eps_SHAM_c + eps_SUBTRACTION_c + eps_RELOAD_c

derived branchwise from the actual datatype, summation, masks, normalizer and reader, outcome
independently. It bounds the scoring path on serialized states; it is NOT a stability bound on
engine dynamics. Scorer agreement is an oracle, not a proof of this bound. See
`ETA_ORACLE_L2_FORWARD_ERROR_CERTIFICATE.md`.

Forbidden: converting the old `ETA_bu`/`A_bu` by `sqrt(18)` or any fitted sparsity constant;
empirical RMS, pooled sd, covariance, percentile, quantile, maximum response, observed shape or a
favourable sector.

Frozen future cell rule:

    CELL_MATERIAL_PASS  iff lower(M2[d,o]) >  upper(TAU_MATERIAL_L2[d])
    CELL_MATERIAL_FAIL  iff upper(M2[d,o]) <= lower(TAU_MATERIAL_L2[d])
    otherwise CELL_MATERIAL_NUMERICALLY_UNRESOLVED

Equality is failure. No future programme may replace a descendant because its threshold is high or
because an active response fails.

## 4. Propagation to quotient and contrast estimands

Independent unit = the upstream ancestry block. Descendants, allocation branches, sham twins,
carrier sentinels, channels, sites and times are repeated conditions, never replications.

    G1 weights: 1/4 per upstream block, 1/4 per descendant, 1/2 per sentinel = 1/32 per row, n=4
    G2 weights: 1/8 per upstream block, 1/2 per descendant, 1/2 per sentinel = 1/32 per row, n=8

    E_TAU = sum_i alpha_i * TAU_MATERIAL_L2[i]^2          A_TAU = sqrt(E_TAU)
    E_ETA_ORACLE = sum_i alpha_i * ETA_ORACLE_L2[i]^2     A_ETA_ORACLE = sqrt(E_ETA_ORACLE)

`A_ETA_ORACLE` bounds only the weighted response-matrix perturbation norm. Certified `R_k`
intervals are built by bounding `sqrt(R_k)` first (1-Lipschitz argument) and squaring nonnegative
endpoints; `L2 = R1 - R2` by certified interval subtraction. The inequality
`|sqrt(L2_hat) - sqrt(L2_true)| <= A_ETA_ORACLE` is NOT asserted.

    TAU_CONTRAST(c) = sum_i |c_i| * TAU_MATERIAL_L2[i]       (normalised c, gauge-valid sector only)
    TAU_QUOTIENT_PAIR(i,j) = TAU_MATERIAL_L2[i] + TAU_MATERIAL_L2[j]
    H3_PRIMARY_ALLOCATION_OBJECT = UNORDERED_QUOTIENT_DISTANCE_BETWEEN_ALLOCATIONS
    H3_SIGNED_LINEAR_CONTRAST = NOT_DEFINED

Future gates, defined now and NOT evaluated here:

    QDIM_TOTAL_SCATTER_MATERIAL      iff lower(R0) > upper(E_TAU)
    QDIM_SECOND_INCREMENT_MATERIAL   iff lower(sqrt(L2)) > upper(A_TAU)
    inherited relative gates, additionally required: sqrt(L2/L1) > 0.10 and L2/R0 >= 0.05

Boundary and degeneracy rules are as written in the handoff and are reproduced verbatim in
`MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json`.

## 5-8. Panel, namespace, budget

    HISTORY route precedence H1 -> H2 -> H3 -> H4; GEOMETRY route precedence G1 -> G2
    fresh namespace (frozen queue) = [65000, 65001, 65002, 65003, 65004, 65005, 65006, 65007]
    62000-62009 reserved and unread; 61000-61009, 63xxx, 64000-64011 excluded
    START CONVENTION (inherited from WSFSCRP00 unchanged): one constructed descendant state = 1
    start. A precursor shared by an allocation pair is an internal sub-step of that pair, exactly
    as `make_founder` was a single start in the parent.
    C_ATTEMPT_MAX = 4 (one block = 4 descendants)
    C_SETUP = 2 (byte-equivalence replay of the refactored constructor against two old descendants,
                 one from each parity branch)
    N_ATTEMPT_MAX = floor((32 - C_SETUP) / C_ATTEMPT_MAX) = 7
    G1_MINIMUM = 4 accepted four-descendant blocks
    EXPECTED_SHAM_STARTS_IF_PANEL_COMPLETE = 32; MAX_TOTAL = 64
    UNUSED_STARTS_MAY_BE_REPURPOSED = false

    CONSTRUCTION_QUALIFICATION_ENDS_AT = EXACT_FUTURE_CHECKPOINT_T0
    ANY_POST_T0_STATE_ADVANCE_OTHER_THAN_SHAM_0_OR_SHAM_1 = ACTIVE_OUTCOME_PROTOCOL_BREACH

## 9-10. Append-only status and claim ceiling

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    GIMB00_DISPOSITION_REWRITTEN    = false
    OLD_EXPOSED_ACTIVE_ROWS = INELIGIBLE_FOR_THRESHOLD_SELECTION_OR_VALIDATION
    OLD_SHAMS = EXPOSED_METHOD_DEVELOPMENT_AND_PARSER_FIXTURES_ONLY
    OLD_SHAMS_LOCKED_CALIBRATION_UNITS = 0
    PHASE2_EXECUTED_IN_WL2SMF00 = false
    HISTORICAL_CARRIER_STRUCTURE_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_ENVIRONMENTAL_EXTENSION_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_FOUNDER_STRATUM_ABSOLUTELY_MATERIAL = NOT_TESTED

Maximum successful claim: a response-independent, descendant-specific operational materiality rule
defined directly in the normalised time-weighted two-channel L2 norm, passing non-vacuous
gauge/reference/mutation oracles, numerically sealed from sham-only trajectories on the exact fresh
panel intended for a later, separately authorised active carrier test. Nothing more.
