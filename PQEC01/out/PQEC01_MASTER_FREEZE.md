# PQEC01 — MASTER FREEZE (prospective)

> Committed **alone**, in its own commit, **before the first scientific start**. Nothing below
> may be changed after any outcome array is opened.

```
PROGRAM           PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01
PARENT_TIP        86291212955d4a4816efc1ebd671fbd234bf574c
METHODS_HASH      a1c910c870e92a2a8d33c8fdbc0d29224b7d02a7d9ab1c490383db2bd20e8142
INDEPENDENT_UNIT  ONE WORLD
```

## 1. Scientific question

Can a prospectively frozen, independently seeded calibration identify the event-aligned spatial environment encountered by one and two mobile Y lineages well enough to derive an executable (kY, muY) candidate region for a later, disjoint confirmatory test?

## 2. A finding declared BEFORE any run

**NO admissible (kY, muY) satisfies all five frozen boundaries simultaneously. The maximin point falls short by 0.1513 decades (a factor of 1.42); three boundaries are violated there at once: first-birth-not-too-rare, founder-not-extinct and no-premature-third-centre.**

*Why now:* this is a property of the FROZEN boundary arithmetic and the parent's measured magnitudes. It is computable before a single world runs, so it is preregistered rather than discovered later. Recording it after the fact would look like a post-hoc excuse.

*What it does not mean:* it is NOT structural preclusion, and it does NOT abort the calibration. PQEC01's task is to IDENTIFY the environmental operator from measured worlds, not to satisfy the window. The boundary arithmetic uses the parent's MEAN exposure as a proxy; the calibration replaces that proxy with measured, position-resolved, world-level quantities, which can move every boundary.

*Preregistered consequence:* the candidate-region derivation may return an EMPTY region. That outcome is declared admissible here, in advance, and will not be treated as a failure of the calibration or as grounds for retuning.

## 3. Phase A — Y-off spatial environment calibration

| field | value |
|---|---|
| `PURPOSE` | characterize the mobile source/X environment WITHOUT dynamic Y feedback |
| `kY` | 0.0 |
| `muY` | 0.0 |
| `p_hop_Y` | 0.10263340389897246 |
| `branch` | MOBILE |
| `X_SOURCE_LAWSPEC` | UNCHANGED (LAWSPEC_V2_EXCHANGE, frozen OBTC02 point) |
| `N_WORLDS` | 40 |
| `LABEL` | A0 |
| `RECORDS` | the full pre-reaction six-species field at EVERY step, plus all ledgers |

## 4. Phase B — low-count active-Y calibration

Initial condition: exactly one Y (the organiser), mobile branch, same X baseline. Points: 2. Worlds per point: **44**.

| point | role | `kY` | `muY` | selection rule |
|---|---|---|---|---|
| **B1** | central maximin point | `2.51189e-05` | `9.26119e-05` | argmax over the frozen log grid of the MINIMUM normalized distance to the five frozen boundaries; ties broken by first-encountered in the deterministic grid order |
| **B2** | operator-identification point | `2.15443e-05` | `1e-08` | argmax of expected co-located steps over the frozen coarse grid, restricted to points whose clamp and founder-extinction margins are at least B1's; evaluated on a frozen 2000-step design horizon so the score is a design quantity, not a prediction of the run |

Normalized boundary margins at B1, in decades (positive = inside):

```
first_birth_not_too_rare     -0.1447
no_immediate_clamp           +1.3959
founder_not_extinct          -0.1414
no_premature_third_centre    -0.1513
numerical_precision          +4.0333
MIN                          -0.1513   ALL_SATISFIED = False
```

Both points are frozen **before Phase A begins**; B2 was **not** selected after seeing B1.

## 5. Stop rules, in order

| id | condition |
|---|---|
| `EXTINCT` | N_Y == 0 (founder and all descendants gone) |
| `PREMATURE_THIRD_CENTRE` | N_CENTRES(t) >= 3, where a CENTRE is a single-linkage cluster of occupied Y cells at toroidal Euclidean distance <= CORE_R = 5.0 |
| `MAX_PERMITTED_Y` | N_Y > N_STAR = 10 |
| `INTEGRITY_FAILURE` | free(x) < 0 anywhere, or occupancy > CAP anywhere, or the organiser cell cannot be located while N_Y > 0 |
| `HORIZON` | t reaches T_HORIZON = 11000 |

The third-centre rule is the parent's frozen notion made per-world observable. `N_Y` and the
other proxies are recorded but are **not** adjudicative.

## 6. Sample sizes — derived, not decreed

**Phase A.** N_A = 40 exceeds both frozen floors (quantile 29, precision 27), attains a 0.81% relative standard error on the world-level mean exposure, and leaves the remaining budget divisible into two equal Phase-B points. It is not 'about thirty'.

- distribution-free 10th-percentile floor: `n >= ln(0.05)/ln(0.90)` = **29**
- precision floor at 1% relative SE: `n >= (sd/(0.01*mean))^2` = **27**
- chosen `N_A` = **40**, achieved relative SE **0.81%**

**Phase B.** N_B = 44 per point is the largest equal allocation of the remaining budget; it exceeds the mandated floor of 29 by 15 and bounds any unobserved per-world event rate above by 0.066 at 95%.

```
TOTAL_OUTCOME_INFORMATIVE_STARTS = 128   CAP = 128   WITHIN_CAP = True
```

## 7. Seeds

```
seed = 940000000 + int(SHA256(parent_tip|program|phase|point|index)[:12], 16) mod 50000000
band              [940000000, 989999999]
disjoint from     the OBFOR01 development band 9300000-9300027 and the non-scientific fixture band 77000001-77900001
collision         deterministic re-hash with index + 10000*bump; never manual
unique seeds      True
```

All 128 scientific seeds and 15 reserve seeds are published in `PQEC01_MASTER_FREEZE.json`.

## 8. Analysis split — by seed hash, never by outcome

```
DISCOVERY if int(SHA256('SPLIT|parent_tip|seed')[:8],16) mod 3 < 2 else VALIDATION -- a hash of the FROZEN SEED, never of an outcome
```

| set | discovery | validation |
|---|---|---|
| A | 31 | 9 |
| B1 | 29 | 15 |
| B2 | 28 | 16 |

## 9. Frozen analysis formulas

```
free                     CAP - (nX+nY+nSX+nSY+nWX+nWY)
candidate_Y              min(nSY, free)
candidate_X              min(nSX, free)
Q_POSITION               nX * min(nSY, free)
world_exposure_E_w       mean over t in [BURN_IN, T_end) of Q at the founder cell
world_low_quantile_S_w   the 10th percentile over t in [BURN_IN, T_end) of the founder-cell Q
branch_lower_bound       the MINIMUM over worlds of S_w; with N >= 29 this is a 95% one-sided distribution-free lower bound for the 10th world-level percentile
exact_first_birth_law    P(no Y birth in world w) = prod_t (1 - p_t)^(c_t), with p_t = min(1, kY*nX_t*nY_t) and c_t = min(nSY_t, free_t) at the occupied Y cell -- the engine's own binomial, not an approximation
radial_exposure          mean of Q_POSITION over cells at toroidal distance in [r, r+1) from the source, averaged over t, then over worlds
feedback_delta           E_B[.] - E_A[.] for nSY, free and N_X, compared at the DISTRIBUTION level across worlds; never as a paired trajectory
colocation_duration      number of consecutive steps with >= 2 Y in one centre
separation_time          first step at which two centres exist, measured from the first birth
uncertainty              world-level; the estimator of any branch quantity is the mean over worlds and its standard error uses N_worlds, never N_frames
```

## 10. Inclusion and technical invalidity

Every started world is included. **Not** technical invalidity: extinction, no birth, no separation, low Q, high Q, boundary contact, an unfavourable scientific outcome.

Technical invalidity only: corrupt serialization, process interruption, observer schema failure, checksum failure, engine invariant violation (free < 0 or occ > CAP).

a technically invalid world is replaced by the next unused reserve seed, in the frozen order; BOTH the failed start and the replacement are counted and appear in the run ledger

## 11. Outcome firewall

During execution, inspect only: process return code, expected file existence, file size, schema, checksum, the technical-validity flags defined above.

Do not inspect until every scheduled start is complete: Y birth counts, extinction, separation, Q, spatial profiles, third-centre outcomes, any primary scientific value.

## 12. Terminal dispositions and decision gates

```
PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED
PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED
EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW
CALIBRATION_TECHNICALLY_INVALID
```

All of these must hold for the positive disposition:

```
PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS
INSTRUMENTATION_INERTNESS
ALL_FROZEN_STARTS_ACCOUNTED_FOR
NO_OUTCOME_DRIVEN_REPLACEMENT
PHASE_A_SPATIAL_OPERATOR_IDENTIFIED
PHASE_B_REAL_DESCENDANT_EXPOSURE_RECORDED
FIRST_BIRTH_OPERATOR_VALIDATED
TWO_Y_OPERATOR_IDENTIFIED
FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED
INTERNAL_VALIDATION_PASS
CANDIDATE_REGION_POSITIVE_WIDTH
NO_SINGLE_WORLD_DOMINANCE
NO_FRAME_PSEUDOREPLICATION
```

## 13. Forbidden in this programme

```
reproduction claim
heredity claim
autonomous cohesion claim
life claim
architecture change
new species
new physics state variable
adaptive retuning
outcome-driven seed/horizon/sample-size change
arm replacement after scientific failure
manuscript drafting
```

```
TOMMY_ACTION_REQUIRED = NONE
```
