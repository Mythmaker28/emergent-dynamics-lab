# LOBO_VS_LODO_AUDIT — correct-unit stability of FWL2_RELATIVE_QUOTIENT_BASIS_V1

Append-only corrigendum. The immutable V1 object is **not** modified.

## 1. What SQDT00 actually removed — from the code, not the prose

SQDT00's stability loop (`sq_offline.py`) is:

    for dleft in range(16):
        keep = [i for i in range(n) if D_OF[i] != dleft]
        ...

`D_OF` maps each of the 32 rows to its **descendant** index (0..15). Each fold therefore removed
**one descendant = 2 rows**, over **16 folds**. This is **leave-one-DESCENDANT-out (LODO)**, and
the reported *maximum leave-one-descendant-out angle of 3.14 degrees* is a 16-fold descendant
statistic.

The independent unit of this experimental line is the **upstream ancestry block**, not the
descendant. FWL2CF00 has:

    4 ancestry blocks : 65000, 65001, 65002, 65003
    16 descendants    : block x {FAR,NEAR} x {alloc a0,a1}   (4 per block)
    32 rows           : descendant x {CARRIER_1, CARRIER_2}  (8 per block)

**Verdict: SQDT00's stability audit is `INCORRECT_LODO`.** No transfer license is inherited from
it. The correct audit removes one complete ancestry block (4 descendants, 8 rows) per fold — four
folds — and is computed here. `TRUE_ANCESTRY_BLOCK_ROW_MAP.json` records the exact kept/omitted row
sets for all four folds.

## 2. The corrected four-fold leave-one-ancestry-block-out result

Each fold removes one block, refits `mu_minus_b`, `P2_minus_b`, `e2_minus_b` on the remaining three
blocks (24 rows) with the exact legal linked A/B gauge and the exact solver, and reconstructs the
omitted block **out of sample**. `mu, P1, P2, e1, e2` in V1 are never changed.

| omitted block | S3 (common argmin, +I2, rel gates) | ‖alignment‖² P2 vs LOBO_P2 | ‖alignment‖² e2 vs LOBO_e2 | out-of-sample per-line residual |
|---|---|---|---|---|
| 65000 | pass | 0.9986 | 0.9986 | 1.217e-07 |
| 65001 | pass | 0.9997 | 0.9997 | 8.142e-08 |
| 65002 | pass | 0.9989 | 0.9989 | 1.015e-07 |
| 65003 | pass | 0.9962 | 0.9962 | 1.204e-07 |
| **min / max** | all pass | **0.9962** | **0.9962** | **1.217e-07** |

The serialized object was first cross-checked against an independent rebuild from the committed raw
bytes: `e1`/`e2` projective alignment `1.000000`, `mu` difference `0`.

## 3. Corrected gates and licenses

    BASIS_S0 exact rederivation + independent implementation agree    PASS (R0 bit-for-bit)
    BASIS_S1 same certified linked-swap argmin for k=0,1,2 (full)     PASS
    BASIS_S2 full I2/I1 = 0.0995 > 0.01 and I2/R0 = 0.0885 > 0.05     PASS
    BASIS_S3 every true-LOBO fold: common argmin, +I2, both rel gates PASS (4/4)
    BASIS_S4 min squared plane alignment 0.9962 > 0.80               PASS
    BASIS_S5 min squared e2 projective alignment 0.9962 > 0.64       PASS
    BASIS_S6 max block contribution to I2 = 0.3529 < 0.50            PASS
    BASIS_S7 reload + mutation oracle                                PASS

    P2_TRANSFER_LICENSE_CORRECTED = S0&S1&S2&S4&S6&S7 = TRUE
    E2_AXIS_TRANSFER_LICENSE_CORRECTED = P2&S3&S5&S6  = TRUE

Per-block contribution to I2: 65000 0.210, 65001 0.271, 65002 0.353, 65003 0.167 — no single
ancestry block drives the second mode.

## 4. Scientific reading

SQDT00 used the wrong stability unit, which was a real methodological defect. Re-doing the audit
with the **correct** ancestry-block unit — a strictly harder test that removes 25% of the data per
fold instead of 6.25% — the P2 plane and the individual e2 axis remain aligned to at least 0.996
(equivalent worst-case principal angle ≈ 3.5°), and no block dominates the second mode. The
serialized object therefore **earns both transfer licenses under the correct unit**, with wide
margins. The transfer tube is frozen at `TUBE_P2_LOBO = 1.217e-07` (the worst out-of-sample
per-line residual across folds, plus a certified propagation bound). Fresh construction is
licensed.
