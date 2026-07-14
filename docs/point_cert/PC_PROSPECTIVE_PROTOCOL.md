# PROSPECTIVE PROTOCOL (PREREGISTRATION) — EXP-GT-PC-00 (committed BEFORE execution). Deliverable 10.
* Frozen point layer `point_cert/pointcert.py` sha256 `8c1bf736...`; NASI dependency `nasi.py` `3027044479...` (unmodified, hash-gated).
* Constants: EPS_Q_REL=0.30, SNR_FLOOR=8.0, LORO_TOL=0.15, FOLD_TOL=0.22, DROP_R2=0.10, SELECT_B=199, POINT_INFLATE=1.75, CATASTROPHIC_MISS=0.5.
* Generator `point_cert/pcprospgen.py` seed `0x50507A9E`; N=10000; >=40% dropout/sparse (verified 0.40); SNR oversampled low (40% <=5). Distinct from dev (0x9C0DE7) and the burned NASI hold-out.
* Runner hash-gates both pointcert.py and nasi.py before scoring.

## Endpoints & gates (fixed before the run)
1. zero false exact-zero (HARD); 2. selection-aware SET coverage compatible with 95% (both arms);
3. **zero CATASTROPHIC invalid point certificates** (miss>0.5) — HARD; 4. point-certified coverage
compatible with 95% (near-edge misses count); 5. blind arm uses no truth contracts; 6. dropout
false-acceptance below frozen bound (0 catastrophic on dropout); 7. sparse-contamination point validity;
8. low-SNR (<SNR_FLOOR) refuses points; 9. ill-conditioned widen/refuse; 10. non-vacuity by stratum;
11. independent implementation agreement; 12. no tuning after execution.

## Stop rules
One CATASTROPHIC invalid point certificate -> STOP, burn the hold-out, preserve, do NOT patch.
Material point-coverage underperformance -> withdraw point claims (retain the set method).
Any oracle contract in the blind arm -> benchmark invalid.
