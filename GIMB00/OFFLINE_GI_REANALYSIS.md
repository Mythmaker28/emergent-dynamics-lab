# OFFLINE_GI_REANALYSIS — Phase 1

**Engine starts: 0.** Asserted equal before and after. No engine, substrate, state or checkpoint is
imported anywhere in the Phase-1 code path.

## 1. The gauge, and an oracle that can fail

The physical ambiguity is exactly one A/B exchange per founder, shared across every scored time and
every arm of that founder. Verified from the reader, the mask lifecycle and the operator code.

All required operators are exchange-equivariant: the matched transposition is symmetric in its two
argument lists, and both the intensive reflection and the environmental perturbation never read the
masks at all.

Oracle, with all `2^12 = 4096` artificial assignments enumerated and every invariant recomputed
from genuinely exchanged `delta_A`/`delta_B` bytes:

| test | result |
|---|---|
| `Q0C_u_invariant` | True |
| `Q0D_whole_block_vvT_invariant` | True |
| `Q0F_energy_identity` | True |
| `v_itself_changes_sign` | True |
| `Q0E_block_outer_product_is_exactly_rank_one` | True |
| `Q0E_block_determined_by_u_and_vvT_up_to_one_sign` | True |
| `Q0E_cross_arm_relative_sign_is_retained` | True |
| `Q0G_quotient_distance_invariant_over_all_2F_assignments` | True |

and four negative controls, all of which fire, proving the suite is not vacuous:

* `N1_per_row_swap_changes_block_vvT` = True
* `N2_per_row_swap_changes_quotient_distance` = True
* `N3_quotient_strictly_richer_than_u_only` = True
* `N4_energy_identity_detects_a_corrupted_row` = True

**VERDICT: GAUGE_ORACLE_PASS_WITH_NEGATIVE_CONTROLS**

## 2. Absolute materiality — the load-bearing negative

The inherited threshold bounds a weighted **L1** functional; the quotient lives in weighted **L2**.
The exact worst-case propagation is `||z|| <= A_bu / sqrt(min_h w_h) = sqrt(18) * A_bu`, attained
when the whole response sits on one endpoint of the scored grid, so no smaller constant is valid.

Applied to the parents' own cells it reverses **12 of 36**:
every CARRIER_1 matched-transposition cell, in both roles, with `||z||/eta_z` in
[0.610, 0.749].
Surviving cells run from 1.100
to 17.685.

By the criterion frozen before any array was read: **`ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`**.
Relative structure only, no material claim, `PHASE2_LICENSE = NO`.

## 3. The certified quotient optimum

Exhaustive over all 32 linked assignments, exact rational Gram, Sylvester-inertia eigenvalue
enclosures.

| quantity | certified |
|---|---|
| `R0` (exact) | 3.790826e-06 |
| `R1` | [4.431740e-07, 4.432322e-07] |
| `R2` | [5.073650e-08, 5.085291e-08] |
| `L1` | 3.347593e-06 |
| `L2` | 3.923211e-07 |
| `QUOTIENT_INCREMENT_RATIO = sqrt(L2/L1)` | [0.3423, 0.3424] |
| `QUOTIENT_SECOND_SHARE = L2/R0` | [0.1035, 0.1035] |

The argmin is **unique** and is the same assignment for k = 0, 1, 2: swap
`[64002, 64006, 64010]`. One co-optimum only, so no co-optimal disagreement can arise.

    QDIM2 (ratio > 0.10)      : True
    QDIM3 (share >= 0.05)     : True
    QDIM0 / QDIM1 (absolute)  : NOT_AVAILABLE

Direct reconstruction gates on CARRIER_BASIS:

    one affine family : aggregate 0.1169 (needs < 0.05), worst cell 0.2759 (needs < 0.10)  -> FAIL
    two dimensions    : aggregate 0.0134 (needs < 0.05), worst cell 0.0359 (needs < 0.10)  -> PASS

So `CARRIER_MODEL_DIMENSION_USED_FOR_ENV_TEST = 2`.

## 4. Sector of the second degree

Nested extension of the frozen one-dimensional model, under the same alignment:
`P_PLUS = 0.4451`, `P_MINUS = 0.5549` -> **MIXED**,
identical across every co-optimal representative (['MIXED']). The nested extra
energy has no compatible absolute bound, so it is a shape statement, not a material one.

## 5. Transfer to CARRIER_LOCKED, no refit

| k | aggregate residual | worst cell | gate |
|---|---|---|---|
| 1 | 0.1112 | 0.2981 | False |
| 2 | 0.0195 | 0.0487 | True |

`CARRIER_QUOTIENT_TRANSFER_STATUS = SAME_GATE_STATUS_ON_CARRIER_LOCKED_WITHOUT_REFIT`. The BASIS gate status
at the frozen dimension reproduces on twelve cells that were never used to fit anything.

## 6. The environmental relation

Scored against the frozen two-dimensional carrier family; the carrier family was never refitted to
environmental rows.

| panel | off-family aggregate | worst-of-min cell | cells >= 0.05 | F_PLUS | F_MINUS | max single-founder share |
|---|---|---|---|---|---|---|
| ENV_PROBE | 0.7340 | 0.7101 | 6/6 | 0.8848 | 0.1152 | 0.1807 |
| ENV_LOCKED | 0.7227 | 0.7091 | 6/6 | 0.8898 | 0.1102 | 0.1911 |
| +0.25 dose (diagnostic) | 0.7090 | 0.6891 | 6/6 | 0.8942 | 0.1058 | 0.1798 |

LOAO carrier tube radius 0.0630; the smallest environmental cell is
0.7091, above it by more than a factor of ten.
Direction stability modulo the linked swap: probe vs locked
0.999765; +0.50 vs +0.25 0.999613.

`ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS = OPERATOR_SPECIFIC_MIXED_EXTENSION`.

Both `F_PLUS` values sit at ~0.885-0.890, below the 0.95 a common-only label requires, and both
`F_MINUS` values exceed 0.05. The environmental extension is **mixed**, not common-only. Since the
carrier quotient is already at least two-dimensional, the environment is an off-carrier extension
and never "the second mode".

## 7. The parent-aliased founder stratum

Named `PARENT_ALIASED_FOUNDER_STRATUM` throughout; no member name (geometry, history, parity) is
adopted as the cause.

    support BASIS  : 3 + 3   (True)
    support LOCKED : 3 + 3   (True)
    R_STRATUM_0    = 3.790826e-06
    R_STRATUM_2MEAN= 3.413150e-06
    E_STRATUM      = 3.776760e-07
    STRATUM_SHARE  = 0.0996    (relative gate >= 0.05: True)
    nested sector  : P+ = 0.5220, P- = 0.4780 -> MIXED
    LOAO shares    : all >= 0.05 = True, min alignment 0.9961
    max single cluster share = 0.2322 (needs <= 1/3: True)
    LOCKED transfer share    = 0.0998, axis alignment 0.9923
    ABSOLUTE_MATERIALITY     = NOT_AVAILABLE

Every relative and support sub-gate the stratum object had to clear, it clears. The one it cannot
clear is absolute materiality, because no compatible bound exists in this panel's units. The
conjunctive rule therefore gives

**`FOUNDER_STRATUM_QUOTIENT_STATUS = NUMERICALLY_UNRESOLVED` and `PHASE2_LICENSE = NO`.**

This is the honest reading: the stratum object is *there* in the relative geometry, reproducibly and
with balanced support, and it *cannot be called material* on the evidence available. Those are two
different statements and only the first is licensed.
