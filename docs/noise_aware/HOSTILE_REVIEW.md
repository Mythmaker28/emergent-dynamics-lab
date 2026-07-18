# HOSTILE REVIEW — EXP-GT-NASI-00 (internal, rejection-oriented; deliverable 24)
NOT an external review. Ten+ strongest objections; each marked RESOLVED / NARROWING / BLOCKING.

1. **"It abstains its way to safety."** Arm B abstains on 3195/5000. NARROWING: informativeness is modest,
   and much of the blind arm is honestly NON_IDENTIFIABLE (T6-E). But Arm O still emits 918 informative
   sets (216 points, 702 bounds), median finite width 1.15×|q|, and every SNR band shows rising
   informativeness (fig4). Non-vacuity is reported, never used to override safety. Not blocking.

2. **"95% coverage still makes 5% wrong claims."** Correct and disclosed. The only HARD guarantees are
   (a) no false {0} — 0/5000 — and (b) no invalid confident point — which FAILED. Set/bound outputs carry
   an explicit 95% coverage, not certainty. NARROWING → the POINT claim is withdrawn (see #5).

3. **"Oracle leakage."** Arm O deliberately consumes truth contracts (it validates conditional theorems)
   and records provenance; Arm B consumes only sensor-physics/geometry contracts; `blind_used_truth = 0`
   in both dev and prospective. The arms are never compared as equals. RESOLVED.

4. **"Generator leakage between dev and prospective."** Distinct seed namespaces (0x0DE7 vs 0x5A5A0000);
   the prospective generator was committed at 33ef80e BEFORE execution and hash-gated. They share the
   STRUCTURAL physics form (same substrate) and the noise contract — intended, not leakage; coverage
   outside the declared noise family is not claimed. RESOLVED (with the noise-contract NARROWING).

5. **"Post-freeze tuning to pass the hold-out."** NONE. The prospective FAILED the point gate; the
   instrument was NOT patched and NOT re-run. `nasi.py` sha256 is unchanged since the freeze commit
   33ef80e; the prospective results are at 2aef791 (later). This would be BLOCKING if it had happened; it
   did not, and is git-verifiable. RESOLVED.

6. **"Correlated MC trials inflate confidence."** Cluster-aware (by structural stratum) bootstrap CIs are
   reported: Arm O [0.981,0.990], Arm B [0.955,0.971]; worst strata sparse1 0.939 / dropout 0.925 are
   surfaced, not hidden. RESOLVED.

7. **"Numerical/near-zero degeneracy."** Ill-conditioned mixtures (coupling spread < 0.15) abstain; FHN
   ill-conditioned cases widen/abstain 75/75 without excluding truth. RESOLVED.

8. **"FHN claim inflation."** FHN is used for STRUCTURAL transfer only; no quantitative point-accuracy
   claim is made and this is stated in the claim table and the FHN audit. RESOLVED.

9. **"Cherry-picked figures."** All four figures are generated from raw artifacts with sha256 provenance
   (`figure_provenance.json`). Fig1 shows the repair honestly; fig3 plots ALL 57 invalid points including
   the 2 catastrophic. No plotted value is hand-edited. RESOLVED.

10. **"Suppressed failures."** The headline result IS a failure (the hold-out FAILS the point gate). All
    5000 cases are preserved; the 57 invalid points are saved to `invalid_point_forensics.json`. Nothing
    is suppressed. RESOLVED.

11. **"Duplicated evidence sold as independent."** The replication does not import `nasi`, uses a different
    uncertainty method, and reaches a DIFFERENT coverage (0.939 vs 0.986) — demonstrably not a copy. It
    confirms only the load-bearing invariant (0 false {0}). RESOLVED.

12. **"The sandbox blocked git — are the commits real?"** The default index/refs were stale-locked and the
    mount blocks unlinking `.git/*.lock`; commits were completed via plumbing (`write-tree`/`commit-tree` +
    direct ref write). Committed `nasi.py`/`prospgen.py` hashes were re-verified against the freeze/protocol
    and match. Real and `git log`-verifiable. Also flagged: a truncated-file mount-sync hazard was detected
    and worked around (all executable code authored via the shell and `py_compile`-checked). RESOLVED, with
    the environment caveats recorded in the final report.

## Residual BLOCKING items for a "safe operational instrument" claim
* point-identification under reference dropout / sparse contamination is not safe (2 catastrophic
  confident errors / 5000). Until a point-suppressed variant passes a FRESH preregistered hold-out, the
  instrument may be described only as a no-false-zero SET/BOUND instrument, not a point estimator.
