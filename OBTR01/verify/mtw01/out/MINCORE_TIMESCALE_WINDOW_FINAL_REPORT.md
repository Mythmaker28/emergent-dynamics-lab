# MINCORE_TIMESCALE_WINDOW_FINAL_REPORT

```
MISSION                          MINCORE-TIMESCALE-WINDOW-01
METHODS_CORE_HASH                2d48ecadbd779a657a301220e7ceb7c136f6f8f1e3a66a17f81a19a2995a647e
ANALYTIC_ADJUDICATION            WINDOW_NON_EMPTY_WITH_MARGIN
STOCHASTIC_PROBES_BEFORE_FREEZE  0
OUTCOME_INFORMATIVE_STARTS_USED  4 of 16          TECHNICAL_RESERVE = 0
BLOCKS_COMPLETED                 1 of 4 planned; the frozen sequential rule stopped the mission
DISPOSITION                      WINDOW_NOT_CONFIRMED__FAILURE_NOT_ATTRIBUTABLE_TO_THE_HAZARD
```

---

## 1. What was asked, and what is established

The mission had three parts: correct the MINCORE scope append-only; re-derive the
Kamimura–Kaneko minority window in dimension 2 and adjudicate it **analytically**, with any
stochastic probe forbidden; and, only if a non-empty window with margin was demonstrated, spend
up to sixteen starts testing it.

All three parts were executed in that order. The results:

| part | result |
|---|---|
| byte recovery and verification | all twelve declared SHA-256 verified; `MINCORE_BYTES = INDEPENDENTLY_VERIFIED` |
| scope correction | written append-only, no run; the `integrity.py` arm recorded as a protocol-order violation; the ledger audited and a machine under-count of one found and explained; the bilinear impossibility statement withdrawn with an explicit stable counterexample |
| `d = 2` window, analytic | derived in closed form; the frozen MINCORE point has an **empty** window by a factor of 190; a derived design point has a **non-empty** window containing the entire arithmetically reachable band with margins 10 and 2 |
| 16 starts | block 1 opened, 4 arms, 0 passed; the frozen rule stopped the mission with 12 starts unused |
| what the four arms tested | **not the window.** The cumulative hazard `H3` summed to exactly `0.0` across all four arms, because no second organiser ever appeared. The failure is in the preparation, not in the hazard |

---

## 2. The window in dimension 2, derived

Kamimura and Kaneko give two boundaries, `a_Y < R_Y` and, in three dimensions,
`R_Y = D_Y*(a_X/R_X)^(2/3)`, with `L_C ~ N_CX^(1/3)`, `N_CX = R_X/a_X`, `tau_D = L_C^2/D_Y`.
Repeating the packing argument in dimension `d` gives `L_C = N_CX^(1/d)` and therefore

```
a_Y  <  R_Y  <  D_Y * (a_X/R_X)^(2/d)          d = 2  =>  exponent 1
```

Three refinements were needed to make this adjudicable for MINCORE and all three are stated in
the preplan before any start.

**`L_C` is diffusive here, not packed.** MINCORE has no attractive potential, so its cluster is a
diffusion–decay cloud of size `ell_X = sqrt(D_X/a_X)`, not a condensed droplet. Both lower bounds
were computed and the larger one taken; at both the frozen point and the design point the
diffusive one binds.

**The separation time is a first passage, not a scaling form.** `tau_D = L_C^2/D_Y` is a scaling
statement. The exact quantity is the mean first passage of the relative coordinate of two
organisers, diffusion constant `2*D_Y`, from 0 to `Delta = 2*L_C`, which in two dimensions is
`Delta^2/(8*D_Y)` — a factor 8 smaller than the naive `Delta^2/D_Y`. Both are reported; a
declared safety factor 2 is carried in the design.

**The upper boundary is a hazard, not an inequality between two numbers.** With two organisers
present, the cumulative hazard of a third over the separation window is
`H3 = INT [lambda_Y1 + lambda_Y2] dt` and `P(no third) = exp(-H3)`. For this engine the births
are Bernoulli, so the exact form `H3 = SUM_t SUM_cells cand_Y * (-ln(1-p_Y))` is used, and
`P = exp(-H3)` is then exact given the trajectory.

The window is then **non-empty if and only if**

```
   ( 2*SF*sep^2 / (8 * -ln P*) ) * (a_Y/a_X) * (D_X/D_Y)  <  1
             coefficient 18.9824 at SF = 2, sep = 2, P* = 0.90
```

a condition on the two decay rates and the two diffusion constants **only**. It does not involve
`k_X`, `k_Y`, `CAP`, `S0`, `phi`, `omega`, or the state.

### 2.1 The frozen MINCORE configuration had an empty window

| quantity | frozen MINCORE point |
|---|---|
| non-emptiness left-hand side (must be < 1) | **189.82** |
| window lower edge `a_Y` / upper edge | 5.00e−4 / 2.63e−6 |
| reachable band `k_Y*[1,27]` | 8.0e−4 … 2.16e−2 |
| `H3` over one separation window at `Q_max` | 432 |
| `P(no third organiser)` | ≈ 0 |

The lower KK boundary was satisfied, so the organiser replicated. The upper one was violated by
between 304 and 8200 depending on the local state, so a third organiser was certain long before
any two could move apart. **The dominant single factor is `D_X/D_Y = 100`:** MINCORE gave the
organiser a hundredfold reduced mobility to make it "the slow minority", and the upper edge of
the window is proportional to `D_Y`, so that one choice divided the window by one hundred. In
Kamimura and Kaneko the minority character is carried by the synthesis fraction `gamma_Y`, and
`D_Y = D_X` for every species.

This is a derivation from the frozen source. No saved output enters it. It agrees with the single
saved descriptor, and that agreement is reported as a consistency check and nothing more:
`OBSERVED_MECHANISM = CONSISTENT_WITH_Y_REPLICATION_TOO_FAST__NOT_PROVEN` stands.

### 2.2 The window is not empty in general

At the derived design point (`ell_X = 2.5`, `D_X = 0.25`, `D_Y = D_X/2`, `k_Y = 1.9511e−5`,
`muY = 1.9511e−6`), the non-emptiness left-hand side is **0.0018519**, the window is
`R_Y in (1.95e−6, 1.05e−3)`, and the entire arithmetically reachable band
`R_Y = k_Y*[Q_min, Q_max] = k_Y*[1,27] = [1.95e−5, 5.27e−4]` lies inside it with a factor 10 of
margin at the lower edge and a factor 2 at the upper edge. `Q_max = 27` is an exact integer
capacity bound, obtained by exhaustive search over every occupancy vector the engine permits.

```
ADJUDICATION = WINDOW_NON_EMPTY_WITH_MARGIN     established with zero stochastic probes
```

---

## 3. What the four starts showed

Block 1, `ONE_Y_FIXED_CORE`, four seeds, design parameters, horizon 40 000 steps.

| seed | outcome | `N_X` at the gate | `Q` at the gate | `Q` time-averaged | `N_X` at the end | `H3` |
|---|---|---|---|---|---|---|
| 101 | `GATE_FAIL` | 0 | 0.00 | — | 0 | 0 |
| 202 | `GATE_FAIL` | 0 | 0.00 | — | 0 | 0 |
| 303 | `GATE_FAIL` | 1 | 0.00 | — | 1 | 0 |
| 404 | `CENSORED_NO_DUPLICATION` | 35 | 7.04 | **0.0608** | **0** | 0 |

Three arms never grew a body cloud at all. The fourth grew one, passed all five gate conditions,
and then lost it: over 40 000 steps the realised `Q` averaged 0.0608 — that is, the organiser's
cell was essentially always empty of body molecules — and the cloud reached `N_X = 0`, which is
an absorbing state because every birth probability carries the factor `nX*nY`. The organiser
itself survived, as designed, and never duplicated.

```
TOTAL H3 ACCUMULATED ACROSS ALL FOUR ARMS = 0.0
```

The hazard was never accumulated, because no second organiser ever appeared. **The window
prediction was not tested, not confirmed and not refuted.** That is exactly the pre-registered
disposition `WINDOW_NOT_CONFIRMED__FAILURE_NOT_ATTRIBUTABLE_TO_THE_HAZARD`, and the frozen
sequential rule — all four arms of block 1 must pass before any other block is started — fired
and stopped the mission with twelve starts unused.

---

## 4. The inequality that was missing, and it was missing from my own preplan

The MINCORE static gate tested that a body cloud **grows** and that it fits the domain, but not
whether new organisers appear faster than existing ones can move apart. The addendum records that
as `STATIC_LOCALIZATION_GATE = INCOMPLETE__DEFECT_DISCOVERED_POST_START`. The MTW01 preplan
supplied the missing timescale comparison — and then made an omission of exactly the same kind.

It gated the body cloud **at one instant**, at `t = min(T_X, t_2)`. It did not gate the cloud's
**self-maintenance over the whole window**. The following is an exact consequence of the frozen
rate semantics and would have been true whether or not any arm had run:

```
DERIVED_FROM_SOURCE
   cand_X = min(n[SX], free)  and  n[SX] <= S0
   => ONE organiser cell can convert at most S0 resource units per step
   => the body cloud it maintains obeys the exact bound   N_X <= S0 / muX
   and  N_X = 0  is absorbing, because every birth probability carries the factor nX*nY
```

| | `S0/muX` = hard cap on the cloud around one organiser |
|---|---|
| frozen MINCORE point (`muX = 0.005`) | **600** |
| MTW01 design point (`muX = 0.04`) | **75** |

`muX = 0.04` was not chosen carelessly: it is forced by `ell_X = 2.5` once `D_X` is set to the
largest value a lattice hop allows, and `D_X` was made large to keep `tau_sep` and therefore the
run length small. **The choice that made the runs affordable is the same choice that capped the
body cloud at 75 molecules next to an absorbing state.**

A self-consistency calculation confirms it quantitatively, using only the frozen semantics. Let
`G(0)` be the expected number of steps a body molecule spends in the cell where it was created,
including diffusive returns; production is `S = c_X * P(at least one body molecule in the
organiser's cell)`; with a Poisson closure the occupancy there solves
`u = c_X*G(0)*(1 - exp(-u))`, which has a positive root **iff `c_X*G(0) > 1`**.

| point | `G(0)` | `c_X*G(0)` at `c_X = S0 = 3` | `c_X*G(0)` at `c_X = phi*S0 = 0.15` | predicted `N_X` |
|---|---|---|---|---|
| MTW01 design | 2.093 | 6.28 (supercritical) | **0.314 (subcritical)** | 0 … 75 |
| frozen MINCORE | 9.207 | 27.62 (supercritical) | **1.381 (supercritical)** | 15 … 600 |

The two brackets on `c_X` — the hard cap `S0`, and the purely local feed `phi*S0` available to a
stationary organiser — straddle the critical line at the design point and do **not** straddle it
at the frozen MINCORE point. In other words: MINCORE's body cloud was robustly supercritical
(and indeed grew until it filled the domain), whereas the MTW01 design point sits **on** the
critical line. The observed arm that established reached `N_X = 35`, between the two brackets,
and then went extinct — which is what a small population beside an absorbing state does.

```
BODY_CLOUD_SELF_MAINTENANCE_GATE = MISSING_FROM_THE_MTW01_PREPLAN
CAUSE_OF_THE_BLOCK_1_STOP        = SUBCRITICAL_OR_CRITICAL_BODY_CLOUD__NOT_THE_HAZARD
c_X_SUSTAINABLE                  = BRACKETED_ONLY, in [phi*S0, S0] = [0.15, 3]
```

`c_X` — the sustainable candidate count in the organiser's own cell, for an organiser that is
itself diffusing through a resource field that recovers at rate `phi` — is the one quantity in
this model that has resisted a tight closed-form bound. Naming it is the useful output: it is
precisely what a future mission must measure first, and cheaply.

---

## 5. Is the three-condition region non-empty?

Three conditions must now hold **simultaneously**: body-cloud self-maintenance
(`c_X*G(0) > 1`, with a cloud large enough to resist stochastic extinction), the KK lower
boundary `a_Y < R_Y`, and the KK upper boundary in the hazard form. A closed-form scan
(`code/postmortem.py`, no run) over `N_ROBUST` and `ell_X`:

| `N_ROBUST` | `ell_X` | `p_hop_X` | `c_X*G(0)` at the pessimistic `c_X` | `tau_sep` | `k_Y` | `T_div` at `Q = 7` | self-maintenance |
|---|---|---|---|---|---|---|---|
| 100 | 2.5 | 0.750 | 0.39 | 33.3 | 1.46e−5 | 9 762 | fails |
| 300 | 2.5 | 0.250 | 1.04 | 100.0 | 4.88e−6 | 29 287 | marginal |
| 1000 | 2.5 | 0.075 | 3.32 | 333.3 | 1.46e−6 | 97 624 | **holds with margin** |
| 1000 | 3.0 | 0.108 | 2.46 | 333.3 | 1.46e−6 | 97 624 | **holds with margin** |

The direction is unambiguous: **reducing `p_hop_X` at fixed `ell_X` satisfies self-maintenance
linearly, and costs run length linearly.** The region where all three conditions hold is
non-empty, at a price of roughly 100 000 steps per arm instead of 3 400 — about thirty times the
cost of the point tested here, and still affordable.

Two honesty markers on that table. First, it uses the *pessimistic* bracket for `c_X`; the
predicted cloud size at those points is bracketed between about 45 and `N_ROBUST`, and which end
holds depends on the unbounded `c_X`. Second, and more important:

```
ANY PARAMETER POINT SELECTED USING THIS TABLE IS OUTCOME_INFORMED,
because the need for the third condition was revealed by the block-1 stop.
No such point is selected here, and none is run here.
```

The inequalities themselves are `DERIVED_FROM_SOURCE` and would be true with no run at all. The
decision of *where* to test next is not, and it belongs to a mission with its own declared budget.

---

## 6. Protocol integrity

The MINCORE violation — a full arm executed inside an integrity harness — is now prevented by the
code rather than by intention. `code/guard.py` runs three modes: `TEST`, where no start can be
opened, the **total** number of steps across the whole harness is capped at 3000, and every
scoring function raises; `STATIC`, where scoring can be exercised on hand-built states but no
world can be advanced at all; and `EXPERIMENT`, where every advance must be inside an open start
and starts are capped at 16. `mtw.World` exposes no public `advance`, so `guard.advance` is the
only path forward in time. The harness asserts at its end that it consumed zero starts.

| | |
|---|---|
| integrity tests | 26, all PASS |
| mutations injected into the real gate, verdict and budget path | 13, all DETECTED |
| test steps used | 721 of 3000 |
| starts consumed by the harness | **0** |
| AST checks on the real source | no lattice-wide reduction enters any rate; the two diagnostic accumulators are write-only in every operator; every `.any()` is a branch guard only; no clone, child or division operator; no public `advance`; the frozen update order unchanged |

The freeze was taken twice, both times before any start. Freeze v1
(`a6bddcd3…dc8668`) was superseded when re-reading found that the gate demanded exactly one
organiser even when evaluated at the instant the second appears, which would have turned every
early duplication into a spurious failure. Freeze v2 (`2d48ecad…995a647e`) is the one under which
the four arms ran. Both hashes are recorded so the chain is auditable.

```
LEDGER (machine-audited, cross-checked against its own log)
  starts consumed  4      log entries 4      consistent TRUE
  max_starts 16          technical_reserve 0
  1  ONE_Y_FIXED_CORE/seed101     100 steps
  2  ONE_Y_FIXED_CORE/seed202     100 steps
  3  ONE_Y_FIXED_CORE/seed303     100 steps
  4  ONE_Y_FIXED_CORE/seed404   40000 steps
```

---

## 7. Status fields

```
MINCORE_BYTES                              = INDEPENDENTLY_VERIFIED
FROZEN_MINCORE_CONFIGURATION               = SOURCE_LOCALIZATION_AND_MINORITY_GATE_FAIL
STATIC_LOCALIZATION_GATE                   = INCOMPLETE__DEFECT_DISCOVERED_POST_START
CAUSAL_ARMS_COMPLETED (MINCORE)            = 0
BILINEAR_MINORITY_CORE_FAMILY              = NOT_CLOSED
Y_SATURATION_MATHEMATICALLY_REQUIRED       = NOT_ESTABLISHED
OBSERVED_MECHANISM (MINCORE)               = CONSISTENT_WITH_Y_REPLICATION_TOO_FAST__NOT_PROVEN

MINORITY_TIMESCALE_WINDOW_d2               = DERIVED_ANALYTICALLY
FROZEN_MINCORE_POINT_INSIDE_THE_WINDOW     = NO__EMPTY_BY_A_FACTOR_190
WINDOW_NON_EMPTY_IN_THE_MODEL_FAMILY       = YES__WITH_MARGIN_10_AND_2
WINDOW_TESTED_PROSPECTIVELY                = NO__H3_NEVER_ACCUMULATED
BODY_CLOUD_SELF_MAINTENANCE_GATE           = MISSING_FROM_THE_MTW01_PREPLAN
N_X_HARD_CAP_PER_ORGANISER                 = S0/muX   (75 at the design point, 600 at MINCORE)
c_X_SUSTAINABLE                            = BRACKETED_ONLY__[phi*S0, S0]
THREE_CONDITION_REGION                     = NON_EMPTY__NOT_TESTED
RECONSTRUCTION_TESTING                     = STILL_NOT_ELIGIBLE
```

No claim of reproduction, heredity, evolution, organism, life, autopoiesis, fresh matter,
biological mass or material lineage is made or implied. No claim that the same individual
persists, and none that material ownership is proven. "Separation" would have meant one geometric
event on a lattice; it did not occur, and nothing stands in its place. Stability of a fixed point
under a linearisation is not independent replication, and a known non-zero descriptive quantity
is not a non-zero population effect.

```
ENGINE_STARTS_USED             = 4 of 16
STOCHASTIC_PROBES_BEFORE_FREEZE = 0
REPOSITORY_HISTORY_REWRITTEN   = NO
PREEXISTING_RESULTS_ALTERED    = NO
TOMMY_ACTION_REQUIRED          = NONE
```
