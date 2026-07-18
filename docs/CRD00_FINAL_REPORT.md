# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00 — FINAL REPORT

**Factorized Causal Response Decomposition.**

# RESULT: **FAIL AT DEVELOPMENT (19/20).** Not frozen. The new prospective split was **not touched**.

---

## 1. Integrity audit

Branch `main`, HEAD was `50d58b8`, tree clean, `git fsck --full` clean. v00's six frozen files still hash-match
byte-for-byte. The four historical verdicts stand (v00 FAIL · v01 FAIL · v02 FAIL · v03 BENCHMARK_INVALID ·
**BRANCH CLOSED — NO V04**), none of them has a freeze manifest, and the **historical sealed hold-out has still
never been generated**. This programme is additive: `decomp.py`, `manifests_crd.py`, `crdecomp.py`, `exp_gt_crd.py`.

## 2. What was built

A **factorized** profile — `R = (E_trans, P_inf, A_peak, L_onset, T_recovery, C, U)` — with **no composite**, no
weighting and no scalar ranking. Every case is `base` vs `base + one extra parallel path`, so the accessible
difference is **exactly that path's response** and ground truth is a design parameter rather than an accident.

## 3. THE CENTRAL REPAIR WORKS — and the must-fail control proves it

Nested prefixes of **one** acquisition (same noise, same probes, only the window truncated):

| W | OLD scalar `D_W` | ratio | **NEW `E_trans` (integral)** | `A_peak` | `P_inf` |
|---|---|---|---|---|---|
| 160 | 144.04 | 1.000 | 3.220e6 | 426.3 | 0 |
| 240 | 117.61 | 0.817 | 3.303e6 | 426.3 | 0 |
| 320 | 101.86 | 0.707 | 3.324e6 | 426.3 | 0 |
| 480 | **83.17** | **0.577** | **3.365e6** | 426.3 | 0 |

`sqrt(160/480) = 0.577`. **The old scalar dilutes at exactly the normalization rate. The integral converges
upward and holds. The persistent axis correctly stays at zero for a transient with an identical asymptote.**

## 4. The dissociation controls (G5) — the whole reason the old scalar had to die

A single leaky path **cannot** dissociate peak from energy: measured, its shape factor `E/A^2` stays between 18 and
41 across `Tx` from 1 to 64, and the best equal-energy peak ratio achievable was **1.36** — a rounding error, not a
control. **My first attempt at these controls therefore failed, and it failed silently.** Peak and energy only come
apart when the **shape** comes apart (high-pass SPIKE, `E/A^2 = 6.9`, versus cascade BROAD, `E/A^2 = 56.1`):

| control (exact by construction on privileged traces) | measured on the instrument |
|---|---|
| **EQUAL ENERGY** | energy ratio **0.84**, **PEAK RATIO 3.09x** — the peak axis separates |
| **EQUAL PEAK** | peak ratio **0.90**, **ENERGY RATIO 7.04x** — the energy axis separates |

**The two quantities the old scalar conflated are now measured on separate axes, and each separates on its own.**

## 5. Development matrix: 19 / 20 (accuracy-checked against privileged truth)

Passing: the null · pure transient (`P_inf = 0`) · pure persistent (`P = -193.2` vs true `-203.6`) · latency ·
both dissociation controls · gain · sign · **hidden state** (`P = -339.6` vs true `348.5`) · **limited-access
collision -> exact zeros, `EQUIVALENCE_CLASS_ONLY`** · equivalent implementations · **unit change -> exact zeros** ·
solver refinement · **drift-only -> zero causal components on every axis** · slow response without drift ·
silent / noisy / low-coverage all refused for their declared reasons. Estimated energies land within **0.68–1.21x**
of privileged truth.

## 6. WHAT FAILS: Z-17 — a slow causal response under heavy drift

The instrument reports `E_trans = 3.05e6` against a privileged truth of `4.30e5` (**overstated 7.1x**) and quotes
`A_peak = 422.7` when the true causal peak is ~97. **It silently calls the drift a response**, which is exactly what
gate G8 forbids, and it does **not** abstain.

**Diagnosis, measured:**

> The matched sham has the **same variance** as the causal trace's drift but is an **independent realization**.
> Subtracting its **energy** is unbiased *in expectation* and useless *per pair*: `E_raw` and `E_sham` fluctuate
> independently, and their difference carries an error of the same order as the thing being removed.
>
> **A sham can CALIBRATE A BAND. It cannot SUBTRACT A REALIZATION IT NEVER SAW.**

This is why the drift-only control (Z-15) passes — there a *band* is all that is needed, and it works perfectly —
while Z-17, which needs an actual *subtraction*, does not.

## 7. Two defects found and named along the way

1. **The inherited `BASELINE_MAX` refusal pre-empted the new machinery.** Importing the old admission wholesale
   re-imposed the old fingerprint's "refuse anything that drifts" rule and threw away the sham channel this
   programme exists to test — **the same mistake v01 made** when it inherited v00's dead in-flight guard.
   *Inheriting a core means inheriting its assumptions unless you name the one you are replacing.* Named, removed,
   and the cost declared: a drifting system is now admitted and must be defended on-axis.
2. **`max`-over-blocks is a verdict rule, not an estimator.** The FOR-ALL aggregation inherited from the fingerprint
   is right for *"is there any probe on which they differ?"* and wrong for *"how much?"* — over 32 blocks it selects
   the block where independent drift realizations conspire. Fixed: **median over the four carrier phases**
   (replicates), **max over the eight probes** (distinct interventions). It was not enough to save Z-17.

## 8. Decision

**FAIL AT DEVELOPMENT.** Per the protocol: **the new prospective split is NOT touched** and remains sealed. No
freeze manifest — this version never earned one. The historical hold-out likewise remains untouched.

**What a successor must change is the acquisition, not the estimator.** To *subtract* drift rather than merely bound
it, the sham must share the drift realization with the causal episode — interleaved or common-mode acquisition —
not merely its distribution. That is an **acquisition-contract** change, and it is not attempted here.

## 9. Branch, commits, hashes, tests

Branch **`main`**. Starting commit **`50d58b8`**. Split/protocol commit **`609e12d`**. **No freeze commit.**
Files added: `edlab/substrates/ctrans/decomp.py`, `edlab/substrates/ctrans/manifests_crd.py`,
`edlab/identity/crdecomp.py`, `edlab/experiments/exp_gt_crd.py`, `docs/CRD00_PROTOCOL.md`,
`docs/CRD00_FINAL_REPORT.md`, `results/EXP-GT-CRD00-DEV/`. **No historical file modified.** v00 tests 11/11.
No droplet experiment. `beta`, `D_int` and the droplet equations untouched.

---

**`EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00: FAIL`**

**`SC-PILOT-RESPONSE-DECOMPOSITION-PREFLIGHT: NOT AUTHORIZED`**

**`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`**

**`EXP-SC-01 remains BLOCKED.`**
