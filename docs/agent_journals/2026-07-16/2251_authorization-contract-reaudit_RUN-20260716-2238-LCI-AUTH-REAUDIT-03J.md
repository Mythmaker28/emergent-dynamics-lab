# Agent journal — authorization contract re-audit 03J

- Role: fresh narrow scientific reproducibility auditor.
- Run ID: `RUN-20260716-2238-LCI-AUTH-REAUDIT-03J`.
- Start time: 2026-07-16 22:38 Europe/Paris.
- End time: 2026-07-16 23:02 Europe/Paris.
- Starting Git state: exact audited commit
  `2b1f45357b0e0be22236e5f73a403cecc27778ea`, parent
  `7f005bca81e1a8bbd03ca9aa8f7d114931a686a9`, isolated clean checkout.
- Ending Git state: local branch
  `audit/lci-turnover-authorization-contract-03j`, four audit-only documents
  added on the exact audited commit, no push.
- Assigned scope: authorization-binding correction and affected provenance
  only; no prospective execution and no repair.

## Important files read

- `AGENTS.md`;
- `docs/RESEARCH_CHARTER.md`;
- `docs/PROJECT_STATE.md`;
- `docs/DECISION_LOG.md`;
- `docs/EXPERIMENT_INDEX.md`;
- `docs/RUN_INDEX.md`;
- latest repair journal and 03G manifest/PRESEAL/canonical records;
- production runner and focused integration tests;
- exact historical commits
  `def070685bf9833a6571766f91c5c7d8a2f8e787` and
  `4bf65651d7b5970c6d21f7369f6fc6386c49449f`.

## Actions

1. Preserved the dirty shared checkout and audited in an isolated materialized
   checkout.
2. Created the required local audit branch at exact commit `2b1f453...`.
3. Verified exact parent, one-parent topology, 22-file diff, and scope.
4. Recomputed the retired seal SHA-256 directly from its historical Git blob.
5. Inspected the production authorization path and validation order.
6. Ran an independent synthetic focused harness using temporary files only.
7. Ran the frozen regression matrix and clean-environment checks.
8. Verified DEV payload equality and traced every changed DEV digest.
9. Audited canonical blob references.
10. Recorded NOT READY without modifying the defect or creating a seal.

## Reproducible commands and experiments

The concise command set is in
`docs/individuation/AUTHORIZATION_CONTRACT_REAUDIT_REPRODUCTION_03J.md`.

The independent focused harness supplied a synthetic seal and temporary
directories to the production runner. It exercised one valid case and eleven
invalid cases. No prospective manifest or 54xxx seed was used.

## OBSERVED

- Whole committed execution-manifest marker count is 2; required count is 1.
- The phrase-template string itself is exact UTF-8, single-line, and has one
  marker.
- Production validation computes and binds the canonical seal hash before
  ledger initialization and engine import.
- All 12 focused dispositions matched expectation; every invalid case created
  no journal, imported no engine, and created no prospective directory.
- 03G 7/7, 03E 18/18, 03C 9/9, tracker 10/10, tracer/event 6/6, power,
  protected-map, runtime, and package checks passed.
- DEV resume passed in its bound repository instance.
- Scientific and feasibility payloads are exactly identical to the parent.
- Exact repaired reproduction and execution-manifest blobs are not both bound
  by the affected canonical indexes.
- No 54xxx record, valid permission, final seal, or prospective directory
  exists.

## INFERRED

- The runner implementation closes the originally reported literal-placeholder
  acceptance defect.
- The audited commit nevertheless does not satisfy the stricter re-audit
  document contract, so issuing a final seal would be scientifically
  irreproducible.
- DEV digest changes are provenance-only and do not alter the scientific
  outcome.

## HYPOTHESIS

A minimal follow-up repair that reduces whole-manifest marker cardinality to
one and binds the exact execution-manifest and reproduction blobs can pass a
fresh narrow audit without changing scientific code or payloads.

## WHAT WOULD FALSIFY THIS?

- Evidence that the mission's marker-count requirement applies only to the
  phrase field rather than the whole committed manifest.
- An existing affected canonical record that binds both exact missing blobs.
- Any frozen regression or payload-equality failure after the document-only
  repair.

## Failures and dead ends

- Normal Windows checkout failed on unrelated historical filenames containing
  invalid Windows path characters. Sparse materialization with
  `core.protectNTFS=false` was used for the audited paths.
- A DEV resume from the audit clone correctly failed repository-instance
  binding. The exact committed resume was rerun read-only in its bound
  repository instance and passed.
- The focused test left a one-byte lock file in the audit clone; it was
  inspected and removed before deliverables were added.

## Decisions

- Verdict: `NOT READY — REPAIR REQUIRED`.
- No final seal or 03I authorization template was created.
- No scientific decision was reopened.
- No repair, push, merge, tag, publication, or submission was performed.

## Unresolved risks

- The manifest marker cardinality and canonical blob coverage must be repaired
  and independently re-audited.
- The retired seal remains invalid and must never be reused.

## Handoff

Exact next authorized action: create a separate document-contract repair that
leaves one `{final_seal_sha256}` occurrence in the whole execution manifest and
binds the exact execution-manifest and reproduction-instruction blobs, then
request a fresh narrow audit. Do not execute any 54xxx seed.
