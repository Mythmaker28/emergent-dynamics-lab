# PROSPECTIVE AUDIT — EXP-GT-PC-00 (N=10000, frozen, executed once). Deliverables 12,13,14,15.
Frozen `pointcert.py` `8c1bf736...`; generator `pcprospgen.py` `832dc4c7...`; NASI `3027044479...` (unmodified,
hash-gated). Committed at `0ce70cb` BEFORE the run. 40% dropout/sparse; SNR oversampled low. No post-hoc tuning.

## Hard safety endpoints — PASS
* false exact-zero on nonzero cases: **0 / 10000**, both arms.
* **CATASTROPHIC invalid point certificates (miss > 0.5): 0 / 127 issued** — the load-bearing gate.
* dropout: 0 catastrophic on any dropout case (1 near-edge dropout miss).

## Set-valued layer (primary) — PASS
| arm | set coverage | Wilson95 | dropout/sparse subset | other |
|---|---|---|---|---|
| O (conditional) | 8967/9346 = 0.9594 | [0.955,0.963] | 0.949 | 0.967 |
| B (blind)       | 5221/5389 = 0.9688 | [0.964,0.973] | 0.963 | 0.974 |
Selection-aware set coverage is ≥95% overall AND on the dropout/sparse subset, both arms. `blind_used_truth = 0`.

## Point-certification layer — COVERAGE GATE FAILS -> claim withdrawn
Arm B issued 127 certificates; **point coverage = 101/127 = 0.795** (Wilson [0.717, 0.856]) — materially
below the preregistered 95% target. Arm O issued 0 (C1 forbids truth-contract points — correct).
Miss distribution (26 misses): median 3.5%, p90 15.8%, **max 25.9%, catastrophic 0**.
Coverage by regime (the diagnosis):
* `contaminated_highSNR`: **7/23 = 0.30** — the culprit. Strong contamination at high SNR yields a
  STABLE, PRECISE, but BIASED estimate that passes every stability (C4/C5) and SNR (C8) certificate.
* everything else covers near-perfectly: clean_strong 22/22, sparse1 18/19, all dropout variants 4/4,
  no_dropout 9/9, weak 5/5, collinear 5/5.
The certificates catch INSTABILITY (dropout, selection) and IMPRECISION (low SNR) but NOT stable
high-SNR contamination bias. Independent replication (C7): certified-interval overlap 120/120 = 1.000, so
the shortfall is a property of the estimate/contract, not the interval method.

## Verdict on this hold-out
Hard safety gates PASS (0 false-zero, 0 catastrophic, set coverage ≥95%). The point-certification coverage
gate FAILS (0.795 < 0.95). Per the stop rule ("point coverage materially underperforms -> withdraw point
claims, retain the set method"), POINT CERTIFICATION is WITHDRAWN. The hold-out is NOT burned (zero
catastrophic); the SET-VALUED instrument is validated on a fresh N=10000 hold-out including 40% dropout/sparse.
