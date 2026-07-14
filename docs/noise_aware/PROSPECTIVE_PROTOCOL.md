# PROSPECTIVE PROTOCOL (PREREGISTRATION) — committed BEFORE execution
EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00. Deliverable 14.

## Frozen instrument (hash-gated)
* `noise_aware/nasi.py` sha256 = `3027044479451f54c03c6265f1497b6f93d61eb56254b3e7bb16571e57ff1437`
* constants: DIVERSITY_FLOOR=0.15, POINT_HALFWIDTH=0.15, BOOT_B=399, BLOCK_FRAC=0.20, DRIFT_ORDER=1,
  SIMUL_INFLATE=1.12, ALPHA=0.05.
The runner (`run_prosp.py`) verifies these hashes before any case is scored.

## Fresh prospective generator (committed BEFORE the run)
* `noise_aware/prospgen.py` sha256 = `aa264b2e53e82c20d7be8a72ed786341026939f5b2f25888c5bfc71f854f6305`
* seed namespace `PROSP_SEED_BASE = 0x5A5A0000` (distinct from development 0x0DE7).
* N = 5000. SNR by log-uniform band with EXACT 25% mass each: (0.5,5], (5,10], (10,30], (30,100].
* Stratified additionally by: response sign (±), anchor present/absent, contamination mode
  (attenuate/amplify/mixed/common-mode/sparse/majority/all/dropout/nonlinear/clean), true-null, weak,
  reference count m∈{2,3,4,5,8}, conditioning (ill-conditioned band), and the 6 noise families.

## Endpoints
* PRIMARY SAFETY: proportion of emitted identified sets excluding the true |q|, per arm. Report exact
  (Clopper–Pearson) and cluster-aware (by structural stratum) confidence intervals.
* Low-SNR safety: same, restricted to SNR≤5.
* Secondary (non-vacuity): point-identification rate, median interval width, one-sided-bound tightness,
  abstention rate — reported by stratum. Non-vacuity NEVER overrides safety.

## PASS/FAIL gates (fixed here, before the run)
1. zero invalid POINT verdicts (HARD);
2. zero false `{0}` on any nonzero case (HARD);
3. overall simultaneous coverage compatible with 95% (Wilson/exact CI overlaps 0.95, Arm O);
4. low-SNR (≤5) coverage compatible with 95% (Arm O);
5. null cases: 0 ∈ Q at ≥ the declared rate;
6. blind arm consumes no truth-derived metadata (used_truth == 0);
7. ill-conditioned cases widen or abstain, never exclude truth.

## Stop rules (mission sections 19, 24)
* One false `{0}` on a nonzero case → HARD FAIL. Preserve, do not patch on this hold-out.
* One invalid confident POINT → HARD FAIL. Burn the hold-out; preserve the failure; do NOT patch on it.
* Material 95% coverage failure → stop and narrow the noise contract.
* Any oracle metadata entering the blind arm → benchmark invalid.

## Execution
`run_prosp.py START END` over deterministic content-addressed chunks covering [0,5000); the aggregator
(`aggregate_prosp.py`) concatenates rows and computes the audit. Chunk boundaries cannot change any result
(per-case seeds are content-addressed). No tuning after execution.
