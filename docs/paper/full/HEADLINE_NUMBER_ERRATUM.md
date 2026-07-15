# Headline-number erratum (V3 → V4)

**Status of the old numbers: HISTORICAL, NON-REPRODUCIBLE. Superseded by the canonical committed pipeline.**
No new physics and no new simulation were run to produce this erratum; the change is purely one of analysis
provenance. The underlying data are the *same prospective, held-out trajectories* (untouched sealed seeds
38502/38503/38504); only the scoring pipeline changed, from an uncommitted ad-hoc script to the committed,
deterministic `reproduction/` package.

## 1. Old (historical) numbers — as printed in V1–V3
| quantity | historical value | where it appeared |
|---|---|---|
| h1 deep-turnover held-out R² | **0.98**, 95% CI **[0.97, 1.00]** | abstract, results, Table (results/tracker/gates), Fig. 3b/4, discussion, conclusion, supplement |
| h1 initial held-out R² | 0.92 [0.86, 0.99] | results/tracker paragraph |
| h2 deep-turnover held-out R² | **0.34**, 95% CI **[−0.89, 0.87]** | abstract, results, tables, Fig. kill-switch, discussion |
| tracker-sensitivity h1 (largest / 2nd / longitudinal) | 0.96 / 0.98 / 0.99 | results/tracker paragraph, sensitivity table |

## 2. Why they are non-reproducible
The exact decoding/scoring script that produced `0.98` / `0.34` was executed inline in an earlier working
session and **was never committed** to the repository. Only its *outputs* (the numbers) and the raw
trajectory data (`results/observer/tca_holdout_raw.pkl`) survive. The transformation from raw features to
those specific R² values cannot be regenerated from committed code.

## 3. Search performed to recover the original pipeline
Against the committed holdout features, the following decoders were implemented and evaluated; **none**
reproduces `0.98` / `0.34` (all reproduce the same *conclusions*):
- grouped leave-one-history-out ridge, λ ∈ {3, 1, 0.3, 0.1, 0.03, 0.01};
- leave-one-seed-out ridge;
- k-nearest-neighbours, k ∈ {3, 5};
- per-history-aggregated R² (12 history means);
- `largest-at-each-frame` tracker features (vs the longitudinal tracker);
- feature sets: 10-D memory stats; +mminus_std; +size.

Reproduced deep-turnover values cluster at **h1 ≈ 0.89** (always CERTIFIED, lower bound ≫ 0.50) and
**h2 ≈ −0.24 … +0.04** (always ≤ 0.50, not established). The exact `0.98`/`0.34` are not recoverable.

## 4. New canonical numbers (from `python -m reproduction.primary`)
Deterministic (fixed bootstrap seed 20260715); byte-identical in a clean-room rerun.
| checkpoint | mean M | h1 R² [95% CI] | h2 R² [95% CI] |
|---|---|---|---|
| initial | 1.00 | 0.78 [0.56, 0.94] | 0.80 [0.53, 0.92] |
| moderate | 0.39 | 0.93 [0.89, 0.98] | −0.03 [−0.68, 0.57] |
| deep−1 | 0.25 | 0.90 [0.86, 0.97] | −0.05 [−0.53, 0.46] |
| **deep** | **0.19** | **0.89 [0.84, 0.96]** | **−0.24 [−0.78, 0.32]** |
| track survival | — | 36/36 | (shared) |
| reassignment switches | — | 0 | (shared) |
Exact deep values: h1 = 0.8878, CI [0.8366, 0.9581]; h2 = −0.2394, CI [−0.7850, 0.3182]. Two-decimal
rounding gives the deep-h2 lower bound as **−0.78** (the mission brief's "−0.79" is the same interval rounded
one unit differently; the committed pipeline value governs).

## 5. Exact canonical pipeline
`reproduction/decode.py` + `reproduction/primary.py`: features = 10-D per-entity memory order-statistics
[mean, std, p10, p50, p90] of (m1, m2) plus the m_minus dispersion (mminus_std) → 11-D; decoder = ridge
(λ = 1.0) under **grouped leave-one-history-out** cross-validation (fold = one of 12 histories); R² = pooled
coefficient of determination over held-out records; uncertainty = donor-level (history-grouped) percentile
bootstrap, n_boot = 3000, seed = 20260715. Full spec in `STATISTICAL_REAUDIT_V4.md`.

## 6. Impact on each conclusion
| conclusion | change | still holds? |
|---|---|---|
| h1 retained through deep turnover (the load-bearing result) | point 0.98 → **0.89**; CI [0.97,1.00] → **[0.84,0.96]** | **YES — still CERTIFIED** (lower bound 0.84 ≫ 0.50) |
| h1 causal necessity (inert/erase carry no information) | unchanged (deterministic) | YES |
| h1 causal sufficiency magnitude (transplant 0.61, wide CI) | unchanged; separate causal experiment | YES (still "supported, wide") |
| h1 is global / non-individuating | unchanged | YES |
| h2 deep-turnover retention not established | point 0.34 → **−0.24**; still ≤ 0.50 | **YES — conclusion identical** |
| mechanism of h2 non-persistence indeterminate | unchanged | YES |
| individuation not supported | unchanged | YES |

**No conclusion is overturned.** The headline h1 number is smaller (0.89 vs 0.98) but the certification (and
every qualitative claim) is unchanged.

## 7. Explicit statements
- **No new simulation was executed.** The trajectories are the original prospective, held-out runs.
- The analysis pipeline was **retrospectively standardized** and is now fully committed (`reproduction/`).
- The old numbers may appear **only** in this erratum and equivalent clearly-labelled historical notes; they
  are removed as canonical results everywhere else.
