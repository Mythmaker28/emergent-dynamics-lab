"""Detector + MORPHOLOGICAL identity phenotype for EXP-MA-00.

Identity features are translation- and rotation-invariant. FORBIDDEN and absent: absolute position, total mass,
absolute orientation, tracker ID. The PRIMARY phenotype is morphological only (the arrangement); the SECONDARY adds
bulk composition f_A, which a within-support permutation preserves exactly and which is therefore, by construction,
NOT organizational.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..chemotaxis.diagnostics import _label_periodic, circular_centroid
from .engine import MAState


@dataclass(frozen=True)
class MADetectionSpec:
    threshold: float = 0.30
    min_cells: int = 12


@dataclass
class MAEntity:
    cells: np.ndarray
    centroid: np.ndarray
    size: int
    rg: float
    cohort_mass: np.ndarray
    f_A: float
    phenotype: np.ndarray            # PRIMARY: morphological only
    phenotype_sec: np.ndarray        # SECONDARY: morphological + bulk composition


PRIMARY_NAMES = ("demixing_index", "n_A_domains", "janus_separation", "radial_A", "radial_B",
                 "interface_fraction", "rg_A_ratio", "rg_B_ratio")

# demixing_index = rho-weighted std of the LOCAL composition phi = A/(A+B) inside the entity.
# Threshold-free, and 0 for a perfectly mixed droplet whatever its bulk ratio f_A. A-rich sub-domains are defined by
# composition EXCESS over the entity's OWN mean f_A -- not by "A > B", which is degenerate for a mixed droplet
# (all-or-nothing depending on f_A alone, carrying no morphological information at all).


def _sub_centroid_and_rg(w: np.ndarray, cen: np.ndarray, n: int):
    tot = float(w.sum())
    if tot <= 1e-12:
        return None, 0.0, 0.0
    sc = circular_centroid(w)
    ys, xs = np.nonzero(w > 0)
    dy = ys - cen[0]; dy -= n * np.round(dy / n)
    dx = xs - cen[1]; dx -= n * np.round(dx / n)
    r = np.sqrt(dy ** 2 + dx ** 2)
    ww = w[ys, xs]
    mean_r = float(np.average(r, weights=ww))
    rg = float(np.sqrt(np.average(r ** 2, weights=ww)))
    return sc, mean_r, rg


def detect(st: MAState, det: MADetectionSpec, rho_max: float = 1.0) -> list[MAEntity]:
    n = st.A.shape[0]
    rho = st.rho
    _lbl, groups = _label_periodic(rho > det.threshold * rho_max)
    out: list[MAEntity] = []
    for sel in groups.values():
        size = int(sel.sum())
        if size < det.min_cells:
            continue
        w = rho * sel
        cen = circular_centroid(w)
        ys, xs = np.nonzero(sel)
        dy = ys - cen[0]; dy -= n * np.round(dy / n)
        dx = xs - cen[1]; dx -= n * np.round(dx / n)
        wt = rho[ys, xs]
        rg = float(np.sqrt(np.average(dy ** 2 + dx ** 2, weights=wt))) + 1e-9

        A = st.A * sel
        B = st.B * sel
        mA, mB = float(A.sum()), float(B.sum())
        f_A = mA / (mA + mB + 1e-12)

        # local composition phi = A/(A+B); demixing measured as its rho-weighted spread (threshold-free)
        phi = np.zeros_like(rho)
        np.divide(st.A, rho, out=phi, where=rho > 1e-9)
        phi_in = phi[ys, xs]
        demix = float(np.sqrt(np.average((phi_in - f_A) ** 2, weights=wt)))
        # A-rich sub-domains = composition EXCESS over the entity's OWN mean (not "A > B", which is degenerate)
        a_rich = sel & (phi > f_A)
        _l2, agroups = _label_periodic(a_rich)
        n_dom = sum(1 for g in agroups.values() if int(g.sum()) >= 3)

        scA, rA, rgA = _sub_centroid_and_rg(A, cen, n)
        scB, rB, rgB = _sub_centroid_and_rg(B, cen, n)
        if scA is None or scB is None:
            janus = 0.0
        else:
            d = scA - scB
            d -= n * np.round(d / n)
            janus = float(np.linalg.norm(d)) / rg      # rotation-invariant MAGNITUDE (no absolute orientation)

        # A/B interfacial length inside the entity, normalized by entity size
        inter = 0
        for ddy, ddx in ((0, 1), (1, 0)):
            ny, nx = (ys + ddy) % n, (xs + ddx) % n
            same = sel[ny, nx]
            flip = (phi[ys, xs] > f_A) != (phi[ny, nx] > f_A)
            inter += int((same & flip).sum())
        phen = np.array([demix, float(n_dom), janus, rA / rg, rB / rg,
                         inter / size, rgA / rg, rgB / rg], dtype=float)
        out.append(MAEntity(np.stack([ys, xs], 1), cen, size, rg,
                            np.array([float((st.C[i] * sel).sum()) for i in range(st.C.shape[0])]),
                            f_A, phen, np.concatenate([phen, [f_A]])))
    return out
