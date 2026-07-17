# DOWNSTREAM-ORDER-READER-01 — prospective preflight failure

Status: **SEAL_OR_PREFLIGHT_FAILURE**. No scientific runner, engine or world was initialized.

## Binding failure

The authorization requires a new execution branch:

```text
codex/downstream-order-reader-prospective-run-00
```

The immutable manifest and engine-free verifier instead require:

```text
codex/downstream-order-reader-prospective-seal-00
```

The requested execution worktree starts clean and exactly at sealed parent
`0949ff7167082a894c12480e0b2c75b4cae1c7c6`. On that branch the sealed engine-free verifier passes 24 of 25 checks
and fails only `required_branch`. The frozen production runner contains the same branch gate, so it cannot legally
reach its lazy scientific imports from the authorized execution branch.

There is a second command-binding conflict. The mission requires the exact command in
`DOWNSTREAM_ORDER_READER_01_FUTURE_COMMANDS.md`, but that parent file remains the old unsealed placeholder template
and lacks the runner's required `--authorization` argument. The actual bound command is in
`DOWNSTREAM_ORDER_READER_01_SEALED_COMMANDS.md`. Substituting one path for the other would violate the explicit
mission instruction.

## Passing preflight evidence

- manifest SHA-256 exact:
  `0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4`;
- exact sealed parent: PASS;
- clean worktree before preflight: PASS;
- prospective and reproduction output paths absent: PASS;
- exactly 48 unique ordered seeds `58001-58048`: PASS;
- all 15 bound file and preregistration hashes: PASS;
- environment: Windows 11 build 26200, Python 3.12.10, NumPy 2.5.1, SciPy 1.18.0, pytest 8.4.2;
- engine-free verifier: **24/25, FAIL on `required_branch`**;
- scientific runner invoked: no;
- engine/world initialization: `0/0`;
- external authorization JSON created: no;
- prospective output created: no.

## Exact preflight command

```powershell
$env:PYTHONUTF8='1'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $py -m experiments.individuation.downstream_order_reader_verify_seal `
  --manifest docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json
```

The verifier returned exit code 1 and `verdict=REVISE_SEAL`. Per the authorized kill-switch, the prospective
runner was not invoked.

## Required human handoff

A new bounded repair must align the immutable manifest, verifier, runner, execution branch and named exact-command
file without changing any scientific content. That repair must be resealed to a new manifest hash, followed by a
new explicit human execution authorization. The current authorization cannot be used to patch and continue.
