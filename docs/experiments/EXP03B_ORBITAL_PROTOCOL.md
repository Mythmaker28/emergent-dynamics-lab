# EXP03-B-ORBITAL-COREV0-20260710-001 — Frozen Protocol (preregistered before screening)

Status: **FROZEN before any screening result was inspected.** Preregistered by `RUN-20260710-1930-EXP03B`.
Authorized by D-018 (EXP03-A negative). Mechanism validated: 80/80 tests incl. bitwise neutral limit, momentum
conservation, and circulation injection.

## QUESTION
Does adding an isolated orbital / transverse interaction (a tangential pair force perpendicular to the connecting
line) enrich the regime of high phenotype continuity `P` under low material retention `M`, compared with CORE V0?
Isolates the ORBITAL family only. Density OFF, mutation OFF, type transition OFF, recycling OFF.

## MECHANISM
- **WHAT LOCAL GEOMETRY IS USED?** For a pair within `orbital_range`, the in-plane direction perpendicular to the
  periodic minimum-image connecting vector `u_ij`: `t_ij = rot90(unit(u_ij)) = (-uy, ux)`.
- **HOW DOES IT MODIFY THE FORCE?** Adds `F_orbital_i = sum_j orbital_strength * env(d_ij) * t_ij`, with a
  triangular envelope `env` peaking at `orbital_range/2`. Total = frozen CORE V0 force + `F_orbital`. Integration/
  damping unchanged.
- **WHAT IS THE EFFECT?** The pair force is equal-and-opposite (linear momentum conserved) but exerts a torque
  about the pair midpoint, injecting circulation / vorticity. `orbital_strength` sign sets chirality (CW/CCW).
- **IS IT TYPE-SPECIFIC?** No — type-agnostic and isolated (a single scalar mechanism), kept separate from the
  CORE V0 type-interaction matrix.
- **WHAT NEW PARAMETERS ENTER LawSpec?** `OrbitalSpec(orbital_strength, orbital_range)`, paired with the
  unchanged core `LawSpec`.
- **WHAT VALUES REDUCE EXACTLY TO CORE V0?** `orbital_strength = 0` (NEUTRAL LIMIT). Verified bit-for-bit on 5
  controlled worlds (`tests/test_exp03b_orbital.py::test_neutral_limit_equals_core_v0_bitwise`). Momentum
  conservation and a from-rest circulation-injection contrast are tested; a central (radial) interaction cannot
  reproduce the injected angular momentum.

## CAUSAL CONTRAST TO CORE V0 / NEUTRAL LIMIT
Matched design: each core law index i and seed is run OFF (`orbital_strength=0` = CORE V0) and ON (sampled). OFF
is the within-experiment CORE V0 comparator; EXP02 is an additional historical comparator. Frozen observers, no
recalibration.

## LAW PARAMETERIZATION
Core `LawSpec` via frozen `law_from_halton(i)`. Orbital params from Halton dims 13,14,15 of `halton_point(i+32,16)`
(dims 0..12 identical to CORE V0): magnitude in [0.4, 1.6], `orbital_range` in [0.12, 0.28], chirality sign from
dim 15. ON `orbital_strength = sign * magnitude`; OFF `orbital_strength = 0`.

## SAMPLING PLAN / SEEDS / WORLD / RUN / TIME / CADENCES
64 Halton laws (0..63) x {OFF, ON} x seeds {7001,7002,7003} x cadences {10,30,60}. Three seeds per condition is a
SCREENING, not a P(event|law) estimate. `WorldSpec(64,3,box=1,initial_speed=0.04)`; `dt=0.02`, `steps=600`
(12.0 time units), vectorized backend; snapshot interval = 10.

## TRACKER CONFIG / P AND M
Frozen `TrackerSpec(0.16,0.25)`; association by centroid distance + size ratio only; IDs/M/P never in the gate;
all edges/events logged. `M(tau)` Jaccard of diagnostic IDs; `P(tau)=exp(-RMS(dPhi))`; joint retained; NO composite
score; `P>0.8,M<0.5` is only the INITIAL EXPLORATORY PROBE.

## SCREENING GATE / PSEUDOREPLICATION / CENSORING
Frozen CORE V0 candidate rule: probe-positive on a track-clean, long (>=8 obs) track under >=2 cadences; a seed is
eligible with >=1 such endpoint; a (law, condition) earns SCREENING PERMISSION at >=2/3 seeds. Rows are
pseudoreplicated (descriptive only). Tracks alive at the final snapshot are right-censored and counted.

## NULL MODELS / TRACKER-CADENCE SENSITIVITY
Frozen CORE V0 nulls remain live (ID-permutation, static-motif-material-flux, tracker/cadence-sensitivity, sparse
look-alike). Eligibility already requires >=2 cadences. Mean |internal circulation| is reported OFF vs ON.

## FRESH-SEED HOLD-OUT / ALIAS AUDIT / DECISION / FALSIFIERS
If any (law, ON) earns permission: freeze and run the 5 fresh-seed hold-out (>=2/5), then direct alias audit,
then same-state matched-branch causal intervention if authorized (identical discipline to CORE V0). If none:
**EXP03-B SCREEN = NEGATIVE**; advance to EXP03-C per the charter. Do not lower `>=2/5` or P/M; do not select
visually; do not replace a rejected law; do not present a screening law as a candidate. Falsifiers: F1 ON does not
exceed OFF eligible-law count; F2 any ON enrichment explained by vortex trapping / regular circulatory motion /
tracker-friendly rotation rather than turnover-individuality; F3 permitted laws fail fresh-seed hold-out; F4
survivors alias-compatible.

## VALIDATION GATE (before screening)
`pytest tests/test_exp03b_orbital.py` (17) + full suite (80) green; neutral limit bitwise on several worlds;
reference/vector agreement at `abs(err) <= 1e-12 + 1e-10*abs(ref)`; momentum conservation.

## REPRODUCTION
`python -m edlab.experiments.exp03b_orbital_cli --output results/EXP03B-ORBITAL-COREV0-20260710-001
--experiment-id EXP03B-ORBITAL-COREV0-20260710-001 --protocol-sha <this commit>`.
