# EXTERNAL-ANCHOR REQUIREMENTS (deliverable 3) — scope analysis, NOT a new instrument
Valid point identification requires information that constrains the unidentified contamination direction
(Proposition 1). For each candidate anchor:

| Anchor | Mathematical information | Physical meaning | Operational test | in ctrans? | in FHN? | in droplet? | oracle? |
|---|---|---|---|---|---|---|---|
| Certified clean reference | fixes one beta_k = 0 | a reference known to be uncontaminated | independent calibration showing zero coupling to the response channel | NO (no reference is certified clean) | NO | NO (all passive refs share nutrient field N) | YES if taken from truth labels |
| Absolute response standard | fixes q directly on one case | a known-magnitude reference response | measure a reference of known amplitude | NO | NO | NO | YES if from truth |
| Known sensor gain | fixes alpha_i (hence beta_i given kappa_i) | calibrated transducer gain | bench calibration of each sensor | PARTIAL (gains modelled, not independently certified) | NO | NO | borderline |
| Physical conservation law | linear constraint among c_i | conserved quantity ties channels | verify conservation on controls | NO | NO | NO (drift & response both flow through N — no conservation separates them) | NO |
| Signed calibration intervention | sign(beta_i) from a controlled push | an intervention with known contamination sign | apply a calibrated intervention, read the sign | YES (sign contract) — but sign only BOUNDS, does not pin | limited | NO | NO |
| Direct external measurement | measures q out-of-band | an independent instrument | cross-instrument comparison | NO | NO | NO | YES if it is the truth |
| Certified contamination bound | |beta_i| <= b | a proven bound on contamination | worst-case physical argument | PARTIAL | NO | NO | NO |

## Conclusion
A **sign** or **bound** anchor yields a valid SET (one-sided bound / interval) — this is what NASI uses and
what passes. A **point** requires an anchor that pins some beta_i to a value (certified clean reference,
known gain, conservation, absolute standard). None of these exists operationally in `ctrans`, FHN, or the
droplet substrate without oracle access. Therefore, on all three substrates the correct operational output
is a SET; a point is claimable only where such an anchor is independently established — which is a
substrate/instrumentation requirement, not an algorithmic one.
