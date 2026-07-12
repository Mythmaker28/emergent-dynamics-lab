# EXP-FL-02 — Screen decision (matched OFF/ON reservoir-exchange throughput)

Protocol @30c01b0. RUN-20260710-2200-EXPFL02. Model: claude-opus-4-8 (lock lifted). OFF = EXACT current-core limit.

## OBSERVED (levels 1-2 only)
- 64 laws x {OFF,ON} x 3 seeds = 384 runs. Global mass (A+R) conserved to 5e-16 in every run.
- OFF (exact core): mean P 0.989, mean M 0.989, median min-M 0.969, 0.5% of runs reach min-M<0.5, 3 probe rows,
  0 eligible seeds, **0 screening-permitted laws**, mean 1.4 tracks/run.
- ON (throughput): mean P 0.941, mean M 0.836, median min-M **0.224**, **87% of runs reach min-M<0.5**, 1942 probe
  rows, 81 eligible seeds, **24 screening-permitted laws** {2,3,4,13,16,18,19,23,33,36,38,39,40,42,43,45,47,48,
  53,59,60,61,62,63}, mean **28.1 tracks/run**.
- ON - OFF: d(median min-M) = -0.745; d(permitted laws) = +24.

## Five levels (kept distinct)
1. DISTRIBUTIONAL SHIFT: the throughput mechanism decisively moves the field into the low-M (turnover) regime that
   the minimal core could never reach. Descriptive.
2. SCREENING SIGNAL: **present for the first time in this project** -- 24 permitted laws (ON) vs 0 (OFF).
3-5. FRESH-SEED RECURRENCE / ALIAS REJECTION / CAUSAL RE-ESTABLISHMENT: NOT yet evaluated.

## MANDATORY CAUTION (falsifier F2 is live)
Screening permission is NOT a scientific candidate. ON also shows a ~20x increase in track count (28.1 vs 1.4 per
run), a strong FRAGMENTATION / TRACKER-CHURN signature. The observed low M may reflect reservoir-driven blob
dissolution-and-reformation (look-alike replacement) rather than a persistent organization exchanging
constituents. This is exactly falsifier F2 and must be resolved by: frozen fresh-seed hold-out (>=2/5 unseen
seeds) -> direct alias audit -> same-state matched-branch causal intervention. No thresholds were changed; no
composite score was formed; no law was selected visually.

## DECISION
**EXP-FL-02 SCREEN = CANDIDATES (24 permitted ON laws).** Proceed to the frozen fresh-seed hold-out. Nothing is
promoted; F2 remains the leading alternative explanation until the alias audit and causal intervention are done.
