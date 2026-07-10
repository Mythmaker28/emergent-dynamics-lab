# HOLDOUT-COREV0-20260710-004 — EXP02 fresh-seed diagnostic

**Status:** PREREGISTERED BEFORE EXECUTION.

## Parent and scope

- Parent: `EXP02-COREV0-20260710-001`, 900/900 runs at SHA `6c593780ab33326fd0957f73bb885bfe1c15ab84`.
- Frozen eligible laws: `{0,12,35,52,73,94,209,225,298}`.
- These are all laws satisfying the preregistered same-endpoint, independently clean cross-cadence rule in at least two of screening seeds `{2001,2002,2003}`. No raw-probe-rate ranking or post-hoc exclusion is used.
- Direct audit covers 47 cadence rows / 22 endpoints for these laws: P/M recomputation errors are zero and no compatible unselected edge is hidden, but zero rows reject static occupancy or sparse look-alike alias. This hold-out is diagnostic recurrence only.

## Fresh seeds and runs

- Unseen seeds: `{3001,3002,3003,3004,3005}`.
- Nine laws × five seeds = 45 runs.
- Five seeds are not a probability estimate.

## Fixed simulation and observer settings

- 64 particles, 3 types, unit periodic box.
- `dt=0.02`, 600 steps, simulated time 12.
- Vectorized backend; law mapping and every CORE V0 force, detector, phenotype, tracker, lag, cadence `{10,30,60}`, P, M, null, and threshold remain unchanged.
- Mutation, neighbor-induced transition, recycling, density preference, orbital interaction, and substrate switching remain OFF.

## Frozen per-seed gate

A law qualifies in one fresh seed only if at least one physical endpoint `(start_step,end_step)` is probe-positive (`P>0.8,M<0.5`) under at least two observer cadences, and every contributing cadence independently uses a track with at least eight observations and no split, merge, or ambiguous-association event anywhere on that track.

A law survives this hold-out only if it qualifies in at least **two of five** fresh seeds. The count is a recurrence gate, not an estimate of `P(event|law)`.

## Interpretation boundary

- Failure below `2/5` rejects that law without replacement or threshold relaxation.
- Survival authorizes direct dense-trajectory/intervention design only. It does not reject the mandatory static-flux or sparse look-alike null and is not evidence of individuality.
- All probe and surviving rows retain `unresolved_sparse_alias_risk=True`.

## Execution and analysis

```powershell
.\.venv\Scripts\python.exe -m edlab.cli baseline `
  --output results\HOLDOUT-COREV0-20260710-004 `
  --experiment-id HOLDOUT-COREV0-20260710-004 `
  --laws 9 --law-indices 0 12 35 52 73 94 209 225 298 `
  --kind holdout --seeds 3001 3002 3003 3004 3005 `
  --particles 64 --steps 600 --cadences 10 30 60

.\.venv\Scripts\python.exe -m edlab.experiments.audit_candidates `
  results\HOLDOUT-COREV0-20260710-004
```

The final disposition must be computed only from `cross_cadence_seeds_by_law` under the corrected clean-cadence join. Preserve raw tables, manifest, candidate rows, hashes, summaries, and figures.

## Stop / next-stage rule

- If no law survives `>=2/5`, record a negative CORE V0 hold-out and advance to the already authorized EXP03-A causal extension; do not substitute a non-eligible law.
- If one or more laws survive, freeze the survivor set and design an intervention that can reject static occupancy/look-alike flux before any perturbation-recovery claim.
