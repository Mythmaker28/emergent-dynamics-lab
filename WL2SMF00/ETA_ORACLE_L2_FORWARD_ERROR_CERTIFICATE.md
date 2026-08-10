# ETA_ORACLE_L2_FORWARD_ERROR_CERTIFICATE

## Claim

    eps_INT = eps_SHAM = eps_SUBTRACTION = eps_RELOAD = 0   exactly, for every channel and time
    ETA_ORACLE_L2[d] = 0                                    for every descendant

This bounds the **scoring path on serialized states**: reader, subtraction and reload. It is not a
stability bound on engine dynamics, and it is not claimed to be one.

## Proof, branch by branch

1. **Reload.** `numpy.savez` stores raw IEEE754 bytes and `numpy.load` returns them unchanged.
   Verified on an adversarial vector including a subnormal (`2^-1074`), `-0.0`, `1e16`, `1e-300`
   and values whose decimal forms do not round-trip: the byte images are identical.
2. **Reader.** `wsfscrp_core.dsum` accumulates `Fraction(float(v))`. Every IEEE754 double is
   *exactly* a dyadic rational, so the conversion is exact; `Fraction` addition is exact and
   therefore order-independent. `B_of` is the same construction, and `q_channels` divides two exact
   rationals. No rounding occurs.
3. **Subtraction.** `delta = X[INT] - X[SHAM_0]` is a difference of two exact rationals.
4. **Weights.** `w` is built in exact `Fraction` arithmetic from the frozen physical times, so
   `sum_h w_h (delta_A^2 + delta_B^2)` is exact.

## The test is not vacuous

An oracle that always says "exact" is worthless. Two controls fire:

* the production reader (forward order) and the independent reference reader (**reverse** order)
  agree exactly on the adversarial vector -- if the arithmetic were floating point they would not;
* a float64-accumulating scorer on the **same input** produces a **different** value, so the test
  demonstrably distinguishes an exact path from an inexact one.

## Consequence for the threshold

Because `ETA_ORACLE_L2 = 0` on every descendant, it never dominates:
`TAU_MATERIAL_L2 = max(0, TAU_DYNAMIC_L2, TAU_SITE_L2)` is set by a **scientific** floor in
16 of 16 descendants, never by numerical detectability. That is exactly the separation this
programme was created to establish, and it is the reason the disposition is
`MATERIAL_AND_NUMERICAL_SEPARATED` rather than `NUMERICAL_ONLY`.
