# Clean-room reproduction report

**Scope.** Independent-environment reproduction of the paper's PRIMARY longitudinal certification from
committed data only. This is an *independent-environment* reproduction (fresh OS-level environment, fresh
dependency install from the lockfile) — **not** a third-party or human external replication.

## Procedure
1. Isolated tree in a native (non-repo) filesystem containing only the release inputs: the `reproduction/`
   package (source), `requirements-lock.txt`, `reproduction/EXPECTED.json`, and the single raw data file
   `results/observer/tca_holdout_raw.pkl`.
2. Fresh Python virtual environment (`python -m venv`), no inherited site-packages.
3. Installed **only** from `requirements-lock.txt` → numpy==2.2.6, matplotlib==3.10.9 (Python 3.10.12).
4. Ran `python -m reproduction.primary --check` in a **stripped environment** (`env -i`, no inherited
   `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, no reused `__pycache__`).
5. Compared output SHA-256 to the canonical outputs.

## Result: PASS (byte-identical scientific outputs)
| output | canonical SHA-256 | clean-room SHA-256 | match |
|---|---|---|---|
| primary_table.csv | 8cac07a6eb3d7b31… | 8cac07a6eb3d7b31… | ✓ |
| primary_results.json | 022429e564a699b4… | 022429e564a699b4… | ✓ |

`--check` passed (all values within tolerance point=0.06, ci=0.08). The figure PNG is regenerated but not
hash-compared (matplotlib raster output can vary by platform font rendering; the underlying numbers are in
the CSV/JSON, which match byte-for-byte). Determinism comes from the fixed bootstrap seed (20260715).

## Reproduced primary result
```
track survival: 36/36  switches=0  lost=0
ckpt      meanM |  h1 R^2 [95% CI]          |  h2 R^2 [95% CI]
init      1.000 | +0.785 [+0.557,+0.944]     | +0.801 [+0.532,+0.922]
moderate  0.387 | +0.933 [+0.889,+0.979]     | -0.032 [-0.679,+0.573]
deep-1    0.245 | +0.897 [+0.860,+0.974]     | -0.053 [-0.528,+0.460]
deep      0.190 | +0.888 [+0.837,+0.958]     | -0.239 [-0.785,+0.318]
GATE h1 deep-turnover CERTIFIED (CI lower bound 0.837 > 0.50): True
GATE h2 deep-turnover NOT ESTABLISHED (CI does not clear 0.50):  True
```

## MATERIAL FINDING — reproducibility caveat (release blocker #1)
The committed-data reproduction reproduces the paper's **conclusions** but **not** the exact **inline point
estimates** printed in the manuscript / `TCA_01_HOLDOUT_CERTIFICATION.md`:

| quantity | manuscript inline | committed-data reproduction | same conclusion? |
|---|---|---|---|
| h1 deep-turnover R² | **0.98** [0.97, 1.00] | **0.89** [0.84, 0.96] | Yes — CERTIFIED (lower bound ≫ 0.50) |
| h2 deep-turnover R² | **0.34** [−0.89, 0.87] | **−0.24** [−0.79, 0.32] | Yes — NOT ESTABLISHED (CI ≤ 0.50) |
| h2 init R² | 0.78 | 0.80 | Yes |
| track survival | 36/36, 0 switches | 36/36, 0 switches | Yes (raw) |

**Cause.** The exact scoring/decoding script that produced the manuscript's inline `0.98` / `0.34` was run
inline in an earlier working session and was **never committed** to the repository. No standard grouped
leave-one-history-out ridge / kNN decode over the committed `tca_holdout_raw.pkl` features reproduces those
exact values; multiple documented decoder variants were tried (see the reproduction search log summarized in
`release/PORTABLE_DATA_AUDIT.md`). The committed data therefore supports the **qualitative certification**
robustly (every decoder gives h1 lower bound ≫ 0.50 and h2 ≤ 0.50), but not the **exact numbers** as printed.

**Consequence for the claims.** The load-bearing science is unaffected: h1 is certified through deep turnover
and h2 deep-turnover retention is not established under the committed-data reproduction, exactly as the V3
manuscript concludes. Only the specific point/CI values differ.

**Required before public release (operator decision — not done here, no retroactive edit of V3):**
- EITHER recover and commit the original inline scoring script so the manuscript's `0.98`/`0.34` are
  regenerable, OR update the manuscript's inline values (in a future V4, not by rewriting V3 history) to the
  committed-data reproduction values (`0.89`, `−0.24`) produced by the now-committed `reproduction/` package.
- The `reproduction/` package added here is fully specified and deterministic and should become the canonical
  source of these numbers going forward.
