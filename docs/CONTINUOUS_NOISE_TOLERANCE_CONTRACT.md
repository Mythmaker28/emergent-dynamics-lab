# NOISE AND TOLERANCE CONTRACT — continuous causal fingerprints

The noise model is **load-bearing**. It was defined before the prospective run and is stated here in full.

## The six things the instrument must tell apart

| | how |
|---|---|
| floating-point noise | never used as a signal. Exact float inequality is control **L1**, and it calls a system different from **its own re-measurement** (1.0000 of samples). |
| measurement noise | `sigma_hat` = std of the FIRST DIFFERENCES of the pooled pre-probe segments / sqrt(2). Differencing annihilates drift, so this is the fast/white scale. |
| baseline variability | `baseline_stability` = rms(detrended pre-probe) / `sigma_hat`. Pure white noise gives ~1.0. |
| slow drift | an Ornstein–Uhlenbeck baseline (`tau = 500`), **independent per episode** so it does **not** cancel between a probe and its baseline. Caught by `BASELINE_MAX = 3.0`. |
| stochastic system variation | none in this substrate; the dynamics are deterministic and the stochasticity is entirely in the measurement channel. **Declared scope limit.** |
| genuine causal-response change | everything above the calibrated separation radius. |

## Where the tolerance comes from — and where it does not

```
r_continuity = SAFETY     * quantile_99.9( NULL distance distribution )     SAFETY     = 2.0
r_separation = SEP_FACTOR * r_continuity                                    SEP_FACTOR = 3.0
```

The **NULL** is *repeated independent measurement of the same development system*. **No label, and no difference
pair, was ever consulted to set a threshold.** `SAFETY` and `SEP_FACTOR` were fixed in the protocol before the
instrument existed and were not revisited after a single distance was seen.

Measured: limited `r_cont = 7.786`, `r_sep = 23.357`; rich `r_cont = 8.207`, `r_sep = 24.622`.

## Why a radius calibrated on development noise transfers to an unseen noise regime

Every stochastic term in the substrate **scales with sigma** (the drift is defined as a fraction of the noise, not
as an absolute). The representation divides by the channel's **own measured** noise scale. Therefore:

* the **NULL** distance is **sigma-invariant by construction** — not by luck;
* a **difference** distance scales as **1/sigma** — a noisier channel genuinely resolves less, which is physics,
  not instrument failure.

Prospective gate **G7** cashed this: continuity held at an **unseen 1.6x** noise level (distance 2.808, radius
7.786). Pin the drift to an absolute value instead and this invariance quietly dies.

## The measurement-contract theorem — the load-bearing assumption, stated plainly

> If the readout may be rescaled by an unknown `a > 0`, the **only** scale the instrument can calibrate against is
> the channel's own **noise floor**. Therefore a system whose noise floor is **halved** is, to this instrument,
> *exactly* as indistinguishable from a system whose **gain is doubled**.
>
> **ABSOLUTE GAIN IS NOT IDENTIFIABLE WHEN BOTH THE OUTPUT SCALE AND THE NOISE SCALE ARE FREE.**

This is a theorem about the declared nuisance group, not an implementation defect. Its consequences:

1. The noise **scale** is **NOT a nuisance**. It is a **declared** property of the channel. A comparison is
   admissible only if the two systems are **declared** to sit on a **common noise channel**. The admission layer
   **refuses** otherwise. Control **L8** removes the refusal and the false difference walks straight in: the same
   system on a 4x noisier channel is confidently reported **DIFFERENT** (d = 123.1).
2. The instrument's **gain resolution is bounded by its noise-scale resolution**. `sigma_hat` carries ~**1.39%**
   relative error (measured over 12 independent acquisitions; theory for 3072 independent difference samples says
   1.28%). That error **multiplies the entire standardized trace**, so the metric quotients over one common scale
   `lambda` clipped to the estimator's own **+-3-sigma band (+-4.2%)**.
   **DECLARED PRICE: gain differences below ~4% are NOT RESOLVABLE by this instrument.** Reported, not hidden.
3. **This is the debt the droplet mapping must pay physically.** "Field noise" is on the unresolved list in the
   domain-admission contract for exactly this reason. Two droplets cannot be compared on gain unless their
   measurement channels are established, *physically*, to share a noise floor.

## Detection thresholds — calibrated on noise, never on labels

`Z_DET = 8.0`. Measured on rows of systems that **cannot** respond (so every row is pure noise): max|z| has
**mean 3.67, median 3.55, max 5.25**, and **3% of rows exceed 5.0**. The original `Z_DET = 5.0` ("five sigma") was
therefore **below the noise floor it was thresholding**, because `sigma_hat` measures the *white* part while z's
excursion over 160 samples also contains the *drift*. A **silent system was scoring 1/32 "responses"** and being
handed a confident verdict. `Z_DET = 8.0` is **1.5x the largest excursion ever observed on a noise-only row**.

## Unit invariance — tested, exact

`u -> a*u + b`. Prospective gate **G6**, same seeds, `a = 250`, `b = -0.02`: maximum relative deviation between
the standardized fingerprints of `P_leak` and `affine(P_leak)` = **0.0** (bound: 1e-9). Exact, not approximate:
`b` cancels in the deviation and `a` cancels against `sigma_hat`.

**Gain is NOT removed with it**, because gain is declared part of the accessible function: `P_leak` vs
`P_leak_gain3` -> **170.6**, `DIFFERENT`. Control **L7** normalizes by the response's own RMS instead — also
unit-invariant, and **gain-blind**: the doubled-gain pair collapses to **1.490** against a null of **1.448**.
