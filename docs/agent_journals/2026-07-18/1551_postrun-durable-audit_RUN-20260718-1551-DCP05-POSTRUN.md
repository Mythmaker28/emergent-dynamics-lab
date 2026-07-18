# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5 post-run durable-state audit

- Role: outcome-blind post-run durable-state auditor
- Run ID: `RUN-20260718-1551-DCP05-POSTRUN`
- Start time: 2026-07-18 15:37 +02:00
- End time: 2026-07-18 15:55 +02:00
- Starting branch: `codex/directed-causal-pair-00-phase05`
- Starting HEAD: `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- Starting Git state: tracked tree clean; canonical Phase-0.5 DEV manifest and raw directory untracked
- Ending branch: `codex/directed-causal-pair-00-phase05`
- Ending HEAD: `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- Ending Git state: this journal, manifest/raw, report, and concurrently created reproduction artefacts/journal are untracked; the parent concurrently modified the four shared durable-state documents; this audit itself modified no shared tracked file

## Assigned scope

Perform a read-only, outcome-blind durability audit of the completed Phase-0.5 mechanical raw prefix. Inspect only mechanical completion/failure metadata and the durable project indexes, recommend the exact terminal disposition and precise index/state updates, and create this unique journal. Do not inspect or compute pair-feeding `Y`, `C`, or `I`; do not edit shared indexes or the report; do not create a prospective package unless the fixed mechanics qualify.

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-18/1431_recovery-integration_RUN-20260718-1431-DCP00-P05-RECOVER.md`
- `docs/agent_journals/2026-07-18/1433_executor-mechanics-audit_RUN-20260718-1433-DCP05-EXEC-AUD.md`
- `docs/agent_journals/2026-07-18/1431_preflight-package_RUN-20260718-1431-DCP05-PREFLIGHT.md`
- `docs/agent_journals/2026-07-18/1433_raw-reproducer_RUN-20260718-1433-DCP05-REPRO.md`
- `docs/agent_journals/2026-07-18/1450_final-preflight-redteam_RUN-20260718-1450-DCP05-FINAL-REDTEAM.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/INDEX.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/COMPLETE.json`
- the four compressed raw shards, decompressed only far enough to read mechanical arm completion and first-failure metadata

## Actions and reproducible commands

1. Read the repository operating contract and durable state in the mandated order.
2. Checked branch, HEAD, status, raw names, sizes, and SHA-256 provenance.
3. Read only mechanical manifest/index/completion metadata.
4. Ran the standard-library engine-free raw reproducer in memory, without writing output and without loading pair-feeding outcomes.
5. Decompressed each shard only to enumerate `world_id`, arm completion, deep-mechanics completion, access-regime count, and first mechanical failure.
6. Did not inspect, derive, aggregate, print, or interpret `Y`, `C`, or `I`.

Representative commands:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
Get-ChildItem docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW | Select-Object Name,Length
Get-FileHash -Algorithm SHA256 docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json
Get-FileHash -Algorithm SHA256 docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/INDEX.json
Get-FileHash -Algorithm SHA256 docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/COMPLETE.json
```

The engine-free reproducer returned:

```text
reproduction_status=INCOMPLETE_OR_FAILED
ordered_prefix_complete=true
all_worlds_mechanically_complete=false
mechanical_firewall_pass=true
```

## Provenance

- Branch code commit bound by the manifest: `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- Accepted Phase-0 commit: `4bcb551092291b7383c4168f653818d4bade14f6`
- Manifest SHA-256: `ed29675de3b90ca7570bf09a2b9f75fe2ccf070f23f09728408b8aeb2eb5367f`
- Plan SHA-256: `0c3c75fe8142373dcf6d1aa765dd4247c11570b993e4ea5d1cf4379f958826c3`
- Index SHA-256: `06629af2ca9a6092047134ffe18fb1107888d1cd15d1fb28f86c49a8ea3108d1`
- Completion-marker SHA-256: `47d628acc102f6649200011e1620e0121ef43ff47015f263909a8ebbe89def05`
- Exact fixed already-open DEV prefix: `50002, 50004, 50005, 50007`
- Raw shards:
  - `000_50002.json.gz`: `0af4715a4fae6e65b601e332afb835d4b8721db9514dc55ea4cc37749a7f690b`
  - `001_50004.json.gz`: `e40e726ddb30ad5eae1d6db7aca1ef54f410efb6b7d17ef87059bcc2b16f1979`
  - `002_50005.json.gz`: `024c65434f1cb4806488569358516fedfaa8956d2c58c0ff2200ab71cc980da3`
  - `003_50007.json.gz`: `81a0c79ed2f9d1f717ed6c709eaacc33699406ab617dc80d6492e94849286719`

## OBSERVED

The exact four-world prefix is present in canonical order. Both the persisted `INDEX.json`/`COMPLETE.json` and the independent engine-free reproduction agree that all four raw worlds were processed, the mechanical firewall passes, and `all_worlds_mechanically_complete` is false. Zero of four worlds completed the fixed mechanics, and no arm recorded an access regime.

The mechanically inert `H00` arm fails before the common deep/access phase in every world:

- world `50002`: writer step 61 / engine step 861, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`;
- world `50004`: writer step 58 / engine step 858, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`;
- world `50005`: writer step 110 / engine step 910, `PAIR_GEOMETRY_UNAVAILABLE`, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`, `TARGET_OR_SENTINEL_NOT_ALIVE`, and `TRACKER_SPLIT_T1`;
- world `50007`: writer step 40 / engine step 840, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`.

The other arms either fail at the same pre-deep writer viability gate or, for `50005` `H10`/`H11`, stop immediately because the `H00` common deep step is unavailable. No prospective namespace exists, no prospective seed was used, and no unsealed prospective package is mechanically authorized.

## INFERRED

The frozen Phase-0.5 pair operator is mechanically infeasible on its exact predeclared DEV prefix. Because even `H00` cannot preserve the selected target/sentinel pair through the writer phase, the run never reaches the history-bearing no-swap/access qualification needed to ask the directed-causal question. The correct terminal disposition is therefore:

`STOP_PAIR_MECHANICS — COMPLETE OUTCOME-BLIND DEV PREFIX — 0/4 WHOLE WORLDS MECHANICALLY COMPLETE — NO PROSPECTIVE PACKAGE OR AUTHORIZATION`

This is a mechanical stop and an unanswered scientific question. It is not evidence for absence of pair-level individuation, and it is not a scientific negative result about pair feeding.

## HYPOTHESIS

The selected target/sentinel pairs are not viable under the frozen writer schedule and minimum-size/tracker constraints long enough to enter the common deep/access phase. The recurrence across all four fixed worlds, including the inert `H00` arm, is consistent with an operator-level mechanical mismatch rather than a treatment-specific causal effect.

## WHAT WOULD FALSIFY THIS?

An engine-free reproduction of the same manifest, same code commit, same exact four shards, and same fixed rules showing an `H00` common deep step or any complete world would falsify this audit. A new pair selection, lower size threshold, altered writer schedule, changed horizon, changed tracker, or new DEV worlds would not falsify it; those would be a new protocol and require separate authorization.

## Failures and dead ends

- The engine-free reproduction took roughly 110 seconds but completed normally.
- No pair-feeding outcome analysis was attempted. The mechanical failure was sufficient for disposition.
- Concurrent work created reproduction artefacts and a reproduction journal after this audit began. They were observed in Git status but were not edited or interpreted here.

## Decisions and restrictions

- Recommend `STOP_PAIR_MECHANICS`, not `REVISE` and not `GO_FOR_HUMAN_SEAL_REVIEW`.
- Do not create a prospective package or seal-review request.
- Do not rescue the fixed run by lowering thresholds, changing pair choice, altering writer timing/horizon, or adding worlds.
- Do not inspect pair-feeding `Y`, `C`, or `I`.
- Preserve that no prospective namespace or seed exists.
- Preserve the prohibition on changes to V5, 03G, or any 58xxx namespace.

## Precise durable-state update recommendation

### `docs/PROJECT_STATE.md`

Add a top branch addendum stating that the exact outcome-blind DEV prefix `50002,50004,50005,50007` completed at code commit `3a86ebb...`, manifest SHA `ed296...`; ordering and firewall reproduced; 0/4 worlds mechanically completed; `H00` failed pre-deep in all four; zero access regimes were recorded; disposition `STOP_PAIR_MECHANICS`; the causal question remains unanswered; no prospective package, namespace, seed, or authorization exists. The exact next action is to preserve/index the manifest, raw shards, reproduction, report, journals, and push the completed branch. Any redesign must be a separately authorized DEV protocol.

### `docs/EXPERIMENT_INDEX.md`

Replace the current `DIRECTED-CAUSAL-PAIR-00` Phase-0 status with:

```text
PHASE05_COMPLETE_STOP_PAIR_MECHANICS_0_OF_4_NO_PROSPECTIVE
```

Record `0 prospective runs`; the exact four-world outcome-blind DEV mechanical prefix is complete, but `0/4` worlds are mechanically complete, `H00` fails before deep/access qualification in every world, and no access regimes exist. Index the Phase-0 report/preregistration, Phase-0.5 manifest, raw directory, engine-free reproduction, Phase-0.5 report, code/tests, and journals. Interpretation must say “fixed mechanics infeasible; scientific question unanswered,” not “no individuation.”

### `docs/DECISION_LOG.md`

Add the next decision entry (expected `D-092`) with title “DIRECTED-CAUSAL-PAIR-00 Phase 0.5 exact mechanics fail target/sentinel viability.” Decision: `STOP_PAIR_MECHANICS`. Include code/manifest/plan/index hashes, exact four-world prefix, the four `H00` failures above, 0/4 complete, zero access regimes, and the engine-free ordering/firewall reproduction. State explicitly that no `Y/C/I` were inspected, the finding is not a scientific null, no prospective package/seal is allowed, and post-failure rescue tuning is prohibited. The only current action is durable preservation and branch push; a redesign requires a new authorization.

### `docs/RUN_INDEX.md`

Index the primary integration run and each independently journaled audit/reproduction run. At minimum add:

```text
RUN-20260718-1431-DCP00-P05-RECOVER | 2026-07-18 | recovery integrator | recover/checkpoint, implement and execute exact DEV mechanics, reproduce, disposition | DIRECTED-CAUSAL-PAIR-00 | 898b459... | final branch tip | PHASE05_COMPLETE_STOP_PAIR_MECHANICS_0_OF_4_NO_PROSPECTIVE | docs/agent_journals/2026-07-18/1431_recovery-integration_RUN-20260718-1431-DCP00-P05-RECOVER.md
```

Also add rows for `RUN-20260718-1433-DCP05-EXEC-AUD`, `RUN-20260718-1431-DCP05-PREFLIGHT`, `RUN-20260718-1433-DCP05-REPRO`, `RUN-20260718-1450-DCP05-FINAL-REDTEAM`, the final raw-reproduction run, and `RUN-20260718-1551-DCP05-POSTRUN`, each pointing to its own journal and using its actual starting/ending Git state. This follows the repository rule that every working run is indexed.

## Unresolved risks

- The main integration journal was still marked in progress when read and needs a final addendum with the actual terminal branch tip, artefact hashes, disposition, tests, and push status.
- The final report labels `36c23aaf2832987198f7314702086cf2a36ed4f6414ba1b8336ec31cfb905551` as the “final raw-schema SHA-256.” This is the reproducer's SHA-256 of canonicalized schema JSON, while the byte SHA-256 of the tracked schema file is `1fa377afe7595b12800b205215d51fa621e3785629ea48e837eec29d18380edc` as bound in the manifest. The report should label the former explicitly as the canonicalized-schema hash or list both hashes.
- `docs/RUN_INDEX.md` currently adds only the primary integration run. The individually journaled preflight, executor-audit, reproducer, red-team, final raw-reproduction, and this post-run audit should also receive rows under the repository's per-run indexing rule.
- For maximum precision, use `PHASE05_COMPLETE_STOP_PAIR_MECHANICS_0_OF_4_NO_PROSPECTIVE` consistently in `EXPERIMENT_INDEX.md` and `RUN_INDEX.md`; the current shorter status is scientifically correct but omits the complete-prefix and 0/4 facts encoded elsewhere.
- The shared durable indexes must not overstate the result as a scientific negative.

## Post-integration read-only verification

The parent's concurrently integrated `PROJECT_STATE`, `EXPERIMENT_INDEX`, `DECISION_LOG`, `RUN_INDEX`, and Phase-0.5 report preserve the required `STOP_PAIR_MECHANICS` boundary and contain no pair-feeding interpretation. `git diff --check` is clean. The two reproduction files are exactly 4,524 bytes and byte-identical at SHA-256 `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`; both declare `reproduction_status=INCOMPLETE_OR_FAILED`. Apart from the provenance-label and per-run indexing corrections above, the integrated disposition is coherent.

## Handoff

Finalize the canonical outcome-blind report and engine-free reproduction, update the four durable state/index documents exactly within the boundaries above, run relevant tests and schema/reproduction checks, finalize the primary journal, commit the coherent terminal artefacts, push `codex/directed-causal-pair-00-phase05`, and report the exact commits and remote status. Do not create a prospective package.
