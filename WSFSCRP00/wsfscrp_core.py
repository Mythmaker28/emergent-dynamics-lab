"""WSFSCRP00 core: a self-contained fixed-support integrated-rho oracle.

STRICT DEPENDENCY SEPARATION (Section 0.4). This module does NOT import or use the ETCMNFC
TappedEngine, its tap arithmetic, its component-bath or global-bath ledgers, its pre-step or
exchange material-bath masks, its depth ratios, or its 60/60 count. The ONLY ETCMNFC object
reused is the conservative Mf[0] transposition operator, and only after its code hash is checked
and its domain preconditions are re-verified per unit.

The reader, endpoint, restart oracle and twin tests below are separately implemented here.
"""
from __future__ import annotations
import sys, os, json, hashlib, itertools
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import numpy as np
import domc_core as K
import ppai_core as P
from ppai_engine import PPAIEngine, PPAIParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState

L = 64
DT = C.SPEC.dt
GAIN_ON = 1.0 / 3.0
FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
RHO_THRESHOLD = 0.30            # inherited detector threshold, strict >
MIN_SITES = 12                  # inherited minimum component size
H_GRID = [40, 80, 120, 160, 200, 240, 280, 320, 360, 400]   # inherited scored native steps


def engine():
    return PPAIEngine(C.SPEC, PPAIParams(gain=GAIN_ON, z_index=0), C.TRACER)


# ------------------------------------------------------------------ exact dyadic arithmetic
def dsum(vals):
    """Exact rational sum. Order-independent: Fraction addition is exact."""
    return sum((Fr(float(v)) for v in vals), Fr(0))


def dmedian(vals):
    s = sorted(Fr(float(v)) for v in vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


# ------------------------------------------------------------------ trapezoidal weights
def weights(phys):
    p = list(phys)
    T = len(p) - 1
    assert T >= 1, "at least two scored times are required"
    v = [Fr(0)] * len(p)
    v[0] = (Fr(p[1]).limit_denominator(10**9) - Fr(p[0]).limit_denominator(10**9)) / 2
    v[T] = (Fr(p[T]).limit_denominator(10**9) - Fr(p[T - 1]).limit_denominator(10**9)) / 2
    for j in range(1, T):
        v[j] = (Fr(p[j + 1]).limit_denominator(10**9)
                - Fr(p[j - 1]).limit_denominator(10**9)) / 2
    s = sum(v, Fr(0))
    return [x / s for x in v]


PHYS = [Fr(h) * Fr(DT).limit_denominator(10**9) for h in H_GRID]
W = weights(PHYS)


# ------------------------------------------------------------------ the fixed-support reader
def _components(rho):
    """Connected components of {rho > 0.30} on the PERIODIC 4-connected lattice.
    Separately implemented here; nothing is imported from ETCMNFC."""
    m = rho > RHO_THRESHOLD
    lab = -np.ones(m.shape, dtype=np.int64)
    comps = []
    for y in range(L):
        for x in range(L):
            if not m[y, x] or lab[y, x] >= 0:
                continue
            cid = len(comps)
            stack, cells = [(y, x)], []
            lab[y, x] = cid
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    na, nb = (a + da) % L, (b + db) % L
                    if m[na, nb] and lab[na, nb] < 0:
                        lab[na, nb] = cid
                        stack.append((na, nb))
            comps.append(sorted(cells))
    return comps


def t0_masks(st):
    """Exactly-two-eligible-component admissibility, then two immutable boolean site masks.
    The pair is UNORDERED; canonical serialisation is by the lexicographically sorted
    immutable site-id lists. No largest-pair selection, ever."""
    comps = [c for c in _components(st.rho) if len(c) >= MIN_SITES]
    if len(comps) != 2:
        return None, {"n_eligible": len(comps),
                      "sizes": sorted(len(c) for c in _components(st.rho))}
    ids = [sorted(y * L + x for y, x in c) for c in comps]
    order = sorted(range(2), key=lambda i: ids[i])          # canonical unordered-pair order
    masks = []
    for i in order:
        m = np.zeros((L, L), dtype=bool)
        for y, x in comps[i]:
            m[y, x] = True
        masks.append(m)
    MA, MB = masks
    assert not (MA & MB).any() and MA.any() and MB.any()
    meta = {"n_eligible": 2, "n_A": int(MA.sum()), "n_B": int(MB.sum()),
            "ids_A": ids[order[0]], "ids_B": ids[order[1]],
            "mask_sha": hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest()}
    return (MA, MB), meta


def reference_masks(st):
    """A minimal, deliberately different reference implementation of the same rule, used only
    to cross-check the unordered pair. Label-order differences are not disagreements."""
    m = st.rho > RHO_THRESHOLD
    seen = np.zeros_like(m)
    out = []
    for idx in range(L * L):
        y, x = divmod(idx, L)
        if not m[y, x] or seen[y, x]:
            continue
        q, cell = [idx], []
        seen[y, x] = True
        while q:
            k = q.pop(0)
            a, b = divmod(k, L)
            cell.append(k)
            for na, nb in (((a + 1) % L, b), ((a - 1) % L, b), (a, (b + 1) % L), (a, (b - 1) % L)):
                if m[na, nb] and not seen[na, nb]:
                    seen[na, nb] = True
                    q.append(na * L + nb)
        if len(cell) >= MIN_SITES:
            out.append(tuple(sorted(cell)))
    return tuple(sorted(out))


def B_of(st, MA, MB):
    """Fixed pre-treatment normaliser from raw baseline bytes."""
    sel = np.nonzero(MA | MB)
    return dsum(st.rho[sel])


def q_channels(st, MA, MB, B):
    return (dsum(st.rho[np.nonzero(MA)]) / B, dsum(st.rho[np.nonzero(MB)]) / B)


# ------------------------------------------------------------------ complete state hashing
def state_fields(st):
    """Enumerated by dynamic inspection of the returned object, not by a trusted name list."""
    return {k: v for k, v in vars(st).items()}


def full_sha(st):
    h = hashlib.sha256()
    for k in sorted(vars(st)):
        v = getattr(st, k)
        a = np.ascontiguousarray(v) if isinstance(v, np.ndarray) else np.array([v])
        h.update(k.encode()); h.update(str(a.shape).encode())
        h.update(str(a.dtype.str).encode()); h.update(a.tobytes(order="C"))
    return h.hexdigest()


def save(st, path):
    np.savez(path, **{f: np.ascontiguousarray(getattr(st, f)) for f in FIELDS},
             step=np.array([st.step], dtype=np.int64))
    return full_sha(st)


def load(path):
    d = np.load(path)
    return IOMState(*(np.array(d[f], copy=True) for f in FIELDS), int(d["step"][0]))


# ------------------------------------------------------------------ founder generator
def make_founder(seed, geom):
    """The frozen inherited generator, LawSpec and checkpoint time. One engine start."""
    K.set_geometry(geom)
    e = engine()
    f = K.advance(e, K.found(seed), K.T_FOUND)
    hA, hB = (P.HIST_H, P.HIST_L) if seed % 2 == 0 else (P.HIST_L, P.HIST_H)
    return K.advance(e, K.apply_dual_history(e, f, hA, hB), K.SETTLE)


def canonical_geometry_id(geom, meta):
    """Support-axis identifier. Geometry class plus the unordered support-size pair; it is a
    stratification label, never an independence claim."""
    return f"{geom}:{min(meta['n_A'], meta['n_B'])}-{max(meta['n_A'], meta['n_B'])}"


# ------------------------------------------------------------------ scoring one arm
def run_arm(st0, op, MA, MB, B):
    e = engine()
    cur = op(st0.copy())
    qa0, qb0 = q_channels(cur, MA, MB, B)
    qa, qb = [], []
    for t in range(1, max(H_GRID) + 1):
        cur = e.step(cur)
        if t in H_GRID:
            a, b = q_channels(cur, MA, MB, B)
            qa.append(a); qb.append(b)
    return {"q0": (qa0, qb0), "qA": qa, "qB": qb, "end_sha": full_sha(cur)}


def loss(pred_A, pred_B, true_A, true_B):
    """Exact rational primary loss."""
    return sum((W[j] * (abs(pred_A[j] - true_A[j]) + abs(pred_B[j] - true_B[j]))
                for j in range(len(W))), Fr(0))
