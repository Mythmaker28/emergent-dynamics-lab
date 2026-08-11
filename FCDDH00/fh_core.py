"""FCDDH00 PRODUCTION core.

Certified-arithmetic implementation of the frozen FCDDH00 estimands (master freeze Section 6).

Design rules enforced here:
  * every response quantity is an EXACT rational or a RIGOROUS rational interval enclosure;
  * the only irrational entering the response map is sqrt(W[h]/2); it is enclosed, never rounded;
  * every comparison is a certified interval comparison whose third outcome is UNRESOLVED;
  * no dynamic import, no eval, no unresolved getattr, no string-to-call dispatch, no filename or
    seed label inference;
  * nothing in this module reads a geometry label, an allocation label, a panel role or a
    candidate-axis score in any admission, reader, gauge or threshold formula.

Frozen inherited constants are re-derived here from the committed parent specification and are
cross-checked against the parent modules by the pre-analysis oracle.
"""
from __future__ import annotations

from fractions import Fraction as Fr

# --------------------------------------------------------------------------- frozen constants
H_GRID = [40 * i for i in range(1, 11)]          # inherited scored native steps
DT = Fr(1, 10)                                   # inherited SPEC.dt
PHYS = [Fr(h) * DT for h in H_GRID]              # physical scored times 4 .. 40


def _weights():
    n = len(PHYS)
    v = [Fr(0)] * n
    v[0] = (PHYS[1] - PHYS[0]) / 2
    v[n - 1] = (PHYS[n - 1] - PHYS[n - 2]) / 2
    for j in range(1, n - 1):
        v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
    s = sum(v, Fr(0))
    return [x / s for x in v]


W = _weights()
T = len(W)
W_POST = sum(W, Fr(0))                           # exactly 1
COEFF = Fr(1, 100)                               # inherited threshold coefficient, not fitted
RHO_THRESHOLD = Fr(3, 10)
MIN_SITES = 12
DIM = 2 * T                                      # 20

PREC = 200                                       # outward-rounding precision, bits


# ------------------------------------------------------------------ outward-rounded dyadics
def _dfloor(x: Fr, p: int = PREC) -> Fr:
    if x == 0:
        return Fr(0)
    n, d = x.numerator, x.denominator
    e = abs(n).bit_length() - d.bit_length()
    sh = p - e
    if sh > 0:
        return Fr((n << sh) // d, 1 << sh)
    return Fr((n // (d << (-sh))) << (-sh), 1)


def _dceil(x: Fr, p: int = PREC) -> Fr:
    return -_dfloor(-x, p)


class Iv:
    """Rigorous rational interval. Every operation rounds OUTWARD, so the enclosure is valid."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        lo = Fr(lo)
        hi = Fr(hi)
        if lo > hi:
            lo, hi = hi, lo
        self.lo = lo
        self.hi = hi

    # -- constructors -------------------------------------------------------------------
    @staticmethod
    def exact(x):
        return Iv(Fr(x), Fr(x))

    def round_out(self, p: int = PREC):
        return Iv(_dfloor(self.lo, p), _dceil(self.hi, p))

    # -- arithmetic ---------------------------------------------------------------------
    def __add__(self, o):
        o = o if isinstance(o, Iv) else Iv.exact(o)
        return Iv(_dfloor(self.lo + o.lo), _dceil(self.hi + o.hi))

    def __sub__(self, o):
        o = o if isinstance(o, Iv) else Iv.exact(o)
        return Iv(_dfloor(self.lo - o.hi), _dceil(self.hi - o.lo))

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __mul__(self, o):
        o = o if isinstance(o, Iv) else Iv.exact(o)
        c = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(_dfloor(min(c)), _dceil(max(c)))

    __rmul__ = __mul__
    __radd__ = __add__

    def __truediv__(self, o):
        o = o if isinstance(o, Iv) else Iv.exact(o)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("interval division by an interval containing zero")
        c = (self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi)
        return Iv(_dfloor(min(c)), _dceil(max(c)))

    # -- predicates ---------------------------------------------------------------------
    def gt0(self):
        """certified > 0 ; returns True | False | None(unresolved)"""
        if self.lo > 0:
            return True
        if self.hi <= 0:
            return False
        return None

    def gt(self, o):
        o = o if isinstance(o, Iv) else Iv.exact(o)
        return (self - o).gt0()

    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def mid(self):
        return (self.lo + self.hi) / 2

    def width(self):
        return self.hi - self.lo

    def __repr__(self):
        return "Iv(%.17g, %.17g)" % (float(self.lo), float(self.hi))

    def as_pair(self):
        return [str(self.lo), str(self.hi)]

    def fl(self):
        return float(self.mid())


def isqrt_iv(x: Iv, p: int = PREC) -> Iv:
    """Rigorous enclosure of sqrt over a non-negative interval."""
    if x.hi < 0:
        raise ValueError("sqrt of a negative interval")
    lo = x.lo if x.lo > 0 else Fr(0)

    def _sq(v: Fr, up: bool) -> Fr:
        if v == 0:
            return Fr(0)
        # integer sqrt on a scaled numerator/denominator, then round outward
        scale = 1 << (2 * p)
        num = (v.numerator * scale) // v.denominator
        r = _isqrt(num)
        if up and r * r < num:
            r += 1
        return Fr(r, 1 << p)

    return Iv(_sq(lo, False), _sq(x.hi, True))


def _isqrt(n: int) -> int:
    if n < 0:
        raise ValueError
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


SQRT2 = isqrt_iv(Iv.exact(Fr(2)))
INV_SQRT2 = Iv.exact(Fr(1)) / SQRT2

# sqrt(W[h]/2): exactly 1/6 at the two endpoints, sqrt(1/18) = sqrt(2)/6 in the interior
SW = [isqrt_iv(Iv.exact(W[h] / 2)) for h in range(T)]


# ------------------------------------------------------------------ exact rational reader
def esum(vals):
    """Exact rational sum of float64 values. Every float64 IS a dyadic rational."""
    return sum((Fr(float(x)) for x in vals), Fr(0))


def read_series(rho_support, support_index, MA, MB):
    """The frozen reader on the fixed support. rho_support[k] is the raw rho on the support at
    scored time index k (k = 0 is h0). Returns exact rational X_A, X_B series and B."""
    fa = MA.ravel()[support_index]
    fb = MB.ravel()[support_index]
    XA, XB, B = [], [], None
    for k in range(rho_support.shape[0]):
        row = [float(x) for x in rho_support[k]]
        if k == 0:
            B = esum(row)
        XA.append(esum([row[i] for i in range(len(row)) if fa[i]]) / B)
        XB.append(esum([row[i] for i in range(len(row)) if fb[i]]) / B)
    return XA, XB, B


def deltas(XA_act, XB_act, XA_sham, XB_sham):
    """Exact per-scored-time response, h0 excluded (structural zero)."""
    dA = [XA_act[h + 1] - XA_sham[h + 1] for h in range(T)]
    dB = [XB_act[h + 1] - XB_sham[h + 1] for h in range(T)]
    r0 = (XA_act[0] - XA_sham[0], XB_act[0] - XB_sham[0])
    return dA, dB, r0


def m2sq(dA, dB):
    return sum((W[h] * (dA[h] * dA[h] + dB[h] * dB[h]) for h in range(T)), Fr(0))


def uv_energy(dA, dB):
    """Same quantity through the orthonormal u/v coordinates; must equal m2sq exactly."""
    return sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) / 2 for h in range(T)), Fr(0))


def uv_vectors(dA, dB):
    """u and v halves of the 20-dimensional parent coordinate space, as interval enclosures."""
    u = [SW[h] * Iv.exact(dA[h] + dB[h]) for h in range(T)]
    v = [SW[h] * Iv.exact(dA[h] - dB[h]) for h in range(T)]
    return u, v


def z_of(u, v, s):
    """z(s) = (u , s*v) in R^20 with the linked A/B gauge s in {+1,-1}."""
    assert s in (1, -1)
    return list(u) + [(x if s == 1 else -x) for x in v]


# ------------------------------------------------------------------ TAU (inherited, unchanged)
def tau_dynamic_sq(XA, XB):
    """(1/100)^2 * sum_h W[h]((XA[h]-XA[0])^2 + (XB[h]-XB[0])^2) on the SHAM series."""
    g = sum((W[h] * ((XA[h + 1] - XA[0]) ** 2 + (XB[h + 1] - XB[0]) ** 2) for h in range(T)), Fr(0))
    return COEFF * COEFF * g


def exact_median(vals):
    s = sorted(Fr(float(x)) for x in vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def tau_site_sq(rho0_support, B):
    med = exact_median(rho0_support)
    return (COEFF * med / B) ** 2 * W_POST


def tau_material_sq(eta_sq, dyn_sq, site_sq):
    return max(eta_sq, dyn_sq, site_sq)


# ------------------------------------------------------------------ linear algebra on floats
def mat_vec(Mrows, x):
    """M @ x with M a list of rows of float64 (exact dyadics) and x a list of Iv."""
    out = []
    for row in Mrows:
        acc = Iv.exact(Fr(0))
        for j, mij in enumerate(row):
            if mij != 0.0:
                acc = acc + Iv.exact(Fr(mij)) * x[j]
        out.append(acc.round_out())
    return out


def vec_sub(a, b):
    return [a[i] - b[i] for i in range(len(a))]


def vec_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]


def vec_scale(a, c):
    c = c if isinstance(c, Iv) else Iv.exact(Fr(c))
    return [(a[i] * c).round_out() for i in range(len(a))]


def dot_iv(a, b):
    acc = Iv.exact(Fr(0))
    for i in range(len(a)):
        acc = acc + a[i] * b[i]
    return acc.round_out()


def dot_float(vfloat, x):
    """<v, x> with v a list of float64 (exact) and x a list of Iv."""
    acc = Iv.exact(Fr(0))
    for i, vi in enumerate(vfloat):
        if vi != 0.0:
            acc = acc + Iv.exact(Fr(vi)) * x[i]
    return acc.round_out()


def norm_iv(x):
    return isqrt_iv(dot_iv(x, x))


# ------------------------------------------------------------------ the frozen estimand chain
class Parent:
    """Immutable parent objects. Loaded once, never modified, never refitted."""

    def __init__(self, mu, P1, P2, e1, e2, tube):
        self.mu = [float(t) for t in mu]
        self.P1 = [[float(t) for t in row] for row in P1]
        self.P2 = [[float(t) for t in row] for row in P2]
        self.e1 = [float(t) for t in e1]
        self.e2 = [float(t) for t in e2]
        self.tube = Fr(tube)
        self.Q = [[(1.0 if i == j else 0.0) - self.P2[i][j] for j in range(DIM)] for i in range(DIM)]


def gauge_statistic(parent, u1, v1, u2, v2):
    """D_desc = sum_o (u_o - mu)^T Q v_o, over the descendant's TWO carrier rows.

    Depends only on that descendant's own two rows and on immutable parent objects. It reads no
    geometry label, no allocation label, no panel role and no candidate axis. Descendant
    separable, therefore block separable.
    """
    acc = Iv.exact(Fr(0))
    for (u, v) in ((u1, v1), (u2, v2)):
        a = [u[i] - Iv.exact(Fr(parent.mu[i])) for i in range(T)] + \
            [Iv.exact(Fr(0)) - Iv.exact(Fr(parent.mu[T + i])) for i in range(T)]
        # u occupies coordinates 0..T-1, v occupies coordinates T..2T-1
        vv = [Iv.exact(Fr(0))] * T + list(v)
        Qa = mat_vec(parent.Q, a)
        acc = acc + dot_iv(Qa, vv)
    return acc.round_out()


def gauge_sign(D: Iv):
    """s minimises the outside-P2 residual. Returns (+1|-1, cooptimal_flag)."""
    g = D.gt0()
    if g is True:
        return -1, False
    if g is False and D.hi < 0:
        return +1, False
    return +1, True          # exactly zero, or not certifiably signed -> co-optimal orbit


def residual_r(parent, z):
    """r = (I - P2) @ (z - mu)."""
    zc = [z[i] - Iv.exact(Fr(parent.mu[i])) for i in range(DIM)]
    return mat_vec(parent.Q, zc)


def differential_d(parent, z1, z2):
    """d = (r2 - r1)/sqrt(2) = Q(z2 - z1)/sqrt(2); mu cancels exactly."""
    diff = vec_sub(z2, z1)
    Qd = mat_vec(parent.Q, diff)
    return [(c * INV_SQRT2).round_out() for c in Qd]


def interaction_x(dN0, dN1, dF0, dF1):
    """x[b] = 1/2 * sum_a ( d[NEAR,a] - d[FAR,a] )."""
    half = Iv.exact(Fr(1, 2))
    out = []
    for i in range(DIM):
        term = (dN0[i] - dF0[i]) + (dN1[i] - dF1[i])
        out.append((term * half).round_out())
    return out


def A_X_block(tau_iv_four):
    """A_X[b] = (1/sqrt(2)) * sum_{g,a} TAU[b,g,a]  (eight rows, |coeff| = 1/(2 sqrt 2) each)."""
    s = Iv.exact(Fr(0))
    for t in tau_iv_four:
        s = s + t
    return (s * INV_SQRT2).round_out()


def A_PAIR(tau_N_aN: Iv, tau_F_aF: Iv):
    """A_PAIR = sqrt(2) * (TAU[NEAR,aN] + TAU[FAR,aF]) (four rows, |coeff| = 1/sqrt(2) each)."""
    return ((tau_N_aN + tau_F_aF) * SQRT2).round_out()


def certified_verdict(lower_side: Iv, upper_side: Iv):
    """strict > with equality counted as FAILURE; unresolved reported as UNRESOLVED."""
    g = (lower_side - upper_side).gt0()
    if g is True:
        return "PASS"
    if g is False:
        return "FAIL"
    return "UNRESOLVED"
