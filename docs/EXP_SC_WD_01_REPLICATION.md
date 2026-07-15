# EXP-SC-WRITING-DIMENSIONALITY-01 — Phase A: Replication of the MCM core (G2/G3)

All numbers below were produced this session by running the **committed** `sc_mcm` code independently.

## G3 — Backward compatibility: EXACT
MCM engine with `MCParams(lam_plus=0.25, lam_minus=0)` vs IOM-00 `MemoryScaffoldEngine(MemParams(lam_m=0.25))`,
from the identical seeded state (seed 32000), 200 steps, comparing rho,U,V,c,N,C,Mf,uptake:
- cumulative **max|dev| = 0.00e+00** → bit-identical. **G3 PASS.**
- One-step channel-locality: turning lam_minus 0→0.15 changes only `c` (d_c=1.4e-3) with **d_rho=0, d_Mf=0**
  → the 2nd channel is a pure attractant-production readout; the memory write is untouched (truly frozen).

## G2 — Positive result reproduces (order is causally readable)
Seed 32000, central protocol (transplant memory into a common erased body, settle, read multi-axis signature):
- attractant-axis order contrast |R_H1−R_H2| (full) = 0.1198; under lam_minus=0 ablation = 0.0019 →
  **contrast 62.8×** (certificate median: dev 70.3×, prosp 73.1×). Same effect, same order of magnitude.
- uptake-axis order = 2.1e-4 (negligible) → order is channel-specific, as claimed.
- m−(H1)=−0.125, m−(H2)=−0.259 → temporal order stored in m1−m2 with H2 (c→N) more negative (consistent
  with the handoff's m−(H1)≈−0.23, m−(H2)≈−0.34; the gentler MCM histories shrink magnitudes but preserve sign/ordering).

## Storage-dimensionality result reproduces (and is sharpened)
Re-deriving from the committed `cont_*.pkl`: stored memory tracks p2 (corr(m·,p2)≈−0.45…−0.69) and is blind
to p1 (corr≈−0.06…+0.11); (m1,m2) collinear at 0.97–0.98; response_effdim≈1.08. Reproduced. My grouped
leave-history-out decode gives **p2 R²=0.38** vs the certificate's row-LOO **0.57** — the 0.19 gap is
replicate leakage (4 seeds share each history in the row-LOO). See the Phase-B audit for the correction.

## Phase-A verdict
**A-PASS — MCM CORE REPLICATED.** Backward-compat exact; the positive order-readout effect reproduces;
the storage-1-D observation reproduces. The *interpretation* of the 1-D observation is audited in Phase B.
