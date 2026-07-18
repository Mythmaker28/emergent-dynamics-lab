# EXP-GT-CONTINUOUS-FINGERPRINT-02 — FINAL STRATEGIC REPORT

**Resolution-Certified Tail-Aware Continuous Fingerprint.**

# RESULT: **FAIL AT DEVELOPMENT. NOT FROZEN. PROSPECTIVE NOT RUN. THE SEALED SPLIT IS UNTOUCHED.**

---

## 1. Repository and provenance audit

Branch `main`, HEAD was **`daee515`**, tree clean, `git fsck --full` clean. Stale `.git/HEAD.lock` and
`.git/index.lock` remain undeletable on this mount; worked around with an out-of-tree index and direct ref writes.
Every run used a dedicated `PYTHONPYCACHEPREFIX`; every source file was `py_compile`d from disk before use.

**v00's six frozen files still hash-match their freeze manifest, byte-for-byte.** v01's artifacts are intact.
v02 is **additive**: `cfingerprint02.py`, `exp_gt_cfp02.py`, `docs/CFP02_*`. Nothing historical was rewritten.

**Cache provenance:** v02's acquisition cache is keyed on a hash of **every system parameter** plus the **arm, seed,
horizon and the instrument's own sha256**. v01 keyed on the system *name* alone and silently served a stale
re-parameterised system; that class of bug cannot recur here by construction.

## 2. Prospective seal audit — CONFIRMED SEALED

No `Q_*` (prospective) acquisition has ever existed on disk. No `EXP-GT-CFP01-PROSPECTIVE` directory was ever
created or committed. `git log --all -- 'results/EXP-GT-CFP01-PROSPECTIVE*'` is empty. **31 systems, 27 cases,
including a third-order cascade absent from development — untouched, and still available exactly once.**

## 3. The claim

> Under a frozen continuous measurement contract **whose temporal resolution is certified against its noise
> floor**, a causal-response fingerprint can classify decidable slow tails, abstain when the unseen remainder could
> change the verdict, and preserve continuity/difference discrimination on unseen continuous systems.

**NOT ESTABLISHED.** The battery is not admissible at any preregistered horizon.

## 4. THE RESULT — and it falsifies the fix I proposed at the end of v01

`k = 3.0` and the grid `{160, 240, 320, 480, 640}` were preregistered at `44121e9`, **before the sweep**.

| W | B_noise | k·B_noise | T4 B_signal | **ratio** |
|---|---|---|---|---|
| 160 | 5.85 | 17.56 | 5.19 | 0.89 |
| 240 | 3.67 | 11.00 | 9.33 | 2.55 |
| **320** | 3.49 | 10.47 | 8.92 | **2.56** |
| 480 | 2.64 | 7.92 | 3.12 | 1.18 |
| 640 | 3.36 | 10.08 | 0.96 | 0.29 |

**The ratio is NON-MONOTONE. It peaks at 2.56 and collapses. It never reaches 3.0.**

```
B_noise   improves as exp(-(W-84)/(3*TAU_MAX))   -- an e-fold every 3*TAU_MAX
B_signal  decays   as exp(-W/tau)                -- an e-fold every tau
```

> **The signal decays faster than the noise floor improves whenever `tau < 3*TAU_MAX` — which is true for
> essentially every in-contract system, because `TAU_MAX` is by definition the slowest one admitted.**
>
> **A longer window destroys the very evidence it was supposed to reveal.**

**At the end of v01 I proposed a longer observation window as the fix. That hypothesis is now falsified by
measurement.** It was the obvious move; it was mine; it is wrong. This is a **theorem about the tail-bound method**,
not a budget problem, and no grid escapes it.

**Second finding:** at long horizons the noise floor is **drift-limited, not white-noise-limited**. The white-noise
model predicts `B_noise -> 0.58` by W=320; **measured 3.49**, and it stops improving. The sub-block *means* wander
with the slow OU baseline while `sd`, derived by differencing, is **blind to drift by construction**. *The longer
you look, the more the baseline has wandered.* That is the floor no amount of observation lowers.

## 5. What v02 nevertheless achieves (W = 320, 13/15 development gates)

**D1 — the v00 burned cascade: `DECIDABLE_SETTLED` -> DIFFERENT** (`D_lo = 45.52` vs `r_sep = 22.89`). v00's fatal
case is fixed by bound, with no exception anywhere. Also: harmless slow tails classify (D4); non-settling and
out-of-contract systems abstain (D5, D5b); drift is refused, not read as an unresolved cause (D8); the null is
`DECIDABLE_SETTLED` + `INDISTINGUISHABLE` (D8b); gain, hidden state and extra causes separate (D9a/c/d); continuity
holds under equivalent implementations and unit change (D10); limited-access collisions return
`EQUIVALENCE_CLASS_ONLY` (D11); silent systems are refused.

**Failing: D9b (sign) and D9e (delayed second component)** — drift-driven false-unbounded blocks, the same root
cause as the floor.

## 6. Why "T4 abstains at W=320" is NOT a pass

T4 *does* return `INDETERMINATE` at the best horizon. But its bracket straddles because a block went **unbounded
from drift** — not because the bound resolved the remainder. The certificate proves the instrument **cannot see**
that remainder: `B = 8.92 < k·B_noise = 10.47`.

**A correct-by-accident verdict is not a qualification**, and accepting it would be exactly the self-deception this
programme exists to prevent.

## 7. Controls rebuilt — and one of them found a real bug in how v01 tested

**T7 / T8 must be evaluated on nested prefixes of a SINGLE long acquisition.** Attempting the naive check first
revealed *why*: **a prefix of a long episode is not a short episode with the same seed.** The engine draws the
measurement noise (T samples) and *then* the drift innovations from the same RNG stream, so the drift sequence
depends on episode length. Measured: `max|Z_long[:320] - Z_short(320)| = 6.48` **on a system compared with itself.**

**v01's T7 and T8 compared separately simulated noisy episodes as though they differed only in length. They
differed in their noise. Those controls were measuring the RNG, and their verdicts meant nothing.** v02 provides
`prefix()`, which slices one long acquisition and is therefore exact by construction.

## 8. Failure taxonomy

| # | classification | what it was |
|---|---|---|
| 1 | **SCOPE FAILURE — the fatal one** | the tail-bound's signal-to-noise ratio is **bounded above (~2.56) and non-monotone in W**. No horizon reaches the preregistered `k = 3.0`. Structural, not budgetary. |
| 2 | **noise-model failure** | `sd` is derived from the white noise by differencing and is **blind to drift**, so at long horizons the block-mean statistics are drift-dominated and the noise floor stops improving. |
| 3 | **normalization failure** | the out-of-contract bars are **not constants across horizons**. Carrying v01's `W=160` values across the grid made *every* pair — including the NULL — come back OUT OF CONTRACT. |
| 4 | **benchmark/control failure (inherited, now fixed)** | v01's T7/T8 varied the window by re-simulating, which changed the noise. They tested the RNG. |
| — | **provenance** (prevented) | cache now keyed on full parameters + instrument hash. |

## 9. Decision

The instrument failed **development**, on a gate fixed before any distribution was seen. **The sealed prospective
split was not touched and is not burned.** No more flexible estimator was invented after seeing the failure, as the
preregistered stop rule requires.

**The failure is structural.** It says the *tail-bound family* — bounding an unseen remainder from a decaying
envelope observed inside a window — has a resolution ceiling that no observation horizon can raise. A successor
must change the **method**, not the budget. Candidate directions, none attempted here: a drift-aware noise model so
the floor is not drift-limited; a decision rule that does not require resolving the remainder (e.g. accepting a
declared error rate rather than a bound); or abandoning near-boundary decidability as a goal and reporting the gap
honestly.

**A note on transfer, since it bears on the droplet programme:** the certified horizon that *would* be needed does
not exist, so no statement about droplet temporal resolution can be made from this work — but the drift-limited
floor is a warning that longer droplet observation will not, by itself, buy tail certainty either.

## 10. Branch, commits, files, tests

Branch **`main`**. Starting commit **`daee515`**. Protocol/preregistration commit **`44121e9`**.
Files added: `edlab/identity/cfingerprint02.py`, `edlab/experiments/exp_gt_cfp02.py`,
`docs/CFP02_PROTOCOL.md`, `docs/CFP02_RESOLUTION_CERTIFICATE.md`, `docs/CFP02_FINAL_REPORT.md`,
`results/EXP-GT-CFP02-DEV/`. **No v00 or v01 file was modified.** v00's freeze manifest still verifies.
v00 tests: 11/11 pass. **No freeze manifest was written — v02 never earned one.**
No droplet experiment. `beta`, `D_int` and the droplet equations untouched.

---

**`EXP-GT-CONTINUOUS-FINGERPRINT-02: FAIL`**

**`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT: NOT AUTHORIZED`**

**`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`**

**`EXP-SC-01 remains BLOCKED.`**
