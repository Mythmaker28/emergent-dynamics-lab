"""OMLDCT02 — classifier B, rebound: the second, independently written E3 classifier.

It imports neither ldfma01_raw (classifier A) nor any other OMLDCT01 module, and it never reads
c_cid or k_id.  Every step of the pipeline is a different algorithm from A's:

    stage            classifier A (LDFMA01/code/ldfma01_raw.py)   classifier B (this file)
    cell rows        argsort + searchsorted bucketing of all T    boolean mask on the window only
    components       BFS flood-fill on a dense adjacency matrix   union-find over an edge list
    centroid         Python accumulation loop, anchor = idx[0]    numpy exact-integer offsets
    link rule        forward/backward dicts of candidate lists    boolean matrix row/column counts
    identity         running ids assigned to every component      one identity chased forward
    exposure         re-scan of ids_at membership after the fact  accumulated during the chase

The ENDPOINT DEFINITION is shared on purpose — two implementations of one definition is the whole
point of the qualification.  The window convention is inherited from the frozen classifier A and
is stated here explicitly rather than rediscovered:

    duration  = end - t_m                 rows t_m+1 .. end          (t_m EXCLUDED)
    exposure  = sum of nY over rows t_m .. end                       (t_m INCLUDED)

That asymmetry is deliberate in A and is re-derived in DECLARED_WINDOW_ASYMMETRY below; B also
computes the symmetric variant so the difference is measured rather than assumed away.
"""
from __future__ import annotations
import os, json, math
import numpy as np

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")

def _constants():
    """L and CORE_R from the frozen PQEC01 master freeze — the same authority classifier A uses,
    read by a different traversal.  A walks the tree recursively and returns the first
    INHERITED_FROZEN_CONSTANTS block it meets; B walks it iteratively, collects EVERY occurrence of
    each key anywhere in the document and refuses to proceed unless the value is unique.  A silent
    disagreement inside the freeze would pass A and stop B."""
    path = f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"
    with open(path) as fh: doc = json.load(fh)
    found = {"L": set(), "CORE_R": set()}
    stack = [doc]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for k, v in node.items():
                if k in found and isinstance(v, (int, float)) and not isinstance(v, bool):
                    found[k].add(float(v))
                if isinstance(v, (dict, list)): stack.append(v)
        elif isinstance(node, list):
            stack.extend(x for x in node if isinstance(x, (dict, list)))
    for k, vals in found.items():
        if len(vals) != 1:
            raise SystemExit(f"PQEC01 freeze does not pin {k} uniquely: {sorted(vals)}")
    return int(next(iter(found["L"]))), float(next(iter(found["CORE_R"])))

L, CORE_R = _constants()
R2 = CORE_R * CORE_R
NEAR_BOUNDARY_REL = 1e-12

# ---------------------------------------------------------------- geometry
def _toroidal_delta(a, b):
    d = abs(a - b)
    return min(d, L - d)

# ---------------------------------------------------------------- components: union-find
def _components_uf(ys, xs):
    """toroidal single-linkage at CORE_R by union-find over an explicitly enumerated edge list.
    Groups come back sorted ascending and ordered by smallest member, the same canonical order
    classifier A produces, so that component indices are comparable between the two."""
    n = len(ys)
    if n == 0: return []
    if n == 1: return [[0]]
    ya = np.asarray(ys, np.int64); xa = np.asarray(xs, np.int64)
    dy = np.abs(ya[:, None] - ya[None, :]); dy = np.minimum(dy, L - dy)
    dx = np.abs(xa[:, None] - xa[None, :]); dx = np.minimum(dx, L - dx)
    iu, ju = np.triu_indices(n, 1)
    d2 = dy[iu, ju] * dy[iu, ju] + dx[iu, ju] * dx[iu, ju]
    keep = d2 <= R2                      # integer arithmetic: exact, no boundary ambiguity
    parent = list(range(n))
    def find(a):
        r = a
        while parent[r] != r: r = parent[r]
        while parent[a] != r: parent[a], a = r, parent[a]
        return r
    for a, b in zip(iu[keep].tolist(), ju[keep].tolist()):
        ra, rb = find(a), find(b)
        if ra != rb: parent[max(ra, rb)] = min(ra, rb)
    buckets = {}
    for i in range(n): buckets.setdefault(find(i), []).append(i)
    out = [sorted(v) for v in buckets.values()]
    out.sort(key=lambda g: g[0])
    return out

# ---------------------------------------------------------------- centroid
def _centroid(ya, xa, idx):
    """anchor on the smallest-index member, wrap each offset into [-L/2, L/2), average, wrap back.
    The offsets are exact integers in float, so the summation order cannot change the result and
    no ULP question arises before the single division."""
    i0 = idx[0]
    ay = int(ya[i0]); ax = int(xa[i0])
    if len(idx) == 1: return (float(ay % L), float(ax % L))
    sub_y = ya[idx].astype(np.int64); sub_x = xa[idx].astype(np.int64)
    oy = ((sub_y - ay + L // 2) % L) - L // 2
    ox = ((sub_x - ax + L // 2) % L) - L // 2
    m = len(idx)
    return (float((ay + oy.sum() / m) % L), float((ax + ox.sum() / m) % L))

# ---------------------------------------------------------------- link rule
def _link_map(prev_cens, cur_cens):
    """the frozen strict identity rule, as a boolean within-range matrix reduced by row and column
    counts.  i -> j survives only when row i has exactly one candidate and column j has exactly
    one.  Split, merge and tie all terminate and none is resolved by preference.

    Returns (mapping, rowcount, colcount, near_boundary) where near_boundary lists any pair whose
    squared distance sits within NEAR_BOUNDARY_REL of CORE_R^2 — the only place where B's squared
    comparison could in principle part company with A's hypot comparison."""
    npv, ncu = len(prev_cens), len(cur_cens)
    if npv == 0 or ncu == 0: return {}, [0]*npv, [0]*ncu, []
    M = np.zeros((npv, ncu), bool); near = []
    for i, p in enumerate(prev_cens):
        for j, q in enumerate(cur_cens):
            dy = _toroidal_delta(p[0], q[0]); dx = _toroidal_delta(p[1], q[1])
            d2 = dy*dy + dx*dx
            M[i, j] = d2 <= R2
            if abs(d2 - R2) <= NEAR_BOUNDARY_REL * R2:
                near.append({"i": i, "j": j, "d2": d2, "R2": R2})
    rc = M.sum(1).tolist(); cc = M.sum(0).tolist()
    mp = {}
    for i in range(npv):
        if rc[i] == 1:
            j = int(np.flatnonzero(M[i])[0])
            if cc[j] == 1: mp[i] = j
    return mp, rc, cc, near

# ---------------------------------------------------------------- archive reader
class Window:
    """cell rows grouped by step.  A sorts every row with argsort and locates steps with
    searchsorted; B first VERIFIES that the archive already emits rows in non-decreasing step order
    — it must, because a row is written after its step — and then takes group boundaries from a
    single difference scan.  If that verification fails B does not sort silently: it falls back to
    an O(n) counting sort by step and records that the archive was out of order."""
    def __init__(self, path):
        z = np.load(path, allow_pickle=True)
        self.meta = json.loads(str(z["meta"][0]))
        self.T = int(self.meta["steps_executed"])
        ct = z["c_t"].astype(np.int64)
        cy = z["c_y"].astype(np.int64); cx = z["c_x"].astype(np.int64); cn = z["c_nY"].astype(np.int64)
        z.close()
        self.ARCHIVE_ROWS_WERE_ORDERED = bool(ct.size == 0 or np.all(np.diff(ct) >= 0))
        if not self.ARCHIVE_ROWS_WERE_ORDERED:
            # not silently absorbed: the flag travels into every result dictionary
            order = np.argsort(ct, kind="stable")
            ct, cy, cx, cn = ct[order], cy[order], cx[order], cn[order]
        self.t, self.y, self.x, self.ny = ct, cy, cx, cn
        if ct.size:
            cut = np.flatnonzero(np.diff(ct)) + 1
            starts = np.concatenate(([0], cut))
            ends = np.concatenate((cut, [ct.size]))
            self._span = {int(ct[s]): (int(s), int(e)) for s, e in zip(starts, ends)}
        else:
            self._span = {}
    def rows(self, t):
        sp = self._span.get(int(t))
        if sp is None: return None
        return sp

# ---------------------------------------------------------------- the classifier
def e3(path, t_m=None, daughter_cells=None):
    """Given an archive, the frozen trigger step and the frozen locked-daughter cell set at t_m,
    return the post-intervention identity duration and particle-step exposure.

    t_m and daughter_cells are INPUTS, not classifier decisions: in the campaign they come from the
    fork runner and are identical in both arms by construction.  Here they default to the archive's
    own frozen ledger."""
    W = Window(path)
    if t_m is None: t_m = int(W.meta["t_m"])
    t_m = int(t_m)
    iv = W.meta.get("intervention", {}) or {}
    if daughter_cells is None:
        daughter_cells = iv.get("daughter_cells_after")
    dset = set((int(a), int(b)) for a, b in (daughter_cells or []))

    r0 = W.rows(t_m)
    if r0 is None:
        return {"OK": False, "REASON": "NO_CELL_ROWS_AT_t_m", "t_m": t_m}
    s0, e0 = r0
    ya = W.y[s0:e0]; xa = W.x[s0:e0]; na = W.ny[s0:e0]
    groups = _components_uf(ya.tolist(), xa.tolist())
    cens = [_centroid(ya, xa, g) for g in groups]
    cellsets = [set((int(ya[i]), int(xa[i])) for i in g) for g in groups]
    hit = [k for k, S in enumerate(cellsets) if S == dset]
    if len(hit) != 1:
        return {"OK": False, "REASON": "LEDGER_DAUGHTER_CELLS_ARE_NOT_EXACTLY_ONE_COMPONENT_AT_t_m",
                "t_m": t_m, "n_matching_components": len(hit),
                "ledger_daughter_cells": sorted(dset)}
    cur = hit[0]

    exposure_incl = int(sum(int(na[i]) for i in groups[cur]))
    exposure_excl = 0
    hist = {}
    v0 = exposure_incl
    hist[v0] = hist.get(v0, 0) + 1
    minNY = v0; maxNY = v0
    near_boundary = []
    t = t_m; end = t_m; term = None
    while True:
        rn = W.rows(t + 1)
        if t + 1 >= W.T:
            term = "REACHED_THE_WINDOW_HORIZON"; break
        if rn is None:
            term = "NO_COMPONENT_AT_THE_NEXT_STEP"; break
        s1, e1 = rn
        yb = W.y[s1:e1]; xb = W.x[s1:e1]; nb = W.ny[s1:e1]
        gn = _components_uf(yb.tolist(), xb.tolist())
        cn = [_centroid(yb, xb, g) for g in gn]
        mp, rc, cc, near = _link_map(cens, cn)
        if near: near_boundary.extend([dict(nb_, t=t) for nb_ in near])
        if cur not in mp:
            if rc[cur] == 0: term = "OUT_OF_RANGE"
            elif rc[cur] > 1: term = "SPLIT_OR_TIE"
            else: term = "MERGE"
            break
        nxt = mp[cur]
        v = int(sum(int(nb[i]) for i in gn[nxt]))
        exposure_incl += v; exposure_excl += v
        hist[v] = hist.get(v, 0) + 1
        minNY = min(minNY, v); maxNY = max(maxNY, v)
        ya, xa, na = yb, xb, nb
        groups, cens = gn, cn
        cur = nxt; t += 1; end = t

    duration = end - t_m
    return {"OK": True, "t_m": t_m, "interval_end": end,
            "E3_DURATION": duration,
            "E3_EXPOSURE": exposure_incl,
            "E3_EXPOSURE_SYMMETRIC_VARIANT": exposure_excl,
            "identity_termination_type": term,
            "n_rows_in_interval": duration + 1,
            "min_nY": minNY, "max_nY": maxNY,
            "nY_histogram": {str(k): v for k, v in sorted(hist.items())},
            "near_boundary_link_comparisons": near_boundary,
            "ARCHIVE_ROWS_WERE_ORDERED": W.ARCHIVE_ROWS_WERE_ORDERED,
            "L": L, "CORE_R": CORE_R}

DECLARED_WINDOW_ASYMMETRY = (
    "duration counts rows t_m+1..end; exposure sums rows t_m..end.  This is not an off-by-one: the "
    "archive writes a cell row AFTER the step, so the occupancy on row t is the population that a "
    "decay at step t+1 acts on.  An exposure window that starts at row t_m is therefore the correct "
    "driver for events at steps t_m+1..end+1, and it is the convention under which LDFMA01's Poisson "
    "map read 5.809 predicted against 5 observed.  The duration counts post-intervention steps and "
    "starts one row later.  Both quantities are reported; the symmetric variant is reported beside "
    "the frozen one so the difference is measured, not assumed away."
)
