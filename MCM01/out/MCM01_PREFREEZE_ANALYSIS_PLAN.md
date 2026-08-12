# MCM01_PREFREEZE_ANALYSIS_PLAN

`MINCORE-CLOUD-MAINTENANCE-01`. Written and hashed **before the first calibration start**.
Section 12 gives the provenance of every number.

```
QUESTION      Is there, in the current model family and at a still practical cost, a
              PRE-REGISTERED point at which the body cloud X maintains itself long enough to
              make the minority timescale window testable later?
NOT TESTED    H3, the timescale window itself, reconstruction, reproduction, heritability,
              individuality, or any higher-level behaviour. A success here makes a LATER
              mission eligible and establishes nothing else.
BUDGET        cost_probe 2, calibration 8, confirmation 6, control 10. Enforced per class.
```

---

## 1. Étape A: what was reproduced, and what had to be corrected

Every load-bearing claim inherited from MINCORE and MTW01 was re-derived independently
(`code/audit.py`, `out/_audit.json`): 8 reproduced, 7 reproduced with a correction, 0 lost.

| claim | verdict |
|---|---|
| MTW01 and MINCORE manifests (20 + 12 files, both bundles) | REPRODUCED, 0 mismatches |
| `D = p_hop/4` | **CORRECTED.** `_diffuse` applies four direction attempts per step, so a particle can move and move back within one step: `D_eff = q(1−q)` with `q = p_hop/4`. Error −5 % at `p_hop = 0.2`, **−25 % at `p_hop = 1`**. MINCORE and MTW01 both used `p_hop/4`. |
| `cand_X ≤ S0` | **CORRECTED, the claim is false.** `_diffuse` accepts `min(movers, dest_free)`, capped by free capacity and **not** by `S0`, so a cell can hold more than `S0` resource units. Exhaustive integer search gives `max cand_X = 7` at `CAP = 16`. |
| `N_X ≤ S0/muX` | **CORRECTED, not an exact bound.** The exact per-organiser bound is `N_X ≤ 7/muX`. Neither is operative: the sustainable supply is transport limited (below). |
| `Q_max = 27` | **CORRECTED.** 27 is reproduced *under MTW01's restriction* `n[SY] ≤ S0`. That restriction is unsound for the same reason, and the exact maximum is **28**, at `nX = 7, nSY = 4, free = 4`. |
| `N_X = 0` is absorbing | REPRODUCED, by AST (only `_react` increases `n["X"]`, and both birth probabilities carry `nX*nY`) and by a bounded score-blind synthetic run. |
| definition of `G(0)` | **CORRECTED.** MTW01 used the walk of X alone. The organiser moves too, and the source needs *co-location with the organiser*, so the correct walk is the relative one and `G(0)` is the value for `Δ_X − Δ_Y`. The X-only walk overstates `G(0)` by 24 % at the MTW01 point. |
| `c_X` bracketed in `[phi·S0, S0]` | **CORRECTED and tightened.** The sustainable supply to one absorbing cell is `c_X = S0/G_S(0)`, a lattice Green's function evaluation. At the MTW01 point this is **1.342**, inside the old bracket `[0.15, 3]` and far tighter. |
| MTW01 was "subcritical or critical" | **CORRECTED, and this is the substantive one.** At the MTW01 design point `c_X·G(0) = 2.53 > 1`: the point was **supercritical**. The maintenance condition is *not* what failed. What failed is that `N_X* = c_X/muX = 33.5`, and the transport bound predicts 33.5 against the 35 recorded — with no free parameter. A quasi-stationary population of ~34 beside an absorbing state does not survive. |
| **1519 versus 190** | **RESOLVED.** Both are the same quantity, the non-emptiness left-hand side at the frozen MINCORE point, under two conventions for the separation time: `τ = Δ²/D_Y` gives **1518.6**, the exact 2D first passage `τ = Δ²/(8·D_Y)` gives **189.8**. The ratio is exactly **8.0000**, the first-passage correction and nothing else. 1519 appeared only in an intermediate console evaluation and is superseded. With the corrected `D_eff` the traceable final value is **180.4**. In every convention the window at the frozen MINCORE point is empty by two to three orders of magnitude, so the conclusion is unchanged. |
| margins 10 and 2 | REPRODUCED. Both are **linear** ratios recomputed from the frozen `_window.json`; no logarithmic convention. |
| the "×30" cost | REPRODUCED as 28.6, and it applies to a *future window* mission, whose cost is set by the organiser duplication time. The present mission measures maintenance, whose cost is set by the body-molecule lifetime. |

---

## 2. `c_X`: exact definition

`_react` computes, per cell,
`cand_X = min(n[SX], max(free, 0))`, `free = CAP − (nX+nY+nSX+nSY+nWX+nWY)`,
then draws `births_X ~ Binomial(cand_X, min(1, kX·nX·nY))`.

```
c_X(t) := cand_X evaluated at the organiser's cell, at the reaction sub-step of step t
```

It is literally the `n` parameter of the binomial draw the engine is about to make at the only
cell where body molecules can be created.

| property | value |
|---|---|
| mathematical form | `min(n[SX](z), CAP − occ(z))` at the organiser cell `z` |
| engine variables | `self.n["SX"]`, `self.free()`, `self.n["Y"] > 0` |
| unit | resource units converted per step (a count, integer) |
| timescale | one step; reported as a full distribution over the window, never as a bare mean |
| local or global | strictly local: one cell |
| geometry | through `free`, hence through the local occupancy only |
| depends on X density | yes, through `free` |
| depends on free capacity | yes, by definition |
| depends on the organiser count | yes: reported both summed over organiser cells and per organiser |
| depends on boundaries | on a torus, only through the cluster's own periodic image; monitored and gated |
| depends on `D_X`, `D_Y`, `S0`, `muX`, `phi` | through the resource transport that refills the cell; see the certified bound below |
| depends on `gamma_X`, `gamma_Y` | in this engine the analogues are `kX`, `kY`; `c_X` does not depend on either, since `cand` is computed before the probability is applied |

**Method priority, as required.** (1) exact computation from the state and the transition rule —
adopted, this is what the recorder does; (2) certified bound with a stated direction of
conservatism — also computed, `c_X ≤ min(7, S0/G_S(0))`; (3) direct measurement from raw logs —
the recorder writes every step to disk; (4) pre-registered statistical estimation — not needed;
(5) a proxy — not used.

**Certified transport bound.** A perfectly absorbing cell in a field fed at rate `phi` toward
`S0` draws `J = S0/G_S(0)` per step, with `G_S(0)` the lattice Green's function of the resource
walk at survival `1 − phi`. The linearised feed, the neglect of exclusion on the resource and the
perfectly absorbing sink all make this an **upper** bound on the sustainable `c_X`. The gate is
therefore never flattered by it.

**The recorder does not change the law.** `RecWorld` overrides `_react` and `_decay` only to read
the state; it draws no random number and writes no field. `tests_mcm.py` proves it by comparing
state hashes after 250 steps with and without the recorder: identical.

---

## 3. The maintenance condition, and its exact status

A lone body molecule sitting with the organiser triggers `c_X` births per step for `G(0)` steps in
expectation, so its mean offspring number is exactly `c_X·G(0)`. Writing `A = c_X·G(0)` and closing
the local occupancy with a Poisson law, the mean occupancy of the organiser's cell solves

```
u = A * (1 - exp(-u))          positive root iff A > 1       P(source off) = exp(-u*)
```

```
NECESSARY AND SUFFICIENT   for supercriticality of the linearisation about N_X = 0
NECESSARY, NOT SUFFICIENT  for persistence: the source SATURATES at cand_X once nX >= 1, which
                           caps the quasi-stationary population at N_X* = c_X/muX, and extinction
                           beside an absorbing state is certain in finite time
LOCAL and LINEARISED       it is a linearisation at the absorbing state
CLOSURE                    Poisson, and the free-walk G(0); ignoring exclusion makes particles
                           MORE mobile, so the computed G(0) is a LOWER bound and the test is
                           conservative
NOT MERELY HEURISTIC       the offspring-number statement is exact for the linearised process
```

At the MTW01 design point `A = 2.53`, `u* = 2.20`, `P(source off) = 0.11`. **That** is why the
MTW01 cloud died: the source was off eleven per cent of the time and the population was ~34.
This mission therefore requires `A ≥ 8`, giving `P(source off) = 3.4·10⁻⁴`.

---

## 4. The region, and its constraints

`S0 = 3`, `CAP = 16`, `omega = 0.05`, `L = 36` are **pinned at their MINCORE values** throughout
the grid, so no result can be attributed to enlarging the material budget. A control varies `S0`
separately.

Grid: `muX ∈ {0.001, 0.002, 0.004, 0.008, 0.016}`, `phi ∈ {0.05, 0.10, 0.20, 0.40}`,
`ell_X ∈ {2.5, 3.0}`, `p_hop_Y/p_hop_X ∈ {1.0}` (KK use one diffusion constant for every
species). `p_hop_X` is obtained by inverting `D_eff = q(1−q)` exactly.

| # | constraint | status |
|---|---|---|
| 1 | `0 < p_hop ≤ 1`, `0 < muX < 1`, `0 < phi ≤ 1`, `2·S0 < CAP` | EXACT (native admissibility) |
| 2 | `c_X ≤ 7` | EXACT (exhaustive integer search) |
| 3 | `A = c_X·G(0) ≥ 8` | NECESSARY, on the CERTIFIED upper bound for `c_X`; re-tested on the MEASURED value after calibration |
| 4 | `N_X* = c_X/muX ≥ 200` | NECESSARY |
| 5 | `N_X* ≤ rho_max·π·(2·ell_X)²` | GEOMETRIC consistency between the predicted population and the room |
| 6 | `τ_sep ≤ 2000` steps | PRACTICAL, so a future window mission stays affordable |
| 7 | `T_run ≤ 20000` steps | PRACTICAL |
| 8 | `4·ell_X ≤ L/3` | GEOMETRIC, no wrap-around artefact |
| 9 | the future window is non-empty at this point | NECESSARY, computed with the corrected first-passage `τ_sep` |

**40 grid points, 8 analytically admissible** (`out/_region.json`). The region is non-empty.

---

## 5. The deterministic selection rule

> Among the points satisfying **every** constraint of section 4, take the one with the minimum
> predicted `T_run`. Break ties by the ascending lexicographic order of
> `(muX, phi, ell_X, rho_Y)`.

Written before any calibration data exists, fully deterministic, reproducible, independent of
trajectory aesthetics and of confirmation results, with a fixed tie-break. After calibration the
**same rule** is re-applied with the **measured** `c_X` substituted into constraints 3 and 4;
points failing either are eliminated. If none survives, the mission stops.

Calibration covers the **four cheapest admissible points** in that same frozen order, two
calibration seeds each: 8 starts, exactly the class cap.

Pooling of the measured `c_X` across the two calibration seeds: **the minimum over seeds of the
median over the measurement window**. Conservative, because the certified value is an upper bound
and the gate must not be flattered.

---

## 6. The temporal gate

The MTW01 defect was a gate evaluated at one instant. Here it is a window.

**Formation.** `N_X ≥ 30` **and** `u ≥ 3` for **50 consecutive steps**, before
`T_FORM_MAX = 5/muX`. An oscillating record does not qualify; a unit test covers that.

**Persistence**, over the whole window `[t_form, t_form + T_MAINT)`, `T_MAINT = max(20/muX,
10·τ_sep)`. Every one of the following is required:

```
never N_X = 0 at any step in the window
at least one organiser present at every step        <- NOT "exactly one"
fraction of steps with N_X >= N_KEEP  >=  0.95      N_KEEP = max(20, 0.25*N_X_predicted)
longest CONSECUTIVE excursion below N_KEEP  <=  1/muX
fraction of steps with c_X*G(0) > 1  >=  0.90
a main component carrying at least N_KEEP/2 body molecules at every component sample
no wrap-around contact of the main component with its own periodic image
```

**The organiser-count ordering defect is fixed and tested.** The gate requires `N_Y ≥ 1`, never
`N_Y == 1`, so the appearance of a second organiser can never by itself fail an arm. Two unit
tests cover it: a record in which `N_Y` goes 1 → 2 mid-window must PASS, and a record in which
`N_Y` reaches 0 must FAIL.

**End classification**, exhaustive, mutually exclusive, evaluated in a fixed order:
`NO_FORMATION`, `TRANSIENT_FORMATION`, `MAINTENANCE_ACHIEVED`, `MATERIAL_COLLAPSE`,
`ORGANISATION_LOST`, `BOUNDARY_ARTEFACT`, `PROTOCOL_VIOLATION`, `ENGINE_ERROR`, `UNCLASSIFIABLE`.

---

## 7. Horizons, and where they come from

`τ = L²/D` is not used anywhere. The separation time is the exact two-dimensional mean first
passage of the relative coordinate of two organisers, `τ_sep = Δ²/(8·D_Y)` with `Δ = 2·ell_X`,
and every diffusion constant is the corrected `D_eff = q(1−q)`. Dimensional consistency: `Δ²`
in sites², `D_Y` in sites² per step, so `τ_sep` is in steps.

```
preparation                 the organiser is placed with X_SEED = 4 body molecules
maximum formation time      T_FORM_MAX = 5/muX
start of the window         the step at which formation completes
required maintenance        T_MAINT = max(20/muX, 10*tau_sep)
sampling                    every step for the scalar series, every 50 steps for components
maximum horizon             T_FORM_MAX + T_MAINT
early stop                  none: the full window is always run, so a late collapse is seen
relation to the KK bounds   T_MAINT >= 10*tau_sep, so the cloud must outlive ten separation
                            times, the timescale a future window mission would need
```

---

## 8. Budget, seeds, sequential rule

```
cost_probe    2   timing on the manifold n[Y] == 0, where births are identically zero
calibration   8   4 candidate points x 2 seeds
confirmation  6   6 independent seeds at the selected point
control      10   the pre-declared controls
seeds         calibration (1001, 1002) | confirmation (2001..2006) | control (3001+)   disjoint
```

Sequential stopping rule, frozen:

1. no analytically admissible point → STOP, FAIL (region empty)
2. no calibration arm forms a cloud → STOP, `MINCORE_CX_UNRESOLVED`
3. no point survives the frozen rule with the MEASURED `c_X` → STOP, FAIL
4. the first two confirmation seeds both fail to form → STOP, FAIL
5. the first three confirmation seeds all fail maintenance → STOP, FAIL
6. any protocol or logging defect → STOP, `AUDIT_INVALID`
7. controls run only if at least three confirmation seeds were executed

Block sizes are fixed here and are not chosen after seeing results. The ledger counts
separately: synthetic tests, cost probes, calibration starts, confirmation starts, control
starts, invalid runs.

**Success criterion, frozen: at least 5 of the 6 confirmation seeds classified
`MAINTENANCE_ACHIEVED`.**

Cost estimate on the real engine (`out/_costprobe.json`): 1.63 ms per step at `L = 36`,
2.75 ms at `L = 52`; worst case for the whole mission, every start of every class used,
**about 195 seconds**.

---

## 9. Controls, declared before any run

| control | what it changes | prediction |
|---|---|---|
| `NO_ORGANISER` | no organiser is placed | `N_X` stays 0; the absorbing state is exact |
| `MINCORE_FROZEN` | the frozen MINCORE `Spec`, one organiser | stated from its own `A` and `N_X*` before the run |
| `MTW01_DESIGN` | the MTW01 design point, one organiser | transient formation then collapse (`A = 2.53`, `N_X* = 33.5`) |
| `DOMAIN_L52` | the selected point on a larger torus | same classification; no finite-size artefact |
| `TRIVIAL_S0` | MTW01's point with `S0` doubled to 6 | still fails; success here is not a trivial `S0` effect |
| `WINDOW_KINETICS_ON` | the selected point with the future `(kY, muY)` switched on | maintenance unaffected over the window |
| `SLOW_ORGANISER` | the selected point with `p_hop_Y = p_hop_X/100`, the MINCORE asymmetry | maintenance still holds: `D_Y` governs the window, not the cloud |
| `SENSITIVITY_PHI_HALF` | the selected point with `phi` halved | `A` roughly halves; a falsifiable sensitivity probe |

Material balance is audited from the saved raw series (`N_X(t) − N_X(t−1) = births − deaths`,
exactly), and consumes no start.

---

## 10. Dispositions

`MINCORE_CLOUD_MAINTENANCE_QUALIFIED` requires all of: `c_X` measured or certified; the frozen
condition satisfied; formation; maintenance over the whole window; confirmation on independent
seeds; no boundary artefact and no protocol defect; all raw data present. It does **not** mean H3
is confirmed; it means a later window mission becomes eligible.
`MINCORE_CLOUD_MAINTENANCE_FAIL`, `MINCORE_CX_UNRESOLVED`, `AUDIT_INVALID` as specified in the
handoff.

## 11. Claims that will not be made

No claim of reproduction, reconstruction of identity, individuality, hereditary memory,
validation of Kamimura–Kaneko as a whole, confirmation of H3, living organisation, or
higher-level causation. Permitted claims are local: a measurement or bound on `c_X`, the
formation of a cloud, self-maintenance over a stated duration in a stated domain, compatibility
or incompatibility with stated inequalities, a simulation cost, and the eligibility or otherwise
of the next mission.

## 12. Provenance

| number | origin | outcome-informed? |
|---|---|---|
| `S0 = 3`, `CAP = 16`, `omega = 0.05` | pinned at the MINCORE frozen values | inherited, already declared |
| `L = 36` | MTW01, and constraint 8 | no |
| `cand_X ≤ 7`, `Q_max = 28` | exhaustive integer search over the capacity constraint | no |
| `D_eff = q(1−q)` | algebra of the four-attempt step | no |
| `G(0)`, `G_S(0)`, `c_X ≤ S0/G_S(0)` | lattice Green's function by convergent quadrature | no |
| `A ≥ 8` | `P(source off) = e⁻⁸ = 3.4·10⁻⁴`, declared before the grid was evaluated | **design-informed by the MTW01 failure**, and declared as such |
| `N_MIN = 200` | declared | design-informed by the MTW01 failure, declared |
| grid, thresholds 5–9, `T_MAINT`, `N_KEEP`, `FRAC_MIN`, `CRIT_FRAC`, `RUN_MAX` | declared here, before any start | no |
| seeds | declared here | no |

That the third condition was needed at all was learned from the MTW01 stop. This mission is
therefore, by construction, a **design informed by earlier results** — which the handoff permits
explicitly, on condition that this mission has its own freeze, that none of its own results is
read before that freeze, that the old data are not mixed into the confirmation set, and that the
final selection is governed by a pre-registered deterministic rule. All four hold.
