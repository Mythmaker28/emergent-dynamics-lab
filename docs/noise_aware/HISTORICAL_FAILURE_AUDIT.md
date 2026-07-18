# HISTORICAL FAILURE AUDIT — the burned large hold-out

Deliverable 1. Independent re-derivation of why the frozen sign-safe instrument
(`consolidation/signsafe.py`, frozen at `09016d7`) failed the preregistered N=2000
distributional hold-out (`a76f8a7`, executed at `d71502f`).

## 1. What was verified independently (from the committed HEAD tree)

* HEAD = `d71502f`; hold-out preregistration = `a76f8a7`; instrument freeze = `09016d7`.
* Repository integrity: `git fsck --full` reports only *dangling* objects (normal after resets); no
  missing/corrupt objects.
* Freeze manifests: 36/38 pinned file hashes reproduce bit-for-bit from HEAD. The 2 mismatches are in the
  older `SOURCE_TRANSDUCER` freeze (`boolnet/circuits.py`, `boolnet/evaluator.py`); those files were
  legitimately re-edited at `5bd0c7f` for a later experiment and the pinned version still exists at
  `0f12dd6` — benign evolution of a shared file, not tampering. The sign-safe instrument and all
  droplet/`ctrans` physics are bit-intact.
* Working tree is NOT clean: the index carried a staged mass-deletion of the entire prior corpus
  (recoverable; no data lost). The prior "working tree clean" report is therefore incorrect.

## 2. The exact defect

`signsafe.identify()` contains an operational "null gate" that is NOT part of the proved T6 algebra:

```python
if np.median(amp) < 2.0*np.median(nul):
    return POINT, (0.0, 0.0), rep      # emits the EXACT set {0}
```

`amp` is the per-channel windowed standard deviation. At low SNR the response fails to clear the 2x-noise
threshold, so the instrument returns the **exact** identified set `{0}`, excluding any true nonzero
response. This is the logical error:

> failure to detect a response  ⇏  proof that the response is zero.

## 3. Quantified failure (recomputed from the committed raw rows)

`consolidation/HOLDOUT_RESULTS.json`, ORACLE arm, emitted = 1333:

| SNR | invalid / emitted | mechanism |
|----:|------------------:|-----------|
| 5   | 542 / 546 | null-gate `{0}` on genuine low-SNR responses |
| 15  | 20 / 406  | over-confident POINT (non-null) |
| 50  | 24 / 381  | over-confident POINT (non-null) |
| all | **586 / 1333** | every invalid emission was `POINT` |

BLIND arm: 541/541 emitted sets invalid, all at SNR=5, all `{0}`.

**Provenance discrepancy (new finding).** The saved `summary.oracle.invalid = 541` disagrees with the
saved rows, which contain **586** invalid emissions. The in-memory summary undercounted via a
`np.bool_ is False` identity bug (numpy's `False` is not Python's `False` singleton). The headline
"541/1333" therefore *understated* the recorded failure; the reproducible figure is 586/1333 (≈44%).

**Secondary failure mode.** 44 of the 586 invalids are at SNR 15/50 and are non-null wrong points: even
setting the null-gate aside, the point-emission logic under oracle contracts is not fully safe.

## 4. Classification

* Operational observer failure: **YES** (the null gate).
* Statistical decision failure: **YES** (a threshold crossing treated as a proof of zero; no interval).
* Overconfident null assertion: **YES** (primary).
* Distributional scope failure: **YES** (the frozen dev battery lacked low-SNR nonzero mass; SNR=5 was
  under-represented at development and dominated the failure).

It is **NOT**: a theorem failure (the T6 algebra is untouched and correct), a set-identification algebra
failure, a benchmark-label failure, or a droplet-physics failure.

## 5. Consequence for the new instrument

The new instrument (`noise_aware/nasi.py`) removes every data-driven route to `{0}`. Exact zero is
reachable ONLY through an independent structural null contract. Non-detection is represented as an
identified SET (zero-compatible, below-detection, or insufficient-SNR), never as the point `{0}`.
See `NOISE_AWARE_SPEC.md`.
