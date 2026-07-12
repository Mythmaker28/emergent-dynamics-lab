"""Detector / phenotype / turnover for the chemotactic substrate (frozen for EXP-CH-01 GATE-0)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .diagnostics import _label_periodic, circular_centroid
from .engine import CHState


@dataclass(frozen=True)
class CHDetectionSpec:
    threshold: float = 0.30          # x rho_max; the reference threshold of the frozen R7 band
    min_cells: int = 12


@dataclass(frozen=True)
class CHPhenotypeSpec:
    length_scale: float = 8.0
    c_scale: float = 1.0


@dataclass
class CHEntity:
    cells: np.ndarray
    centroid: np.ndarray
    size: int
    mass: float
    cohort_mass: np.ndarray
    rg: float
    phenotype: np.ndarray


def detect(st: CHState, det: CHDetectionSpec, phe: CHPhenotypeSpec, rho_max: float = 1.0) -> list[CHEntity]:
    n = st.rho.shape[0]
    _m, groups = _label_periodic(st.rho > det.threshold * rho_max)
    out: list[CHEntity] = []
    for sel in groups.values():
        if int(sel.sum()) < det.min_cells:
            continue
        w = st.rho * sel
        cen = circular_centroid(w)
        ys, xs = np.nonzero(sel)
        dy = ys - cen[0]; dy -= n * np.round(dy / n)
        dx = xs - cen[1]; dx -= n * np.round(dx / n)
        wt = st.rho[ys, xs]
        r = np.sqrt(dy ** 2 + dx ** 2)
        rg = float(np.sqrt(np.average(r ** 2, weights=wt)))
        cov = np.cov(np.stack([dy, dx]), aweights=wt)
        ev = np.linalg.eigvalsh(cov)
        aniso = float((ev[1] - ev[0]) / (ev[1] + ev[0] + 1e-12))
        q = np.percentile(r, [25, 50, 75]) / phe.length_scale
        mass = float(wt.sum())
        size = int(sel.sum())
        cm = np.array([float((st.C[i] * sel).sum()) for i in range(st.C.shape[0])])
        c_in = float(np.average(st.c[ys, xs], weights=wt)) / phe.c_scale
        phen = np.array([mass / size, rg / phe.length_scale, aniso, *q, c_in])
        out.append(CHEntity(np.stack([ys, xs], 1), cen, size, mass, cm, rg, phen))
    return out


def continuity(a: np.ndarray, b: np.ndarray) -> float:
    """FROZEN kernel, unchanged: P = exp(-RMS(Phi_a - Phi_b))."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.exp(-float(np.sqrt(np.mean((a - b) ** 2)))))


def retention(a: np.ndarray, b: np.ndarray) -> float:
    """Cohort-mass Jaccard M. Low M == genuine constituent turnover."""
    return float(np.minimum(a, b).sum() / (np.maximum(a, b).sum() + 1e-12))


def spatial_autocorr(field: np.ndarray, sup: np.ndarray) -> float:
    """Mean lag-1 spatial autocorrelation of `field` restricted to `sup` (Moran-like).
    Used to PROVE the scramble destroyed spatial structure without changing the preserved statistics."""
    ys, xs = np.nonzero(sup)
    v = field[ys, xs]
    if v.size < 3 or float(v.std()) < 1e-12:
        return 0.0
    mu, sd = float(v.mean()), float(v.std())
    n = field.shape[0]
    num = 0.0
    cnt = 0
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        ny, nx = (ys + dy) % n, (xs + dx) % n
        inside = sup[ny, nx]
        if not np.any(inside):
            continue
        a = field[ys[inside], xs[inside]] - mu
        b = field[ny[inside], nx[inside]] - mu
        num += float((a * b).sum())
        cnt += int(inside.sum())
    return num / (cnt * sd * sd) if cnt else 0.0
