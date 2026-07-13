# EXP-SC-00 — open scaffold + confined internal multistable network
## Equation-level rationale, orthogonality qualification, and bounded domain. **NO law map. NO GATE-0.**
**Preregistered and frozen BEFORE any screen.** Governed by `docs/CAUSAL_METHODOLOGY.md` R1–R8 and `docs/R8_GATES.md`.

## 1. Why this architecture
EXP-MA-00 died because **cohesion and internal structuring competed through the same transport flux** (D-043). Here
they are **functionally orthogonal by construction**:

* **Cohesion** is carried by the scaffold density `rho` via a shared secreted attractant `c` — the mechanism that
  already passed R7 and every substrate check in EXP-CH-00. The internal network **never enters `chi`, `c`, or any
  cohesive term.**
* **Internal structure** is carried by two *concentrations* `u, v` **confined to the scaffold**, obeying a bistable
  mutual-inhibition (toggle) reaction with **small internal diffusion**, so domain walls inside a droplet are pinned
  and **several internal configurations are metastable under one and the same law**.
* Structuring the interior therefore **costs the droplet no cohesion**. That is the whole design.

## 2. Frozen constitutive equations
`q(rho) = max(0, 1 - rho/rho_max)`. Concentrations `u = U/rho`, `v = V/rho` (extensive `U, V` ride the scaffold).

```
SCAFFOLD (cohesion; independent of u, v)
  J    = -D_rho grad(rho) + chi(c) * rho^up * q(rho^recv) * grad(c)
  chi(c) = chi0 / (1 + (c/c_sat)^2)
  d(rho)/dt = -div(J) + g - k*rho
  d(c)/dt   = D_c lap(c) + s*rho - delta*c
  d(N)/dt   = D_N lap(N) - g + F*(N0 - N)

BEHAVIOUR COUPLING (internal state -> future uptake; beta = 0 is the negative control)
  sig  = (u - v) / (u + v + eps)                     internal state, in [-1, 1]
  g    = g0 * rho * N * q(rho) * (1 + beta * sig)    UPTAKE depends on internal state

INTERNAL NETWORK (confined to the scaffold; plays NO part in cohesion)
  U, V are transported by exactly the SAME face fluxes as rho (donor-cell composition), plus small internal
  diffusion D_int acting on the CONCENTRATIONS.
  reaction:  du/dt = a/(1 + (v/K)^2) - u      (bistable toggle)
             dv/dt = a/(1 + (u/K)^2) - v
  turnover:  new mass inherits the LOCAL internal state (U += g*u, V += g*v); homogeneous death removes
             U, V in local proportion. Concentrations are therefore INVARIANT under constituent turnover --
             an internal organization is maintained across complete material replacement.
```
Passive temporal cohorts `C` partition `rho` exactly and influence nothing.

**Exact limits.** `g0 = k = 0` → `rho` conserved. `chi0 = 0` → cohesion removed. **`beta = 0` → the internal state
is causally inert (a decorative label): the built-in NEGATIVE CONTROL for orthogonality criterion O4.**
**`a = 0` → the internal network is off: the scaffold-only control for O1.**

## 3. ORTHOGONALITY QUALIFICATION — must pass BEFORE any R8 screen
* **O1 — the scaffold cohere s on its own.** With the internal dynamics **disabled** (`a = 0`), the scaffold must
  pass **R7** (frozen threshold-independent diagnostics: PR ≤ 0.15, entity Rg ≤ 8, occupancy ≤ 0.15 across the frozen
  threshold band). Cohesion must not depend on the internal network.
* **O2 — distinct internal states leave localization broadly intact.** Droplets prepared in different internal
  states (u-dominant, v-dominant, and a mixed/domained state) must **all** pass R7, and their PR and entity Rg must
  agree within a frozen tolerance (|ΔPR| ≤ 0.05, |ΔRg| ≤ 1.5 cells). Internal structure must not buy or cost cohesion.
* **O3 — the internal fields alone cannot create an entity.** With sub-threshold `rho`, any `u, v` configuration must
  yield **zero** detected entities. The detector reads `rho` only; `u, v` must be incapable of manufacturing a
  droplet.
* **O4 — the internal state causally alters a FUTURE behavioural observable.** Flipping a droplet's internal state
  (`u <-> v`) must change its **future specific uptake** `Uptake = (N consumed by the entity) / (entity mass)` by a
  frozen margin. **With `beta = 0` it must NOT change it.** Identity must not be decorative.

**Every metric used (internal-organization phenotype, uptake observable, orthogonality statistics) must first pass
synthetic MUST-PASS and MUST-FAIL unit cases.** No exceptions: four criteria this session could not fire.

## 4. Identity phenotype (translation- and rotation-invariant; forbidden features excluded)
**PRIMARY — internal spatial organization:** `internal_heterogeneity` (rho-weighted std of `sig` inside the entity;
threshold-free, 0 for a uniform interior), `n_u_domains` (connected `sig > mean` sub-domains, ≥3 cells),
`interface_fraction`, `radial_u`, `janus_sig` (|centroid(u-rich) − centroid(v-rich)| / Rg — a rotation-invariant
magnitude).
**SECONDARY — adds the bulk internal state** `mean_sig`.
**Disclosed in advance:** a within-support permutation preserves `mean_sig` **exactly**, so any identity carried by
it is by construction **compositional, not organizational**. **R8-C is decided on the PRIMARY (spatial) phenotype**;
the secondary is reported alongside so the split is visible.
**Forbidden and absent everywhere:** absolute position, total mass, absolute orientation, tracker ID.

## 5. Order of operations, and where this stops
O1–O4 → **R8-A** (diversity) → **R8-B** (predictive identity, prototypes fitted on early states only) → **R8-C**.

**R8-C scramble:** preserve the **external scaffold** (`rho`, `c`, `N`), the **support**, all **masses** and all
**cohort totals** exactly; scramble **only the internal reaction-state organization** — independent within-support
permutations of `U` and `V`, destroying the internal spatial pattern and the u–v spatial correlation.
**PRIMARY OUTCOME: source-specific identity recovery AND behavioural prediction — not generic droplet reformation.**
A scrambled cargo that reforms a perfectly good droplet with a *different* internal identity is an identity
**failure**, and that is the discrimination this gate exists to make.

**No broad law map and no GATE-0 until at least two distinguishable, temporally persistent internal organizations
are demonstrated under the same frozen global law on entirely unseen seeds.** If O1–O4 or R8 fails, the substrate is
retired. **No mechanism may be added after observing a failure.**

---

## AMENDMENT 1 (2026-07-12) — `beta` is SELECTED BY the qualification, prospectively. Full disclosure.

**What happened.** The protocol above declares the behaviour coupling `beta` and declares `beta = 0` as its negative
control, but **never fixed a value for `beta`**. I hand-set `beta = 0.6` in the code and ran O1–O4:
**O1 PASS** (scaffold coheres with the internal network off: PR 0.133, entity Rg 2.36), **O3 PASS** (internal fields
alone create no entity), **O4 PASS** (flipping the internal state changes future specific uptake by 58.6 %; the
`beta = 0` control changes it by 0.0 %), **O2 FAIL** (dPR 0.139 > 0.05, dRg 4.36 > 1.5).

I then scanned `beta` as a **post-hoc diagnostic** and found that O2 and O4 are antagonistic in `beta` — but not
absolutely so:

| beta | dPR (tol 0.05) | dRg (tol 1.5) | O2 | uptake change | O4 |
|---|---|---|---|---|---|
| 0.00 | 0.000 | 0.00 | PASS | 0.0 % | **FAIL** (decorative label) |
| 0.15 | 0.031 | 1.04 | **PASS** | 17.3 % | **PASS** |
| 0.30 | 0.069 | 2.23 | FAIL | 34.8 % | PASS |
| 0.60 | 0.139 | 4.36 | FAIL | 58.6 % | PASS |

**I will NOT adopt `beta = 0.15` on the strength of that scan.** It was found *after* a failure, on the seed the
failure was observed on. Doing so would be tuning-after-failure, which is the single thing this project exists to
not do.

**What is legitimate, and what is therefore done instead.** `beta` is an unspecified design parameter, and the
orthogonality qualification is precisely a **selection procedure over substrate configurations** — the same role R7
played in selecting the Gray-Scott regime and the chemotaxis laws. So `beta` is selected **prospectively**, by a rule
declared here **before** it is run, on **seeds never used before**:

- **Declared grid (frozen, in this order):** `beta ∈ (0.05, 0.10, 0.15, 0.20)`.
- **Declared seeds (entirely unseen):** 8101, 8102. (The post-hoc scan used 8001; it is discarded.)
- **Declared rule:** select the **smallest `beta` in the grid that passes O1, O2, O3 and O4 on BOTH seeds.**
  Ties impossible by construction.
- **The selection criterion references ONLY O1–O4. It never references R8-A, R8-B, R8-C, or any identity outcome**,
  so it cannot bias the gates that follow.
- **If no `beta` in the declared grid passes on both seeds, the substrate is RETIRED.** The grid is not widened, and
  no mechanism is added.

The scanned values above are reported for transparency and carry **no** selective weight; the prospective run below
is the only evidence used.
