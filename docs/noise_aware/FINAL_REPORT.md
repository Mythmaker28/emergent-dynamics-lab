# FINAL SCIENTIFIC REPORT — EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00
Repository: `Mythmaker28/emergent-dynamics-lab`. Branch: `main`.

## 1. Mandate and outcome in one paragraph
The burned sign-safe hold-out was traced to an operational null-gate that converted non-detection into an
exact `{0}` claim (recomputed 586/1333 invalid, SNR=5 dominated). A NEW noise-aware instrument was built
that estimates simultaneous channel confidence intervals and propagates them through the exact T6
identifiability inequalities, so `{0}` is never emitted from data. It passed a 12/12 development
certificate, was frozen and hash-gated, and a fresh N=5000 prospective hold-out was executed once. Result:
the historical failure is ELIMINATED (0/5000 false `{0}`, both arms; set/bound coverage ≥95% in every SNR
band), but the preregistered hard gate "zero invalid confident points" FAILED (57 invalid POINTs, 2
catastrophic in dropout/sparse). Per the stop rules the hold-out is BURNED and the instrument was NOT
patched. The no-false-zero SET/BOUND core and the T6 theory are validated; POINT identification is
withdrawn pending a fresh preregistered hold-out.

## 2. Repository grounding (independently verified)
* Starting commit (HEAD at entry): `d71502f`.
* `git fsck --full`: only dangling objects (normal); no corruption.
* Freeze manifests: 36/38 pinned hashes reproduce from HEAD; the 2 mismatches are benign shared-file
  evolution in the older SOURCE_TRANSDUCER freeze (pinned version still at `0f12dd6`). Sign-safe instrument
  and all droplet/ctrans physics are bit-intact.
* Working tree was NOT clean on entry (a staged mass-deletion of the prior corpus; recoverable). The prior
  "working tree clean" report is incorrect. No frozen instrument or droplet physics was modified by me.
* Provenance discrepancy found in the burned artifact: `summary.invalid=541` vs recorded rows `586`
  (a `np.bool_ is False` undercount). The recorded failure is worse than the headline.

## 3. Instrument (frozen `nasi.py` sha256 3027044479...)
Simultaneous channel CIs: studentized moving-block bootstrap, HC3, max-|t| simultaneity, order-1 drift
regressor, HAC ρ-inflation, SIMUL_INFLATE=1.12. Theorem-aware interval propagation (attenuate lower bound;
amplify upper bound over DETECTED channels — dropout-robust; clean-anchor bracket; sparse clean-majority;
T6-E impossibility). 14 statuses; exact zero only via a structural null contract. Two arms: conditional
(records external contracts) and blind (op contracts only; `blind_used_truth=0`).

## 4. Development certificate (N=800): 12/12 gates PASS
Arm O coverage 0.985 (all noise families ≥0.96, low-SNR 0.981, 0 false {0}); Arm B 0.949; historical
regressions 47/48, 0 false {0}. Calibration and the dropout-robustness fix were done on development only,
BEFORE freeze.

## 5. Prospective hold-out (N=5000, executed once, hash-gated)
| endpoint | Arm O | Arm B |
|---|---|---|
| false `{0}` on nonzero | **0/…** | **0/…** (0/5000 total) |
| set/bound coverage | 0.986 (cluster95 [0.981,0.990]) | 0.963 (cluster95 [0.955,0.971]) |
| coverage, every SNR band | ≥0.982 | ≥0.951 |
| invalid confident POINTs | 17/216 | 40/149 |
| worst stratum | sparse1 0.939 | dropout 0.925 |
Invalid-point severity: median relative miss 0.02; 50/57 benign CI-tail misses; **2/57 catastrophic**
(dropout, low-SNR, blind). Preregistered gate 1 (zero invalid points) → **FAIL**. Primary safety endpoint
(false {0}) → **PASS**.

## 6. Independent replication + FHN
Independent implementation (no `nasi` import, different method): false `{0}` = 0; coverage 0.939 vs nasi
0.986 (the less-conservative independent path under-covers slightly — confirming nasi's HAC+inflation is
necessary, not arbitrary); 95% cover/miss agreement. FHN (non-exponential profile, structural only): false
`{0}` = 0, structural coverage 0.984, low-SNR 0.987, ill-conditioned widen/abstain 75/75.

## 7. Reproduction (honest)
`make reproduce-nasi` deterministic: identical canonical SHA `36b25c3e...` on two runs. Freeze-verify PASS,
cache-poison invariance PASS. **Docker unavailable in this sandbox** → container NOT built/run; CI
configured (py3.10/3.12 + container job) but NOT executed from here; no clean-clone run. → INCOMPLETE.

## 8. Environment caveats (material to reproducibility)
This sandbox exhibited (a) stale-bytecode reuse (mitigated with fresh `PYTHONPYCACHEPREFIX` + `-B`); (b)
a truncated mount-sync of editor-written files (all executable code re-authored via the shell and
`py_compile`-verified); (c) stale-locked git index/refs with blocked `.git` unlinks (commits completed via
plumbing + direct ref writes; committed hashes re-verified). These are documented so a clean host can
confirm the results.

## 9. Commit lineage
* start: `d71502f`
* Phase-0 freeze + preregistration (instrument + dev cert + prospective generator, BEFORE run): `33ef80e`
* prospective results (executed once): `2aef791`
* independent replication + FHN: `d0256e7`
* reproduction + CI: `f81eb29`
* figures + claim table: `1f2a4e8`
* this report: (final commit)

## 10. VERDICTS
`IDENTIFIABILITY THEORY: PASS`
`NOISE-AWARE SET INSTRUMENT: INDETERMINATE`  (no-false-zero + set/bound core validated; POINT identification FAILED the hard gate and is withdrawn)
`FRESH LARGE HOLD-OUT: FAIL`  (0/5000 false {0}, but 57 invalid confident points violate the preregistered zero-invalid-point gate; BURNED, not patched)
`CLEAN REPRODUCTION: INCOMPLETE`  (deterministic + freeze + cache-poison verified; Docker/CI/clean-clone not run here)
`CROSS-SUBSTRATE: STRUCTURAL PASS`  (FHN structural transfer; no quantitative point claim)
`PUBLICATION STATUS: THEORY PAPER SOLID`  (identifiability + impossibility + failure-of-null-detection + necessity of set outputs; the operational/methods paper is NOT ready)
`EXTERNAL HUMAN REVIEW: PENDING`
`DROPLET CAUSAL-CONTINUITY PILOT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`
