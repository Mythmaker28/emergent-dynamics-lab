"""ETCMNFC core: canonical carrier semantics, exact arithmetic, eligible edges, the frozen
maximum-support lexicographic matching, the raw-byte transposition, and the passive ON tap.

Everything here is written to be exact. Where an invariant is claimed, it is proved either by a
multiset identity on raw bytes or by an exact rational (dyadic) accumulation -- never by
np.sum, np.allclose or a small residual.
"""
from __future__ import annotations
import sys, os, json, hashlib
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import numpy as np
import domc_core as K
import etpc_core as E
import ppai_engine as PE
from ppai_engine import PPAIEngine, PPAIParams, kappa
from edlab.substrates.scaffold.engine import lap, EPS
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState

L = 64
ALIVE_EPS = 1e-4                 # the KERNEL's own material predicate threshold
GAIN_ON = 1.0 / 3.0
Z_INDEX = 0
FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
# every canonical field except the target carrier Mf[0] and its declared pure descendants
PUBLIC_FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake")


# ------------------------------------------------------------------ exact arithmetic
def exact_sum(a):
    """Exact rational sum of a float64 array. Order-independent by construction: Fraction
    addition is exact, so no summation order can change the result."""
    return sum((Fr(float(v)) for v in np.asarray(a).ravel()), Fr(0))


def exact_sum_at(arr, ys, xs):
    return sum((Fr(float(arr[y, x])) for y, x in zip(ys, xs)), Fr(0))


def multiset_sha(a):
    """sha256 of the sorted raw bytes of an array: an exact multiset fingerprint."""
    b = np.sort(np.asarray(a, dtype=np.float64).ravel().view(np.int64))
    return hashlib.sha256(b.tobytes()).hexdigest()


def arr_sha(name, a):
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(name.encode()); h.update(str(a.shape).encode())
    h.update(str(a.dtype.str).encode()); h.update(a.tobytes(order="C"))
    return h.hexdigest()


def full_state_sha(st):
    """Hash EVERY canonical array plus the step counter. The engine holds no other dynamical
    state: no integrator memory, no event queue, no RNG, no scheduler state, no cache (proved
    in the A1 schema audit)."""
    parts = {f: arr_sha(f, getattr(st, f)) for f in FIELDS}
    parts["step"] = hashlib.sha256(str(int(st.step)).encode()).hexdigest()
    h = hashlib.sha256()
    for k in sorted(parts):
        h.update(k.encode()); h.update(parts[k].encode())
    return h.hexdigest(), parts


def public_sha(st, include_mf1=True):
    """The OFF/ON public projection: every canonical field that can influence future public
    dynamics, EXCLUDING only Mf[0] and its pure descendants. Mf[1] is a NON-target field and is
    deliberately included, which makes the test strictly stronger."""
    h = hashlib.sha256()
    for f in sorted(PUBLIC_FIELDS):
        h.update(arr_sha(f, getattr(st, f)).encode())
    if include_mf1:
        h.update(arr_sha("Mf1", st.Mf[1]).encode())
    h.update(str(int(st.step)).encode())
    return h.hexdigest()


# ------------------------------------------------------------------ canonical semantics (A1)
def z_of(st):
    return st.Mf[Z_INDEX] / np.maximum(st.rho, EPS)


def alive_of(st):
    return st.rho > ALIVE_EPS


def domain_ok(mf0, rho):
    """The COMPLETE joint admissibility set for the canonical carrier, from the A1 audit:
      C1  |Mf[0]_i| <= rho_i          (clip on the intensive, then Mf = rho*newm)
      C2  Mf[0]_i == 0.0 exactly wherever rho_i <= ALIVE_EPS   (the alive gate)
      plus finiteness, and strict positivity of rho where z = Mf[0]/rho is formed."""
    fin = np.isfinite(mf0) & np.isfinite(rho)
    c1 = np.abs(mf0) <= rho
    c2 = (rho > ALIVE_EPS) | (mf0 == 0.0)
    return fin & c1 & c2, {"finite": fin, "C1": c1, "C2": c2}


# ------------------------------------------------------------------ B0 : eligible edges
def site_ids(mem, k):
    ys, xs = mem[k]
    return np.asarray(ys, dtype=np.int64) * L + np.asarray(xs, dtype=np.int64)


def eligible_edges(st, mem):
    """A candidate edge may connect i in A to j in B only if the storage weights are
    byte-identical and the COMPLETE post-swap local joint state is admissible.

    rho_i == rho_j is NOT required. Mf[0] and rho enter ONLY through the frozen boolean
    predicate; neither their values, nor their prospective changes, nor z, nor any descendant
    is read by the matching objective or the tie-break."""
    (ya, xa), (yb, xb) = mem["A"], mem["B"]
    x = st.Mf[Z_INDEX]
    rA, rB = st.rho[ya, xa], st.rho[yb, xb]
    xA, xB = x[ya, xa], x[yb, xb]
    # w is a compile-time constant 1.0 at every site (A1). Compare its raw bits anyway.
    wbits = np.float64(1.0).tobytes()
    wa = [wbits] * len(rA)
    wb = [wbits] * len(rB)
    n_a, n_b = len(rA), len(rB)
    ok = np.zeros((n_a, n_b), dtype=bool)
    for i in range(n_a):
        for j in range(n_b):
            if wa[i] != wb[j]:
                continue
            post_i, post_j = xB[j], xA[i]
            oi, _ = domain_ok(np.array([post_i]), np.array([rA[i]]))
            oj, _ = domain_ok(np.array([post_j]), np.array([rB[j]]))
            ok[i, j] = bool(oi[0] and oj[0] and rA[i] > 0.0 and rB[j] > 0.0)
    return ok


# ------------------------------------------------------------------ B1 : frozen matching
def _max_matching(adj, n_a, n_b, banned_a=(), banned_b=()):
    """Kuhn's algorithm. Deterministic: adjacency lists are in ascending index order."""
    ba, bb = set(banned_a), set(banned_b)
    match_b = [-1] * n_b

    def try_k(i, seen):
        for j in adj[i]:
            if j in bb or seen[j]:
                continue
            seen[j] = True
            if match_b[j] == -1 or try_k(match_b[j], seen):
                match_b[j] = i
                return True
        return False

    size = 0
    for i in range(n_a):
        if i in ba:
            continue
        if try_k(i, [False] * n_b):
            size += 1
    return size, match_b


def frozen_matching(ok, ids_a, ids_b):
    """THE single frozen algorithm, fixed before any primary ID exists.

      1. form every eligible A-B edge;
      2. maximise the number of disjoint pairs;
      3. among all maximum-cardinality matchings, take the unique one whose complete sorted
         list of canonical (immutable_A_id, immutable_B_id) pairs is lexicographically smallest.

    No floating tolerance, no binning, no repeated search order, no rho-, Mf[0]-, z- or
    effect-distance cost. The result depends only on immutable site ids and the boolean
    eligibility matrix."""
    n_a, n_b = ok.shape
    order_a = np.argsort(ids_a, kind="stable")           # ascending immutable id
    order_b = np.argsort(ids_b, kind="stable")
    adj = [[int(j) for j in order_b if ok[i, j]] for i in range(n_a)]
    M, _ = _max_matching(adj, n_a, n_b)
    chosen, ba, bb = [], set(), set()
    remaining = M
    for i in order_a:
        i = int(i)
        if i in ba:
            continue
        for j in adj[i]:
            if j in bb:
                continue
            # can a maximum matching of the remaining size still be completed without i and j?
            sz, _ = _max_matching(adj, n_a, n_b, ba | {i}, bb | {j})
            if sz == remaining - 1:
                chosen.append((int(ids_a[i]), int(ids_b[j]), i, j))
                ba.add(i); bb.add(j); remaining -= 1
                break
        if remaining == 0:
            break
    chosen.sort(key=lambda t: (t[0], t[1]))
    return M, chosen


def manifest(st, mem):
    ok = eligible_edges(st, mem)
    ids_a, ids_b = site_ids(mem, "A"), site_ids(mem, "B")
    M, pairs = frozen_matching(ok, ids_a, ids_b)
    (ya, xa), (yb, xb) = mem["A"], mem["B"]
    I = [(int(ya[i]), int(xa[i])) for (_, _, i, j) in pairs]
    J = [(int(yb[j]), int(xb[j])) for (_, _, i, j) in pairs]
    man = {"max_cardinality": int(M), "n_pairs": len(pairs),
           "eligible_edge_fraction": float(ok.mean()),
           "pairs_by_immutable_id": [[a, b] for (a, b, _, _) in pairs],
           "sites_A": I, "sites_B": J,
           "n_sites_A": len(ya), "n_sites_B": len(yb)}
    man["hash"] = hashlib.sha256(
        json.dumps({k: man[k] for k in sorted(man)}, sort_keys=True).encode()).hexdigest()
    return man, I, J


# ------------------------------------------------------------------ B2 : raw-byte transposition
def transpose(st, I, J, identity=False):
    """Out of place, through a buffer. Never reconstructed from rho*z."""
    out = st.copy()
    out.Mf = st.Mf.copy()
    if identity or not I:
        return out
    flat = [y * L + x for y, x in I] + [y * L + x for y, x in J]
    if len(set(flat)) != len(flat):
        raise ValueError("transpose: the pair list is not a set of disjoint 2-cycles; "
                         "a repeated site would silently break the multiset, Q and the "
                         "involution. Refusing to apply.")
    before = st.Mf[Z_INDEX].copy()
    after = before.copy()
    for (yi, xi), (yj, xj) in zip(I, J):
        after[yi, xi] = before[yj, xj]
        after[yj, xj] = before[yi, xi]
    out.Mf[Z_INDEX] = after
    return out


def carrier_content(st, mem, k):
    ys, xs = mem[k]
    return exact_sum_at(st.Mf[Z_INDEX], ys, xs)          # w_i == 1 exactly (A1)


def displacement(before, after):
    """gross_canonical_displacement = 0.5 * exact_sum_i |w_i * dMf0_i|.
    A DESCRIPTIVE displacement induced by the permutation. It is NOT a conserved content, NOT a
    treatment normalisation and NOT transported material mass."""
    d = np.abs(after - before)
    return Fr(1, 2) * exact_sum(d)


# ------------------------------------------------------------------ engines and the passive tap
def engine(gain):
    return PPAIEngine(C.SPEC, PPAIParams(gain=gain, z_index=Z_INDEX), C.TRACER)


class TappedEngine(PPAIEngine):
    """Copies the native per-face transfer operands. Every ARITHMETIC statement is identical
    to the parent's, statement by statement; the tap adds a call counter and guarded `.copy()`
    appends, so the claim is arithmetic identity, NOT character-for-character identity of the
    source. Passivity is therefore not asserted from the text: it is measured by comparing the
    complete post-window state with tap on and tap off."""

    def __init__(self, spec, par, tracer):
        super().__init__(spec, par, tracer)
        self.ledger = []
        self.call = 0
        self.enabled = True

    def _face_transport(self, X, kap):
        if self.par.gain == 0.0:
            return lap(X)
        self.call += 1
        out = np.zeros_like(X)
        for axis in (-2, -1):
            kf = 0.5 * (kap + np.roll(kap, -1, axis))
            fl = kf * (np.roll(X, -1, axis) - X)
            if self.enabled:
                self.ledger.append({"call": self.call, "axis": int(axis), "fl": fl.copy()})
            out += fl - np.roll(fl, 1, axis)
        if self.enabled:
            # the ACTUAL return value and the ACTUAL operands, copied. These are what make the
            # reconstruction oracle non-vacuous: the ledger is later compared against THIS
            # array, not against a second evaluation of the same expression.
            self.ledger.append({"call": self.call, "returned": out.copy(),
                                "X_in": X.copy(), "kap_in": kap.copy()})
        return out

    def step(self, st):
        out = super().step(st)
        if self.enabled:
            # native masks, read from the returned state AFTER the arithmetic is complete.
            # rho is not modified after the writer, so this IS the alive mask the kernel used.
            self.ledger.append({"call": None, "alive": (out.rho > ALIVE_EPS).copy(),
                                "step": int(out.step)})
        return out


def native_boundary_links(alive):
    """The material-bath link set of the KERNEL's own material predicate. Each native link is
    recorded exactly once, by axis and by the lower-index endpoint."""
    links = []
    for ax in (0, 1):
        nb = np.roll(alive, -1, ax)
        xor = alive ^ nb
        ys, xs = np.nonzero(xor)
        for y, x in zip(ys, xs):
            here = bool(alive[y, x])
            m = (y, x) if here else ((y + 1) % L, x) if ax == 0 else (y, (x + 1) % L)
            b = ((y + 1) % L, x) if ax == 0 else (y, (x + 1) % L)
            if here:
                links.append((ax, int(y), int(x), m, b))
            else:
                links.append((ax, int(y), int(x), m, (int(y), int(x))))
    return links
