# Agent Journal — RUN-20260710-1721-HOLD04-AUD

## AGENT / ROLE

Independent HOLDOUT04 raw-data auditor.

## RUN ID

`RUN-20260710-1721-HOLD04-AUD`

## START TIME

2026-07-10 17:21:10 +02:00

## END TIME

In progress.

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3`
- Branch: `main`
- HEAD: `d9d9a52ee5ff11a580227ed362354d914b8f9`
- `origin/main`: `d9d9a52ee5ff11a580227ed362354d914b8f9`
- Worktree was not clean: `results/HOLDOUT-COREV0-20260710-004/` was untracked because the primary agent was producing and indexing the hold-out.
- The primary agent owns the active-run lock; this delegated read-only audit does not acquire or release it.

## ASSIGNED SCOPE

Independently recompute the frozen HOLDOUT04 disposition from the preregistered protocol and raw tables; verify eligible laws/seeds, alias status, hashes and counts; identify discrepancies. Read-only except this unique journal. Do not edit project docs, code, results, or commit.

## IMPORTANT FILES READ

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-10/1609_primary_RUN-20260710-1609-EXP02REC.md`
- `results/HOLDOUT-COREV0-20260710-004/manifest.json`
- `results/HOLDOUT-COREV0-20260710-004/summary.json`

## ACTIONS PERFORMED

- Read the repository's durable state in the mandated order.
- Read the `data:validate-data` skill and adopted its independent recalculation, completeness, deduplication, denominator, and selection-bias checks.
- Inspected the starting Git state before creating this journal.

## COMMANDS / EXPERIMENTS EXECUTED

In progress.

## OBSERVED

In progress.

## INFERRED

In progress.

## HYPOTHESIS

The committed frozen rule, when reconstructed only from raw measurement/entity/lineage/edge tables, will retain laws 0 and 52 in exactly two of five unseen seeds without rejecting the live sparse look-alike/static-flux nulls.

## WHAT WOULD FALSIFY THIS?

Any independent raw-table reconstruction yielding a different law/seed set, a failed manifest hash/count, an unlogged compatible alternative edge, a P/M recomputation mismatch, or evidence that the selected tracks reject the declared alias null.

## FAILURES / DEAD ENDS

None yet.

## DECISIONS

No protocol or scientific decision is authorized for this audit.

## UNRESOLVED RISKS

In progress.

## HANDOFF

In progress.

## ENDING GIT STATE

In progress.
