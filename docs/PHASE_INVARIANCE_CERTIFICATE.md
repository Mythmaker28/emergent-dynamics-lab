# PHASE_INVARIANCE_CERTIFICATE.md

**Status: GRANTED (development).** EXP-GT-ACERT2, run `results/EXP-GT-ACERT2-20260714-001`.

## What went wrong (D-056)

V2's delay estimator struck at phases **(0, 15, 30, 45)** and took the earliest onset.
V2's development phase-null tested phases **(0, 15, 30, 45)**.

**The same four numbers.** The estimator's sampling grid and the null's test grid coincided, so the null was
*structurally incapable* of firing. It reported a delay deviation of **zero** — and it was right, and
uninformative, and could not have known. On held-out phases (7, 22, 37, 52) every delay moved **214 → 222** and
`A` reported DIFFERENT on a **pure phase shift**.

**A null drawn from the estimator's own free choices measures the estimator's agreement with itself.**

## The repair is structural, not procedural

The fix is not a better null. **It is an estimator with no free phase parameter.**

`blind_a3` infers the fundamental period `T` from the raw trajectory (the *smallest* exact period, so a harmonic
can never be reported), and strikes at **every phase `0 … T−1`**. `assert_exhaustive_phases` refuses to run on a
subset. **An estimator with nothing to select cannot have its null selected to match it.**

## Invariance is now a theorem, not a hope

Settling a circuit `φ` extra steps and then striking at phase `p` is identical to striking the unshifted circuit
at phase `(φ + p) mod T`. Because V3 strikes at **all** `p ∈ [0, T)`, the *set* of strike phases is the whole
cycle either way. A global phase shift therefore **permutes the phase labels and nothing else**, so the *multiset*
of per-phase responses is identical.

Every summary V3 builds — effect probability, median, quartiles, min, max — is a function of that multiset, and is
therefore **exactly invariant**. Not approximately. Exactly.

## Measured

| | |
|---|---|
| inferred fundamental period | **T = 60** (harmonics resolved by construction: the *smallest* exact period) |
| strike schedule | **EXHAUSTIVE, 0…59** |
| null phase origins | **drawn from a seed in `gt_nulls.py`, which imports nothing from the observer** |
| null manifest hash | `0f4cfb50c963255d` (frozen before evaluation) |
| phases checked | 9 (phase 0 + 8 independently-drawn origins: 1, 4, 6, 8, 9, 10, 11, 14) |
| **A_TOPO under phase shift** | **INVARIANT** |
| **A_TAU under phase shift** | **INVARIANT** |
| **G under phase shift** | **INVARIANT** |
| **max median-delay deviation** | **0.0** |
| **⇒ DERIVED A_TAU TOLERANCE** | **0.0** |

`assert_null_independence` is executable and has teeth: given the **V2** schedule (4 of 60 phases) it **raises**,
naming the loophole. Given the V3 schedule it passes.

## The general lesson, which is worth more than the bug

It is not enough for a null to be a case the instrument *might* fail.

**The null must be drawn from a distribution that the instrument's own free choices did not help select.**

Where that independence cannot be guaranteed procedurally, **remove the free choice**.
