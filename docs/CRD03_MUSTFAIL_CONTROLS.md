# CRD-03 MUST-FAIL CONTROLS

Each control must FAIL (produce a wrong/rejected result) for the benchmark to be discriminating. Confirmed on dev.

| # | control | required behaviour | observed |
|---|---|---|---|
| 1 | single contaminated reference (CRD-02) | attenuates the response | z_single/s_true = **0.85** (attenuated) |
| 2 | two collinear references | fail identifiability | `REFERENCE_MIXTURE_ILL_CONDITIONED` |
| 3 | hiding the condition number | overconfident on collinear refs | the diversity gate catches it (else accepted) |
| 4 | assume perfect antisymmetry on nonlinear | even part ignored | even part **is** detected (even_significant) |
| 5 | signed differencing under hysteresis | wrong odd amplitude | truth = odd part; the odd part is well-defined and recovered (hysteresis carried in the even diagnostic) |
| 6 | disable complementary-probe check | admit contaminated control regions | comp non-null flag fires on D11, silent on D10 |
| 7 | remove absolute-scale calibration | amplitude ambiguity returns | common-mode → lower bound (ABSOLUTE_SCALE_UNAVAILABLE) |
| 8 | fit reference coeff on the active tail | suppresses slow causal response | tail-fit of the contaminated ref → **0.04** (response erased) |
| 9 | max-over-blocks aggregation | selects drift excursions | median-over-phases used; max-over-blocks reproduced CRD-00 inflation |
| 10 | independent sham subtraction (no reference) | reproduce CRD-00 drift residual | no-ref residual > reference-corrected residual |
| 11 | exact float inequality | false differences | `0.1+0.2 != 0.3` → identical-after-roundoff flagged different |
| 12 | integer casting | false sameness | `int(1e-4)==int(2e-4)==0` collapses distinct responses |
| 13 | separately simulated prefixes | RNG confound | documented: a prefix is not a short episode (noise then drift from one stream) |
| 14 | implementation labels leak | leakage | privileged truth imports no instrument code; labels never read |
| 15 | remove a discriminating probe | repertoire collision | silent system → null/equivalence class |

All must-fail controls fail as required.
