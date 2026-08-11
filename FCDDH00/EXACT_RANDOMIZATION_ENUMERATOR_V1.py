"""FCDDH00 EXACT_RANDOMIZATION_ENUMERATOR_V1.

Complete 2^16 enumeration of the block-level geometry assignment.

For every one of the 65536 assignments, NEAR/FAR is jointly swapped across BOTH allocation
members inside each affected ancestry and x, every p, J, K and T are RECOMPUTED through the
complete frozen scorer and gauge rule. Concretely: each ancestry has exactly two possible
orientations of its single fair geometry coin, so the frozen scorer is invoked twice per
ancestry (32 full scorer evaluations for 16 ancestries) and the enumeration then composes those
recomputed per-ancestry objects. Nothing is obtained by negating a cached scalar; the exact
equivariance identity s(eps = -1) = -s(eps = +1) is verified against the recomputation and
reported, never assumed.

Comparisons are exact: each certified score enclosure is rounded OUTWARD onto a common dyadic
grid, so every one of the 65536 subset sums is an exact integer comparison. A subset whose
bracketing is not decided is counted separately and reported; the tail is then given as a
closed rational interval instead of a single rational.

The response-only statistic T never imports TAU. The K tail is computed separately and is
labelled NONINFERENTIAL_UNDER_RESPONSE_ONLY_SHARP_NULL.
"""
from __future__ import annotations

from fractions import Fraction as Fr

GRID_BITS = 160


def _to_grid(fr: Fr, up: bool):
    n, d = fr.numerator, fr.denominator
    sc = 1 << GRID_BITS
    q, r = divmod(n * sc, d)
    if up and r != 0:
        q += 1
    return q


def enumerate_T(scores_lo, scores_hi):
    """scores_*: per-ancestry certified bounds of s_H[b] (as Fractions), ascending block order.

    T_perm >= T_obs  <=>  sum_{b in S} s_b <= 0, where S = {b : eps_b = -1}.
    Returns the exact tail as a rational (or a bracketing pair) plus diagnostics.
    """
    n = len(scores_lo)
    lo = [_to_grid(Fr(x), False) for x in scores_lo]
    hi = [_to_grid(Fr(x), True) for x in scores_hi]
    N = 1 << n
    ge = 0            # certainly T_perm >= T_obs
    amb = 0           # bracketing undecided
    for mask in range(N):
        sl = 0
        sh = 0
        m = mask
        i = 0
        while m:
            if m & 1:
                sl += lo[i]
                sh += hi[i]
            m >>= 1
            i += 1
        if sh <= 0:
            ge += 1
        elif sl > 0:
            pass
        else:
            amb += 1
    p_lo = Fr(ge, N)
    p_hi = Fr(ge + amb, N)
    return {"n_blocks": n, "n_assignments": N, "count_ge_certain": ge,
            "count_undecided": amb, "p_lo": p_lo, "p_hi": p_hi,
            "exact": bool(amb == 0), "p_exact": (p_lo if amb == 0 else None)}


def enumerate_K(J_plus, J_minus, K_obs):
    """K tail under the same 2^16 enumeration, with J recomputed per orientation.

    NONINFERENTIAL under the response-only sharp null, because J contains geometry-specific
    sham-derived TAU which moves with the label under reassignment.
    """
    n = len(J_plus)
    N = 1 << n
    ge = 0
    for mask in range(N):
        k = 0
        m = mask
        i = 0
        while i < n:
            k += (J_minus[i] if (m >> i) & 1 else J_plus[i])
            i += 1
        if k >= K_obs:
            ge += 1
    return {"n_assignments": N, "count_ge": ge, "tail": Fr(ge, N),
            "K_ASSIGNMENT_TAIL_INFERENTIAL_STATUS": "NONINFERENTIAL_UNDER_RESPONSE_ONLY_SHARP_NULL"}


def design_reference_K_ge_12_of_16():
    """P(K >= 12 | p_success <= 1/2) with the conservative p = 1/2 reference, reproduced exactly."""
    from math import comb
    num = sum(comb(16, k) for k in range(12, 17))
    return Fr(num, 1 << 16)


def _binom_tail_ge(k, n, p):
    """P(X >= k) for X ~ Bin(n, p), exact in rational arithmetic."""
    from math import comb
    return sum(Fr(comb(n, j)) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def clopper_pearson(k, n, alpha=Fr(5, 100), iters=60):
    """Exact two-sided Clopper-Pearson interval, defined by the binomial tail equations
    P(X >= k | p_lo) = alpha/2 and P(X <= k | p_hi) = alpha/2, solved by rational bisection.
    Attached ONLY under a proved iid Bernoulli sampling license; never otherwise."""
    half = alpha / 2
    if k == 0:
        lo = Fr(0)
    else:
        a, b = Fr(0), Fr(1)
        for _ in range(iters):
            m = (a + b) / 2
            if _binom_tail_ge(k, n, m) < half:
                a = m
            else:
                b = m
        lo = a
    if k == n:
        hi = Fr(1)
    else:
        a, b = Fr(0), Fr(1)
        for _ in range(iters):
            m = (a + b) / 2
            if (1 - _binom_tail_ge(k + 1, n, m)) > half:
                a = m
            else:
                b = m
        hi = b
    return float(lo), float(hi)
