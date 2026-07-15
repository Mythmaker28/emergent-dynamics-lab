# Journal — EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00

- Role: primary scientific execution agent (interactive; isolated branch). Base 0ea1250 (IOM-00 final).
- Goal: expand the read-out of the existing memory (m+ and m- to two functions) to test individuation.

## OBSERVED
- Storage audit (frozen IOM-00): order reproducibly stored in m- (100% held-out classification dev+prosp);
  net exposure in m+; continuous spatial history NOT stored (Psi saturates). Decision S1.
- New channel m- -> attractant production; lam_minus=0 -> IOM-00 bit-identical (max dev 0.0).
- Order read-out now channel-specific: order on attractant axis collapses 70x (dev)/73x (prosp) under
  lam_minus ablation; absent on uptake axis; ablate-all -> 0. Dose read-out retained. Erase/transplant OK.
  Viability size ~103; turnover M~0.12 (order survives, ~17% retained).
- Continuous 2 phase-drives: only ONE dimension recoverable held-out (p2 R2 0.57, p1 -0.09); response
  effective dim 1.08; individuation AUC 0.75 (carried by the single dim). Tried 3 history parametrizations;
  all show ~1-D response because m+ and m- both integrate the same saturating Psi.

## INFERRED
- The 2nd channel achieves ORDER-SENSITIVITY (the IOM-00 failure) but not individuation: STORAGE is ~1-D
  in viable regimes (write saturation), so read-out expansion alone cannot create a 2nd continuous dim.

## DECISION
- VERDICT PASS - ORDER-SENSITIVE MEMORY ONLY. Gates fail: G10 dim, G11 two-dims, G12 individuation.
- NEXT-PROJECT: do NOT add persistence; revise WRITING (non-saturating) or add recurrent plasticity, then
  re-expand channels. QUANTUM NOT USED. HMC prospective SEALED; SC-PILOT + EXP-SC-01 BLOCKED.

## ENVIRONMENT
- create-only mount / stale locks / no background jobs: resumable runners + lock-free plumbing + /tmp
  compute + bash-heredoc edits. See memory [[ising-v3-git-mount-workaround]].
