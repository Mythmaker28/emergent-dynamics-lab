# EXP-SC-00B — prospective orthogonality qualification with O2' (viability, not size-invariance)
**Preregistered and frozen BEFORE any run. Entirely unseen seeds. D-044 is NOT reinterpreted and its seeds are NOT reused.**

## Why O2 is replaced
O2 required entity radius to be near-invariant across internal states. An internal state that **alters uptake must
alter growth and therefore morphology** — so O2 and O4 were contradictory by construction (D-045). Functional
orthogonality means **scaffold-independent cohesion** and **viability across identity states**, *not* identical body
size. **Size and shape may differ; they are REPORTED, never thresholded away.**

## Substrate — UNCHANGED from EXP-SC-00 (no mechanism added, nothing retuned)
`ScaffoldSpec` exactly as committed: scaffold = the EXP-CH-00 law-2 R7 survivor; confined bistable toggle
(`a, K, D_int, tau`); uptake coupling `beta`. Passive temporal cohorts. Only `beta` is selected, prospectively.

## Frozen criteria
**O1 (unchanged)** — with the internal network **disabled** (`a = 0`) the scaffold must pass **R7**.
Cohesion must not depend on the internal network. (`beta`-independent: with `u = v = 0`, `sig = 0`.)

**O3 (unchanged)** — violently structured `u`/`v` on a **sub-threshold** scaffold must yield **zero** entities.

**O2' (NEW — VIABILITY, evaluated INDEPENDENTLY for EACH internal state ∈ {u, v, random}):**
each state must, on its own, satisfy **all** of:
1. **R7 localization** — PR <= 0.15, entity Rg <= 8, occupancy <= 0.15 at every threshold in the frozen band.
2. **Bounded sub-domain occupancy / no domain invasion** — largest connected component <= 0.15 of the domain at
   every threshold in the band.
3. **No extinction** — total mass > 1e-3 **and** at least one detected entity.
4. **No catastrophic fragmentation** — the largest entity holds >= 5 % of all above-threshold material **and** is
   >= `min_cells` (12).
5. **Persistence** — an entity is detected in >= 80 % of the window snapshots (window = 800 steps, cadence 100).
6. **Continued temporal-cohort turnover** — min cohort-Jaccard `M < 0.5` at lags of **400 and 600 STEPS**
   (declared in steps, not snapshots; material half-life = ln2/(k*dt) = 268 steps, so the lag spans one).
**REPORTED, NOT THRESHOLDED:** entity size, Rg, mass, density and count, for every internal state.

**O4' (STRENGTHENED) — the internal state must predict FUTURE behaviour after controlling for trivial morphology.**
For every detected entity at time `T`, record `sig(T)` and the controls `mass(T), Rg(T), mean density(T), size(T)`.
Run `Δ = 300` steps; match each entity to its successor by nearest centroid and record its **specific uptake at
`T + Δ`**. Compute the **partial correlation** `r(sig(T), uptake(T+Δ) | mass, Rg, density, size)`, pooled across the
three internal states and the three seeds, with a **permutation p-value** (2000 permutations).
- **PASS requires |r_partial| >= 0.30 and p < 0.05.**
- **`beta = 0` NEGATIVE CONTROL must FAIL** (|r_partial| < 0.30).
The partial-correlation metric must first pass **synthetic must-pass and must-fail** cases — including the decisive
confound case where a *naive* correlation fires but the partial correlation must not.

## Prospective `beta` selection (frozen before running)
- **Grid, in this order:** `beta ∈ (0.05, 0.10, 0.20, 0.30, 0.45, 0.60)`.
- **Seeds (entirely unseen):** 8201, 8202, 8203. **D-044's seeds (8001, 8101, 8102) are NOT reused.**
- **Rule:** select the **smallest `beta` in the grid** passing **O1, O2' (on all three internal states, all three
  seeds), O3, and O4'**. The rule references **only** O1/O2'/O3/O4' — **never** any identity or R8 outcome.
- **If no `beta` qualifies → RETIRE the substrate** and move identity coupling to **motility direction, oscillatory
  phase, or probe response** (channels that do not feed the scaffold's mass balance). No mechanism is added here.

## If EXP-SC-00B qualifies
Proceed **directly to R8-A → R8-B → R8-C, with the substrate unchanged**. No retuning, no law map, no GATE-0 before
R8. **Identity features for R8 exclude total mass, radius, position and absolute orientation** — the frozen PRIMARY
phenotype (`internal_heterogeneity`, `n_u_domains`, `interface_fraction`, `radial_u`, `janus_sig`) already contains
none of them; `radial_u` and `janus_sig` are normalized by Rg and are therefore scale-free and rotation-invariant.
