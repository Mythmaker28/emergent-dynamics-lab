# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-01 — PREREGISTERED PROTOCOL

**Committed before any fitting, any frontier sweep, and any prospective system.**

## 1. What killed CRD-00

CRD-00 failed on **Z-17** (`K_base` vs `K_slow_drift`): a slow causal response under heavy drift. `E_trans` was
overstated **7.1×** (3.05e6 against a privileged 4.30e5) and `A_peak` read **422.7** against a true ~97. The
instrument called the drift a response, and said so with confidence.

The diagnosis was not an estimator defect:

> **A sham with the same variance but an independent realization is unbiased in expectation and useless per pair.**

The matched sham had the right *distribution* of drift. It did not have the *disturbance*. Debiting its energy
removes the right amount on average and the wrong amount every single time.

So CRD-01 **changes the acquisition contract**. It does not tune CRD-00's estimators. The one thing it adds to the
decomposition is **the right to refuse on drift grounds** (`INDETERMINATE_DRIFT`) — the verdict CRD-00 could not
reach and therefore never issued.

## 2. The acquisition model (declared)

    y_A(t) = s_A(t) + a_A·d(t−δ_A) + b_A·n_A(t) + ε_A(t)      ACTIVE   (receives the intervention)
    y_C(t) = s_C(t) + a_C·d(t−δ_C) + b_C·n_C(t) + ε_C(t)      CONTROL  (receives none)

`d(t)` is **one shared realization**. `n_A`, `n_C` are the *unshared* residual drifts — `b = 0` is perfect common
mode, and `b` is the frontier axis. The instrument receives only the traces. It never sees `d`, `a`, `δ`, `b`, the
system labels, or the states.

This is composed **on top of the frozen v00 engine, run noise-free**. `engine.py` is not touched; its sha256 stays
in the v00 freeze manifest. The frozen engine gives every episode an *independent* drift — which is precisely the
defect CRD-01 exists to repair, so the drift must be composed outside it.

## 3. Four simultaneous channels — and why two controls, not one

    y_A  ACTIVE     receives the intervention
    y_C  CONTROL-1  the SUBTRAHEND
    y_D  CONTROL-2  the DRIFT PROXY
    y_S  SHAM       identical acquisition, intervention amplitude zero — calibrates the bands

A proxy built from the **same** control you subtract shares that control's *measurement noise* with the deviation
you are correcting. The regression then fits ε against itself. **Measured: `g_hat = −1.008` on a drift-free
system** — the "correction" was injecting noise, not removing drift. Two control channels share the drift and not
the noise, so the regression sees only drift. This was a real bug, caught, and it is why the contract has four
channels.

Two simultaneous reference channels is an ordinary instrumentation request, not an oracle: neither channel is ever
told the system's state, the intervention, or the drift.

## 4. The correction

    ĉ_r(t) = y_D(r,t) − mean_r y_D(r,t)                              drift proxy, CONTROL-ONLY
    r_corr(r,t) = [y_A(r,t) − y_C(r,t)] − [g₀·ĉ_r(t) + g₁·ĉ_r(t−λ)]

`g₀, g₁, λ` are fitted **on the pre-intervention region only** — where the causal response is zero *by
construction*. A correction fitted on the causal tail can subtract the signal; this one is structurally unable to.

**Two taps, not one.** The declared model puts a lag on *each* channel, so the residual drift is
`(a_A/a_C)·ĉ(t+δ_C−δ_A) − ĉ(t)`: a gained, lagged copy *minus* an unlagged one. With `δ_A=0, δ_C=4` that is
`d(t)−d(t−4) ≈ 4·d′(t)`, a **derivative**, and a single tap returns `g=0` and cancels nothing (measured: RDNR 1.67,
common mode wrongly downgraded to PARTIAL). Two taps span exactly the declared model. This is not a degree of
freedom bought to improve a number; it is the minimum basis in which the acquisition contract's own algebra closes.

## 5. Pre-window = analysis window (W_PRE = W_FIXED = 480)

A common-mode certificate earned on a short window, where the drift has barely developed, **does not transfer** to
a long window where it has. The rejection is certified over the same duration it will be trusted for.

## 6. Noise floor — declared, not fitted

    σ̂_ε = std(diff(r_pre)) / √2

The drift is smooth (τ ≈ 500), so differencing annihilates it. The measurement noise is white, so differencing
preserves it. This estimator is **drift-immune by construction**. (Same discipline as NSRC: the noise scale is
declared, not inferred from the signal.)

## 7. Admission — thresholds fixed here

    RDNR = std(r_corr, pre) / σ̂_ε          residual common mode, in units of the measurement-noise floor

| condition | verdict |
|---|---|
| channel drift < 2·σ̂_ε | `DRIFT_ABSENT` — common mode is moot, not failed; correction switches **itself off** |
| RDNR ≤ 1.5 | `COMMON_MODE_ADMISSIBLE` |
| 1.5 < RDNR ≤ 4.0 | `COMMON_MODE_PARTIAL` — **reported, never used for a component verdict** |
| RDNR > 4.0 | `COMMON_MODE_NOT_ESTABLISHED` |
| control's probe-dependence, post/pre > 3.0 | `CONTROL_CONTAMINATED` |

The admission question is physical, not statistical decoration: *after correction, is the residual common mode down
at the measurement-noise floor — i.e. inside the bands the sham already covers?* Not "is the correlation high".

**Contamination needs no oracle.** An honest control's baseline is *probe-independent*: pre-intervention its
ensemble mean is identical across probes, and post-intervention it stays identical — unless the control is leaking
the intervention. The probe-to-probe spread of the control's ensemble mean, post versus pre, is the detector.

## 8. Output — still factorized. No composite score. Ever.

    R = (E_trans, P_∞, A_peak, L_onset, T_recovery, C, U)

Component statuses: `RESOLVED` / `NULL` / `INDETERMINATE` (band-limited) / **`INDETERMINATE_DRIFT`**.

**Hard rule:** if admission is not `ADMISSIBLE` or `DRIFT_ABSENT`, **every component returns
`INDETERMINATE_DRIFT`.** No component verdict is issued on a partially-rejected common mode. This is the refusal
CRD-00 lacked.

## 9. Candidate contracts and the selection rule (fixed before any is run on a case)

- **A — simultaneous.** One shared `d` across channels. *Assumption:* the channels couple to the drift with
  similar gain/lag. *Cost:* simultaneous channels.
- **B — ABBA interleaved.** Single channel, episodes ordered A-B-B-A; cancels the drift's **linear** component
  only. *Assumption:* drift locally linear over the block — false for fast drift. *Cost:* none.
- **C — intervention reversal.** Record `+u` and `−u` sharing one `d`; `(y₊−y₋)/2` cancels the drift **exactly**,
  with no control channel at all. *Assumption:* **the response is odd in u** — false under saturation.

**Selection rule:** take the contract that passes its own admission test on development data, on the case that
killed CRD-00 (Z-17). If more than one passes, prefer the one whose stated assumption is weakest. If none passes,
return `SCOPE FAILURE`.

## 10. The partial common-mode frontier

Swept axes (declared here, measured later): unshared residual drift `b_A`; gain mismatch `a_C/a_A`; lag mismatch
`δ_C−δ_A`; control contamination `κ_C`; drift amplitude. **The frontier is the deliverable**, not a single
best-case success: what matters is *where* the contract stops working, and whether the instrument knows it.

## 11. Splits

New dev/prospective split (dev `8xx`, prospective `9xx`). It **has** to be new: CRD-01 changes what is acquired, so
a split earned under CRD-00's acquisition was earned under a different instrument. The prospective split is opened
**once**, after the freeze.
