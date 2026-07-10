"""Separate phenotype continuity P(tau) and material retention M(tau)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..entities.detection import EntityObservation
from .phenotype import phenotype_similarity

if TYPE_CHECKING:
    from ..entities.tracking import LineageEvent


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
    interval_has_ambiguity: bool
    interval_has_split_or_merge: bool
    unresolved_sparse_alias_risk: bool


def material_retention(left_ids: frozenset[int], right_ids: frozenset[int]) -> float:
    union = left_ids | right_ids
    if not union:
        return 1.0
    return len(left_ids & right_ids) / len(union)


def measure_tracks(
    tracks: dict[int, list[EntityObservation]],
    *,
    lag_indices: tuple[int, ...] = (1, 3, 6),
    events: list["LineageEvent"] | None = None,
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
                relevant_events = [
                    event
                    for event in (events or [])
                    if left.snapshot_step < event.snapshot_step <= right.snapshot_step
                    and (
                        track_id in event.parent_track_ids
                        or track_id in event.child_track_ids
                    )
                ]
                p_value = phenotype_similarity(left.phenotype, right.phenotype)
                m_value = material_retention(left.particle_ids, right.particle_ids)
                measurements.append(
                    ContinuityMeasurement(
                        track_id=track_id,
                        start_step=left.snapshot_step,
                        end_step=right.snapshot_step,
                        start_time=left.time,
                        end_time=right.time,
                        tau=right.time - left.time,
                        phenotype_continuity=p_value,
                        material_retention=m_value,
                        start_count=len(left.particle_ids),
                        end_count=len(right.particle_ids),
                        interval_has_ambiguity=any(
                            event.kind == "ambiguous_association"
                            for event in relevant_events
                        ),
                        interval_has_split_or_merge=any(
                            event.kind in {"split", "merge"}
                            for event in relevant_events
                        ),
                        unresolved_sparse_alias_risk=(p_value > 0.8 and m_value < 0.5),
                    )
                )
    return measurements
