# RESOLUTION CERTIFICATE — EXP-GT-CONTINUOUS-FINGERPRINT-02

**Development data only. `k = 3.0` and the horizon grid were preregistered at commit `44121e9`, before any sweep.**

## The mandated question

> *What is the smallest decision-relevant unseen remainder that this battery can reliably detect?*

**Answer, per horizon:** `k * B_noise(W) = 3 * B_noise(W)`.

| W | L | r_cont | r_sep | **B_noise** | **k·B_noise** | **T4 B_signal** | **ratio** | T4 decision-relevant? (privileged) | admissible |
|---|---|---|---|---|---|---|---|---|---|
| 160 | 25 | 6.91 | 20.73 | 5.85 | 17.56 | 5.19 | **0.89** | yes (41.1 -> 14.4) | **NO** |
| 240 | 52 | 7.04 | 21.13 | 3.67 | 11.00 | 9.33 | **2.55** | yes (34.6 -> 14.4) | **NO** |
| **320** | 78 | 7.63 | 22.89 | **3.49** | **10.47** | **8.92** | **2.56** | yes (30.2 -> 14.4) | **NO** |
| 480 | 132 | 8.18 | 24.54 | 2.64 | 7.92 | 3.12 | **1.18** | yes (24.7 -> 14.4) | **NO** |
| 640 | 185 | 8.54 | 25.63 | 3.36 | 10.08 | 0.96 | **0.29** | no (21.4 -> 14.4, same side) | **NO** |

**`B_critical(W) >= k * B_noise(W)` FAILS AT EVERY HORIZON ON THE PREREGISTERED GRID.** Peak ratio **2.56**, against
a bar of **3.0** fixed before the sweep. **The bar is not moved.**

---

# THE STRUCTURAL RESULT — and it falsifies the fix v01 proposed

**A longer window does not buy resolution. The ratio is NON-MONOTONE in `W`: it peaks near `W = 240–320` and then
collapses.** Measured (0.89 · 2.55 · **2.56** · 1.18 · 0.29) and reproduced analytically.

```
B_noise(W)   improves as   exp(-L/TAU_MAX) = exp(-(W - 84)/(3*TAU_MAX))   -- an e-fold every  3*TAU_MAX = 240
B_signal(W)  decays  as    exp(-W/tau)                                    -- an e-fold every  tau
```

> **The signal decays faster than the noise floor improves whenever `tau < 3 * TAU_MAX`** — which is true for
> *essentially every in-contract system*, since `TAU_MAX` is by definition the slowest one admitted.
>
> **The remainder you are trying to detect dies faster than your ability to detect it grows. Lengthening the
> window destroys the very evidence it was supposed to reveal.**

This is a **theorem about the tail-bound method**, not a budget problem, and no horizon on any grid escapes it.
At the end of v01 I proposed a longer observation window as the fix. **That hypothesis is now falsified by
measurement.** It was the obvious move, it was mine, and it is wrong.

## A second finding: at long horizons the noise floor is DRIFT-limited, not white-noise-limited

The analytic white-noise model predicts `B_noise` should fall to ~0.58 by `W = 320`. **Measured: 3.49.** It floors
out near 3 and stops improving.

Because the sub-block **means** wander with the slow OU baseline, while `sd` is derived from the **white** noise by
differencing and is therefore *blind to drift by construction*. The level statistic's noise-only maximum grows
`2.07 -> 7.20 -> 8.00 -> 15.11 -> 26.95` across the grid.

Two consequences, both recorded:

1. **The out-of-contract bars are not constants.** Carrying v01's `W=160` values across the grid made *every* pair
   — **including the NULL, a system compared with itself** — come back `OUT OF CONTRACT`. Bars must be
   recalibrated per horizon: `LVL_K = {3, 9, 10, 19, 34}`, `RIP_K = {3, 4, 5, 5, 6}`.
2. **Drift sets a floor that more observation cannot lower.** The longer you look, the more the baseline has
   wandered. This is *why* `B_noise` stops improving — and it is the deeper reason the ratio cannot be rescued.

## What the instrument nevertheless achieves at the best horizon (W = 320)

**13 / 15 development gates**, with per-horizon bars:

**D1 — the v00 burned cascade -> `DECIDABLE_SETTLED` -> DIFFERENT** (`D_lo = 45.52` vs `r_sep = 22.89`). v00's fatal
case is fixed, by bound, with no exception. · D4 harmless slow tail classifies · D5 non-settling abstains · D5b
out-of-contract abstains · D8 drift refused · D8b the null is `DECIDABLE_SETTLED` + `INDISTINGUISHABLE` · D9a gain ·
D9c hidden state · D9d extra cause · D10 continuity (equivalent implementations, unit change) · D11 limited-access
collision -> `EQUIVALENCE_CLASS_ONLY` · silent systems refused.

**Failing:** D9b (sign) and D9e (delayed second component) return `INDETERMINATE_IN_FLIGHT` — residual
**drift-driven false-unbounded** blocks, the same root cause as above.

## The verdict this certificate compels

**T4 does abstain at `W = 320` — but for the WRONG REASON.** Its bracket straddles because a block went unbounded
from *drift*, not because the bound resolved the remainder. The certificate proves the instrument **cannot see**
that remainder: `B = 8.92 < k * B_noise = 10.47`.

**A correct-by-accident verdict is not a qualification.** The battery is **NOT ADMISSIBLE** at any preregistered
horizon.

**`EXP-GT-CONTINUOUS-FINGERPRINT-02: FAIL AT DEVELOPMENT.`**

Per the preregistered stop rule: **no more flexible estimator may be invented after seeing this failure**, and the
sealed prospective split is **not touched**.
