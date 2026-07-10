# EXP03-A-DENSITY-COREV0-20260710-001 — Frozen Protocol (preregistered before screening)

Status: **FROZEN before any screening result was inspected.** Preregistered by `RUN-20260710-1850-EXP03A`.
Authorized by D-017 (CORE V0 closed CASE A). Mechanism validated: 63/63 tests incl. bitwise neutral limit.

## QUESTION

Does adding an isolated density-preference / comfortable-neighbour mechanism enrich the regime of high phenotype
continuity `P` under low material retention `M`, compared with CORE V0? This isolates the DENSITY PREFERENCE
causal family only. No orbital/transverse interaction, no mutation, no type transition, no recycling.

## MECHANISM

- **WHAT LOCAL QUANTITY IS MEASURED?** A soft local neighbour count (density proxy) for particle i:
  `rho_i = sum_{j!=i, d_ij<R} (1 - d_ij/R)` using periodic minimum-image distances `d_ij` and radius `R`.
- **HOW DOES IT MODIFY THE FORCE?** An added term `F_density_i = density_strength * (comfortable_density - rho_i)
  * ghat_i`, where `ghat_i` is the unit direction toward the kernel-weighted local neighbour mass
  `h_i = sum K_ij * (pos_j - pos_i)` (minimum image), and `ghat_i = 0` when `|h_i|` is below 1e-12. Total force =
  frozen CORE V0 force + `F_density_i`. Integration/damping unchanged.
- **WHAT IS THE COMFORTABLE REGION?** `rho_i ~ comfortable_density`, where the added force vanishes.
- **WHAT HAPPENS BELOW IT?** `rho_i < comfortable_density` -> coefficient positive -> force toward neighbours
  (seek density).
- **WHAT HAPPENS ABOVE IT?** `rho_i > comfortable_density` -> coefficient negative -> force away from the local
  neighbour mass (relieve crowding). This homeostatic sign-flip is a many-body property a pairwise type force
  cannot represent.
- **IS THE MECHANISM TYPE-SPECIFIC?** No. It is type-agnostic and isolated (a single scalar mechanism), kept
  separate from the CORE V0 type-interaction matrix so the causal family is not conflated.
- **WHAT NEW PARAMETERS ENTER LawSpec?** `DensityPreferenceSpec(density_strength, comfortable_density,
  density_radius)`, paired with the unchanged core `LawSpec`.
- **WHAT PARAMETER VALUES REDUCE EXACTLY TO CORE V0?** `density_strength = 0` (the NEUTRAL LIMIT). Verified
  bit-for-bit against CORE V0 `simulate()` on several controlled worlds
  (`tests/test_exp03a_density.py::test_neutral_limit_equals_core_v0_bitwise`).

## CAUSAL CONTRAST TO CORE V0

Matched design: every core law index i and seed is run in TWO conditions — **OFF** (`density_strength=0`, exactly
CORE V0 on that law/seed) and **ON** (sampled density params). The OFF arm is the within-experiment CORE V0
comparator; the frozen EXP02 screen is an additional historical comparator. Same frozen observers and P/M
normalisation are used for both — no recalibration.

## NEUTRAL LIMIT

`density_strength = 0` -> added force is exactly 0.0 (guarded finite direction) -> total force == CORE V0 force ->
trajectory identical to CORE V0. Tested bitwise on 5 worlds; the OFF condition IS this limit.

## LAW PARAMETERIZATION

Core `LawSpec` via the frozen `law_from_halton(i)` (unchanged). Density params from Halton dims 13,14,15 of
`halton_point(i+32, 16)` (the radical inverse for the extra primes; dims 0..12 are identical to CORE V0):
`density_strength in [0.2, 2.0]` (ON), `comfortable_density in [1.0, 8.0]`, `density_radius in [0.12, 0.28]`.

## SAMPLING PLAN

Deterministic low-discrepancy screen of **64 laws** (Halton indices 0..63) x **2 conditions {OFF, ON}** x
**3 seeds** x **3 cadences**. Three seeds per law per condition is a SCREENING, not a P(event|law) estimate.

## SEEDS

`{7001, 7002, 7003}` (fresh; screening used 2001-2003, hold-out 3001-3005, alias-intervention 5001-5040 — none
reused). World seeding `seed + 100000*law_index`.

## WORLD SPEC

`WorldSpec(n_particles=64, n_types=3, box_size=1.0, initial_speed=0.04)`.

## RUN SPEC

`dt=0.02`, `steps=600`, backend vectorized (validated vs scalar reference), snapshot interval = min cadence (10).

## SIMULATED TIME

`600 * 0.02 = 12.0` time units.

## SNAPSHOT CADENCES

`{10, 30, 60}` steps.

## TRACKER CONFIG

`TrackerSpec(max_centroid_distance=0.16, min_size_ratio=0.25)`; association by periodic centroid distance and
size ratio only; IDs/M/P never in the association gate; all edges and lineage events logged (frozen CORE V0).

## P AND M DEFINITIONS

Frozen and unchanged: `M(tau)` = Jaccard of diagnostic constituent-ID sets; `P(tau) = exp(-RMS(Phi_t - Phi_t+tau))`
with the committed dimensionless phenotype `Phi`. The joint `(P,M)` is retained. **No composite score.** The
quadrant `P>0.8, M<0.5` is only the INITIAL EXPLORATORY PROBE, not an identity definition.

## SCREENING GATE

Identical to the frozen CORE V0 candidate rule: an endpoint (start,end) is eligible if probe-positive
(`P>0.8, M<0.5`) on a track-clean (no split/merge/ambiguous), long (>=8 observations) track under >=2 cadences.
A seed is eligible if it has >=1 such endpoint. A **(law, condition)** earns SCREENING PERMISSION if eligible in
**>= 2 of 3 seeds**. This is a permission for fresh-seed hold-out, not a scientific candidate.

## PSEUDOREPLICATION HANDLING

Rows repeat tracks, overlapping windows, cadences and lags; all P/M summaries are descriptive. Gate uses
per-seed eligibility and per-(law,condition) seed counts, not raw row counts.

## RIGHT-CENSORING

Tracks alive at the final snapshot are right-censored and counted; absence of an endpoint before the horizon is
censored, not evidence of impossibility.

## NULL MODELS

The frozen CORE V0 nulls remain live: ID-permutation, static-motif-with-material-flux (expected probe-positive
false positive), tracker/cadence-sensitivity, and sparse look-alike alias. Any ON candidate must be read against
these exactly as CORE V0 candidates are.

## TRACKER / CADENCE SENSITIVITY

Eligibility already requires the SAME physical endpoint to be probe-positive under >=2 cadences (cadence
robustness). Cadence structure of P/M is reported descriptively for OFF and ON.

## FRESH-SEED HOLD-OUT RULE

If any (law, ON) earns screening permission, freeze those laws and run a hold-out on 5 fresh unseen seeds with
unchanged settings; retain a law only at `>= 2/5`. (Same frozen rule as CORE V0; not lowered.)

## ALIAS AUDIT RULE

Diagnostic survivors get the direct P/M/edge audit and, if authorized, the same-state matched-branch
alias-intervention (CONTROL/SHAM/PERTURBED/PLACEBO) discipline used for CORE V0. Screening/recurrence never
equals alias rejection.

## DECISION RULE

- If **no (law, ON)** earns screening permission -> **EXP03-A screening = NEGATIVE** for the enriched-candidate
  question; document and advance to EXP03-B per the charter. (A descriptive P/M distributional shift may still be
  reported, distinctly from a candidate.)
- If some (law, ON) earn permission -> proceed to frozen fresh-seed hold-out -> diagnostic survivors only ->
  direct alias audit -> same-state causal intervention if authorized. Do not present a screening law as a
  scientific candidate; do not select visually; do not replace a rejected law; do not lower `>=2/5` or P/M.

## FALSIFIERS

- F1: ON does not increase eligible (law, condition) count over OFF (no enrichment of the candidate regime).
- F2: any ON enrichment of P or long tracks is explained by densification / rigid clusters / bridge artefacts /
  reduced mobility / longer slot residence rather than turnover-individuality (PASS B explanations).
- F3: ON screening-permitted laws fail the frozen fresh-seed hold-out.
- F4: apparent survivors are alias-compatible (occupancy / look-alike / tracker reassignment) under audit.

## VALIDATION GATE (must pass before screening)

`pytest tests/test_exp03a_density.py` (17) and the full suite (63) green; neutral limit bitwise on several worlds;
reference/vector agreement at `abs(err) <= 1e-12 + 1e-10*abs(ref)`.

## REPRODUCTION

`python -m edlab.experiments.exp03a_density_cli --output results/EXP03A-DENSITY-COREV0-20260710-001
--experiment-id EXP03A-DENSITY-COREV0-20260710-001 --protocol-sha <this commit>`.
