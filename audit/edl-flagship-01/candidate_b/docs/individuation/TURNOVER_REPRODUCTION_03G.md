# Turnover 03G reproduction

## Clean environment

```powershell
$repo = "C:\Users\tommy\Documents\ising-v3-repair-03i-index"
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

The 03G integration suite remains exactly 7 tests. Its authorization-tamper test contains the 13 focused 03I
contract cases: exact calculated hash accepted in both the separate field and expanded phrase; both literal
placeholder syntaxes, wrong/malformed hashes, template cardinality errors, and exact-string changes rejected; and
pre-engine failure proved without a ledger or prospective run directory.

## DEV smoke

The committed DEV fixture is structurally identical to the future prospective path but allows only seed `50001`,
uses `DEV/EXPLORATORY` manifests/authorization, and writes to
`results/LCI-TURNOVER-DEV-E2E-03G`.

```powershell
& "$venv\Scripts\python.exe" experiments\individuation\turnover_runner_03g.py `
  --manifest docs\individuation\TURNOVER_DEV_EXECUTION_MANIFEST_03G.json `
  --seal docs\individuation\TURNOVER_DEV_SEAL_03G.json `
  --authorization docs\individuation\TURNOVER_DEV_AUTHORIZATION_03G.json `
  --resume
```

The committed DEV chain was rebound after the runner and protected manifest hashes changed by replaying the
already-open seed-50001 raw scientific payload through the ledger and analyzer with an injected executor. Engine
import was forbidden and observed zero calls. The `scientific` and `feasibility` subtrees are identical to the
pre-repair DEV record; only provenance-dependent hashes changed. A fresh invocation must fail. Explicit `--resume`
must verify and return the existing certified result without rerunning seed 50001.

## Future authorization contract

The frozen manifest template is exactly:

```text
I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256={final_seal_sha256}
```

A fresh auditor must create a new final seal. A future human authorization must separately set
`final_seal_sha256` to the canonical SHA-256 of that seal, set `one_execution_only` to `true`, and put the same
lowercase 64-character hash into `approval_phrase` by replacing the single allowed placeholder. The runner performs
no case, whitespace, punctuation, length, or Unicode normalization.

## Prospective guard

```powershell
& "$venv\Scripts\python.exe" experiments\individuation\turnover_runner_03g.py `
  --authorization docs\individuation\TURNOVER_AUTHORIZATION_TEMPLATE_03G.json
```

Expected: refusal because `FINAL_SEAL_MANIFEST_03G.json` is absent and the template is deliberately unfilled and
invalid. The literal `{final_seal_sha256}` is never authorization. Do not execute any seed `54001-54096`.
