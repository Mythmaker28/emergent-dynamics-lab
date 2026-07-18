# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-01 — FINAL REPORT

## Verdict

    GROUND TRUTH:      PASS  (contract A — simultaneous shared-drift acquisition)
    PHYSICAL TRANSFER: TRANSFER_NOT_ESTABLISHED

The instrument works. It is not yet shown to be buildable on a droplet.

## 1. What was fixed

CRD-00 died on **Z-17** (`K_base` vs `K_slow_drift` — a slow causal response under heavy drift): `E_trans`
overstated **7.1×**, `A_peak` read **422.7** against a true ~97. It quoted a drift excursion as a causal response.

Under a **shared drift realization**, the same pair (`CM-02`) returns:

| quantity | CRD-00 | CRD-01 |
|---|---|---|
| `E_trans` / truth | **7.10×** | **1.01×** |
| `A_peak` / truth | ~4.4× | **1.00×** |

Nothing in the decomposition estimators was tuned to achieve this. What changed is **what is acquired**.

## 2. Prospective run — 8/8, opened once, hash-gated

| case | admission | E_trans | P_inf | A_peak | E/E* | A/A* |
|---|---|---|---|---|---|---|
| P-01 null | ADMISSIBLE | NULL | NULL | NULL | — | — |
| P-02 slow + drift | ADMISSIBLE | RESOLVED | NULL | RESOLVED | 1.00 | 1.00 |
| P-03 persistent | ADMISSIBLE | RESOLVED | **INDETERMINATE** | RESOLVED | 1.00 | 1.02 |
| P-04 transient | ADMISSIBLE | RESOLVED | NULL | RESOLVED | 1.00 | 1.01 |
| P-05 independent control | **NOT_ESTABLISHED** | INDETERMINATE_DRIFT | ″ | ″ | refused | refused |
| P-06 partial common mode | **NOT_ESTABLISHED** | INDETERMINATE_DRIFT | ″ | ″ | refused | refused |
| P-07 contaminated control | **CONTAMINATED** | INDETERMINATE_DRIFT | ″ | ″ | refused | refused |
| P-08 heavy-drift null | ADMISSIBLE | NULL | NULL | NULL | — | — |

`P-03` is a genuine miss, and it is reported as one: the persistent offset was `RESOLVED` in development
(`CM-07`) and only `INDETERMINATE` prospectively. `P_∞` is the weakest component of the factorization.

All 12 gates pass. All 12 must-fail controls fail as required — including the one that matters most: **CRD-00's own
sham (an independent drift realization presented as a control) is REFUSED, not corrected.**

## 3. The frontier — the actual deliverable

The admission verdict **tracks the accuracy boundary**. That is the whole claim.

| axis | ADMISSIBLE up to | first refusal | accuracy inside the admissible region |
|---|---|---|---|
| unshared residual drift `b_A` | 0.10 | 0.25 (PARTIAL) | E/E* ≤ 1.05 |
| gain mismatch `a_C/a_A` | 1.40 | 1.80 (PARTIAL) | E/E* ≤ 1.32, A/A* ≤ 1.06 |
| lag mismatch `δ_C−δ_A` | 8 | 16 (PARTIAL) | E/E* ≤ 1.04 |
| control contamination `κ_C` | 0.00 | **0.02** (flagged) | — |

Inside the admissible region the instrument is accurate. Outside it, **it refuses instead of degrading**. The
contamination detector fires at 2% leakage and does not false-fire at zero.

The lag boundary is not a discovery: it is `LAG_MAX = 12`, declared before the sweep. The instrument stops where
its declared model stops, and says so.

## 4. Three bugs, all mine, all fixed by replacement rather than re-thresholding

1. **The drift proxy shared measurement noise with the deviation it corrected.** Built from the same control that
   was subtracted, the regression fitted ε against itself: `g_hat = −1.008` on a **drift-free** system — the
   "correction" was *injecting* noise. Fixed by acquiring **two** control channels: they share the drift, not the
   noise.
2. **Worst-of-64 episode admission reproduced CRD-00's own `max`-over-blocks error.** It made the pure null
   (`CM-01`, no response at all) come back `INDETERMINATE_DRIFT` — the unluckiest RDNR draw out of 64 carried the
   verdict. Common-mode rejection is a property of the **contract**, not of an episode: pooled median.
3. **The first contamination detector fired on every case, κ = 0 included.** It compared the control's
   probe-to-probe spread post-intervention against pre-intervention — but the OU drift starts at zero and its
   variance *grows*, so the post window holds more drift for purely temporal reasons. It confounded "the control
   varies with the probe" with "the drift accumulated." Replaced by a **sham-deviation** test: the sham is a null
   by construction, so if it is not flat, the control is leaking.

A single-tap correction was also insufficient — not because one tap fits badly, but because the declared
acquisition model's residual is `(a_A/a_C)·ĉ(t+δ_C−δ_A) − ĉ(t)`, a **derivative**, not a scaled copy. Two taps are
the minimum basis in which the contract's own algebra closes.

## 5. PHYSICAL-TRANSFER AUDIT — the reason this is not a success

Classification: **`MAPPING_REQUIRES_NEW_OBSERVABLE`**, and therefore **`TRANSFER_NOT_ESTABLISHED`**.

The contract that passed requires, for every episode, a **control channel that is the same system, unprobed,
recorded simultaneously**. On a droplet that channel does not exist: *you cannot intervene and not intervene on
the same droplet at the same time.* Everything demonstrated above rests on a control that a real experiment
cannot produce.

There is a reduction that would rescue it, and it is worth stating precisely because it is the next experiment:

> Co-record **one reference channel** (any stable co-located sensor sharing the environmental drift — it need not
> be an identical droplet) with **every** episode, active and sham alike. The drift then cancels *within* each
> episode against the reference; the reference's own baseline mismatch, being probe-independent, cancels *across*
> episodes between active and sham. No identical unprobed twin is required.

**I have not tested that variant.** The algebra says it should work; the ground truth here does not say so, because
every control in this run *was* the same system's baseline. An argued transfer is not a demonstrated one, and this
programme has already been burned twice by instruments that were right in expectation and wrong in every instance.

So the honest position is: the common-mode contract is **demonstrated in ground truth** and **unproven in
physics**. The frontier already fixes the acceptance criterion any real implementation must meet — unshared
residual drift ≤ 10%, gain mismatch ≤ 40%, lag ≤ 8 samples, contamination < 2%. A reference channel that misses
those numbers will be refused by the instrument rather than believed, which is the one property worth having.

## 6. Standing constraints

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment was run.
`β`, `D_int` and the droplet equations were not touched. `P(τ)` and `M(τ)` remain separate. There is no composite
identity score anywhere in the instrument, and the output remains factorized:
`R = (E_trans, P_∞, A_peak, L_onset, T_recovery, C, U)`.

## 7. What CRD-02 must do first

Test the co-recorded reference channel in ground truth — with a control whose baseline is **not** the system's own.
If it holds, the transfer becomes real. If it does not, the correct verdict is
`SCOPE FAILURE — COMMON-MODE CONTROL NOT TRANSFERABLE`, and the continuous causal-response programme should stop.
