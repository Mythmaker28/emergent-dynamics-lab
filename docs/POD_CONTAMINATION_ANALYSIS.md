# POD CONTAMINATION & CONDITIONING ANALYSIS

Calibration used ONLY the permitted external nutrient handle (an imposed slow OU drift on N) and the declared
initial-condition family (internal state `u`/`v`/`off`) to create a known causal response. `β`, `D_int` and the
equations were untouched. Reference coupling `a_i` (to drift) and contamination `κ_i` (to response) were estimated
by regression; privileged state was never read by the operational references.

## 1. Reference diversity exists at the level of TYPES

Drift couplings `a_i` (mean over dev seeds): N-field mean ≈ +0.20 (N_global, N_background, N_core, sectors — all
**collinear**, must-fail #1 confirmed); N spatial-derivative ≈ −0.004 (N_laplacian, N_flux); attractant
c_global ≈ −0.50. Coupling diversity across types 7.79, condition number 1.14 — nominally well-conditioned.

## 2. But the diverse-and-observing references are COMMON-MODE contaminated

Under a clean strong response (internal `u` active vs `off` inert), the strong references carry the response at
**contam/drift ≈ 0.79–0.90** (robust across seeds):

| reference | contam/drift (3 seeds) | κ_i/a_i |
|---|---|---|
| N_global | 0.95, 0.79, 0.82 → **0.85** | 234.7 |
| N_background | 0.99, 0.86, 0.86 → **0.90** | 249.5 |
| N_core | 0.88, 0.72, 0.76 → **0.79** | 217.2 |
| c_global | 0.86, 0.45, 0.61 → 0.64 | 179.3 |

The `κ_i/a_i` ratio is nearly constant across the N references (spread **0.056 ≈ 0**): the contamination is
**common-mode** — every reference sees the response *in proportion to how it sees the drift*, because both act
through N. This is exactly the direction CRD-03 proved **unidentifiable** without an absolute scale. CRD-03 would
return these references as a **lower bound**, not a correction.

## 3. The low-contamination references do not observe the drift

N_laplacian and N_flux have low contamination (0.07–0.14) but drift couplings ~0.003–0.005 — roughly **50× smaller**
than the measurement's own coupling (~0.15). The CRD-03 correction `z_i = y − α_i r_i` with `α_i = a_y/a_i ≈ 50`
amplifies the reference's noise ~50×: unusable. Low contamination here is *because* the reference barely couples to
the drift, not because it cleanly separates drift from response.

## 4. Consequence

There is **no passive reference set that is simultaneously (a) diverse, (b) drift-observing, and (c)
low-contamination.** The references that observe the drift are common-mode contaminated by the response; the ones
that are clean do not observe the drift. Reading the internal state (`U, V, σ`) directly WOULD separate them — and
is forbidden oracle access (must-fail #11).
