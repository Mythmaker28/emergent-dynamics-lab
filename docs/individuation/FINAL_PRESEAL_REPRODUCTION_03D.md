# Final PRESEAL reproduction 03D

## Status

Audit-only reproduction. The candidate is **NOT READY** and no prospective execution is authorized.

## Exact source checkout

```powershell
$repo = "C:\path\to\isolated\emergent-dynamics-lab"
git -C $repo fetch origin codex/lci-causal-turnover-preseal-integration-03c
git -C $repo switch --detach a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3
git -C $repo rev-parse HEAD
git -C $repo rev-parse HEAD^
```

Expected:

```text
a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3
cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1
```

On Windows, a normal checkout can fail because unrelated committed paths contain `|`. A sparse checkout covering
`docs`, `experiments`, `edlab`, `tests`, `config`, `reproduction`, `consolidation`, and `release` was required for
this audit.

## One dry-check command block

This block runs no `54xxx` seed. The tracer test uses only existing DEV seeds `50001` and `50002`.

```powershell
Set-Location $repo
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
$python = "C:\path\to\python.exe"

& $python experiments\individuation\test_turnover_preseal_03c.py
& $python experiments\individuation\test_bijective_tracker.py
& $python experiments\individuation\test_turnover_tracer.py
& $python experiments\individuation\turnover_prospective_runner.py --selfcheck
& $python -m py_compile `
  experiments\individuation\turnover_prospective_runner.py `
  experiments\individuation\turnover_statistics.py `
  experiments\individuation\turnover_ownership_analyze.py `
  experiments\individuation\turnover_scope_features.py `
  experiments\individuation\turnover_event_evidence.py
```

Audit results:

- PRESEAL reconciliation tests: 9/9 PASS.
- Bijective tracker: 10/10 PASS.
- Passive tracer/periodicity/DEV censorship checks: PASS.
- Static selfcheck: PASS; no engine instantiated and no seed executed.
- Python compile and JSON parsing: PASS.

These results were obtained under Python 3.12.10 / NumPy 2.5.1 / SciPy 1.18.0 because the exact declared
environment was unavailable and internally contradictory.

## Independent power recomputation

The following non-scientific numerical integration reproduces the committed rounded power claim without running an
engine:

```powershell
@'
import numpy as np
from scipy.special import roots_jacobi, beta
from scipy.stats import binom

def beta_quad(a, b, n=160):
    x, w = roots_jacobi(n, b - 1, a - 1)
    p = (x + 1) / 2
    w = w / (2 ** (a + b - 1) * beta(a, b))
    return p, w

pe, we = beta_quad(8.5, 2.5)
pf, wf = beta_quad(4.5, 4.5)
p = (pe[:, None] * pf[None, :]).ravel()
w = (we[:, None] * wf[None, :]).ravel()
for n in (50, 96):
    print(n, float(np.sum(w * binom.sf(17, n, p))))
'@ | & $python -
```

Expected:

```text
50 0.570903754176...
96 0.924519023326...
```

The number is correct, but no equivalent committed regenerator exists in the candidate.

## Future execution command

There is no valid future execution command for the audited candidate because no final seal exists. The syntactic
template below is deliberately non-runnable and must remain so until a repaired candidate is independently sealed:

```powershell
throw "NOT AUTHORIZED: FINAL_SEAL_MANIFEST_03D.json does not exist"

& $python experiments\individuation\turnover_prospective_runner.py `
  --authorization "<VALID_AUTHORIZATION_BOUND_TO_A_FUTURE_FINAL_SEAL>" `
  --output "<IMMUTABLE_LEDGER_CONTROLLED_OUTPUT>" `
  --phase primary
```

## Frozen analysis command

This command itself runs no scientific engine, but analysis of future data is not authorized until the statistical
gate is repaired and resealed:

```powershell
& $python experiments\individuation\turnover_ownership_analyze.py `
  "<FUTURE_SEALED_RAW_LEDGER>.json" `
  "<FUTURE_SEALED_GROUPED_ANALYSIS>.json"
```

## Reproduction blockers

1. Python/package declarations disagree across the manifest, lockfile, package metadata, and Dockerfile.
2. The runner does not bind a final seal or enforce one-time authorization consumption.
3. Raw outputs have no immutable ledger or final checksum/certificate contract.
4. The power headline lacks a committed regenerator.
5. The required primary analysis gates are incomplete.
