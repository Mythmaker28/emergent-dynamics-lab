"""CLEA01 — Model C, implementation 2: boolean morphology on numpy arrays.

The same frozen rule expressed with no sets and no per-cell loop. The Moore-1 dilation is nine
np.roll shifts OR-ed together; the CERTAIN rule becomes

    certain(t+1) = occ(t+1) & dilate(certain(t)) & ~dilate(occ(t) & ~certain(t))

which reads: d is occupied, at least one admissible source is certain, and no admissible source is
an occupied non-certain cell. That is exactly "every member of S(d) is in CERTAIN(t)" together with
"S(d) is non-empty". Implementation 1 arrives at the same set by enumerating S(d) explicitly.
"""
from __future__ import annotations
import json
import numpy as np

L = 36
SHIFTS = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]

def dilate(a):
    out = np.zeros_like(a)
    for dy, dx in SHIFTS:
        out |= np.roll(np.roll(a, dy, axis=0), dx, axis=1)
    return out

def load_grids(path, t_from):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0]))
    T = int(meta["steps_executed"])
    ct = z["c_t"].astype(np.int64); cy = z["c_y"].astype(np.int64)
    cx = z["c_x"].astype(np.int64); cn = z["c_nY"].astype(np.int64)
    yb = z["ybirth"]; yd = z["ydeath"]; xb = z["xbirth"]
    z.close()
    m = (ct >= t_from) & (ct < T) & (cn > 0)
    ct, cy, cx, cn = ct[m], cy[m], cx[m], cn[m]
    order = np.argsort(ct, kind="stable")
    ct, cy, cx, cn = ct[order], cy[order], cx[order], cn[order]
    bounds = {}
    if ct.size:
        cut = np.flatnonzero(np.diff(ct)) + 1
        starts = np.concatenate(([0], cut)); ends = np.concatenate((cut, [ct.size]))
        for s, e in zip(starts, ends): bounds[int(ct[s])] = (int(s), int(e))
    def led(a):
        d = {}
        for r in a:
            t = int(r[0])
            if t >= t_from: d.setdefault(t, []).append((int(r[1]), int(r[2])))
        return d
    return meta, T, (ct, cy, cx, cn, bounds), led(yb), led(yd), led(xb)

def grid_at(data, t):
    ct, cy, cx, cn, bounds = data
    sp = bounds.get(t)
    occ = np.zeros((L, L), bool); nY = np.zeros((L, L), np.int64)
    if sp is None: return occ, nY
    s, e = sp
    occ[cy[s:e], cx[s:e]] = True
    nY[cy[s:e], cx[s:e]] = cn[s:e]
    return occ, nY

def run(path, t_m, daughter_cells, horizon_cap=None):
    meta, T, data, YB, YD, XB = load_grids(path, t_m)
    cap = T if horizon_cap is None else min(T, horizon_cap)
    occ0, nY0 = grid_at(data, t_m)
    root = np.zeros((L, L), bool)
    for a, b in daughter_cells: root[int(a), int(b)] = True
    certain = root & occ0
    possible = certain.copy()
    seeded_ok = bool((certain == root).all())
    cert_end = poss_end = t_m
    cert_exposure = int(nY0[certain].sum()); poss_exposure = int(nY0[possible].sum())
    yb_c = yb_p = yd_c = yd_p = xb_c = xb_p = 0
    splits = 0; viol = 0
    prev_occ, prev_nY = occ0, nY0
    t = t_m
    while t + 1 < cap:
        occ, nY = grid_at(data, t + 1)
        if not occ.any(): break
        dil_all = dilate(prev_occ)
        dil_cert = dilate(certain)
        dil_noncert = dilate(prev_occ & ~certain)
        dil_poss = dilate(possible)
        viol += int((occ & ~dil_all).sum())
        nc = occ & dil_cert & ~dil_noncert
        npos = occ & dil_poss
        cert_src_ok = dil_cert & ~dil_noncert          # pre-state test for event attribution
        for cell in YB.get(t + 1, ()):
            if cert_src_ok[cell]: yb_c += 1
            if dil_poss[cell]: yb_p += 1
        for cell in YD.get(t + 1, ()):
            if cert_src_ok[cell]: yd_c += 1
            if dil_poss[cell]: yd_p += 1
        for cell in XB.get(t + 1, ()):
            if cert_src_ok[cell]: xb_c += 1
            if dil_poss[cell]: xb_p += 1
        certain, possible = nc, npos
        if certain.any():
            cert_end = t + 1; cert_exposure += int(nY[certain].sum())
            if _n_groups(certain) > 1: splits += 1
        if possible.any():
            poss_end = t + 1; poss_exposure += int(nY[possible].sum())
        prev_occ, prev_nY = occ, nY
        t += 1
        if not possible.any(): break
    return {"IMPL": 2, "t_m": t_m, "root_size": int(root.sum()), "root_all_occupied_at_t_m": seeded_ok,
            "CERTAIN_duration": cert_end - t_m, "CERTAIN_exposure": cert_exposure,
            "POSSIBLE_duration": poss_end - t_m, "POSSIBLE_exposure": poss_exposure,
            "certain_split_rows": splits,
            "yb_certain": yb_c, "yb_possible": yb_p,
            "yd_certain": yd_c, "yd_possible": yd_p,
            "xb_certain": xb_c, "xb_possible": xb_p,
            "n_invariant_violations": int(viol), "stopped_at": t, "horizon": T}

def _n_groups(mask):
    rem = set(zip(*np.nonzero(mask))); n = 0
    while rem:
        n += 1; stack = [rem.pop()]
        while stack:
            y, x = stack.pop()
            for dy, dx in SHIFTS:
                c = ((y + dy) % L, (x + dx) % L)
                if c in rem: rem.discard(c); stack.append(c)
    return n
