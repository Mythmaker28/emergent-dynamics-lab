# SET-VALUED STATISTICAL AUDIT (deliverable 6) — EXP-GT-PC-00 prospective (N=10000)
Computed from raw rows (`results/EXP-GT-PC-PROSPECTIVE/set_statistical_audit.json`). We distinguish
MARGINAL coverage (mixture-averaged), CONDITIONAL diagnostics (per regime), EMPIRICAL guarantees (measured
here), and EXACT guarantees (proved). No empirical number is promoted to a universal theorem.

## Marginal coverage (EMPIRICAL) — meets the preregistered ≥95% gate
| arm | coverage | Wilson95 | cluster95 (by stratum) | non-identifiable rate | abstain rate |
|---|---|---|---|---|---|
| O (conditional) | 8967/9346 = 0.9594 | [0.955,0.963] | [0.956,0.963] | 0.079 | 0.065 |
| B (blind)       | 5221/5389 = 0.9688 | [0.964,0.973] | [0.964,0.973] | 0.388 | 0.461 |
Arm B abstains far more (NON_IDENTIFIABLE 39%) — honest: with only operational contracts, most cases are
not identifiable and correctly return no finite set.

## Conditional diagnostics (the honest caveat)
Coverage is NOT uniform. It falls on the stable-contamination direction:
* by SNR: Arm O `<=5` 0.973, `5-10` 0.967, `10-30` 0.952, **`>30` 0.919**; Arm B similar (`>30` 0.919).
  High SNR REDUCES set coverage — the selection-aware widening shrinks when all channels are precise,
  so a stable contamination bias is no longer covered (the stable-bias impossibility reaching the set).
* by regime (Arm O worst): **`contaminated_highSNR` 0.798**, `dropout_post_intervention` 0.79,
  `all_contaminated` 0.936, `sparse1` 0.948.
* by reference count: `m=3` 0.932 (least leave-one-out widening) vs `m>=4` ≥0.98.
* dropout/sparse subset 0.949–0.963 (meets ~95%); clean/other 0.967–0.974.

## Interpretation
The set instrument's MARGINAL coverage under the declared mixture is ≥95% (empirical, both arms). Its
guarantee is NOT uniform: conditional coverage on the contamination-collinear direction at high SNR is
~0.80–0.92. This is the Stable-Bias Impossibility (STABLE_BIAS_IMPOSSIBILITY.md) reaching even the set:
without an external anchor, high-SNR precision shrinks the honest set below the truth's offset. The paper
claims MARGINAL empirical set coverage under the declared contract/noise mixture — NOT a universal or
per-regime theorem, and NOT point identification.

## Exact guarantees (proved, not empirical)
* No false exact-zero from data (structural: exact zero requires a structural null contract). Verified 0/10000.
* Under the declared contract, Q is a valid simultaneous confidence set for the noise-free magnitudes by
  construction (T6 propagation of simultaneous channel CIs) — the coverage of Q is inherited from the
  channel CIs; where channel CIs are biased (stable contamination), Q inherits that bias. This is exact and
  is precisely why marginal, not uniform, coverage is the honest claim.
