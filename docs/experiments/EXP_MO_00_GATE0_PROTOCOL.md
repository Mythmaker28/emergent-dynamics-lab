# EXP-MO-00 / GATE-0 PROTOCOL — is organization load-bearing in the motile polar substrate?
**Preregistered and frozen before any GATE-0 result is produced or inspected.** Governed by `docs/CAUSAL_METHODOLOGY.md` (R1–R6).

## The question GATE-0 answers, and why it comes first
Gray-Scott died because its structures are reconstructible from unstructured matter: a scrambled lump re-established
*more* often than the intact entity (D-035). Before any law search, a substrate must therefore demonstrate that the
**internal organization of a structure is causally load-bearing**. If it is not, there is nothing for an individual
to be, and the substrate is retired immediately — no rescue mechanisms, no re-tuning.

## Substrate (frozen)
`MotilePolarSpec(size=64, dt=1.0, D_rho=0.06, D_R=0.20, v0=0.55, J=0.0, a=0.5, b=0.5, F=0.030, R0=1.0, g0=0.25, k=0.060)`
`TracerSpec(n_spatial=4, n_temporal=8, tau_feed=60)`. Detector `threshold=0.30, min_cells=12`.

Qualification (all passed, recorded in `results/EXP-MO-00-.../qualification.json`):
cohort partition `sum_c C == rho` exact (rel. err 6e-19); **exact closed limit** F=g0=k=0 conserves rho (drift 1.4e-16);
**homogeneity null** — a uniform state stays exactly uniform (rho ptp = 0.0, R ptp = 0.0), so the forcing provably
cannot impose a spatial pattern; **passive tracers** bit-identical rho and p under cohort relabelling;
**polarity causally drives transport** — with v0 = 0 the centroid drifts 1.1 cells in 300 steps versus a path length
of 853 cells with v0 > 0; and the reference structure is **persistent (24/24), motile (0.95 cells/step) and fully
turned over (min M ≈ 8e-7 — complete constituent replacement)**.

**J (polar alignment) is frozen at ZERO, and this is a REMOVAL of a mechanism, not a rescue.** A Vicsek-like
alignment term regenerates coherent polarity from disorder, which would make GATE-0 untestable by construction (an
incoherent seed recovered polar order 0.71 with J=0.6). With J=0 the Landau term is direction-neutral (p=0 stays
exactly p=0), so orientation can be inherited or destroyed but never spontaneously rebuilt.

## Branches (identical pre-intervention state `s*`, identical destination `old_centroid + DELTA`, DELTA=(18,18))
| arm | cargo |
|---|---|
| CONTROL | nothing displaced |
| SHAM | zero displacement — asserted an **exact bitwise no-op** |
| **INTACT** | the detected entity: rho, R, py, px and **all** passive cohorts, translated together |
| **SCRAMBLED** (decisive null) | see below |
| PLACEBO | non-entity support, same cell count, same DELTA — **reported separately; it is a weak control and per R2 carries NO eliminative weight** |

## The scrambled cargo (R3)
Inside the support, three **independent** permutations:
- `P1` applied **jointly to rho and every cohort** — preserves total material, per-cohort mass, the multiset of local
  rho values, and the exact cell-wise invariant `sum_c C == rho`;
- `P2` applied to the nutrient R — preserves total R and its value multiset, **destroys the rho↔R spatial correlation**;
- `P3` applied to the polarity **magnitudes**, with **directions redrawn uniformly at random** — preserves the
  polarity-magnitude distribution exactly, **destroys coherent polarity and the rho↔p correlation**.

Preserved: support geometry, total material, per-species mass, per-cohort mass, multiset of local scalar values,
polarity-magnitude distribution, destination, perturbation magnitude. Destroyed: coherent polarity, cross-field
spatial correlations, internal spatial organization. **Nothing else differs from INTACT.**

## Executable assertions (R5) — every intervention must be proven to change its intended variable
Per unit, all must hold or the run aborts: SHAM is bitwise identical to CONTROL in every field; INTACT conserves
total rho and total R exactly and actually moved the cargo; SCRAMBLED has **identical** total rho, total R, per-cohort
masses, sorted rho multiset and sorted |p| multiset to INTACT's cargo; and SCRAMBLED's **polar order is strictly
less than half** the intact cargo's, and |corr(rho, |p|)| is strictly reduced.

## Readout (frozen)
The entity **moves**, so it is tracked: seeded from entities within `SITE_RADIUS=10` of the destination, then
followed to the nearest entity within a gate of `0.8 * cadence` cells per snapshot. AUDITED requires **jointly**:
1. SHAM ≡ CONTROL; 2. **re-establishment** — phenotype continuity > 0.8 in > 0.5 of post snapshots, **under BOTH
phenotypes**; 3. **no old-site regeneration** at the original centroid; 4. **sustained motility** — mean tracked
speed > **0.25 cells/step**; 5. **continued temporal-cohort turnover** — min cohort-Jaccard M < 0.5 at lags (1,3,6).

**Two frozen phenotypes; both must pass.** FULL includes polar order and speed. **BLIND is geometry and mass only and
cannot see polarity at all.** BLIND exists to defeat the obvious objection that a polarity-aware observable makes the
scrambled-polarity null fail by construction. If INTACT beats SCRAMBLED only under FULL, that is an artefact of the
observable and **GATE-0 does NOT pass**.

**Observer sensitivity (R6):** physics computed once per branch at a fixed `t* = 300` (NOT cadence-derived);
the observer is then varied **offline** over 27 settings — cadence {5,10,15} × site radius {0.8,1.0,1.2} ×
tracker gate {0.8,1.0,1.2}. HORIZON = 300. Endpoint **AUDITED_ROBUST** = audited in **all 27** settings under
**both** phenotypes.

### Instrument corrections made BEFORE freezing (full disclosure)
A smoke test on seed 30001 and the qualification run exposed three defects in my first draft of the readout. All are
**instrument** faults — settings under which *no* arm can be measured — and all were fixed from
**qualification-derived quantities only**, never from a GATE-0 outcome:

1. **Tracker gate too small.** Qualification measured the reference pattern travelling at **0.95 cells/step** — it is
   a *traveling wave*: the PATTERN outruns its own material, whose advective speed is capped at v0 = 0.55. My gate
   (0.8 × cadence) was below the pattern speed, so the tracker lost **every** arm. Gate set to **1.5 cells/step**.
2. **Tracker seeding ignored motility.** The entity has already moved by up to one gate before the first post
   snapshot, so the initial search radius is `SITE_RADIUS + gate`.
3. **Cadences {25,50,100} are INADMISSIBLE observers.** At 0.95 cells/step a cadence-100 snapshot advances the
   pattern ~95 cells on a 64-lattice — it wraps 1.5× per sample, below Nyquist for the trajectory. Those settings
   failed *all three arms identically*, measuring nothing. **Sampling-adequacy criterion, declared from
   qualification:** an observer is admissible only if `speed × cadence ≤ L/4 = 16` cells. Hence {5, 10, 15}
   (0.95 × 15 = 14.3 ✓).

**Seeds moved to 31001–31030.** Seed 30001 was burned on the smoke test and is excluded: no unit I have looked at
enters the frozen run. Instrument validation was done on seeds 99001/99002, outside the GATE-0 set.

*Note on PLACEBO, confirming R2:* on the validation seeds the non-entity PLACEBO scored 24/27 — it re-establishes
almost as well as the intact entity. It is a **straw-man control** and is reported for completeness only; it carries
**no eliminative weight** and enters **no** decision rule. Pooling it with the scrambled null — the exact error that
produced the Gray-Scott false positive — is forbidden.

## Predeclared statistics and decision
Fixed **N = 30 seeds** (31001–31030). Denominator = enrolled units, stated explicitly. Wilson 95 % per arm,
**each arm reported separately — no pooling of unequal nulls (R1)**.
- Primary: **paired exact two-sided McNemar**, INTACT vs SCRAMBLED.
- Effect-size margin: **MARGIN = 0.25** absolute on `p_intact − p_scrambled`, plus Newcombe 95 % LB > 0.

**GATE-0 PASSES iff all three hold:** G1 `p_intact > 0`; G2 McNemar p < 0.05; G3 `p_intact − p_scrambled > 0.25`
**and** Newcombe LB > 0.

**If GATE-0 passes** → a blind low-discrepancy law map may begin (and not before).
**If GATE-0 fails** → the substrate is **RETIRED IMMEDIATELY**. No re-tuning, no mechanism addition, no second look.

**Stopping:** fixed N = 30, no interim inspection, no sequential stopping, no extension of N after seeing results.
