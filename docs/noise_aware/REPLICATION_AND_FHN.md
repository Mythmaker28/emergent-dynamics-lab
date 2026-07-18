# INDEPENDENT REPLICATION + FHN STRUCTURAL AUDIT — EXP-GT-NASI-00
Deliverables 19, 20.

## Independent replication (noise_aware/replicate_nasi.py)
A second implementation that does NOT import the operational instrument and uses a DIFFERENT method at
every stage: percentile moving-block bootstrap of the slope (no studentization) with Bonferroni
simultaneity and linear-drift removal, vs nasi's studentized max-|t| block bootstrap with HAC ρ-inflation.
Set propagation independently re-derived. Comparison on 500 prospective ARM-O cases (sets, not statuses):
* independent false-`{0}` on nonzero cases = **0** (the no-exact-zero property reproduces under a fully
  independent path);
* independent coverage = 0.939 (vs nasi 0.986). The independent method omits the HAC inflation and
  SIMUL_INFLATE and is therefore slightly LESS conservative — it under-covers by ~1 point, which
  *validates* that nasi's extra conservatism is doing real, necessary work rather than being arbitrary;
* cover/miss agreement between the two implementations = 0.952;
* finite-set endpoint discrepancy: small in the median, large in the tail (wide low-SNR / below-detection
  sets are sized differently by the two methods — expected, not a bug).
Conclusion: the load-bearing property (never a false `{0}`) is implementation-invariant; the coverage
level agrees to ~1–2 points; residual disagreements are confined to the width of already-wide sets.

## FHN structural audit (noise_aware/fhn_structural.py)
FitzHugh–Nagumo used for STRUCTURAL validation only (mission section 21). The response profile is the
FHN spike + refractory recovery — non-exponential and non-monotonic, unlike the ctrans exp profile. If the
method transfers, it is structural, not an artefact of the exp waveform. Result over 600 cases:
* false exact-zero on nonzero = **0**;
* coverage of the structural identified set = 0.984; low-SNR(≤5) coverage = 0.987;
* ill-conditioned cases widen or abstain (never exclude truth): 75/75.
NO quantitative point-accuracy claim is made for FHN. Verdict: **CROSS-SUBSTRATE STRUCTURAL PASS**;
substrate-independent point accuracy is NOT claimed.
