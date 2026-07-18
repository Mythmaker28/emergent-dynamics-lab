# Post-run engine-free raw reproduction — RUN-20260718-1543-DCP05-RAW-REPRO

- **Role:** post-run raw reproducer subagent
- **Run ID:** `RUN-20260718-1543-DCP05-RAW-REPRO`
- **Start time:** 2026-07-18 15:43:56 +02:00
- **End time:** 2026-07-18 15:50:05 +02:00
- **Branch:** `codex/directed-causal-pair-00-phase05`
- **Starting Git state:** `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`; only the completed DEV manifest and raw directory were untracked
- **Ending Git state:** HEAD remains `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`; the manifest/raw directory plus two requested reproduction outputs and this journal are untracked
- **Runtime lock:** not acquired; this direct human-requested post-run task did not launch or advance an experiment and used only the engine-free reproducer on already-persisted shards

## Assigned scope

Run the standard-library Phase-0.5 reproducer twice against exactly the four persisted raw mechanical shards and the final raw schema; preserve both outputs even on mechanical failure; compare exact bytes and SHA-256; report only the mechanical classification. Do not import or run the engine, inspect or compute pair-feeding Y/C/I outcomes, or edit shared indexes/report.

## Context and inventory

The complete repository operating contract and required durable-state sequence had already been read during the immediately preceding reproducer audit in this same agent session. Before this post-run action, the current branch/HEAD/status and recent commits were rechecked, and the latest integration journal, fixed DEV manifest, raw `INDEX.json`, and raw `COMPLETE.json` were read.

The raw directory contained exactly four canonical shard payloads in frozen order:

1. `000_50002.json.gz`
2. `001_50004.json.gz`
3. `002_50005.json.gz`
4. `003_50007.json.gz`

`INDEX.json` and `COMPLETE.json` are control metadata and were not passed as shards.

## Files created

- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION_REPEAT.json`
- this journal

No implementation, schema, shard, manifest, shared index, report, or existing journal was modified.

## Reproducible commands

Both invocations used the same explicitly ordered four `--shard` arguments:

```powershell
$python = 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
$script = 'experiments/individuation/directed_causal_pair_phase05_reproduce.py'
$schema = 'docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json'

& $python -I -B $script --schema $schema `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/000_50002.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/001_50004.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/002_50005.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/003_50007.json.gz `
  --output docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION.json

& $python -I -B $script --schema $schema `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/000_50002.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/001_50004.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/002_50005.json.gz `
  --shard docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/003_50007.json.gz `
  --output docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION_REPEAT.json
```

Both commands exited `0`.

## Exact output comparison

- First output size: 4,524 bytes
- Repeat output size: 4,524 bytes
- First SHA-256: `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`
- Repeat SHA-256: `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`
- Byte identity: `True`

## Mechanical classification

`INCOMPLETE_OR_FAILED`

Supporting mechanical status only:

- `all_worlds_mechanically_complete = false`
- `mechanical_firewall_pass = true`

## OBSERVED

- Both independent engine-free invocations accepted the same four ordered raw shards and completed normally.
- Both emitted exactly the same canonical 4,524-byte reproduction artefact.
- The reproduced mechanical classification is `INCOMPLETE_OR_FAILED`.
- The reproducer's mechanical firewall passed.
- No engine module was imported or executed, and no pair-feeding Y/C/I outcome was inspected or computed.

## INFERRED

The mechanical classification is deterministic for the exact persisted shards and bound final schema. Because all-world mechanical completion is false, this raw package does not mechanically qualify as a completed Phase-0.5 pass.

## HYPOTHESIS

Any further run of the same committed standard-library reproducer against these exact four bytes-identical shards and schema will emit the same canonical reproduction bytes and `INCOMPLETE_OR_FAILED` classification.

## WHAT WOULD FALSIFY THIS?

- A repeated isolated invocation on the same exact inputs yields a different output hash or classification.
- A later integrity check finds that either output is not exactly 4,524 bytes with SHA-256 `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`.
- The reproducer can be shown to import an engine or derive a forbidden pair-feeding outcome while producing this result.

## Failures and dead ends

None. Both requested invocations completed with exit code `0`; the fail-closed classification is a scientific/mechanical result, not an execution failure.

## Decisions

- Passed only the four canonical shard payloads; excluded raw control metadata from `--shard` arguments.
- Used `-I -B` for both invocations to preserve isolated, bytecode-free execution.
- Preserved both outputs exactly, despite the non-qualifying mechanical classification.

## Unresolved risks

- Final repository disposition (`REVISE` or `STOP_PAIR_MECHANICS`) belongs to the primary integrator under the preregistered gates.
- This subtask intentionally did not inspect scientific pair-feeding outcomes or attempt any prospective package/namespace action.

## Handoff

The two requested reproduction artefacts are ready for integration and have identical SHA-256 `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`. Exact mechanical classification: `INCOMPLETE_OR_FAILED`. No commit or push was made by this subagent.
