"""Separate phenotype continuity P(tau) and material retention M(tau)."""

from __future__ import annotations

from dataclasses import dataclass

from ..entities.detection import EntityObservation
from .phenotype import phenotype_similarity


@dataclass(frozen=True)
class ContinuityMeasurement:
    track_id: int
    start_step: int
    end_step: int
    start_time: float
    end_time: float
    tau: float
    phenotype_continuity: float
    material_retention: float
    start_count: int
    end_count: int


def material_retention(left_ids: frozenset[int], right_ids: frozenset[int]) -> float:
    union = left_ids | right_ids
    if not union:
        return 1.0
    return len(left_ids & right_ids) / len(union)


def measure_tracks(
    tracks: dict[int, list[EntityObservation]],
    *,
    lag_indices: tuple[int, ...] = (1, 3, 6),
) -> list[ContinuityMeasurement]:
    measurements: list[ContinuityMeasurement] = []
    for track_id, observations in sorted(tracks.items()):
        ordered = sorted(observations, key=lambda item: (item.time, item.snapshot_step))
        for lag in lag_indices:
            if lag < 1:
                raise ValueError("lag indices must be positive")
            for start_index in range(len(ordered) - lag):
                left = ordered[start_index]
                right = ordered[start_index + lag]
                measurements.append(
                    ContinuityMeasurement(
                        track_id=track_id,
                        start_step=left.snapshot_step,
                        end_step=right.snapshot_step,
                        start_time=left.time,
                        end_time=right.time,
                        tau=right.time - left.time,
                        phenotype_continuity=phenotype_similarity(
                            left.phenotype, right.phenotype
                        ),
                        material_retention=material_retention(
                            left.particle_ids, right.particle_ids
                        ),
                        start_count=len(left.particle_ids),
                        end_count=len(right.particle_ids),
                    )
                )
    return measurements
