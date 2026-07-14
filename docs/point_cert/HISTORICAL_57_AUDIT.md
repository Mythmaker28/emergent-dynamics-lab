# HISTORICAL 57-CASE AUDIT (deliverable 1) — EXP-GT-PC-00
The 57 NASI invalid-point cases replayed through the frozen point-certification layer (`pcregressions.py`):
* catastrophic cases (2) — both **REFUSED** (mandatory load-bearing controls);
* catastrophic invalid certificates issued — **0**;
* points issued — 8 (6 valid, 2 near-edge invalid ≤ 2% miss, counted in coverage, none catastrophic);
* selection-aware set Q_wide contains truth — 45/57 (the residual 12 are the adversarial tail NASI itself
  missed; Q_wide widens them but cannot always reach truth without more information — correctly no point);
* refusal reasons — ORACLE_CONTRACT 17 (Arm-O truth contracts), SELECTION_INSTABILITY 21, INSUFFICIENT_SNR 5,
  DROPOUT 4, CERTIFICATE_FAILED (diameter) 2.
Interpretation: the two mechanisms that caused the catastrophic dropout failures (a dead channel selected as
the min; a clean majority mis-selected under noise) are caught by C2 (dropout) and C4 (leave-one-reference-out).
These cases are development regressions and are never used prospectively again.
