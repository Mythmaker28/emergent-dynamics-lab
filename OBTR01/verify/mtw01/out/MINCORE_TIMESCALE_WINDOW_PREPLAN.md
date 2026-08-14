# MINCORE_TIMESCALE_WINDOW_PREPLAN

**Frozen before the first start.** Everything below — every rate, every threshold, every
horizon, every predicted outcome and every decision rule — is fixed by `code/window.py` or by an
exact capacity argument, and is hashed into `out/_freeze.json` before `code/blocks.py` is run
once. Section 9 gives the provenance of every number, so that any reader can check that none of
them came from an outcome.

```
ENGINE_STARTS_BEFORE_THIS_DOCUMENT_IS_FROZEN = 0
STOCHASTIC_PROBES_OF_ANY_KIND                = 0
MAX_NEW_OUTCOME_INFORMATIVE_STARTS           = 16
PLANNED_BLOCKS = 4    PLANNED_ARMS_PER_BLOCK = 4    TECHNICAL_RESERVE = 0
```

---

## 1. Exact rate semantics, read from the frozen MINCORE source

From `MINCORE/code/mincore.py`, sha256 `f5ecd405…c385af1`, verified byte for byte
(addendum section 1). Per cell, per step, with `nX`, `nY` the counts in that cell:

```
_react()
    p_s     = min(1, k_s * nX * nY)                       s in {X, Y}
    cand_s  = min(n[res_s], max(free, 0))                 res_X = SX,  res_Y = SY
    free    = CAP - (nX + nY + nSX + nSY + nWX + nWY)
    births_s ~ Binomial(cand_s, p_s)
_decay()               d_s ~ Binomial(n[s], mu_s)
_diffuse(s, p_hop)     per direction: movers ~ Binomial(n, p_hop/4);
                       accepted = min(movers, dest_free); four directions per step
_feed_and_outflow()    SX,SY += Binomial(min(S0-n, free), phi);  WX,WY -= Binomial(n, omega)
```

Three structural facts follow, and all three are used below.

1. **The reaction converts, it does not add.** One resource unit becomes one product unit, so
   occupancy is invariant under `_react` and `free` is identical for the X and the Y sub-step.
2. **Every birth requires BOTH species in the SAME cell**, because both probabilities carry the
   factor `nX*nY`. `nX = 0` and `nY = 0` are exact invariant manifolds. There is no contact
   range beyond one cell, and there is no cohesive interaction of any kind.
3. **`cand` is the whole of the resource and capacity coupling.** Everything the resources and
   the volume exclusion can do to a rate, they do through `cand = min(n[res], free)`.

Mapped onto Kamimura and Kaneko's symbols:

```
a_X = muX        a_Y = muY                              per particle per step
R_Y = k_Y * nX* * c_Y  =  k_Y * Q                       per organiser, Q = nX* * c_Y
R_X = k_X * nX* * c_X                                   per organiser
D_X = p_hop_X / 4      D_Y = p_hop_Y / 4                since <r^2> = p_hop per step = 4*D
```

`Q = nX* * c_Y` is the **only** state-dependent factor in `R_Y`. Section 3 bounds it exactly.

---

## 2. Kamimura and Kaneko, and the re-derivation in dimension 2

Verbatim from arXiv:1005.1142v1 (Phys. Rev. Lett. 105, 268103):

```
X + Y -(p*gamma_X)-> 2X + Y        X + Y -(p*gamma_Y)-> 2Y + X
X -(a_X)-> 0                       Y -(a_Y)-> 0
r_X = p*gamma_X    r_Y = p*gamma_Y    R_Y = r_Y * nbar_X    gamma_X = 1-gamma_Y >= gamma_Y
extinction / division boundary :  a_Y < R_Y
division / explosion boundary  :  R_Y = D_Y * (a_X/R_X)^(2/3)
cluster size                   :  L_C ~ N_CX^(1/3)        separation time : tau_D = L_C^2/D_Y
```

One point deserves emphasis because it is where MINCORE departed from the mechanism: **KK use a
single diffusion constant `D = 1` for every species.** The minority character of `Y` is carried
by `gamma_Y`, not by a reduced mobility.

**Derivation of the upper boundary, then its generalisation.** The upper boundary is the
statement that the two organisers must move apart before a third appears:
`R_Y * tau_D <~ 1` with `tau_D = L_C^2/D_Y`. KK obtain `L_C` by packing: the number of body
molecules maintained around one organiser is `N_CX = R_X/a_X` (production `R_X` balanced by
decay `a_X`), and `N_CX` molecules packed at fixed density occupy a region of linear size
`N_CX^(1/3)` in three dimensions. Substituting,

```
R_Y  <  D_Y / L_C^2  =  D_Y * (a_X/R_X)^(2/3)              (d = 3, as printed)
```

In dimension `d` the same packing argument gives `L_C = N_CX^(1/d)`, hence

```
R_Y  <  D_Y * (a_X/R_X)^(2/d)         and for  d = 2   the exponent is 1:
R_Y  <  D_Y * a_X / R_X
```

**Two lower bounds on `L_C`, and the one that binds here.** MINCORE has no attractive potential,
so its cluster is not a condensed droplet. Both of the following are lower bounds on the linear
size of the material maintained by one organiser, and the larger one binds:

```
DIFFUSIVE   L_diff   = ell_X = sqrt(D_X/a_X)
            the body cloud is a diffusion-decay cloud; independent of every reaction constant
PACKED      L_packed = sqrt( N_CX / (pi * rho_max) )
            N_CX = R_X/a_X ; rho_max = (CAP - 2*S0)/(1 + a_X/omega), the largest sustainable
            body density once each body molecule carries its own steady-state waste
```

`R_X` is capped twice, kinetically by `k_X*Q_max` and by resource supply. A point sink in a
field relaxing to `S0` at rate `phi` has screening length `ell_S = sqrt(D_X/phi)` and can draw at
most `2*pi*D_X*S0/ln(1+ell_S)` units per step. At both the frozen MINCORE point and the design
point below, **`L_diff > L_packed`, so the diffusive bound binds** and `L_C = ell_X`.

**The separation time.** KK write `tau_D = L_C^2/D_Y` as a scaling form. The exact quantity is
the mean first passage of the *relative* coordinate of two organisers — diffusion constant
`D_rel = 2*D_Y` — from separation 0 to separation `Delta`. In two dimensions the mean exit time
from a disc of radius `Delta` started at its centre is `Delta^2/(4*D_rel)`, so

```
Delta   = 2 * L_C                       two clouds of radius L_C, just disjoint
tau_sep = Delta^2 / (8 * D_Y)           exact 2D first passage
```

At `Delta = 2*L_C` the KK scaling form `L_C^2/D_Y` is exactly **2x** larger than `tau_sep`; it is
reported alongside. Using the scaling form would place the design point far inside the window,
make every control block indecisive, and make every run eight times longer. A declared safety
factor `SF = 2` is applied on top of `tau_sep` in the design, to absorb the difference between a
free walker and one moving inside its own cloud under volume exclusion. `tau_design = 2*tau_sep`,
which happens to coincide numerically with the KK scaling form.

**The window, in the form that is actually adjudicated.** Let `H3` be the cumulative hazard of a
third organiser over the separation window, exactly as the handoff specifies:

```
H3(tau_sep) = INTEGRAL_0^tau_sep [ lambda_Y1(t) + lambda_Y2(t) ] dt ,  lambda_Yi = k_Y*nX_i*c_Y,i
P(no third organiser) = exp( -H3 )
```

For the engine the births are Bernoulli, not Poisson, so the **exact** version is used in the
code and reported as the primary quantity:

```
H3_exact = SUM over steps SUM over cells   cand_Y * ( -ln(1 - p_Y) )
P(no third organiser) = exp(-H3_exact)   EXACTLY, given the realised trajectory
```

`H3_kk = SUM cand_Y * p_Y` is recorded too, as the first-order form that matches KK's algebra.
Requiring `P >= P_star` gives, at a constant worst-case rate `R_Y`,

```
LOWER   R_Y > a_Y                                  (KK: a_Y < R_Y)
UPPER   R_Y <= -ln(P_star) / (2 * tau_design)
```

and, substituting `tau_design = 2*Delta^2/(8*D_Y)` and `L_C = sqrt(D_X/a_X)`, the window is
**non-empty if and only if**

```
   ( 2*SF*sep^2 / (8 * -ln P_star) ) * (a_Y/a_X) * (D_X/D_Y)  <  1
             coefficient = 18.9824  at  SF = 2, sep = 2, P_star = 0.90
```

This condition involves the two decay rates and the two diffusion constants **only**. It does
not involve `k_X`, `k_Y`, `CAP`, `S0`, `phi`, `omega`, or `Q`. That is what makes it adjudicable
in closed form.

---

## 3. Exact bound on `Q`, the only state-dependent factor

`Q = nX* * c_Y` with `c_Y = min(nSY, free)`, `free = CAP - occupancy`, and `nSY <= S0` because
nothing but the feed creates `SY` and the feed stops at `S0`. Maximising `Q` over **every**
occupancy vector the engine permits (exhaustive integer search, `code/window.py::q_bounds`):

```
Q_max = 27   attained at   nX = 9, nY = 1, nSX = 0, nSY = 3, waste = 0, free = 3, c_Y = 3
Q_min = 1    the smallest productive cell
```

This is a hard arithmetic bound, not an estimate. The design point is therefore required to keep
the **entire** reachable band `R_Y = k_Y * [1, 27]` inside the window, so that no assumption
about the realised `Q` is load-bearing.

---

## 4. Adjudication of the frozen MINCORE point — the window was empty

Evaluating the same formulas at the configuration that stopped
(`p_hop_X=0.20, p_hop_Y=0.002, muX=0.005, muY=0.0005, kX=0.02, kY=0.0008`):

| quantity | value |
|---|---|
| `ell_X`, `L_packed`, binding | 3.1623, 1.9446, **diffusive** |
| `Delta_sep`, `tau_sep`, `tau_design` | 6.325, 10 000, 20 000 steps |
| window lower edge `a_Y` | 5.0000e−4 |
| window upper edge (diffusive) | 2.6340e−6 |
| window upper edge (KK packed, `D_Y*(a_X/R_X)^1`) | 4.6296e−6 |
| non-emptiness left-hand side (must be < 1) | **189.82** |
| reachable band `k_Y*[1,27]` | 8.0e−4 … 2.16e−2 |
| `H3` at `Q_max` over one separation window | 432 |
| `P(no third organiser)` | ≈ 0 |

**The window was empty by a factor of 190, and the operating point sat above the upper edge by
between 304 and 8200 depending on `Q`.** The lower KK boundary was satisfied — `R_Y > a_Y`, so
the organiser replicated — but the upper one was violated by orders of magnitude, so a third
organiser was certain to appear long before any two could move apart.

This is a **derivation**, not a reading of the stopped run. It uses only the frozen `Spec` and
the frozen source; no saved output enters it. It happens to predict what the single saved
descriptor showed, and that agreement is reported as a consistency check and nothing more:
`OBSERVED_MECHANISM = CONSISTENT_WITH_Y_REPLICATION_TOO_FAST__NOT_PROVEN` stands unchanged.

The dominant single factor is `D_X/D_Y = 100`. MINCORE gave the organiser a hundredfold reduced
mobility in order to make it "the slow minority", but the upper edge of the window is
proportional to `D_Y`, so that choice divided the window by one hundred. In KK the minority
character is carried by `gamma_Y`, and `D_Y = D_X`.

---

## 5. The design point, and the adjudication

Fixed in this order, each value by one stated inequality:

| # | quantity | value | fixed by |
|---|---|---|---|
| 1 | `ell_X` | 2.5 sites | lattice resolution floor: the separation criterion `2*ell_X` must span several sites; every cost scales as `ell_X^2` |
| 2 | `D_X` | 0.25 (`p_hop_X = 1.0`) | the largest a lattice hop allows |
| 3 | `muX` | `D_X/ell_X^2` = 0.04 | forced by 1 and 2 |
| 4 | `D_Y` | 0.125 (`p_hop_Y = 0.5`) | `D_Y = D_X/2` puts the organiser's wander over one body lifetime at `sqrt(2)` cloud radii, so the cloud stays with its organiser. KK use `D_Y = D_X`; MINCORE's cluster has no cohesive potential, and this is the substitute |
| 5 | `k_X` | 1.0 | deliberately far above the marginal value for cloud existence; it enters **no** boundary of the window |
| 6 | `k_Y` | 1.9511206603301162e−05 | upper gate at the **worst case** `Q = Q_max = 27`, with margin 2 |
| 7 | `muY` | 1.9511206603301160e−06 | lower gate with margin 10 against `R_Y` at `Q_min = 1` |
| 8 | `L`, `CAP`, `S0`, `phi`, `omega` | 36, 16, 3, 0.05, 0.05 | `CAP, S0, phi, omega` inherited unchanged from the MINCORE frozen `Spec`; `L` from the torus geometry in section 6 |

Result (`out/_window.json`):

| quantity | value |
|---|---|
| `ell_X`, `L_packed`, binding | 2.5000, 2.3975, **diffusive** |
| `R_X` (resource cap binds over the kinetic cap 27) | 4.013 per step |
| `Delta_sep`, `tau_sep`, `tau_design` | 5.000, 25.0, 50.0 steps |
| coherence `chi` = organiser wander per body lifetime, in cloud radii | 1.414 |
| window `R_Y` | **(1.9511e−06 , 1.0536e−03)** |
| KK packed upper edge (looser, so not binding) | 1.2460e−03 |
| non-emptiness left-hand side (must be < 1) | **0.0018519** |
| reachable band `k_Y*[1,27]` | 1.9511e−05 … 5.2680e−04 — **entirely inside** |
| margin at the lower edge / at the upper edge | **10.0 / 2.0** |
| `H3` at `Q_max` (true `tau_sep` / with `SF`) | 0.02634 / 0.05268 |
| `P(no third organiser)` at `Q_max` | 0.9740 / 0.9487 |

```
ADJUDICATION = WINDOW_NON_EMPTY_WITH_MARGIN
```

The window is non-empty, and the entire arithmetically reachable band of `R_Y` lies inside it
with a factor 10 of margin at the lower edge and a factor 2 at the upper edge. **No stochastic
probe of any kind was used to reach this conclusion, and none has been run.**

---

## 6. Two changes to the engine, both decided here and both declared

`code/mtw.py` keeps the MINCORE species set, reaction scheme, candidate rule, decay, feed,
outflow and update order unchanged. Two things differ.

**Periodic boundary instead of reflecting.** At a fixed margin below the upper edge, `tau_div`
and `tau_sep` both scale as `1/D_Y`, so the distance a free organiser wanders during one
division cycle is **independent of `D_Y`**: it is `2*sqrt(4 * 3.91 * m) * L_C ~ 11 * L_C` at
margin `m = 2`. A reflecting box would need `L >~ 38 * ell_X` and would censor most arms — which
is exactly how MINCORE stopped. The absolute position of the cluster is irrelevant to the window;
only the relative separation of two organisers is. On a torus `L = 36` is ample: the separation
criterion is 5 sites, two separated clouds span about 15, and `L/2 = 18`.

**Cohort ledger disabled.** The three integer channels on `SX`, `SY`, `X`, `Y` exist to account
for donor versus receiver material. This mission uses no cohort observable. MINCORE integrity
test 8 established that cohort labels are causally inert — the same particles in different
channels give byte-identical species fields — so removing them leaves the law of the species
process unchanged, and removes 40 hypergeometric draws per step.

What is **not** changed: no lattice-wide reduction of any kind enters any rate. This is checked
by an AST pass over the real source, not asserted (`code/tests_mtw.py::ast_checks`), together
with the frozen update order, the absence of any clone/child/division operator, and the absence
of any public `advance` on `World`.

---

## 7. The two gates, the escapee rule, and the pass criterion

### 7.1 Preparation, identical in all four blocks

One organiser at the centre of the torus with `X_SEED = 4` body molecules in the same cell, all
resources at `S0`. Nothing is copied, no boundary is drawn, no cell is divided.

### 7.2 `G_X`, the body-cloud gate

Evaluated **once**, at `t = min(T_X, t_2)` where `t_2` is the step at which the second organiser
appears and `T_X = 100` steps (four body lifetimes; the cloud equilibrates on
`max(1/muX, ell_X^2/D_X) = 25` steps). All five conditions must hold:

```
organiser_count_one_or_two         1 <= N_Y <= 2 at the gate. The gate is evaluated at
                                   min(T_X, t_2); at t_2 the second organiser is already
                                   present, so one or two are legal there, three or none are not
body_cloud_present                 N_X >= N_X_MIN = 10
cloud_colocated_with_organiser     Rg of X about the organiser <= 3 * L_C = 7.5 sites
does_not_fill_torus                occupied support <= 0.25 * L^2
core_strength_sufficient           mean Q over the preceding T_Q = 50 steps >= Q_FLOOR = 6
```

A failure is recorded as `GATE_FAIL:<conditions>`; the start is consumed and the arm yields no
window evidence. If the block carries a perturbation it is applied **at the gate and nowhere
else**, so every block differs from block 1 in exactly one parameter at exactly one moment.

### 7.3 `G_Y`, the organiser-window gate

From `t_2` the hazard accumulator is armed and `H3_exact`, `H3_kk` are integrated over every
cell at every step. The window closes at the first of:

```
SEPARATED                 the two organisers reach torus distance >= Delta_sep = 5.0
EXPLOSION                 a third organiser appears
ORGANISER_LOST_IN_WINDOW  one of the two decays
EXTINCTION                no organiser remains
CENSORED_NO_SEPARATION / CENSORED_NO_DUPLICATION   the horizon is reached
```

Recorded per arm: `t_2`, `tau_sep_observed`, `tau_sep_predicted`, `H3_exact`, `H3_kk`,
`P(no third organiser) = exp(-H3_exact)`, the realised `Q` trace, `N_X`, `N_Y`.

### 7.4 Per-component minority, and the escapee rule

Two partitions are computed and both are written out.

**Organiser disc — primary, used by the pass criterion.** The disc of torus radius `L_C` about
each organiser. Deterministic, no threshold, no connectivity heuristic, and it is the quantity
the derivation is about. At separation exactly `Delta_sep = 2*L_C` the two discs are tangent, so
no site is double counted.

**Contact graph — secondary, descriptive only.** Connected components of the occupied mask under
4-connectivity **with wrap**. On a lattice gas a single stray body molecule can bridge two
clusters, so a component carrying no organiser and total mass `<= ESCAPEE_MAX_MASS = 2` is
labelled an **escapee**, listed separately, and excluded from the component count. This partition
is reported and never used to decide anything. Saying so before the run is the point: on the
torus there is no wall, so the MINCORE wall rule is replaced by `does_not_fill_torus` and by
this escapee rule.

**Pass criterion for one arm** (`observe.arm_verdict`):

```
outcome == SEPARATED
exactly two organisers present
each organiser disc contains exactly 1 organiser
each organiser disc contains >= MIN_BODY_PER_ORGANISER = 3 body molecules
each organiser disc satisfies the minority condition N_Y/(N_X+N_Y) <= MINORITY_MAX = 0.25
```

`MINORITY_MAX = 0.25` with one organiser per disc is equivalent to `N_X >= 3`; both are stated
because the first is the property being tested and the second is its arithmetic consequence.

---

## 8. The four blocks, their predictions, and the decision rule

All predictions below were computed by `code/blocks.py::predictions()` and written into the
freeze **before** the first start.

| block | single change, applied at the gate | horizon | predicted outcome | key predicted number |
|---|---|---|---|---|
| 1 `ONE_Y_FIXED_CORE` | none — the design point | 40 000 | `SEPARATED` | `H3 = 0.0146` at `Q_typ`, `0.0263` at `Q_max`; `P(no third) = 0.985 / 0.974`; `T_div = 3417` steps |
| 2 `WINDOW_UPPER_VIOLATED` | `k_Y * 300` | 5 000 | `EXPLOSION` | `H3 = 4.39`; `P(no third) = 0.0124`; `T_div = 11` steps |
| 3 `WINDOW_LOWER_VIOLATED` | `muY = 10 * R_Y(Q_typ)` | 5 000 | `EXTINCTION` or `ORGANISER_LOST_IN_WINDOW` | `P(duplicate before decay) = 1/11 = 0.0909` |
| 4 `SLOW_ORGANISER_MINCORE_MOBILITY` | `p_hop_Y = 0.002`, the literal MINCORE value | 40 000 | `EXPLOSION` | `tau_sep = 6250`; `H3 = 3.66`; `P(no third) = 0.0258` |

Block 4 is the block that tests the defect named in the addendum, and it changes **only** the
organiser's mobility. At MINCORE's *ratio* `D_Y = D_X/100` the prediction would be
`P(no third) = 0.48` — the boundary is crossed but not decisively — which is why the literal
MINCORE value `p_hop_Y = 0.002` is used instead. That is stated here rather than discovered later.

### Sequential rule

```
Block 1 runs first. ALL FOUR of its arms must PASS.
If they do not, no further block is started and the mission stops.
Blocks 2, 3, 4 each require AT LEAST 3 OF 4 arms to match their predicted outcome.
```

### Power

Per arm in block 1, `p1 = P(gate) * P(duplication within the horizon) * P(no third organiser)`.
`P(gate) = 0.98` and `P(duplication) = 0.99` are the assumed values written into the freeze;
`P(no third)` is derived: 0.9487 with the safety factor, 0.9740 without.

```
P(block 1 passes all four | the window is real)   = 0.718  to  0.797
P(block 1 passes all four | the window is absent) < 1e-6      (per-arm P(no third) <= 0.026)
P(a control block reaches 3 of 4 | its prediction is right, per-arm p >= 0.90) = 0.948
```

The 20 to 28 percent risk of a false stop at block 1 is the pre-registered price of the
"all four must pass" stringency. It is stated in advance so that a block-1 failure is read as
what it is — either a refutation or that price — and is adjudicated against the **measured**
`H3` and `tau_sep`, which are recorded for every arm whatever the outcome.

### Dispositions

```
4/4 in block 1 AND 3/4 in each of blocks 2,3,4
    -> MINORITY_TIMESCALE_WINDOW_PROSPECTIVELY_CONFIRMED__d2
4/4 in block 1, at least one control fails to fail
    -> WINDOW_CONSISTENT__MECHANISM_ATTRIBUTION_INCOMPLETE
block 1 fails with H3 measured well below its predicted bound
    -> WINDOW_NOT_CONFIRMED__FAILURE_NOT_ATTRIBUTABLE_TO_THE_HAZARD
block 1 fails with H3 measured at or above its predicted bound
    -> WINDOW_NOT_CONFIRMED__ANALYTIC_PREDICTION_REFUTED
```

None of these dispositions is, or licenses, a claim about reproduction, heredity, evolution,
organism, life, autopoiesis, fresh matter, biological mass, material lineage, the persistence of
an individual, or material ownership. "Separation" means one geometric event on a lattice: two
organisers reach a stated distance, each with body molecules around it. Nothing more.

---

## 9. Provenance of every number

| number | value | where it comes from | outcome-informed? |
|---|---|---|---|
| `CAP`, `S0`, `phi`, `omega` | 16, 3, 0.05, 0.05 | inherited unchanged from the MINCORE frozen `Spec`. `CAP` and `S0` were set there by two declared capacity probes | **inherited, already declared** in `MINCORE/out/_freeze.json`; not re-derived here |
| `Q_max = 27`, `Q_min = 1` | — | exhaustive integer search over the capacity constraint | no |
| `ell_X = 2.5` | — | lattice resolution floor and cost scaling | no |
| `D_X = 0.25`, `muX = 0.04` | — | largest lattice hop; then forced by `ell_X` | no |
| `D_Y = D_X/2` | 0.125 | coherence `chi = sqrt(2)`: the cloud stays with its organiser | no |
| `k_X = 1.0` | — | supra-marginal for cloud existence; enters no boundary | no |
| `k_Y`, `muY` | 1.9511e−5, 1.9511e−6 | upper gate at `Q_max` with margin 2; lower gate at `Q_min` with margin 10 | no |
| `P_star = 0.90`, `SF = 2`, `sep = 2` | — | declared before evaluation | no |
| `Delta_sep`, `tau_sep`, `tau_design` | 5.0, 25.0, 50.0 | closed form from `L_C` and `D_Y` | no |
| `T_X = 100`, `T_Q = 50` | — | four body lifetimes; the cloud equilibrates in 25 steps | no |
| `N_X_MIN = 10` | — | one tenth of the predicted `N_CX = R_X/a_X ~ 100`; deliberately loose | no |
| `RG_MAX_ELL = 3`, `FILL_MAX_FRAC = 0.25`, `ESCAPEE_MAX_MASS = 2` | — | declared, deliberately loose | no |
| `Q_FLOOR = 6` | — | 40 percent of `Q_typ`; below it the core cannot be adjudicated | no |
| `Q_TYP = 15` | — | closed-form estimate from the resource-supply cap `R_X = 4.01`, `N_CX = 100`, cloud area `pi*L_C^2`; used **only** to size horizons and to state predictions, never to set a rate | no |
| `MINORITY_MAX = 0.25`, `MIN_BODY_PER_ORGANISER = 3` | — | declared; equivalent to each other at one organiser per disc | no |
| horizons 40 000 / 5 000 | — | about 12x the predicted `T_div`, and 4x the predicted event time for the fast controls | no |
| seeds 101, 202, 303, 404 | — | declared before the first start | no |
| `P(gate) = 0.98`, `P(dup) = 0.99` | — | assumed, and written into the freeze so the power claim is falsifiable | no |

The single saved MINCORE descriptor (`N_X = 1186`, `N_Y = 1081`, and the rest) is used **nowhere
above**. It appears in the addendum as the record of what happened and is not an input to any
number in this preplan. Accordingly:

```
LEGACY_OUTPUT_USED_NUMERICALLY = NO
THIS_WORK_IS_EXPLORATORY_DEVELOPMENT = NO
```

---

## 10. Order of operations, and how it is enforced

```
0  scope-correction addendum (append-only, no run)
1  analytic adjudication (code/window.py)      -- no engine, no RNG, no trajectory
2  engine and observables written
3  integrity and mutation harness (code/tests_mtw.py) -- bounded, score-blind, 0 starts
4  FREEZE over the tested bytes and over this document
5  16 starts, block 1 first
6  final report
```

**Freeze chain.** Step 4 was executed twice, both times before any start. Freeze v1
(`METHODS_CORE_HASH = a6bddcd3...dc8668`) was superseded when a re-reading of the gate found that
it demanded exactly one organiser even when evaluated at the instant the second one appears,
which would have turned every early duplication into a spurious `GATE_FAIL`; the rolling `Q`
window was made always-defined at the same time. Both are corrections of the specification, made
with zero trajectories in existence, and the harness was re-run before freeze v2. The
superseded hash is recorded here so the chain is auditable.

Step 3 precedes step 4 so that fixing a test failure can never invalidate a freeze. The
separation between step 3 and step 5 is mechanical, not editorial: `guard.py` runs the harness in
`TEST` mode, where no start can be opened, the **total** number of steps across the whole harness
is capped at 3000, and every scoring function raises; and in `STATIC` mode, where the observables
and the verdict can be exercised on hand-built states but no world can be advanced at all. The
harness asserts at its end that it consumed zero starts. This is the mechanical form of the
correction recorded in `MINCORE_SCOPE_CORRECTION_ADDENDUM` section 6, and it is the reason the
`integrity.py` violation cannot recur.
