# Turnover 03G reproduction

## Clean environment

```powershell
$repo = "C:\Users\tommy\Documents\ising-lci-turnover-repair-03g"
$venv = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean-reproduction"
py -3.12 -m venv $venv
& "$venv\Scripts\python.exe" -m pip install -r `
  "$repo\docs\individuation\TURNOVER_ENVIRONMENT_LOCK_03G.txt"
$env:PYTHONPATH = "$repo;$repo\experiments\individuation"
```

## Static and integration validation

```powershell
Set-Location $repo
& "$venv\Scripts\python.exe" -m compileall -q experiments\individuation
& "$venv\Scripts\python.exe" experiments\individuation\test_turnover_end_to_end_03g.py
& "$venv\Scripts\python.exe" experiments\individuation\test_turnover_preseal_03e.py
& "$venv\Scripts\python.exe" experiments\individuation\test_turnover_preseal_03c.py
& "$venv\Scripts\python.exe" experiments\individuation\test_bijective_tracker.py
& "$venv\Scripts\python.exe" experiments\individuation\test_turnover_tracer.py
& "$venv\Scripts\python.exe" experiments\individuation\turnover_power_regen.py
& "$venv\Scripts\python.exe" experiments\individuation\turnover_runner_03g.py --selfcheck
```

These checks use synthetic states or already-open DEV seeds only.

## DEV smoke

The committed DEV fixture is structurally identical to the future prospective path but allows only seed `50001`,
uses `DEV/EXPLORATORY` manifests/authorization, and writes to
`results/LCI-TURNOVER-DEV-E2E-03G`.

```powershell
& "$venv\Scripts\python.exe" experiments\individuation\turnover_runner_03g.py `
  --manifest docs\individuation\TURNOVER_DEV_EXECUTION_MANIFEST_03G.json `
  --seal docs\individuation\TURNOVER_DEV_SEAL_03G.json `
  --authorization docs\individuation\TURNOVER_DEV_AUTHORIZATION_03G.json
```

Second fresh invocation must fail. Explicit `--resume` must verify and return the existing certified result without
rerunning seed 50001.

## Prospective guard

```powershell
& "$venv\Scripts\python.exe" experiments\individuation\turnover_runner_03g.py `
  --authorization docs\individuation\TURNOVER_AUTHORIZATION_TEMPLATE_03G.json
```

Expected: refusal because `FINAL_SEAL_MANIFEST_03G.json` is absent and the template is invalid. Do not execute any
seed `54001-54096`.
