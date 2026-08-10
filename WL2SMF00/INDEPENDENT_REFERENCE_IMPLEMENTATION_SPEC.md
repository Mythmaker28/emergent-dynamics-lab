# INDEPENDENT_REFERENCE_IMPLEMENTATION_SPEC

`wl2_ref.py` is written from the estimand specification, not from the production code, and an AST
audit confirms it imports nothing from `wl2_prod.py`.

Deliberate differences, so that agreement is informative:

| quantity | production | reference |
|---|---|---|
| weights | trapezoid written as an explicit loop over interior nodes | trapezoid written as a matrix contraction against interval widths |
| summation | forward index order | reverse index order |
| norm | directly from `delta_A`, `delta_B` | only through the `u`, `v` coordinates |
| median | index arithmetic on the sorted list | counting argument on the sorted multiset |
| `max` | Python `max` over three terms | explicit pairwise comparison loop |

Agreement is required on 40 randomly generated fixtures for `X_channels`, `normalizer`,
`tau_site_sq` and `M2sq`, and on all 16 sealed descendants for `TAU_MATERIAL_L2`, `RHO_MED`, `B`
and the `t0` reader. A negative control confirms the reference detects a deliberately wrong
production value, so agreement is evidence rather than tautology.
