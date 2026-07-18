# CAUSAL FINGERPRINTS IN CONTINUOUS SUBSTRATES — a methodological synthesis of v00–v03

**Four instruments. Four failures. One preserved negative result worth more than any of them would have been.**

The sealed prospective hold-out was **never spent**. Every failure was caught on development or on a single
prospective run, and every one is preserved.

---

## 1. Discrete-to-continuous transfer does not happen by adaptation

A Boolean causal fingerprint (`EXP-GT-FINGERPRINT-00`) passed prospectively on binary observables. It is
**undefined** on a continuous float, and the two obvious mappings both destroy the measurement:

| naive mapping | measured on the continuous substrate |
|---|---|
| cast to `uint8` | every sample -> `0`. **Universal false SAMENESS.** |
| exact float inequality | **304/304 samples differ from a system's own re-measurement.** **Universal false DIFFERENCE.** |

Supplying the missing quantization, tolerance, noise model and metric is **defining a new instrument**, not
adapting one. A prospective PASS is not transferable across a change of observable alphabet.

## 2. What must be standardized: the noise, never the signal

Units rescale the response **and the noise**; internal gain rescales the response and **leaves the noise alone**.
Standardizing by the channel's measured noise scale is therefore *exactly* unit-invariant and *exactly*
gain-sensitive. Normalizing by the response's own amplitude is unit-invariant and **gain-blind** — a doubled gain
collapses to the null.

**Consequent theorem:** *absolute gain is not identifiable when both the output scale and the noise scale are
free.* The noise scale must be **declared**, not inferred. Any physical mapping (droplets included) inherits this
debt.

## 3. Latency, and the guard that killed the first instrument

v00 aligned to the exogenous probe onset (correct) but guarded settling with a threshold on late-block motion. A
second-order cascade whose tail moved by 5.3% of peak against a 5% bar was refused — at a distance of 64.15 against
a separation radius of 23.36. **A fabricated abstention is exactly as dishonest as a fabricated certainty, and
harder to notice, because it looks like caution.**

## 4. The deterministic tail bound has a resolution ceiling no horizon can raise

v01 replaced the guard with a bound on the unseen remainder. Its noise floor (7.40) exceeded the remainder it had
to detect (8.25). v02 then swept a preregistered horizon grid and measured the ratio `B_signal/B_noise`:

**0.89 · 2.55 · 2.56 · 1.18 · 0.29** — it **peaks at 2.56 and collapses.**

```
B_noise  improves as exp(-(W-84)/(3*TAU_MAX))        B_signal decays as exp(-W/tau)
```

**The signal dies faster than the floor improves whenever `tau < 3*TAU_MAX` — true for essentially every
in-contract system, since `TAU_MAX` is by definition the slowest admitted.** *A longer window destroys the very
evidence it was supposed to reveal.*

## 5. Measurement in these substrates is drift-limited

White-noise theory predicts the floor should fall to ~0.58 by W=320. **Measured: 3.49, and it stops improving.**
Sub-block **means** wander with the slow baseline while a differenced noise estimate is **blind to drift by
construction**. *The longer you look, the more the baseline has wandered.* Any statistic built on late block means
must carry a drift-aware scale — and v03's matched sham channel (baselines only, no intervention) measures it
directly (1.26 noise units).

## 6. THE RESULT — the quantity all three tail guards were protecting is not well-defined

The fingerprint distance is an **RMS over an observation window**. For any **transient** difference it dilutes at
**exactly** `sqrt(W/W')` and **tends to zero as the window grows**:

| noise-free, same metric, only the window changes | W=320 | W=1400 | ratio |
|---|---|---|---|
| v00 burned cascade | 47.35 | 22.64 | 0.478 |
| v01 T4 | 30.18 | 14.45 | 0.479 |
| gain x2 | 115.32 | 55.13 | 0.478 |
| sign inversion | 230.64 | 110.27 | 0.478 |
| **hidden state (PERSISTENT)** | 346.43 | 348.01 | **1.005** |

`sqrt(320/1400) = 0.478`. **The persistent difference does not dilute. That control proves the effect is the
metric's normalization, not the systems.**

> **For a FIXED window the instrument already sees everything it will ever see. There is no "unseen remainder"
> affecting `D_W`; the only uncertainty is measurement noise. "The distance at a longer window" is not a fact about
> the pair — it is a fact about the pair AND the window, and for transient differences its limit is zero.**

**v00, v01 and v02 were each defeated by a quantity that does not exist.** The one legitimate truncation concern is
**persistence** — a transient probe leaving a permanent mark — and that does *not* dilute and is fully captured by
any window exceeding the settling time plus the declared delay horizon.

## 7. Deterministic identifiability versus calibrated statistical risk

v03 was to retreat from proof to **risk**: predict the eventual distance, attach a conformal interval, abstain when
it touches a boundary. The retreat is sound in principle — but it inherited the ill-posed target, and the
inconsistency surfaced **before a single parameter was fitted**, as a disagreement between construction truth and
the privileged path. `BENCHMARK_INVALID`.

**A risk-calibrated instrument is only as meaningful as the quantity whose risk it calibrates.**

## 8. What survives — and it is not nothing

* the **repertoire-relative verdict vocabulary**: `INDISTINGUISHABLE_UNDER_REPERTOIRE` / `DIFFERENT` /
  `INDETERMINATE`, and `EQUIVALENCE_CLASS_ONLY`. **There is never a metaphysical `SAME`.**
* **false sameness is real and constructible**: an internal mode unreachable from the external fields makes two
  systems *bit-for-bit identical* under a limited repertoire and separable under a rich one. Both statements are
  true. Equivalence is relative to a repertoire.
* **hidden state is detectable exactly insofar as it changes the causal response** — a purely static output offset
  is absorbed by the readout offset and is *correctly* unidentifiable.
* **abstention machinery** — silence, unreadability, nonstationarity, insufficient access, off-contract channels —
  all work and all fire for their declared reasons.
* the **two-path truth check earned its keep twice**: it caught a free-affine-fit bug in the privileged evaluator
  that was absorbing gain and sign as "units", and it caught the ill-posed target here.

## 9. Implication for causal fingerprints in artificial-life substrates

**Any fingerprint whose distance is a mean over an observation window inherits a window-dependent verdict, and any
guard that tries to certify against "what would happen if we looked longer" is chasing its own normalization.**
A well-posed continuous fingerprint needs a **window-invariant discrepancy functional** — an integral rather than a
mean, or a normalization by response energy rather than window length. That is a change to the **metric**, which
has been the one unchanged component since v00, and it is therefore a **new programme, not a new version**.

**No v04 is built.** `SC-PILOT-CAUSAL-FINGERPRINT` and `EXP-SC-01` remain **BLOCKED**. No droplet experiment was
ever executed anywhere in this branch, and `beta`, `D_int` and the droplet equations were never touched.
