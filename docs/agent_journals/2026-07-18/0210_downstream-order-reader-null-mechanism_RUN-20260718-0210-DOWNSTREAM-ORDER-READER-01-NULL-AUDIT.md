# Agent journal — DOWNSTREAM-ORDER-READER-01 NULL-MECHANISM-AUDIT-00

- Role: bounded raw-only mechanistic auditor
- Run ID: `RUN-20260718-0210-DOWNSTREAM-ORDER-READER-01-NULL-AUDIT`
- Start time: 2026-07-18 02:10 +02:00
- End time: 2026-07-18 02:27 +02:00
- Starting accepted Git state: `d71c7ebb14cb74d47bbaac7858f4ec0286240bdb`
- Working branch: `codex/downstream-order-reader-null-mechanism-audit-00`
- Ending scientific-artifact commit: `2c582307c79159c841ac5078c604cd39160182bb`
- Ending repository state: final metadata commit and clean pushed branch verified after journal creation
- Assigned scope: one immutable, equation-based, raw-only autopsy; no scientific replay or reclassification

## Repository and branch handling

The shared checkout was dirty, so it was not modified. The first ordinary `git worktree add -b` attempt was
blocked by unrelated tracked cache filenames containing `|`, which Windows cannot check out. The partially
created target was removed after verification; the already-created branch was preserved. A clean isolated
worktree was then created from the exact accepted commit with `--no-checkout` and sparse checkout restricted to
the mission-relevant repository directories. No parent artefact was changed.

This was a direct human-authorized audit, not a scheduled heartbeat, so the scheduled-run lock did not apply.

## Important files read

Read in the required order: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`,
`docs/DECISION_LOG.md`, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`, the completed prospective journal,
`docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json`, the prospective report, `results.json`,
`run_state.json`, all 48 immutable world shards, and the committed raw-only reproduction. Static causal equations
were audited without importing experiment code.

## Actions and reproducible commands

1. Verified exact accepted commit, manifest/raw/reproduction hashes, 48 ordered records, 35 stored contrasts,
   frozen classification, run accounting and all 15 parent bindings using standard-library JSON and SHA-256.
2. Audited raw keys only, before evaluating any mechanism value.
3. Froze the exact decomposition and fail-closed sufficiency gate in commit `130be74`.
4. Implemented a standard-library-only audit and AST/runtime import guards.
5. Ran:

```powershell
python -m pytest -q experiments/individuation/test_downstream_order_reader_null_mechanism_audit.py
python experiments/individuation/downstream_order_reader_null_mechanism_audit.py --repo-root . --plan docs/individuation/DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_DECOMPOSITION_PLAN.md --output docs/individuation/DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_RAW_AUDIT.json
python experiments/individuation/downstream_order_reader_null_mechanism_audit.py --repo-root . --plan docs/individuation/DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_DECOMPOSITION_PLAN.md --output C:\Users\tommy\Documents\DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_RAW_AUDIT_SECOND.json
python experiments/individuation/downstream_order_reader_reproduce.py --manifest docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json --raw-dir results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001/worlds --output C:\Users\tommy\Documents\DOWNSTREAM_ORDER_READER_01_NULL_AUDIT_PARENT_REPRO.json
```

## OBSERVED

- Raw collection SHA-256: `8d4baaac198cf5e5526359ad723d4cebd0c0614ffa2441fead41144ef573adf1`.
- Reproduction SHA-256: `35616172409424d28d765acecb2c29ac1f2527fb7acd48196a9113e85081b679`.
- All immutable accounting and classification checks pass.
- Each complete arm stores aggregate `J_internal_x`, `flux_abs_sum`, count, scale terms and hashes.
- It does not store numerical source core `c`, internal face state/flux or numerical boundary flux.
- Two audit outputs are byte-identical at
  `f22bcb0f0fdd4b858d8f756c56233cb80c9cf8e7a2b2fecc7255efa010d47a7c`.
- The fresh parent raw-only reproduction is byte-identical to the committed reproduction.
- Focused tests pass: `4 passed`.
- Runtime import probes show no engine, runner, reproducer or `edlab` module imported by the audit.
- Zero worlds were initialized or reconstructed.

## INFERRED

The missing numerical values cannot be recovered from aggregates and hashes. Exact local-buffering,
signed-cancellation, saturation, gradient/upwind and boundary-partition decompositions cannot be performed under
the mission's no-reconstruction rule. The predeclared fail-closed outcome therefore applies.

## HYPOTHESIS

None selected. The immutable raw cannot uniquely identify a failure mechanism, and the audit does not rank the
candidate mechanisms.

## WHAT WOULD FALSIFY THIS?

A prospectively persisted numerical face-level array or source-state record, already present inside the accepted
immutable raw collection and sufficient to evaluate the frozen formulas without replay, would falsify the raw-
insufficiency diagnosis. The schema and all 48 shards were checked; no such record exists.

## Failures and dead ends

- Ordinary Windows worktree checkout failed on unrelated invalid cache filenames; recovered with verified
  `--no-checkout` sparse worktree setup.
- A diagnostic command initially looked for a nonexistent aggregate `raw_worlds.jsonl`; the sealed family uses
  48 immutable `worlds/W###.json` shards. This did not change or inspect a scientific outcome.
- No mechanism calculation was attempted after the raw-sufficiency failure.

## Decisions, risks and handoff

Diagnosis: **`RAW_INSUFFICIENT`**. Roadmap: **`UNRESOLVED_RAW_INSUFFICIENT`**. The prospective classification
remains **`NO_ACCESS_ESTABLISHED`**. This does not establish absence or equivalence. No new probe is recommended
because no unique equation-derived mechanism was available. Human review is required; no execution is
authorized.
