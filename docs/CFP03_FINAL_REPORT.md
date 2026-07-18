# EXP-GT-CONTINUOUS-FINGERPRINT-03 — FINAL REPORT

**Drift-Aware Risk-Calibrated Continuous Causal Fingerprint.**

# RESULT: **BENCHMARK_INVALID** — the target quantity is ill-posed. Detected **before any predictor was fitted**.

The calibration set was never touched. The sealed prospective split was never touched.

---

## 1. Integrity audit

Branch `main`, HEAD was `05aaa7f`, tree clean, `git fsck --full` clean. v00's six frozen files still hash-match,
byte-for-byte. **Sealed split confirmed untouched**: no `Q_*` acquisition has ever existed on disk or in git
history; no prospective-results directory was ever created or committed. Every run used a fresh
`PYTHONPYCACHEPREFIX`, sources were `py_compile`d from disk, and the v03 cache is content-addressed on system
parameters + arm + seed + horizon + **battery hash** + **instrument hash**.

## 2. What was built, and what stopped it

Preregistered at **`cc39c6c`** *before any fitting*: `alpha = 0.05` marginal coverage; a disjoint **FIT (14) /
CALIBRATION (14) / CHALLENGE (22)** partition; a **matched sham channel** (baseline episodes only, differing solely
in the absence of intervention amplitude) to measure the drift scale that v02's differenced `sd` was blind to; a
ridge predictor on label-free features; split-conformal intervals; radii by the unchanged rule from **fit-set nulls
only** (`r_cont = 7.96`, `r_sep = 23.88`).

The sham channel works — it returns a per-system drift scale of **1.264** noise units, precisely the quantity that
set v02's floor.

**Then the pre-fit truth check (gate G11) failed, and it failed for a reason that invalidates the question.**

## 3. THE FINDING — the fingerprint distance is not a property of a pair of systems

`D_inf` — the "eventual distance", measured on **noise-free** traces at `W_INF = 1400` — was compared against
radii calibrated from `D_W` at `W = 320`. They are **not commensurate**, and the reason is structural:

| pair (noise-free, same metric, only the window changes) | W=320 | W=1400 | ratio |
|---|---|---|---|
| v00 burned cascade | 47.35 | 22.64 | **0.478** |
| v01 T4 | 30.18 | 14.45 | **0.479** |
| gain x2 | 115.32 | 55.13 | **0.478** |
| sign inversion | 230.64 | 110.27 | **0.478** |
| **hidden state (PERSISTENT difference)** | 346.43 | 348.01 | **1.005** |

`sqrt(320/1400) = 0.478`.

> **The RMS-over-window fingerprint distance DILUTES AT EXACTLY THE NORMALIZATION RATE for any TRANSIENT
> difference, and tends to ZERO as the window grows. The persistent (hidden-state) pair does not dilute at all.
> That control proves the effect is the METRIC, not the systems.**

**Therefore "the distance at a longer window" is not a fact about the pair. It is a fact about the pair AND the
window.** Asking an instrument to predict `D_inf` is asking it to predict an artifact of its own normalization —
and for any transient difference the honest answer is *zero*, which is absurd.

## 4. Why this invalidates the benchmark rather than merely inconveniencing it

The privileged truth path places the **v00 burned cascade at `D_inf = 22.64`, BELOW the preregistered
`r_sep = 23.88` — inside the ambiguity gap.** Gate **G5** requires that case to *classify*. Gate **G2** forbids a
confident wrong verdict. **Both cannot hold.** Construction truth and privileged truth **disagree**, and **G11
forbids scoring a benchmark whose truth paths disagree.**

The radii were preregistered and are **not moved**. The target was preregistered and is **not redefined after
seeing that it fails**. Per the protocol's own rule: **`BENCHMARK_INVALID`. Do not score.**

## 5. What this says about v00, v01 and v02 — retrospectively, and it is the real result

**For a FIXED observation window, the instrument sees everything it will ever see. There is no "unseen
remainder" affecting `D_W`. The only uncertainty in `D_W` is MEASUREMENT NOISE.**

The entire tail-guard programme — v00's in-flight guard, v01's tail-uncertainty bound, v02's resolution
certificate — was built to protect a verdict against a quantity ("the distance at a longer window") that **shrinks
toward zero for any transient difference as a pure consequence of the RMS normalization**.

* **v00** abstained on a decidable cascade. Its guard asked "is the signal still moving?" — a question whose answer
  is irrelevant to `D_W`, which the instrument had already measured completely.
* **v01** tried to bound the remainder and could not see it through the noise.
* **v02** proved no horizon can: the ratio is bounded above (~2.56), non-monotone, and the floor is drift-limited.
* **v03** now shows *why every one of them was hard*: **the thing they were all trying to bound is not
  well-defined.**

**The one legitimate truncation concern is PERSISTENCE** — a probe leaving a permanent mark. That difference does
**not** dilute (ratio 1.005), and it is already captured at any window that exceeds the settling time plus the
declared delay horizon. **v00's original persistence logic was addressing the real problem; its in-flight guard was
addressing a phantom.**

## 6. What would have to change for a v04 — which is NOT authorized

A well-posed target requires a **window-invariant** discrepancy functional: e.g. an *integral* of the squared
difference rather than a *mean*, or a normalization by the response energy rather than the window length. That is a
change to the **fingerprint metric itself** — the one component preserved unchanged since v00 — and therefore a new
programme, not a new version.

## 7. Deliverables and status

Committed: integrity audit · v00–v02 retirement registry · v03 preregistration (`cc39c6c`) · fit/cal/challenge
partition (verified disjoint) · drift-and-noise contract · sham specification · privileged `D_inf` path ·
`docs/CFP03_SYNTHESIS.md` (the methodological synthesis of v00–v03).
**No freeze manifest** — v03 never earned one. **No calibration was performed** — the calibration set is untouched.
**No prospective acquisition exists.**

## 8. Branch, commits, hashes, tests

Branch **`main`**. Starting commit **`05aaa7f`**. Preregistration commit **`cc39c6c`**. **No freeze commit.**
Files added: `edlab/identity/cfingerprint03.py`, `edlab/experiments/exp_gt_cfp03.py`,
`edlab/substrates/ctrans/manifests03.py`, `docs/CFP03_PROTOCOL.md`, `docs/CFP03_FINAL_REPORT.md`,
`docs/CFP03_SYNTHESIS.md`, `results/EXP-GT-CFP03-DEV/`. **No v00/v01/v02 file modified.** v00 tests 11/11.
No droplet experiment. `beta`, `D_int` and the droplet equations untouched.

---

**`EXP-GT-CONTINUOUS-FINGERPRINT-03: BENCHMARK_INVALID`**

**`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT: NOT AUTHORIZED`**

**`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`**

**`EXP-SC-01 remains BLOCKED.`**

**`CONTINUOUS-FINGERPRINT BRANCH CLOSED — NO V04`**
