# POINT-CERTIFICATION CONTRACT + SELECTION-AWARE DERIVATION (deliverables 4,5) — EXP-GT-PC-00
The set layer is primary. A point is a claim REDUCTION issued only under all certificates.

## Selection-aware set Q_wide (the primary output)
Naive NASI returns a set Q0 (possibly a narrow "POINT" interval) whose location depends on a DATA-DRIVEN
selection (argmax/argmin channel, or a clean-majority cluster). That selection is the source of the 57
historical point failures. The point layer replaces Q0 with a SELECTION-AWARE set:
  Q_wide = hull( Q0 , { point location with reference j removed : all j } , { fold locations } ,
                 selection Monte-Carlo interval )
Because a dropout/selection artefact moves the point when the offending reference is removed, the
leave-one-out locations pull Q_wide wide enough to contain the truth. Q_wide ⊇ Q0 always. Coverage of
Q_wide is the primary safety endpoint.

## Certificates (all required for a point)
* **C1 provenance** — every contract used is operational (sensor-physics / calibration / geometry /
  external prior). Truth-derived contracts (benchmark labels, hidden κ, privileged topology) → `POINT_FORBIDDEN_ORACLE_CONTRACT`.
* **C2 dropout** — the determining channel is not dropout-suspect (fit R² ≥ 0.10), unless externally essential.
* **C3 diameter** — relative diam(Q_wide) ≤ `EPS_Q_REL=0.30`; else it is a set, not a point.
* **C4 leave-one-reference-out** — the point location shifts by ≤ `LORO_TOL=0.15` when any non-essential
  reference is removed.
* **C5 leave-one-fold-out** — stable across temporal folds (≤ `FOLD_TOL=0.22`); a point may not be
  determined by one noise-selected segment (single-probe proxy for leave-one-probe-out).
* **C6 selection-aware uncertainty** — the certified interval is the selection Monte-Carlo interval
  (re-selecting each draw), inflated by `POINT_INFLATE=1.50`, intersected with Q_wide. It accounts for the
  data-driven selection rather than treating it as fixed.
* **C8 SNR floor** — max per-channel SNR ≥ `SNR_FLOOR=8.0`; low-SNR yields a set, never a point.
* **C7 independent agreement** — a second implementation must produce an overlapping certified interval
  (checked in the replication harness, not per call).

## Point statuses
`PRACTICALLY_POINT_IDENTIFIED_WITHIN_MARGIN` (data), `STRUCTURALLY_POINT_IDENTIFIED` (exact structural
equality only), and refusals `POINT_CERTIFICATE_FAILED`, `POINT_FORBIDDEN_{DROPOUT,SELECTION_INSTABILITY,
INSUFFICIENT_SNR,ORACLE_CONTRACT,CONDITIONING}`. A naked scalar is never returned without its certificate.

## Safety ordering
Safety is lexicographically prior to informativeness. A catastrophic invalid certificate (truth outside the
certified interval by > 0.5 relative) is a hard failure. Near-edge misses count in coverage only.
