# EXP-CH-01 / GATE-0 — is the organization of a chemotactic aggregate load-bearing?
**Preregistered and frozen BEFORE any GATE-0 unit is run or inspected.** Governed by `docs/CAUSAL_METHODOLOGY.md` R1–R7.

## Status of the inputs
**Laws {2, 4, 5} are FROZEN** (D-039). The 32-point R7 screen was a **candidate-selection exercise, not a
prevalence estimate** — the per-entity Rg repair post-dated the first readout of those points. No rate from it is
quoted. **All GATE-0 evidence uses entirely unseen seeds**, disjoint per law:
law 2 → 40001–40040, law 4 → 41001–41040, law 5 → 42001–42040. (Qualification consumed 5001–5005, 7001–7002.)

## Design — per law, never pooled
**N = 40 unseen paired causal units per law**, fixed in advance. **Each law is decided on its own.** Laws are NOT
pooled for the primary decision. All arms of a unit share the **identical pre-intervention state `s*` (fixed
`t* = 2000` steps, not cadence-derived), the identical source support, the identical destination
`old_centroid + DELTA` (DELTA = (16,16)) and the identical displacement magnitude.**

| arm | cargo |
|---|---|
| CONTROL | nothing displaced (also supplies the **spontaneous-target-site control**: scored at the destination) |
| SHAM | zero displacement — asserted an exact bitwise no-op |
| **INTACT** | the detected aggregate: `rho`, `c` and **all** temporal cohorts, translated together |
| **JOINT-SCRAMBLE** (PRIMARY null) | see below |
| INDEP-SCRAMBLE (secondary null) | `rho`, `c` and the cohorts permuted by **independent** permutations — destroys the local rho–c/cohort association *as well*. **Reported separately. NEVER pooled with the primary null.** |
| PLACEBO (non-entity) | matched non-entity support, same cell count, same DELTA. **Reported separately; per R2 it carries NO eliminative weight and enters NO decision rule.** |

## The PRIMARY organization-destroying null (JOINT-SCRAMBLE)
**One single permutation** applied to the **local tuples** `(rho, c, C_1..C_n)` inside the exact same support: the
tuple resident at cell *i* moves, intact, to cell *pi(i)*.

**Preserved exactly:** support geometry; total `rho`; total `c`; every cohort mass; the multiset of local field
values for every field; **the local rho–c and rho–cohort associations** (the tuple is never broken); and the
perturbation magnitude.
**Destroyed:** spatial gradients, neighbourhood correlations, and global internal organization.

This is the sharpest possible null: it differs from INTACT *only* by a permutation of positions. Anything the
protocol could be responding to other than the arrangement itself is held fixed by construction.
**INTACT must beat JOINT-SCRAMBLE. Beating the non-entity placebo is not evidence and will not be accepted.**

## Executable assertions (R5) — per unit, must all hold or the unit aborts
1. **Exact conservation**: displacement changes neither `sum rho` nor `sum c` (to machine precision).
2. **Non-overlap**: the source support and its translate by DELTA are **disjoint** (a swap between overlapping sets
   is not a bijection and would destroy mass). Overlapping units are **CENSORED**, identically for every arm.
3. **SHAM is an exact bitwise no-op** in every field.
4. **The scramble preserved what it must**: identical total `rho`, total `c`, per-cohort masses, and identical
   sorted multisets of `rho` and `c` inside the support.
5. **The scramble destroyed what it must**: the lag-1 spatial autocorrelation of `rho` **and** of `c` inside the
   support is **materially reduced** (asserted: `|autocorr_scrambled| < 0.5 * autocorr_intact`).

## Audited success — every condition required
1. SHAM ≡ CONTROL.
2. **Re-establishment at the destination**: phenotype continuity > 0.8 in > 0.5 of post-intervention snapshots.
3. **Compact localization retained**: entity Rg ≤ 8 and PR ≤ 0.15 (the frozen R7 thresholds, unchanged).
4. **Continued temporal-cohort turnover**: min cohort-Jaccard M < 0.5 at lags of **400 and 600 STEPS**. A frozen
   lump fails. **The lags are declared in steps, not snapshots**: a snapshot-indexed lag shrinks with the observation
   cadence and can never fire at coarse cadence. **Verified fireable a priori** on smoke seed 90001 (outside every
   GATE-0 block): the intact aggregate's M at lag 400 steps is 0.330 / 0.195 / 0.156 for laws 2 / 4 / 5, all below
   the frozen 0.5; at lag 200 law 2 sits at 0.530 and could never pass. Material half-lives: 268 / 190 / 166 steps.
   HORIZON = 800 steps. **The 0.5 threshold is unchanged.**
5. **No old-site regeneration** at the original centroid.
6. **No spontaneous target-site entity in CONTROL** (the ambient alias, checked per unit).
7. **Observer robustness**: audited under **all 9** offline observer settings — physics computed once per branch at
   fixed `t*`, then re-observed offline at cadence {50,100,200} × site radius scale {0.8,1.0,1.2}. Fixed trajectory,
   fixed branches, fixed `t*` (R6).

## Predeclared statistics and decision rule
Per law, `p_intact` and `p_joint` are AUDITED rates over the 40 unseen units (denominator = enrolled; censored units
reported). Wilson 95 % per arm; **every arm reported separately (R1)**.
- **Primary test, per law:** paired **exact two-sided McNemar**, INTACT vs JOINT-SCRAMBLE.
- **Multiple testing:** three laws → **Holm–Bonferroni** across the three McNemar p-values, family-wise α = 0.05.
- **Effect-size margin:** `p_intact − p_joint > 0.25` (absolute), and Newcombe 95 % LB of the difference > 0.

**A law PASSES GATE-0 iff, individually:** `p_intact > 0` **and** Holm-adjusted McNemar p < 0.05 **and**
`p_intact − p_joint > 0.25` **and** Newcombe LB > 0.

- **No law passes → the substrate is RETIRED before any law map.** No new mechanisms, no threshold changes.
- **At least one law passes → that law is replicated PROSPECTIVELY on a further block of unseen seeds before any
  broader screening is authorized.** A single GATE-0 pass authorizes nothing on its own.

**Stopping:** fixed N = 40 per law. No interim inspection, no sequential stopping, no extension of N after results.
