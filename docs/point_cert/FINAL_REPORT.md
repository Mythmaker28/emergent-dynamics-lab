# FINAL SCIENTIFIC REPORT — EXP-GT-POINT-CERTIFIED-SET-IDENTIFICATION-00
Repository `Mythmaker28/emergent-dynamics-lab`, branch `main`.

## 1. One-paragraph outcome
Building on the validated NASI set core (frozen, unmodified), a point-certification LAYER was built that
computes a selection-aware set Q_wide and issues a point only under eight certificates (provenance,
dropout, diameter, leave-one-reference-out, leave-one-fold, selection-aware uncertainty, SNR floor,
independent agreement). It passed a development certificate and was frozen; a fresh N=10000 prospective
hold-out (40% dropout/sparse, SNR oversampled low) was executed once. Result: the SET layer is validated
(0/10000 false {0}; selection-aware set coverage 0.959 / 0.969 ≥95%, both arms, including the dropout/sparse
subset) and the certification ELIMINATES CATASTROPHIC point errors (0/127). But operational point coverage
is only 0.795 (< 95%), defeated by stable high-SNR contamination bias that passes every stability/SNR
certificate. Per the stop rule, POINT CERTIFICATION is WITHDRAWN and the set-valued method is retained.

## 2. Grounding (independently verified)
HEAD at entry `3e3b8a3`; NASI `nasi.py` still `3027044479...` (frozen, untouched); fsck clean (dangling only);
all 57 historical point failures reconstructed. No frozen instrument or droplet physics modified (additions
only).

## 3. The point-certification layer (frozen `pointcert.py` 8c1bf736..., imports NASI, never patches it)
Primary output: selection-aware set Q_wide = hull(NASI naive set, leave-one-reference-out point locations,
fold locations, selection Monte-Carlo interval); always ⊇ the NASI naive set. Point issued only if C1..C8
all pass; certified interval ⊆ Q_wide. Constants EPS_Q_REL=0.30, SNR_FLOOR=8.0, LORO_TOL=0.15, FOLD_TOL=0.22,
DROP_R2=0.10, POINT_INFLATE=1.75, CATASTROPHIC=0.5.

## 4. Development (N=900): 7/7 gates PASS
Set coverage O 0.958 / B 0.969; 21 certified points, coverage 0.905, 0 catastrophic, 0 dropout false-accept.
Historical-57: 2/2 catastrophic refused, 0 catastrophic invalid, refusals dominated by SELECTION_INSTABILITY
(21) + ORACLE_CONTRACT (17).

## 5. Prospective (N=10000, executed once, hash-gated)
| endpoint | result | gate |
|---|---|---|
| false exact-zero (nonzero) | 0 / 10000 both arms | PASS (hard) |
| catastrophic invalid point cert | **0 / 127** | PASS (hard) |
| selection-aware set coverage | O 0.9594 [0.955,0.963]; B 0.9688 [0.964,0.973] | PASS |
| set coverage on dropout/sparse | O 0.949; B 0.963 | PASS |
| point coverage (Arm B) | 101/127 = 0.795 [0.717,0.856] | **FAIL** |
| miss distribution | median 3.5%, p90 15.8%, max 25.9%, catastrophic 0 | — |
| culprit stratum | contaminated_highSNR 7/23 = 0.30 (stable high-SNR bias) | — |
| blind_used_truth | 0 | PASS |
| independent replication (C7) | interval overlap 120/120 = 1.000 | PASS |

## 6. Reproduction (honest)
`make reproduce-pc` deterministic: identical `PC_CANON_SHA256 17080664...` on two runs. `verify_pc_freeze.py`
PASS (all frozen files + NASI dependency). Docker NOT available in this sandbox -> container/CI configured
(reuses `.github/workflows/nasi-ci.yml` conventions) but NOT executed here. -> INCOMPLETE.

## 7. Commit lineage
* start `3e3b8a3`; point-contract preregistration + point-layer freeze + prospective generator `0ce70cb`
  (committed BEFORE the run); prospective results + replication + figure `c3341f2`; this report (final commit).
* frozen hashes: pointcert.py `8c1bf736`; pcprospgen.py `832dc4c7`; nasi.py dependency `3027044479` (unchanged).

## 8. Environment caveats
Sandbox exhibited stale bytecode, truncated editor->shell file sync, and unremovable `.git/*.lock`; all
executable code was authored via the shell and `py_compile`-verified, every run used a fresh
`PYTHONPYCACHEPREFIX`, and commits were made via plumbing + direct ref writes with hashes re-verified.

## 9. VERDICTS
`SET-VALUED INSTRUMENT: PASS`
`POINT CERTIFICATION: WITHDRAWN`  (certificates eliminate catastrophic errors — 0/127 — but coverage 0.795 < 0.95; stable high-SNR contamination bias is undetectable by stability/SNR certificates)
`FRESH POINT-CERTIFICATION HOLD-OUT: FAIL`  (point-coverage gate; hard safety gates PASS; NOT burned — 0 catastrophic)
`CLEAN REPRODUCTION: INCOMPLETE`  (determinism + freeze verified; Docker/CI not run in sandbox)
`PUBLICATION STATUS: SET-VALUED METHODS PAPER SOLID`  (set method validated on a fresh N=10000 hold-out incl. dropout/sparse; point identification is a clean negative result)
`EXTERNAL HUMAN REVIEW: PENDING`
`DROPLET CAUSAL-CONTINUITY PILOT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`
