"""RPP97 — the two statistics, defined once and shared by the capability test and the measurement.

Nothing here opens an archive. Keeping S1 and S2 in one place means the test that establishes
they CAN take the refuting sign and the measurement that reads them cannot drift apart.

Status: post-hoc. See RPP97/out/RPP97_STATEMENT.md, section 0.
"""
from __future__ import annotations
import os, sys
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("FDOT01/code", "PQEC01/code", "FMRT01/code"):
    sys.path.insert(0, os.path.join(REPO, p))
import fdot01_centres as CC          # byte-unchanged: the frozen component rule
import fmrt01_identity as ID         # byte-unchanged: the frozen local-X disc

assert int(ID.L) == int(CC.L) and float(ID.CORE_R) == float(CC.CORE_R), \
    "fmrt01_identity and fdot01_centres disagree on L or CORE_R"

L, CORE_R = CC.L, CC.CORE_R
DISC_AREA = int(ID.disc_mask(0, 0).sum())     # read, never assumed
LATTICE_CELLS = L * L
MIN_CELLS_FOR_S1 = 4                          # below this a core cannot be told from a rim


def centroid_frozen(a0y, a0x, soy, sox, m):
    """The frozen centroid expression in the frozen order: (a0 + sum(offsets)//m) % L."""
    return ((a0y + soy // m) % L, (a0x + sox // m) % L)


def dist2(cell, cen):
    dy = min((cell[0] - cen[0]) % L, (cen[0] - cell[0]) % L)
    dx = min((cell[1] - cen[1]) % L, (cen[1] - cell[1]) % L)
    return dy * dy + dx * dx


def S1(cells, nX, cen):
    """mean(nX | RIM) - mean(nX | CORE), split at the median toroidal distance to the centroid.
    Returns None when the component is too small for the split to mean anything."""
    if len(cells) < MIN_CELLS_FOR_S1:
        return None
    d = np.array([dist2(c, cen) for c in cells], dtype=np.float64)
    x = np.asarray(nX, dtype=np.float64)
    core = d <= float(np.median(d))
    rim = ~core
    if core.sum() == 0 or rim.sum() == 0:
        return None
    return float(x[rim].mean() - x[core].mean())


def S2(k_xd, nX_total, disc_area=None):
    """X per cell inside the frozen disc, minus X per cell in the world."""
    a = DISC_AREA if disc_area is None else disc_area
    return float(k_xd) / float(a) - float(nX_total) / float(LATTICE_CELLS)
