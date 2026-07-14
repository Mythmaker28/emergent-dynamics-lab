# DEVELOPMENT CERTIFICATE (deliverable 8) — EXP-GT-PC-00  (N=640, frozen constants)
| metric | Arm O (conditional) | Arm B (blind/operational) |
|---|---|---|
| selection-aware set coverage | 0.956 | 0.965 |
| certified points issued | 0 (all C1-refused: truth contracts) | 15 |
| point coverage | — | 0.933 (14/15; 1 near-edge, compatible with 0.95 at n=15) |
| catastrophic invalid certificates | 0 | 0 |
| dropout false-acceptance | 0 | 0 |
| false exact-zero | 0 | 0 |
| non-vacuity (high-SNR point rate) | 0 | 0.07 |
Gates G1 (set safety), G3 (catastrophic), G4 (no false zero), G5 (oracle provenance: Arm O issues no
points), G7 (dropout protection), G9 (point coverage), G10 (non-vacuity) — all PASS. Historical-57
regression PASS. The layer is deliberately conservative: it certifies points RARELY (~2–3% of cases) and
only when stable, dropout-free, high-SNR and operationally contracted.
