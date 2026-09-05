# Reproduction and future activation commands — PRESEAL 03C

## Static verification only (authorized now; runs no simulation)

```powershell
cd "C:\Users\tommy\Documents\ising-lci-turnover-integration"
$env:PYTHONPATH = (Get-Location).Path
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\test_turnover_preseal_03c.py
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\turnover_prospective_runner.py --selfcheck
```

`--selfcheck` is static. It does not instantiate an engine and cannot execute a seed.

## Human approval artifact (future only)

After explicit human approval, copy
`docs\individuation\TURNOVER_EXECUTION_APPROVAL_TEMPLATE_03C.json` outside the protected specification set, set
`authorized` and `one_execution_only` to `true`, preserve the exact manifest blob and approval phrase, and fill:

`authorization_id`, `approved_by`, `approved_at_utc`.

This changes an approval record only; no code, seed plan, feature, gate, or statistical specification changes.

## Prospective primary execution (NOT AUTHORIZED NOW; do not run)

```powershell
cd "C:\Users\tommy\Documents\ising-lci-turnover-integration"
$env:PYTHONPATH = (Get-Location).Path
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\turnover_prospective_runner.py `
  --authorization work\TURNOVER_EXECUTION_APPROVAL_03C.json `
  --output work\turnover_prospective_03c.json `
  --phase primary
```

## Feasibility reserve (future only; runner refuses unless the frozen trigger fires)

```powershell
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\turnover_prospective_runner.py `
  --authorization work\TURNOVER_EXECUTION_APPROVAL_03C.json `
  --output work\turnover_prospective_03c.json `
  --phase reserve
```

## Frozen grouped analysis (after the authorized execution)

```powershell
& "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe" `
  experiments\individuation\turnover_ownership_analyze.py `
  work\turnover_prospective_03c.json `
  work\turnover_grouped_analysis_03c.json
```

No `54xxx` command in this document is authorized by its presence here.
