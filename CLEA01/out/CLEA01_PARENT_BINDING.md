# CLEA01 — PARENT BINDING

```
PARENT_PROGRAM        = OMLDCT02 — ONE-MATCHED-LOCKED-DAUGHTER-CONTROL-TEST-02
PARENT_FINAL_TIP      = 84000ff3a67fd4e550934313019decda05219da0
TIP_RESOLVED_FROM     = git bundle list-heads on the verified Windows OMLDCT02_FINAL_FULL.bundle
PARENT_FINAL_DISPOSITION = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS
OMLDCT02_PAIRED_STATISTICS = DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT
```

CLEA01 may not promote, reject or reinterpret the OMLDCT02 paired hypothesis, and does not. **No
p-value is computed or interpreted anywhere in this mission** — the checker grepped every file to
confirm it.

## The six numbers, re-verified independently

Recomputed from the sealed ledger and the archives on disk, not from OMLDCT02's own summaries.

| | required | observed |
|---|---|---|
| base seeds attempted | 805 | 805 |
| valid matched pairs | 33 | 33 |
| minimum required | 41 | 41 |
| hard arm-instance count | 510.56902 | 510.56902 |
| hard ceiling | 512 | respected |
| technical failures | 0 | 0 |
| load-bearing defects | 0 | 0 |

All 66 archives re-hashed against the sealed ledger: 66 of 66 match. Indices contiguous 0–804.

**One small thing worth stating.** The ledger stores each per-seed cost as `round(x, 5)`. The sum of
805 rounded values is 510.56902; the exact rational sum recomputed from `t_m` and `prefix_steps` is
exactly 510569/1000 = 510.569. They differ by 2.0e-05 — a rounding artefact, not a discrepancy.

## What is bound

TLMR01, FIMRCC01, LDFMA01 (tip `2101b30`), the OMLDCT01 invalid closure (`d8b5007`,
`OMLDCT01_TECHNICALLY_INVALID`), OMLDCT02 C1–C5, all 66 paired archives, the sealed ledger, the raw
checker return, the checker adjudication and the final disposition.

## Declared: what I had already seen

The aggregate OMLDCT02 summaries were known before CLEA01 began — the launcher acknowledges this and
calls the CLEA01 validation developmental rather than confirmatory for exactly that reason. In
addition I had already seen **one** per-pair row, index 664, while verifying the OMLDCT02 checker's
undefined-log finding. The other 32 were unopened at binding time. The split later placed 664 in
DEVELOPMENT by its own digest; the checker confirmed the row carries no distinguishing information
(Model A duration 0 in both arms).
