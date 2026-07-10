# AGENTS.md

## Operating contract

The repository is the durable memory. Do not rely on chat context. Before acting, read in order:

1. `AGENTS.md`
2. `docs/RESEARCH_CHARTER.md`
3. `docs/PROJECT_STATE.md`
4. `docs/DECISION_LOG.md`
5. `docs/EXPERIMENT_INDEX.md`
6. `docs/RUN_INDEX.md`
7. the latest completed or partial journal under `docs/agent_journals/`
8. the manifest and summary of the current or last experiment

Inspect Git state before changes. Do not assume the preceding handoff is correct.

## Mandatory scheduled-run lock

The native heartbeat wakes every **30 minutes**. This is a wake cadence, not a runtime limit. Before a scheduled run changes files or launches an experiment, acquire the conservative lock:

```powershell
$head = git rev-parse HEAD
.\.venv\Scripts\python.exe -m edlab.runtime_lock acquire `
  --run-id SCHED-YYYYMMDD-HHMM-NNN `
  --task-identity emergent-dynamics-lab-autonomous-research `
  --starting-head $head `
  --experiment EXPERIMENT-ID
```

If it reports `SKIPPED_DUE_TO_ACTIVE_RUN`, create the minimal journal/index disposition when safe and end without overlapping work. Never delete a lock because of age alone. Verify its owner and execution state. Release only the matching run ID after a genuine finish or clean checkpoint:

```powershell
.\.venv\Scripts\python.exe -m edlab.runtime_lock release --run-id SCHED-YYYYMMDD-HHMM-NNN
```

## Journal requirement

Every agent and subagent creates its own unique journal:

`docs/agent_journals/YYYY-MM-DD/HHMM_role_RUN-ID.md`

It must record role, run ID, start/end time, starting/ending Git state, assigned scope, actions, important files read/changed, reproducible commands/experiments, OBSERVED, INFERRED, HYPOTHESIS, WHAT WOULD FALSIFY THIS?, failures/dead ends, decisions, unresolved risks, and handoff. Never rewrite another agent's historical journal to hide an error; append a correcting journal instead.

## Scientific invariants

- Diagnostic particle IDs never influence physics, detection, or tracker association.
- The tracker must not optimize or hard-gate on final `P` or material Jaccard `M`. Association uses predeclared physical geometry/size terms and logs alternatives.
- Keep `P(tau)` and `M(tau)` as a joint distribution. Do not add `P*(1-M)`, `theseus_score`, `memory_score`, or an equivalent composite.
- `P > 0.8, M < 0.5` is only `INITIAL EXPLORATORY PROBE — NOT AN IDENTITY DEFINITION`.
- Do not lower thresholds after a negative result.
- The static motif with complete material flux is an expected probe-positive null, not a discovery.
- Historical values are labeled precisely. Code/tests/artefacts at `9992e6c` were audited; the historical simulation was not independently rerun.
- Mutation, neighbor-induced type transition, and particle recycling remain OFF.
- Do not switch substrate before EXP02 and EXP03-A/B/C plus tracker/cadence/time controls meet the documented Particle Dynamics kill-switch.

## Required validation

- Run relevant tests after code changes.
- Compare any physics/backend change to the scalar reference path at the frozen float64 criterion `abs(error) <= 1e-12 + 1e-10*abs(reference)`.
- Run tracker/cadence sensitivity controls before interpreting rare candidates after tracker, detector, or cadence changes.
- Preserve raw descriptor and lineage evidence needed to audit P/M.
- Three seeds per law are screening, never a reliable probability estimate.

## Authorized sequence

`vertical slice -> current independent baseline -> EXP02 -> held-out fresh seeds if predefined signal; otherwise EXP03-A -> EXP03-B -> EXP03-C -> Particle Dynamics decision`.

Do not invent a direction merely to keep the automation busy.

## End of every working run

1. run relevant tests;
2. inspect Git state;
3. finalize the individual journal;
4. update `docs/RUN_INDEX.md`;
5. update `docs/PROJECT_STATE.md` when state changed;
6. update `docs/EXPERIMENT_INDEX.md` when experiment state changed;
7. update `docs/DECISION_LOG.md` only for a genuine decision;
8. identify the active experiment and index outputs;
9. commit coherent useful work;
10. push when authentication permits;
11. release the active-run lock only after finish/checkpoint;
12. leave one exact next authorized action.

