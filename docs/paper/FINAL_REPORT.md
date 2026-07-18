# FINAL SCIENTIFIC REPORT — Set-Valued Paper Consolidation
Repository `Mythmaker28/emergent-dynamics-lab`, branch `main`.

## 1. Outcome
The set-valued causal-metrology instrument is consolidated into a methods paper with a proved impossibility
result explaining why point identification was withdrawn. The set layer is validated (0 false {0} on 5,000
and 10,000 fresh cases; marginal coverage 0.959/0.969). Point certification eliminates catastrophic errors
(0/127) but cannot reach 95% coverage (0.795) because of stable contamination bias, now formalized: internal
precision cannot resolve structural non-identifiability (Propositions 1–2; numerically var→1e-6, bias→−0.30).

## 2. Grounding (verified)
HEAD at entry `f4e776e`; frozen `nasi.py` `3027044479`, `pointcert.py` `8c1bf736` (unchanged); fsck clean;
no frozen instrument or droplet physics modified (additions only).

## 3. Permanent results preserved
NASI/PC set: 0/10000 false {0}; set coverage O 0.959, B 0.969; dropout/sparse ≥~95%; no blind-arm oracle.
Point: 127 issued, 101 covered (0.795), 26 invalid, 0 catastrophic; contam_highSNR 7/23; clean 22/22; sparse
18/19; dropout variants 4/4. Prospective hold-out FAILED AND BURNED for point qualification.

## 4. New scientific content
Stable-bias impossibility theorem (Prop 1: observational collinearity; Prop 2: internal precision is
orthogonal to identifiability; Corollary + numerical demo). Three-class failure taxonomy (detection /
instability / identifiability) with decision diagram. External-anchor requirements (none operational in
ctrans/FHN/droplet without oracle). Set-valued statistical audit distinguishing marginal (≥95%) from
conditional (0.80–0.92 on the stable-contamination direction) coverage. Corrected two-panel figure. Frozen
10-claim table. Full manuscript.

## 5. Reproduction (honest)
`make reproduce-pc`/`reproduce-nasi` deterministic (PC_CANON `17080664`, NASI `36b25c3e`, identical on 2
runs); freeze + cache-poison verified. Docker NOT available in sandbox → container/CI configured but not
executed. CLEAN REPRODUCTION INCOMPLETE.

## 6. Commit lineage
start `f4e776e`; claim-freeze/analysis `9326522`; manuscript + final docs (this) `<final>`. Frozen hashes:
nasi.py `3027044479`, pointcert.py `8c1bf736`, pcprospgen.py `832dc4c7`.

## 7. Environment caveats
Stale bytecode, truncated editor→shell sync, unremovable `.git/*.lock` — mitigated (shell-authored + py_compile
verified code; fresh PYTHONPYCACHEPREFIX; commits via plumbing + direct ref writes with hashes re-verified).

## 8. VERDICTS
`THEORY PACKAGE: SOLID`
`SET-VALUED INSTRUMENT: PASS`  (marginal empirical coverage ≥95%; conditional weakness on the stable-contamination direction documented, not hidden)
`POINT CERTIFICATION: WITHDRAWN`
`CLEAN REPRODUCTION: INCOMPLETE`  (deterministic reproduction + freeze + cache-poison verified; Docker/CI not executed in sandbox)
`PUBLICATION STATUS: SET-VALUED METHODS PAPER SOLID`
`EXTERNAL HUMAN REVIEW: PENDING`
`DROPLET CAUSAL-CONTINUITY PILOT remains BLOCKED.`
`EXP-SC-01 remains BLOCKED.`
