"""Observables for MTW01. Every threshold here is fixed by code/window.py or by an exact
capacity argument; none is fitted to any output, of this mission or of any earlier one.

Two partitions of the material are computed and both are reported.

  ORGANISER DISC (primary, used by the pass criterion). Around each organiser, the disc of
  torus radius L_C = ell_X. This partition is deterministic, needs no threshold and no
  connectivity heuristic, and matches the quantity the window derivation is about: the body
  cloud that belongs to one organiser.

  CONTACT GRAPH (secondary, descriptive). Connected components of the occupied mask under
  4-connectivity WITH WRAP. On a lattice gas a single stray body molecule can bridge two
  clusters, so this partition is reported with an explicit escapee rule and is NOT used as the
  pass criterion. Stating that in advance is the point.
"""
from __future__ import annotations

import numpy as np

import guard

ESCAPEE_MAX_MASS = 2          # a component of total mass <= 2 carrying no organiser
MINORITY_MAX = 0.25           # per component, N_Y/(N_X+N_Y) must not exceed this
MIN_BODY_PER_ORGANISER = 3    # each organiser must carry at least this many body molecules


# ---------------------------------------------------------------- torus geometry
def torus_delta(a, b, L):
    d = abs(int(a) - int(b))
    return min(d, L - d)


def torus_dist(p, q, L):
    dy = torus_delta(p[0], q[0], L)
    dx = torus_delta(p[1], q[1], L)
    return float(np.hypot(dy, dx))


def organiser_positions(w):
    """One entry per organiser particle, so two organisers in the same cell give two entries."""
    ys, xs = np.nonzero(w.n["Y"] > 0)
    out = []
    for y, x in zip(ys, xs):
        out.extend([(int(y), int(x))] * int(w.n["Y"][y, x]))
    return out


def max_pair_separation(w):
    ps = organiser_positions(w)
    if len(ps) < 2:
        return 0.0
    return max(torus_dist(ps[i], ps[j], w.L)
               for i in range(len(ps)) for j in range(i + 1, len(ps)))


def disc_counts(w, centre, radius):
    L = w.L
    yy = np.arange(L)
    dy = np.minimum(np.abs(yy - centre[0]), L - np.abs(yy - centre[0]))
    dx = np.minimum(np.abs(yy - centre[1]), L - np.abs(yy - centre[1]))
    mask = (dy[:, None] ** 2 + dx[None, :] ** 2) <= radius ** 2
    return int(w.n["X"][mask].sum()), int(w.n["Y"][mask].sum()), mask


def contact_components_torus(mask):
    """4-connectivity WITH WRAP. Iterative flood fill, no recursion."""
    L = mask.shape[0]
    lab = -np.ones(mask.shape, dtype=np.int64)
    comps = []
    for y0 in range(L):
        for x0 in range(L):
            if not mask[y0, x0] or lab[y0, x0] >= 0:
                continue
            cid = len(comps)
            lab[y0, x0] = cid
            stack, cells = [(y0, x0)], []
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    na, nb = (a + da) % L, (b + db) % L
                    if mask[na, nb] and lab[na, nb] < 0:
                        lab[na, nb] = cid
                        stack.append((na, nb))
            comps.append(cells)
    return comps


def component_report(w):
    occupied = (w.n["X"] + w.n["Y"]) > 0
    comps = contact_components_torus(occupied)
    out, escapees = [], []
    for cells in comps:
        ys = np.array([c[0] for c in cells])
        xs = np.array([c[1] for c in cells])
        nx = int(w.n["X"][ys, xs].sum())
        ny = int(w.n["Y"][ys, xs].sum())
        rec = {"cells": len(cells), "N_X": nx, "N_Y": ny,
               "minority_fraction": (ny / (nx + ny)) if (nx + ny) else None}
        if ny == 0 and (nx + ny) <= ESCAPEE_MAX_MASS:
            escapees.append(rec)
        else:
            out.append(rec)
    return {"components": out, "escapees": escapees,
            "n_components_excluding_escapees": len(out), "n_escapees": len(escapees),
            "n_components_raw": len(comps)}


# ---------------------------------------------------------------- gates
def gate_X(w, L_C, N_X_MIN, RG_MAX_ELL, FILL_MAX_FRAC, Q_FLOOR, q_mean):
    """The body-cloud gate, evaluated once, at t = T_X. All six conditions must hold."""
    guard.assert_not_test_mode("gate_X")
    NX, NY = int(w.n["X"].sum()), int(w.n["Y"].sum())
    occupied = (w.n["X"] + w.n["Y"]) > 0
    support = int(occupied.sum())
    ps = organiser_positions(w)
    rg = None
    if ps and NX > 0:
        # radius of gyration of the body cloud about the organiser (or, at the instant the
        # second one appears, about the pair) measured with wrapped distances
        cy = float(np.mean([p[0] for p in ps]))
        cx = float(np.mean([p[1] for p in ps]))
        c = (int(round(cy)) % w.L, int(round(cx)) % w.L)
        ys, xs = np.nonzero(w.n["X"] > 0)
        wts = w.n["X"][ys, xs].astype(float)
        d2 = np.array([torus_dist((y, x), c, w.L) ** 2 for y, x in zip(ys, xs)])
        rg = float(np.sqrt((d2 * wts).sum() / wts.sum()))
    checks = {
        # the gate is evaluated at min(T_X, t_2). At t_2 the second organiser is already
        # present, so one OR two are legal there; three, or none, are not.
        "organiser_count_one_or_two": 1 <= NY <= 2,
        "body_cloud_present": NX >= N_X_MIN,
        "cloud_colocated_with_organiser": rg is not None and rg <= RG_MAX_ELL * L_C,
        "does_not_fill_torus": support <= FILL_MAX_FRAC * w.L * w.L,
        "core_strength_sufficient": q_mean >= Q_FLOOR,
    }
    return {"N_X": NX, "N_Y": NY, "support_cells": support, "Rg_X_about_organiser": rg,
            "Q_mean_over_window": q_mean, "checks": checks,
            "PASS": bool(all(checks.values()))}


def realised_Q(w):
    """Q = nX * c_Y summed over organiser-carrying cells, the ONLY state-dependent factor in
    the per-organiser replication rate R_Y = k_Y * Q. Read directly off the engine state with
    the engine's own candidate rule."""
    free = np.maximum(w.free(), 0)
    c_Y = np.minimum(w.n["SY"], free)
    m = w.n["Y"] > 0
    return float((w.n["X"][m] * c_Y[m]).sum())


def arm_verdict(rec, L_C, Delta_sep):
    """The pass criterion. Primary partition only; the contact graph is descriptive."""
    guard.assert_not_test_mode("arm_verdict")
    if rec["outcome"] != "SEPARATED":
        return False, rec["outcome"]
    fails = []
    for i, d in enumerate(rec["discs_at_separation"]):
        if d["N_Y"] != 1:
            fails.append("disc%d_organiser_count_%d" % (i, d["N_Y"]))
        if d["N_X"] < MIN_BODY_PER_ORGANISER:
            fails.append("disc%d_body_%d_below_%d" % (i, d["N_X"], MIN_BODY_PER_ORGANISER))
        mf = d["N_Y"] / max(d["N_X"] + d["N_Y"], 1)
        if mf > MINORITY_MAX:
            fails.append("disc%d_minority_%.3f_above_%.2f" % (i, mf, MINORITY_MAX))
    if rec["N_Y_at_separation"] != 2:
        fails.append("organiser_count_%d" % rec["N_Y_at_separation"])
    return (len(fails) == 0), ("PASS" if not fails else "FAIL:" + ";".join(fails))
