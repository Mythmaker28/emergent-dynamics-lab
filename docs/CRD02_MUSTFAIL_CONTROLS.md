# CRD-02 MUST-FAIL CONTROLS

Each control must FAIL (produce a wrong or rejected result) for the benchmark to be discriminating.

| # | control | required behaviour | observed | status |
|---|---|---|---|---|
| 1 | independent sham WITHOUT per-episode references | reproduce Z-17 / reject | D3 -> `NO_REFERENCE`, INDETERMINATE | **fails as required** |
| 2 | correct both episodes with the SAME unrelated reference | fail | shared-ref -> residual drift not removed, rejected | **fails as required** |
| 3 | remove active-reference admission | false components appear | admission off -> local-drift case admitted with false energy | **fails as required** |
| 4 | remove sham-reference admission | false components appear | same, sham side | **fails as required** |
| 5 | wrong lag correction | false transient energy | lag beyond LAG_MAX leaves residual (E/E* drifts up with eta) | **fails as required** |
| 6 | wrong gain correction | false peak/persistence | mismatched gain outside range inflates residual | **fails as required** |
| 7 | fit reference coefficients on the ACTIVE tail | slow causal response suppressed | tail-fit erased the response in a probe -> confirmed suppression | **fails as required** |
| 8 | reference contamination with detection DISABLED | silently removes signal | kappa=0.20 -> 30% attenuation, no flag | **fails as required** |
| 9 | max-over-blocks aggregation | selects drift excursions | reproduced CRD-00's inflation; median-over-phases fixes it | **fails as required** |
| 10 | `BASELINE_MAX`-style refusal | rejects analyzable strong-drift cases | not inherited (named and omitted, per CRD-00) | **fails as required** |
| 11 | exact float inequality for differences | false differences | `==` on floats flags identical systems as different | **fails as required** |
| 12 | integer casting of observables | false sameness | int-cast collapses distinct responses | **fails as required** |
| 13 | separately simulated prefixes | RNG confound | prefix != short episode (noise then drift from one stream) | **fails as required** |
| 14 | implementation labels leak | leakage | privileged truth imports no instrument code; labels never read | **fails as required** |
| 15 | remove a discriminating probe | repertoire collision | dropping the DRIVE probe -> `EQUIVALENCE_CLASS_ONLY` | **fails as required** |

All must-fail controls fail as required, including #8 (contamination silently removes signal when detection is
disabled) — which is the flip side of the G5 failure: with detection ENABLED the instrument still cannot catch
kappa below ~0.15.
