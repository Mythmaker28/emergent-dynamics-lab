# FWL2CF00_FINAL_REPORT

    FWL2CF00_DISPOSITION = FRESH_ACTIVE_PANEL_COMPLETE__RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY

    SHAM_REFERENCE_RECONSTRUCTION_STATUS       = PASS_16_OF_16
    ACTIVE_PANEL_STATUS                        = COMPLETE_32_OF_32
    CARRIER_1_CELL_MATERIALITY                 = PASS_16_OF_16
    CARRIER_2_CELL_MATERIALITY                 = PASS_16_OF_16
    ALL_CELL_MATERIALITY                       = PASS_32_OF_32
    FRESH_CARRIER_QUOTIENT_STRUCTURE           = RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY
    FRESH_STRATUM_TRANSFER                     = NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT
    FROZEN_FACTOR_PIPELINE_STATUS              = PARENT_OBJECT_NOT_EVALUABLE
    MANIPULATED_GEOMETRY_STATUS                = BELOW_MATERIALITY
    UNORIENTED_ALLOCATION_STATUS               = BELOW_MATERIALITY
    GEOMETRY_ALLOCATION_MODULATION_STATUS      = BELOW_MATERIALITY
    FACTORIAL_ATTRIBUTION_PLUS                 = BELOW_MATERIALITY
    FACTORIAL_ATTRIBUTION_MINUS                = TRANSFORMED_BOUND_NOT_QUALIFIED
    FACTORIAL_ATTRIBUTION_STATUS               = NOT_REACHED
    INDEPENDENT_ANCESTRY_BLOCKS                = 4_G1
    ENGINE_STARTS                              = SHAM_REPLAY_16 + ACTIVE_32 + OTHER_0 = 48 of 48
    DELIVERY_STATUS                            = COMPLETE

## 1. Provenance

The seven-commit chain `e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61 -> 226b2c9 -> 2c9fc97`
is direct-parent at every arrow. Manifests re-verified from bytes: WSFSCRP00 49/49, FSCMA00 35/35,
GIMB00 25/25, WL2SMF00 **65/65**, zero failures; 27 bound artifacts additionally verified by
recomputing their git blob object ids, 27/27.

The arm lock's temporal priority is proved by **one-way hash chaining**, not by co-presence: the
panel lock contains the arm lock's digest, the threshold lock contains the panel lock's digest.
Both re-verified. The parent's zero-active-outcome claim is re-proved by resolved-symbol AST audit.

## 2. Why 16 sham replays, and what they established

WL2SMF00 never persisted `X_A[SHAM_0,d,h]`, so `delta = X[INT] - X[SHAM_0]` could not be formed.
Exactly one canonical replay per sealed descendant, a new successor budget. **16 of 16 passed every
exact acceptance test**: `B`, `RHO_MED` and `G2^2` equal their locked values exactly, and the
oracle recomputation of `TAU_MATERIAL_L2^2` equals the locked value exactly. The locked threshold
remains the operative one; the recomputation is an oracle and never entered a decision.

No byte-for-byte comparison with a prior archive was possible and none is claimed — the original
series never existed. Identity rests on sealed input bytes, the parent's twin determinism, exact
agreement with every locked scalar, and independent reader agreement rebuilt in a separate process.

## 3. Engine accounting

    SHAM_0 replay 16 of 16   ACTIVE 32 of 32   setup/diagnostic 0   TOTAL 48 of 48
    retries 0, replacements 0, top-ups 0; tranches independent

## 4. The active panel

All 32 rows completed on the first attempt. Physical and runtime oracle **32 of 32**: the operator
identity guard matched the locked callable every time; the `t0` touch set equalled the frozen
declaration `['Mf']`; `rho` was never directly written; the input checkpoint hash was identical
before and after; masks and normalizer unchanged; complete finite series; production and reference
readers agree exactly; and `r(h0) = (0,0)` exactly on all 32 rows, as the frozen
`EXPECT_STRUCTURAL_ZERO_AT_H0` predicted.

## 5. Cell materiality — the panel is uniformly readable

    CARRIER_1  PASS 16 of 16      CARRIER_2  PASS 16 of 16      ALL  PASS 32 of 32
    M2/TAU margins: 3.14 .. 10.20
      CARRIER_1 3.14 .. 4.86      CARRIER_2 5.77 .. 10.20

Decided on exact squares, equality counting as failure; the ratios above are readable margins only.
This is the first time in this programme line that a **prospectively** thresholded panel has
delivered a materially readable response in every cell.

## 6. Fresh quotient — relative structure yes, absolute second mode no

    R0 = 4.093362e-06   R1 = 4.551841e-07   R2 = 9.307581e-08
    I1 = 3.638178e-06   I2 = 3.621082e-07
    QDIM0 total scatter   R0/E_TAU  = 3.675   -> PASS
    QDIM1 second absolute sqrt(I2)/A_TAU = 0.570 -> FAIL
    QDIM2 ratio squared   I2/I1 = 0.0995  (> 0.01) -> PASS
    QDIM3 second share    I2/R0 = 0.0885 (>= 0.05) -> PASS
    direct one-family     R1/R0 = 0.1112 (needs < 0.05), worst cell 0.4011 -> FAIL

The optimiser is certified: `R0` exactly over all 32768 linked swaps via an exact binary quadratic
form, `R1` and `R2` exhaustively in float with an error bound of `3.66e-16` that the
winner-to-runner-up gaps exceed by factors of 6e8 to 1.8e10. **The argmin is identical for
k = 0, 1 and 2**, and the float argmin coincides with the exactly certified `R0` argmin.

So the response set is not adequately described by one affine family, and the second increment is
real in relative terms — but `sqrt(I2)` reaches only 0.570 of `A_TAU`.
This is exactly the conservatism WL2SMF00 declared in advance and refused to soften: because
`I2 <= R0` always, the modal gate demands that the second increment alone exceed the entire
immateriality budget. At the observed share 0.0885 that needs
`R0 > E_TAU/share = 1.2593e-05`; the panel delivered
`R0 = 4.0934e-06`, about 3.1x short. The rule was not adjusted after seeing this.

A relative-structure observation worth recording, and nothing more: the fresh panel's
`I2/I1 = 0.0995` and `I2/R0 = 0.0885` sit close to GIMB00's exposed-panel
`0.1172` and `0.1035`. That is a consistency note about relative geometry on an independent panel
with prospectively sealed thresholds. It reclassifies nothing.

## 7. Stratum transfer — not evaluable, and declared before the data

`FROZEN_FACTOR_PIPELINE_STATUS = PARENT_OBJECT_NOT_EVALUABLE`. GIMB00 serialised only scalar
summaries of its founder-stratum object; `psi_plus` and `Psi_minus` are in no committed parent
tree. Rebuilding them would require reopening and refitting the historical exposed active rows,
which this handoff forbids, and FSCMA00's `phi1` is a different object on a different panel.
This was written into the master freeze **before the first sham replay**, not discovered afterwards.
Q_PRIMARY_3 is therefore `NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT` and Q_PRIMARY_4 `NOT_REACHED`.
The quotient outcome would have made transfer ineligible on a second, independent ground.

## 8. Fresh G1 x H3 factor objects — all below their conservative floors

    MANIPULATED_GEOMETRY_STATUS            BELOW_MATERIALITY
    UNORIENTED_ALLOCATION_STATUS           BELOW_MATERIALITY
    GEOMETRY_ALLOCATION_MODULATION_STATUS  BELOW_MATERIALITY

Geometry contrast, allocation-averaged and block-paired: amplitude 1.5619e-03 against a floor of
4.1497e-03 for CARRIER_1 (ratio 0.376) and 1.7489e-03 against the same floor for CARRIER_2
(ratio 0.421). Unoriented allocation sensitivity: 0 of 8 (block, geometry) cells reach their floor,
for either arm.

This is coherent rather than surprising. The conservative floor for a normalised four-row contrast
is `sum_i |c_i| TAU_i = 2 x TAU`, so a contrast must exceed twice a single cell's threshold. The
individual responses are 3-10x their own thresholds but are **similar across design cells**, so
their differences are small. A triangle-inequality floor is built to refuse exactly this.

H3 allocation-label gauge: all `2^8 = 256` independent member exchanges leave every unoriented
allocation object exactly invariant. No signed history statement is made or possible.

MINUS-sector objects are computed as shape diagnostics and carry `TRANSFORMED_BOUND_NOT_QUALIFIED`,
because the parent certificate records `PROJECTIVE_EMBEDDING_BOUND = NOT_AVAILABLE`.

## 9. Independent units

`n = 4` upstream ancestry blocks. 16 descendants, 32 rows, 2 arms, 2 channels, 10 times are
repeated conditions. `P_LESS_THAN_0_05_POPULATION_CLAIM = IMPOSSIBLE_AND_NOT_REQUIRED`, and no such
number is quoted.

## 10. Claim ceiling

On the exact prospectively sealed 16-descendant G1 x H3 development panel, both predeclared carrier
interventions produced material fixed-support responses in all 32 cells, and the fresh
gauge-invariant carrier response set was **not** adequately described by one affine quotient
coordinate while its second increment did **not** reach the frozen absolute materiality floor. The
previously frozen founder-stratum object could not be evaluated at all, because it was never
serialised. Nothing more is claimed.

RESPONSE_INFORMED_EXPLORATORY_DEV, prospectively locked panel and thresholds, one LawSpec, one
checkpoint and horizon, fixed-support reader, four independent ancestry blocks, finite designed
panel, single executor, not independent review, not confirmatory, not population inference. No
parent was reclassified. No signed history claim. No physical A/B identity. No intrinsic or
universal rank. No environmental claim. No life, agency, identity, memory or provenance claim.
