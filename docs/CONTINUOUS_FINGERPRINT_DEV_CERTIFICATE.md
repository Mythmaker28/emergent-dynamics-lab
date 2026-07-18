# DEVELOPMENT CERTIFICATE — EXP-GT-CONTINUOUS-FINGERPRINT-00

**Development data only.** The prospective systems were not simulated at any point during this phase.

## Result

| | |
|---|---|
| challenge matrix | **52 / 52** (26 cases x 2 arms) |
| two-path benchmark validation | **52 / 52**, **0 disagreements** |
| must-fail controls fired | **7 / 8** — **L6 did not fire, and that is reported, not hidden** |
| radii (limited) | `r_continuity = 7.786`, `r_separation = 23.357` |
| radii (rich) | `r_continuity = 8.207`, `r_separation = 24.622` |

Radii come from the **NULL alone** — repeated independent measurement of the same system — by the rule frozen in
the protocol *before this instrument existed*: `r_cont = 2.0 * q99.9(null)`, `r_sep = 3.0 * r_cont`. No label and
no difference pair was ever consulted to set a threshold.

## Candidate representations tested (development only)

| detrend | representation | max(null/continuity) | min(difference) | separation ratio |
|---|---|---|---|---|
| offset | **NSRC** (noise-standardized) | 5.219 | 7.926 | **1.52** |
| offset | `resp_rms` (normalize by the response's own RMS) | 0.832 | 0.428 | **0.51** |
| offset | `ncc` (normalized cross-correlation) | 0.066 | 0.034 | **0.52** |
| linear | NSRC | 6.594 | 8.067 | 1.22 |

`resp_rms` and `ncc` score **below 1**: their difference distances are *smaller* than their null distances. They
are unit-invariant and **gain-blind**, and they cannot be given a threshold at all. They are retained only as
must-fail control **L7**. Linear detrending extrapolates a 96-sample slope fit across 160 samples and amplifies
noise; offset detrending is simpler and better, so it is frozen.

## Three defects found in the instrument by development, and what each would have falsely concluded

**1. The metric aggregated over probe blocks with a MEAN.** `supply_cause` differs from `leak` on the two SUPPLY
probes and is *bit-for-bit identical* on the six DRIVE probes (measured: 6.5e-19). A real per-block separation of
21.8 was averaged down to **8.6** by twenty-four blocks of pure noise, making it the weakest difference in the set.
*Would have falsely concluded:* that a system with an entire extra independently-controllable cause was nearly
indistinguishable from one without it. **Fixed by the quantifier, not by tuning:** "indistinguishable under the
repertoire" is a FOR-ALL, and a for-all is certified by its WORST case. `AGGREGATE = max`. The pair went to 38.9.

**2. `sigma_hat` estimator error was multiplying the signal.** `z = r / sigma_hat`, so a relative error `eps` in
`sigma_hat` injects `eps * z_signal` into every comparison **including a system's comparison with itself**. With
the signal at z ~ 250, a 2% disagreement between two `sigma_hat`s manufactured a null distance of ~5 on the
large-amplitude probes while the quiet probes sat at 1.8. **The null was not noise — it was my own estimator,
multiplied by the signal.** Its signature: raising the repeat count made the instrument *worse* (null at R=4/8/16
was 5.2 / 9.4 / 25.8), because the signal grows with R and so did the artefact.
*Would have falsely concluded:* that more data makes a causal measurement less reliable.
**Fixed** by (a) one independent baseline episode *per probe* rather than four shared baselines, and (b)
quotienting over one common scale `lambda` **clipped to the estimator's own +-3-sigma confidence band** (+-4.2%).
The null became pure noise and **R-invariant** (3.70 / 4.29 / 4.12) while differences grew as sqrt(R)
(21.0 / 29.9 / 42.5 — ratios 1.42 and 2.02, i.e. exactly sqrt(2) and 2). `N_REPEAT = 16` was then chosen.

**DECLARED PRICE:** gain differences **below ~4% are not resolvable**. This is not a bug that was papered over. It
is the measurement-contract theorem cashing out: the unit factor is knowable only through the noise floor, so the
precision with which a GAIN can be resolved is bounded by the precision with which the NOISE can be measured.

**3. Responsiveness and in-flight thresholds were miscalibrated.**
* `Z_DET = 5.0` ("five sigma") was **below the noise floor it was thresholding**. `sigma_hat` measures the *white*
  noise (a std of first differences, which annihilates drift by design), but z's excursion over a 160-sample
  window also contains the *drift*. Measured on systems that **cannot** respond: max|z| per row has mean 3.67 and
  **max 5.25**, and 3% of rows exceed 5.0. A **silent system was scoring 1/32 "responses"**, passing the
  responsiveness check, and being handed a confident **DIFFERENT** against a system it cannot even hear.
  *Would have falsely concluded:* that silence is evidence. **Fixed:** `Z_DET = 8.0`, calibrated on **noise-only**
  rows (1.5x the largest excursion ever observed there). No label was consulted.
* The in-flight guard's threshold was **absolute** (3 noise units). A response 500 noise units tall that has
  decayed to 1% of itself still moves by 5 units, so `D_leak_T16` — a perfectly ordinary system — was refused as
  though its response had not finished. *Would have falsely concluded:* a **fabricated abstention**, which is
  exactly as dishonest as a fabricated certainty and harder to notice because it looks like caution.
  **Fixed:** the guard must also clear a threshold **relative to the row's own amplitude** (5% of peak).

## A defect found in the BENCHMARK, not the instrument

`D_noisy` was built with `sigma_mult = 60`, giving a true SNR of **1.97** — which is not "below the noise floor",
it is marginally **above** it. The instrument duly detected it and returned DIFFERENT, and the case "failed".
**The failing thing was my system, not the instrument.** Raising the instrument's detection threshold until the
case abstained would have been fitting a threshold to a label. The **system** was fixed instead (`sigma_mult = 250`,
true SNR 0.47). Classified: **benchmark-label failure**. Recorded, not buried.

## A defect found in the PRIVILEGED TRUTH PATH — by the two-path check, which is what it is for

The privileged evaluator's residual was a **free global affine fit** of B onto A. But a doubled gain **is** an
affine map (`a = 2`) and a sign inversion **is** an affine map (`a = -1`). The evaluator was therefore absorbing
exactly the differences the instrument exists to detect, and it certified `D_leak` **EQUIVALENT** to
`D_leak_gain2` and to `D_leak_sign` — two flagship DIFFERENCE cases.

**A benchmark whose truth path is wrong cannot fail an instrument; it can only slander one.**

The error was conceptual and it is the measurement-contract theorem again: under a *free* output scale, gain is
genuinely unidentifiable; under the *declared contract* the noise floor is common and fixed, so `a` is **pinned**.
The residual now divides each response by that channel's **declared** noise scale and fits nothing at all.
Classified: **evaluator / ground-truth failure**.

## Must-fail controls

| id | what it breaks | observed | fired |
|---|---|---|---|
| **L1** | exact float inequality as the metric | **1.0000** of samples differ — system vs **itself** | **YES** |
| **L2** | uint8 cast of the raw observable, no calibrated scaling | d(leak, **sign-inverted**) = **0.0000** | **YES** |
| **L3** | response window 40 (< the longest response) | persistent rows **4 -> 12** | **YES** |
| **L4** | remove the SUPPLY probes | d(leak, supply_cause) **76.55 -> 3.01** (below `r_continuity`) | **YES** |
| **L5** | reintroduce a forbidden topology label | d(leak, leak+dead_site) **2.35 -> 51.18** | **YES** |
| **L6** | lexicographic phase sort instead of the group quotient | null **2.66 -> 3.45** | **NO** |
| **L7** | normalize by the response's own RMS, not the noise | d(gain x2) = **1.490** vs null **1.448** | **YES** |
| **L8** | disable the common-noise-channel refusal | same system, 4x noisier channel -> **DIFFERENT** (d=123.1) | **YES** |

**L2 initially did not fire, and finding out why mattered.** The first implementation cast the *already
standardized* `z` (which is O(100)) to uint8, and of course it survived. **A control that breaks the wrong thing
tests nothing.** The cast belongs at the ADC, on the **raw observable** of order 1e-3 — which is precisely where
the preflight said the Boolean instrument dies. Moved there, it collapses everything to 0.0000: universal false
sameness, reproduced exactly as D-073 predicted.

**L6 DID NOT FIRE, AND IS REPORTED AS SUCH.** The lexicographic quotient is *stable* in this benchmark because the
four phase rows are well separated, so noise does not reorder them. The cyclic-shift quotient remains the
**principled** choice — a canonical ordering of continuous rows is discontinuous in general — but it is **NOT
demonstrated to be load-bearing here**. A control that does not fire is not a control, and the protection it was
supposed to prove is therefore **unproven**, not proven.

## Ship of Theseus — reported with the D-073 correction built into the field names

`n_deviating_samples` and `span_from_swap_to_last_deviation` are **different quantities** and carry **different
names**, so that they cannot be conflated again. Measured at a 1e-9 relative threshold:

| replacement at t=150 | deviating samples | span to last deviation | max relative deviation |
|---|---|---|---|
| add an inert internal degree of freedom | **0** | **0** | 0.00e+00 |
| relocate the machinery to another address | **164** | **164** | 7.18e-01 |

The first replacement is genuinely seamless. The second is **not**: the accessible output deviates for 164
consecutive samples, decaying exponentially back to the original behaviour. **No "uninterrupted behaviour" claim
is made anywhere.**

## Solver convergence — the measurement that licenses "refinement is a nuisance"

RK4 `h=0.25` vs `h=0.125`, relative: `D_leak` 5.9e-09 · `D_fb` 8.8e-09 · `D_sat` 6.4e-09 · `D_cascade` 7.6e-08 ·
`D_mem_p` 2.1e-07. All below the `TOL_REL = 1e-5` solver tolerance and orders of magnitude below the noise floor.
