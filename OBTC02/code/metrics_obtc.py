"""OBTC01 §6.2 — the localisation metrics, reimplemented, plus the ones CSC01 did not have.

Shared metrics are differentially verified against the CSC01 implementation in tests_obtc.py;
the new ones (lag, mobility, lifetime, fusion, fission) are checked against known-answer states.
"""
from __future__ import annotations

import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, "/home/claude/OBTC01/code")

import topology as TOP          # noqa: E402

CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


# ------------------------------------------------------------------ torus primitives
def wdist1(delta, L):
    d = np.abs(delta) % L
    return np.minimum(d, L - d)


def components(mask):
    lab, k = ndimage.label(mask, structure=CROSS)
    if k == 0:
        return -np.ones(mask.shape, np.int64), 0
    parent = list(range(k + 1))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    L = mask.shape[0]
    for i in range(L):
        if mask[0, i] and mask[L - 1, i]:
            union(lab[0, i], lab[L - 1, i])
        if mask[i, 0] and mask[i, L - 1]:
            union(lab[i, 0], lab[i, L - 1])
    roots = [find(a) for a in range(k + 1)]
    remap = {r: j for j, r in enumerate(sorted(set(roots[1:])))}
    out = -np.ones(mask.shape, np.int64)
    out[mask] = [remap[roots[v]] for v in lab[mask]]
    return out, len(remap)


def frechet_centre(f):
    """Separable exact minimiser of sum_i w_i d(i, c)^2 on the torus."""
    L = f.shape[0]
    M = float(f.sum())
    if M <= 0:
        return None, None
    i = np.arange(L)
    D2 = wdist1(i[:, None] - i[None, :], L).astype(float) ** 2
    cy = int(np.argmin(D2 @ f.sum(axis=1).astype(float)))
    cx = int(np.argmin(D2 @ f.sum(axis=0).astype(float)))
    return cy, cx


def rg_pairwise(f):
    L = f.shape[0]
    M = float(f.sum())
    if M <= 0:
        return float("nan")
    i = np.arange(L)
    D2 = wdist1(i[:, None] - i[None, :], L).astype(float) ** 2
    my = f.sum(axis=1).astype(float)
    mx = f.sum(axis=0).astype(float)
    return float(np.sqrt((my @ D2 @ my + mx @ D2 @ mx) / (2.0 * M * M)))


def dist_field(L, cy, cx):
    y = wdist1(np.arange(L) - cy, L).astype(float)
    x = wdist1(np.arange(L) - cx, L).astype(float)
    return np.sqrt(y[:, None] ** 2 + x[None, :] ** 2)


def radii(f, cy, cx, qs=(0.5, 0.8, 0.9)):
    L = f.shape[0]
    M = float(f.sum())
    if M <= 0:
        return {q: float("nan") for q in qs}
    d = dist_field(L, cy, cx).ravel()
    w = f.astype(float).ravel()
    o = np.argsort(d, kind="stable")
    d, w = d[o], w[o]
    cw = np.cumsum(w) / M
    return {q: float(d[int(np.searchsorted(cw, q, side="left"))]) for q in qs}


def geodesic_diameter(labels, cid, cap=800):
    L = labels.shape[0]
    cells = [tuple(map(int, c)) for c in np.argwhere(labels == cid)]
    n = len(cells)
    if n <= 1:
        return 0
    idx = {c: i for i, c in enumerate(cells)}

    def bfs(src):
        dist = -np.ones(n, np.int64)
        dist[idx[src]] = 0
        q, h, best = [src], 0, 0
        far = src
        while h < len(q):
            a, b = q[h]
            h += 1
            d0 = dist[idx[(a, b)]]
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = ((a + da) % L, (b + db) % L)
                j = idx.get(nb)
                if j is not None and dist[j] < 0:
                    dist[j] = d0 + 1
                    if dist[j] > best:
                        best, far = int(dist[j]), nb
                    q.append(nb)
        return far, best

    if n <= cap:
        return int(max(bfs(c)[1] for c in cells))
    a, _ = bfs(cells[0])
    return int(bfs(a)[1])


def effective_n(m):
    m = np.asarray(m, float)
    return float(m.sum() ** 2 / (m ** 2).sum()) if m.sum() > 0 else float("nan")


# ------------------------------------------------------------------ one frame
def frame(nX, nY, core_radius):
    L = nX.shape[0]
    mask = (nX + nY) > 0
    labels, k = components(mask)
    out = {"step": None, "N_X": int(nX.sum()), "N_Y": int(nY.sum()), "n_components": int(k)}
    if k == 0 or nX.sum() == 0:
        out.update({m: float("nan") for m in ("r50", "r80", "r90", "Rg", "main_mass_fraction",
                                              "n_eff_components", "core_fraction",
                                              "organiser_to_core", "geodesic_diameter",
                                              "core_free_mean")})
        out.update({"centre_y": -1, "centre_x": -1, "organiser_y": -1, "organiser_x": -1,
                    "wraps_y": False, "wraps_x": False, "any_winding": False,
                    "legacy_extent_proxy": False, "main_cid": -1, "main_N_X": 0})
        return out, labels
    masses = np.array([float((nX + nY)[labels == c].sum()) for c in range(k)])
    main = int(np.argmax(masses))
    out["main_cid"] = main
    out["main_N_X"] = int(nX[labels == main].sum())
    out["main_mass_fraction"] = float(masses[main] / masses.sum())
    out["n_eff_components"] = effective_n(masses)
    cy, cx = frechet_centre(nX)
    out["centre_y"], out["centre_x"] = cy, cx
    rq = radii(nX, cy, cx)
    out["r50"], out["r80"], out["r90"] = rq[0.5], rq[0.8], rq[0.9]
    out["Rg"] = rg_pairwise(nX)
    d = dist_field(L, cy, cx)
    out["core_fraction"] = float(nX[d <= core_radius].sum()) / float(nX.sum())
    out["geodesic_diameter"] = geodesic_diameter(labels, main)
    oy, ox = np.nonzero(nY)
    if len(oy):
        out["organiser_y"], out["organiser_x"] = int(oy[0]), int(ox[0])
        out["organiser_to_core"] = float(np.hypot(wdist1(int(oy[0]) - cy, L),
                                                  wdist1(int(ox[0]) - cx, L)))
    else:
        out["organiser_y"] = out["organiser_x"] = -1
        out["organiser_to_core"] = float("nan")
    wy, wx = TOP.winding_by_tiling(mask, labels, main)
    any_w = wy or wx
    if not any_w:
        for c in range(k):
            if c == main:
                continue
            a, b = TOP.winding_by_tiling(mask, labels, c)
            if a or b:
                any_w = True
                break
    out["wraps_y"], out["wraps_x"], out["any_winding"] = bool(wy), bool(wx), bool(any_w)
    out["legacy_extent_proxy"] = TOP.legacy_extent_proxy(nX, nY, labels == main)[
        "LEGACY_EXTENT_PROXY"]
    return out, labels


# ------------------------------------------------------------------ temporal
def unwrap(seq, L):
    a = np.asarray(seq, float)
    return np.cumsum(np.concatenate([[a[0]], ((np.diff(a) + L / 2) % L) - L / 2]))


def lagged_correlation(core, org, L, max_lag, step_of_frame):
    """Cross-correlation of the unwrapped core and organiser tracks, over lags in STEPS."""
    c = np.array(core, float)
    o = np.array(org, float)
    cy, cx = unwrap(c[:, 0], L), unwrap(c[:, 1], L)
    oy, ox = unwrap(o[:, 0], L), unwrap(o[:, 1], L)
    dt = step_of_frame
    lags = np.arange(0, int(max_lag / dt) + 1)
    best, out = None, []
    for lg in lags:
        if lg >= len(cy) - 5:
            break
        a = np.concatenate([np.diff(cy)[lg:], np.diff(cx)[lg:]])
        b = np.concatenate([np.diff(oy)[:len(np.diff(oy)) - lg],
                            np.diff(ox)[:len(np.diff(ox)) - lg]])
        n = min(len(a), len(b))
        if n < 20 or np.std(a[:n]) == 0 or np.std(b[:n]) == 0:
            continue
        r = float(np.corrcoef(a[:n], b[:n])[0, 1])
        out.append({"lag_steps": int(lg * dt), "r": r})
        if best is None or r > best["r"]:
            best = {"lag_steps": int(lg * dt), "r": r}
    return {"curve": out, "best": best,
            "zero_lag_position_correlation":
                {"y": float(np.corrcoef(cy, oy)[0, 1]) if np.std(oy) > 0 else float("nan"),
                 "x": float(np.corrcoef(cx, ox)[0, 1]) if np.std(ox) > 0 else float("nan")}}


def track_components(labels_seq, main_cids):
    """Link components between consecutive frames by cell overlap. Returns continuity of the
    main component plus fusion and fission counts."""
    n = len(labels_seq)
    prev_map, tracks, cid2tid, nxt = {}, {}, [], 0
    fusions = fissions = 0
    main_track = []
    for i in range(n):
        lab = labels_seq[i]
        k = int(lab.max()) + 1
        cur = {}
        parents = {}
        for c in range(k):
            sel = lab == c
            best, ov = None, 0
            if i > 0:
                pl = labels_seq[i - 1]
                ids, cnt = np.unique(pl[sel & (pl >= 0)], return_counts=True)
                parents[c] = set(int(v) for v in ids)
                if len(ids):
                    j = int(np.argmax(cnt))
                    best, ov = int(ids[j]), int(cnt[j])
            if best is not None and ov > 0 and best in prev_map:
                tid = prev_map[best]
            else:
                tid = nxt
                nxt += 1
                tracks[tid] = {"first": i, "n": 0}
            cur[c] = tid
            tracks[tid]["last"] = i
            tracks[tid]["n"] += 1
        if i > 0:
            fusions += sum(1 for c in parents if len(parents[c]) > 1)
            child_of = {}
            for c, ps in parents.items():
                for p in ps:
                    child_of.setdefault(p, set()).add(c)
            fissions += sum(1 for p in child_of if len(child_of[p]) > 1)
        main_track.append(cur.get(main_cids[i], -1) if k > 0 else -1)
        prev_map = cur
        cid2tid.append(cur)
    seg = main_track
    breaks = sum(1 for a, b in zip(seg, seg[1:]) if a != b)
    longest = run = 1
    for a, b in zip(seg, seg[1:]):
        run = run + 1 if a == b else 1
        longest = max(longest, run)
    vals, cnts = (np.unique(np.array(seg), return_counts=True) if seg else (np.array([]),
                                                                           np.array([])))
    return {"n_tracks": nxt, "main_track_per_frame": main_track,
            "identity_breaks": int(breaks), "longest_unbroken_frames": int(longest),
            "modal_coverage": float(cnts.max() / len(seg)) if len(seg) else float("nan"),
            "fusion_events": int(fusions), "fission_events": int(fissions),
            "main_track_lifetimes": {int(t): tracks[t]["n"] for t in set(seg) if t >= 0}}
