# EXP-CH-00 — open chemotactic self-aggregation substrate
## Part 1: equation-level rationale and bounded qualification domain
**Preregistered and frozen BEFORE any screen is coded or run.** Governed by `docs/CAUSAL_METHODOLOGY.md` R1–R7.
Gate order is binding: **R7 (localization) → GATE-0 (organization is load-bearing) → law map.** Not before.

## 1. Why chemotaxis, and why cohesion must be constitutive
The motile polar substrate died (D-037) because **nothing held a structure together**: polarity advected material but
there was no cohesive mechanism, so the active phase was a Fisher–KPP front — it invaded the whole domain or went
extinct. Localizing it afterwards would have required *adding* cohesion, i.e. a rescue mechanism.

Here cohesion is **in the constitutive equations from the outset**. Cells secrete a chemoattractant and climb its
gradient; the field they produce pulls them toward each other. Aggregation is not an emergent bonus — it is what the
equations do. The finite-density regularization is likewise **part of the core**, not a later patch.

## 2. Frozen constitutive equations
Periodic lattice, `dx = 1`, explicit time step `dt`. Fields: `rho` (cells), `c` (chemoattractant, produced BY the
cells), `N` (nutrient, fed homogeneously), `C` (passive origin cohorts partitioning `rho`, exactly).

```
d(rho)/dt = -div( J )      +  g0 * rho * N * q(rho)   -  k * rho          [q = volume-filling factor]
d(c)/dt   = D_c * lap(c)             +  s * rho          -  delta * c
d(N)/dt   = D_N * lap(N)             -  g0 * rho * N      +  F * (N0 - N)

J = -D_rho * grad(rho)  +  chi(c) * rho_donor * q(rho_receiver) * grad(c)   [cells climb the gradient]

chi(c)  = chi0 / (1 + (c / c_sat)^2)      <- SATURATING CHEMOTACTIC RESPONSE (receptor saturation)
q(rho)  = max(0, 1 - rho / rho_max)       <- VOLUME EXCLUSION (volume-filling Keller-Segel)
```

`q` appears in BOTH the chemotactic flux and the growth source, and in the flux it is evaluated on the **receiving**
cell. Both details are load-bearing and both were wrong in my first draft (see the correction note below).

**The finite-density regularization is predeclared and constitutive.** Two independent mechanisms, both in `chi`:
- **Receptor saturation** `1/(1+(c/c_sat)^2)`: chemotactic drift vanishes where the signal is strong, so a forming
  aggregate stops pulling ever harder on itself.
- **Volume exclusion** `q(rho) = max(0, 1 - rho/rho_max)`: chemotactic filling of a cell stops **exactly** at
  `rho = rho_max` (volume-filling Keller–Segel, Hillen & Painter), and the **same factor regularizes the growth
  source**, so cells cannot be born into a full cell either. Together these make `0 <= rho <= rho_max` an
  **invariant**: blow-up is impossible and the bound is proven, not tuned (`tests/test_chemotaxis.py`).

**CORRECTION made before any qualification result was used (full disclosure).** My first draft claimed this bound but
did not implement it: `q` multiplied the *donor* cell (so a cell already at `rho_max` could still be filled) and did
**not** regularize growth at all. A smoke test on Halton point 0 reached `rho = 1.408 > rho_max = 1.0` — the
"globally bounded" claim was **false**. Both defects are fixed above and the invariant is now asserted in tests. The
pre-fix diagnostics of point 0 were computed under different equations and carry no information about the corrected
substrate; the full 32-point qualification is run from scratch on the corrected equations.

**Openness.** `N` is fed spatially homogeneously by `F*(N0 - N)` — detector-independent, and (as required) provably
incapable of imposing a pattern: a uniform state stays exactly uniform. Cells are created by `g0*rho*N` (consuming
nutrient) and removed by the homogeneous death rate `k*rho`. A persistent aggregate therefore continuously replaces
its constituents.

**Exact controlled limit.** `g0 = k = 0` ⇒ `d(rho)/dt = -div(J)` in flux form ⇒ **total `rho` is exactly conserved**
(no source, no sink). Setting `chi0 = 0` removes chemotaxis entirely and is the **causal control for cohesion**.

**Numerics (frozen).** `J` is evaluated in conservative flux form on cell faces with donor-cell (upwind) composition:
the face flux is computed once from `rho`, and each passive cohort is transported by **that same face flux** times the
donor cell's cohort fraction. This makes `sum_c C == rho` hold **cell-wise and exactly at every step**, and makes the
closed limit conserve mass to machine precision. Cohorts never influence `rho`, `c` or `N`.

## 3. Bounded qualification domain (frozen box)
Sampled by a blind low-discrepancy (Halton) sequence — **no hand-picking, no visual selection**:

| parameter | meaning | lower | upper |
|---|---|---|---|
| `chi0` | chemotactic sensitivity | 2.0 | 12.0 |
| `D_rho` | cell diffusion | 0.05 | 0.30 |
| `D_c` | chemoattractant diffusion | 0.20 | 1.00 |
| `s` | secretion rate | 0.05 | 0.40 |
| `delta` | chemoattractant degradation | 0.02 | 0.20 |
| `g0` | growth on nutrient | 0.02 | 0.20 |
| `k` | homogeneous death | 0.01 | 0.10 |
| `F` | homogeneous nutrient feed | 0.01 | 0.10 |

Fixed: `size = 64`, `dt = 0.1`, `rho_max = 1.0`, `c_sat = 1.0`, `N0 = 1.0`, `D_N = 0.5`.
**Qualification domain = the first 32 Halton points of this box.** If **no** point clears R7, the substrate is
**retired immediately, with no mechanism added** — including no widening of the box.

## 4. R7 — localization, with THRESHOLD-INDEPENDENT diagnostics
The motile substrate reported persistence, motility and turnover for a structure that was the entire lattice
(D-037). The detector alone cannot be trusted. R7 is therefore evaluated with diagnostics that **do not depend on
any detector threshold**, and the detector is only a supplementary check:

1. **Participation ratio (threshold-free).** `PR = (sum rho)^2 / (L^2 * sum rho^2)` — the effective *fraction* of the
   domain carrying the mass. `PR = 1` for a uniform (delocalized) field, `PR -> 0` for a localized one.
   **Require `PR <= 0.15`.**
2. **Radius of gyration (threshold-free, periodic).** Mass-weighted `Rg` about the circular-mean centroid.
   **Require `Rg <= L/8 = 8` cells** — bounded, and far below the domain scale.
3. **Strict sub-domain occupancy, across a FROZEN THRESHOLD BAND.** Occupancy = fraction of cells above threshold,
   for every threshold in the frozen band `{0.2, 0.3, 0.4, 0.5, 0.6} * rho_max`.
   **Require occupancy `<= 0.15` at EVERY threshold in the band** (robustness to the detector threshold).
4. **Non-space-filling support.** Largest connected component `<= 0.15 * L^2` at **every** threshold in the band.
5. **Persistence across seeds.** Criteria 1–4 must hold at `t*` **and** through the observation window, for
   **>= 80 % of 5 qualification seeds**.
6. **Not the trivial states.** Total mass must be bounded away from 0 (not extinct) and `PR` bounded away from 1
   (not space-filling).

**Centroid motion is INADMISSIBLE until 1–5 pass.** If they do, motion is reported only with: (a) an explicit check
that every inter-snapshot displacement is `< L/2`, so the periodic unwrapping is unambiguous; and (b) a
**straightness ratio** `|net displacement| / path length` separating **coherent translation** (straightness -> 1)
from **centroid jitter** (straightness -> 0, path long, net small) and from **front invasion** (which is excluded by
criteria 1–4 anyway, since an invading front is not sub-domain).

## 5. Then, and only then: substrate validation
Genuine openness (uniform state stays exactly uniform: forcing cannot impose a pattern); exact closed limit
(`g0=k=0` conserves `rho` to machine precision); `sum_c C == rho` exactly, cell-wise, every step; passive tracers
(cohort relabelling leaves `rho`, `c`, `N` **bit-identical**); determinism (identical seeds ⇒ identical bits);
continued temporal-cohort turnover (`M < 0.5`); and the **causal dependence of cohesion on the internal chemotactic
field**: with `chi0 = 0` the aggregate must fail localization — cohesion must be *caused* by `c`, not assumed.

## 6. Then GATE-0 (R4/R3) — unchanged in form from EXP-MO-00
Identical pre-intervention state and destination. CONTROL / SHAM / **INTACT** / **SCRAMBLED** / PLACEBO (PLACEBO
reported separately; per R2 it carries **no eliminative weight** and enters no decision rule; **no pooling of unequal
nulls**, R1). The scrambled arm preserves support geometry, total masses of every species, per-cohort masses, the
multisets of local scalar values and the perturbation magnitude, while destroying cross-field spatial correlations
and coherent internal organization (independent permutations per field). **Executable assertions (R5) prove that
every intervention and every null actually altered its intended variable, and that the scrambled arm actually
destroyed the organization.** Fixed N, paired exact McNemar, predeclared margin, no sequential stopping.

**A blind law map is authorized only if R7 and GATE-0 both pass. If either fails, the substrate is retired
immediately, with no mechanism added.**
