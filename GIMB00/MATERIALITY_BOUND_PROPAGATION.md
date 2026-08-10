# MATERIALITY_BOUND_PROPAGATION

Written before any numeric response array is loaded. Nothing here is fitted; every constant comes
from the frozen quadrature weights.

## What the inherited bound bounds

WSFSCRP00 and FSCMA00 declared a cell's response material by

    A_bu = sum_h w_h * ( |delta_A_h| + |delta_B_h| )   >   ETA_b
    ETA_b = max( 1e-12, 0.01*G_bu, 0.01*rho_median/B_b )

`A_bu` is a **weighted L1** functional. The quotient estimands `R0` and `sqrt(L2)` live in the
**weighted L2** norm of `z = (u, v)`, where

    ||z||^2 = ||u||^2 + ||v||^2 = sum_h w_h ( delta_A_h^2 + delta_B_h^2 )

These are different norms. A bound in one is not automatically a bound in the other, and the
handoff forbids improvising a conversion constant.

## The exact worst-case propagation, derived

Let `t_h = |delta_A_h| + |delta_B_h| >= 0`. Then `delta_A_h^2 + delta_B_h^2 <= t_h^2`, so

    ||z||^2 <= sum_h w_h t_h^2

subject to `sum_h w_h t_h = A_bu` and `t >= 0`. That is a linear constraint on a nonnegative
vector maximising a convex function, so the maximum sits at a vertex: all the mass on the single
index with the **smallest** weight, `t_h = A_bu / w_h`. Hence

    max sum_h w_h t_h^2 = A_bu^2 / min_h w_h
    ||z|| <= A_bu / sqrt(min_h w_h)

With the frozen weights `w = [1/18, 1/9 x 8, 1/18]`, `min_h w_h = 1/18` and

    eta_b_z = sqrt(18) * ETA_b   ~=  4.2426 * ETA_b

The bound is attained, so no smaller constant is valid without extra assumptions about the shape
of the response curve. Any such assumption would be an improvised conversion.

## Aggregation, as prescribed

    FROZEN_BETWEEN_RESPONSE_MATERIALITY_ENERGY = sum_i alpha_i * eta_i_z^2
    FROZEN_MODAL_MATERIALITY_AMPLITUDE         = sqrt( sum_i alpha_i * eta_i_z^2 )
    ETA_CONTRAST(c) = sum_i |c_i| * eta_i_z              for a normalised contrast c

No maximum, no simple mean, no pooled empirical RMS, no fitted covariance.

## The compatibility test that decides whether this bound may be used

Because the constant is a worst case for a delta-concentrated curve, it may be far larger than the
true L2 size of a smooth response. The frozen criterion in GIMB00_FREEZE.md therefore requires the
propagated bound to reproduce the parent's own accepted materiality decisions:

    for every parent carrier cell accepted as material (A_bu > ETA):
        require   ||z_cell|| > eta_z_cell

If that fails, the propagation is not a compatible restatement of the inherited threshold in L2
units, `ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`, only relative structure may be reported, and
`PHASE2_LICENSE = NO`.

## Quadratic embeddings

`v OUTER v` is a fourth-order object. A response-amplitude bound does not transfer to a Frobenius
norm by name. Unless a separate dimensionally valid propagation is derived,
`PROJECTIVE_EMBEDDING_BOUND = NOT_AVAILABLE` and `H3_K_BOUND = NOT_AVAILABLE`; such objects remain
shape diagnostics and their materiality must be settled in the original quotient distance.
