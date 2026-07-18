# Agent journal — DOWNSTREAM-ORDER-READER-01 PROSPECTIVE-SEAL-00

- Role: prospective seal and semantic seed-namespace auditor
- Run ID: `RUN-20260718-0000-DOWNSTREAM-ORDER-READER-01-SEAL`
- Start: 2026-07-18 00:00 CEST
- End: 2026-07-18 00:35 CEST
- Starting Git state: clean isolated worktree at accepted parent
  `5ae98861b00f62cde78858234dd03ef4a47f549c`
- Ending Git state: clean pushed tip of `codex/downstream-order-reader-prospective-seal-00` after the final seal
  report commit
- Assigned scope: namespace audit, immutable 48-seed manifest, engine-free verification, final seal artefacts and
  push; no prospective execution, merge, PR, scientific world, BODY-EQUALIZATION or active reconstruction

## Actions and important files

1. Read the repository operating contract and durable research/project/decision/experiment/run state before edits.
2. Created an isolated worktree and branch from the exact accepted parent.
3. Audited the historical 50xxx-57xxx families, every valid local/remote/tag tip, 207 reachable commits, all Git
   objects and all 10 registered worktrees. Recovered and included the valid final OID from the pre-existing
   malformed `probe/tmp01` ref without modifying it.
4. Selected exactly `58001-58048`. Classified the two historical `58001` strings as explicit invalid-seed refusal
   tests, not assignments. No other selected integer had a bounded pre-seal occurrence.
5. Preserved the accepted preregistration byte hash and claim table. Added only a sealing cover, namespace evidence,
   environment/provenance, strict sealed schema, exact commands and immutable manifest.
6. Added a separate authorization boundary: the sealed manifest embeds no execution permission. The runner now
   requires an external exact-manifest-hash authorization and validates branch, accepted ancestry, clean tree,
   bound hashes, sealed output location and non-existing initial output before lazy scientific imports.
7. Added an independent standard-library verifier that imports no runner, contract, NumPy, SciPy or engine.
8. Applied the testing-strategy skill as a compact fail-closed matrix: happy seal, placeholder, duplicate/order,
   design, minimum-world, equivalence-margin and wrong-authorization mutations.
9. Committed the seal inputs separately, ran the verifier from the clean committed tree, then prepared the final
   report, machine result, SHA-256 inventory and durable index updates.

Primary artefacts:

- `docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_NAMESPACE_AUDIT.md` and `.json`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_SEAL_VERIFICATION.md` and `.json`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_SEALED_PREREGISTRATION.md`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_SEALED_COMMANDS.md`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_ENVIRONMENT_PROVENANCE.md`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_SEAL_SHA256.txt`
- `experiments/individuation/downstream_order_reader_verify_seal.py`

## Reproducible commands and validations

```powershell
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $py -m py_compile `
  experiments\individuation\downstream_order_reader_prospective.py `
  experiments\individuation\downstream_order_reader_verify_seal.py `
  experiments\individuation\test_downstream_order_reader_seal.py

& $py -m pytest -q `
  experiments\individuation\test_downstream_order_reader_seal.py `
  experiments\individuation\test_downstream_order_reader_prospective.py
# 17 passed

& $py -m experiments.individuation.downstream_order_reader_verify_seal `
  --manifest docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json
# PASS, 25/25 checks, SEALED_READY_FOR_EXECUTION_REVIEW
```

Namespace commands and exact semantic rules are recorded in the namespace audit. The prospective runner command
was documented but never invoked.

## OBSERVED

- The established candidate blocks from 50xxx through 57xxx are used, reserved, superseded or contaminated.
- `58001-58048` contains no pre-seal scientific assignment or world record.
- `58001` appears only in two tests that deliberately assert refusal of a seed outside their allowed family.
- The pre-existing malformed ref contains a warning line followed by a valid commit OID; the OID is auditable.
- Manifest SHA-256 is `0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4`.
- All 15 bound file hashes and committed blobs match; the prospective output and authorization file are absent.
- Engine initializations: 0. World initializations: 0.

## INFERRED

- The selected namespace is fresh under the declared semantic assignment rule; incidental refusal-test use does
  not constitute seed opening or assignment.
- Separating execution authorization from immutable manifest bytes removes the need to mutate and invalidate the
  sealed manifest after human review.
- The sealed package is ready for a final execution-authorization decision, not for execution itself.

## HYPOTHESIS

If a future exact-hash authorization is supplied and every preflight remains valid, the fixed 48-world family can
test the frozen downstream order interaction without namespace reuse, manifest drift or droplet pseudoreplication.

## WHAT WOULD FALSIFY THIS?

- Evidence that any selected integer was previously assigned to or initialized as a scientific world.
- Any mismatch in the manifest, preregistration, runner, instrumentation, verifier or other bound hash.
- A dirty/wrong branch, changed accepted ancestry, existing initial output, malformed authorization, duplicate seed,
  altered family, altered scientific contract or engine import before preflight.

## Failures and dead ends

- `git rev-list --all` initially failed on the pre-existing malformed `probe/tmp01` ref. The ref was preserved; its
  valid final OID was recovered read-only and explicitly included in the audit tip set.
- The first focused test run had one expected-message mismatch because the accepted-commit gate fired before the
  unsealed-mode gate. The test was broadened to accept either fail-closed preflight reason; no scientific code or
  threshold changed. The rerun passed 17/17.
- A PowerShell `ConvertFrom-Json -AsHashtable` check was unavailable in the installed PowerShell. The same complete
  hash check was rerun with standard-library Python and passed.

## Decisions, unresolved risks and handoff

- Decision recorded as D-097: select and seal `58001-58048`; execution remains unauthorized.
- No scientific definition, endpoint, horizon, threshold, eligibility rule or classification changed.
- Operational crash recovery remains explicit `--resume` with exact ordered-prefix validation; it is not an
  outcome-driven extension or early stop.
- Exact next authorized action: human review of manifest hash
  `0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4`. Only a new explicit exact-hash execution
  authorization may permit the documented prospective command. Otherwise stop.
