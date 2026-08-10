# WL2SMF00_FINAL_REPORT

    WL2SMF00_DISPOSITION = PROSPECTIVE_WEIGHTED_L2_RULE_AND_TARGET_PANEL_QUALIFIED

    MATERIALITY_SEMANTICS_STATUS             = MATERIAL_AND_NUMERICAL_SEPARATED
    WEIGHTED_L2_RULE_STATUS                  = QUALIFIED
    TARGET_PANEL_ROUTE                       = G1
    HISTORY_FACTOR_ROUTE                     = H3
    TARGET_PANEL_CONSTRUCTION_STATUS         = COMPLETE
    INDEPENDENT_ANCESTRY_BLOCKS              = 4_G1
    SHAM_TWIN_STATUS                         = PASS_16_OF_16
    NUMERICAL_THRESHOLD_LOCK_STATUS          = SEALED
    CELL_MATERIALITY_RULE                    = QUALIFIED_FOR_FUTURE_EXACT_PANEL
    MODAL_MATERIALITY_RULE                   = QUALIFIED_FOR_FUTURE_EXACT_PANEL
    GAUGE_VALID_FACTOR_OBJECT_RULE           = QUALIFIED_FOR_SELECTED_ROUTE
    ACTIVE_OUTCOME_STATUS                    = ZERO_GENERATED_AND_ZERO_OPENED
    NEXT_FRESH_ACTIVE_PANEL_LICENSE          = YES
    DELIVERY_STATUS                          = COMPLETE

    ENGINE STARTS: setup 2 + construction 16 = 18 of 32
                   sham 32 of 32; extra after panel lock 0
                   TOTAL 50 of 64
    ACTIVE INTERVENTION STARTS: 0 carrier, 0 environmental, 0 factorial, 0 other

## 1. Materiality separated from numerical detectability

`ETA_ORACLE_L2 = 0` exactly, on every descendant, with a proof rather than an assertion: the reader
accumulates `Fraction(float(v))` and every IEEE754 double is exactly a dyadic rational, so the sum
is exact and order-independent; `B` is exact; the difference of two exact rationals is exact; and
`npz` round-trips raw bytes. Two controls make the test non-vacuous -- the forward and reverse
summation orders agree exactly, and a float64 scorer on the same adversarial input gives a
*different* answer.

Because the numerical term is zero, `TAU_MATERIAL_L2 = max(0, TAU_DYNAMIC_L2, TAU_SITE_L2)` is set
by a **scientific** floor in 16 of 16 descendants. That is the separation the programme existed to
establish. Had only the numerical term survived, the frozen stop `NUMERICAL_DETECTABILITY_RULE_ONLY`
would have applied.

## 2. The formula and what dominates

    TAU_DYNAMIC_L2[d] = 0.01 * || sqrt(w_h) (X[SHAM_0,h] - X[SHAM_0,h0]) ||_2      both channels
    TAU_SITE_L2[d]    = 0.01 * RHO_MED[d] / B[d] * sqrt(W_POST),   W_POST = 1 exactly
    ETA_ORACLE_L2[d]  = 0
    TAU_MATERIAL_L2[d] = max of the three

`TAU_DYNAMIC_L2` dominates in **16 of 16**. Range across the panel
7.2618e-04 .. 1.2667e-03;
`TAU_SITE_L2` sits between 2.5306e-04 and
2.7588e-04, roughly a factor of four below. Aggregates:
`E_TAU = 1.113984e-06`, `A_TAU = 1.055454e-03`, `A_ETA_ORACLE = 0`.

`h0` is not among the scored times, so `W_POST` is exactly 1 and the site term is exactly
`0.01 * RHO_MED / B` -- worth stating, because a reader who assumed `h0` was scored would expect a
`sqrt` factor that is not there.

## 3. Oracles

14 groups pass; **12 negative controls all fire**: an unnormalised weight, a missing one-half
factor in the `u/v` identity, a per-time swap caught by the block invariant, the reference catching
a wrong production value, an L1 substitution flipping a decision, a perturbed weight, a wrong
normalizer, corrupted channel bytes, duplication-without-halving inflating the norm, equality at
threshold failing, an injected self-comparing predicate rejected by the AST audit, and the float64
path being distinguishable from the exact one.

One result deserves emphasis because it constrains how the gauge may be validated in future:
**`M2` alone is blind to a per-time swap.** The norm cannot see the difference between the physical
one-swap-per-descendant group and a larger, non-physical per-time group. Only the whole-descendant
block invariant detects it, and it does. Any future programme that validates the gauge with `M2`
alone would be validating nothing.

## 4. Routes and the true independent-unit count

`HISTORY_FACTOR_ROUTE = H3`. `H1` is ineligible because `apply_dual_history` delivers both
histories in lockstep and its own docstring proves the global forcing series is identical between
allocations -- there is no temporal order to contrast. `H2` is ineligible because no physical
anchor was uniquely designated in committed pre-outcome artifacts, and nominating one now would be
response-informed. Both complementary allocations run from identical precursor bytes, so the
unordered orbit is available with neutral branch names and no sign.

`TARGET_PANEL_ROUTE = G1`, and the decisive evidence is that `domc_core.found(seed)` draws
`seed_state(SPEC, TRACER, seed, 'random')` with **no geometry argument** and then multiplies by a
blob mask; hashing the seed field under both geometry settings gives the same digest. Geometry is
therefore an explicit constructor argument on a shared upstream ancestry, not a property of the
seed.

**Independent ancestry blocks: 4.** Sixteen descendants, thirty-two sham twins and the two future
carrier sentinels per descendant are repeated conditions. `n = 4`, never 16 and never 32.

The refactor that exposes geometry and allocation as explicit arguments was proved
semantics-preserving by reproducing **both** old parity branches byte-for-byte against their
committed checkpoint hashes.

## 5. The panel

Four blocks accepted from the first four queue entries, 16 of 16 descendants admissible, every
descendant with two byte-identical shams over the full horizon **including the terminal state
hash**, and one finite positive sealed threshold each. Production and independent reference agree
on all 16 descendants and on 40 random fixtures.

## 6. A baseline observation that justifies descendant-specific thresholds

In **NEAR** geometry the two complementary allocations separate completely in sham drift: allocation 0
gives 7.262e-04..7.573e-04 and allocation 1 gives
9.594e-04..1.027e-03, with no overlap in any of the four blocks. In
**FAR** they overlap. This is an observation about *untreated* trajectories -- no response exists --
and it is exactly why a single panel-wide threshold would have been wrong: the immateriality scale
genuinely differs by descendant, and by allocation within a geometry.

## 7. Propagation, proved

Under the null that every row is individually immaterial: swaps are isometries, weighted centering
is contractive, projection is contractive, hence `R0 <= E_TAU`; and `L2 = R1 - R2 <= R1 <= R0 <= E_TAU`,
hence `sqrt(L2) <= A_TAU`. Contrasts follow by the triangle inequality, quotient pairs likewise.
`sqrt(R_k)` is 1-Lipschitz in the perturbation norm, which is how certified `R_k` intervals are
built; the inequality `|sqrt(L2_hat) - sqrt(L2_true)| <= A_ETA_ORACLE` is **not** asserted, because
`R1` and `R2` are separately optimised.

**Declared consequence, not weakened:** since `L2 <= R0` always, the modal gate strictly implies the
total gate, and passing it requires the second increment alone to exceed the entire immateriality
budget. With the inherited relative gate `L2/R0 >= 0.05`, a future panel needs
`R0 > 20 * E_TAU = 2.2280e-05` in the worst case. That is demanding. Adjusting the rule
after noticing it is demanding would be response-adaptive, so it stands as frozen.

## 8. Zero active outcomes

No carrier, environmental or factorial operator was constructed, imported or applied. A
resolved-symbol AST audit confirms `wl2_prod.py` imports only `fractions`, the reference imports
nothing from production, and no active-operator symbol is called anywhere in the programme. The two
future carrier executables are named as **strings** in `FUTURE_ACTIVE_CARRIER_ARM_LOCK.json` for
the sole purpose of preventing arm shopping once the thresholds are known.

## 9. Licence

`NEXT_FRESH_ACTIVE_PANEL_LICENSE = YES`: the disposition is exactly
`PROSPECTIVE_WEIGHTED_L2_RULE_AND_TARGET_PANEL_QUALIFIED`, gates Q0-Q12 pass, the 16-descendant panel and its thresholds are sealed, and zero active
outcome exists. The licence covers a later, **separately authorised** active carrier programme on
this exact sealed panel. Nothing about the historical results changes:

    PHASE2_EXECUTED_IN_WL2SMF00 = false
    HISTORICAL_CARRIER_STRUCTURE_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_ENVIRONMENTAL_EXTENSION_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_FOUNDER_STRATUM_ABSOLUTELY_MATERIAL = NOT_TESTED

## 10. Claim ceiling

A response-independent, descendant-specific operational materiality rule was defined directly in
the normalised time-weighted two-channel L2 norm, passed non-vacuous gauge, reference and mutation
oracles, and was numerically sealed from sham-only trajectories on the exact fresh panel intended
for a later active carrier test. Nothing more. Methods and measurement qualification only; one
LawSpec; one checkpoint and horizon; a finite designed dev panel; single executor; not independent
review; not confirmatory; not population inference. The numeric thresholds are valid only for this
exact reader, masks, normalizer, weights, checkpoint, horizon, LawSpec and sealed panel.
