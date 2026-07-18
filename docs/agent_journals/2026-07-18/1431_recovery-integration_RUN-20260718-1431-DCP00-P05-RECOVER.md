# Recovery integration journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5

- **Role:** primary recovery integrator
- **Run ID:** `RUN-20260718-1431-DCP00-P05-RECOVER`
- **Start time:** 2026-07-18 14:31:01 +02:00
- **End time:** 2026-07-18 16:04 +02:00
- **Starting branch:** `codex/directed-causal-pair-00-phase05`
- **Starting Git state:** `898b4595dec15e7d5277058d41697a618405bb99` (clean after recovery checkpoint)
- **Ending Git state:** clean Phase-0.5 deliverable commit
  `64b690edeab77b5bb91545e7cb4413cd08516593` pushed to `origin/codex/directed-causal-pair-00-phase05`; the subsequent
  journal-only closeout commit is the final branch tip reported in the terminal handoff

## Assigned scope

Recover the vanished Phase-0.5 session without discarding inherited work; mechanically qualify the already-open DEV worlds `50002`, `50004`, `50005`, and `50007`; preserve the outcome firewall; reproduce the mechanical raw artefacts without importing the engine; and either prepare an unsealed, seedless human-seal review package or stop/revise on the predeclared gates.

## Recovery and preservation

The inherited worktree was inspected before edits. It was on the expected branch at accepted Phase-0 commit `4bcb551092291b7383c4168f653818d4bade14f6`, with eleven untracked Phase-0.5 files and no tracked or staged changes. Read-only AST, JSON, whitespace, no-index diff, and focused synthetic checks passed. The exact inherited inventory was preserved in checkpoint commit `898b4595dec15e7d5277058d41697a618405bb99` before continuation.

## Actions

- Read the repository operating contract and all mandated state, decision, experiment, run, journal, manifest, summary, Phase-0 report, preregistration draft, feasibility, and raw-schema sources.
- Inspected branch, HEAD, status, diffs, hashes, and recent commits without reset, clean, stash, restore, checkout-over, or discard operations.
- Ran read-only syntax/diff checks and the inherited 36-test synthetic suite before checkpointing.
- Created three bounded audit tracks for executor/mechanics, preflight/package, and engine-free reproduction; each
  audit left its own journal.
- Created two independent post-run audit tracks and one isolated engine-free reproduction track; all left unique
  journals and independently converged on `STOP_PAIR_MECHANICS`.
- Executed only the fixed already-open DEV worlds `50002`, `50004`, `50005`, and `50007`, in that order, from an
  exact clean code binding. No prospective namespace or seed was opened.

## Pre-execution integration addendum — 2026-07-18 15:24 CEST

The first integrated review found and repaired outcome-bearing detector use, omitted seed component masks,
rho-centroid inconsistencies, non-role-matched H00 references, missing sentinel switch coverage, absent initial
collar gates, resetting tracker lifecycle time, dead isolation perturbations, incomplete code bindings, and six
engine-free reproduction parity gaps. A subsequent independent red-team blocked execution on five additional
fail-closed defects: prior-edge weighted-centroid mismatch, unweighted isolation supports, absent eight-way access
seed parity, importable unbound module shadows, and noncanonical centroid aliases. Follow-up review then found and
closed schedule-zero isolation-failure schema parity, package-form module shadows, and deep-joint centroid range
parity.

No DEV world was advanced while any blocker remained. The independent final verdict is
`GO_FOR_BOUND_DEV_MECHANICAL_EXECUTION` after the exact code commit and manifest binding; it is explicitly not yet
human-seal approval.

Final pre-code-checkpoint validation at this stage:

```powershell
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py `
  experiments/individuation/test_directed_causal_pair_phase0.py `
  experiments/individuation/test_access_structure_operators.py `
  experiments/individuation/test_access_structure_noswap_operators.py `
  experiments/individuation/test_turnover_tracer.py
# 100 passed in 99.42s

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
  experiments/individuation/test_bijective_tracker.py
# 10/10 checks PASS

# Read-only AST parsing of all six Phase-0.5 Python implementation/test files: PASS
# Final raw JSON parse and standard-library schema-contract load: PASS
# Runner/reproducer exact bindings: 7 input paths and 51 code paths, equal
# git diff --check: PASS
```

Corrected test-command dead ends were preserved rather than hidden: an initial command named nonexistent
`test_material_tracer.py`/`test_turnover_diag_engine.py`; the correct regression is `test_turnover_tracer.py`.
`test_bijective_tracker.py` is a standalone script that raises `SystemExit` during pytest collection, so it was
correctly rerun directly. The optional third-party `jsonschema` package is absent; the committed standard-library
schema validator and raw reproducer tests passed instead.

The first exact manifest bound to code checkpoint `944eb9c75d905c686a31384825fe515de3269e57` failed before
engine import because the namespace guard interpreted a coincidental `58xxx` digit run inside an opaque
cryptographic binding as a seed namespace. Its exact 10,790 bytes are preserved at
`DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST_REJECTED_944eb9c.json` with SHA-256
`2b3c26638a4d9eca30d9482c115842114c48d841cbfca019dabb1969aaeea967`. The narrow repair excludes only complete
40- or 64-character lowercase hexadecimal identities from namespace parsing; semantic paths/strings and integer
IDs remain fail-closed. A fresh code commit and canonical manifest binding are required before execution.

The next manifest, bound to `66a7283dac932525d14f86054647c562adf9649a`, passed the complete preflight with
SHA-256 `3f8ee7dc5e5186298d02cef5998814701566c1459960c33a808dcced46bfe0d4` but the file-style runner invocation then
failed at the first executor import with `ModuleNotFoundError: No module named 'experiments'`. No engine module or
world was initialized and the raw directory remained absent. The exact rejected manifest is preserved as
`DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST_REJECTED_66a7283_IMPORT_PATH.json`. The narrow repair adds the
already-verified repository root to `sys.path` only inside the isolated executor-import context and restores the
previous path afterward; another code commit and manifest rebind are required.

## Post-execution closeout addendum — 2026-07-18 16:00 CEST

The canonical manifest bound exact code commit `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`, passed preflight with
SHA-256 `ed29675de3b90ca7570bf09a2b9f75fe2ccf070f23f09728408b8aeb2eb5367f`, and wrote only the fixed raw directory.
The runner attempted the four worlds exactly once in the frozen order and atomically published `COMPLETE.json` last.

All four worlds failed frozen mechanics before the common deep step:

- 50002: writer step 61, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`;
- 50004: writer step 58, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`;
- 50005: writer step 110, `PAIR_GEOMETRY_UNAVAILABLE`, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`,
  `TARGET_OR_SENTINEL_NOT_ALIVE`, and `TRACKER_SPLIT_T1`;
- 50007: writer step 40, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`.

The observed prefixes retain distance above 24 and zero radius-12 halo overlap, but target/tracker viability is
conjunctive. Each world has all four history-arm records and zero access regimes; no arm reached a common H00 deep
step. The index is a complete 4/4 execution prefix while `COMPLETE.json` correctly declares
`all_worlds_mechanically_complete=false`.

The engine-free reproducer was run twice under isolated Python against exactly the four shards and final schema.
Both runs exited zero and wrote byte-identical 4,524-byte results with SHA-256
`8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`. Both derive
`ordered_prefix_complete=true`, `mechanical_firewall_pass=true`, `all_worlds_mechanically_complete=false`, and
`reproduction_status=INCOMPLETE_OR_FAILED`. Independent post-run audits verified compressed and canonical hashes,
predecessor chain, schema, assignments, earliest failures, and absence of engine imports during reproduction.

Final disposition: **STOP_PAIR_MECHANICS — 0/4 MECHANICALLY COMPLETE — NO PROSPECTIVE AUTHORIZATION**. This is a
mechanical feasibility failure and leaves the scientific question unanswered. No unsealed seal-review package was
created because mechanical qualification is a prerequisite.

## Important files read or changed

- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION_REPEAT.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPORT.md`
- `experiments/individuation/directed_causal_pair_phase05_{runner,executor,mechanics,reproduce}.py`
- `experiments/individuation/test_directed_causal_pair_phase05_mechanics.py`

## Reproducible commands and experiments

The recovery checkpoint is independently reproducible as Git commit
`898b4595dec15e7d5277058d41697a618405bb99`. Implementation checkpoints are
`944eb9c75d905c686a31384825fe515de3269e57`, `66a7283dac932525d14f86054647c562adf9649a`, and exact executed code
`3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
  experiments/individuation/directed_causal_pair_phase05_runner.py `
  --manifest docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json
# Four fixed worlds attempted; COMPLETE record published last.

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py `
  experiments/individuation/test_directed_causal_pair_phase05_reproduce.py `
  experiments/individuation/test_directed_causal_pair_phase0.py `
  experiments/individuation/test_access_structure_operators.py `
  experiments/individuation/test_access_structure_noswap_operators.py `
  experiments/individuation/test_turnover_tracer.py
# 102 passed in 103.03s

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
  experiments/individuation/test_bijective_tracker.py
# 10/10 checks PASS
```

The exact isolated reproducer commands and their zero exits are recorded in
`1543_raw-reproduction_RUN-20260718-1543-DCP05-RAW-REPRO.md`. Final `git diff --check`, Python AST parsing, JSON
loads, manifest/raw hash reconciliation, byte comparison, and forbidden namespace/path audit passed.

## OBSERVED

- The inherited implementation was coherent but incomplete: its runner referenced a missing reproducer test and no fixed DEV manifest existed.
- The inherited executor called the scaffold detector, which computes specific uptake, despite the Phase-0.5 prohibition on computing or inspecting pair-feeding outcomes.
- H00 no-swap reference selection was not role-matched, component-switch coverage omitted sentinel transitions, and the engine-free reproducer used joint-row order where assignment order was persisted.
- The preflight did not bind the complete local import closure or require an exact clean code checkout.
- The exact four-world raw prefix is complete and cryptographically consistent, but 0/4 worlds pass the mechanical
  viability/tracker union.
- All H00 reference arms fail before a common deep step; no access regime or pair feeding endpoint is reached.
- Two isolated engine-free reproductions are byte-identical and independently derive the same failure disposition.

## INFERRED

The pre-execution defects were narrow implementation issues that were repaired without advancing a world. The final
DEV failures are different: exact raw and independent reproduction show that the fixed natural targets do not
satisfy the frozen writer-stage viability/tracker gates. This does not establish a scientific null; it closes only
the current mechanical path.

## HYPOTHESIS

After narrow repairs, all four already-open DEV worlds can be executed outcome-blindly and their mechanical
qualification can be reproduced from raw shards with a standard-library-only program. The execution and
reproduction parts passed; the hypothesis that they would mechanically qualify was falsified in all four worlds.

## WHAT WOULD FALSIFY THIS?

The frozen minimum-size gate fired in every world and a tracker split fired in 50005. Those observations satisfy the
predeclared falsifier even though the raw prefix, firewall, geometry-before-failure, and deterministic reproduction
all pass.

## Failures and dead ends

- Rejected manifest `944eb9c`: conservative namespace false positive inside an opaque hash; stopped before engine
  import and preserved exactly.
- Rejected manifest `66a7283`: file-style package import path failure; stopped before engine module import/world
  initialization and preserved exactly.
- Final DEV execution: 0/4 mechanically complete under frozen gates. This is not repaired or retuned.
- Earlier incorrect test filenames and pytest collection of the standalone tracker are preserved in the
  pre-execution addendum; corrected commands passed.

## Decisions

- Preserve the inherited implementation in a standalone checkpoint and continue it rather than recreate it.
- Fail closed: no prospective identifiers, seeds, or scientific Y/C/I computation will be introduced during Phase 0.5.
- Accept `STOP_PAIR_MECHANICS`, not `REVISE` or `GO_FOR_HUMAN_SEAL_REVIEW`, because independent raw validation shows
  a frozen mechanical failure rather than a packaging/reproducer defect.
- Do not create the conditional unsealed human-seal package; mechanical qualification was not achieved.
- Do not lower the minimum-size threshold, replace the pair/world, or reinterpret the complete execution prefix as a
  mechanical pass.

## Unresolved risks

- Human review may challenge the stop record, but no further execution is authorized by this run.
- Any changed gate, target definition, writer interval, pair, or DEV plan is a new design requiring separate explicit
  authorization.
- Remote push of deliverable commit `64b690edeab77b5bb91545e7cb4413cd08516593` was verified by equal local and
  remote-tracking refs. Only this journal-closeout metadata change follows it and must be pushed before handoff.

## Handoff

**STOP_PAIR_MECHANICS.** Exact next authorized action: human review of
`docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPORT.md` only. No prospective execution, human seal, threshold
change, pair substitution, or continuation of this frozen Phase 0.5 plan is authorized.
