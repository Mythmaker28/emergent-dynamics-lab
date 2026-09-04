"""TBRT02 — the DISPLACED intervention.

CLEA01 closed because in the treated arm Model C became the ambient population: removing the parent
left the daughter as the world's only Y source, so "everything descends from the daughter" was true
by construction and explained nothing. Its terminal requires that any successor keep a competing Y
source in the treated arm.

Leaving the parent in place is not a treatment — that is SHAM. What is needed is a treatment that
removes the parent's INFLUENCE while leaving a competitor:

    SHAM        nothing                                     control
    SELECTIVE   the parent's Y removed, Y -> WY             the OMLDCT02 treatment, kept for
                                                            comparability
    DISPLACED   the parent's Y removed from its cells and
                the SAME mass placed at the toroidal
                antipode of the DAUGHTER's centroid         the new treatment

WHAT IT BUYS, and it is what every previous lineage attempt lacked: GROUND TRUTH. The competing mass
sits at a known cell at t_m, so its descendants are labelled by construction, and Model C becomes
falsifiable instead of merely self-consistent.

WHAT IT COSTS, declared rather than buried: displacement is MORE invasive than removal. Removal uses
the engine's own decay channel. Displacement is a teleport — no engine channel moves mass across the
lattice in one step. Two things bound the damage and both are checked in the fixtures: total Y mass
is conserved exactly, and no random number is consumed.

WHY THE POLE IS THE DAUGHTER'S AND NOT THE PARENT'S. TBRT01's fixtures caught this before any world
was spent and the correction is inherited here. The daughter buds from the parent, so the two are
close, so the parent's antipode is USUALLY far from the daughter — usually, not always. At L = 5 the
displaced mass landed at Chebyshev 1 from the daughter, inside its one-step reach, which would have
contaminated the lineage on the very first transition. At L = 36 the same rule would have failed
silently in the minority of layouts where the daughter sits near the parent's antipode.
"""
from __future__ import annotations
import os, sys
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("FMRCT01/code", "OMLDCT02/code", "ORR01/code", "OBTC02/code", "PQEC01/code", "TLMR01/code"):
    sys.path.insert(0, os.path.join(REPO, p))

MIN_SEPARATION_FROM_THE_DAUGHTER = 2      # strictly beyond one-step reach; not tunable


def antipode(cells, L):
    """The toroidal antipode of the anchored centroid. The anchor is the first cell in sorted order;
    offsets are wrapped to (-L/2, L/2] relative to it and averaged as exact integers before a single
    floor division, so the centroid does not depend on where the component straddles the seam."""
    cs = sorted((int(y), int(x)) for y, x in cells)
    ay, ax = cs[0]
    sy = sx = 0
    for y, x in cs:
        sy += (y - ay + L // 2) % L - L // 2
        sx += (x - ax + L // 2) % L - L // 2
    cy = (ay + sy // len(cs)) % L
    cx = (ax + sx // len(cs)) % L
    return ((cy + L // 2) % L, (cx + L // 2) % L)


def cheb(a, b, L):
    dy = min((a[0] - b[0]) % L, (b[0] - a[0]) % L)
    dx = min((a[1] - b[1]) % L, (b[1] - a[1]) % L)
    return max(dy, dx)


def choose_destination(w, parent_cells, daughter_cells, need):
    """The toroidal antipode of the DAUGHTER's centroid; if it lacks capacity, the nearest cell to
    that antipode that has it, scanned outward by Chebyshev radius then row then column. In every
    case the chosen cell must be at Chebyshev >= MIN_SEPARATION from EVERY daughter cell, so no
    admissible one-step source of any daughter cell can ever be the displaced mass. If no such cell
    exists the caller raises rather than returning a contaminating destination."""
    L = w.L
    free = np.maximum(w.free(), 0)
    ty, tx = antipode(daughter_cells, L)
    banned = {(int(y), int(x)) for y, x in parent_cells}
    dcells = [(int(y), int(x)) for y, x in daughter_cells]
    rejected_capacity = 0
    rejected_too_close = 0
    for r in range(0, L):
        ring = set()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dy), abs(dx)) == r:
                    ring.add((((ty + dy) % L), ((tx + dx) % L)))
        for c in sorted(ring):
            if c in banned:
                rejected_capacity += 1
                continue
            if min(cheb(c, d, L) for d in dcells) < MIN_SEPARATION_FROM_THE_DAUGHTER:
                rejected_too_close += 1
                continue
            if free[c] >= need:
                return c, r, rejected_capacity, rejected_too_close
            rejected_capacity += 1
    return None, None, rejected_capacity, rejected_too_close


def displace(w, cells, daughter_cells):
    """Remove the parent's Y from `cells` and place the SAME total at the chosen destination.
    Deterministic. Consumes no random number. Total Y mass conserved exactly — nothing goes to WY,
    unlike removal. Raises if capacity or separation cannot be satisfied, so a silent partial or
    contaminating displacement is impossible."""
    m = np.zeros_like(w.n["Y"], dtype=bool)
    for (y, x) in cells:
        m[int(y), int(x)] = True
    taken = np.where(m, w.n["Y"], 0)
    total = int(taken.sum())
    before = int(w.n["Y"].sum())
    if total == 0:
        return {"moved": 0, "destination": None, "Y_conserved": True,
                "reason": "the parent carried no Y at t_m"}
    dest, radius, rej_cap, rej_near = choose_destination(w, cells, daughter_cells, total)
    if dest is None:
        raise RuntimeError("no cell is both far enough from the daughter and has capacity for the "
                           "displaced mass")
    sep = min(cheb(dest, (int(y), int(x)), w.L) for y, x in daughter_cells)
    assert sep >= MIN_SEPARATION_FROM_THE_DAUGHTER, "destination inside the daughter's reach"
    w.n["Y"] = w.n["Y"] - taken
    w.n["Y"][dest] += total
    after = int(w.n["Y"].sum())
    return {"moved": total, "destination": [int(dest[0]), int(dest[1])],
            "antipode_of_the_daughter": [int(v) for v in antipode(daughter_cells, w.L)],
            "search_radius_used": radius,
            "cells_rejected_for_capacity": rej_cap,
            "cells_rejected_for_being_within_the_daughters_reach": rej_near,
            "chebyshev_to_the_nearest_daughter_cell": int(sep),
            "MIN_SEPARATION_FROM_THE_DAUGHTER": MIN_SEPARATION_FROM_THE_DAUGHTER,
            "Y_before": before, "Y_after": after, "Y_conserved": before == after,
            "source_cells": [[int(y), int(x)] for y, x in sorted(cells)],
            "daughter_cells": [[int(y), int(x)] for y, x in sorted(daughter_cells)]}


ARMS = ("SHAM", "SELECTIVE", "DISPLACED")
