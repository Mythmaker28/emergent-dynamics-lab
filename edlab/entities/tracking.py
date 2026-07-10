"""Geometry/phenotype tracker with explicit auditable lineage events."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..specs import TrackerSpec
from ..substrates.particle_dynamics.engine import minimum_image
from .detection import EntityObservation


@dataclass(frozen=True)
class TrackedObservation:
    track_id: int
    entity: EntityObservation


@dataclass(frozen=True)
class LineageEvent:
    kind: str
    snapshot_step: int
    time: float
    parent_track_ids: tuple[int, ...] = ()
    child_track_ids: tuple[int, ...] = ()
    detail: str = ""


@dataclass
class LineageTracker:
    spec: TrackerSpec
    box_size: float
    next_track_id: int = 0
    tracks: dict[int, list[EntityObservation]] = field(default_factory=dict)
    events: list[LineageEvent] = field(default_factory=list)
    _previous: dict[int, EntityObservation] = field(default_factory=dict)

    def _new_track(self, entity: EntityObservation) -> int:
        track_id = self.next_track_id
        self.next_track_id += 1
        self.tracks[track_id] = [entity]
        return track_id

    def update(self, entities: list[EntityObservation]) -> list[TrackedObservation]:
        if not entities:
            for track_id, previous in sorted(self._previous.items()):
                self.events.append(
                    LineageEvent(
                        "disappearance",
                        previous.snapshot_step,
                        previous.time,
                        parent_track_ids=(track_id,),
                        detail="no entity observations in current snapshot",
                    )
                )
            self._previous = {}
            return []

        step = entities[0].snapshot_step
        time = entities[0].time
        if not self._previous:
            assignments: dict[int, int] = {}
            for entity in entities:
                track_id = self._new_track(entity)
                assignments[entity.local_index] = track_id
                self.events.append(
                    LineageEvent("birth", step, time, child_track_ids=(track_id,))
                )
            self._previous = {assignments[e.local_index]: e for e in entities}
            return [TrackedObservation(assignments[e.local_index], e) for e in entities]

        candidate_scores: list[tuple[float, int, int]] = []
        by_parent: dict[int, list[int]] = {track_id: [] for track_id in self._previous}
        by_child: dict[int, list[int]] = {entity.local_index: [] for entity in entities}
        entity_by_index = {entity.local_index: entity for entity in entities}

        for track_id, previous in sorted(self._previous.items()):
            for entity in entities:
                displacement = minimum_image(entity.centroid - previous.centroid, self.box_size)
                distance = float(np.linalg.norm(displacement))
                previous_count = len(previous.particle_indices)
                current_count = len(entity.particle_indices)
                size_ratio = min(previous_count, current_count) / max(
                    previous_count, current_count
                )
                if (
                    distance <= self.spec.max_centroid_distance
                    and size_ratio >= self.spec.min_size_ratio
                ):
                    # The association function is deliberately separate from
                    # both final phenotype continuity P and ID-Jaccard M.
                    score = size_ratio * np.exp(-distance / self.spec.max_centroid_distance)
                    candidate_scores.append((float(score), track_id, entity.local_index))
                    by_parent[track_id].append(entity.local_index)
                    by_child[entity.local_index].append(track_id)

        assigned_parents: set[int] = set()
        assigned_children: set[int] = set()
        assignments = {}
        for score, track_id, local_index in sorted(
            candidate_scores,
            key=lambda item: (-item[0], item[1], item[2]),
        ):
            if track_id in assigned_parents or local_index in assigned_children:
                continue
            assignments[local_index] = track_id
            assigned_parents.add(track_id)
            assigned_children.add(local_index)
            entity = entity_by_index[local_index]
            self.tracks[track_id].append(entity)
            self.events.append(
                LineageEvent(
                    "continuity",
                    step,
                    time,
                    parent_track_ids=(track_id,),
                    child_track_ids=(track_id,),
                    detail=f"physical score={score:.6g}; IDs were not used",
                )
            )

        for entity in entities:
            if entity.local_index not in assignments:
                track_id = self._new_track(entity)
                assignments[entity.local_index] = track_id
                self.events.append(
                    LineageEvent("birth", step, time, child_track_ids=(track_id,))
                )

        for parent_track_id, child_indices in sorted(by_parent.items()):
            child_tracks = tuple(sorted({assignments[index] for index in child_indices}))
            if len(child_tracks) > 1:
                self.events.append(
                    LineageEvent(
                        "split",
                        step,
                        time,
                        parent_track_ids=(parent_track_id,),
                        child_track_ids=child_tracks,
                        detail="multiple physically compatible child entities",
                    )
                )

        ambiguous_parents = {
            parent: tuple(sorted(children))
            for parent, children in by_parent.items()
            if len(children) > 1
        }
        ambiguous_children = {
            child: tuple(sorted(parents))
            for child, parents in by_child.items()
            if len(parents) > 1
        }
        if ambiguous_parents or ambiguous_children:
            self.events.append(
                LineageEvent(
                    "ambiguous_association",
                    step,
                    time,
                    parent_track_ids=tuple(sorted(ambiguous_parents)),
                    child_track_ids=tuple(
                        sorted({assignments[index] for index in ambiguous_children})
                    ),
                    detail=(
                        f"parent alternatives={ambiguous_parents}; "
                        f"child alternatives={ambiguous_children}"
                    ),
                )
            )

        for child_index, parent_tracks in sorted(by_child.items()):
            unique_parents = tuple(sorted(set(parent_tracks)))
            if len(unique_parents) > 1:
                self.events.append(
                    LineageEvent(
                        "merge",
                        step,
                        time,
                        parent_track_ids=unique_parents,
                        child_track_ids=(assignments[child_index],),
                        detail="multiple physically compatible parent entities",
                    )
                )

        merged_parents = {track_id for parents in by_child.values() if len(parents) > 1 for track_id in parents}
        for track_id, previous in sorted(self._previous.items()):
            if track_id not in assigned_parents:
                reason = "compatible merge parent not selected" if track_id in merged_parents else "no selected physical continuation"
                self.events.append(
                    LineageEvent(
                        "disappearance",
                        step,
                        time,
                        parent_track_ids=(track_id,),
                        detail=reason,
                    )
                )

        self._previous = {assignments[e.local_index]: e for e in entities}
        return [TrackedObservation(assignments[e.local_index], e) for e in entities]
