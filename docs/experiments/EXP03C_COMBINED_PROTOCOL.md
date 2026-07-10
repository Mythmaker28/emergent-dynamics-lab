# EXP03-C-COMBINED-COREV0-20260710-001 — Frozen Protocol (preregistered before screening)

Status: **FROZEN before any screening result was inspected.** Preregistered by `RUN-20260710-1945-EXP03C`.
Authorized by D-019 (EXP03-B negative). Final Particle Dynamics causal family before a substrate decision.
Mechanism validated: 91/91 tests incl. bitwise neutral limit and partial-limit recovery of EXP03-A/EXP03-B.

## QUESTION
Does adding BOTH the density-preference and the orbital/transverse mechanisms together enrich the regime of high
phenotype continuity `P` under low material retention `M`, compared with CORE V0? Tests the combined causal family
(the charter's EXP03-C). Mutation OFF, type transition OFF, recycling OFF.

## MECHANISM
Combined force = frozen CORE V0 + EXP03-A density-preference term + EXP03-B orbital term (both validated). Density:
homeostatic force toward a comfortable local neighbour count (`DensityPreferenceSpec`). Orbital: transverse pair
force perpendicular to the connecting line, momentum-conserving, circulation-injecting (`OrbitalSpec`).
- **NEUTRAL LIMIT:** `density_strength = 0 AND orbital_strength = 0` reduces to CORE V0 bit-for-bit (tested on 5
  worlds). Setting only one strength to zero recovers the EXP03-B or EXP03-A path exactly (partial-limit tests).
- **NEW PARAMETERS:** `DensityPreferenceSpec(density_strength, comfortable_density, density_radius)` and
  `OrbitalSpec(orbital_strength, orbital_range)` paired with the unchanged core `LawSpec`. Type-agnostic; isolated.

## CAUSAL CONTRAST / LAW PARAMETERIZATION
Matched OFF (both strengths 0 = CORE V0) vs ON (both on). Core via frozen `law_from_halton(i)`; density from Halton
dims 13-15, orbital from dims 16-18 of `halton_point(i+32,19)` (the built-in prime table was extended additively to
19 primes; dims 0-12 identical to CORE V0, dims 13-15 identical to EXP03-A, dims 13-15 of EXP03-B unaffected).
Ranges: density_strength [0.2,2.0], comfortable_density [1.0,8.0], density_radius [0.12,0.28]; orbital magnitude
[0.4,1.6], orbital_range [0.12,0.28], chirality sign from dim 18.

## SAMPLING / SEEDS / WORLD / RUN / CADENCES / TRACKER / P&M
64 Halton laws x {OFF,ON} x seeds {7001,7002,7003} x cadences {10,30,60}; three seeds is SCREENING, not a
probability. `WorldSpec(64,3,box=1,initial_speed=0.04)`, `dt=0.02`, `steps=600` (12.0 units), vectorized. Frozen
`TrackerSpec(0.16,0.25)`; frozen `M`=Jaccard(IDs), `P`=exp(-RMS(dPhi)); joint retained; NO composite; `P>0.8,M<0.5`
is only the INITIAL EXPLORATORY PROBE. Mean |internal circulation| reported OFF vs ON.

## GATE / PSEUDOREPLICATION / CENSORING / NULLS
Frozen CORE V0 candidate rule: probe-positive on a track-clean, long (>=8 obs) track under >=2 cadences; seed
eligible with >=1 such endpoint; (law, condition) earns SCREENING PERMISSION at >=2/3 seeds. Rows pseudoreplicated
(descriptive). Final-snapshot tracks right-censored and counted. Frozen CORE V0 nulls remain live.

## FRESH-SEED HOLD-OUT / ALIAS AUDIT / DECISION / FALSIFIERS
If any (law, ON) earns permission: frozen 5 fresh-seed hold-out (>=2/5) -> direct alias audit -> same-state
matched-branch causal intervention if authorized. If none: **EXP03-C SCREEN = NEGATIVE**; then the Particle
Dynamics substrate is exhausted for this ladder and a substrate decision is due per the charter. Do not lower
`>=2/5` or P/M; no visual selection; no replacement of rejected laws. Falsifiers: F1 ON does not exceed OFF
eligible-law count; F2 any ON enrichment explained by densification/rigidity/vortex-trapping/mixing rather than
turnover-individuality; F3 permitted laws fail fresh-seed hold-out; F4 survivors alias-compatible.

## VALIDATION GATE (before screening)
`pytest tests/test_exp03c_combined.py` (11) + full suite (91) green; neutral limit bitwise on several worlds;
partial limits recover EXP03-A/EXP03-B; reference/vector agreement inherited from the validated sub-mechanisms.

## REPRODUCTION
`python -m edlab.experiments.exp03c_combined_cli --output results/EXP03C-COMBINED-COREV0-20260710-001
--experiment-id EXP03C-COMBINED-COREV0-20260710-001 --protocol-sha <this commit>`.
