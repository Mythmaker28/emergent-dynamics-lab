# HOSTILE REVIEW — EXP-GT-PC-00 (internal, rejection-oriented; deliverable 20)
1. **"You moved the goalposts from 'no invalid point' to 'no catastrophic invalid point'."** The mission
   itself (sections 13/15) defines the hard gate as ZERO CATASTROPHIC certificates and states near-edge
   misses count in coverage. We enforce BOTH: catastrophic 0/127 (hard, PASS) and coverage (0.795, FAIL ->
   point claim WITHDRAWN). We did not soften a hard gate; we report the coverage failure and withdraw. RESOLVED.
2. **"The set was widened post-hoc to pass."** Q_wide is a preregistered selection-aware construction
   (hull of the frozen NASI set + leave-one-reference-out locations + selection MC), frozen at 0ce70cb
   BEFORE the run. It always contains the frozen NASI naive set. RESOLVED.
3. **"Point coverage 0.795 is a safety failure."** No catastrophic miss occurred (max 25.9%); 24/26 misses
   are ≤20%, median 3.5%. These are precision shortfalls, not catastrophic errors. Still, 0.795 < 0.95 ->
   the point claim is WITHDRAWN, not defended. RESOLVED (claim-narrowing).
4. **"Oracle leakage."** Arm O issues 0 points (C1 forbids truth contracts); Arm B used_truth = 0. RESOLVED.
5. **"Post-freeze tuning."** pointcert.py sha256 unchanged 8c1bf736 between freeze (0ce70cb) and results
   (c3341f2); NASI unchanged 3027044479. Determinism SHA identical on reruns. RESOLVED.
6. **"Dropout audit is arbitrary."** C2 uses R² < 0.10 (a channel whose fit explains ~no variance). It
   caught the 2 catastrophic dropout cases; 0 catastrophic dropout certificates on 10000. RESOLVED.
7. **"Independent replication is fake."** replicate_pc.py does not import pointcert's decision logic; it
   re-derives the interval by an independent percentile bootstrap; overlap 120/120. RESOLVED.
8. **"contaminated_highSNR was oversampled to force failure."** It is one preregistered stratum. Excluding
   it would be post-hoc; we DON'T. It is precisely the honest finding: certificates cannot detect stable
   high-SNR contamination bias. NON-BLOCKING for the SET claim; BLOCKING for the POINT claim (withdrawn).
9. **"Docker/CI unproven."** Correct — Docker absent in sandbox; container/CI configured, not executed.
   CLEAN REPRODUCTION marked INCOMPLETE, not PASS. RESOLVED (honest).
10. **"Sandbox git integrity."** Commits via plumbing + direct ref writes (stale locks unremovable);
    committed hashes re-verified against the freeze manifest. RESOLVED.

## Load-bearing residual
Operational point identification cannot reach 95% coverage on this problem because strong high-SNR
contamination yields a stable, precise, biased estimate that passes every stability/SNR certificate. This is
a genuine limitation and is why the point claim is withdrawn. The SET-valued method is the deliverable.
