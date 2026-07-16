# Reproduction record — final scientific audit 03H rerun

Repository checkout:

```powershell
git rev-parse HEAD
git rev-parse HEAD^
git fsck --full
git status --short --branch
```

Expected target and parent:

```text
7f005bca81e1a8bbd03ca9aa8f7d114931a686a9
23b6e9b3c667705158af833c1cf8458a03c8fb66
```

Fresh authoritative environment:

```powershell
py -3.12 -m venv C:\Users\tommy\Documents\ising-v3-audit-03h-venv
& C:\Users\tommy\Documents\ising-v3-audit-03h-venv\Scripts\python.exe -m pip install `
  -r docs\individuation\TURNOVER_ENVIRONMENT_LOCK_03G.txt
$env:PYTHONPATH = "$PWD;$PWD\experiments\individuation"
$env:PYTHONUTF8 = "1"
```

Canonical checks:

```powershell
$py = "C:\Users\tommy\Documents\ising-v3-audit-03h-venv\Scripts\python.exe"
& $py experiments\individuation\test_turnover_end_to_end_03g.py
& $py experiments\individuation\test_turnover_preseal_03e.py
& $py experiments\individuation\test_turnover_preseal_03c.py
& $py experiments\individuation\test_bijective_tracker.py
& $py experiments\individuation\test_turnover_tracer.py
& $py experiments\individuation\turnover_power_regen.py
& $py experiments\individuation\turnover_runner_03g.py --selfcheck
& $py -m compileall -q experiments\individuation
```

Registered DEV-chain replay controls:

```powershell
$repo = "C:\Users\tommy\Documents\ising-lci-turnover-repair-03g"
& $py "$repo\experiments\individuation\turnover_runner_03g.py" `
  --manifest "$repo\docs\individuation\TURNOVER_DEV_EXECUTION_MANIFEST_03G.json" `
  --seal "$repo\docs\individuation\TURNOVER_DEV_SEAL_03G.json" `
  --authorization "$repo\docs\individuation\TURNOVER_DEV_AUTHORIZATION_03G.json"
# Expected: refused because the canonical execution already exists.

& $py "$repo\experiments\individuation\turnover_runner_03g.py" `
  --manifest "$repo\docs\individuation\TURNOVER_DEV_EXECUTION_MANIFEST_03G.json" `
  --seal "$repo\docs\individuation\TURNOVER_DEV_SEAL_03G.json" `
  --authorization "$repo\docs\individuation\TURNOVER_DEV_AUTHORIZATION_03G.json" `
  --resume
# Expected: already_certified, tip e79cfc4f...adf0.
```

The real seed executor was also called independently for allowed seed `50001` using the committed raw bindings.
Canonical serialization was byte-identical to the committed raw file:

```text
a43817bb72f62c8a2b0f9f1fa919579840e249546e260d2ebbeea10fa9663df6
```

Seal validation and unfilled-permission refusal:

```powershell
& $py experiments\individuation\turnover_runner_03g.py `
  --manifest docs\individuation\TURNOVER_EXECUTION_MANIFEST_03G.json `
  --seal docs\individuation\FINAL_SEAL_MANIFEST_03G.json `
  --authorization docs\individuation\HUMAN_AUTHORIZATION_TEMPLATE_03G.json
```

Expected: `prospective execution is not authorized`; the directory
`results/LCI-TURNOVER-PROSPECTIVE-03G` remains absent.
