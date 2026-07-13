"""ARCHITECTURE HEAD V4. Spec: docs/ARCHITECTURE_HEAD_V4_SPEC.md. Replaces the RETIRED V3 (D-058).

THE ONE IDEA, and it is the lesson of the whole repair cycle:

    DO NOT INTEGRATE OUT THE NUISANCE PARAMETER. QUOTIENT BY IT.

D-056 killed V2 because its delay estimator was phase-SENSITIVE (it struck at 4 chosen phases and its null was
drawn from the same 4). V3 fixed that by striking at EVERY phase and taking the MEDIAN -- integrating the phase
out. That is invariant, and it is also BLIND: for an edge whose onset is gated by a PERIODIC ARRIVAL, the median
over a full cycle is invariant to exactly the delay it exists to measure. The evaluator saw the gate->output delay
move 184 -> 164; V3 reported 185.5 in both. A false-SAME on the certified edit scale (D-058).

V4 keeps the WHOLE phase-resolved response profile tau_e(phi) and obtains invariance BY SYMMETRY:

    A global phase shift by phi0 acts on the data as a COMMON CYCLIC ROTATION of every edge's profile and of the
    validity mask -- settling phi0 extra steps and striking at p is identical to striking the base circuit at
    (phi0 + p) mod T. So the canonical form is the minimum, over all phi0, of the profiles rotated TOGETHER.

Invariance is then a group quotient, not an average. And a RELATIVE timing change -- one edge's profile shifting
while the others do not -- IS NOT A GROUP ELEMENT. No common rotation can undo it, so it SURVIVES. That is exactly
the signal V3 destroyed.

Two further changes, both forced by D-058:
  * VALIDITY IS PHASE-RESOLVED. Each (component, strike-phase) pair is graded on its own. 6 of 60 phases make the
    V3 probe leave a block behind; under V3 that poisoned the whole circuit. Here it costs those phases only, and
    the bad phases live in the validity mask -- which rotates with everything else and is part of the signature.
  * The null generator is rebuilt (gt_nulls2) and asserts its own coverage of the full cycle.

A_TOPO carries NO delays and NO geometry. A_TAU is compared ONLY after the topology matches. G is auxiliary and is
NEVER composited. Inert components are excluded from A_TOPO: decoration is not architecture.
"""

from __future__ import annotations

import hashlib
import os
import pickle

import numpy as np

from ..substrates.life.fast import step

OBS = 480
TAIL = 120
OCC_THRESH = 0.25
MERGE_GAP = 4
MARGIN = 2
HOLD = 10
SITE = 10
MIN_CELLS = 4
MAX_PERIOD = 240
MIN_VALID_FRAC = 0.5      # PREREGISTERED: a component is RESOLVED if >= half the cycle's strike phases are VALID
EDGE_MAJORITY = 0.5       # PREREGISTERED: an edge exists if it fires in > half of that component's valid phases
EPS = 1e-9
CACHE = os.path.join("results", "_tomo4_cache")


# ------------------------------------------------------------------ clock, from raw trajectories only
def infer_period(g0, max_period=MAX_PERIOD) -> int:
    """The FUNDAMENTAL period: the SMALLEST exact one, so a harmonic can never be reported."""
    g = g0.copy()
    for t in range(1, max_period + 1):
        g = step(g)
        if np.array_equal(g, g0):
            return t
    raise AssertionError("no exact period: the circuit is not settled and cannot be certified")


def _dilate(mask, r):
    out = mask.copy()
    for _ in range(r):
        m = out.copy()
        m[1:, :] |= out[:-1, :]
        m[:-1, :] |= out[1:, :]
        m[:, 1:] |= out[:, :-1]
        m[:, :-1] |= out[:, 1:]
        out = m
    return out


def occupancy(g0, T):
    g, acc = g0.copy(), np.zeros(g0.shape, float)
    for _ in range(T):
        acc += g
        g = step(g)
    return acc / T


def stationary_mask(g0, T):
    return occupancy(g0, T) >= OCC_THRESH


def _clusters_1d(cols, gap=6):
    out, cur = [], []
    for c in sorted(cols):
        if cur and c - cur[-1] > gap:
            out.append(cur)
            cur = []
        cur.append(c)
    if cur:
        out.append(cur)
    return out


def discover_components(g0, out_row, T):
    """Stationary matter that does NOT propagate. Gliders sweep through and are excluded by construction."""
    m = stationary_mask(g0, T)
    m[out_row:, :] = False
    H, W = m.shape
    seen, frags = np.zeros_like(m, bool), []
    for r in range(H):
        for c in range(W):
            if m[r, c] and not seen[r, c]:
                st, cells = [(r, c)], []
                seen[r, c] = True
                while st:
                    y, x = st.pop()
                    cells.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                st.append((ny, nx))
                frags.append(cells)
    boxes = [(min(y for y, _ in f), max(y for y, _ in f), min(x for _, x in f), max(x for _, x in f), len(f))
             for f in frags]
    merged, used = [], set()
    for i, b in enumerate(boxes):
        if i in used:
            continue
        cur, n = list(b[:4]), b[4]
        used.add(i)
        ch = True
        while ch:
            ch = False
            for j, o in enumerate(boxes):
                if j in used:
                    continue
                if (o[0] <= cur[1] + MERGE_GAP and cur[0] <= o[1] + MERGE_GAP
                        and o[2] <= cur[3] + MERGE_GAP and cur[2] <= o[3] + MERGE_GAP):
                    cur = [min(cur[0], o[0]), max(cur[1], o[1]), min(cur[2], o[2]), max(cur[3], o[3])]
                    n += o[4]
                    used.add(j)
                    ch = True
        if n >= MIN_CELLS:
            merged.append(tuple(cur))
    return sorted(merged)


# ------------------------------------------------------------------ one ablation, at ONE strike phase
def _ablate(g0, box, out_row, T):
    """Returns (output-line trace, post-ablation stationary mask). The ablation is held for HOLD steps."""
    r0, r1, c0, c1 = box
    g = g0.copy()
    line = np.empty((OBS + 1, g.shape[1]), dtype=np.int32)
    line[0] = g[out_row]
    for t in range(OBS):
        if t < HOLD:
            g[r0:r1, c0:c1] = 0
        g = step(g)
        line[t + 1] = g[out_row]
    return line, stationary_mask(g, T)


def _grade(g0, base_stat, box, out_row, T):
    """PHASE-RESOLVED validity. Graded at THIS strike phase, on its own.

    EFFICACY    -- it removed live matter here (a silent no-op is not evidence).
    NO NEW MACHINE AT THE SITE -- the ablation must REMOVE the component, not REPLACE it. Clipping an in-flight
        glider can leave a block behind, and at 6 of 60 phases it does. Under V3 that one bad phase invalidated the
        whole circuit. Here it invalidates the phase.
    (SPECIFICITY -- the box must be a WHOLE discovered component -- is structural and checked once, not per phase.)
    """
    H, W = g0.shape
    b = (max(0, box[0] - MARGIN), min(H, box[1] + 1 + MARGIN),
         max(0, box[2] - MARGIN), min(W, box[3] + 1 + MARGIN))
    if int(g0[b[0]:b[1], b[2]:b[3]].sum()) == 0:
        return b, None, None, "NO_OP"
    line, after = _ablate(g0, b, out_row, T)
    site = np.zeros_like(after)
    site[max(0, b[0] - SITE):b[1] + SITE, max(0, b[2] - SITE):b[3] + SITE] = True
    new = after & ~_dilate(base_stat, 2) & site
    if int(new.sum()) >= MIN_CELLS:
        return b, line, after, "MUTILATION"
    return b, line, after, "VALID"


# ================================================================== FULL-CYCLE, PHASE-RESOLVED TOMOGRAPHY
def tomography(g0: np.ndarray, out_row: int, region=None) -> dict:
    T = infer_period(g0)
    phases = tuple(range(T))                    # EXHAUSTIVE. The estimator has NO free phase choice to select.
    base_stat = stationary_mask(g0, T)

    states, g = {}, g0.copy()
    for p in phases:
        states[p] = g.copy()
        g = step(g)
    long_base = np.empty((OBS + T + 1, g0.shape[1]), dtype=np.int32)
    gg = g0.copy()
    long_base[0] = gg[out_row]
    for t in range(OBS + T):
        gg = step(gg)
        long_base[t + 1] = gg[out_row]
    base_at = {p: long_base[p:p + OBS + 1] for p in phases}

    comps = discover_components(g0, out_row, T)
    if region:
        rl, rh, cl, ch = region
        comps = [b for b in comps if rl <= b[0] and b[1] < rh and cl <= b[2] and b[3] < ch]
    comp_set = {tuple(c) for c in comps}

    # ---- pass 1: ablate every component at every phase, grading each pair on its own
    raw, valid = {}, {}
    live_cols = set(np.nonzero(long_base.sum(0))[0])
    for i, box in enumerate(comps):
        if tuple(box) not in comp_set:
            continue
        raw[i], valid[i] = {}, np.zeros(T, bool)
        for p in phases:
            _b, line, _after, st = _grade(states[p], base_stat, box, out_row, T)
            if st != "VALID":
                continue
            valid[i][p] = True
            d = line - base_at[p]
            raw[i][p] = d
            live_cols |= set(np.nonzero(np.abs(d).sum(0))[0])

    out_nodes = [(min(gp), max(gp)) for gp in _clusters_1d(sorted(live_cols))]

    # ---- pass 2: per-edge PHASE PROFILES (not marginals)
    nodes, edges = [], []
    for i, box in enumerate(comps):
        nv = int(valid[i].sum())
        node = {"id": i, "box": box, "n_valid_phases": nv, "valid_mask": valid[i].copy(),
                "resolved": nv >= MIN_VALID_FRAC * T, "targets": {}, "destroys": []}
        if node["resolved"]:
            for j, (lo, hi) in enumerate(out_nodes):
                prof = np.full(T, -1, dtype=np.int32)
                kinds = []
                for p in np.nonzero(valid[i])[0]:
                    dj = raw[i][p][:, lo:hi + 1].sum(1).astype(float)
                    nz = np.nonzero(np.abs(dj) > EPS)[0]
                    if len(nz) == 0:
                        continue
                    drift = float(dj[-TAIL:].mean())
                    k = "PERSISTENT_DOWN" if drift < -EPS else ("PERSISTENT_UP" if drift > EPS else "TRANSIENT")
                    if k == "TRANSIENT":
                        continue                # a WIRE: matter in transit, re-supplied by its source
                    prof[p] = int(nz[0])
                    kinds.append(k)
                if len(kinds) <= EDGE_MAJORITY * max(1, nv):
                    continue                    # not present in a majority of this component's valid phases
                kind = max(set(kinds), key=kinds.count)
                node["targets"][j] = {"kind": kind, "profile": prof, "n_fired": len(kinds)}
                edges.append({"src": i, "dst": j, "kind": kind, "profile": prof})
        nodes.append(node)

    base_live = {j for j, (lo, hi) in enumerate(out_nodes) if long_base[:, lo:hi + 1].sum() > 0}
    suppressed = set(range(len(out_nodes))) - base_live
    sourced = {e["dst"] for e in edges if e["kind"] == "PERSISTENT_DOWN"}
    explained = {e["dst"] for e in edges if e["kind"] == "PERSISTENT_UP"}
    cov = {"live_outputs": sorted(base_live), "unsourced_live": sorted(base_live - sourced),
           "unexplained_suppressed": sorted(suppressed - explained),
           "n_components": len(comps),
           "n_resolved": sum(1 for n in nodes if n["resolved"]),
           "n_unresolved": sum(1 for n in nodes if not n["resolved"]),
           "valid_phase_fracs": [round(n["n_valid_phases"] / T, 3) for n in nodes]}
    cov["outputs_explained"] = not cov["unsourced_live"] and not cov["unexplained_suppressed"]
    cov["complete"] = cov["outputs_explained"] and cov["n_unresolved"] == 0
    return {"T": T, "n_out": len(out_nodes), "out_nodes": out_nodes, "nodes": nodes, "edges": edges,
            "coverage": cov}


def cached_tomography(g0, out_row, region=None) -> dict:
    os.makedirs(CACHE, exist_ok=True)
    k = hashlib.sha256(g0.tobytes() + str(region).encode() + str(out_row).encode()).hexdigest()[:24]
    fp = os.path.join(CACHE, k + ".pkl")
    if os.path.exists(fp):
        return pickle.load(open(fp, "rb"))
    t = tomography(g0, out_row, region)
    pickle.dump(t, open(fp, "wb"))
    return t


# ================================================================== A_TOPO -- no delays, no geometry
def topo_signature(t: dict) -> tuple:
    rows = []
    for n in t["nodes"]:
        if not n["resolved"]:
            continue
        if not n["targets"] and not n["destroys"]:
            continue                            # CAUSALLY INERT: decoration is not architecture
        rows.append((tuple(sorted((j, tt["kind"]) for j, tt in n["targets"].items())), len(n["destroys"])))
    return (t["n_out"], tuple(sorted(rows)))


def head_A_TOPO(t1, t2) -> str:
    """ASYMMETRIC BY DESIGN. An incomplete graph can fabricate a DIFFERENCE as easily as a sameness -- a missing
    node looks exactly like an absent one -- so without OUTPUTS_EXPLAINED nothing may be concluded at all.
    DIFFERENT then needs sufficient evidence; SAME needs complete evidence."""
    if not (t1["coverage"]["outputs_explained"] and t2["coverage"]["outputs_explained"]):
        return "INDETERMINATE"
    if topo_signature(t1) != topo_signature(t2):
        return "DIFFERENT"
    if not (t1["coverage"]["complete"] and t2["coverage"]["complete"]):
        return "INDETERMINATE"
    return "SAME"


# ================================================================== A_TAU -- the GROUP QUOTIENT
def _canonical_order(t):
    """An isomorphism-invariant edge order: by (target ordinal, role). No position, no delay enters it."""
    return sorted(t["edges"], key=lambda e: (e["dst"], e["kind"]))


def tau_canonical(t: dict) -> tuple:
    """THE QUOTIENT. A global phase shift rotates EVERY profile and EVERY validity mask by the SAME phi0. So take
    the minimum over all phi0 of the profiles rotated TOGETHER. Invariance by symmetry, not by averaging -- and a
    RELATIVE shift between edges is not a group element, so it survives."""
    T = t["T"]
    ed = _canonical_order(t)
    if not ed:
        return ()
    profs = [e["profile"] for e in ed]
    masks = [n["valid_mask"].astype(np.int8) for n in t["nodes"] if n["resolved"] and n["targets"]]
    best = None
    for phi0 in range(T):
        cand = tuple(tuple(int(p[(k + phi0) % T]) for k in range(T)) for p in profs) + \
               tuple(tuple(int(m[(k + phi0) % T]) for k in range(T)) for m in masks)
        if best is None or cand < best:
            best = cand
    return best


def head_A_TAU(t1, t2, tol: float = 0.0) -> str:
    if head_A_TOPO(t1, t2) == "INDETERMINATE":
        return "INDETERMINATE"
    if topo_signature(t1) != topo_signature(t2):
        return "INDETERMINATE"                  # different graphs: their delays are not comparable
    c1, c2 = tau_canonical(t1), tau_canonical(t2)
    if len(c1) != len(c2):
        return "INDETERMINATE"
    for a, b in zip(c1, c2):
        if len(a) != len(b):
            return "INDETERMINATE"
        if any(abs(x - y) > tol for x, y in zip(a, b)):
            return "DIFFERENT"
    return "SAME"


# ================================================================== G -- layout. Auxiliary. Never composited.
def geom_signature(t: dict) -> tuple:
    cs = sorted(((n["box"][0] + n["box"][1]) / 2, (n["box"][2] + n["box"][3]) / 2) for n in t["nodes"])
    cg = tuple(round(cs[i + 1][1] - cs[i][1]) for i in range(len(cs) - 1))
    rg = tuple(round(cs[i + 1][0] - cs[i][0]) for i in range(len(cs) - 1))
    o = [(lo + hi) / 2 for lo, hi in t["out_nodes"]]
    og = tuple(round(o[i + 1] - o[i]) for i in range(len(o) - 1))
    return (cg, rg, og)


def head_G(t1, t2) -> str:
    return "SAME" if geom_signature(t1) == geom_signature(t2) else "DIFFERENT"


def assert_phase_invariance(toms: dict) -> dict:
    ref = toms[sorted(toms)[0]]
    bad = []
    for ph, t in sorted(toms.items()):
        if topo_signature(t) != topo_signature(ref):
            bad.append(f"A_TOPO moved at phase {ph}")
        if tau_canonical(t) != tau_canonical(ref):
            bad.append(f"A_TAU moved at phase {ph}")
        if geom_signature(t) != geom_signature(ref):
            bad.append(f"G moved at phase {ph}")
    if bad:
        raise AssertionError("PHASE INVARIANCE VIOLATED: " + "; ".join(bad))
    return {"phases_checked": sorted(toms), "verdict": "INVARIANT"}
