# Statistical Re-audit (V2 -> V3), recomputed from committed raw data

Method: grouped leave-one-history-out ridge (lambda = 1.0); resampling unit = history (donor group);
n_boot = 3000; percentile 95% CI; features = 10-D per-entity memory statistics [mean, std, p10, p50, p90] of
(m1, m2). No new simulations. Raw: results/{observer,wd01_phasec,h2cert}/*.pkl.

## 1. h2 kill-switch (longitudinal, untouched seeds 38502-38504, n = 12 histories)
| checkpoint | h2 point | 95% CI | pre-specified test |
|---|---|---|---|
| M ~ 0.39 | +0.59 | [-0.33, +0.93] | upper bound > 0.50 |
| M ~ 0.25 | +0.41 | [-1.13, +0.90] | upper bound > 0.50 |
| M ~ 0.19 | +0.34 | [-0.89, +0.87] | upper bound > 0.50 |

Interpretation (corrected): the 95% CI spans the 0.50 threshold at every deep checkpoint, and the point estimate
at M ~ 0.39 is itself 0.59. Therefore neither a lower-bound-above-0.50 (certification) nor an upper-bound-below-0.50
test is satisfied. **h2 deep-turnover retention is NOT ESTABLISHED (did not meet the certification criterion); it is
NOT falsified.** Prior V2 wording ("falsified", "confirmed failure", "h2 is transient") is withdrawn.

## 2. h1 (reference) longitudinal deep turnover
h1 at M ~ 0.19 = +0.98, 95% CI [+0.97, +1.00]. **Statistically established** (lower bound far above 0.50).

## 3. h1 causal (Phase C, n = 12 histories)
| quantity | point | 95% CI | reading |
|---|---|---|---|
| mean-transplant decode of h1 | +0.61 | [-0.69, +0.87] | positive point; wide CI (crosses 0) |
| in-place dR (full - inert) decode of h1 | +0.50 | [-1.39, +0.92] | positive point; wide CI |
| active-minus-inert (full - both0) | +0.61 | [-0.69, +0.87] | same as transplant |
| memory-inert control (both = 0) | -0.19 | [-0.19, -0.19] | deterministic: no history information |
| erase (Mf = 0) -> baseline read | -0.19 | [-0.19, -0.19] | deterministic: no information |

Interpretation (corrected): causal **necessity** is clean and deterministic --- with the memory ablated (inert
control) or erased, the standardized-body response carries no h1 information (R^2 = -0.19 with zero-width CI). Causal
**sufficiency magnitude** (transplant R^2 = 0.61) is a positive point estimate but with wide uncertainty at n = 12
(CI crosses zero). Authorized wording: "h1 is causally expressed (necessity established: the memory-inert/erase
controls carry no information) with a positive but statistically uncertain sufficiency magnitude (R^2 = 0.61, 95% CI
[-0.69, 0.87])." V2's unqualified "established" for the causal magnitude is downgraded to "supported with wide uncertainty."

## 4. h1 internal memory vs body size+mass (H2-CERT sealed)
| checkpoint | memory | size+mass |
|---|---|---|
| M ~ 1.00 | +0.94 [+0.89, +0.99] | +0.86 [+0.70, +0.96] |
| M ~ 0.21 | +0.93 [+0.83, +1.00] | +0.64 [+0.51, +0.98] |

Interpretation (corrected): the point estimates suggest internal memory retains more history information than body
size+mass after turnover (0.93 vs 0.64), but the 95% CIs overlap (memory [0.83,1.00] vs size+mass [0.51,0.98]).
Authorized wording: "suggestive but not statistically separated at n = 12." V2's "exceeds body baselines" is
downgraded to "point estimate favours internal memory; CIs overlap."

## 5. Power paragraph correction
V2 asserted that a pilot point estimate at/below threshold implies no sample size can raise the lower confidence
bound above it. This is incorrect: a point estimate below threshold does not imply the true value is below threshold,
and additional donors could raise the estimate. Correct statement: at n = 12 the deep-turnover h2 estimate is too
uncertain (CI spans the threshold) to certify or refute; deciding the question would require substantially more
donor histories, which we did not run (no new simulation was authorized).

## Summary of evidence tiers
- STATISTICALLY ESTABLISHED: h1 decodable at rest (0.94 [0.89,0.99]); h1 retained through deep turnover longitudinally
  (0.98 [0.97,1.00]); causal necessity (inert/erase carry no information; deterministic); backward-compat / no-leakage.
- SUPPORTED, WIDE UNCERTAINTY: h1 causal sufficiency magnitude (transplant 0.61, in-place 0.50); memory-vs-size+mass advantage.
- NOT ESTABLISHED / INDETERMINATE: h2 deep-turnover retention (CI spans 0.50); mechanism of h2 non-persistence.
- FALSIFIED: none of the load-bearing claims (the earlier "h2 falsified" is itself withdrawn as unsupported).
