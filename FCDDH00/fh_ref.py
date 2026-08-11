"""FCDDH00 INDEPENDENT REFERENCE implementation.

Written from the frozen specification (FCDDH00_MASTER_FREEZE.md Section 6) and deliberately
different from `fh_core` in every place a difference is possible. It imports NOTHING from
`fh_core`, `DISCOVERY_AXIS_TRAINER_V1` or `HOLDOUT_FIXED_AXIS_SCORER_V1`.

Differences on purpose:
  * weights obtained from a trapezoid contraction matrix, not from a loop over neighbours;
  * reader sums accumulated in REVERSE index order;
  * the 20-vector built by an explicit (dA,dB) -> (u,v) rotation contraction, not elementwise;
  * the outside-P2 residual built through the mu-form  r = Q(z - mu)  and then
    d = (r2 - r1)/sqrt(2), never through the algebraic shortcut Q(z2 - z1)/sqrt(2);
  * x[b] assembled as an explicit signed sum over the eight rows with coefficient +-1/(2 sqrt 2),
    not as a difference of two allocation-averaged differentials;
  * the linked A/B gauge chosen by evaluating the residual at BOTH signs and taking the argmin,
    not by the sign of the cross statistic;
  * float64 throughout, with an explicit agreement tolerance against the production enclosure.
"""
from __future__ import annotations

import math

import numpy as np

_TIMES = [4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0]


def _trapz_matrix(n):
    M = np.zeros((n, n))
    for k in range(n - 1):
        M[k, k] += 0.5
        M[k + 1, k] += 0.5
    return M


def weights():
    n = len(_TIMES)
    dx = np.array([_TIMES[k + 1] - _TIMES[k] for k in range(n - 1)])
    raw = _trapz_matrix(n)[:, : n - 1] @ dx
    return raw / raw.sum()


WR = weights()
TR = len(WR)
DIMR = 2 * TR
COEFFR = 0.01


def rsum(vals):
    acc = 0.0
    for x in reversed(list(vals)):
        acc += float(x)
    return acc


def read_series(rho_support, support_index, MA, MB):
    fa = MA.ravel()[support_index]
    fb = MB.ravel()[support_index]
    XA, XB, B = [], [], None
    for k in range(rho_support.shape[0]):
        row = np.asarray(rho_support[k], dtype=float)
        if k == 0:
            B = rsum(row[fa | fb])
        XA.append(rsum(row[fa]) / B)
        XB.append(rsum(row[fb]) / B)
    return XA, XB, B


def m2sq(dA, dB):
    """through u and v only"""
    tot = 0.0
    for h in reversed(range(TR)):
        u = dA[h] + dB[h]
        v = dA[h] - dB[h]
        tot += WR[h] * (u * u + v * v) / 2.0
    return tot


_ROT = None


def rot():
    """the (dA,dB) -> (u,v) contraction, as one explicit 20x20 matrix"""
    global _ROT
    if _ROT is None:
        M = np.zeros((2 * TR, 2 * TR))
        for h in range(TR):
            c = math.sqrt(WR[h] / 2.0)
            M[h, h] = c
            M[h, TR + h] = c
            M[TR + h, h] = c
            M[TR + h, TR + h] = -c
        _ROT = M
    return _ROT


def z_of(dA, dB, s):
    w = np.concatenate([np.asarray(dA, float), np.asarray(dB, float)])
    uv = rot() @ w
    out = uv.copy()
    out[TR:] *= s
    return out


def tau_material_sq(XA, XB, rho0_support, B):
    dyn = 0.0
    for h in reversed(range(TR)):
        dyn += WR[h] * ((XA[h + 1] - XA[0]) ** 2 + (XB[h + 1] - XB[0]) ** 2)
    dyn *= COEFFR * COEFFR
    med = float(np.median(np.asarray(rho0_support, dtype=float)))
    site = (COEFFR * med / B) ** 2 * float(WR.sum())
    return max(0.0, dyn, site)


def gauge_sign(mu, Q, u1v1, u2v2):
    """argmin over s of the descendant's total outside-P2 residual, evaluated at BOTH signs."""
    best, arg, vals = None, None, {}
    for s in (+1, -1):
        tot = 0.0
        for (dA, dB) in (u1v1, u2v2):
            z = z_of(dA, dB, s)
            zc = z - mu
            r = Q @ zc
            tot += float(r @ r)
        vals[s] = tot
        if best is None or tot < best:
            best, arg = tot, s
    return arg, vals


def residual_r(mu, Q, z):
    return Q @ (z - mu)


def differential_d(mu, Q, z1, z2):
    return (residual_r(mu, Q, z2) - residual_r(mu, Q, z1)) / math.sqrt(2.0)


def interaction_x(rows):
    """rows: dict (g,a,o) -> z vector. x assembled as an explicit signed sum of the EIGHT rows."""
    raise NotImplementedError("use interaction_x_from_r")


def interaction_x_from_r(rmap):
    """rmap: (g,a,o) -> r vector. x = sum over the eight rows with coefficient +-1/(2 sqrt 2)."""
    c = 1.0 / (2.0 * math.sqrt(2.0))
    acc = np.zeros(DIMR)
    for (g, a, o), r in rmap.items():
        sg = 1.0 if g == "NEAR" else -1.0
        so = 1.0 if o == "CARRIER_2" else -1.0
        acc = acc + (sg * so * c) * np.asarray(r, float)
    return acc


def A_X_block(taus):
    return sum(float(t) for t in taus) / math.sqrt(2.0)


def A_PAIR(tau_N, tau_F):
    return math.sqrt(2.0) * (float(tau_N) + float(tau_F))
