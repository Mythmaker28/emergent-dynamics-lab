# EXP-SC-HISTORY-MATERIAL-CONTINUITY-00 — DEVELOPMENT RESULTS

Raw: `results/sc_hmc/records_dev.pkl`, `results/sc_hmc/analysis_dev.json`, `results/sc_hmc/final_report.json`.
Figure: `results/sc_hmc/EXP_SC_HMC_00_figures.png` (turnover curves · axis discrimination · predictive NRMSE).
Development seeds 9401–9412 (12 valid). Prospective 9501–9516 **NOT executed (preserved)**.

## Material-turnover curves (deliverable 13)
M_early mean 0.560 → M_tc mean 0.265 (min 0.228, max 0.326). **12/12 below M_low = 0.35.** Curves
(capability seeds): 0.73 → 0.49 → 0.34 → 0.28 over 200→700 steps. Half-life ≈ 268 steps. Real exchange
(labelled leaving, new entering), partition-robust.

## Organizational-axis trajectories (deliverable 14) — per-seed distance to OWN earlier axis
Win rate = fraction of 12 seeds where H is strictly closer to its own past than the named control.

```
axis   H-vs-P  H-vs-M  H-vs-U   individuation-AUC
P1      0.00    0.00    0.08     -            (geometry shared by construction with P and M)
P2      1.00    1.00    0.50     0.65 (weak)  (evolved != reset, but NOT history-individuating)
P3      0.58    0.67    0.50     -
R (P4)  0.50    0.58    0.58     0.52 (none)  (causal response carries no history signature)
```
P5 recovery and P6 path are H-only diagnostics (recovery reconverges to a co-evolved control; path
continuity high) and do not discriminate history. **Axes history-specifically within regime: 0 (≥3 required).**

## History-vs-material predictive comparison (deliverable 15)
LOO k-NN, target = future causal-response profile, baseline (predict mean) = 1.000:
A material 1.074 · B snapshot 1.148 · C history 1.069 · D full 1.169. **No model beats baseline.**
History provides no predictive advantage over snapshot or material.

## Counterfactual control results (deliverable 16)
Exact-clone stochastic ceiling < H's own drift in **12/12** (reproducibility valid, K4/G5). Material-only
trap (arm M) reproduces H's response (d_M ≈ d_H) — material overlap not counted as continuity (K5).
Shape-only trap (arm P) preserves geometry, differs internally (K6). Unrelated arm U indistinguishable
from H relative to its past (K8). Full K1–K10 table in `final_report.json`.

## Partition-robustness analysis (deliverable 17)
M is stable across detector thresholds {0.25, 0.30, 0.35} (≤ 0.006 spread). The negative result is not
produced by one arbitrary segmentation — the history signal is absent, not marginal.

## Development gates (deliverable 10)
**11/12 pass.** Fail: **G10 (history signal)** — no model beats baseline; 0 history-specific axes.
G1 entity · G2 turnover · G3 passivity · G4 responsiveness · G5 clone · G6 phenotype-reset · G7
material-reset · G8 axis-independence · G9 partition · G11 non-vacuity · G12 truth-independence: PASS.
Per protocol the prospective hold-out is preserved.
