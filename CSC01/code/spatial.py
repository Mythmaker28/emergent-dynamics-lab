"""CSC01 — exact toroidal geometry.

Every observable here is defined so that it is correct on a torus in ALL circumstances,
including when the mass wraps or is multimodal. Where ORR01 used a definition that is only
correct when the component does not wrap (the angular-mean centre, and the radius of gyration
taken about it), that definition is recomputed here as well and reported side by side, so that
the difference between the two is a measurement rather than an assertion.

SEPARABILITY. The squared toroidal distance is d(a,b)^2 = dy^2 + dx^2 with
dy = min(|Δy|, L-|Δy|). Both the Frechet centre and the pairwise radius of gyration are
therefore separable into their y and x marginals, which makes them exact and O(L^2) instead of
O(L^4).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

NEI = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ------------------------------------------------------------------ distances
def wrapped_abs(delta, L):
    d = np.abs(delta) % L
    return np.minimum(d, L - d)


def dist2_matrix(L):
    """(L, L) matrix of squared 1-D wrapped distances between index pairs."""
    i = np.arange(L)
    return wrapped_abs(i[:, None] - i[None, :], L).astype(np.float64) ** 2


# ------------------------------------------------------------------ components on a torus
def torus_components(mask):
    """4-connected components with periodic boundaries.

    Returns (labels, sizes) with labels in 0..k-1 on occupied cells and -1 elsewhere.
    scipy labels the array non-periodically; the wrap edges are then merged by union-find.
    """
    lab, k = ndimage.label(mask, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    if k == 0:
        return -np.ones(mask.shape, dtype=np.int64), np.zeros(0, dtype=np.int64)
    parent = np.arange(k + 1)

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
    for i in range(L):                                   # top row against bottom row
        if mask[0, i] and mask[L - 1, i]:
            union(lab[0, i], lab[L - 1, i])
        if mask[i, 0] and mask[i, L - 1]:
            union(lab[i, 0], lab[i, L - 1])
    roots = np.array([find(a) for a in range(k + 1)])
    uniq = {r: j for j, r in enumerate(sorted(set(roots[1:].tolist())))}
    out = -np.ones(mask.shape, dtype=np.int64)
    m = mask
    out[m] = np.array([uniq[roots[v]] for v in lab[m]], dtype=np.int64)
    sizes = np.bincount(out[m], minlength=len(uniq)).astype(np.int64)
    return out, sizes


# ------------------------------------------------------------------ centre and spread
def frechet_centre(field):
    """The lattice site minimising sum_i w_i d(i, c)^2. Exact, separable, O(L^2).

    Defined for any mass distribution on the torus, wrapped or multimodal. Returns
    (cy, cx, inertia) with inertia the minimised value divided by the total mass.
    """
    L = field.shape[0]
    M = float(field.sum())
    if M <= 0:
        return None, None, float("nan")
    my = field.sum(axis=1).astype(np.float64)
    mx = field.sum(axis=0).astype(np.float64)
    D2 = dist2_matrix(L)
    cost_y = D2 @ my                                     # cost_y[c] = sum_y my[y] d(y,c)^2
    cost_x = D2 @ mx
    cy = int(np.argmin(cost_y))
    cx = int(np.argmin(cost_x))
    return cy, cx, float((cost_y[cy] + cost_x[cx]) / M)


def rg_pairwise(field):
    """Radius of gyration in the centre-free pairwise form,
       Rg^2 = (1 / 2M^2) sum_ij w_i w_j d(i,j)^2.  Exact on a torus, separable."""
    L = field.shape[0]
    M = float(field.sum())
    if M <= 0:
        return float("nan")
    my = field.sum(axis=1).astype(np.float64)
    mx = field.sum(axis=0).astype(np.float64)
    D2 = dist2_matrix(L)
    s = float(my @ D2 @ my) + float(mx @ D2 @ mx)
    return float(np.sqrt(s / (2.0 * M * M)))


def dist_field(L, cy, cx):
    y = wrapped_abs(np.arange(L) - cy, L).astype(np.float64)
    x = wrapped_abs(np.arange(L) - cx, L).astype(np.float64)
    return np.sqrt(y[:, None] ** 2 + x[None, :] ** 2)


def radii_quantiles(field, cy, cx, qs=(0.5, 0.8, 0.9)):
    """Weighted quantiles of the toroidal distance to (cy, cx), over the mass in `field`."""
    L = field.shape[0]
    M = float(field.sum())
    if M <= 0:
        return {q: float("nan") for q in qs}
    d = dist_field(L, cy, cx).ravel()
    w = field.astype(np.float64).ravel()
    o = np.argsort(d, kind="stable")
    d, w = d[o], w[o]
    cw = np.cumsum(w) / M
    return {q: float(d[int(np.searchsorted(cw, q, side="left"))]) for q in qs}


def mass_within(field, cy, cx, R):
    L = field.shape[0]
    d = dist_field(L, cy, cx)
    return float(field[d <= R].sum())


# ------------------------------------------------------------------ winding, percolation
def winding_vectors(mask, labels, cid):
    """Lift the component into the universal cover by BFS. Whenever a cell is reached with a
    lift different from the one already assigned, the difference is L times a winding vector.
    Returns (wrap_y, wrap_x, vectors)."""
    L = mask.shape[0]
    cells = np.argwhere(labels == cid)
    if len(cells) == 0:
        return False, False, []
    start = tuple(int(v) for v in cells[0])
    lift = {start: (start[0], start[1])}
    stack = [start]
    vecs = set()
    while stack:
        a, b = stack.pop()
        la, lb = lift[(a, b)]
        for da, db in NEI:
            na, nb = (a + da) % L, (b + db) % L
            if labels[na, nb] != cid:
                continue
            cand = (la + da, lb + db)
            if (na, nb) not in lift:
                lift[(na, nb)] = cand
                stack.append((na, nb))
            else:
                ha, hb = lift[(na, nb)]
                dy, dx = cand[0] - ha, cand[1] - hb
                if dy or dx:
                    vecs.add((dy // L, dx // L))
    wy = any(v[0] != 0 for v in vecs)
    wx = any(v[1] != 0 for v in vecs)
    return bool(wy), bool(wx), sorted(vecs)


def geodesic_diameter(labels, cid, cap=600):
    """Longest shortest path inside the component, with periodic adjacency.
    Exhaustive if the component has at most `cap` cells; otherwise a double sweep, flagged."""
    L = labels.shape[0]
    cells = [tuple(int(v) for v in c) for c in np.argwhere(labels == cid)]
    n = len(cells)
    if n <= 1:
        return 0, True
    idx = {c: i for i, c in enumerate(cells)}

    def bfs(src):
        dist = -np.ones(n, dtype=np.int64)
        dist[idx[src]] = 0
        q = [src]
        head = 0
        far, fd = src, 0
        while head < len(q):
            a, b = q[head]
            head += 1
            d0 = dist[idx[(a, b)]]
            for da, db in NEI:
                nb_ = ((a + da) % L, (b + db) % L)
                j = idx.get(nb_)
                if j is not None and dist[j] < 0:
                    dist[j] = d0 + 1
                    if dist[j] > fd:
                        far, fd = nb_, int(dist[j])
                    q.append(nb_)
        return far, fd

    if n <= cap:
        return int(max(bfs(c)[1] for c in cells)), True
    a, _ = bfs(cells[0])
    _, d = bfs(a)
    return int(d), False


# ------------------------------------------------------------------ the full frame record
def effective_n(masses):
    m = np.asarray(masses, dtype=np.float64)
    if m.sum() <= 0:
        return float("nan")
    return float((m.sum() ** 2) / (m ** 2).sum())


def angular_centre(idx, wts, L):
    """The ORR01 definition, reproduced for comparison only."""
    th = 2.0 * np.pi * idx / L
    c = float((wts * np.cos(th)).sum())
    s = float((wts * np.sin(th)).sum())
    return (np.arctan2(s, c) % (2.0 * np.pi)) * L / (2.0 * np.pi)


def frame_report(nX, nY, ell_X, occ=None, cap=None, comp_cap=600):
    """Every spatial observable of §1 of the autopsy pre-plan, at one instant."""
    L = nX.shape[0]
    mask = (nX + nY) > 0
    labels, sizes = torus_components(mask)
    k = len(sizes)
    out = {"L": L, "N_X": int(nX.sum()), "N_Y": int(nY.sum()), "n_components_raw": int(k)}

    massw = nX + nY
    comp = []
    for cid in range(k):
        sel = labels == cid
        m = float(massw[sel].sum())
        comp.append({"id": cid, "cells": int(sel.sum()), "N_X": int(nX[sel].sum()),
                     "N_Y": int(nY[sel].sum()), "mass": m})
    comp.sort(key=lambda r: -r["mass"])
    masses = [c["mass"] for c in comp]
    total = float(sum(masses)) if masses else 0.0
    out["main_mass_fraction"] = (masses[0] / total) if total > 0 else float("nan")
    out["n_eff_components"] = effective_n(masses) if masses else float("nan")
    out["n_components"] = int(k)
    out["n_singletons"] = int(sum(1 for c in comp if c["mass"] <= 1))
    out["main_N_X"] = comp[0]["N_X"] if comp else 0
    out["main_cells"] = comp[0]["cells"] if comp else 0
    out["main_cid"] = int(comp[0]["id"]) if comp else -1

    # --- geometry of the X mass as a whole, centre-free where possible
    if nX.sum() > 0:
        cy, cx, inertia = frechet_centre(nX)
        out["centre_y"], out["centre_x"] = cy, cx
        out["inertia_per_mass"] = inertia
        rq = radii_quantiles(nX, cy, cx)
        out["r50"], out["r80"], out["r90"] = rq[0.5], rq[0.8], rq[0.9]
        out["Rg_pairwise"] = rg_pairwise(nX)
        ys, xs = np.nonzero(nX)
        w = nX[ys, xs].astype(np.float64)
        acy, acx = angular_centre(ys, w, L), angular_centre(xs, w, L)
        out["angular_centre_y"], out["angular_centre_x"] = acy, acx
        dy = wrapped_abs(ys - acy, L)
        dx = wrapped_abs(xs - acx, L)
        out["Rg_ORR01_angular"] = float(np.sqrt(((dy ** 2 + dx ** 2) * w).sum() / w.sum()))
        out["core_mass_within_2ellX"] = mass_within(nX, cy, cx, 2.0 * ell_X)
        out["core_fraction_within_2ellX"] = out["core_mass_within_2ellX"] / float(nX.sum())
        out["mass_within_r50"] = mass_within(nX, cy, cx, rq[0.5]) / float(nX.sum())
    else:
        for key in ("centre_y", "centre_x", "inertia_per_mass", "r50", "r80", "r90",
                    "Rg_pairwise", "angular_centre_y", "angular_centre_x", "Rg_ORR01_angular",
                    "core_mass_within_2ellX", "core_fraction_within_2ellX", "mass_within_r50"):
            out[key] = float("nan")

    # --- organiser
    oy, ox = np.nonzero(nY)
    if len(oy):
        out["n_organiser_cells"] = int(len(oy))
        out["organiser_y"], out["organiser_x"] = int(oy[0]), int(ox[0])
        if out.get("centre_y") is not None and not isinstance(out["centre_y"], float):
            dy = wrapped_abs(np.array([out["organiser_y"] - out["centre_y"]]), L)[0]
            dx = wrapped_abs(np.array([out["organiser_x"] - out["centre_x"]]), L)[0]
            out["organiser_to_centre"] = float(np.hypot(dy, dx))
        else:
            out["organiser_to_centre"] = float("nan")
    else:
        out["n_organiser_cells"] = 0
        out["organiser_y"] = out["organiser_x"] = -1
        out["organiser_to_centre"] = float("nan")

    # --- winding, percolation and geodesic diameter of the main component
    if k:
        main_cid = int(comp[0]["id"])
        wy, wx, vecs = winding_vectors(mask, labels, main_cid)
        out["main_wraps_y"], out["main_wraps_x"] = wy, wx
        out["main_winding_vectors"] = [list(v) for v in vecs]
        gd, exact = geodesic_diameter(labels, main_cid, cap=comp_cap)
        out["main_geodesic_diameter"] = gd
        out["main_geodesic_exact"] = exact
        out["any_component_wraps"] = bool(wy or wx)
        if not out["any_component_wraps"]:
            for c in comp[1:]:
                a, b, _ = winding_vectors(mask, labels, int(c["id"]))
                if a or b:
                    out["any_component_wraps"] = True
                    break
    else:
        out["main_wraps_y"] = out["main_wraps_x"] = False
        out["main_winding_vectors"] = []
        out["main_geodesic_diameter"] = 0
        out["main_geodesic_exact"] = True
        out["any_component_wraps"] = False

    if occ is not None and cap is not None:
        out["free_total"] = int(np.maximum(cap - occ, 0).sum())
        out["cells_at_capacity"] = int((occ >= cap).sum())
    out["_labels"] = labels
    out["_comp"] = comp
    return out
