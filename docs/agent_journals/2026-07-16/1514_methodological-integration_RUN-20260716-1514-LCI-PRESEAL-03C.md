# Journal — RUN-20260716-1514-LCI-PRESEAL-03C

- Role: independent methodological/statistical integrator.
- Run ID: `RUN-20260716-1514-LCI-PRESEAL-03C`.
- Start: 2026-07-16 15:14 Europe/Paris.
- End: 2026-07-16, finalized before the reconciliation commit.
- Starting Git state: clean isolated branch at
  `cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1`.
- Ending Git state: clean integration branch after the reconciliation commit; exact SHA is the final branch tip.
- Scope: integrate Claude commits `ca7929b` and `cd74eda`; repair remaining PRESEAL blockers; execute no `54xxx`
  seed; keep V4.1 paper work separate.

## Important committed blobs read

- `244bc32`: parent canonical PRESEAL, protocol, seed manifest, power, reproduction, risk register, DEV certificate,
  engine audit, and statistical re-audit.
- `ca7929b` and `cd74eda`: all 21 Claude-added files, inspected through `git show` / Git object reads.
- Frozen dependencies: C1c engine/config, tracker, tracer, confirm-02 runner and analysis.

## OBSERVED

1. Claude added parallel 03A prose without modifying the existing canonical PRESEAL files.
2. `PRESEAL_CANDIDATE_03A.json` at `cd74eda` is truncated and invalid JSON.
3. The 03A static environment token is not a manifest-bound human authorization.
4. The reported cap 96 conflicts with a 96-seed main family plus reserve `54097-54120` (cap 120).
5. E and G do not match their stated scopes: E is four summary values; G is three.
6. The 03A interval fixes LOWO predictions but aggregates row residuals rather than original-world fold losses.
7. Raw tracker status does not establish persistent fission versus transient fragmentation or loss versus death.

## INFERRED

- The authoritative file requiring direct repair is `PRESEAL_CANDIDATE_PROTOCOL.md`, supported by the pre-existing
  canonical JSON/seed/power/reproduction/risk files. Addenda are not an adequate substitute.
- A scientifically coherent hard cap is 50 primary seeds plus 46 feasibility-reserve seeds, all inside
  `54001-54096`.
- Target-local storage is not equivalent to complete-world decodability. The target-memory-masked E scope is the
  load-bearing comparator.

## HYPOTHESIS

If target-local memory genuinely retains target-specific dose information, the fixed L decoder should improve over
the intercept and have lower held-out original-world loss than geometric-neighbour N, target-memory-masked E, and
body baseline B. P and G may still contain information; they are access-scope results, not local-storage proof.

## WHAT WOULD FALSIFY THIS?

- A unit test showing any original world in both train and test.
- A bootstrap path that calls model fitting.
- E retaining nonzero target m1/m2 values.
- Reserve activation changing after endpoint-only mutations.
- Lambda-plus-only ablation changing lambda-minus or another memory parameter.
- Synthetic event evidence failing to distinguish the five required event classes.

## Actions and changed files

- Repaired canonical PRESEAL, seed, power, reproduction, and risk files directly.
- Added Git-blob-bound execution manifest and unauthorized approval template.
- Replaced the prospective runner with fail-closed manifest approval and exact seed sequencing.
- Added complete label-free scope persistence, grouped statistical inference, event evidence, and nine unit tests.
- Marked Claude 03A addenda and DEV diagnostics historical/exploratory where their methods are superseded.
- Updated project, experiment, decision, and run indexes.

## Reproducible validation commands

```powershell
$env:PYTHONPATH = (Get-Location).Path
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\test_turnover_preseal_03c.py
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\test_bijective_tracker.py
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\turnover_prospective_runner.py --selfcheck
```

The first two are synthetic/static. `--selfcheck` instantiates no engine. No simulation was launched.

## Failures / dead ends

- The first unit-test import failed because dynamically loaded dataclasses were not registered in `sys.modules`.
  The import helper was repaired; all nine tests then passed.
- A broad grep entered committed raw JSON and produced unusably large output; subsequent audits excluded raw files.

## Decisions

- Canonical PRESEAL version: 03C.
- Primary `54001-54050`; reserve `54051-54096`; hard cap 96; minimum valid worlds 18.
- Approval is a separate procedural artifact bound to the exact execution-manifest Git blob.
- DEV `n=4` diagnostics remain exploratory.

## Unresolved risks

- Human approval is procedural, not cryptographically signed.
- An effect smaller than the precision available at 18 valid worlds may remain unresolved.
- The historical DEV event labels cannot be retrospectively upgraded because five-frame evidence was not persisted.

## Handoff

Do not run any `54xxx` seed. After explicit human approval only, create a separate approval artifact from the
unauthorized template; do not modify protected code/specifications. The next authorized action is static external
review of the PRESEAL 03C package.
