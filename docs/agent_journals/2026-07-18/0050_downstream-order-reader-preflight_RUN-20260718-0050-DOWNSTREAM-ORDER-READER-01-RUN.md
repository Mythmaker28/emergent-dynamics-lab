# Agent journal — DOWNSTREAM-ORDER-READER-01 PROSPECTIVE-RUN-00 preflight

- Role: prospective execution operator and fail-closed preflight auditor
- Run ID: `RUN-20260718-0050-DOWNSTREAM-ORDER-READER-01-RUN`
- Start: 2026-07-18 00:45 CEST
- End: 2026-07-18 00:55 CEST
- Starting Git state: requested execution branch created from exact sealed parent
  `0949ff7167082a894c12480e0b2c75b4cae1c7c6`
- Ending Git state: documentation-only failure handoff on
  `codex/downstream-order-reader-prospective-run-00`; no scientific output
- Assigned scope: one exact authorized prospective family only after 25/25 preflight; otherwise zero-world
  `SEAL_OR_PREFLIGHT_FAILURE`; no code/protocol changes, merge, PR, extension, replacement or reinterpretation

## Actions and important files

1. Read the human authorization verbatim and hashed its source as
   `289872888ba19d149617a70256f62f7c21b97efcea7fd222cc5d9f71ef54557d`.
2. Created `codex/downstream-order-reader-prospective-run-00` at the exact sealed parent.
3. Re-read the repository contract, charter, durable state, decisions, indexes, latest journal, immutable manifest
   and seal report.
4. Verified the manifest hash, exact parent, clean tree, absent outputs, 48 unique ordered seeds, all 15 bound
   hashes and environment without importing the scientific runner or engine.
5. Ran only the standard-library seal verifier. It returned 24/25 and failed `required_branch` because the sealed
   manifest requires the seal branch while the authorization requires the execution branch.
6. Audited the command named by the mission. `DOWNSTREAM_ORDER_READER_01_FUTURE_COMMANDS.md` is the old placeholder
   template and lacks `--authorization`; the actual bound command is in `DOWNSTREAM_ORDER_READER_01_SEALED_COMMANDS.md`.
7. Applied the frozen kill-switch. Did not create an authorization JSON, invoke the runner, initialize an engine or
   world, or create the prospective output directory.

Important evidence:

- `docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_PREFLIGHT_FAILURE.md`
- `docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_PREFLIGHT_FAILURE.json`
- immutable parent manifest and verifier, unchanged

## Reproducible commands

```powershell
$env:PYTHONUTF8='1'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
Get-FileHash docs\individuation\DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json -Algorithm SHA256
git rev-parse HEAD
git branch --show-current
git status --porcelain --untracked-files=all
& $py -m experiments.individuation.downstream_order_reader_verify_seal `
  --manifest docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json
# FAIL: 24/25; failure=[required_branch]; worlds_initialized_by_verifier=0
```

## OBSERVED

- Manifest hash, parent, seeds, bound files, environment and empty output paths all match.
- Manifest `required_branch` is `codex/downstream-order-reader-prospective-seal-00`.
- Human-authorized execution branch is `codex/downstream-order-reader-prospective-run-00`.
- The engine-free verifier fails exactly `required_branch`; all other 24 checks pass.
- The mission-named command file is an unsealed template without the now-required authorization argument.
- Scientific runner invoked: false. Engine/world initializations: 0/0. Prospective files: 0.

## INFERRED

- The current sealed artefacts and current authorization cannot simultaneously satisfy the branch contract.
- Replacing the mission-named command with the separate sealed command would be an unauthorized interpretation of
  an explicit path, even though the latter is technically executable.
- Continuing would require a seal/code binding modification expressly forbidden in this run.

## HYPOTHESIS

A narrow non-scientific reseal that changes only the execution-branch and exact-command bindings can make the same
frozen scientific package executable, but it will create a new manifest hash and therefore requires new human
authorization.

## WHAT WOULD FALSIFY THIS?

- A committed immutable manifest/verifier/runner at the authorized hash that accepts the requested execution branch.
- An executable authorization-aware command actually present at the exact mission-named path and bound by that seal.

## Failures and dead ends

- The first ordinary worktree checkout failed on historical Windows-invalid cache filenames containing `|`. The
  partially attempted path was absent, and no world/output existed. The already-created branch was safely attached
  with `--no-checkout`, then populated by cone-mode sparse checkout of `docs`, `experiments`, `edlab` and root
  environment files. HEAD remained the exact sealed parent and the tree was clean.
- Preflight then failed on the substantive immutable branch binding. No retry or code patch was attempted.

## Decisions, risks and handoff

- Disposition: `SEAL_OR_PREFLIGHT_FAILURE`; authorization not executed and not reusable after a repair/reseal.
- No scientific result or frozen classification exists for this run.
- Exact next authorized action: human-authorized binding-only repair and reseal, followed by a new exact-hash
  execution authorization. No follow-up experiment or execution is automatic.
