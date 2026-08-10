# WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC

## Raw reader versus differenced response

    X_A[arm,d,h] = sum_i M_A0[d,i]*rho[arm,d,h,i] / B[d]        (RAW, undifferenced)
    X_B[arm,d,h] = sum_i M_B0[d,i]*rho[arm,d,h,i] / B[d]

`wsfscrp_core.q_channels(st, MA, MB, B)` returns exactly this pair. It is **not** a difference.
The `dA`/`dB` arrays stored by WSFSCRP00, FSCMA00 and GIMB00 are already `arm - sham`. Binding this
distinction explicitly is the point of this section: subtracting a sham from a stored `dA` would
subtract the sham twice.

    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0,d,h]
    delta_B[d,o,h] = X_B[INT,d,o,h] - X_B[SHAM_0,d,h]

## Norm and orthonormal coordinates

    z[d,o] = concat_h( sqrt(w_h)*delta_A[d,o,h], sqrt(w_h)*delta_B[d,o,h] )
    M2[d,o] = ||z||_2

    u[d,o,h] = sqrt(w_h)*(delta_A + delta_B)/sqrt(2)
    v[d,o,h] = sqrt(w_h)*(delta_A - delta_B)/sqrt(2)

    IDENTITY (required, certified): M2^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

The map `(delta_A, delta_B) -> (u, v)` is an orthogonal change of basis in each time slot, so it is
an isometry of the weighted product space. This is why `M2` is simultaneously the natural norm of
the raw two-channel response and of the GIMB00 common/differential decomposition.

## Gauge

    one A/B exchange per DESCENDANT, shared across every scored time and every future arm and dose
    u -> u,  v -> -v,  M2 invariant,  TAU invariant

`M2` alone cannot validate the group scope: some non-physical local swaps leave `M2` numerically
unchanged because the norm is blind to sign patterns. The scope is therefore validated by the
whole-descendant reconstruction oracle inherited from `gimb_oracle_v2.py`, and by a mutation
control that flips exactly one arm and requires the block invariant to change.

## Exactness of the weights

`w` is computed in exact `Fraction` arithmetic from the frozen physical times 4.0 .. 40.0:
`w = ['1/18', '1/9', '1/9', '1/9', '1/9', '1/9', '1/9', '1/9', '1/9', '1/18']`, all strictly positive, summing to exactly 1.
`h0` is not among the scored times, so `W_POST = 1` exactly.
