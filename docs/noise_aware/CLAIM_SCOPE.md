# FROZEN CLAIM-SCOPE TABLE — EXP-GT-NASI-00 (deliverable 23)
No claim absent from this table may enter an abstract or conclusion. Scope is narrowed to what the
prospective run actually qualified. The POINT-identification claim is WITHDRAWN (failed the hard gate).

| ID | Exact claim | Support | Assumptions | Prospective | Replication | Substrate | Falsifier | Prohibited interpretation |
|----|-------------|---------|-------------|-------------|-------------|-----------|-----------|---------------------------|
| C1 | The T6 attenuation/amplification one-sided bounds, clean-anchor bracket, sparse (m≥2s+1) threshold, and sign-agnostic impossibility hold. | T6-A..E proofs; 0/4000 violations historically | drift-free channels v_i=q(1−α_iκ_i); declared contract | N/A (theorem) | Re-derived independently | algebra | one counterexample within assumptions | not universal point recovery |
| C2 | Overconfident null detection is unsafe: a threshold-crossing null gate excludes true low-SNR responses. | burned hold-out 586/1333 invalid, all POINT {0}, SNR=5 dominated | std-amplitude null gate | demonstrated | recomputed from raw | ctrans | — | not a claim the algebra is wrong |
| C3 | An uncertainty-aware SET instrument that propagates simultaneous channel CIs through T6 never converts non-detection into an exact-zero claim. | nasi.py construction | simultaneous (1−α) channel CIs | **0/5000 false {0}, both arms** | independent impl: 0 false {0} | ctrans+FHN | one false {0} on a nonzero case | not "safe point identification" |
| C4 | Under the declared noise family, set/bound coverage is ≥95% in every SNR band incl. low-SNR. | prospective O=0.986,B=0.963; all bands ≥0.95 | preregistered noise contract | validated | indep 0.939 (less conservative) | ctrans | material undercoverage on a fresh hold-out | not coverage outside the declared noise family |
| C5 | The identifiability CLASSES and no-false-zero property transfer structurally to a second substrate. | FHN: false-zero 0, structural coverage 0.984 | FHN response profile known | structural only | — | FHN | a substrate where classes fail | NOT substrate-independent point accuracy |
| C6 | Droplets are a NEGATIVE transfer example: drift and causal response share the nutrient field, giving common-mode contamination and observational rank deficiency. | inherited 9042ba0 / CRD-03 | passive observation | — | — | droplet | a passive observable separating drift from response | not a claim about identity/life/turnover |

## WITHDRAWN / NOT CLAIMED
* **Safe operational POINT identification** — FAILED the preregistered hard gate (57 invalid confident
  points, 2 catastrophic in `dropout`/`sparse`). Withdrawn. A point-suppressed set-only variant is
  promising but requires a FRESH preregistered hold-out to claim; it is NOT claimed on the burned one.
* Substrate-independent quantitative point accuracy; identity; individuality; life; material turnover;
  universal point recovery; droplet causal continuity.
