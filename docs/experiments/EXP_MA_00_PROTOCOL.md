# EXP-MA-00 — minimal open MULTISTABLE active-droplet / catalytic-field substrate
## Equation-level rationale and bounded qualification domain. **R7 and R8 ONLY.**
**Preregistered and frozen BEFORE any screen.** Governed by `docs/CAUSAL_METHODOLOGY.md` R1–R8 and `docs/R8_GATES.md`.
**No broad law map and no GATE-0 until multiple distinguishable, temporally persistent entities are demonstrated on
entirely unseen seeds.**

## 1. Rationale
D-041: the chemotactic substrate failed GATE-0 not because it self-assembles, but because it has **one
interchangeable aggregate attractor**. The requirement is therefore a substrate whose **same frozen global law admits
SEVERAL metastable internal organizations**, so that a scrambled cargo may re-assemble *an* entity while failing to
recover *the source* entity.

Cohesion is intrinsic and is the **already-validated** chemotactic mechanism (it passed R7 and every substrate
check; it is reused as a building block, not bolted on to rescue a failure). What is **new by design, from the
outset** is an internal degree of freedom that is **multistable**: two catalytic species A and B that cohere
together but **demix from each other**, so a droplet's interior settles into one of several long-lived morphologies
(mixed / core-shell / Janus / multi-domain) under one and the same law.

## 2. Frozen constitutive equations
Periodic lattice, `dx = 1`. `rho = rho_A + rho_B`. `q(rho) = max(0, 1 - rho/rho_max)` (volume exclusion, in flux
AND growth — the proven finite-density regularization from EXP-CH-00).

```
J_X = -D_rho grad(rho_X)                       Fickian
      + chi(c) * rho_X^up * q(rho^recv) grad(c)   COHESION  (both species climb the shared attractant)
      - lam   * rho_X^up * q(rho^recv) grad(rho_Y)   DEMIXING (X is pushed down the gradient of the OTHER species)

d(rho_X)/dt = -div(J_X) + g0 * rho_X * N * q(rho) - k * rho_X      autocatalytic: A makes A, B makes B
d(c)/dt     = D_c lap(c) + s * rho - delta * c                     attractant produced by BOTH species
d(N)/dt     = D_N lap(N) - g0 * rho * N + F * (N0 - N)             HOMOGENEOUS feed; detector-independent
chi(c)      = chi0 / (1 + (c/c_sat)^2)                             receptor saturation
```
Passive temporal cohorts `C` partition `rho` exactly and are transported by the **same face fluxes** with donor-cell
composition. They never influence `rho_A`, `rho_B`, `c` or `N`.

**Multistability comes from `lam`**: A and B cohere into a common droplet (via `c`) but repel each other (via `lam`),
so the interior micro-phase-separates. **Growth is species-preserving** (`A` makes `A`), so an internal morphology is
maintained across complete constituent turnover instead of being re-randomized.

**Exact controlled limits.** `g0 = k = 0` → total `rho_A` and `rho_B` each conserved (flux form). `chi0 = 0` →
cohesion removed. **`lam = 0` → demixing removed: the substrate degenerates to EXP-CH-00 with a passive species
label, i.e. exactly ONE entity type. `lam = 0` is therefore the built-in R8 NEGATIVE CONTROL** — it must FAIL R8-A
and R8-B. If it does not, the R8 gates are not measuring what they claim.

## 3. Bounded qualification domain (frozen; blind Halton)
`chi0 ∈ [2,12]`, `D_rho ∈ [0.05,0.30]`, `D_c ∈ [0.2,1.0]`, `s ∈ [0.05,0.40]`, `delta ∈ [0.02,0.20]`,
`g0 ∈ [0.02,0.20]`, `k ∈ [0.01,0.10]`, `F ∈ [0.01,0.10]`, **`lam ∈ [0.5, 6.0]`** (demixing strength).
Fixed: `size=64, dt=0.1, rho_max=1.0, c_sat=1.0, N0=1.0, D_N=0.5`. **Domain = the first 32 Halton points.**

## 4. Identity phenotype (translation- and rotation-invariant; forbidden features excluded)
Computed on the detected entity only. **PRIMARY (morphological — the arrangement):**
`n_A_domains` (connected A-rich sub-domains inside the entity), `|centroid_A − centroid_B| / Rg` (Janus-ness;
a rotation-invariant magnitude), `<r>_A / Rg` (core-vs-shell), `<r>_B / Rg`, `A/B interfacial length / entity
perimeter`, `Rg_A / Rg`, `Rg_B / Rg`.
**SECONDARY (adds bulk composition):** the above plus `f_A = mass_A / rho_total`.

**Disclosed in advance:** a within-support permutation **preserves `f_A` exactly**. Any identity carried by `f_A` is
therefore, by construction, **not organizational**. R8-C is decided on the **PRIMARY (morphological)** phenotype;
the secondary is reported alongside so the split between compositional and organizational identity is visible.
**Excluded everywhere:** absolute position, total mass, absolute orientation, tracker ID.

## 5. What this experiment does, and stops at
**R7** (localization; threshold-independent diagnostics, frozen from EXP-CH-00, unchanged) → then **R8-A** (diversity)
→ **R8-B** (predictive identity, prototypes fitted on early states only, evaluated on held-out later states and
held-out trajectories). Both on **entirely unseen seeds**.
Plus the **`lam = 0` negative control**, which must FAIL R8-A/R8-B.

**No law map. No GATE-0. No R8-C.** They are authorized only if R7, R8-A and R8-B all pass, and R8-C only after.
**If R7 or R8 fails, the substrate is retired. No mechanism may be added after observing a failure.**
Every new metric passes synthetic must-pass and must-fail cases before use (`tests/test_r8_gates.py`).
