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
class AssociationEdge:
    snapshot_step: int
    time: float
    parent_track_id: int
    child_local_index: int
    centroid_distance: float
    size_ratio: float
    distance_gate_passed: bool
    size_gate_passed: bool
    score: float
    selected: bool
    classification: str


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
    association_edges: list[AssociationEdge] = field(default_factory=list)
    _previous: dict[int, EntityObservation] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.box_size <= 0 or not np.isfinite(self.box_size):
            raise ValueError("box_size must be finite and positive")
        if self.spec.max_centroid_distance >= self.box_size / 2.0:
            raise ValueError(
                "max_centroid_distance must be strictly below box_size/2"
            )

    def _new_track(self, entity: EntityObservation) -> int:
        track_id = self.next_track_id
        self.next_track_id += 1
        self.tracks[track_id] = [entity]
        return track_id

    def update(
        self,
        entities: list[EntityObservation],
        *,
        snapshot_step: int | None = None,
        time: float | None = None,
    ) -> list[TrackedObservation]:
        if not entities:
            if self._previous and (snapshot_step is None or time is None):
                raise ValueError(
                    "empty snapshots require explicit snapshot_step and time for auditable disappearances"
                )
            for track_id, previous in sorted(self._previous.items()):
                self.events.append(
                    LineageEvent(
                        "disappearance",
                        int(snapshot_step),
                        float(time),
                        parent_track_ids=(track_id,),
                        detail="no entity observations in current snapshot",
                    )
                )
            self._previous = {}
            return []

        step = entities[0].snapshot_step if snapshot_step is None else snapshot_step
        event_time = entities[0].time if time is None else time
        if any(entity.snapshot_step != step or entity.time != event_time for entity in entities):
            raise ValueError("all entities must match the update snapshot step and time")
        if not self._previous:
            assignments: dict[int, int] = {}
            for entity in entities:
                track_id = self._new_track(entity)
                assignments[entity.local_index] = track_id
                self.events.append(
                    LineageEvent("birth", step, event_time, child_track_ids=(track_id,))
                )
            self._previous = {assignments[e.local_index]: e for e in entities}
            return [TrackedObservation(assignments[e.local_index], e) for e in entities]

        candidate_scores: list[tuple[float, int, int]] = []
        edge_terms: dict[tuple[int, int], tuple[float, float, bool, bool, float]] = {}
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
                distance_passed = distance <= self.spec.max_centroid_distance
                size_passed = size_ratio >= self.spec.min_size_ratio
                score = float(
                    size_ratio * np.exp(-distance / self.spec.max_centroid_distance)
                )
                edge_terms[(track_id, entity.local_index)] = (
                    distance,
                    size_ratio,
                    distance_passed,
                    size_passed,
                    score,
                )
                if distance_passed and size_passed:
                    # The association function is deliberately separate from
                    # both final phenotype continuity P and ID-Jaccard M.
                    candidate_scores.append((score, track_id, entity.local_index))
                    by_parent[track_id].append(entity.local_index)
                    by_child[entity.local_index].append(track_id)

        assigned_parents: set[int] = set()
        assigned_children: set[int] = set()
        assignments = {}
        selected_pairs: set[tuple[int, int]] = set()
        for score, track_id, local_index in sorted(
            candidate_scores,
            key=lambda item: (-item[0], item[1], item[2]),
        ):
            if track_id in assigned_parents or local_index in assigned_children:
                continue
            assignments[local_index] = track_id
            selected_pairs.add((track_id, local_index))
            assigned_parents.add(track_id)
            assigned_children.add(local_index)
            entity = entity_by_index[local_index]
            self.tracks[track_id].append(entity)
            self.events.append(
                LineageEvent(
                    "continuity",
                    step,
                    event_time,
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
                    LineageEvent("birth", step, event_time, child_track_ids=(track_id,))
                )

        for parent_track_id, child_indices in sorted(by_parent.items()):
            child_tracks = tuple(sorted({assignments[index] for index in child_indices}))
            is_unambiguous_split = len(child_tracks) > 1 and all(
                len(set(by_child[index])) == 1 for index in child_indices
            )
            if is_unambiguous_split:
                self.events.append(
                    LineageEvent(
                        "split",
                        step,
                        event_time,
                        parent_track_ids=(parent_track_id,),
                        child_track_ids=child_tracks,
                        detail="multiple physically compatible child entities",
                    )
                )

        ambiguous_parents = {
            parent: tuple(sorted(children))
            for parent, children in by_parent.items()
            if len(children) > 1
            and not all(len(set(by_child[child])) == 1 for child in children)
        }
        ambiguous_children = {
            child: tuple(sorted(parents))
            for child, parents in by_child.items()
            if len(parents) > 1
            and not all(len(set(by_parent[parent])) == 1 for parent in parents)
        }
        if ambiguous_parents or ambiguous_children:
            self.events.append(
                LineageEvent(
                    "ambiguous_association",
                    step,
                    event_time,
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

        for (track_id, local_index), terms in sorted(edge_terms.items()):
            distance, size_ratio, distance_passed, size_passed, score = terms
            if not (distance_passed and size_passed):
                classification = "rejected_by_gate"
            elif len(set(by_parent[track_id])) > 1 and all(
                len(set(by_child[child])) == 1 for child in by_parent[track_id]
            ):
                classification = "split_candidate"
            elif len(set(by_child[local_index])) > 1 and all(
                len(set(by_parent[parent])) == 1 for parent in by_child[local_index]
            ):
                classification = "merge_candidate"
            elif len(set(by_parent[track_id])) > 1 or len(set(by_child[local_index])) > 1:
                classification = "ambiguous_candidate"
            else:
                classification = "unique_candidate"
            self.association_edges.append(
                AssociationEdge(
                    snapshot_step=step,
                    time=event_time,
                    parent_track_id=track_id,
                    child_local_index=local_index,
                    centroid_distance=distance,
                    size_ratio=size_ratio,
                    distance_gate_passed=distance_passed,
                    size_gate_passed=size_passed,
                    score=score,
                    selected=(track_id, local_index) in selected_pairs,
                    classification=classification,
                )
            )

        for child_index, parent_tracks in sorted(by_child.items()):
            unique_parents = tuple(sorted(set(parent_tracks)))
            is_unambiguous_merge = len(unique_parents) > 1 and all(
                len(set(by_parent[parent])) == 1 for parent in unique_parents
            )
            if is_unambiguous_merge:
                self.events.append(
                    LineageEvent(
                        "merge",
                        step,
                        event_time,
                        parent_track_ids=unique_parents,
                        child_track_ids=(assignments[child_index],),
                        detail="multiple physically compatible parent entities",
                    )
                )

        alternative_parents = {
            track_id
            for parents in by_child.values()
            if len(parents) > 1
            for track_id in parents
        }
        for track_id, previous in sorted(self._previous.items()):
            if track_id not in assigned_parents:
                reason = (
                    "compatible alternative not selected"
                    if track_id in alternative_parents
                    else "no selected physical continuation"
                )
                self.events.append(
                    LineageEvent(
                        "disappearance",
                        step,
                        event_time,
                        parent_track_ids=(track_id,),
                        detail=reason,
                    )
                )

        self._previous = {assignments[e.local_index]: e for e in entities}
        return [TrackedObservation(assignments[e.local_index], e) for e in entities]
