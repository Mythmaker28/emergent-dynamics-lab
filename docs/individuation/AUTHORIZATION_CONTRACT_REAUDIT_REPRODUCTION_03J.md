# Reproduce authorization contract re-audit 03J

Use commit
`2b1f45357b0e0be22236e5f73a403cecc27778ea` in a clean checkout. These commands
do not execute a prospective seed.

```powershell
git rev-parse HEAD
git rev-parse HEAD^
git rev-list --parents -n 1 HEAD
git diff --name-status 7f005bca81e1a8bbd03ca9aa8f7d114931a686a9 HEAD
git diff --check 7f005bca81e1a8bbd03ca9aa8f7d114931a686a9 HEAD
```

Verify the blocking marker cardinality:

```powershell
$raw = Get-Content -Raw `
  docs\individuation\TURNOVER_EXECUTION_MANIFEST_03G.json
([regex]::Matches(
  $raw,
  [regex]::Escape('{final_seal_sha256}')
)).Count
```

Expected result: `2`. The mission requires `1`.

Verify the repaired blobs:

```powershell
git rev-parse HEAD:experiments/individuation/turnover_runner_03g.py
git rev-parse HEAD:docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json
git rev-parse HEAD:docs/individuation/TURNOVER_AUTHORIZATION_TEMPLATE_03G.json
git rev-parse HEAD:experiments/individuation/test_turnover_end_to_end_03g.py
git rev-parse HEAD:docs/individuation/TURNOVER_REPRODUCTION_03G.md
```

Search the canonical records for all five exact blobs. The reproduction blob
`6107c29990071ec0ac9906661bf4bd21ec881337` and execution-manifest blob
`c65d8ba80b5961ef32ca37f65c6082c93002b928` have no exact canonical reference.

Run the frozen regressions in the exact environment:

```powershell
$env:PYTHONPATH = "$PWD;$PWD\experiments\individuation"
$env:PYTHONUTF8 = "1"
$python = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe"

& $python experiments\individuation\test_turnover_end_to_end_03g.py
& $python experiments\individuation\test_turnover_preseal_03e.py
& $python experiments\individuation\test_turnover_preseal_03c.py
& $python experiments\individuation\test_bijective_tracker.py
& $python experiments\individuation\test_turnover_tracer.py
& $python experiments\individuation\turnover_runner_03g.py --selfcheck
& $python experiments\individuation\turnover_power_regen.py
```

Do not run the production manifest, create the prospective directory, or
execute any seed from 54001 through 54096.
