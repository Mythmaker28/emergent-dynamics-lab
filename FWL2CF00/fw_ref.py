"""FWL2CF00 INDEPENDENT REFERENCE scorer, written from the spec. Imports nothing from fw_prod.
Differences on purpose: weights by matrix contraction; reverse-order accumulation; M2 obtained
only through the u/v coordinates; deltas formed by an explicit accumulation loop."""
from __future__ import annotations
from fractions import Fraction as Fr

_TIMES = [Fr(4 * k) for k in range(1, 11)]


def weights():
    n = len(_TIMES)
    dx = [_TIMES[k + 1] - _TIMES[k] for k in range(n - 1)]
    M = [[Fr(0)] * n for _ in range(n)]
    for k in range(n - 1):
        M[k][k] += Fr(1, 2)
        M[k + 1][k] += Fr(1, 2)
    raw = [sum((M[j][k] * dx[k] for k in range(n - 1)), Fr(0)) for j in range(n)]
    tot = sum(raw, Fr(0))
    return [r / tot for r in raw]


WR = weights()
TR = len(WR)


def rsum(vals):
    acc = Fr(0)
    for x in reversed(list(vals)):
        acc = acc + Fr(float(x))
    return acc


def X_channels(rho, mA, mB, B):
    ia = [i for i in range(len(rho)) if mA[i]]
    ib = [i for i in range(len(rho)) if mB[i]]
    return rsum(rho[i] for i in ia) / B, rsum(rho[i] for i in ib) / B


def deltas(XA_int, XB_int, XA_sham, XB_sham):
    dA, dB = [], []
    for h in range(TR):
        dA.append(XA_int[h] - XA_sham[h])
        dB.append(XB_int[h] - XB_sham[h])
    return dA, dB


def M2sq(dA, dB):
    tot = Fr(0)
    for h in reversed(range(TR)):
        u = dA[h] + dB[h]
        v = dA[h] - dB[h]
        tot += WR[h] * (u * u + v * v) / 2
    return tot
