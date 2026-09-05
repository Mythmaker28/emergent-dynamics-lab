"""Detector (scaffold only), INTERNAL-organization identity phenotype, and the behavioural uptake observable."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..chemotaxis.diagnostics import _label_periodic, circular_centroid
from .engine import SCState, EPS


@dataclass(frozen=True)
class SCDetectionSpec:
    threshold: float = 0.30      # on the SCAFFOLD rho ONLY. The internal fields cannot manufacture an entity (O3).
    min_cells: int = 12


PRIMARY_NAMES = ("internal_heterogeneity", "n_u_domains", "interface_fraction", "radial_u", "janus_sig")
SECONDARY_NAMES = PRIMARY_NAMES + ("mean_sig",)


@dataclass
class SCEntity:
    cells: np.ndarray
    centroid: np.ndarray
    size: int
    mass: float
    rg: float
    cohort_mass: np.ndarray
    mean_sig: float
    specific_uptake: float                # BEHAVIOUR: nutrient consumed per unit mass, last step
    phenotype: np.ndarray                 # PRIMARY: internal spatial organization only
    phenotype_sec: np.ndarray             # SECONDARY: + bulk internal state


def detect(st: SCState, det: SCDetectionSpec, rho_max: float = 1.0) -> list[SCEntity]:
    n = st.rho.shape[0]
    _l, groups = _label_periodic(st.rho > det.threshold * rho_max)
    sig = st.sigma()
    out: list[SCEntity] = []
    for sel in groups.values():
        size = int(sel.sum())
        if size < det.min_cells:
            continue
        ys, xs = np.nonzero(sel)
        w = st.rho[ys, xs]
        cen = circular_centroid(st.rho * sel)
        dy = ys - cen[0]; dy -= n * np.round(dy / n)
        dx = xs - cen[1]; dx -= n * np.round(dx / n)
        rg = float(np.sqrt(np.average(dy ** 2 + dx ** 2, weights=w))) + 1e-9
        sg = sig[ys, xs]
        mean_sig = float(np.average(sg, weights=w))
        het = float(np.sqrt(np.average((sg - mean_sig) ** 2, weights=w)))   # threshold-free; 0 if interior uniform

        # NUMERICAL tolerance, not a tuned threshold: sigma lives in [-1, 1], so 1e-6 is float noise. Without it a
        # PERFECTLY UNIFORM interior reports a spurious domain from +-2e-16 jitter around its own mean.
        SIG_EPS = 1e-6
        u_rich = sel & (sig > mean_sig + SIG_EPS)
        _l2, ug = _label_periodic(u_rich)
        n_dom = sum(1 for g in ug.values() if int(g.sum()) >= 3)

        inter = 0
        for ddy, ddx in ((0, 1), (1, 0)):
            ny, nx = (ys + ddy) % n, (xs + ddx) % n
            inter += int((sel[ny, nx] & ((sig[ys, xs] > mean_sig + SIG_EPS)
                                        != (sig[ny, nx] > mean_sig + SIG_EPS))).sum())

        wu = np.maximum(sg - mean_sig, 0.0) * w
        wv = np.maximum(mean_sig - sg, 0.0) * w
        r = np.sqrt(dy ** 2 + dx ** 2)
        radial_u = float(np.average(r, weights=wu) / rg) if wu.sum() > 1e-12 else 0.0
        if wu.sum() > 1e-12 and wv.sum() > 1e-12:
            cu = np.array([np.average(dy, weights=wu), np.average(dx, weights=wu)])
            cv = np.array([np.average(dy, weights=wv), np.average(dx, weights=wv)])
            janus = float(np.linalg.norm(cu - cv) / rg)      # rotation-invariant MAGNITUDE
        else:
            janus = 0.0
        mass = float(w.sum())
        upt = float(st.uptake[ys, xs].sum() / (mass + EPS))   # BEHAVIOUR: specific uptake
        phen = np.array([het, float(n_dom), inter / size, radial_u, janus])
        out.append(SCEntity(np.stack([ys, xs], 1), cen, size, mass, rg,
                            np.array([float((st.C[i] * sel).sum()) for i in range(st.C.shape[0])]),
                            mean_sig, upt, phen, np.concatenate([phen, [mean_sig]])))
    return out
