"""Periodic proximity-component entity detector for CORE V0."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..observables.phenotype import Phenotype, compute_phenotype
from ..specs import DetectionSpec, PhenotypeSpec, WorldSpec
from ..state import ParticleState
from ..substrates.particle_dynamics.engine import minimum_image


@dataclass(frozen=True)
class EntityObservation:
    local_index: int
    snapshot_step: int
    time: float
    particle_indices: tuple[int, ...]
    particle_ids: frozenset[int]
    centroid: np.ndarray
    phenotype: Phenotype


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            self.parent[right_root] = left_root
        else:
            self.parent[left_root] = right_root


def periodic_centroid(positions: np.ndarray, box_size: float) -> np.ndarray:
    """Circular mean centroid on a square torus."""

    angles = positions * (2.0 * np.pi / box_size)
    mean_sin = np.sin(angles).mean(axis=0)
    mean_cos = np.cos(angles).mean(axis=0)
    mean_angle = np.arctan2(mean_sin, mean_cos)
    return (mean_angle % (2.0 * np.pi)) * (box_size / (2.0 * np.pi))


def connected_components_periodic(
    positions: np.ndarray,
    box_size: float,
    connection_radius: float,
) -> list[tuple[int, ...]]:
    """Connected components in a periodic proximity graph."""

    n = positions.shape[0]
    union_find = _UnionFind(n)
    for left in range(n - 1):
        displacement = minimum_image(positions[left + 1 :] - positions[left], box_size)
        distances = np.sqrt(np.sum(displacement * displacement, axis=1))
        for offset in np.flatnonzero(distances <= connection_radius):
            union_find.union(left, left + 1 + int(offset))
    groups: dict[int, list[int]] = {}
    for index in range(n):
        groups.setdefault(union_find.find(index), []).append(index)
    return [tuple(indices) for _, indices in sorted(groups.items())]


def detect_entities(
    state: ParticleState,
    *,
    snapshot_step: int,
    time: float,
    world: WorldSpec,
    detection: DetectionSpec,
    phenotype_spec: PhenotypeSpec,
) -> list[EntityObservation]:
    components = connected_components_periodic(
        state.positions,
        world.box_size,
        detection.connection_radius,
    )
    retained = [component for component in components if len(component) >= detection.min_size]
    observations: list[EntityObservation] = []
    for local_index, component in enumerate(retained):
        indices = np.asarray(component, dtype=np.int64)
        centroid = periodic_centroid(state.positions[indices], world.box_size)
        phenotype = compute_phenotype(
            state,
            indices,
            centroid=centroid,
            world=world,
            spec=phenotype_spec,
        )
        observations.append(
            EntityObservation(
                local_index=local_index,
                snapshot_step=snapshot_step,
                time=time,
                particle_indices=component,
                particle_ids=frozenset(int(value) for value in state.ids[indices]),
                centroid=centroid,
                phenotype=phenotype,
            )
        )
    return observations

