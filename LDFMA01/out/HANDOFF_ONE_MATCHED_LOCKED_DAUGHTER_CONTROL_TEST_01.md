# HANDOFF — ONE MATCHED LOCKED-DAUGHTER CONTROL TEST 01

```
SHORT_NAME  = OMLDCT01
PARENT      = LDFMA01 — LOCKED-DAUGHTER-FAILURE-MECHANISM-ARBITRATION-01
PARENT_DISPOSITION = LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__
                     ONE_MATCHED_CONTROL_TEST_ELIGIBLE
KIND        = ONE frozen matched-control experiment. Not a design mission, not a search.
STATUS      = CREATED, NOT EXECUTED. Authorising it is Tommy's decision.
```

This is one experiment, frozen. It is not a licence to design one.

## 0. Two preconditions, before world 1

**P1 — repair the event-attribution defect at the instrumentation level.** LDFMA01 measured that
the frozen endpoint attributes a ledger event to the component whose cell set contains it *at step
t*, while the archive writes cell rows *after* the step. A Y decay that empties a cell is therefore
invisible: across the 22 retrospective worlds the decay rate delivers **8.44** expected constituent
removals and the frozen rule counts **1**. The repair is to record, for every ledger event, the
component membership it had **at the moment the event occurred**. That changes no law, no
parameter, no classifier and no gate. It must be implemented, fixture-tested and frozen before
world 1.

Do **not** adopt LDFMA01's step-*t−1* re-attribution as the endpoint. It was a lower-bounding proxy
computed after the outcomes were known, it loses ~10 % of events to inter-step hops, and using it
would be post-outcome endpoint selection.

**P2 — publish the instrumented turnover count on a fixture before world 1.** With P1 in place,
the count of daughter constituent removals must reproduce the Poisson expectation
`λ = muY × particle-steps` on non-scientific fixtures. LDFMA01 verified that map retrospectively at
**5.809 predicted against 5 observed**; P2 checks the instrument, not the hypothesis.

## 1. The experiment

```
LAW              = LAW_C_MCTT01, exactly as bound in FIMRCC01_SELECTED_LAW.json
                   kY 0x3f50763f01e8e5b2  muY 0x3f484713dc1c8ab5  p_hop_Y 0x3fba462ec93926a0
NEW_PARAMETER_POINTS = 0
ARMS             = SELECTIVE_PARENT_REMOVAL and SHAM_NO_REMOVAL, matched on the same seed
TIME_ORIGIN      = t_m, the frozen trigger step, identical in both arms by construction
DESIGN           = fork at t_m. The arms are bit-identical up to t_m: the SHAM path is a proved
                   bit-exact no-op and the intervention leaves the generator hash unchanged in
                   22 of 22 retrospective worlds. The prefix is paid once per seed.
UNIT             = the base block (one seed, one trigger, both arms)
```

**PRIMARY ENDPOINT.** The locked daughter's **post-removal identity lifetime** — steps of survival
after `t_m` under the frozen strict link rule.

**CO-PRIMARY, pre-declared.** The locked daughter's **post-removal particle-step exposure**, the
sum over its interval of component `nY`. This is the quantity the verified Poisson map converts
into completion probability with no free parameter.

**DECISION RULE.** Wilcoxon signed-rank on the paired log difference, two-sided, α = 0.05, on both
the primary and the co-primary. Declared before world 1 and not revisable.

**BUDGET.**

```
MAX_PRIMARY_ARM_INSTANCES = 512
ONE INSTANCE              = one full-horizon world-equivalent of engine work, T = 11000
EXPECTED PAIRED BLOCKS    = 41 under the forked design (22 under independent full runs)
TRIGGER YIELD             = 22 of 256 LAW_C worlds, 8.6 %
MAX_TECHNICAL_RESERVES    = 6
```

**POWER, with its uncertainty.** Against a null of no paired difference, using the retrospective
completion rate 5/22 only to size the design:

| p(SELECTIVE) | power at 22 pairs | power at 41 pairs |
|---|---|---|
| 0.101 (Wilson lower) | 0.065 | 0.402 |
| 0.227 (point) | 0.582 | **0.971** |
| 0.434 (Wilson upper) | 0.988 | 1.000 |

The design is decision-capable at the point estimate and underpowered at the lower bound. That is
stated, not hidden.

## 2. The claim ceiling, binding

A positive result establishes **a causal effect of parent removal on the locked daughter's
post-removal exposure**. It does **not** establish reproduction, heredity, life or autonomous
cohesion, and it is not a turnover measurement. The forbidden vocabulary is unchanged: *organism*,
*daughter organism*, *life created*, *self-replication demonstrated*.

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED   HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

## 3. What LDFMA01 established that this test must not re-litigate

- The locked daughter is a **1-to-6 particle object holding the world's entire Y population** at the
  trigger: `parent_nY + daughter_nY = world_nY` in **22 of 22**.
- Its identity is closed by a split with exactly two successor candidates within `CORE_R` in
  **22 of 22**, at a median of **230** steps.
- **No available-before-outcome feature separates the sole success from the 21 failures.** There is
  no prospective eligibility criterion; do not attempt to enrich the sample.
- The `22/22` ambient endpoint measures a **late-time population**: zero complete intervals other
  than the daughter's own begin inside any daughter's window, and the bloom arrives 706–2 614 steps
  after the removal. Do not use an ambient endpoint.

## 4. Clauses inherited at birth — re-emit these verbatim

```
MEASUREMENT_NOT_POINT_SEARCH                             = true
ONE_ZERO_RUN_DETOUR_ONLY                                 = spent
SECOND_FINITE_SIZE_EXTENSION                             = forbidden
NEW_SIZE_LADDER                                          = forbidden
POST_OUTCOME_SIZE_RETUNING                               = forbidden
NEW_PARAMETER_SWEEP                                      = forbidden
GENERIC_CALIBRATION_SUCCESSOR                            = forbidden
INTERPOLATION                                            = forbidden
RESPONSE_SURFACE                                         = forbidden
EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES               = true
REOPENING_FINITE_SIZE_REQUIRES_EXPLICIT_HUMAN_AUTHORISATION = true
MAX_INDEPENDENT_CHECKERS                                 = 1
MAX_REVIEW_CASCADES                                      = 0
CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON    = mandatory
SECOND_TARGETED_MEASUREMENT_CAMPAIGN                     = forbidden
POST_OUTCOME_ENDPOINT_SELECTION                          = forbidden
MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS                      = 0
```

*Issued by LDFMA01 after a zero-run arbitration, one independent checker and one adjudication.
LDFMA01 does not execute it.*
