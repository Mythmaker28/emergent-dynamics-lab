"""Field-native measurement stack for Flow-Lenia, preserving the frozen phenotype/P philosophy.

Detector: threshold the mass field and take periodic connected components. Phenotype: ID-independent geometric +
dynamical descriptors from the mass field (geometry) and the flow field (velocity), with P = exp(-RMS(dPhi)) --
the SAME formula as CORE V0; only the descriptor scales are declared, not recalibrated to results. Association
reuses the frozen geometry/size LineageTracker. Material retention M(tau) is a passive-cohort mass Jaccard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ...observables.phenotype import Phenotype, phenotype_similarity
from ...entities.detection import EntityObservation
from ...substrates.particle_dynamics.engine import minimum_image


@dataclass(frozen=True)
class FieldPhenotypeSpec:
    length_scale: float = 10.0     # cells (kernel-radius order); declared, not tuned to results
    speed_scale: float = 1.0       # flow units


@dataclass(frozen=True)
class FieldDetectionSpec:
    threshold: float = 0.15        # absolute mass threshold for "occupied" cells
    min_cells: int = 12


def _components_periodic(mask: np.ndarray) -> list[np.ndarray]:
    """Periodic connected components (4-neighbour) of a boolean grid; returns list of (row,col) index arrays."""
    h, w = mask.shape
    label = -np.ones((h, w), dtype=np.int64)
    comps: list[list[tuple[int, int]]] = []
    for i in range(h):
        for j in range(w):
            if not mask[i, j] or label[i, j] >= 0:
                continue
            cid = len(comps); comps.append([]); stack = [(i, j)]; label[i, j] = cid
            while stack:
                y, x = stack.pop(); comps[cid].append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = (y + dy) % h, (x + dx) % w
                    if mask[ny, nx] and label[ny, nx] < 0:
                        label[ny, nx] = cid; stack.append((ny, nx))
    return [np.array(c, dtype=np.int64) for c in comps]


def _field_phenotype(A: np.ndarray, F: np.ndarray, cells: np.ndarray, spec: FieldPhenotypeSpec,
                     size: int, total_mass: float) -> tuple[Phenotype, np.ndarray]:
    ys, xs = cells[:, 0], cells[:, 1]
    m = A[ys, xs]
    msum = float(m.sum())
    # periodic mass-weighted centroid via circular mean
    ang_y = ys * (2 * np.pi / size); ang_x = xs * (2 * np.pi / size)
    cy = np.arctan2((m * np.sin(ang_y)).sum(), (m * np.cos(ang_y)).sum()) % (2 * np.pi) * size / (2 * np.pi)
    cx = np.arctan2((m * np.sin(ang_x)).sum(), (m * np.cos(ang_x)).sum()) % (2 * np.pi) * size / (2 * np.pi)
    centroid = np.array([cy, cx])
    rel = minimum_image(np.stack([ys, xs], axis=1).astype(float) - centroid, size)
    cov = (rel.T * m) @ rel / msum
    eig = np.maximum(np.linalg.eigvalsh(cov), 0.0)
    rgyr = float(np.sqrt(eig.sum()))
    aniso = float((eig[-1] - eig[0]) / (eig.sum() + 1e-15))
    radii = np.sqrt((rel ** 2).sum(axis=1))
    q = _weighted_quantiles(radii, m, [0.25, 0.5, 0.75])
    vel = F[:, ys, xs].T            # (ncells,2) flow (vy,vx) but stack as (y,x)
    vel = np.stack([F[0, ys, xs], F[1, ys, xs]], axis=1)
    cvel = (vel * m[:, None]).sum(0) / msum
    relvel = vel - cvel
    vdisp = float(np.sqrt((m * (relvel ** 2).sum(1)).sum() / msum))
    circ = float((m * (rel[:, 0] * relvel[:, 1] - rel[:, 1] * relvel[:, 0])).sum() / msum
                 / (spec.length_scale * spec.speed_scale))
    names = ("mass_fraction", "radius_gyration_scaled", "anisotropy", "radial_q25_scaled", "radial_q50_scaled",
             "radial_q75_scaled", "center_velocity_y_scaled", "center_velocity_x_scaled",
             "velocity_dispersion_scaled", "internal_circulation_scaled")
    vector = np.array([msum / total_mass, rgyr / spec.length_scale, aniso,
                       *(q / spec.length_scale).tolist(),
                       cvel[0] / spec.speed_scale, cvel[1] / spec.speed_scale,
                       vdisp / spec.speed_scale, circ], dtype=np.float64)
    raw = {"mass": msum, "radius_gyration": rgyr, "anisotropy": aniso,
           "center_velocity": cvel.tolist(), "velocity_dispersion": vdisp, "internal_circulation": circ}
    return Phenotype(names, vector, raw), centroid


def _weighted_quantiles(values: np.ndarray, weights: np.ndarray, qs: list[float]) -> np.ndarray:
    order = np.argsort(values); v = values[order]; w = weights[order]
    cw = np.cumsum(w) - 0.5 * w
    cw /= w.sum()
    return np.interp(qs, cw, v)


@dataclass(frozen=True)
class FieldEntity:
    local_index: int
    snapshot_step: int
    time: float
    cells: np.ndarray               # (ncells,2) row,col
    cohort_mass: np.ndarray         # (C,) mass of each cohort inside the entity
    centroid: np.ndarray
    phenotype: Phenotype
    size: int


def detect_field_entities(A: np.ndarray, F: np.ndarray, cohorts: np.ndarray, *, snapshot_step: int, time: float,
                          detection: FieldDetectionSpec, phenotype_spec: FieldPhenotypeSpec) -> list[FieldEntity]:
    size = A.shape[0]; total_mass = float(A.sum())
    comps = [c for c in _components_periodic(A > detection.threshold) if len(c) >= detection.min_cells]
    out: list[FieldEntity] = []
    for li, cells in enumerate(comps):
        ys, xs = cells[:, 0], cells[:, 1]
        cohort_mass = cohorts[:, ys, xs].sum(axis=1) if cohorts.shape[0] else np.array([])
        phen, centroid = _field_phenotype(A, F, cells, phenotype_spec, size, total_mass)
        out.append(FieldEntity(li, snapshot_step, time, cells, cohort_mass, centroid, phen, len(cells)))
    return out


def to_entity_observation(fe: FieldEntity) -> EntityObservation:
    """Adapter so the frozen geometry/size LineageTracker can associate field entities (IDs unused)."""
    return EntityObservation(local_index=fe.local_index, snapshot_step=fe.snapshot_step, time=fe.time,
                             particle_indices=tuple(range(fe.size)), particle_ids=frozenset(),
                             centroid=fe.centroid, phenotype=fe.phenotype)


def field_material_retention(cohort_mass_a: np.ndarray, cohort_mass_b: np.ndarray) -> float:
    """Passive-cohort mass Jaccard: sum_c min / sum_c max. 1 = same origin composition, ->0 = full turnover."""
    if cohort_mass_a.size == 0 or cohort_mass_b.size == 0:
        return 1.0
    num = np.minimum(cohort_mass_a, cohort_mass_b).sum()
    den = np.maximum(cohort_mass_a, cohort_mass_b).sum()
    return float(num / den) if den > 0 else 1.0


def phenotype_continuity(a: Phenotype, b: Phenotype) -> float:
    return phenotype_similarity(a, b)   # frozen P formula, unchanged
