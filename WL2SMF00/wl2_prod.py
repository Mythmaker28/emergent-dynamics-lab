"""WL2SMF00 PRODUCTION threshold pipeline.

Response-independence is structural: this module has no import of, and no code path to, any
carrier or environmental response array. It accepts only baseline rho, sham trajectories, masks,
the normalizer, the frozen weights and static panel coefficients.
"""
from __future__ import annotations
from fractions import Fraction as Fr

H_GRID = [40 * i for i in range(1, 11)]
DT = Fr(1, 10)
COEFF = Fr(1, 100)                     # inherited from WSFSCRP00, not fitted


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
W_POST = sum(W, Fr(0))                 # h0 is not a scored time, so this is exactly 1


def exact_sum(vals):
    """Exact rational sum of float64 values. Every float64 IS a dyadic rational."""
    return sum((Fr(float(x)) for x in vals), Fr(0))


def normalizer(rho, maskA, maskB):
    return exact_sum([rho[i] for i in range(len(rho)) if maskA[i] or maskB[i]])


def X_channels(rho, maskA, maskB, B):
    """The RAW reader. Undifferenced. Exactly rational."""
    a = exact_sum([rho[i] for i in range(len(rho)) if maskA[i]]) / B
    b = exact_sum([rho[i] for i in range(len(rho)) if maskB[i]]) / B
    return a, b


def M2sq(dA, dB):
    """||z||^2 = sum_h w_h (dA_h^2 + dB_h^2), exact."""
    return sum((W[h] * (dA[h] * dA[h] + dB[h] * dB[h]) for h in range(T)), Fr(0))


def uv(dA, dB):
    """orthonormal channel coordinates, as exact rational coefficient lists (sqrt(w) implied)."""
    return ([dA[h] + dB[h] for h in range(T)], [dA[h] - dB[h] for h in range(T)])


def uv_energy(dA, dB):
    u, v = uv(dA, dB)
    return sum((W[h] * (u[h] * u[h] + v[h] * v[h]) / 2 for h in range(T)), Fr(0))


def exact_median(vals):
    s = sorted(Fr(float(x)) for x in vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def tau_dynamic_sq(XA, XB, XA0, XB0):
    """(0.01 * ||g2||)^2 with g2 the sham's own evolution away from h0."""
    g = sum((W[h] * ((XA[h] - XA0) ** 2 + (XB[h] - XB0) ** 2) for h in range(T)), Fr(0))
    return COEFF * COEFF * g


def tau_site_sq(rho0, maskA, maskB, B):
    """(0.01 * RHO_MED / B * sqrt(W_POST))^2, exact because W_POST is rational."""
    med = exact_median([rho0[i] for i in range(len(rho0)) if maskA[i] or maskB[i]])
    return (COEFF * med / B) ** 2 * W_POST


def eta_oracle_sq(eps_A, eps_B):
    return sum((W[h] * (eps_A[h] ** 2 + eps_B[h] ** 2) for h in range(T)), Fr(0))


def tau_material_sq(eta_sq, dyn_sq, site_sq):
    return max(eta_sq, dyn_sq, site_sq)


def cell_verdict(m2sq, tau_sq):
    """Exact arithmetic: intervals are points, so equality is unambiguous and is FAILURE."""
    if m2sq > tau_sq:
        return "CELL_MATERIAL_PASS"
    if m2sq <= tau_sq:
        return "CELL_MATERIAL_FAIL"
    return "CELL_MATERIAL_NUMERICALLY_UNRESOLVED"


def aggregate(alpha, tau_sq_list):
    E = sum((alpha[i] * tau_sq_list[i] for i in range(len(alpha))), Fr(0))
    return E                                    # A_TAU = sqrt(E), taken by the caller


def tau_contrast(coeffs, tau_list):
    return sum((abs(coeffs[i]) * tau_list[i] for i in range(len(coeffs))), Fr(0))
