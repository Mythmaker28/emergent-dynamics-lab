# Final PRESEAL re-audit reproduction 03F

These commands reproduce the static and synthetic audit without executing or instantiating any prospective
`54xxx` world. They do not authorize execution.

## 1. Exact checkout and provenance

```powershell
$repo = "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f"
$remote = "https://github.com/Mythmaker28/emergent-dynamics-lab.git"
$audited = "23b6e9b3c667705158af833c1cf8458a03c8fb66"
$parent = "a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3"
$priorAudit = "9038ff08f7487e10f3615c269ed2a3af7197e2cb"
$archive = "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77"

git clone --filter=blob:none --no-checkout $remote $repo
git -C $repo config core.protectNTFS false
git -C $repo config core.protectHFS false
git -C $repo fetch origin `
  repair/lci-causal-turnover-preseal-03e `
  audit/lci-causal-turnover-final-preseal-03d `
  archive/main-f3921a4
git -C $repo switch --detach $audited

if ((git -C $repo rev-parse HEAD) -ne $audited) { throw "Wrong repair tip" }
if ((git -C $repo rev-parse "$audited^") -ne $parent) { throw "Wrong repair parent" }
if ((git -C $repo rev-parse "origin/audit/lci-causal-turnover-final-preseal-03d") -ne $priorAudit) {
  throw "Wrong prior audit"
}
if ((git -C $repo rev-parse "origin/archive/main-f3921a4") -ne $archive) { throw "Wrong archive" }
git -C $repo fsck --full
git -C $repo show --stat --oneline $audited
```

Expected repair delta: 17 added files and 1,459 added lines. The protected archive is a separate lineage and is not
an ancestor of the turnover repair line.

## 2. Verify canonical Git blobs, not CRLF-converted working copies

```powershell
Set-Location $repo
$manifestPath = "docs/individuation/TURNOVER_EXECUTION_MANIFEST_03E.json"
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$failures = @()

foreach ($entry in $manifest.protected_git_blobs.PSObject.Properties) {
  $path = $entry.Name
  $expected = [string]$entry.Value
  $actual = (git rev-parse "$audited`:$path").Trim()
  if ($actual -ne $expected) {
    $failures += "$path expected=$expected actual=$actual"
  }
}
if ($failures.Count -ne 0) { throw ($failures -join [Environment]::NewLine) }
"Protected blobs verified: $($manifest.protected_git_blobs.PSObject.Properties.Count)"
```

Expected: `Protected blobs verified: 21`.

Canonical LF bytes of `TURNOVER_ENVIRONMENT_LOCK_03E.txt` have SHA-256
`a0bdccc0c2d91d7df9b1781df9198fa6d9131bd45a1e46e4c18b72a8f86aea0e`. A normal Windows
working copy may have different CRLF bytes and must not be used as the canonical hash.

## 3. Confirm no persisted prospective family result

```powershell
Set-Location $repo
$structured = git log --all -G '"seed"\s*:\s*54(0[0-9]|[1-8][0-9]|9[0-6])' `
  --format='%H %s' -- '*.json' '*.jsonl' '*.md' '*.csv' '*.txt'
if ($structured) { $structured } else { "NO_STRUCTURED_54001_54096_SEED_RECORDS" }

$named = git log --all --name-only --format= |
  Select-String -Pattern '540(0[1-9]|[1-8][0-9]|9[0-6])'
if ($named) { $named } else { "NO_54001_54096_FILENAMES_IN_HISTORY" }
```

This is a history inspection only. It does not prove that no uncommitted execution ever occurred outside the
repository, but it found no committed structured prospective result or prospective filename.

## 4. Substitute-environment tests

The exact declared Linux/Python 3.11.15 environment was not available. The following tests passed in a substitute
Windows environment using Python 3.12.10 with NumPy 2.2.6, SciPy 1.15.3, and Matplotlib 3.10.9:

```powershell
$python = "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe"
Set-Location $repo
$env:PYTHONPATH = $repo
$env:PYTHONIOENCODING = "utf-8"

& $python experiments/individuation/test_turnover_preseal_03e.py
& $python experiments/individuation/test_turnover_preseal_03c.py
& $python experiments/individuation/test_bijective_tracker.py
& $python experiments/individuation/test_turnover_tracer.py
& $python experiments/individuation/turnover_prospective_runner_03e.py --selfcheck
& $python experiments/individuation/turnover_power_regen.py
& $python -m compileall -q experiments/individuation
```

Expected:

- 03E synthetic/static suite: 18 checks pass.
- 03C suite: 9/9 pass.
- bijective tracker: 10/10 pass.
- tracer suite: pass using existing DEV fixtures only.
- runner self-check: pass without an engine or seed.
- power: mean `0.386363636...`, `P(>=18 | 50)=0.570903754175`,
  `P(>=18 | 96)=0.924519023324`.

The passing substitute tests do not satisfy the exact-environment requirement.

## 5. Environment failure reproduction

```powershell
Set-Location $repo
& $python -m pip install --dry-run -r docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03E.txt
```

Expected failure: `platform==Linux-x86_64` is not a valid Python package requirement. The file is descriptive text,
not an installable hash-locked transitive environment.

On the audited host, Docker Desktop was installed but the Linux engine was unavailable because a WSL update was
required. Therefore the exact Linux/Python 3.11.15 environment was not recreated.

## 6. Static runner and decision-path audit

```powershell
Set-Location $repo
@'
import ast
from pathlib import Path

p = Path("experiments/individuation/turnover_prospective_runner_03e.py")
tree = ast.parse(p.read_text(encoding="utf-8"))
names = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name):
            names.append(fn.id)
        elif isinstance(fn, ast.Attribute):
            names.append(fn.attr)

for target in ("run_seed", "record_seed", "close_run"):
    print(target, names.count(target))
print("reserve_activation_function",
      any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and "reserve" in n.name.lower()
          for n in ast.walk(tree)))
'@ | & $python -

rg -n "DISTRIBUTED_ENV|decision.*tree|outcome.*[A-F]|run_seed|record_seed|close_run|reserve" `
  experiments/individuation docs/individuation
```

Expected runner counts are zero and no reserve-activation function exists in the 03E runner. Manual source
inspection is still required to distinguish documentation strings from executable decision logic.

## 7. Required synthetic red-team checks

Using temporary directories and synthetic non-prospective records, verify all of the following against
`turnover_execution_ledger.py` and `turnover_prospective_runner_03e.py`:

1. Present one identical approval/seal pair to two different fresh `--run-dir` paths.
2. Call `record_seed` with seed `99999`.
3. Close a ledger, then call `record_seed` again.
4. Remove the completion line and call `verify_chain` on the retained prefix.
5. Modify a retained line and verify that the chain fails.
6. Reorder retained lines and verify that the chain fails.
7. Remove any hypothetical runner/analysis blob fields from the approval and validate it.

Observed:

```text
same_approval_dir1=fresh
same_approval_dir2=fresh
approval_without_runner_or_analysis_fields=ACCEPTED
arbitrary_seed_99999=ACCEPTED
seed_after_completion=ACCEPTED
completion_deleted_prefix=ACCEPTED
retained_entry_tamper=DETECTED
reordered_entries=DETECTED
```

These tests use no seed from the prospective family and instantiate no simulation engine.

## 8. Seal and execution guard

`docs/individuation/FINAL_SEAL_MANIFEST_03E.json` must remain absent for this verdict. The authorization template
must remain invalid and unfilled.

```powershell
Set-Location $repo
if (Test-Path "docs/individuation/FINAL_SEAL_MANIFEST_03E.json") {
  throw "Unexpected final seal: this candidate failed re-audit"
}

throw "STOP: NOT AUTHORIZED. Do not execute any seed in 54001-54096."
```
