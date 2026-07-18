# PROSPECTIVE HOLD-OUT AUDIT — EXP-GT-NASI-00 (N=5000, frozen, executed once)
Deliverables 15,16,17,18. Instrument frozen at nasi.py `3027044479...`; generator `prospgen.py`
`aa264b2e...`; both committed at `33ef80e` BEFORE this run. Runner hash-gated. NO post-hoc tuning.

## Primary safety endpoint — the historical failure mode
**False `{0}` on a nonzero case: 0 / 5000, BOTH arms.** The catastrophic historical failure
(non-detection converted to an exact-zero claim; 586/1333 on the burned sign-safe hold-out) is
ELIMINATED. Exact one-sided 95% upper bound on the false-`{0}` rate ≈ 0.0006.

## Coverage (dependence-aware)
| arm | emitted | coverage | Wilson95 | cluster95 (by stratum) | worst stratum |
|-----|--------:|---------:|----------|------------------------|---------------|
| O (conditional) | 2979 | 0.9856 | [0.981,0.989] | see cluster_audit.json | — |
| B (blind)       | 1805 | 0.9629 | [0.953,0.971] | see cluster_audit.json | — |
Coverage by SNR band ≥ 0.95 in EVERY band including low-SNR (Arm O 0.5–5: 0.985; Arm B 0.5–5: 0.972).
Low-SNR coverage (the burned instrument's failure regime) is fully within target. `blind_used_truth = 0`
in both arms (no oracle leakage).

## The gate that FAILS: invalid confident points
Preregistered HARD gate 1 = "zero invalid POINT verdicts". Observed: **57 invalid points** (Arm O 17 /
216 points; Arm B 40 / 149 points). Forensics (`invalid_point_forensics`):
* relative miss: median 0.02, p90 0.24, max 0.65;
* 50 / 57 are benign near-edge tail misses of a 95% CI (median 2% outside the interval edge);
* **2 / 57 are catastrophic** (relative miss > 0.5): both ARM B, `dropout`, low-SNR — a POINT picked a
  dead/contaminated channel and confidently reported ≈0.3 when the truth was ≈0.6–0.9. This is the SAME
  CLASS as the historical over-confident assertion (now 2/5000 = 0.04%, vs the historical 44%).
* concentration: `dropout` (20) and `sparse1` (13) dominate; some occur at HIGH SNR (up to 98) → these
  are SYSTEMATIC point-misidentification under contamination, not statistical tail misses.

## Non-vacuity (secondary; never overrides safety)
Arm O: 216 points, 702 one-sided bounds, 2021 abstentions, median finite width 1.15×|q|.
Arm B: 149 points, 547 one-sided bounds, 3195 abstentions, median width 1.14×|q|.
The blind arm abstains far more (honest: less information), and emits proportionally fewer points.

## Verdict on this hold-out
By the preregistered hard gate (zero invalid confident points), **the prospective hold-out FAILS**. Per
the stop rules it is now BURNED: the instrument is NOT patched and NOT re-run on it. Two findings stand:
1. the noise-aware repair of the `{0}` failure SUCCEEDED completely (0/5000, ≥95% set/bound coverage);
2. point-identification under reference dropout / sparse contamination is NOT safe and is WITHDRAWN.
A point-suppressed, set-and-bound-only variant (same frozen sets, POINT re-labelled INTERVAL) would have
0 hard-gate violations here, but claiming it requires a FRESH preregistered hold-out — it is NOT claimed
on this burned one.
