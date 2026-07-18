# EXP-GT-CONTINUOUS-FINGERPRINT-01 — FINAL STRATEGIC REPORT

**Tail-Aware Continuous Causal Fingerprint.**

# RESULT: **FAIL (development). NOT FROZEN. PROSPECTIVE NOT RUN. THE HOLD-OUT IS PRESERVED.**

---

## 1. Repository integrity audit

`git status` clean · `git log` HEAD **`c222259`** on branch **`main`** · `git fsck --full` **clean** (no errors;
dangling objects only). Stale `.git/HEAD.lock` and `.git/index.lock` persist and are **undeletable on this mount**;
worked around with an out-of-tree index and direct ref writes. Every run used a dedicated `PYTHONPYCACHEPREFIX` and
every source file was `py_compile`d from disk before use.

**All six v00 frozen files still hash-match the v00 freeze manifest**, byte-for-byte. v01 is **additive**: new
files only (`tails.py`, `manifests01.py`, `cfingerprint01.py`, `exp_gt_cfp01*.py`). **v00's retirement record
survives intact**, which matters, because it is the evidence that v00 failed honestly.

## 2. Version 00 retirement reference

`EXP-GT-CONTINUOUS-FINGERPRINT-00: FAIL — RETIRED` (D-074, commit `c222259`). Hold-out **burned**. Its guard was
**not** changed, its prospective split was **not** rerun, its freeze and certificates were **not** overwritten, and
52/54 was **not** reinterpreted as a PASS.

## 3. The claim, and what happened to it

> A fixed continuous-response fingerprint can **distinguish sufficiently observed slow relaxation from genuinely
> unresolved in-flight response**, while preserving continuity, difference, abstention and repertoire-relative
> equivalence.

**NOT ESTABLISHED.** The instrument fails the one control that separates a principled tail guard from a
threshold-raising hack.

## 4. What v01 got right — and it is not nothing

| | |
|---|---|
| **T1 — the burned case, by BOUND and not by exception** | `R_cascade_burned` (P_cascade's exact parameters): `D_lo = 41.9` against `r_sep = 22.1`, tail `DECIDABLE_SLOW_TAIL` -> **DIFFERENT**. **v00's exact failure is fixed, and fixed for the right reason:** the bound *proves* the verdict cannot change. There is no hard-coded exception anywhere in the guard. |
| **T2 — genuinely unresolved** | a response that never settles (undamped oscillator) -> `INDETERMINATE_IN_FLIGHT`. |
| **T3 — slow but harmless** | strong long tail + a gain difference that dwarfs it -> bracket `[152.8, 160.2]` -> **DIFFERENT**, `DECIDABLE_SLOW_TAIL`. |
| **T6 — noise is not an unresolved cause** | the null is `DECIDABLE_SETTLED` / `INDISTINGUISHABLE`; the drifty system is refused as nonstationary. |
| **T9 — guard removed** | a non-settling system is handed a confident **DIFFERENT**. The guard is load-bearing. |
| **T10 — v00's guard restored** | it flags 12/24 rows of the burned case in flight (frac 0.50 > 0.25) and **abstains** — reproducing v00's death exactly, while v01 says DIFFERENT. |
| preserved core | unit invariance, gain/sign sensitivity, hidden state, false sameness (`EQUIVALENCE_CLASS_ONLY`), coverage, responsiveness, the common-channel refusal — all re-qualified on the new split. |

**Development matrix: 52 / 54. Controls: 6 / 10.**

## 5. Why it fails: the resolution floor — measured, not inferred

The bound's remaining-envelope statistic `B`, measured on **288 noise-only blocks** (systems that *cannot*
respond): mean **3.76**, q99.9 **7.39**, **max 7.40**. So `TAIL_NOISE = 9.0`.

**That number is not merely a threshold. It is the smallest remainder this bound can see.**

**T4 — the decisive control** — is a pair built so that a real **~10% of its difference energy lies beyond the
window** (confirmed by the privileged path, independently of the instrument). Its measured remaining envelope is
**8.25**. That is **inside the floor**. The bound cannot see it, calls the tail `DECIDABLE_SETTLED`, and returns a
**confident DIFFERENT (29.26)** on a pair whose answer is still partly outside the window.

**This is version 00's error, in the opposite direction.** v00 abstained when it should have spoken; v01 speaks
when it should abstain. T4 exists precisely because *raising v00's 5% threshold would get it wrong* — and a bound
that cannot resolve T4 is, on this case, a threshold-raising hack with extra arithmetic.

**Root cause:** the tail region is 76 samples against a noise-limited sub-block mean. **The fix is more tail
leverage — a longer observation window — which changes the probe battery and therefore constitutes a new, broader
instrument.** It is **not** made here.

## 6. The second limit: the contract check has bounded power

The out-of-contract test compares a per-sub-block decay factor against `rho_max = 0.732`. A system at `tau = 130` —
well outside the contract — decays at **0.825**. The gap is 0.09 per sub-block against comparable noise.

> **The check reliably detects `tau` above roughly `2.5 x TAU_MAX`. In the band `(TAU_MAX, ~2.5*TAU_MAX)` a system
> may be silently accepted as in-contract, and the bound — which ASSUMES `tau <= TAU_MAX` — is then TOO TIGHT.**

Even at `tau = 300` the check fails to fire in the **limited** arm (W-D-20), because its power scales with the tail
level and the limited repertoire does not drive the system hard enough. **This is a soundness limit, and it is
declared rather than left to be discovered.**

## 7. Failure taxonomy

| # | classification | what it was | what it would have falsely concluded |
|---|---|---|---|
| 1 | **observer failure — inherited** | I called `F0.admit()` directly and it **silently re-imposed version 00's in-flight guard**. The bound proved `D_lo = 57.7` vs `r_sep = 22.1` for the burned case and the dead guard refused it anyway. **Six of eight** initial development failures, T1 among them. | that the new bound did not work, when it was never being consulted. **Inheriting a core means inheriting its bugs unless you NAME the one you are replacing.** |
| 2 | **response-representation failure** | the bound estimated the decay **rate** from a ratio of two noisy block means. On a quiet tail both are noise, the ratio is a ratio of noises, and it exceeded the non-convergence bar at random. | that the NULL — a system against **itself** — was out of contract and unbounded. It read its own estimator's variance as the world refusing to relax. Fixed by never estimating the rate: the contract **declares** it, and the check merely **verifies** it. |
| 3 | **noise-model failure** | the noise was **subtracted** from the decrement (`d2 - 4sd`) when bounding the remainder. | **the fatal direction.** For T4 the decrement (2.17) is barely above its noise (0.6); subtracting drove it to zero, the remaining movement to zero, and the instrument concluded "settled, remainder below the noise floor" about a level of **22** that must eventually reach zero. **When the decay is too slow to resolve, the honest inference is that the remainder is LARGE, not that it is zero.** |
| 4 | **normalization failure** | one constant (6 sigma) used for both the out-of-contract **check** and the remainder **bound**. | a 6-sigma bound on a 0.6-noise decrement inflates the remainder to ~15 units **on pure noise** — drowning the ~20-unit remainders it exists to find. A check and a bound want different confidence levels. |
| 5 | **benchmark-label failure** | `TAU_MAX = 40` against a 160-sample window. | that the three-way distinction worked, when **every admissible system had already settled** (remainder 0.02–0.13%) and `DECIDABLE_SLOW_TAIL` could never occur. **A benchmark cannot exercise a boundary it has defined out of existence.** Caught before any instrument code was written. |
| 6 | **provenance failure** | the acquisition cache is keyed on system **name**; `V_slow_oos` was re-parameterised and its stale entry was silently reused. | results computed from a system that no longer exists. Same class as the stale `.pyc` of v00. Fixed by a new cache namespace. |
| 7 | **SCOPE FAILURE — the fatal one** | the bound's **resolution floor** (9.0) exceeds the remainder it must detect (8.25) on the decisive control. | that a pair whose answer is still outside the window has been decided. |
| — | **non-identifiability** (a limit, not a defect) | `tau` in `(TAU_MAX, ~2.5*TAU_MAX)` is not verifiable from a 76-sample tail. | — |

## 8. Decision

**The prospective split was NOT run and is NOT burned.**

The instrument failed on **development**. Freezing it and spending the hold-out to confirm a defect I have already
measured would destroy an asset for no information. The identified fix — **a longer observation window**, giving
the tail region more leverage against the noise floor — is a **battery change** and therefore a **new instrument**,
which requires its own development and is **not** attempted here.

`EXP-GT-CONTINUOUS-FINGERPRINT-01` is **RETIRED at development**. Its artifacts are preserved. Its prospective
split remains **sealed and available** to a successor.

## 9. What was demonstrated / not demonstrated

**Demonstrated.** That version 00's specific defect is fixable **for the right reason**: a bound on the eventual
distance classifies the burned case (T1) because it *proves* the verdict cannot change, with no exception coded
anywhere. That slow tails, ringing tails, non-settling responses, noise and drift are separable in principle. That
a single unbounded probe must not be outvoted by well-behaved ones.

**Not demonstrated.** The claim. The three-way distinction fails at its own resolution floor (T4). The
out-of-contract check's soundness in the band `(TAU_MAX, 2.5*TAU_MAX)`. Nothing about droplets, partitions, or
identity.

## 10. Branch, commits, tests, hashes

Branch **`main`**. Starting commit **`c222259`**. Split committed at **`fb449b2`** (before instrument changes).
Files added: `edlab/substrates/ctrans/tails.py`, `edlab/substrates/ctrans/manifests01.py`,
`edlab/identity/cfingerprint01.py`, `edlab/experiments/exp_gt_cfp01.py`,
`edlab/experiments/exp_gt_cfp01_controls.py`, `docs/CFP01_*`, `results/EXP-GT-CFP01-DEV/`.
**No v00 file was modified.** v00 freeze manifest still verifies. Tests: v00's 11/11 still pass.
No droplet experiment. `beta`, `D_int` and the droplet equations untouched.

---

**`EXP-GT-CONTINUOUS-FINGERPRINT-01: FAIL`**

**`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT: NOT AUTHORIZED`**

**`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`**

**`EXP-SC-01 remains BLOCKED.`**
