# DIRECTED-CAUSAL-PAIR-00 Phase 0.5 post-run independent red-team

- **Role:** independent post-run raw-mechanics and engine-free reproduction auditor
- **Run ID:** `RUN-20260718-1543-DCP05-POSTRUN-REDTEAM`
- **Start time:** 2026-07-18 15:43:00 +02:00 (approximate task receipt)
- **End time:** 2026-07-18 15:55:10 +02:00
- **Starting branch / HEAD:** `codex/directed-causal-pair-00-phase05` / `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- **Starting Git state:** tracked checkout clean; untracked canonical DEV manifest and `DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/` only.
- **Ending branch / HEAD:** `codex/directed-causal-pair-00-phase05` / `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- **Ending Git state:** shared worktree concurrently gained the primary agent's modified indexes/state and other agents' report/reproduction/journal artefacts; this subagent changed only this journal.

## Assigned scope

Audit only the post-run Phase-0.5 mechanical raw artefacts, final schema contract, byte hashes, ordered-prefix/completion records, and engine-free classification. Do not compute or inspect pair-feeding Y/C/I. Return exactly one of `STOP_PAIR_MECHANICS`, `REVISE`, or `GO_FOR_HUMAN_SEAL_REVIEW`. Do not edit shared indexes or the Phase-0.5 report.

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md` (especially D-091)
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- latest primary/recovery and preflight journals
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW/{INDEX,COMPLETE}.json`
- all four compressed mechanical shards, through standard-library hash/decompression checks and the engine-free validator
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPRODUCTION{,_REPEAT}.json`

## Files changed

- This journal only.

No shared index, report, implementation, manifest, raw shard, reproduction output, experiment state, prospective package, V5/03G file, or seed namespace was changed by this subagent.

## Actions and reproducible checks

### Independent canonical/hash/prefix audit

A standard-library-only script parsed the manifest, index, completion record, decompressed each shard, recomputed compressed and uncompressed SHA-256 values, recomputed canonical compact JSON bytes, and walked the predecessor chain.

Observed bindings:

- code commit: `3a86ebb15f857f0e9340aeaaba8a8d8cd7776bfb`
- manifest SHA-256: `ed29675de3b90ca7570bf09a2b9f75fe2ccf070f23f09728408b8aeb2eb5367f`
- plan SHA-256: `0c3c75fe8142373dcf6d1aa765dd4247c11570b993e4ea5d1cf4379f958826c3`
- index SHA-256: `06629af2ca9a6092047134ffe18fb1107888d1cd15d1fb28f86c49a8ea3108d1`
- fixed ordered plan: `[50002, 50004, 50005, 50007]`
- prospective namespace: `null`

Every manifest/index/completion JSON document was canonical. `COMPLETE.json.index_sha256` matched the actual index; manifest and plan hashes matched across manifest, index, completion record, and shards. `INDEX.json.complete` was true, proving the four-shard ordered prefix finished publication; `COMPLETE.json.all_worlds_mechanically_complete` was false.

Exact shard checks:

| sequence/world | bytes | compressed SHA-256 | uncompressed canonical SHA-256 | result |
|---|---:|---|---|---|
| 0 / 50002 | 3,815,093 | `0af4715a4fae6e65b601e332afb835d4b8721db9514dc55ea4cc37749a7f690b` | `2813350356928606c377a75ec1498987790e2e4dddda32fd3f78415a6d6625f9` | size/hash/canonical/predecessor PASS |
| 1 / 50004 | 1,534,106 | `e40e726ddb30ad5eae1d6db7aca1ef54f410efb6b7d17ef87059bcc2b16f1979` | `ac7e790ab74935b0c0eb09eb581826a6d6bbb7ec6d48c5fed9920a30a7c0917f` | size/hash/canonical/predecessor PASS |
| 2 / 50005 | 4,717,791 | `024c65434f1cb4806488569358516fedfaa8956d2c58c0ff2200ab71cc980da3` | `723d65daff0814d92dffac5a8d1ff33e358834a2598855f65da19f0ffcab30c6` | size/hash/canonical/predecessor PASS |
| 3 / 50007 | 1,258,193 | `81a0c79ed2f9d1f717ed6c709eaacc33699406ab617dc80d6492e94849286719` | `33959afa57aaa076677150a3b441589036c7ef9be17cb360408dded6a2568b71` | size/hash/canonical/predecessor PASS |

### Engine-free schema/raw reproduction

Each shard was loaded and validated in a fresh process through `directed_causal_pair_phase05_reproduce.read_raw_shard` and `validate_world_shard`. This verifies the closed final schema document and the full raw mechanical contract without importing the engine. All four returned normally; the explicit forbidden-module check was `[]` for every process.

The canonical full reproduction and a repeat are byte-identical:

- both files: 4,524 bytes
- both SHA-256: `8547706b86002dbaef0b02ecbd734a6a2f89777453f409988e0cd2fed2fda17a`
- `mechanical_firewall_pass=true`
- `ordered_prefix_complete=true`
- `all_worlds_mechanically_complete=false`
- `reproduction_status=INCOMPLETE_OR_FAILED`
- canonical schema-document SHA-256: `36c23aaf2832987198f7314702086cf2a36ed4f6414ba1b8336ec31cfb905551`

No engine, DEV world, prospective seed, or outcome-bearing analyzer was invoked during this audit.

## OBSERVED

All four fixed worlds constructed all four history arms, but every world failed during the writer and therefore produced zero access regimes:

| world | history arms | access regimes | first failure | mechanical geometry before failure |
|---:|---:|---:|---|---|
| 50002 | 4 | 0 | writer step 61 / engine step 861: `TARGET_OR_SENTINEL_BELOW_MIN_SIZE` | minimum pair distance 35.171511; halo gap 11.171511; max core/halo/body overlap 0 |
| 50004 | 4 | 0 | writer step 58 / engine step 858: `TARGET_OR_SENTINEL_BELOW_MIN_SIZE` | minimum pair distance 29.300651; halo gap 5.300651; max core/halo/body overlap 0 |
| 50005 | 4 | 0 | writer step 110 / engine step 910: `PAIR_GEOMETRY_UNAVAILABLE`, `TARGET_OR_SENTINEL_BELOW_MIN_SIZE`, `TARGET_OR_SENTINEL_NOT_ALIVE`, `TRACKER_SPLIT_T1` | prior minimum pair distance 33.253881; halo gap 9.253881; max core/halo/body overlap 0; two tracker-event records |
| 50007 | 4 | 0 | writer step 40 / engine step 840: `TARGET_OR_SENTINEL_BELOW_MIN_SIZE` | minimum pair distance 32.892442; halo gap 8.892442; max core/halo/body overlap 0 |

The engine-free validator checked 1,648 step records and 164,709 association edges in total. All declared and derived world-completion flags are false. The fixed pair geometry stayed above the separation threshold and had no halo overlap before failure, but target/sentinel viability failed in every world and world 50005 additionally split/lost a tracked target.

## INFERRED

This is a genuine frozen-mechanics failure, not a publication, hash-chain, schema, or reproduction failure. The mechanical firewall and byte contracts pass, while the scientific mechanics gate fails before the required history-bearing access/no-swap/sham regimes can run. Because all four preselected worlds fail, there is no mechanically qualified DEV world and no basis for an unsealed prospective human-seal package.

Changing the minimum-size gate, substituting another pair/world, shortening the writer, or redefining a split/loss after observing these failures would alter the frozen Phase-0.5 decision rules. It is not a permissible `REVISE` of packaging or implementation.

## HYPOTHESIS

Under the frozen writer and target/tracker viability rules, the selected natural pairs cannot sustain the required four-arm history long enough to reach the pair-context access qualification.

## WHAT WOULD FALSIFY THIS?

- A hash-bound raw shard from the same exact code/manifest/fixed plan that validates engine-free and derives `world_complete=true` for at least the required mechanical set without changing thresholds, worlds, pair selection, writer schedule, or tracker rules.
- Evidence that the reported first failures arise from a reproducibility/schema defect rather than the persisted mechanical records.
- A deterministic rerun of the same authorization producing different raw state hashes or completion classifications; the byte-identical reproduction repeat currently argues against this.

## Failures and dead ends

- A first attempt to reproduce all four expanded shards in one subprocess ended without output, consistent with excessive peak memory while retaining all decoded masks. The audit switched to one fresh engine-free process per shard; all four validated independently, and the predecessor chain was separately recomputed. The canonical full reproduction produced by the parallel raw-reproduction auditor was then verified twice byte-for-byte.
- No third-party `jsonschema` package was installed. The committed standard-library schema-document validator and complete raw-contract validator accepted all four shards. This does not weaken the STOP disposition because the decisive mechanical failures are independently persisted, hash-bound, and reproduced.

## Decisions

**Final disposition: `STOP_PAIR_MECHANICS`.**

This is not `REVISE`: the artefact and reproduction chain is coherent, and the observed failures are frozen target/tracker viability failures rather than a fixable output-format defect. This is not `GO_FOR_HUMAN_SEAL_REVIEW`: no world reached any access regime and all four worlds are mechanically incomplete.

No pair-feeding Y/C/I outcome was computed or inspected. No prospective namespace or seed was opened.

## Unresolved risks

- The shared primary report and indexes were being updated concurrently and were deliberately not used as evidence for this independent disposition.
- The run establishes only failure of this frozen pair-mechanics construction on the fixed DEV worlds. It is not a negative estimate of the broader scientific question and does not authorize a replacement design or new seed family.
- Human review may audit the raw evidence, but it cannot seal this failed mechanics package for prospective execution.

## Handoff

Preserve the manifest, four shards, index/completion record, and byte-identical reproduction outputs. Record `STOP_PAIR_MECHANICS`, no prospective package, and no new authorization. The exact next action is human review of the mechanical stop record only; any different pair-mechanics design would require a new explicitly authorized Phase 0/DEV protocol rather than modification of this result.
