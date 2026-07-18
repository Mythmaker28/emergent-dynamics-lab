# FROZEN CLAIM-SCOPE TABLE — EXP-GT-PC-00 (deliverable 19)
| ID | Claim | Support | Prospective | Falsifier | Prohibited interpretation |
|----|-------|---------|-------------|-----------|---------------------------|
| S1 | The selection-aware SET (Q_wide) covers the true |q| at ≥95% under the declared noise family, INCLUDING 40% dropout/sparse. | N=10000: O 0.959, B 0.969 | PASS | set coverage < 95% on a fresh hold-out | not point identification |
| S2 | The instrument never converts non-detection into an exact-zero claim. | 0/10000 false {0}, both arms | PASS | one false {0} on a nonzero case | — |
| S3 | Certification eliminates CATASTROPHIC point errors: no certified point misses truth by > 0.5 relative. | 0/127 catastrophic | PASS | one catastrophic certified point | NOT "points are accurate to 95%" |
| S4 | Dropout and sparse-contamination selection failures are converted to refusals or widened sets. | 57-regression: 2/2 catastrophic refused; dropout strata 4/4 covered | PASS | a catastrophic dropout/sparse certificate | — |
| S5 (WITHDRAWN) | Operational POINT identification at 95% coverage. | point coverage 0.795 (<95%), defeated by stable high-SNR contamination bias (contaminated_highSNR 7/23) | **FAIL** | — | WITHDRAWN: do not claim safe point identification |
| S6 | Structural transfer to FHN (identifiability classes + no false zero). | prior EXP-GT-NASI FHN audit | structural | a substrate where classes fail | not substrate-independent point accuracy |
| S7 | Droplets: negative passive-observability (common-mode contamination). | inherited CRD-03 / 9042ba0 | — | a passive observable separating drift from response | not identity/life/turnover |

## NOT CLAIMED / WITHDRAWN
Safe operational point identification; substrate-independent point accuracy; identity; life; material
turnover; universal point recovery; droplet causal continuity. Point identification is retained in the code
ONLY as a catastrophe-free certificate whose coverage is ~80%, explicitly NOT a 95% point claim.
