"""CLEA01 — Model C, implementation 1: explicit set-based frontier propagation.

Deliberately unvectorised. Cells are Python tuples in Python sets, the toroidal Moore-1
neighbourhood is enumerated by nine explicit offsets, and every membership test is a set test.
Implementation 2 computes the same object by boolean morphology over numpy arrays; the two share
nothing but the frozen rule text and the archive.

No online component id, no online identity id, no verdict, no label, no future outcome is read.
"""
from __future__ import annotations
import json
import numpy as np

L = 36
OFFSETS = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]   # Moore-1 including self

def load_rows(path, t_from):
    """per-step occupied-cell lists and the three event ledgers, from row t_from onward."""
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0]))
    T = int(meta["steps_executed"])
    ct = z["c_t"].astype(np.int64); cy = z["c_y"].astype(np.int64)
    cx = z["c_x"].astype(np.int64); cn = z["c_nY"].astype(np.int64)
    yb = z["ybirth"]; yd = z["ydeath"]; xb = z["xbirth"]
    z.close()
    occ = {}
    m = (ct >= t_from) & (ct < T)
    for t, y, x, n in zip(ct[m].tolist(), cy[m].tolist(), cx[m].tolist(), cn[m].tolist()):
        if n > 0: occ.setdefault(t, {})[(y, x)] = n
    def led(a):
        d = {}
        for r in a:
            t = int(r[0])
            if t >= t_from: d.setdefault(t, []).append((int(r[1]), int(r[2])))
        return d
    return meta, T, occ, led(yb), led(yd), led(xb)

def sources(d, occ_prev):
    """S(d, t+1): the Y-occupied cells on row t within toroidal Chebyshev distance 1 of d."""
    y, x = d
    out = set()
    for dy, dx in OFFSETS:
        c = ((y + dy) % L, (x + dx) % L)
        if c in occ_prev: out.add(c)
    return out

def run(path, t_m, daughter_cells, horizon_cap=None):
    meta, T, occ, YB, YD, XB = load_rows(path, t_m)
    cap = T if horizon_cap is None else min(T, horizon_cap)
    root = set((int(a), int(b)) for a, b in daughter_cells)
    prev = occ.get(t_m, {})
    certain = set(c for c in root if c in prev)
    possible = set(certain)
    seeded_ok = (certain == root)
    cert_end = poss_end = t_m
    cert_steps = poss_steps = 0
    cert_exposure = sum(prev[c] for c in certain)
    poss_exposure = sum(prev[c] for c in possible)
    yb_c = yb_p = yd_c = yd_p = xb_c = xb_p = 0
    splits = 0                    # rows where CERTAIN occupies >1 spatially separate group
    invariant_violations = []
    prev_ncert = len(certain)
    t = t_m
    while t + 1 < cap:
        cur = occ.get(t + 1, {})
        if not cur: break
        nc, np_ = set(), set()
        for d in cur:
            S = sources(d, prev)
            if not S:
                invariant_violations.append({"t": t + 1, "cell": list(d)})
                continue
            if S <= certain and certain: nc.add(d)
            if S & possible: np_.add(d)
        # event attribution, judged on the pre-state only
        for cell in YB.get(t + 1, ()):
            S = sources(cell, prev)
            if S and S <= certain and certain: yb_c += 1
            if S & possible: yb_p += 1
        for cell in YD.get(t + 1, ()):
            S = sources(cell, prev)
            if S and S <= certain and certain: yd_c += 1
            if S & possible: yd_p += 1
        for cell in XB.get(t + 1, ()):
            S = sources(cell, prev)
            if S and S <= certain and certain: xb_c += 1
            if S & possible: xb_p += 1
        certain, possible = nc, np_
        if certain:
            cert_end = t + 1; cert_steps += 1
            cert_exposure += sum(cur[c] for c in certain)
            if _n_groups(certain) > 1: splits += 1
        if possible:
            poss_end = t + 1; poss_steps += 1
            poss_exposure += sum(cur[c] for c in possible)
        prev = cur
        t += 1
        if not possible: break
    return {"IMPL": 1, "t_m": t_m, "root_size": len(root), "root_all_occupied_at_t_m": seeded_ok,
            "CERTAIN_duration": cert_end - t_m, "CERTAIN_exposure": cert_exposure,
            "POSSIBLE_duration": poss_end - t_m, "POSSIBLE_exposure": poss_exposure,
            "certain_split_rows": splits,
            "yb_certain": yb_c, "yb_possible": yb_p,
            "yd_certain": yd_c, "yd_possible": yd_p,
            "xb_certain": xb_c, "xb_possible": xb_p,
            "invariant_violations": invariant_violations[:20],
            "n_invariant_violations": len(invariant_violations),
            "stopped_at": t, "horizon": T}

def _n_groups(cells):
    """number of spatially separate groups in CERTAIN, by toroidal Moore-1 flood fill. Reported
    only; it never feeds a lineage decision."""
    rem = set(cells); n = 0
    while rem:
        n += 1
        stack = [rem.pop()]
        while stack:
            y, x = stack.pop()
            for dy, dx in OFFSETS:
                c = ((y + dy) % L, (x + dx) % L)
                if c in rem: rem.discard(c); stack.append(c)
    return n
