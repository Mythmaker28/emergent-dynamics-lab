# DIRECTED-CAUSAL-PAIR-00 Phase 0.5 final pre-execution red-team

- Role: read-only final preflight red-team subagent
- Run ID: `RUN-20260718-1450-DCP05-FINAL-REDTEAM`
- Start time: 2026-07-18 14:50:00 +02:00 (reconstructed approximate start; the journal was added after the review at the parent agent's request)
- End time: 2026-07-18 15:25:06 +02:00
- Branch: `codex/directed-causal-pair-00-phase05`
- Starting Git HEAD: `898b4595dec15e7d5277058d41697a618405bb99`
- Ending Git HEAD: `898b4595dec15e7d5277058d41697a618405bb99`
- Starting Git state: dirty recovered Phase-0.5 worktree with modified schema/executor/mechanics/reproducer/runner/mechanics-test files and untracked Phase-0.5 journals plus the reproducer test file.
- Ending Git state: same inherited Phase-0.5 changes, plus only this subagent journal. This subagent did not modify implementation or scientific artefacts.

## Assigned scope

Read-only re-audit of five pre-execution blockers after patches:

1. production logger to engine-free reproducer parity for rho-weighted prior centroids;
2. exact-isolation rho-weighted collar/core identity and schedule-zero seed gating;
3. exact eight-way standardized access-seed parity;
4. ABI-extension and package-form import-shadow rejection plus isolated bytecode cache;
5. canonical centroid range enforcement in both final schema and reproducer.

The scope expressly prohibited DEV-world execution, prospective identifiers or seeds, V5/03G work, and 58xxx activity.

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- latest relevant Phase-0.5 journals
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json`
- `experiments/individuation/directed_causal_pair_phase05_{mechanics,executor,reproduce,runner}.py`
- `experiments/individuation/test_directed_causal_pair_phase05_{mechanics,reproduce}.py`

## Files changed

- This journal only.

No implementation, raw data, manifest, index, decision log, project-state file, experiment-state file, or prospective package was changed by this subagent.

## Actions and reproducible checks

The initial review identified and reported five contract defects. Other agents patched them; this subagent then reloaded the changed sections and tested the production-path contracts. Two secondary omissions were also reported and patched during the re-audit: schedule-zero isolation failures originally remained schema/reproducer-incompatible, and package-form module shadows were not initially enumerated. A final deep-joint centroid range parity omission was reported and patched before approval.

Focused final test command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -m pytest -q -p no:cacheprovider `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py::test_production_observer_round_trips_weighted_prior_edge_centroids `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py::test_exact_isolation_uses_the_rho_weighted_collar_core `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py::test_exact_code_checkout_refuses_abi_extension_shadow `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py::test_exact_code_checkout_refuses_package_form_module_shadow `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py::test_executor_import_uses_fresh_external_bytecode_cache `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py::test_access_regimes_require_one_exact_standardized_clone_seed `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py::test_centroid_primitive_requires_canonical_grid_range `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py::test_deep_joint_centroid_uses_the_canonical_grid_range `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py::test_final_schema_is_closed_and_freezes_exact_binding_cardinality `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py::test_exact_isolation_accepts_fail_closed_schedule_zero_seed_gate
```

Result: `12 passed in 13.00s` (the parameterized centroid-range test accounts for three cases).

Final syntax and whitespace checks:

```powershell
git diff --check

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -B -c "from pathlib import Path; ps=['experiments/individuation/directed_causal_pair_phase05_mechanics.py','experiments/individuation/directed_causal_pair_phase05_executor.py','experiments/individuation/directed_causal_pair_phase05_reproduce.py','experiments/individuation/directed_causal_pair_phase05_runner.py','experiments/individuation/test_directed_causal_pair_phase05_mechanics.py','experiments/individuation/test_directed_causal_pair_phase05_reproduce.py']; [compile(Path(p).read_bytes(),p,'exec') for p in ps]; print('syntax_ok=6')"
```

Results: `git diff --check` produced no output; the read-only compile reported `syntax_ok=6`.

No DEV or prospective experiment was run. All tests were static or synthetic.

## OBSERVED

- `PassivePairObserver` persists the preceding physical rho-weighted track centroid and the reproducer carries the same primitive into association-edge validation.
- Exact isolation reconstructs the recipient core from the same rho-weighted center as the fixed collar and rejects a collar/core mismatch.
- Left and right exact-isolation seed snapshots are gated at schedule step zero; schema and reproducer both accept failure steps only in the closed range 0 through 80.
- All eight access regimes must expose one identical standardized seed signature, including state hash, engine step, assignment, components, tracks, pair geometry, and physical masks.
- Runner preflight rejects ABI sibling extensions and same-stem package-form shadows across source, bytecode, and extension suffixes. Executor import and execution occur with a fresh external bytecode-cache prefix.
- Final schema and reproducer enforce `0 <= coordinate < 64` for component, track, pair-geometry, and deep-joint phenotype centroids.
- The final focused regressions, syntax compilation, and diff whitespace check all passed.

## INFERRED

The five previously reported discrepancies no longer permit the production logger, isolation mechanics, access cloning, import loader, or centroid contract to diverge along the audited paths. The implementation is mechanically coherent enough to proceed to the fixed, manifest-bound DEV execution step once it is committed and rebound to the exact clean HEAD.

This inference is limited to pre-execution mechanics and raw-contract integrity. It is not a scientific result and does not inspect or infer pair-feeding outcomes.

## HYPOTHESIS

With a coherent commit, canonical manifest bound to that exact commit, clean checkout, and the fixed 500xx DEV plan, the runner will either fail closed before engine import or emit raw shards that the engine-free reproducer can validate under the frozen Phase-0.5 mechanical contract.

## WHAT WOULD FALSIFY THIS?

- A production observer record rejected by the reproducer because its association-edge centroid distance differs from the persisted preceding physical centroid.
- An exact-isolation record whose certified core is not enclosed by the logged fixed collar, or whose schedule-zero gate cannot be represented and reproduced.
- Two access regimes with different standardized seed states that nevertheless pass reproduction.
- An ignored ABI extension, package-form shadow, or repository bytecode cache being imported in place of a bound source after successful preflight.
- Any accepted raw centroid outside `[0, 64)` or any final-schema-valid centroid rejected by the reproducer solely because of range handling.
- Failure of the exact manifest/HEAD/binding preflight after coherent packaging for a reason not represented in the current tests.

## Failures and dead ends

- The first patched isolation version emitted `schedule_step: 0` failures while schema and reproducer still required a minimum of 1. This was reported; both were corrected to 0 through 80 and regression-tested.
- The first import-shadow expansion rejected direct ABI siblings but missed same-stem package directories such as `executor/__init__.py`. This was reported; package-form candidates were added and regression-tested.
- The first centroid-range repair left deep-joint phenotype descriptors on a finite-only reproducer path. This was reported; the path now uses `_read_centroid` and a direct 64.0 tamper regression passes.
- A local `.venv` path did not exist in this worktree; checks used the repository project's established environment at `C:\Users\tommy\Documents\ising v3\.venv`. No scientific execution was attempted.

## Decisions

- Final pre-execution disposition: `GO_FOR_BOUND_DEV_MECHANICAL_EXECUTION`.
- This is not `GO_FOR_HUMAN_SEAL_REVIEW`; human seal review remains conditional on mechanically qualified reproduced DEV results and the later unsealed prospective-package handoff.
- No decision-log entry is warranted from this read-only audit alone.

## Unresolved risks

- The implementation changes are not executable under their own preflight until they are committed coherently and the manifest is regenerated or rebound to the exact resulting clean `HEAD`; this is an expected packaging gate, not a remaining code defect.
- Runtime DEV behavior and qualification outcome remain unobserved because this subagent did not run any DEV world.
- Human review must still confirm result-level qualification, raw artefact hashes, reproduction output, and any unsealed prospective package before seal authorization.

## Handoff

Commit the coherent repaired implementation and journals, bind the canonical Phase-0.5 DEV manifest to that exact commit and exact code-file hashes, verify the checkout is clean, then run only the fixed 500xx DEV mechanical plan through the fail-before-engine runner. Reproduce the emitted raw shards engine-free before assigning the required terminal scientific disposition.

Final audit verdict: **GO_FOR_BOUND_DEV_MECHANICAL_EXECUTION**.
