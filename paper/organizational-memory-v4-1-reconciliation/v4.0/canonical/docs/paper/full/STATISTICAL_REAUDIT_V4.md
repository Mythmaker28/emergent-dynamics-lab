# Statistical re-audit V4 — canonical committed pipeline

Every longitudinal number in the V4 manuscript is produced by `python -m reproduction.primary` (module
`reproduction/decode.py` + `reproduction/primary.py`), reading only the committed raw file
`results/observer/tca_holdout_raw.pkl`. No new simulation. Deterministic.

## 1. Data
- **Seeds (3, untouched, sealed):** 38502, 38503, 38504. Disjoint from every development seed (32xxx–38501).
  Seed 38501 was the tracker-incident/development seed and is excluded as primary.
- **Histories (12, prospective, held-out):** each history applies an early and a late environmental drive of
  amplitudes (a_early, a_late); the decoded coordinates are h1 = a_early + a_late (cumulative dose) and
  h2 = a_late − a_early (temporal order). Exact values (constant per history, replicated across the 3 seeds):

  | hi | h1 | h2 |  | hi | h1 | h2 |
  |---|---|---|---|---|---|---|
  | 0 | +0.0151 | −0.0028 | | 6 | +0.0352 | −0.0033 |
  | 1 | +0.0225 | +0.0071 | | 7 | +0.0233 | −0.0058 |
  | 2 | +0.0216 | +0.0098 | | 8 | +0.0276 | −0.0120 |
  | 3 | +0.0181 | +0.0037 | | 9 | +0.0181 | +0.0053 |
  | 4 | +0.0288 | +0.0024 | | 10 | +0.0297 | −0.0092 |
  | 5 | +0.0183 | +0.0079 | | 11 | +0.0085 | −0.0015 |

- **Records:** 12 histories × 3 seeds = 36 tracked entities.
- **Checkpoints (integration step → mean M):** 0 → 1.00, 400 → 0.39, 650 → 0.25, 800 → 0.19.
- **M (turnover) definition:** the surviving fraction of the entity's *original* material, tracked by a passive
  cohort field (PulseChaseTracer) that labels material present at t=0 and follows its dilution by
  growth/death; M = (original-cohort mass inside the tracked entity) / (total entity mass). M is independent
  of h1/h2/labels.

## 2. Feature vector (11-D, per entity, at a checkpoint)
Concatenation of the 10-D memory order-statistics [mean, std, p10, p50, p90] of the intensive memory
components m1 then m2 over the entity's cells, plus the m_minus dispersion mminus_std = std over entity cells
of (m1 − m2). These are precomputed in the raw file (`ck[step]['long'] = (feat10, M, size, mminus_std)`);
`reproduction/decode.features_from_long` assembles the 11-D vector.

## 3. Decoder
- **Model:** ridge regression, **alpha (λ) = 1.0**.
- **Cross-validation:** **grouped leave-one-history-out** — 12 folds; each fold holds out all records of one
  history (3 seeds) and trains on the other 11 histories (33 records). The grouping unit is the history, so a
  held-out history's coordinate is never seen in training (no leakage across seeds of the same history).
- **Aggregation level:** predictions are collected out-of-fold for all 36 records; R² is the **pooled
  coefficient of determination** over the 36 held-out predictions (not a per-history mean). Grouping enters
  through the fold definition and the bootstrap unit, not through averaging the target.
- **Scaling:** per fold, features are centred and scaled by the **training-fold** mean/std; columns with
  zero training std are dropped. No target scaling. Fit on train only; applied to the held-out fold.
- **Score:** R² = 1 − Σ(y − ŷ)² / Σ(y − ȳ)², ȳ = mean over all 36 true targets.

## 4. Uncertainty (bootstrap)
- **Resampling unit:** the history (donor group) — 12 histories resampled **with replacement**.
- **Duplicate handling:** a history drawn k times contributes its 3 records k times, and each drawn copy is
  assigned a **distinct fold id** (via `enumerate`), so duplicated groups are treated as independent folds in
  the leave-one-out CV of that bootstrap replicate (they cannot leak into each other's training fold).
- **Replicates:** **n_boot = 3000**. **Seed:** `numpy.random.default_rng(20260715)` (fixed → deterministic).
- **Interval:** percentile method, 2.5th and 97.5th percentiles of the 3000 bootstrap R² values.
- Singular bootstrap designs (LinAlgError) are skipped (rare; does not affect determinism of the seed stream).

## 5. Canonical results
| checkpoint | mean M | h1 R² | h1 95% CI | h2 R² | h2 95% CI |
|---|---|---|---|---|---|
| initial | 1.00 | 0.78 | [0.56, 0.94] | 0.80 | [0.53, 0.92] |
| moderate | 0.39 | 0.93 | [0.89, 0.98] | −0.03 | [−0.68, 0.57] |
| deep−1 | 0.25 | 0.90 | [0.86, 0.97] | −0.05 | [−0.53, 0.46] |
| **deep** | 0.19 | **0.89** | **[0.84, 0.96]** | **−0.24** | **[−0.78, 0.32]** |

Exact deep values: h1 = 0.8878 [0.8366, 0.9581]; h2 = −0.2394 [−0.7850, 0.3182]. Survival 36/36; switches 0.
Tracker-independence: the same decode on the `largest-at-each-frame` tracker gives deep h1 = 0.91, versus the
longitudinal 0.89 — comparable, i.e. h1 is tracker-independent (the imposed history is global, not per-blob).

## 6. Gates
- **h1 deep-turnover CERTIFIED:** held-out R² lower bound 0.84 > 0.50 (and > 0).
- **h2 deep-turnover NOT ESTABLISHED:** the 95% CI [−0.78, 0.32] does not clear 0.50 (indeed the point is
  below 0). This bounds the C1c architecture and this dispersion metric; it is not a demonstrated absence of
  all order information, nor a substrate-level impossibility.

## 7. Automatic canonical test
`python -m reproduction.test_canonical` asserts the four frozen numbers within tolerance:
h1 deep = 0.89 ± 0.06, CI [0.84 ± 0.08, 0.96 ± 0.08]; h2 deep = −0.24 ± 0.06, CI [−0.79 ± 0.10, 0.32 ± 0.10];
survival = 36/36 (exact); switches = 0 (exact). Status at time of writing: PASS.
`python -m reproduction.primary --check` additionally asserts every checkpoint value against
`reproduction/EXPECTED.json`.

## 8. Provenance statement
Prospective, held-out trajectories analysed using a **retrospectively standardized, fully committed
pipeline**. The prior inline scoring that produced the historical 0.98/0.34 was never committed and is not
recoverable (see `HEADLINE_NUMBER_ERRATUM.md`). No new simulation was executed for this re-audit.
