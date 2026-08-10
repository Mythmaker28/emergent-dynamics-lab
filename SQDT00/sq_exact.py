"""SQDT00 exact-arithmetic kernel: CERTIFIED eigenvalue enclosures for an exact rational
symmetric matrix, fast enough for a 32x32 Gram.

Method. Round the exact rational matrix G to a dyadic matrix G_D = N / 2^K with N integer. The
Frobenius rounding error is bounded exactly by delta = n / 2^(K+1) >= ||G - G_D||_2 (Weyl). The
integer matrix N - m I (integer shift m) has its inertia computed by fraction-free (Bareiss)
leading-principal-minor sign changes -- NO denominator clearing, NO pivoting, small integers.
Bisecting m brackets each eigenvalue of G_D; widening by delta gives a certified enclosure of the
eigenvalue of the true rational G. Float is used only to seed brackets. Self-tests guard the
inertia routine at import.
"""
from __future__ import annotations
from fractions import Fraction as Fr
import numpy as np


# ------------------------------------------------------------------ exact leading minors (Bareiss)
def leading_principal_minor_signs(M, n):
    """Signs of the leading principal minors D_1..D_n of an INTEGER symmetric matrix M (list of
    lists of Python ints), by fraction-free elimination WITHOUT pivoting. Returns a list of
    {-1,+1} or None if a leading minor vanished."""
    M = [list(row) for row in M]
    signs = []
    prev = 1
    for k in range(n):
        piv = M[k][k]
        if piv == 0:
            return None
        signs.append(1 if piv > 0 else -1)
        Mk = M[k]
        for i in range(k + 1, n):
            Mi = M[i]
            Mik = Mi[k]
            if Mik == 0:
                for j in range(k + 1, n):
                    Mi[j] = (Mi[j] * piv) // prev
            else:
                for j in range(k + 1, n):
                    Mi[j] = (Mi[j] * piv - Mik * Mk[j]) // prev
        prev = piv
    return signs


def _sign_changes(seq):
    c, prev = 0, 1
    for s in seq:
        if s != prev:
            c += 1
        prev = s
    return c


def _neg_count_int(N, m, n):
    """number of eigenvalues of integer symmetric matrix N strictly below integer m, i.e. number
    of negative eigenvalues of N - m I, via Bareiss minor sign changes. None on a zero minor."""
    A = [[N[i][j] - (m if i == j else 0) for j in range(n)] for i in range(n)]
    s = leading_principal_minor_signs(A, n)
    return None if s is None else _sign_changes(s)


_MAXNUDGE = 8


def enclose_eigs(Grat, n, targets, seeds, K=64):
    """Certified rational enclosures {rank: (lo, hi)} of the eigenvalues of the exact rational
    symmetric matrix Grat, ranks counted from the top (1 = largest). The +/-<=8 integer nudge used
    to step off a vanishing leading minor is absorbed into the certified slack."""
    scale = 1 << K
    N = [[int((Grat[i][j] * scale).__round__()) for j in range(n)] for i in range(n)]
    # slack: Weyl rounding bound + the worst-case nudge, both as exact rationals
    delta = Fr(n, 1 << (K + 1)) + Fr(_MAXNUDGE, scale)

    def neg_below(m):
        """number of eigenvalues of N strictly below m, resolving a vanishing minor by a nudge of
        at most _MAXNUDGE integer units (absorbed into delta)."""
        for off in range(0, _MAXNUDGE + 1):
            for s in ((0,) if off == 0 else (off, -off)):
                r = _neg_count_int(N, m + s, n)
                if r is not None:
                    return r
        raise RuntimeError("inertia undefined near shift")

    out = {}
    for rank, seed in zip(targets, seeds):
        want = n - rank                              # #eigenvalues strictly below lambda_rank
        centre = int(round(seed * scale))
        step = max(1 << (K - 8), 1)
        lo = centre - step
        while neg_below(lo) > want:
            lo -= step
            step *= 2
        step = max(1 << (K - 8), 1)
        hi = centre + step
        while neg_below(hi) < want + 1:
            hi += step
            step *= 2
        it = 0
        while hi - lo > 1 and it < K + 16:
            it += 1
            mid = (lo + hi) // 2
            if neg_below(mid) <= want:
                lo = mid
            else:
                hi = mid
        out[rank] = (Fr(lo, scale) - delta, Fr(hi, scale) + delta)
    return out


# ------------------------------------------------------------------ import-time self-tests
def _selftest():
    rng = np.random.default_rng(0)
    for _ in range(8):
        A = rng.integers(-4, 5, size=(5, 5))
        A = A + A.T
        Aint = [[int(A[i, j]) for j in range(5)] for i in range(5)]
        direct = []
        ok = True
        for k in range(1, 6):
            dm = round(float(np.linalg.det(A[:k, :k].astype(float))))
            if dm == 0:
                ok = False
                break
            direct.append(1 if dm > 0 else -1)
        if not ok:
            continue
        got = leading_principal_minor_signs(Aint, 5)
        assert got == direct
        ev = np.linalg.eigvalsh(A.astype(float))
        assert _sign_changes(got) == int((ev < 0).sum())
    # rational enclosure on a diagonal matrix with tiny magnitudes
    diag = [Fr(5, 10 ** 7), Fr(3, 10 ** 7), Fr(1, 10 ** 7), Fr(0)]
    G = [[diag[i] if i == j else Fr(0) for j in range(4)] for i in range(4)]
    enc = enclose_eigs(G, 4, [1, 2, 3], [5e-7, 3e-7, 1e-7])
    assert enc[1][0] <= Fr(5, 10 ** 7) <= enc[1][1]
    assert enc[2][0] <= Fr(3, 10 ** 7) <= enc[2][1]
    assert enc[3][0] <= Fr(1, 10 ** 7) <= enc[3][1]
    # a dense symmetric case vs numpy
    B = rng.integers(-3, 4, size=(6, 6))
    B = B + B.T
    Grat = [[Fr(int(B[i, j]), 1000) for j in range(6)] for i in range(6)]
    evB = np.sort(np.linalg.eigvalsh(np.array(B) / 1000.0))[::-1]
    encB = enclose_eigs(Grat, 6, [1, 2], [evB[0], evB[1]])
    assert encB[1][0] <= Fr(evB[0]).limit_denominator(10**9) <= encB[1][1] or encB[1][0] <= evB[0] <= float(encB[1][1])


_selftest()
