# EXP-SC-HISTORY-MATERIAL-CONTINUITY-00 — INTERPRETIVE ERRATUM

Issued by EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00. **Raw results are unchanged** (records_dev.pkl,
analysis_dev.json, final_report.json, figures). Only the *interpretation* of the verdict is corrected.

## What was wrong
The original verdict was reported as `FAIL — SNAPSHOT SUFFICIENT`. That label is **not supported by the
data**, because the snapshot regression (B), the history regression (C), the material regression (A) and
the full-state regression (D) **all performed worse than the mean baseline** (NRMSE 1.148 / 1.069 / 1.074
/ 1.169 vs 1.000). "Snapshot sufficient" asserts the snapshot captures the future; a model that loses to
predicting the mean cannot support that assertion. The original report did flag this as an "alternative
reading," but it should have been the verdict, not a footnote.

## Corrected interpretation
- **`FAIL — NO HISTORY-SPECIFIC CAUSAL PERSISTENCE DETECTED`** — the well-powered per-axis and
  within-vs-between individuation analyses (n=12) show the entity's organization and causal response are
  no closer to the entity's own past than to an unrelated evolved entity's past (P2 win-rate vs unrelated
  0.50; causal-response individuation AUC 0.52). This is the defensible negative.
- **`PREDICTIVE COMPARISON: INDETERMINATE — NO MODEL BEATS BASELINE`** — the small-n LOO regressions are
  underpowered; none beats the mean, so no ordering among material/snapshot/history/full is interpretable.

## Consequence
Snapshot-sufficiency was neither established nor is it the right frame. Whether the substrate contains a
usable hidden causal state is left **open** and is the subject of EXP-SC-HIDDEN-STATE-CAUSAL-
INDIVIDUATION-00, which replaces underpowered regression with matched counterfactual pairs and direct
causal-divergence tests.
