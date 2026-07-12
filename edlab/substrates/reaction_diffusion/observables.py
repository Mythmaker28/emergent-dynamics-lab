"""Field measurement stack for the open RD substrate. P = exp(-RMS dPhi) unchanged; declared scales, not tuned.

Dynamical observables are the OPEN-SYSTEM rates: production (U*V^2), removal ((F+k)*V) and activity (|dV/dt|).
A frozen/imposed pattern has ZERO activity; a genuine dissipative structure has nonzero throughput. This is what
separates a real organization from a static-flux null in an open system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ...entities.detection import EntityObservation
from ...observables.phenotype import Phenotype, phenotype_similarity
from ...substrates.particle_dynamics.engine import minimum_image
from ...substrates.flow_lenia.observables import _components_periodic, _weighted_quantiles


@dataclass(frozen=True)
class RDDetectionSpec:
    threshold: float = 0.25       # V threshold for "occupied"
    min_cells: int = 12


@dataclass(frozen=True)
class RDPhenotypeSpec:
    length_scale: float = 10.0
    rate_scale: float = 0.02      # declared rate scale (production/removal/activity)


@dataclass(frozen=True)
class RDEntity:
    local_index: int
    snapshot_step: int
    time: float
    cells: np.ndarray
    cohort_mass: np.ndarray
    centroid: np.ndarray
    phenotype: Phenotype
    size: int


def detect_rd_entities(U, V, CV, prod, rem, act, *, snapshot_step: int, time: float,
                       detection: RDDetectionSpec, phenotype_spec: RDPhenotypeSpec) -> list[RDEntity]:
    n = V.shape[0]
    total_V = float(V.sum())
    comps = [c for c in _components_periodic(V > detection.threshold) if len(c) >= detection.min_cells]
    out = []
    for li, cells in enumerate(comps):
        ys, xs = cells[:, 0], cells[:, 1]
        m = V[ys, xs]; msum = float(m.sum())
        ay = ys * (2 * np.pi / n); ax = xs * (2 * np.pi / n)
        cy = np.arctan2((m * np.sin(ay)).sum(), (m * np.cos(ay)).sum()) % (2 * np.pi) * n / (2 * np.pi)
        cx = np.arctan2((m * np.sin(ax)).sum(), (m * np.cos(ax)).sum()) % (2 * np.pi) * n / (2 * np.pi)
        centroid = np.array([cy, cx])
        rel = minimum_image(np.stack([ys, xs], 1).astype(float) - centroid, n)
        cov = (rel.T * m) @ rel / msum
        eig = np.maximum(np.linalg.eigvalsh(cov), 0.0)
        rgyr = float(np.sqrt(eig.sum())); aniso = float((eig[-1] - eig[0]) / (eig.sum() + 1e-15))
        q = _weighted_quantiles(np.sqrt((rel ** 2).sum(1)), m, [0.25, 0.5, 0.75])
        p_rate = float((m * prod[ys, xs]).sum() / msum)
        r_rate = float((m * rem[ys, xs]).sum() / msum)
        a_rate = float((m * np.abs(act[ys, xs])).sum() / msum)
        names = ("v_mass_fraction", "radius_gyration_scaled", "anisotropy", "radial_q25_scaled",
                 "radial_q50_scaled", "radial_q75_scaled", "production_scaled", "removal_scaled", "activity_scaled")
        vec = np.array([msum / max(total_V, 1e-12), rgyr / phenotype_spec.length_scale, aniso,
                        *(q / phenotype_spec.length_scale).tolist(),
                        p_rate / phenotype_spec.rate_scale, r_rate / phenotype_spec.rate_scale,
                        a_rate / phenotype_spec.rate_scale], dtype=np.float64)
        raw = {"v_mass": msum, "radius_gyration": rgyr, "anisotropy": aniso,
               "production": p_rate, "removal": r_rate, "activity": a_rate}
        cm = CV[:, ys, xs].sum(axis=1) if CV.shape[0] else np.array([])
        out.append(RDEntity(li, snapshot_step, time, cells, cm, centroid, Phenotype(names, vec, raw), len(cells)))
    return out


def to_entity_observation(e: RDEntity) -> EntityObservation:
    return EntityObservation(local_index=e.local_index, snapshot_step=e.snapshot_step, time=e.time,
                             particle_indices=tuple(range(e.size)), particle_ids=frozenset(),
                             centroid=e.centroid, phenotype=e.phenotype)


def rd_material_retention(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 1.0
    num = np.minimum(a, b).sum(); den = np.maximum(a, b).sum()
    return float(num / den) if den > 0 else 1.0


def rd_phenotype_continuity(a: Phenotype, b: Phenotype) -> float:
    return phenotype_similarity(a, b)
