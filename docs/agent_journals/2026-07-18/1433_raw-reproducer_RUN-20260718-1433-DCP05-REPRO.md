# Raw reproducer audit — RUN-20260718-1433-DCP05-REPRO

- **Role:** raw-reproducer audit subagent
- **Run ID:** `RUN-20260718-1433-DCP05-REPRO`
- **Start time:** 2026-07-18 14:33 +02:00
- **End time:** 2026-07-18 14:53 +02:00
- **Branch:** `codex/directed-causal-pair-00-phase05`
- **Starting Git state:** `898b4595dec15e7d5277058d41697a618405bb99`; clean when this subtask began
- **Ending Git state:** HEAD remains `898b4595dec15e7d5277058d41697a618405bb99`; shared worktree is dirty from this subtask and concurrent Phase-0.5 integration work
- **Runtime lock:** not acquired; this was a direct human-requested, engine-free code/schema/test audit and launched no experiment or world execution

## Assigned scope

Audit and complete the engine-free Phase-0.5 raw reproducer and final raw schema, add the missing reproducer test suite, and verify synthetic pass/failure behavior, tamper rejection, outcome firewalling, standard-library isolation, and deterministic reproduction. Do not commit, push, edit project indexes, execute DEV worlds, inspect pair-feeding outcomes, or touch prospective/V5/03G/58xxx material.

## Required context read

Read the repository operating contract and durable state in the required order:

1. `AGENTS.md`
2. `docs/RESEARCH_CHARTER.md`
3. `docs/PROJECT_STATE.md`
4. `docs/DECISION_LOG.md`
5. `docs/EXPERIMENT_INDEX.md`
6. `docs/RUN_INDEX.md`
7. latest journal then present: `docs/agent_journals/2026-07-18/0345_mechanics-tests_RUN-20260718-0345-DCP05-TEST.md`
8. `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`
9. `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`

Also read the preregistration draft, prior firewall/schema journal, the complete reproducer, the complete final schema, and relevant executor/mechanics/runner sections needed for parity.

## Files changed by this subtask

- `experiments/individuation/directed_causal_pair_phase05_reproduce.py`
- `experiments/individuation/test_directed_causal_pair_phase05_reproduce.py` (new)
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json`
- this journal

Other dirty files and journals visible at the end belong to concurrent Phase-0.5 agents and were not edited by this subtask.

## Actions and decisions

1. Preserved the inherited reproducer and audited it against the writer/executor/raw schema rather than recreating it.
2. Corrected deep-joint material-retention validation to apply `WORLD_ASSIGNMENTS` before indexing tracker retention. This matters in worlds where B is tracker 2 rather than tracker 1.
3. Bound the shard plan to the frozen canonical SHA-256 and required the exact 58-entry input/code binding identity set, not merely shape-valid arbitrary bindings.
4. Made `deep_material_gate` reproduce the executor rule: all assigned-track retentions pass and there are no derived mechanical kill reasons.
5. Preserved rho-weighted detector centroids as raw physical primitives because the final raw schema does not carry per-site rho weights. Required selected track centroid to equal its selected component centroid, then recomputed pair distance, core/halo/collar geometry, and association terms from the persisted centroids and masks.
6. Extended component-switch reproduction from A/B-only alternatives to every active prior tracker, including the sentinel.
7. Added a standard-library synthetic suite covering all four arms, turnover, all eight access regimes, deep-joint/sham/isolation evidence, and 3,560 step records.
8. Added a legitimate incomplete shard fixture whose four arms stop with `WRITER_SCHEDULE_INCOMPLETE`; the reproducer returns `INCOMPLETE_OR_FAILED` without inventing zero-valued evidence.
9. Added tamper tests for plan, bindings, geometry, assignment order, predecessor chain, duplicate/noncanonical JSON, recursive/case/depth outcome firewalling, and deterministic gzip bytes.
10. Added an isolated CLI test that copies only the reproducer and artifact into a temporary directory and runs `python -I -B` twice with the repository absent from `PYTHONPATH`.

## Reproducible validation

Pre-edit read-only checks:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -m py_compile experiments/individuation/directed_causal_pair_phase05_reproduce.py
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -c "import json, pathlib; json.loads(pathlib.Path('docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json').read_text(encoding='utf-8'))"
git diff --check
```

Focused final suite:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -m pytest -q experiments/individuation/test_directed_causal_pair_phase05_reproduce.py
```

Result: `19 passed in 38.14s`. The integrating agent independently repeated it: `19 passed in 38.22s`.

Combined mechanics plus reproducer suite:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -m pytest -q experiments/individuation/test_directed_causal_pair_phase05_mechanics.py experiments/individuation/test_directed_causal_pair_phase05_reproduce.py
```

Result: `63 passed in 42.02s`.

Final static checks before handoff:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -m py_compile experiments/individuation/directed_causal_pair_phase05_reproduce.py experiments/individuation/test_directed_causal_pair_phase05_reproduce.py
git diff --check -- docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json experiments/individuation/directed_causal_pair_phase05_reproduce.py experiments/individuation/test_directed_causal_pair_phase05_reproduce.py
```

Result: pass.

## OBSERVED

- The inherited reproducer was coherent and substantial, but its deep-joint retention check assumed joint order equaled tracker order.
- The writer records rho-weighted physical centroids but the raw schema does not include the rho field needed to recompute those centroids from masks alone.
- The executor's component-switch and material-gate rules were broader than the inherited reproducer's checks.
- The original schema allowed arbitrary contract-binding cardinality and the reproducer did not bind the plan to its frozen hash.
- No simulation engine, DEV world, prospective namespace/seed, 58xxx path, or pair-feeding Y/C/I outcome was invoked or inspected in this subtask.

## INFERRED

- Treating persisted component/track centroids as raw primitives is the only engine-free way to retain parity with rho-weighted detector geometry under the current final raw schema. Cross-field equality and mask-derived topology still constrain tampering.
- Exact binding identities and plan hashing are necessary to make an otherwise valid-looking shard fail closed when reproduced against a different code/input contract.
- Sentinel-inclusive alternatives are necessary to reproduce the executor's no-swap qualification mechanically.

## HYPOTHESIS

For any schema-valid Phase-0.5 raw shard emitted by the current executor contract, the patched standard-library reproducer will return the same mechanical arm/gate disposition without importing simulation code or computing pair-feeding outcomes.

## WHAT WOULD FALSIFY THIS?

- A writer-produced shard that passes executor validation but is rejected by the isolated reproducer without artifact corruption or contract drift.
- A shard whose executor mechanical disposition differs from the reproducer disposition after recomputing all association, halo, sham, fusion, separation, viability, and deep-joint terms.
- A valid active-track alternative, including sentinel, that changes the executor's switch decision but is not considered by the reproducer.
- Any successful extraction or influence of forbidden Y/C/I outcome material through a nested or case-obfuscated raw payload.

## Failures and dead ends

- The first synthetic-pass assertion expected 3,564 records. Manual recount showed the correct total is 3,560: four times 241 writer records, one turnover record, and eight times 81 access records. The assertion was corrected; no production logic changed for this test mistake.
- Binary-mask centroids could not reproduce rho-weighted centroids exactly. Instead of weakening geometry checks or importing the engine, the reproducer now validates persisted physical centroids as internally consistent raw primitives.

## Unresolved risks

- These tests are exhaustive synthetic contract tests, not a run against a real DEV raw shard; the parent integration run still owns actual mechanical execution and package disposition.
- Exact binding parity is frozen to the current runner constants. Any later intentional binding-set change must update the reproducer, schema, and parity test coherently.
- This subtask did not make the final `GO_FOR_HUMAN_SEAL_REVIEW`, `REVISE`, or `STOP_PAIR_MECHANICS` disposition; that depends on the integrated mechanical run and belongs to the parent agent.

## Handoff

Integrate the three implementation/schema/test files above with the concurrent executor/mechanics/runner work, rerun the combined suites after resolving all shared-worktree edits, then execute only the authorized already-open 500xx DEV mechanical plan. No commit or push was made by this subagent.
