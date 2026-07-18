# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00 — PROTOCOL (PREREGISTERED)

**Factorized Causal Response Decomposition.** A **new programme**, not continuous-fingerprint v04.
Committed **before the instrument exists**.

---

## 1. The discovery that forces this

The historical fingerprint used a **window-normalized RMS**:

```
D_W = sqrt( (1/W) * integral_0^W |delta_r(t)|^2 dt )
```

Measured on noise-free traces, changing **only** the window:

| pair | W=320 | W=1400 | ratio |
|---|---|---|---|
| v00 cascade | 47.35 | 22.64 | **0.478** |
| v01 T4 | 30.18 | 14.45 | **0.479** |
| gain x2 | 115.32 | 55.13 | **0.478** |
| sign inversion | 230.64 | 110.27 | **0.478** |
| **persistent hidden state** | 346.43 | 348.01 | **1.005** |

`sqrt(320/1400) = 0.478`. **Every finite transient dilutes at exactly the normalization rate; the persistent
difference does not dilute at all.** The old scalar was conflating two quantities of different kind:

1. **finite transient disagreement** — vanishes under time averaging;
2. **persistent asymptotic disagreement** — does not.

**The next instrument must not force them into one number.**

## 2. The question

> Can the discrepancy between two continuous causal-response profiles be decomposed into **separate,
> window-stable components** — transient energy, persistent difference, latency, peak, recovery — **without
> manufacturing sameness or difference from observation duration**?

## 3. FORBIDDEN

**No composite.** `D_identity = w1*E + w2*P + w3*A + w4*L` is forbidden, and so is any learned weighting, Pareto
score, or hidden scalar ranking that reintroduces one through the back door. The output stays **factorized**:

```
R(x,y) = ( E_trans , P_inf , A_peak , L_onset , T_recovery , C , U )
```

**Each axis gets its own claim, its own calibration and its own falsifier.**

## 4. The axes, and why each is window-stable

| axis | estimator | window behaviour |
|---|---|---|
| `P_inf` | mean of `delta_r` over a declared LATE window, with a stability check between its halves; **zero unless it exceeds a drift-aware uncertainty** | stabilizes once the late regime is observed |
| `E_trans` | **an INTEGRAL, not a mean**: `sum_t (delta_r - P_inf)^2`, noise-debiased | **non-decreasing toward its limit.** THIS IS THE FIX: an integral does not dilute |
| `A_peak` | `sup_t |delta_r|`, noise-corrected | stable once the peak has been observed |
| `L_onset` | first crossing of a noise band with a dwell requirement | stable once onset is observed |
| `T_recovery` | return to a noise-calibrated band **with a minimum dwell** | stable once recovery occurs |
| `C`, `U` | coverage / responsiveness / missing rows / drift contamination; per-axis uncertainty | carried separately, never folded in |

**A one-sample deviation must not disappear because the window is long** — which is exactly what the old RMS did.

## 5. Component-level verdicts (a partial profile is a valid result)

`ESTIMATED` · `LOWER_BOUND_ONLY` · `UPPER_BOUND_ONLY` · `INDETERMINATE` · `OUT_OF_SCOPE`

**Do not collapse a partial profile into one global abstention** unless every relevant axis is unavailable.
Limited-access collisions still return `EQUIVALENCE_CLASS_ONLY`. **There is never a metaphysical `SAME`.**

## 6. The benchmark construction — ground truth as a design parameter

Every case is `base` versus `base + ONE EXTRA PARALLEL PATH`. Because the readout is linear in the sites, the
accessible difference is **exactly that path's own response**:

```
delta_r(t) = w * x_path(t)
```

* **leaky path** -> rise-and-decay pulse, **asymptote zero**: a pure TRANSIENT difference;
* **integrator path** (self-coupling cancels the decay) -> the probe leaves a **PERMANENT step**: a pure PERSISTENT difference;
* **delayed path** -> the same discrepancy, arriving later: a pure LATENCY difference.

**The two dissociation controls, solved on the privileged traces and exact by construction.** A single leaky path
**cannot** dissociate peak from energy — measured, its shape factor `E/A^2` stays between 18 and 41 across `Tx` from
1 to 64, so one weight buys one constraint and the other follows; the best achievable peak ratio at equal energy
was **1.36**, which is a rounding error, not a control. Peak and energy only come apart when the **shape** comes
apart:

| extra path | E (w=1) | A_peak | shape factor E/A^2 |
|---|---|---|---|
| **SPIKE** (high-pass, 1 vs 3) | 2.57e5 | 192.5 | **6.9** |
| **BROAD** (cascade 30,30) | 1.20e6 | 145.9 | **56.1** |

* **EQUAL ENERGY** (broad weight 0.464): energy ratio **1.000**, **peak ratio 2.9x** -> the peak axis must separate.
* **EQUAL PEAK** (broad weight 1.319): peak ratio **1.000**, **energy ratio 8.1x** -> the energy axis must separate.

## 7. Drift versus slow causal response

The benchmark contains **drift without response**, **slow causal response without drift**, and **both together**.
Matched sham/baseline controls estimate the drift scale. **A slow causal response must not be removed as drift, and
drift must not become a persistent causal difference.** The instrument distinguishes them or abstains.

## 8. Split

`edlab/substrates/ctrans/manifests_crd.py`. Dev seeds `6xx`, prospective `7xx` — disjoint from every previous
namespace. Verified: no spec overlap between dev and prospective, and **no overlap with the historical sealed
fingerprint split**, which stays untouched as a historical asset and is **not** the prospective test here.
Reserved to the prospective set alone: an unseen cascade geometry. Prospective noise `1.4e-5`, unseen.

## 9. Development gates (all must pass to freeze)

**G1** window invariance under nested prefixes of ONE acquisition · **G2** a finite transient must NOT dilute as the
window grows · **G3** persistent differences remain detectable · **G4** single-axis cases do not contaminate
unrelated axes · **G5** the equal-energy and equal-peak controls separate on the **correct** axes · **G6** recovery
-> zero-compatible `P_inf`, nonzero transient history · **G7** noise-only repetitions create no causal components ·
**G8** drift-only creates no persistent difference, and a slow response is not eaten as drift · **G9** non-vacuity ·
**G10** construction truth and privileged truth agree · **G11** limited-access collisions ->
`EQUIVALENCE_CLASS_ONLY` · **G12** declared unit conversions change nothing while genuine gain stays visible.

## 10. Must-fail controls

historical RMS averaging dilutes finite transients · exact float inequality -> false differences · integer cast ->
false sameness · **omitting the persistent subtraction makes `E_trans` diverge for persistent differences** ·
**a final-sample-only persistence estimate misclassifies under noise** · peak-only confounds spike with plateau ·
energy-only confounds low-long with high-short · removing sham correction worsens drift performance · separately
simulated prefixes recreate the RNG confound · implementation labels leak · removing a discriminating probe creates
a collision.

## 11. Decision

PASS -> authorize (do not execute) `SC-PILOT-RESPONSE-DECOMPOSITION-PREFLIGHT`.
FAIL at development -> **do not touch the new prospective split**.
FAIL prospectively -> retire; the new hold-out is burned.
`BENCHMARK_INVALID` -> do not score; stop for strategic review; **do not automatically build version 01**.

The historical verdicts stand: v00 FAIL · v01 FAIL · v02 FAIL · v03 BENCHMARK_INVALID ·
**CONTINUOUS-FINGERPRINT BRANCH CLOSED — NO V04**.
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment.
