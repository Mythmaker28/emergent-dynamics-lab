"""Detector / phenotype / turnover for the motile polar substrate.

TWO phenotypes are frozen, and GATE-0 must pass under BOTH:
  * FULL       -- includes polar order and speed (legitimate observables of a motile polar entity)
  * BLIND      -- geometry and mass ONLY; it CANNOT see polarity at all.
The BLIND phenotype exists to answer the obvious objection that a polarity-aware phenotype makes the
scrambled-polarity null fail by construction. If intact only beats scrambled under FULL, the result is an artefact
of the observable, and GATE-0 does NOT pass.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .engine import MPState


@dataclass(frozen=True)
class MPDetectionSpec:
    threshold: float = 0.30
    min_cells: int = 12


@dataclass(frozen=True)
class MPPhenotypeSpec:
    length_scale: float = 10.0
    speed_scale: float = 0.60


@dataclass
class MPEntity:
    cells: np.ndarray
    centroid: np.ndarray
    size: int
    mass: float
    cohort_mass: np.ndarray
    polar_order: float
    phenotype_full: np.ndarray
    phenotype_blind: np.ndarray


def _components(mask: np.ndarray) -> list[np.ndarray]:
    """Connected components on a PERIODIC lattice. scipy labelling + union-find across the wrap boundaries.
    Semantically identical to the original flood fill (verified in tests/test_motile_polar.py); it is only faster."""
    from scipy import ndimage

    lab, k = ndimage.label(mask, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    if k == 0:
        return []
    parent = list(range(k + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for a, b in ((lab[0, :], lab[-1, :]), (lab[:, 0], lab[:, -1])):     # wrap edges
        m = (a > 0) & (b > 0)
        for u, v in zip(a[m], b[m]):
            union(int(u), int(v))
    roots = {}
    for c in range(1, k + 1):
        roots.setdefault(find(c), []).append(c)
    out = []
    for cs in roots.values():
        sel = np.isin(lab, cs)
        ys, xs = np.nonzero(sel)
        out.append(np.stack([ys, xs], axis=1).astype(np.int64))
    return out


def _periodic_centroid(cells: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    c = []
    for d in (0, 1):
        ang = cells[:, d] * (2 * np.pi / n)
        cm = np.average(np.cos(ang), weights=w)
        sm = np.average(np.sin(ang), weights=w)
        c.append((np.arctan2(sm, cm) % (2 * np.pi)) * n / (2 * np.pi))
    return np.asarray(c)


def detect(s: MPState, det: MPDetectionSpec, phe: MPPhenotypeSpec) -> list[MPEntity]:
    n = s.rho.shape[0]
    ents: list[MPEntity] = []
    for cells in _components(s.rho > det.threshold):
        if len(cells) < det.min_cells:
            continue
        w = s.rho[cells[:, 0], cells[:, 1]]
        cen = _periodic_centroid(cells, w, n)
        d = cells.astype(float) - cen
        d -= n * np.round(d / n)
        r = np.sqrt((d ** 2).sum(1))
        rg = float(np.sqrt(np.average(r ** 2, weights=w))) / phe.length_scale
        cov = np.cov(d.T, aweights=w)
        ev = np.linalg.eigvalsh(cov)
        aniso = float((ev[1] - ev[0]) / (ev[1] + ev[0] + 1e-12))
        q = np.percentile(r, [25, 50, 75]) / phe.length_scale
        mass = float(w.sum())
        py = s.py[cells[:, 0], cells[:, 1]]
        px = s.px[cells[:, 0], cells[:, 1]]
        mag = np.sqrt(py ** 2 + px ** 2)
        # polar ORDER = |mean p| / mean|p| : coherence, invariant to global rotation and to |p| scale
        order = float(np.hypot(np.average(py, weights=w), np.average(px, weights=w)) /
                      (np.average(mag, weights=w) + 1e-12))
        speed = float(np.average(mag, weights=w)) / phe.speed_scale
        cm = np.array([s.C[c][cells[:, 0], cells[:, 1]].sum() for c in range(s.C.shape[0])])
        blind = np.array([mass / (len(cells) + 1e-12), rg, aniso, *q])
        full = np.array([*blind, order, speed])
        ents.append(MPEntity(cells, cen, len(cells), mass, cm, order, full, blind))
    return ents


def continuity(a: np.ndarray, b: np.ndarray) -> float:
    """The FROZEN phenotype continuity kernel, unchanged: P = exp(-RMS(Phi_a - Phi_b)) in (0, 1].
    Identical formula to edlab.observables.phenotype.phenotype_similarity; applied to the raw feature vectors."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("phenotype schemas differ")
    return float(np.exp(-float(np.sqrt(np.mean((a - b) ** 2)))))


def retention(a: np.ndarray, b: np.ndarray) -> float:
    """Cohort-mass Jaccard: material retention M. Low M == genuine constituent turnover."""
    return float(np.minimum(a, b).sum() / (np.maximum(a, b).sum() + 1e-12))
