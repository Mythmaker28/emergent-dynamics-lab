import numpy as np

from edlab.entities.detection import EntityObservation
from edlab.entities.tracking import LineageTracker
from edlab.observables.continuity import measure_tracks
from edlab.observables.phenotype import Phenotype
from edlab.specs import TrackerSpec


def _entity(local: int, step: int, x: float, count: int, id_offset: int) -> EntityObservation:
    phenotype = Phenotype(("fixture",), np.array([count / 10.0]), {"fixture": count / 10.0})
    return EntityObservation(
        local_index=local,
        snapshot_step=step,
        time=float(step),
        particle_indices=tuple(range(count)),
        particle_ids=frozenset(range(id_offset, id_offset + count)),
        centroid=np.array([x, 0.5]),
        phenotype=phenotype,
    )


def test_lineage_birth_continuity_split_merge_and_disappearance() -> None:
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.12, min_size_ratio=0.4), box_size=1.0
    )
    first = tracker.update([_entity(0, 0, 0.50, 8, 0)])
    second = tracker.update([_entity(0, 1, 0.52, 8, 100)])
    assert first[0].track_id == second[0].track_id
    split = tracker.update(
        [_entity(0, 2, 0.48, 5, 200), _entity(1, 2, 0.56, 4, 300)]
    )
    assert len({item.track_id for item in split}) == 2
    merged = tracker.update([_entity(0, 3, 0.52, 8, 400)])
    assert len(merged) == 1
    tracker.update([], snapshot_step=4, time=4.0)
    kinds = [event.kind for event in tracker.events]
    for expected in ("birth", "continuity", "split", "merge", "disappearance"):
        assert expected in kinds


def test_fresh_ids_do_not_change_tracker_topology_or_p() -> None:
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.12, min_size_ratio=0.5), box_size=1.0
    )
    first = tracker.update([_entity(0, 0, 0.50, 6, 0)])
    second = tracker.update([_entity(0, 1, 0.51, 6, 1000)])
    assert first[0].track_id == second[0].track_id
    assert second[0].entity.particle_ids.isdisjoint(first[0].entity.particle_ids)


def test_many_to_many_crossing_is_ambiguity_not_false_split_merge() -> None:
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.2, min_size_ratio=0.5), box_size=1.0
    )
    tracker.update([_entity(0, 0, 0.45, 6, 0), _entity(1, 0, 0.55, 6, 100)])
    tracker.update([_entity(0, 1, 0.46, 6, 200), _entity(1, 1, 0.54, 6, 300)])
    kinds = [event.kind for event in tracker.events]
    assert "ambiguous_association" in kinds
    assert "split" not in kinds
    assert "merge" not in kinds
    assert len(tracker.association_edges) == 4
    assert all(
        edge.classification == "ambiguous_candidate"
        for edge in tracker.association_edges
    )
    assert sum(edge.selected for edge in tracker.association_edges) == 2
    measurements = measure_tracks(
        tracker.tracks, lag_indices=(1,), events=tracker.events
    )
    assert measurements
    assert all(measurement.interval_has_ambiguity for measurement in measurements)


def test_empty_snapshot_uses_current_timestamp() -> None:
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.2, min_size_ratio=0.5), box_size=1.0
    )
    tracker.update([_entity(0, 0, 0.5, 6, 0)])
    tracker.update([], snapshot_step=9, time=1.8)
    disappearance = [event for event in tracker.events if event.kind == "disappearance"][-1]
    assert disappearance.snapshot_step == 9
    assert disappearance.time == 1.8
