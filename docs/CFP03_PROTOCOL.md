# EXP-GT-CONTINUOUS-FINGERPRINT-03 — PREREGISTRATION

**Drift-Aware Risk-Calibrated Continuous Causal Fingerprint.** The **final** authorized version in this branch.

Committed **before any predictor is fitted** and before the calibration set is touched.

---

## 1. The change of question — and it is a retreat, deliberately

| v00–v02 asked | v03 asks |
|---|---|
| Can the unobserved remainder be **bounded** hard enough to **prove** the verdict cannot change? | Under a **declared stochastic noise-and-drift contract**, can the **probability** that the unseen continuation changes the verdict be **calibrated and bounded in advance**? |

v02 proved the first question has no answer in this substrate: the deterministic tail bound's signal-to-noise ratio
is **bounded above (~2.56) and non-monotone in the horizon**, and the noise floor is **drift-limited**. Nothing is
gained by changing constants, horizons or block lengths, and **this protocol does not attempt it.**

**v03 is a risk-controlled instrument. It is NOT a certainty-producing instrument.** That is a real reduction in
what may be claimed, and it is stated up front rather than discovered in the discussion section.

## 2. The claim

> Under a declared continuous noise-and-drift distribution, a fixed causal-response fingerprint can issue
> repertoire-relative verdicts with a **prospectively calibrated error risk**, while abstaining when its prediction
> interval crosses a decision boundary.

**Statistical · distribution-relative · MARGINAL, not conditional · contingent on the stated acquisition contract.**

**Not demonstrated:** identity · individuality · lineage · life · autonomy · universal causal equivalence ·
**deterministic tail certification** · robustness to arbitrary distribution shift · **droplet transfer** ·
material-turnover continuity.

## 3. THE RISK CONTRACT — fixed here, before any fitting

```
        alpha = 0.05        target: >= 95% MARGINAL coverage of the prediction interval for D_infinity
```

Stated explicitly, and not to be quietly forgotten later:

* this is **marginal** coverage over the declared benchmark distribution;
* it is **not** conditional coverage for every topology or every drift regime;
* it is **not** protection against arbitrary out-of-distribution systems;
* it is **not** a metaphysical confidence about sameness.

**If the finite calibration size cannot support `alpha = 0.05`, the run stops with
`INSUFFICIENT_CALIBRATION_RESOLUTION`. `alpha` is NOT silently changed.**

## 4. THE TARGET QUANTITY — predict a distance, not a label

| | |
|---|---|
| `D_W` | the **observable-prefix** distance: the frozen fingerprint metric using only the allowed window `W = 320` |
| `D_inf` | the **privileged eventual** distance: computed by the independent privileged path from **NOISE-FREE ground-truth trajectories** at `W_INF = 1400` (all in-contract responses complete). **It never uses the instrument's tail estimator, sigma-hat, or any threshold.** |

The instrument predicts an **interval for `D_inf`** from information available at `W`. It does **not** predict the
class label. Thresholds stay explicit and the representation stays auditable.

## 5. DRIFT-AWARE ACQUISITION — matched sham controls

v02's floor was **drift-limited**, and its noise scale (`sd`, from differencing) was **blind to drift by
construction**. So the contract now carries a **matched sham**.

Every active probe episode already has an **independent baseline episode** with identical duration, timing,
horizon, sampling and noise/drift generator, differing **only** in the absence of intervention amplitude. The sham
channel is built from those baselines alone:

```
  z_sham(p,k) = [ mean(base over the first  R/2 repeats) - mean(base over the second R/2 repeats) ] / (sqrt(2)*sigma_hat)
```

matched in averaging structure to the causal deviation and **containing no intervention at all**. It gives a
**per-system drift scale** at zero extra simulation cost.

**The drift estimator is derived from sham/baseline episodes only. The active tail is NEVER fitted away to
estimate drift, and no hidden system label is ever consulted.**

## 6. DEVELOPMENT PARTITION — committed here, before fitting

Three **disjoint** sets (`edlab/substrates/ctrans/manifests03.py`), verified: no system, parameter tuple, seed or
acquisition appears in more than one, none matches any sealed-prospective system, and the **third-order cascade
reserved to the prospective split appears nowhere in development**.

| set | n | seeds | role |
|---|---|---|---|
| **FIT** | 14 | `3xx_xxx` | the predictor is fitted here and nowhere else |
| **CALIBRATION** | 14 | `4xx_xxx` | **untouched until the predictor is fixed**; conformal residuals only |
| **CHALLENGE** | 22 | `5xx_xxx` | gates and controls; carries the historical regressions |

## 7. PREDICTOR — small, auditable, fit-set only

Target `Delta_W = D_inf - D_W`. **Allowed inputs** (none of them a label): late differential level; late slope;
tail energy; nested-prefix distance change `D_W - D_{W/2}` (**from prefixes of the SAME acquisition**); peak
amplitude; **sham-derived drift scale**; calibrated noise scale; margin to each decision boundary; coverage and
responsiveness.

**Family: ridge regression on standardized features** (with plain least squares and an intercept-only baseline as
comparators). Selection by **fit-set cross-validation ONLY.**

**Forbidden:** neural networks · topology labels · implementation IDs · hidden states · system names · prospective
metadata · flexible tail models.

## 8. CALIBRATION — split conformal

Absolute residuals `|D_inf - (D_W + pred)|` on the **untouched** calibration set; conformal quantile at level
`ceil((n+1)(1-alpha))/n`. Interval `[L_W, U_W] = pred_D_inf -/+ q`. Reported: calibration `n`, the quantile,
empirical coverage, interval-width distribution, **coverage by system family and by drift/noise regime**
(diagnostic — it does **not** license a conditional guarantee).

## 9. VERDICT LOGIC

`U_W < r_continuity` -> repertoire-relative continuity (**never metaphysical SAME**) ·
`L_W > r_separation` -> `IDENTIFIABLE_DIFFERENT` ·
interval intersects either boundary or the ambiguity region -> **`INDETERMINATE_RISK_INTERVAL`** ·
rich separates but limited does not -> `EQUIVALENCE_CLASS_ONLY` ·
features outside the calibrated ranges -> **`OUT_OF_CALIBRATION_SCOPE`** (no confident extrapolation).
Radii by the unchanged rule, on the **fit set only**: `r_cont = 2 * q99.9(fit-set null D_W)`, `r_sep = 3 * r_cont`.

## 10. DEVELOPMENT GATES (all must pass to freeze)

**G1** >= 95% empirical coverage on the untouched challenge set, with a finite-sample CI reported · **G2** no
confident wrong verdict · **G3** non-vacuity: >= **70%** of predeclared in-contract decidable comparisons receive a
verdict · **G4** the v01 T4 case abstains (or is legitimately resolved) · **G5** the v00 burned cascade classifies ·
**G6** drift robustness · **G7** out-of-contract drift/noise -> `OUT_OF_CALIBRATION_SCOPE` or abstention · **G8**
gain, sign, hidden state, feedback, extra causes detectable · **G9** continuity protected · **G10** limited-access
collisions -> `EQUIVALENCE_CLASS_ONLY` · **G11** construction truth and privileged truth agree · **G12**
nested-prefix coherence.

## 11. MUST-FAIL CONTROLS

remove sham drift correction -> coverage worsens · calibrate on white noise ignoring drift -> **undercoverage** ·
exact float inequality -> false differences · integer cast -> false sameness · remove conformal calibration ->
overconfident errors · **fit on the calibration set -> optimistically narrow intervals** · remove the OOD gate ->
confident prediction under excessive drift · remove a discriminating probe -> a real difference collapses · add an
implementation label -> leakage · **replace nested prefixes with separately simulated episodes -> the RNG confound
returns** (v02 measured this at 6.48 on a system compared with itself).

## 12. FINAL STOP RULE

**This is the last authorized version in the continuous-fingerprint branch.**
Pass -> authorize (do not execute) `SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`.
Fail at development -> **do not touch the sealed split**; close the branch.
Fail prospectively -> the hold-out is burned; close the branch.
**Either way: no v04.** A methodological synthesis of v00–v03 is written.

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment.
