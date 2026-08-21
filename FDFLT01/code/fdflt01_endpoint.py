"""FDFLT01 — the frozen primary endpoint.

This module is the single definition of PRIMARY_SUCCESS. It is derived from the FLRS02
checker A logic with exactly two changes: the raw directory is a parameter, and persistent
centre identity is recorded as analysis bookkeeping. The scientific rule is unchanged, and
that is PROVEN mechanically by the pre-run equivalence gate, which requires this module to
reproduce the FLRS02 developmental result on the historical B1 archives exactly.

Frozen before the first fresh world. No change after any outcome is visible.
"""
from __future__ import annotations
import json, math, os
import numpy as np, yaml

REPO = "/home/claude/edl"
PROTO = yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L = int(PROTO["point"]["L"])
CORE_R = float(PROTO["analytic"]["core_radius_cells"])
MUX = float(PROTO["point"]["muX"])

# ---- the response-fraction band, recomputed, never retyped ----
F_PRIMARY = 1.0 - 1.0 / math.e
def T_of(f):  return math.log(1.0 - f) / math.log(1.0 - MUX)
FRACTIONS = {"T_50": 0.50, "T_primary": F_PRIMARY, "T_80": 0.80, "T_90": 0.90}
BAND = {k: T_of(v) for k, v in FRACTIONS.items()}
# the integer convention FLRS02 used: need_steps = int(math.ceil(T(f)))
STEPS = {k: int(math.ceil(v)) for k, v in BAND.items()}
PRIMARY_KEY = "T_primary"

_ii = np.arange(L)
_D1 = np.minimum(np.abs(_ii[:, None] - _ii[None, :]), L - np.abs(_ii[:, None] - _ii[None, :])).astype(float)

def torus_disc(cy, cx):
    iy, ix = int(round(cy)) % L, int(round(cx)) % L
    return (_D1[iy][:, None] ** 2 + _D1[ix][None, :] ** 2) <= CORE_R * CORE_R

def classify(nY, ncen, integrity_ok):
    """The frozen six-state operator (FLCR01 flcr01_science.py:81)."""
    out = []
    for i in range(len(nY)):
        if not integrity_ok: out.append("F"); continue
        if nY[i] == 0: out.append("E")
        elif ncen[i] >= 3: out.append("P")
        elif nY[i] == 1: out.append("O")
        else: out.append("S" if ncen[i] == 2 else "C")
    return out

def s_episodes(seq):
    ep, t0 = [], None
    for i, s in enumerate(seq):
        if s == "S" and t0 is None: t0 = i
        elif s != "S" and t0 is not None: ep.append((t0, i - 1)); t0 = None
    if t0 is not None: ep.append((t0, len(seq) - 1))
    return ep

def components(cells):
    """Toroidal single-linkage over Y-occupied cells, adjacency distance <= CORE_R."""
    n = len(cells)
    if n == 0: return []
    par = list(range(n))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            dy = abs(cells[i][0] - cells[j][0]); dx = abs(cells[i][1] - cells[j][1])
            dy, dx = min(dy, L - dy), min(dx, L - dx)
            if (dy * dy + dx * dx) ** 0.5 <= CORE_R:
                a, b = find(i), find(j)
                if a != b: par[a] = b
    grp = {}
    for i in range(n): grp.setdefault(find(i), []).append(i)
    return [sorted(v) for _, v in sorted(grp.items())]

def centroid(cells, idxs):
    """Toroidal centroid, anchored on the first member (the FLRS02 checker-A convention)."""
    a0 = cells[idxs[0]]
    oy = [((cells[i][0] - a0[0] + L / 2) % L) - L / 2 for i in idxs]
    ox = [((cells[i][1] - a0[1] + L / 2) % L) - L / 2 for i in idxs]
    return (a0[0] + sum(oy) / len(oy)) % L, (a0[1] + sum(ox) / len(ox)) % L

def match_persistent(prev, cur, cells_prev, cells_cur):
    """FDFLT01 §5 persistent centre identity — analysis bookkeeping only, consumes no engine RNG.

    Maximum component overlap of occupied cells; ties by minimum toroidal centroid distance;
    remaining ties by lexicographic centroid order. Returns cur_index -> prev_label or None.
    """
    setp = [set(cells_prev[i] for i in g) for g in prev]
    setc = [set(cells_cur[i] for i in g) for g in cur]
    cenp = [centroid(cells_prev, g) for g in prev]
    cenc = [centroid(cells_cur, g) for g in cur]
    cand = []
    for j, sc in enumerate(setc):
        for i, sp in enumerate(setp):
            ov = len(sc & sp)
            dy = abs(cenc[j][0] - cenp[i][0]); dy = min(dy, L - dy)
            dx = abs(cenc[j][1] - cenp[i][1]); dx = min(dx, L - dx)
            cand.append((-ov, (dy * dy + dx * dx) ** 0.5, cenc[j], j, i))
    cand.sort()
    used_p, used_c, out = set(), set(), {}
    for _ov, _d, _c, j, i in cand:
        if j in used_c or i in used_p: continue
        used_c.add(j); used_p.add(i); out[j] = i
    for j in range(len(cur)):
        out.setdefault(j, None)
    return out

def x_response(Xplane, cells, comps):
    """Frozen direct local-X response: mass within CORE_R of each centre's toroidal centroid.

    Returns (values_per_component, weaker_over_stronger_ratio). Discs may overlap; no mass is
    attributed to a centre twice within its own disc, and the ratio is scale free, so overlap
    is handled by the ratio itself rather than by an arbitrary partition. Ties: ratio 1.0.
    """
    vals = [float(Xplane[torus_disc(*centroid(cells, g))].sum()) for g in comps]
    hi = max(vals) if vals else 0.0
    return vals, ((min(vals) / hi) if hi > 0 else 0.0)

def score_world(path):
    """Return the frozen per-world record. Reads one archive; no engine is run."""
    z = np.load(path, allow_pickle=True)
    m = json.loads(str(z["meta"][0]))
    sc = z["scalars"]; nm = [str(s) for s in z["scalar_names"]]
    NY = sc[:, nm.index("N_Y")].astype(int)
    NC = sc[:, nm.index("n_centres")].astype(int)
    MPD = sc[:, nm.index("max_pair_dist")].astype(float)
    yb = z["ybirth"]
    integ = (m["stop"] != "INTEGRITY_FAILURE")
    seq = classify(NY, NC, integ)
    eps = s_episodes(seq)
    fb = int(yb[:, 0].min()) if yb.size else -1
    nb = int(yb[:, 3].sum()) if yb.size else 0
    firstS = eps[0][0] if eps else -1
    firstP = next((i for i, s in enumerate(seq) if s == "P"), -1)
    row = {"world": m["tag"], "point": m["point"], "seed": m["seed"], "split": m["split"],
           "stop": m["stop"], "kY": m["kY"], "muY": m["muY"], "steps": int(sc.shape[0]),
           "first_birth": fb, "n_births": nb, "extinct": bool(seq[-1] == "E"),
           "first_S": firstS, "first_P": firstP, "n_S_episodes": len(eps),
           "max_S_duration": max((b - a + 1 for a, b in eps), default=0),
           "integrity_ok": bool(integ),
           "median_separation_during_S": (float(np.median(MPD[NC == 2])) if (NC == 2).any() else None)}
    yc = np.asarray(z["ycells"])
    yc_by_t = {}
    need = bool(eps) and any((b - a + 1) >= min(STEPS.values()) for a, b in eps)
    if need:
        for r in yc: yc_by_t.setdefault(int(r[0]), []).append((int(r[1]), int(r[2])))
        hi = min(max(b for a, b in eps) + 1, int(sc.shape[0]) - 1)
        f0 = z["field0"][0].astype(np.int32)
        cs = np.cumsum(z["field_delta"][:hi, 0].astype(np.int32), axis=0) if hi > 0 else None
    for k, need_steps in STEPS.items():
        f_req = FRACTIONS[k]
        dur = noP = resp = False
        r0 = None; e0 = -1; p0 = None; newer_is_weaker = None
        for (a, b) in eps:
            if (b - a + 1) < need_steps: continue
            e = a + need_steps - 1
            pin = any(seq[i] == "P" for i in range(a, e + 1))
            ratio = None
            if need:
                cells = yc_by_t.get(e, [])
                comps = components(cells)
                if len(comps) == 2:
                    X = f0 if e == 0 else f0 + cs[e - 1]
                    vals, ratio = x_response(X, cells, comps)
                    # bookkeeping: which component is the newer centre
                    cprev = yc_by_t.get(a, []); pprev = components(cprev)
                    if len(pprev) >= 1:
                        mp = match_persistent(pprev, comps, cprev, cells)
                        unmatched = [j for j, v in mp.items() if v is None]
                        if len(unmatched) == 1:
                            newer_is_weaker = bool(vals[unmatched[0]] == min(vals))
            if e0 < 0: r0, e0, p0 = ratio, e, pin
            dur = True
            if not pin: noP = True
            if (ratio is not None) and (ratio >= f_req) and (not pin): resp = True
        row[f"dur_ok_{k}"] = dur; row[f"noP_ok_{k}"] = noP; row[f"resp_ok_{k}"] = resp
        row[f"event_step_{k}"] = int(e0); row[f"weak_centre_X_ratio_{k}"] = r0
        row[f"P_before_event_{k}"] = p0
        row[f"newer_centre_is_weaker_{k}"] = newer_is_weaker
        row[f"joint_timing_{k}"] = bool(nb >= 1 and dur and noP and integ)
        row[f"PRIMARY_SUCCESS_{k}"] = bool(nb >= 1 and dur and noP and resp and integ)
    row["PRIMARY_SUCCESS"] = row[f"PRIMARY_SUCCESS_{PRIMARY_KEY}"]
    z.close()
    return row
