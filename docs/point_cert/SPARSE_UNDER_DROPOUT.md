# SPARSE CONTAMINATION UNDER NOISE AND DROPOUT (deliverable 3) — EXP-GT-PC-00
Deterministic T6-D: with m references, at most s contaminated, differential and non-collinear, a clean
majority is identifiable when m − s ≥ 2, and point-identified (by agreement) when m ≥ 2s + 1.

## Restatement under noise, missingness and dropout
Let the m references split into: v valid-and-observed, c contaminated, d dropped-out (missing/gain/flatline).
Only the v valid references carry a usable clean signal.
* **Point identification requires** a clean MAJORITY that is *observable*: v − c_eff ≥ 2 where c_eff counts
  contaminated references NOT yet excluded, AND the clean set must survive removal of any single reference
  (leave-one-reference-out, C4). Sufficient operational condition: v ≥ 2s + 1 + d, i.e. every potential
  dropout must be *budgeted* as if it could be a hidden contaminant.
* **Missing/dropout references are NOT counted toward the clean majority.** A dropout masquerading as a
  small clean channel is excluded by C2; if it cannot be excluded, its membership ambiguity widens the set
  (C4) and forbids a point.
* **Near the breakdown point** (v − s small), the selection-aware uncertainty (C6) grows sharply and the
  leave-one-reference-out shift (C4) exceeds tolerance — the layer refuses the point and returns the set.
* **The sparsity budget s may not come from hidden benchmark truth** (C1). In the blind arm, s must be an
  externally declared bound (sensor-physics / intervention geometry); otherwise no sparse point is certified.

## Consequence
The historical sparse/dropout point failures arose from treating a data-driven "clean majority" as fixed
when it was selected under noise. Budgeting dropouts as potential contaminants and enforcing leave-one-out
stability converts those failures into refusals or widened sets (verified: 21 SELECTION_INSTABILITY + 4
DROPOUT refusals across the 57 regressions).
