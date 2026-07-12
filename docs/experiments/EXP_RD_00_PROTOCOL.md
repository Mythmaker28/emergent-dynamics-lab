# EXP-RD-00 — Frozen Protocol: OPEN reaction-diffusion substrate + qualification and measurement controls

Status: **FROZEN.** Preregistered by `RUN-20260710-2330-EXPRD00`. Authorized by D-027 (Flow-Lenia closed system
retired; EXP-FL-02 positive withdrawn). NO law search until this gate passes.

## SUBSTRATE (minimal, genuinely open)
Gray-Scott:  dU/dt = Du*lap(U) - U*V^2 + F*(1-U);  dV/dt = Dv*lap(V) + U*V^2 - (F+k)*V.
- **Feed and removal are SPATIALLY HOMOGENEOUS and DETECTOR-INDEPENDENT**: F and k are scalars applied identically
  at every cell and depend only on the LOCAL field value. They cannot reference any structure, entity or detector.
- **Genuinely OPEN**: real source (+F) and real sinks (-F*U, -(F+k)*V). Material is NOT conserved. Non-equilibrium
  driving. (Verified from a non-equilibrium uniform state: the total grows.)
- **EXACT CONTROLLED LIMIT**: F = 0 AND k = 0 removes source and both sinks, leaving diffusion + the U->V reaction
  transfer, which conserves U+V EXACTLY. This CLOSED limit is the matched control for the OPEN system.
- Operator-split explicit scheme (declared): diffuse -> reaction transfer -> V removal -> U removal + feed.

## PASSIVE ORIGIN TRACERS
Cohorts partition BOTH species (sum_c CU = U, sum_c CV = V). Indices 0..7 = initial spatial origin (the verified
G*=8 resolution, D-024); index 8 = **FEED cohort** = material introduced from OUTSIDE. Cohorts are moved by
exactly the same operators as their fields; the reaction transfer carries the source species' LOCAL cohort
proportions; removal scales all cohorts equally; the feed deposits into the FEED cohort. Cohorts NEVER influence
U, V, or any rate (verified: zeroing them leaves U and V bit-identical).

## MEASUREMENT STACK (P/M separation preserved; thresholds frozen)
Detector: threshold V and take periodic connected components (>= min_cells). Association: the FROZEN geometry/size
LineageTracker. Phenotype: geometry (V-mass fraction, radius of gyration, anisotropy, radial quantiles) PLUS the
OPEN-SYSTEM dynamical observables (production U*V^2, removal (F+k)V, activity |dV/dt|), with P = exp(-RMS dPhi)
UNCHANGED and declared (not tuned) scales. M(tau) = cohort mass Jaccard. Probe P>0.8, M<0.5 unchanged. No composite.

## THE IMPOSED-PATTERN QUESTION (explicitly tested)
Any "individuality" must not be a spatial pattern continuously imposed by the external forcing. Two guards:
1. **HOMOGENEITY NULL:** the forcing is spatially homogeneous, so a uniform state must remain EXACTLY uniform
   forever. Verified (ptp = 0.0 over 400 steps). The forcing therefore cannot imprint any spatial structure; every
   structure is self-organized.
2. **NEGATIVE (STATIC-FLUX / IMPOSED-PATTERN) CONTROL:** a frozen pattern with identical geometry and identical
   cohort turnover but ZERO production/removal/activity. It is INDISTINGUISHABLE from a real dissipative
   organization on P/M alone (both P=1.0, M_min=0.065, 83 probe rows) and is separated ONLY by the open-system
   rates (production/activity 0.000 vs 0.117/0.085). Any future candidate must clear this separation.
3. In the causal intervention, re-appearance of the structure at the OLD site after displacement would indicate an
   externally maintained spatial slot (occupancy) and is an alias, not individuality.

## QUALIFICATION GATE (binary; all must pass)
openness (material not conserved) | exact closed limit (F=k=0 conserves) | homogeneity null (no imposed pattern) |
tracer partition | FEED cohort grows | tracers passive | determinism | nonnegativity | reference-path agreement
(two Laplacian implementations) | detector/tracker on real dynamics (a track of length >= 3) | positive control
recognized | negative control separated.

## DECISION
PASS -> preregister and launch EXP-RD-01, a BLIND low-discrepancy map over (F, k, Du, Dv), matched OPEN vs the
exact CLOSED limit, under the five evidence levels, frozen P/M and thresholds, the continued-turnover requirement,
CONTROL/SHAM/PERTURBED/PLACEBO causal discipline and observer-sensitivity checks.
FAIL -> stop and audit; no law search.
