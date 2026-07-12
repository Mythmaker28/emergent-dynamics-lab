# EXP-MO-00 — QUALIFICATION FAILED. Motile polar substrate RETIRED before GATE-0.

**GATE-0 was never run.** The substrate does not produce a localized entity, so there is nothing to displace, and
no arm of GATE-0 could have measured anything.

## What happened
The active phase is a Fisher-KPP-type invasion front: growth `g0*rho*R` with homogeneous nutrient feed, no
carrying capacity and no cohesion. Its uniform steady state is analytic:

`rho* = F * (R0 - k/g0) / k`

The substrate is therefore **bistable between the only two outcomes that contain no entities**:
- `rho* > detector threshold (0.30)` → the active phase **invades the entire domain**. At F=0.030, k=0.060,
  g0=0.25 → rho* = 0.38, and the "detected entity" at t*=300 is **4096 of 4096 cells — the whole lattice**.
- `rho* < 0.30` → the structure **goes extinct**; no entity is detected at all.

Two preregistered qualification grids, **21 parameter points total**, found no localized regime:
grid 1 (F ∈ {0.002,0.005,0.010} × k ∈ {0.10,0.15} × g0 ∈ {0.25,0.40}) — 12/12 extinct;
grid 2, derived analytically to put rho* below threshold (F ∈ {0.020,0.030,0.040} × k ∈ {0.08,0.10,0.12}) —
8/9 extinct, 1/9 space-filling. Selection criteria (localization ≤ 15 % of domain, persistence ≥ 80 %, speed
≥ 0.25 cells/step, cohort turnover M < 0.5, support disjoint from its own translate) were declared **before**
searching and never referenced intact-vs-scrambled separation.

**The search stops here.** Polarity advects material but nothing holds a structure together. Producing a localized
entity would require adding a cohesion / density-dependent aggregation mechanism — that is precisely a **rescue
mechanism**, and it is forbidden. The substrate is retired.

## TWO RESULTS OF MINE THAT ARE VOID — stated plainly
1. **The first qualification is VOID.** It reported the reference structure as persistent (24/24), motile
   (0.95 cells/step) and fully turned over (min M ≈ 8e-7). Those numbers were computed on a **space-filling field**
   whose periodic centroid is ill-defined and simply jitters. There was no structure. The "traveling wave whose
   pattern outruns its material" — which I used to justify the tracker gate — was an artefact of that centroid.
2. **The instrument validation is VOID.** On seeds 99001/99002 it showed **INTACT 27/27 robust vs SCRAMBLED 0/27** —
   a spectacular-looking separation. It was displacing **the entire lattice**. Had the conservation assertion not
   fired, this is the number I would have reported.

**What caught it was R5** — the executable assertion that an intervention must actually do what it claims. The
displacement of a whole-domain "entity" cannot conserve mass (its support overlaps its own translate), the
assertion failed loudly on the first real unit, and the artefact collapsed. This is the entire value of R5, earned
back within one experiment of writing it down.

## Methodology gap this exposes → R7
I designed the substrate around the *sophisticated* prerequisite (is organization load-bearing?) and never checked
the *elementary* one (**is there a localized entity at all?**). A space-filling phase and an extinct phase both
trivially have no individuals. **R7 is added: before GATE-0, a substrate must be shown to produce localized
structures — size « domain — that persist and turn over. GATE-0 presupposes an entity; localization must be
proven first.**
