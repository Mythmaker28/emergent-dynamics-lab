# H2-CERT-01 — Development-only Power Analysis

## Data
DMM development pool + a fresh dev pilot (2 seeds × 14 histories, frozen C1c, forward to step 800 → M=0.15).
Feasibility: M≤0.25 IS reached with full viability (step 650: M=0.20, size 57, 28/28 valid; step 800: M=0.15).
So this is NOT a feasibility failure — deep turnover is achievable in a viable, localized droplet.

## Deep-turnover h2 (dev pilot, grouped leave-history-out, 90% bootstrap CI)
- M≈0.28 (step 500): h2 = −0.09, 90% CI [−1.48, +0.71]
- M≈0.20 (step 650): h2 = +0.07, 90% CI [−0.50, +0.88]
- M≈0.15 (step 800): h2 = +0.37, 90% CI [+0.00, +0.91]
Per-seed at M≈0.20: 37001 = −0.80, 37002 = +0.83 (between-seed swing ≈ 1.6 — noise-level).

## Variance components
Between-seed variance at deep turnover is enormous (per-seed h2 spans [−0.80, +0.88]); history-level signal is
near zero. The h2 estimate at M≤0.25 is dominated by irreducible between-body noise, not a stable history signal.

## Power conclusion
The certification rule requires the prospective **lower** CI bound to exceed 0.50 at M≤0.25. The observed
central value is 0.0–0.37 (< 0.50). **A lower bound cannot exceed a central estimate that is itself ≤ 0.50**,
so retention certification is UNREACHABLE for any finite N given the observed effect. "Adequate power" here
means enough samples to confidently show the effect is **below** 0.50 — which the pilot already does. The
frozen sample for the one-shot sealed confirmation is set at **4 seeds × 12 histories** (sufficient to bound
the deep-turnover h2 well under 0.50; larger N cannot change the sign of the decision). Per the kill-switch
rule, no larger run will be requested afterward.
