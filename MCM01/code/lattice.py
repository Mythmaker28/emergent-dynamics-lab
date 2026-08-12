"""Exact lattice quantities for the MINCORE/MTW01 engine family.

PURE DETERMINISTIC ANALYSIS. No World is constructed, nothing is advanced, no random number is
drawn. Every quantity here is a closed-form or quadrature evaluation of the engine's own
transition rule, read from the frozen source.

THE ONE-PARTICLE STEP OF `_diffuse`
-----------------------------------
`_diffuse(s, p_hop)` applies FOUR direction attempts in sequence within one step, each moving a
particle with probability q = p_hop/4. For a single particle the two axes are independent and,
per axis, the displacement is

    P(+1) = q(1-q)      P(-1) = q(1-q)      P(0) = q^2 + (1-q)^2

because "+1 then -1" returns the particle to its starting cell. Writing a = 2q(1-q):

    <dy^2> = a      <r^2> = 2a      and with the convention <r^2> = 4*D*t,   D_eff = a/2 = q(1-q)

so the effective diffusion constant is  D_eff = q(1-q),  NOT p_hop/4 = q.  The two agree to
first order in q and differ by 5 percent at p_hop = 0.2 and by 25 percent at p_hop = 1.

    characteristic function per axis:   phi1(k) = 1 - a*(1 - cos k)
    in two dimensions:                  phi(ky,kx) = phi1(ky)*phi1(kx)

GREEN'S FUNCTION AT THE ORIGIN
------------------------------
For a walk with per-step survival s and characteristic function phi,

    G(0) = sum_{t>=0} s^t P(walk at the origin at time t)
         = (1/(2*pi)^2) INT INT dky dkx / (1 - s*phi(ky,kx))

evaluated here by tensor-product trapezoid quadrature, whose convergence is checked by doubling
the resolution. G(0) is the expected number of steps a particle spends in the cell where it was
created, counting returns, before it is removed.
"""
from __future__ import annotations

import math

import numpy as np


def q_of(p_hop):
    return p_hop / 4.0


def a_of(p_hop):
    q = q_of(p_hop)
    return 2.0 * q * (1.0 - q)


def D_eff(p_hop):
    """Effective diffusion constant of the engine's four-attempt step, <r^2> = 4*D*t."""
    q = q_of(p_hop)
    return q * (1.0 - q)


def D_naive(p_hop):
    """The value MINCORE and MTW01 assumed."""
    return p_hop / 4.0


def _phi_axis(k, a):
    return 1.0 - a * (1.0 - np.cos(k))


def green_origin(a_list, survival, n=2048):
    """G(0) for a walk whose per-step displacement is the SUM of the independent steps described
    by the coefficients in a_list (one entry per species taking part in the relative motion),
    with per-step survival `survival`.

    a_list = [a] for a single species; [a_X, a_Y] for the X-minus-organiser relative walk, whose
    characteristic function is the product of the two.
    """
    if survival >= 1.0:
        return float("inf")
    k = (np.arange(n) + 0.5) * (2.0 * math.pi / n) - math.pi
    ph = np.ones((n, n))
    for a in a_list:
        ph = ph * np.outer(_phi_axis(k, a), np.ones(n)) * np.outer(np.ones(n), _phi_axis(k, a))
    val = np.mean(1.0 / (1.0 - survival * ph))
    return float(val)


def green_origin_converged(a_list, survival, tol=1e-6, n0=512, nmax=8192):
    """Quadrature with an explicit convergence certificate."""
    n, prev = n0, green_origin(a_list, survival, n0)
    while n < nmax:
        n *= 2
        cur = green_origin(a_list, survival, n)
        if abs(cur - prev) <= tol * max(1.0, abs(cur)):
            return {"G0": cur, "n": n, "delta": abs(cur - prev), "converged": True}
        prev = cur
    return {"G0": prev, "n": n, "delta": float("nan"), "converged": False}


# ------------------------------------------------------------------ derived engine quantities
def G_body_about_organiser(p_hop_X, p_hop_Y, muX, **kw):
    """G(0) for a body molecule RELATIVE TO ITS ORGANISER.

    The source of body molecules is the organiser's own cell, and the organiser moves. What
    matters for whether the source stays switched on is the time a body molecule spends in the
    SAME CELL AS THE ORGANISER, so the relevant walk is the difference of the two, whose
    characteristic function is the product. Ignoring volume exclusion can only make a particle
    MORE mobile, so this value is a LOWER bound on the true G(0) and the maintenance condition
    built on it is conservative.
    """
    return green_origin_converged([a_of(p_hop_X), a_of(p_hop_Y)], 1.0 - muX, **kw)


def G_resource(p_hop_S, phi, **kw):
    """G(0) for the resource field, whose local feed acts as a relaxation at rate phi and
    therefore as a per-step survival (1 - phi) for a 'resource deficit' random walker."""
    return green_origin_converged([a_of(p_hop_S)], 1.0 - phi, **kw)


def c_X_transport(S0, p_hop_S, phi, **kw):
    """Certified steady supply of resource units to a perfectly absorbing sink at one cell.

    The resource field obeys, in the linearised feed regime,
        S(t+1) = diffusion(S) + phi*(S0 - S)        away from the sink
        S = 0                                        at the sink
    whose stationary flux into the sink is  J = S0 / G_S(0)  with G_S(0) the Green's function of
    the same walk at survival (1 - phi). This is the largest number of resource units per step
    that ONE cell can draw from the lattice indefinitely.

    Assumptions, stated so they can be checked: the feed is linearised (`min(S0-n, free)`
    replaced by `S0-n`, exact whenever free capacity is not the binding term), volume exclusion
    on the resource is ignored, and the sink is perfectly absorbing. The first two make this an
    UPPER bound on the sustainable supply; the third also makes it an upper bound. It is
    therefore a certified upper bound on the sustainable c_X, not an estimate of the realised
    one.
    """
    g = G_resource(p_hop_S, phi, **kw)
    return {"c_X_transport": S0 / g["G0"], "G_S0": g["G0"], "quadrature": g}


def c_X_hard_cap(CAP, n_organisers_in_cell=1):
    """EXACT integer maximum of cand_X = min(n[SX], free) over every occupancy vector the engine
    permits in a cell that carries at least one organiser. Exhaustive, no approximation.

    NOTE. n[SX] is NOT bounded by S0: the feed stops adding at S0, but `_diffuse` moves resource
    units between cells with `accepted = min(movers, dest_free)`, which is capped by free
    capacity and not by S0. A cell can therefore hold more than S0 resource units. The bound
    `N_X <= S0/muX` quoted by MTW01 is consequently an approximation, not an exact bound.
    """
    best, arg = 0, None
    for nSX in range(CAP + 1):
        for nSY in range(CAP + 1):
            for nX in range(CAP + 1):
                for nW in range(CAP + 1):
                    occ = nSX + nSY + nX + nW + n_organisers_in_cell
                    if occ > CAP:
                        continue
                    v = min(nSX, CAP - occ)
                    if v > best:
                        best, arg = v, {"nSX": nSX, "nSY": nSY, "nX": nX, "nWaste": nW,
                                        "nY": n_organisers_in_cell, "free": CAP - occ}
    return best, arg


def Q_max_exact(CAP, S0_unused=None):
    """EXACT integer maximum of Q = nX * c_Y with c_Y = min(n[SY], free), over every occupancy
    vector the engine permits in a cell carrying at least one organiser.

    MTW01 restricted n[SY] <= S0 and obtained 27. The restriction is not sound, for the reason
    given in c_X_hard_cap, so the search is repeated here WITHOUT it. Both values are returned.
    """
    def search(sy_cap):
        best, arg = 0, None
        for nX in range(CAP + 1):
            for nSY in range(min(sy_cap, CAP) + 1):
                for nSX in range(CAP + 1):
                    for nW in range(CAP + 1):
                        occ = nX + 1 + nSX + nSY + nW
                        if occ > CAP:
                            continue
                        v = nX * min(nSY, CAP - occ)
                        if v > best:
                            best, arg = v, {"nX": nX, "nY": 1, "nSX": nSX, "nSY": nSY,
                                            "nWaste": nW, "free": CAP - occ,
                                            "c_Y": min(nSY, CAP - occ)}
        return best, arg
    return {"with_nSY_le_S0_3": search(3), "without_that_restriction": search(CAP),
            "space_searched": "all integer (nX, nSY, nSX, nWaste) with nY = 1 and total "
                              "occupancy <= CAP; %d^4 candidates before the occupancy filter"
                              % (CAP + 1)}


def ell_X(p_hop_X, muX, effective=True):
    D = D_eff(p_hop_X) if effective else D_naive(p_hop_X)
    return math.sqrt(D / muX)


def tau_sep(p_hop_X, p_hop_Y, muX, sep_factor=2.0, convention="first_passage_2d",
            effective=True):
    """Time for two organisers born in the same cell to reach separation Delta = sep*L_C.

    first_passage_2d : Delta^2/(4*D_rel) with D_rel = 2*D_Y, i.e. Delta^2/(8*D_Y). Exact mean
                       exit time of a 2D disc of radius Delta from its centre.
    kk_scaling       : L_C^2/D_Y, the scaling form printed by Kamimura and Kaneko.
    naive_delta      : Delta^2/D_Y, the form used in the FIRST evaluation of MTW01 before the
                       first-passage correction. This is the convention behind the number 1519.
    """
    L_C = ell_X(p_hop_X, muX, effective)
    D_Y = D_eff(p_hop_Y) if effective else D_naive(p_hop_Y)
    Delta = sep_factor * L_C
    if convention == "first_passage_2d":
        t = Delta ** 2 / (8.0 * D_Y)
    elif convention == "kk_scaling":
        t = L_C ** 2 / D_Y
    elif convention == "naive_delta":
        t = Delta ** 2 / D_Y
    else:
        raise ValueError(convention)
    return {"L_C": L_C, "Delta": Delta, "D_Y": D_Y, "tau_sep": t, "convention": convention}


def window_emptiness(p_hop_X, p_hop_Y, muX, muY, sep_factor=2.0, safety=2.0, P_star=0.90,
                     convention="first_passage_2d", effective=True):
    """Left-hand side of the non-emptiness condition of the minority timescale window.

        LOWER  R_Y > a_Y = muY
        UPPER  R_Y <= -ln(P*) / (2 * safety * tau_sep)
        non-empty  iff  2*safety*muY*tau_sep / (-ln P*)  <  1
    """
    ts = tau_sep(p_hop_X, p_hop_Y, muX, sep_factor, convention, effective)
    H3_max = -math.log(P_star)
    upper = H3_max / (2.0 * safety * ts["tau_sep"])
    lhs = 2.0 * safety * muY * ts["tau_sep"] / H3_max
    return {"tau": ts, "H3_max": H3_max, "window_lower_R_Y": muY, "window_upper_R_Y": upper,
            "emptiness_lhs": lhs, "non_empty": bool(lhs < 1.0)}
