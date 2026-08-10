"""FWL2CF00 PRODUCTION scorer. Imports only `fractions`. No engine, no operator, no active call."""
from __future__ import annotations
from fractions import Fraction as Fr

H_GRID = [40 * i for i in range(1, 11)]
DT = Fr(1, 10)


def weights():
    p = [Fr(h) * DT for h in H_GRID]
    n = len(p)
    v = [Fr(0)] * n
    v[0] = (p[1] - p[0]) / 2
    v[n - 1] = (p[n - 1] - p[n - 2]) / 2
    for j in range(1, n - 1):
        v[j] = (p[j + 1] - p[j - 1]) / 2
    s = sum(v, Fr(0))
    return [x / s for x in v]


W = weights()
T = len(W)


def exact_sum(vals):
    return sum((Fr(float(x)) for x in vals), Fr(0))


def X_channels(rho, mA, mB, B):
    a = exact_sum([rho[i] for i in range(len(rho)) if mA[i]]) / B
    b = exact_sum([rho[i] for i in range(len(rho)) if mB[i]]) / B
    return a, b


def deltas(XA_int, XB_int, XA_sham, XB_sham):
    return ([XA_int[h] - XA_sham[h] for h in range(T)],
            [XB_int[h] - XB_sham[h] for h in range(T)])


def M2sq(dA, dB):
    return sum((W[h] * (dA[h] * dA[h] + dB[h] * dB[h]) for h in range(T)), Fr(0))


def uv_energy(dA, dB):
    return sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) / 2 for h in range(T)), Fr(0))


def cell_verdict(m2sq, tausq):
    return "CELL_MATERIAL_PASS" if m2sq > tausq else "CELL_MATERIAL_FAIL"


def tau_contrast(coeffs, taus):
    return sum((abs(coeffs[i]) * taus[i] for i in range(len(coeffs))), Fr(0))
