# INDEPENDENT CRITICAL REVIEW (adversarial, goal = reject)

| # | criticism | finding | disposition |
|---|---|---|---|
| 1 | Hidden positivity assumption in the lower bound | CONFIRMED: `argmax|v|` assumes `sign(lam·e)≥0`; fails 0/40 under amplification | **claim RETRACTED**, replaced by sign-agnostic bracket (T6′) |
| 2 | Ground-truth circularity | privileged evaluator imports no instrument code (verified); truth = noise/drift-free response | resolved |
| 3 | Favourable benchmark construction (only κ≥0 tested) | CONFIRMED: all historical dev+prospective used κ≥0 and g_i>0 | **limitation added**; negative/mixed-sign now in the adversarial suite |
| 4 | Code independence of replication | clean-room module imports numpy only; reproduces result AND flaw | resolved |
| 5 | Quantitative claim transfers across substrates | REFUTED: FHN clean-case q̂/q≈0.86 | claim narrowed to ctrans; structural claims general |
| 6 | Multiple testing across probes/components | max-over-probes is a for-all (worst case), median-over-phases; no per-probe cherry-pick | acceptable; documented |
| 7 | Statistical undercoverage | bracket 40/40 all regimes; historical point 0/40 under amplification | point rule undercovers → restricted |
| 8 | Selection bias from choosing a reference channel | the argmax selection is exactly the sign-sensitive step; bracket removes the selection | resolved by bracket |
| 9 | Hidden oracle access | references read only allowed fields; droplet POD confirmed no U/V read | resolved |
| 10 | Transfer inflation | droplet transfer already FAIL; FHN quantitative fail documented | no inflation |
| 11 | Figure/claim selectivity | claim-scope table lists falsifier per claim; retracted claim shown | resolved |

## Publication-blocking items
- The frozen CRD-03 instrument emits `LOWER_BOUND_ONLY`/`CORRECTED` under an undeclared sign contract. Until the
  operational rule is replaced by the bracket + sign-contract admission, the instrument's guarantees are unsound
  outside `sign(lam·e)≥0`. **BLOCKING for a "peer-review submission" claim.**
- Quantitative accuracy is ctrans-specific (FHN 0.86). A "general continuous metrology" claim is **not** supported.

## Not blocking (solid)
The identifiability *structure* (differential identifiable, common-mode not, collinear abstains, bracket covers)
reproduces independently and transfers structurally. This is a genuine, publishable methods-and-limits result once
the sign contract is incorporated.
