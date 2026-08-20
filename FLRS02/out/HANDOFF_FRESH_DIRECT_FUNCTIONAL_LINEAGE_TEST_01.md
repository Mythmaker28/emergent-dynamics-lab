# HANDOFF — FRESH DIRECT FUNCTIONAL LINEAGE TEST 01
## Successor to FLRS02. DO NOT EXECUTE INSIDE FLRS02.

    PARENT                 = FUNCTIONAL-LINEAGE-ROUTE-SELECTION-02
    PARENT_DISPOSITION     = ONE_EXISTING_POINT_DIRECT_TEST_JUSTIFIED
    SELECTED_POINT         = B1
    ESTIMAND               = P(joint functional two-centre success | B1), one world = one unit

## 1. The exact executable point — no interpolation

    kY     = 2.5118864315095822e-05
    muY    = 9.261187281287937e-05
    L      = 36
    L_large= 72
    CAP    = 16
    S0     = 3
    phi    = 0.2
    omega  = 0.05
    muX    = 0.004
    kX     = 1.0
    p_hop  = 0.10263340389897246
    X_SEED = 4

This is the parameter point PQEC01 already executed as Phase-B point B1. Nothing is
interpolated, no response surface is fitted, and no architecture is modified.

## 2. The frozen functional criterion — carried over unchanged

    PRIMARY   f_primary = 0.6321205588285577
              T_primary = 249.49966599830609 steps
    BAND      T_50 = 172.93999003737392
              T_80 = 401.55422159731904
              T_90 = 574.494211634693

A world counts as a functional two-centre success only if ALL SEVEN hold:

    1. at least one dynamic Y birth occurs
    2. the lineage does not go extinct before functional maturation
    3. exactly two spatial centres form under the frozen centre classifier
    4. both centres remain spatially distinct for at least T(f) consecutive steps
    5. both centres exhibit the required local X response
    6. no third centre appears BEFORE the functional maturation event
    7. X/source integrity remains acceptable until that event

Condition 5 is MEASURED, not inferred: the local X mass within CORE_R = 5.0
of the weaker centre's toroidal centroid, divided by the same quantity for the
stronger centre, must be at least f at the maturation event.

Founder identity is irrelevant. No genealogy may be constructed.
H_HOLD = 16 and the 101-birth threshold remain RETIRED and may not be reinstated.

## 3. Sample size, derived by exact binomial calculation

    MAX_PRIMARY_WORLDS       = 192
    RECOMMENDED_N            = 192
    ALPHA                    = 0.05  (one-sided)
    TARGET_POWER             = 0.80

Observed at B1 under the primary criterion: 13/44 = 0.2955,
exact 95% interval [0.1676, 0.4520].

Conservative planning uses the 95% LOWER bound p1 = 0.1676, not the point estimate:

    null p0 = 0.05   ->  n = 39
    null p0 = 0.075  ->  n = 73
    null p0 = 0.10   ->  n = 152

The largest null separable within 192 worlds under conservative planning is
p0 = 0.10499999999999998.

    THE NULL p0 MUST BE FROZEN IN THE PRE-RUN FREEZE, BEFORE THE FIRST WORLD.

FLRS02 does NOT inherit the old 0.50 threshold and does NOT substitute a new one
silently. p0 = 0.10 is the strongest null this budget can separate conservatively
(power 0.8653 at n = 192); adopting it is a decision to be recorded
explicitly in the successor's freeze, with its derivation, not assumed.

## 4. Comparability requirements — these are not optional

    FIXED_HORIZON            = identical for every world, and identical to PQEC01
    STOP_RULE                = identical to PQEC01, INCLUDING the stop at
                               PREMATURE_THIRD_CENTRE
    SEEDS                    = fresh and provably disjoint from every PQEC01 seed
    SPLIT                    = none; one pooled fresh sample

The stop rule must be preserved because removing it changes the estimand: a world
halted at a third centre might later return to two centres and mature, which would
raise the measured probability. Whether to remove it is a SEPARATE question and must
not be entangled with this confirmation.

## 5. Pre-registered reporting

Report the joint success rate and its exact binomial interval at ALL FOUR fractions.
The primary, pre-registered claim is at T_primary only.

    PRE-DECLARED LIMITATION: at T_90 a 192-world experiment is NOT decision-capable.
    The conservative lower bound there separates no null above 0.015.
    NO CLAIM MAY BE MADE AT T_90 FROM THIS EXPERIMENT.

## 6. Provenance requirements

    - commit the pre-run freeze alone, before the first world
    - the freeze must bind: python and numpy versions, every load-bearing source file
      by SHA256, the engine, the LawSpec, the observer, the runner, the centre
      classifier, the functional-response calculator, the sample-size code, the null
      p0, the decision gate and the final-disposition generator
    - no load-bearing source may change after any outcome is visible; if one does, the
      result is TECHNICALLY_INVALID and is not repaired
    - raw ledger and hashes committed before analysis
    - no hand-edited final JSON, no hardcoded True gate, no post-validation refit
    - external durable copy on Tommy's Windows disk BEFORE and AFTER execution

## 7. What this experiment can and cannot conclude

It can conclude whether functional two-centre formation at B1 occurs at a rate
separable from the frozen null within 192 fresh disjoint worlds.

It cannot conclude anything about reproduction, heredity, or H3, and it does not
license an architecture change. Those remain:

    H3_STATUS = NOT_TESTED
    REPRODUCTION_STATUS = NOT_TESTED
    HEREDITY_STATUS = NOT_TESTED
    AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
    X_LAWSPEC_BASELINE = UNCHANGED
    ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
