"""WL2SMF00 INDEPENDENT REFERENCE implementation.

Deliberately different from the production module in every place a difference is possible, and it
imports NOTHING from it. Written from the specification in WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC.md.

Differences on purpose:
  * weights derived from the trapezoid rule written as a matrix-vector contraction, not a loop
  * sums accumulated in REVERSE index order (exactness must not depend on order)
  * the norm computed through the u/v coordinates, never through delta_A/delta_B directly
  * the median obtained from a counting argument on the sorted multiset, not by index arithmetic
"""
from __future__ import annotations
from fractions import Fraction as Fr

_TIMES = [Fr(4), Fr(8), Fr(12), Fr(16), Fr(20), Fr(24), Fr(28), Fr(32), Fr(36), Fr(40)]


def _trapz_matrix(n):
    """row j of the trapezoid contraction: 1/2 to each adjacent interval it borders."""
    M = [[Fr(0)] * n for _ in range(n)]
    for k in range(n - 1):
        M[k][k] += Fr(1, 2)
        M[k + 1][k] += Fr(1, 2)
    return M


def weights():
    n = len(_TIMES)
    dx = [_TIMES[k + 1] - _TIMES[k] for k in range(n - 1)]
    M = _trapz_matrix(n)
    raw = [sum((M[j][k] * dx[k] for k in range(n - 1)), Fr(0)) for j in range(n)]
    tot = sum(raw, Fr(0))
    return [r / tot for r in raw]


WR = weights()
TR = len(WR)


def rsum(vals):
    """exact sum, accumulated in reverse order"""
    acc = Fr(0)
    for x in reversed(list(vals)):
        acc = acc + Fr(float(x))
    return acc


def X_channels(rho, maskA, maskB, B):
    ia = [i for i in range(len(rho)) if maskA[i]]
    ib = [i for i in range(len(rho)) if maskB[i]]
    return rsum(rho[i] for i in ia) / B, rsum(rho[i] for i in ib) / B


def normalizer(rho, maskA, maskB):
    idx = [i for i in range(len(rho)) if (maskA[i] or maskB[i])]
    return rsum(rho[i] for i in idx)


def M2sq(dA, dB):
    """computed ONLY through u and v, never directly from the two channels."""
    tot = Fr(0)
    for h in reversed(range(TR)):
        u = dA[h] + dB[h]
        v = dA[h] - dB[h]
        tot += WR[h] * (u * u + v * v) / 2
    return tot


def median(vals):
    s = sorted(Fr(float(x)) for x in vals)
    n = len(s)
    lo = [x for x in s if sum(1 for y in s if y < x) < (n + 1) // 2]
    if n % 2 == 1:
        return s[(n - 1) // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def tau_dynamic_sq(XA, XB, XA0, XB0, coeff=Fr(1, 100)):
    tot = Fr(0)
    for h in reversed(range(TR)):
        tot += WR[h] * ((XA[h] - XA0) ** 2 + (XB[h] - XB0) ** 2)
    return coeff * coeff * tot


def tau_site_sq(rho0, maskA, maskB, B, coeff=Fr(1, 100)):
    med = median([rho0[i] for i in range(len(rho0)) if (maskA[i] or maskB[i])])
    wpost = sum(WR, Fr(0))
    return (coeff * med / B) * (coeff * med / B) * wpost


def tau_material_sq(eta_sq, dyn_sq, site_sq):
    best = eta_sq
    for x in (dyn_sq, site_sq):
        if x > best:
            best = x
    return best
