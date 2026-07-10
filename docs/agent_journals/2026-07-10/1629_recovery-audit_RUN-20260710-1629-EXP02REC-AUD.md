# Agent Journal - RUN-20260710-1629-EXP02REC-AUD

## AGENT / ROLE

Independent recovery auditor / EXP02 crash, resume, and `COMPLETE` publication gate.

## RUN ID

`RUN-20260710-1629-EXP02REC-AUD`

## START / END TIME

- Start: 2026-07-10 16:19 +02:00.
- End: 2026-07-10 16:29 +02:00.

## STARTING GIT STATE

- Branch: `main` tracking `origin/main`.
- HEAD: `622ba9c4b9f05360a6eb0f409fe099f5dcaf7866`.
- The primary run already owned the conservative lock.
- The recovery implementation and tests were uncommitted primary-agent changes. This audit did not acquire a competing lock and did not modify shared implementation files.

## ASSIGNED SCOPE

Audit the current worktree recovery gate only: Windows process interruption, unpublished shard temporaries, quarantine/resume, premature final manifest publication, raw and derived corruption, plan drift, disk headroom, row-count/index consistency, and idempotent return from a verified `COMPLETE` experiment. Do not launch EXP02 and do not edit shared code or documents other than this journal.

## IMPORTANT FILES READ

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-10/1609_primary_RUN-20260710-1609-EXP02REC.md`
- `results/HOLDOUT-COREV0-20260710-003/manifest.json`
- `results/HOLDOUT-COREV0-20260710-003/summary.json`
- `docs/experiments/EXP02_COREV0_PROTOCOL.md`
- `docs/ARTIFACT_POLICY.md`
- `edlab/experiments/streaming.py`
- `edlab/cli.py`
- `tests/test_experiment_pipeline.py`

## ACTIONS ACTUALLY PERFORMED

- Inspected the full recovery/finalization implementation and the primary agent's diff against HEAD.
- Ran the complete suite twice as the worktree advanced from 33 to 34 tests.
- Independently checked the shard publication ordering, identity hash, file SHA-256/size/CSV-row verification, raw-index uniqueness, manifest/raw/summary total reconciliation, derived-output hashing, manifest-last publication, and completed-manifest fast path.
- Confirmed the real child-process test exits with `os._exit(73)` after shard files and manifest are fsynced but before directory publication; the next invocation quarantines the unpublished directory, recomputes once, and reaches `COMPLETE`.
- Ran two additional adversarial probes in system temporary directories: changed `reservoir_size` across a finalizer-crash resume, and planted an atomic-write-style temporary file directly under `raw/` beside an already complete result.
- Measured current disk headroom without writing experiment data.

## REPRODUCIBLE COMMANDS / PROBES

- `.\.venv\Scripts\python.exe -m pytest -q` -> `34 passed in 6.87s` on the final audited worktree.
- Adversarial temporary-directory probe using `unittest.mock.patch` around `_atomic_plot_sample` -> a partial run started with `reservoir_size=1` resumed with `reservoir_size=17` and published `COMPLETE`; `reservoir_size` was absent from `stream_plan.json`.
- Adversarial temporary-directory probe -> `raw/.recovery_log.json-abrupt.tmp` remained present and a verified `COMPLETE` fast path still returned successfully.
- Disk check: `165864054784` bytes free versus the implementation's EXP02 preflight requirement of `4311744512` bytes, about `38.47x` headroom.

## OBSERVED

- The 34-test worktree exercises byte-equivalence, immutable-shard resume, raw corruption rejection, plan drift rejection, injected finalizer failure, derived-output corruption rejection, idempotent `COMPLETE` return, and a real abrupt process exit before shard publication.
- No final shard is visible before its `run_manifest.json` and four raw files are written and fsynced. A crash before the directory rename leaves only a dot-prefixed unpublished directory. Every visible final shard is reverified before aggregation and again through the final raw index.
- `manifest.json` is written atomically after all derived outputs; its verifier requires `status=COMPLETE`, exact expected/completed run counts, the frozen plan hash, verified output hashes/sizes, unique raw-index keys, all 900 planned identities, raw file row counts, and summary/raw-total agreement.
- The available disk is far above the conservative fixed preflight estimate for 900 remaining runs.
- Two bounded hardening gaps remain:
  1. `reservoir_size` is not part of the plan, manifest, or reproduction command. The API can therefore change the audit-plot reservoir across an interrupted finalization without plan-drift rejection. Raw shards, full histograms, aggregates, probe counts, and scientific observables are unaffected. The official CLI does not expose this option and therefore uses the same fixed default.
  2. Orphan scanning covers top-level atomic temporaries and `raw/runs/.law-*` directories, but not atomic recovery-log temporaries directly under `raw/`. A second crash while publishing the recovery log can leave such a file unreported while a later `COMPLETE` verification succeeds. This does not publish a partial shard or alter indexed scientific data, but it can make the double-crash recovery trace incomplete.

## INFERRED

- The core EXP02 scientific data path is fail-closed for the tested interruption and corruption classes. A complete shard cannot be silently accepted with missing, changed, or row-count-inconsistent raw files.
- The two observed gaps affect reproducibility metadata for a non-default plot reservoir and completeness of a rare double-crash recovery audit trail; neither changes the deterministic raw simulation, the P/M aggregates, or the manifest-last invariant under the preregistered CLI invocation.

## HYPOTHESIS

- On the official fixed-default CLI path, a single process failure at any tested shard/finalizer boundary will either leave a quarantinable unpublished temporary or a fully verifiable immutable shard, and restart will converge idempotently to one complete 900-run index.

## WHAT WOULD FALSIFY THIS?

- A fault that exposes a final shard without a verifiable complete manifest and raw files, accepts a changed raw byte or incorrect CSV row count, duplicates or omits a planned law/seed in `raw_index.json`, publishes `manifest.json` before all indexed outputs exist, or recomputes a verified completed shard.

## FAILURES / DEAD ENDS

- No core crash/recovery test failed.
- The two adversarial hardening probes intentionally demonstrated accepted non-scientific drift/orphan states described above.

## DECISIONS / VERDICT

`GO_AFTER_CLEAN_COMMIT` for the preregistered EXP02 launch. There is no remaining scientific-data recovery blocker in the audited worktree. Do not launch from HEAD `622ba9c`, because the audited recovery implementation is still only a worktree diff. Commit it coherently, rerun the suite on the resulting clean SHA, push, and invoke the official CLI with its fixed default reservoir.

The two hardening gaps are non-blocking for that exact official invocation. Minimal future repairs are: add `reservoir_size` to the frozen plan/manifest/reproduction command, and include `raw/` atomic-write temporaries plus quarantine inventory in recovery reconciliation.

## UNRESOLVED RISKS

- Raw shards remain local and ignored; hashes/indexes detect loss but are not a remote raw backup.
- Directory metadata cannot be fsynced portably through this Windows Python path. Post-crash verification makes loss or tearing fail closed, but cannot guarantee storage-device durability against every power-loss/controller failure.
- Changing HEAD between an interrupted screen and its resume intentionally triggers plan drift. The run should remain on its launch SHA until completion or use an explicitly designed recovery handoff that preserves the original plan commit.

## HANDOFF

Primary agent: commit the audited implementation/tests/journals, run all tests once on the clean resulting SHA, push, then launch `EXP02-COREV0-20260710-001` through `edlab.cli stream-screen` without changing the default reservoir. Keep the same launch SHA for any resume. Do not weaken gates or launch a hold-out before the frozen EXP02 candidate rule is applied.

## ENDING GIT STATE

- HEAD remained `622ba9c4b9f05360a6eb0f409fe099f5dcaf7866` throughout this audit.
- Shared implementation/test changes remained owned by the primary agent.
- This journal is the only file created by this auditor.
