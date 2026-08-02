"""Hand-built source-only qualification for the future lifecycle contract."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import os

import pytest

from edlab.substrates.lattice_bond.instrumentation import (
    DetectedComponent,
    TrackEvent,
    TrackPoint,
    TrackRecord,
    TrackerSpec,
    TrackingResult,
    track_components,
)
from edlab.substrates.lattice_bond.lifecycle import (
    LifecycleContractError,
    LifecyclePublicationError,
    SCHEMA_VERSION,
    canonical_lifecycle_bytes,
    qualify_and_write_lifecycle_contract,
    qualify_lifecycle_contract,
    verify_lifecycle_document,
)


def _track(
    track_id: int,
    points: tuple[tuple[int, int], ...],
    *,
    parents: tuple[int, ...] = (),
    children: tuple[int, ...] = (),
    unresolved: bool = False,
) -> TrackRecord:
    return TrackRecord(
        track_id,
        tuple(TrackPoint(frame, component) for frame, component in points),
        parents,
        children,
        unresolved,
    )


def _event(
    frame: int,
    kind: str,
    sources: tuple[int, ...] = (),
    source_components: tuple[tuple[int, int], ...] = (),
    target_components: tuple[tuple[int, int], ...] = (),
    targets: tuple[int, ...] = (),
    resolved: bool = True,
) -> TrackEvent:
    return TrackEvent(
        frame,
        kind,  # type: ignore[arg-type]
        sources,
        source_components,
        target_components,
        targets,
        resolved,
    )


def _tracking(
    tracks: tuple[TrackRecord, ...],
    events: tuple[TrackEvent, ...],
    *,
    assignments: tuple[tuple[int, int, int], ...] | None = None,
) -> TrackingResult:
    if assignments is None:
        assignments = tuple(
            (point.frame, point.component_index, track.track_id)
            for track in tracks
            for point in track.points
        )
    return TrackingResult(tracks, events, (), assignments)


def _appearance(frame: int, track_id: int, component: int) -> TrackEvent:
    return _event(
        frame,
        "APPEARANCE",
        target_components=((frame, component),),
        targets=(track_id,),
    )


def _continuation(
    track_id: int,
    source: tuple[int, int],
    target: tuple[int, int],
) -> TrackEvent:
    return _event(
        target[0],
        "CONTINUATION",
        (track_id,),
        (source,),
        (target,),
        (track_id,),
    )


def _horizon_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 5, 10)
    track = _track(0, ((0, 0), (5, 0), (10, 0)))
    events = (
        _appearance(0, 0, 0),
        _continuation(0, (0, 0), (5, 0)),
        _continuation(0, (5, 0), (10, 0)),
    )
    return _tracking((track,), events), frames


def _dissolution_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 5, 10)
    track = _track(0, ((0, 0), (5, 0)))
    events = (
        _appearance(0, 0, 0),
        _continuation(0, (0, 0), (5, 0)),
        _event(10, "DISSOLUTION", (0,), ((5, 0),)),
    )
    return _tracking((track,), events), frames


def _split_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 5, 10, 15)
    tracks = (
        _track(0, ((0, 0), (5, 0)), children=(1, 2)),
        _track(1, ((10, 0), (15, 0)), parents=(0,)),
        _track(2, ((10, 1), (15, 1)), parents=(0,)),
    )
    events = (
        _appearance(0, 0, 0),
        _continuation(0, (0, 0), (5, 0)),
        _event(
            10,
            "SPLIT",
            (0,),
            ((5, 0),),
            ((10, 0), (10, 1)),
            (1, 2),
        ),
        _continuation(1, (10, 0), (15, 0)),
        _continuation(2, (10, 1), (15, 1)),
    )
    return _tracking(tracks, events), frames


def _merge_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 5, 10, 15, 20)
    tracks = (
        _track(0, ((0, 0), (5, 0)), children=(2,)),
        _track(1, ((0, 1), (5, 1)), children=(2,)),
        _track(2, ((10, 0), (15, 0)), parents=(0, 1)),
    )
    events = (
        _appearance(0, 0, 0),
        _appearance(0, 1, 1),
        _continuation(0, (0, 0), (5, 0)),
        _continuation(1, (0, 1), (5, 1)),
        _event(
            10,
            "MERGE",
            (0, 1),
            ((5, 0), (5, 1)),
            ((10, 0),),
            (2,),
        ),
        _continuation(2, (10, 0), (15, 0)),
        _event(20, "DISSOLUTION", (2,), ((15, 0),)),
    )
    return _tracking(tracks, events), frames


def _unresolved_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 1, 2, 3)
    tracks = (
        _track(0, ((0, 0), (1, 0)), children=(1, 2), unresolved=True),
        _track(1, ((2, 0), (3, 0)), parents=(0,), unresolved=True),
        _track(2, ((2, 1), (3, 1)), parents=(0,), unresolved=True),
    )
    events = (
        _appearance(0, 0, 0),
        _continuation(0, (0, 0), (1, 0)),
        _event(
            2,
            "TRACKING_UNRESOLVED",
            (0,),
            ((1, 0),),
            ((2, 0), (2, 1)),
            (1, 2),
            False,
        ),
        _continuation(1, (2, 0), (3, 0)),
        _continuation(2, (2, 1), (3, 1)),
    )
    return _tracking(tracks, events), frames


def _many_to_many_unresolved_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 1, 2, 3, 4)
    tracks = (
        _track(0, ((0, 0), (1, 0)), children=(2, 3), unresolved=True),
        _track(1, ((0, 1), (1, 1)), children=(2, 3), unresolved=True),
        _track(2, ((2, 0), (3, 0)), parents=(0, 1), unresolved=True),
        _track(3, ((2, 1), (3, 1), (4, 1)), parents=(0, 1), unresolved=True),
    )
    events = (
        _appearance(0, 0, 0),
        _appearance(0, 1, 1),
        _continuation(0, (0, 0), (1, 0)),
        _continuation(1, (0, 1), (1, 1)),
        _event(
            2,
            "TRACKING_UNRESOLVED",
            (0, 1),
            ((1, 0), (1, 1)),
            ((2, 0), (2, 1)),
            (2, 3),
            False,
        ),
        _continuation(2, (2, 0), (3, 0)),
        _continuation(3, (2, 1), (3, 1)),
        _event(4, "DISSOLUTION", (2,), ((3, 0),)),
        _continuation(3, (3, 1), (4, 1)),
    )
    return _tracking(tracks, events), frames


def _contact_fixture() -> tuple[TrackingResult, tuple[int, ...]]:
    frames = (0, 1)
    tracks = (
        _track(0, ((0, 0), (1, 0))),
        _track(1, ((0, 1), (1, 1))),
    )
    events = (
        _appearance(0, 0, 0),
        _appearance(0, 1, 1),
        _continuation(0, (0, 0), (1, 0)),
        _continuation(1, (0, 1), (1, 1)),
        _event(
            1,
            "TEMPORARY_CONTACT",
            (0, 1),
            ((1, 0), (1, 1)),
            ((1, 0), (1, 1)),
            (0, 1),
        ),
    )
    return _tracking(tracks, events), frames


def _codes(error: LifecycleContractError) -> tuple[str, ...]:
    return tuple(item.code for item in error.violations)


def test_zero_tracks_has_explicit_qualified_run_closure() -> None:
    contract = qualify_lifecycle_contract(TrackingResult((), (), (), ()), (0, 1))
    assert contract.run_terminal_state == "EMPTY_TRACK_SET"
    assert contract.track_count == 0
    assert contract.terminal_records == ()
    assert contract.as_dict()["qualification"] == {
        "all_tracks_closed": True,
        "disposition": "QUALIFIED",
        "run_terminal_state": "EMPTY_TRACK_SET",
    }


def test_nonunit_horizon_censoring_is_explicit() -> None:
    tracking, frames = _horizon_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    [record] = contract.terminal_records
    assert record.terminal_state == "RIGHT_CENSORED_AT_HORIZON"
    assert record.last_observed_frame == 10
    assert record.terminal_frame == 10
    assert record.evidence_kind == "DECLARED_HORIZON"
    assert record.terminal_event_id is None


def test_late_appearance_at_horizon_is_not_a_gap() -> None:
    tracking = _tracking((_track(4, ((10, 2),)),), (_appearance(10, 4, 2),))
    contract = qualify_lifecycle_contract(tracking, (0, 5, 10))
    assert contract.terminal_records[0].first_observed_frame == 10
    assert contract.terminal_records[0].terminal_state == "RIGHT_CENSORED_AT_HORIZON"


def test_dissolution_is_a_detected_track_ending_not_inferred_death() -> None:
    tracking, frames = _dissolution_fixture()
    [record] = qualify_lifecycle_contract(tracking, frames).terminal_records
    assert record.terminal_state == "DISSOLVED_DETECTED_TRACK"
    assert record.last_observed_frame == 5
    assert record.terminal_frame == 10
    assert record.evidence_kind == "TRACK_EVENT"
    assert record.terminal_event_id is not None


def test_split_closes_parent_and_each_successor_closes_independently() -> None:
    tracking, frames = _split_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    states = {row.track_id: row.terminal_state for row in contract.terminal_records}
    assert states == {
        0: "SPLIT_INTO_TRACKS",
        1: "RIGHT_CENSORED_AT_HORIZON",
        2: "RIGHT_CENSORED_AT_HORIZON",
    }
    assert contract.terminal_records[0].successor_track_ids == (1, 2)


def test_merge_closes_each_parent_and_successor_can_later_dissolve() -> None:
    tracking, frames = _merge_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    assert [row.terminal_state for row in contract.terminal_records] == [
        "MERGED_INTO_TRACK",
        "MERGED_INTO_TRACK",
        "DISSOLVED_DETECTED_TRACK",
    ]
    assert contract.terminal_records[0].successor_track_ids == (2,)
    assert contract.terminal_records[1].successor_track_ids == (2,)


def test_unresolved_handoff_is_explicit_without_closing_successors() -> None:
    tracking, frames = _unresolved_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    assert contract.terminal_records[0].terminal_state == "UNRESOLVED_HANDOFF"
    assert contract.terminal_records[0].lineage_status == "UNRESOLVED"
    assert all(row.lineage_status == "UNRESOLVED" for row in contract.terminal_records)
    assert all(
        row.terminal_state == "RIGHT_CENSORED_AT_HORIZON"
        for row in contract.terminal_records[1:]
    )


def test_many_to_many_unresolved_handoff_closes_every_source_and_successor() -> None:
    tracking, frames = _many_to_many_unresolved_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    assert [row.terminal_state for row in contract.terminal_records] == [
        "UNRESOLVED_HANDOFF",
        "UNRESOLVED_HANDOFF",
        "DISSOLVED_DETECTED_TRACK",
        "RIGHT_CENSORED_AT_HORIZON",
    ]
    assert all(row.lineage_status == "UNRESOLVED" for row in contract.terminal_records)


def test_temporary_contact_is_strictly_nonterminal() -> None:
    tracking, frames = _contact_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    assert all(row.terminal_state == "RIGHT_CENSORED_AT_HORIZON" for row in contract.terminal_records)


@pytest.mark.parametrize(
    ("fixture", "expected_states"),
    [
        (_horizon_fixture, ("RIGHT_CENSORED_AT_HORIZON",)),
        (_dissolution_fixture, ("DISSOLVED_DETECTED_TRACK",)),
        (
            _split_fixture,
            ("SPLIT_INTO_TRACKS", "RIGHT_CENSORED_AT_HORIZON", "RIGHT_CENSORED_AT_HORIZON"),
        ),
        (_merge_fixture, ("MERGED_INTO_TRACK", "MERGED_INTO_TRACK", "DISSOLVED_DETECTED_TRACK")),
        (
            _unresolved_fixture,
            ("UNRESOLVED_HANDOFF", "RIGHT_CENSORED_AT_HORIZON", "RIGHT_CENSORED_AT_HORIZON"),
        ),
    ],
)
def test_terminal_count_is_a_bijection_over_tracks(fixture, expected_states) -> None:
    tracking, frames = fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    assert contract.track_count == len(contract.terminal_records)
    assert tuple(row.terminal_state for row in contract.terminal_records) == expected_states


def test_permuted_semantic_inputs_have_identical_canonical_bytes() -> None:
    tracking, frames = _split_fixture()
    permuted_tracks = tuple(reversed(tracking.tracks))
    permuted_events = tuple(
        replace(
            event,
            source_track_ids=tuple(reversed(event.source_track_ids)),
            source_components=tuple(reversed(event.source_components)),
            target_components=tuple(reversed(event.target_components)),
            target_track_ids=tuple(reversed(event.target_track_ids)),
        )
        for event in reversed(tracking.events)
    )
    permuted = TrackingResult(
        permuted_tracks,
        permuted_events,
        (),
        tuple(reversed(tracking.assignments)),
    )
    first = canonical_lifecycle_bytes(qualify_lifecycle_contract(tracking, frames))
    second = canonical_lifecycle_bytes(qualify_lifecycle_contract(permuted, frames))
    assert first == second


def test_digest_and_schema_envelope_are_self_consistent() -> None:
    tracking, frames = _split_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    document = contract.as_dict()
    assert document["schema_version"] == SCHEMA_VERSION
    records = document["terminal_records"]
    expected_digest = hashlib.sha256(
        json.dumps(records, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()
    assert document["lifecycle_binding"]["records_sha256"] == expected_digest
    assert document["lifecycle_binding"]["terminal_record_count"] == len(tracking.tracks)
    assert "lifecycle_input_sha256" in document["source_binding"]
    assert "generic_tracker_sha256" not in document["source_binding"]


def test_lifecycle_input_digest_binds_the_complete_sample_schedule() -> None:
    tracking = _tracking((_track(4, ((10, 2),)),), (_appearance(10, 4, 2),))
    wider = qualify_lifecycle_contract(tracking, (0, 5, 10))
    narrower = qualify_lifecycle_contract(tracking, (5, 10))
    assert wider.lifecycle_input_digest_sha256 != narrower.lifecycle_input_digest_sha256
    assert [row.as_dict() for row in wider.terminal_records] == [
        row.as_dict() for row in narrower.terminal_records
    ]


def test_atomic_publication_and_independent_byte_verification(tmp_path: Path) -> None:
    tracking, frames = _split_fixture()
    target = tmp_path / "LIFECYCLE_CONTRACT.json"
    contract = qualify_and_write_lifecycle_contract(target, tracking, frames)
    assert target.read_bytes() == canonical_lifecycle_bytes(contract)
    assert verify_lifecycle_document(target.read_bytes(), tracking, frames) == contract
    assert not (tmp_path / ".LIFECYCLE_CONTRACT.json.partial").exists()


def test_atomic_publication_refuses_overwrite_and_preserves_unrelated_partial(tmp_path: Path) -> None:
    tracking, frames = _horizon_fixture()
    target = tmp_path / "LIFECYCLE_CONTRACT.json"
    qualify_and_write_lifecycle_contract(target, tracking, frames)
    with pytest.raises(LifecyclePublicationError, match="overwrite"):
        qualify_and_write_lifecycle_contract(target, tracking, frames)

    second = tmp_path / "SECOND.json"
    (tmp_path / ".SECOND.json.partial").write_bytes(b"do not destroy")
    qualify_and_write_lifecycle_contract(second, tracking, frames)
    assert (tmp_path / ".SECOND.json.partial").read_bytes() == b"do not destroy"
    assert second.exists()


def test_atomic_publication_preserves_a_late_racing_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tracking, frames = _horizon_fixture()
    target = tmp_path / "LIFECYCLE_CONTRACT.json"
    real_link = os.link

    def racing_link(source, destination) -> None:
        Path(destination).write_bytes(b"concurrent creator")
        real_link(source, destination)

    monkeypatch.setattr(os, "link", racing_link)
    with pytest.raises(LifecyclePublicationError, match="concurrent"):
        qualify_and_write_lifecycle_contract(target, tracking, frames)
    assert target.read_bytes() == b"concurrent creator"
    assert not (tmp_path / ".LIFECYCLE_CONTRACT.json.partial").exists()


def test_atomic_publication_rejects_a_swapped_partial_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tracking, frames = _horizon_fixture()
    target = tmp_path / "LIFECYCLE_CONTRACT.json"
    foreign = tmp_path / "FOREIGN.partial"
    foreign.write_bytes(b"swapped partial bytes")
    real_link = os.link

    def swapping_link(source, destination) -> None:
        real_link(foreign, destination)

    monkeypatch.setattr(os, "link", swapping_link)
    with pytest.raises(LifecyclePublicationError, match="identity|bytes"):
        qualify_and_write_lifecycle_contract(target, tracking, frames)
    assert target.read_bytes() == b"swapped partial bytes"
    assert foreign.read_bytes() == b"swapped partial bytes"
    assert not tuple(tmp_path.glob(".LIFECYCLE_CONTRACT.json.*.partial"))


def test_atomic_publication_requires_existing_parent(tmp_path: Path) -> None:
    tracking, frames = _horizon_fixture()
    with pytest.raises(LifecyclePublicationError, match="parent"):
        qualify_and_write_lifecycle_contract(tmp_path / "missing" / "contract.json", tracking, frames)


def test_document_verifier_rejects_noncanonical_and_tampered_documents() -> None:
    tracking, frames = _horizon_fixture()
    contract = qualify_lifecycle_contract(tracking, frames)
    pretty = json.dumps(contract.as_dict(), indent=2).encode()
    with pytest.raises(LifecycleContractError) as noncanonical:
        verify_lifecycle_document(pretty, tracking, frames)
    assert _codes(noncanonical.value) == ("DOCUMENT_NOT_CANONICAL",)

    altered = contract.as_dict()
    altered["qualification"]["all_tracks_closed"] = False
    tampered = json.dumps(altered, separators=(",", ":"), sort_keys=True).encode()
    with pytest.raises(LifecycleContractError) as mismatch:
        verify_lifecycle_document(tampered, tracking, frames)
    assert _codes(mismatch.value) == ("DOCUMENT_BINDING_MISMATCH",)

    with pytest.raises(LifecycleContractError) as invalid_json:
        verify_lifecycle_document(b"{", tracking, frames)
    assert _codes(invalid_json.value) == ("DOCUMENT_INVALID_JSON",)


def test_silent_pre_horizon_termination_is_never_inferred() -> None:
    tracking, frames = _dissolution_fixture()
    without_terminal = replace(tracking, events=tracking.events[:-1])
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(without_terminal, frames)
    assert "SILENT_PRE_HORIZON_TERMINATION" in _codes(caught.value)


def test_point_gap_in_declared_schedule_fails() -> None:
    track = _track(0, ((0, 0), (10, 0)))
    tracking = _tracking(
        (track,),
        (_appearance(0, 0, 0), _continuation(0, (0, 0), (10, 0))),
    )
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(tracking, (0, 5, 10))
    assert "TRACK_POINT_GAP" in _codes(caught.value)


def test_empty_or_nonincreasing_frame_schedule_fails_first() -> None:
    tracking = TrackingResult((), (), (), ())
    with pytest.raises(LifecycleContractError) as empty:
        qualify_lifecycle_contract(tracking, ())
    assert _codes(empty.value) == ("EMPTY_SAMPLE_SCHEDULE",)
    with pytest.raises(LifecycleContractError) as duplicate:
        qualify_lifecycle_contract(tracking, (0, 5, 5))
    assert _codes(duplicate.value) == ("NON_INCREASING_SAMPLE_SCHEDULE",)


def test_missing_onset_and_continuation_events_fail() -> None:
    tracking, frames = _horizon_fixture()
    with pytest.raises(LifecycleContractError) as missing_onset:
        qualify_lifecycle_contract(replace(tracking, events=tracking.events[1:]), frames)
    assert "MISSING_ONSET_EVENT" in _codes(missing_onset.value)
    with pytest.raises(LifecycleContractError) as missing_continuation:
        qualify_lifecycle_contract(replace(tracking, events=(tracking.events[0], tracking.events[2])), frames)
    assert "MISSING_CONTINUATION_EVENT" in _codes(missing_continuation.value)


def test_terminal_must_be_at_immediately_next_declared_sample() -> None:
    tracking, frames = _dissolution_fixture()
    bad = replace(tracking.events[-1], frame=5)
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(replace(tracking, events=tracking.events[:-1] + (bad,)), frames)
    assert "TERMINAL_FRAME_MISMATCH" in _codes(caught.value)


def test_duplicate_or_conflicting_terminal_events_fail() -> None:
    tracking, frames = _dissolution_fixture()
    duplicated = replace(tracking, events=tracking.events + (tracking.events[-1],))
    with pytest.raises(LifecycleContractError) as duplicate:
        qualify_lifecycle_contract(duplicated, frames)
    assert "DUPLICATE_EVENT" in _codes(duplicate.value)
    assert "MULTIPLE_TERMINAL_EVENTS" in _codes(duplicate.value)

    conflicting_split = _event(
        10,
        "SPLIT",
        (0,),
        ((5, 0),),
        ((10, 1), (10, 2)),
        (1, 2),
    )
    tracks = tracking.tracks + (
        _track(1, ((10, 1),), parents=(0,)),
        _track(2, ((10, 2),), parents=(0,)),
    )
    events = tracking.events + (
        conflicting_split,
        _event(10, "APPEARANCE", target_components=((10, 1),), targets=(1,)),
        _event(10, "APPEARANCE", target_components=((10, 2),), targets=(2,)),
    )
    conflict = _tracking(tracks, events)
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(conflict, frames)
    assert "MULTIPLE_TERMINAL_EVENTS" in _codes(caught.value)


def test_unknown_event_kind_and_unknown_track_fail_closed() -> None:
    tracking, frames = _horizon_fixture()
    unknown_kind = _event(5, "NEW_SILENT_KIND", (0,), ((0, 0),), ((5, 0),), (0,))
    with pytest.raises(LifecycleContractError) as kind_error:
        qualify_lifecycle_contract(replace(tracking, events=(tracking.events[0], unknown_kind, tracking.events[2])), frames)
    assert "UNKNOWN_EVENT_KIND" in _codes(kind_error.value)

    dangling = _event(10, "SPLIT", (0,), ((5, 0),), ((10, 7), (10, 8)), (7, 8))
    base, base_frames = _dissolution_fixture()
    with pytest.raises(LifecycleContractError) as id_error:
        qualify_lifecycle_contract(replace(base, events=base.events[:-1] + (dangling,)), base_frames)
    assert "UNKNOWN_LINEAGE_ID" in _codes(id_error.value)


def test_duplicate_track_empty_track_and_duplicate_component_fail() -> None:
    tracking, frames = _horizon_fixture()
    duplicate_id = replace(tracking, tracks=tracking.tracks + (tracking.tracks[0],))
    with pytest.raises(LifecycleContractError) as duplicate:
        qualify_lifecycle_contract(duplicate_id, frames)
    assert "DUPLICATE_TRACK_ID" in _codes(duplicate.value)

    empty = _tracking((_track(0, ()),), ())
    with pytest.raises(LifecycleContractError) as empty_error:
        qualify_lifecycle_contract(empty, (0,))
    assert "EMPTY_TRACK" in _codes(empty_error.value)

    colliding = _tracking(
        (_track(0, ((0, 0),)), _track(1, ((0, 0),))),
        (_appearance(0, 0, 0), _appearance(0, 1, 0)),
    )
    with pytest.raises(LifecycleContractError) as collision:
        qualify_lifecycle_contract(colliding, (0,))
    assert "DUPLICATE_COMPONENT_POINT" in _codes(collision.value)


def test_reciprocal_parent_and_child_links_are_mandatory() -> None:
    tracking, frames = _split_fixture()
    missing_child = replace(tracking.tracks[0], child_track_ids=(1,))
    with pytest.raises(LifecycleContractError) as child_error:
        qualify_lifecycle_contract(replace(tracking, tracks=(missing_child,) + tracking.tracks[1:]), frames)
    assert "CHILD_LINK_MISMATCH" in _codes(child_error.value)

    missing_parent = replace(tracking.tracks[1], parent_track_ids=())
    with pytest.raises(LifecycleContractError) as parent_error:
        qualify_lifecycle_contract(replace(tracking, tracks=(tracking.tracks[0], missing_parent, tracking.tracks[2])), frames)
    assert "PARENT_LINK_MISMATCH" in _codes(parent_error.value)


def test_unresolved_flag_requires_and_follows_an_unresolved_event() -> None:
    tracking, frames = _horizon_fixture()
    falsely_unresolved = replace(tracking.tracks[0], unresolved=True)
    with pytest.raises(LifecycleContractError) as false_flag:
        qualify_lifecycle_contract(replace(tracking, tracks=(falsely_unresolved,)), frames)
    assert "UNRESOLVED_FLAG_MISMATCH" in _codes(false_flag.value)

    unresolved, unresolved_frames = _unresolved_fixture()
    false_source = replace(unresolved.tracks[0], unresolved=False)
    with pytest.raises(LifecycleContractError) as missing_flag:
        qualify_lifecycle_contract(replace(unresolved, tracks=(false_source,) + unresolved.tracks[1:]), unresolved_frames)
    assert "UNRESOLVED_FLAG_MISMATCH" in _codes(missing_flag.value)


def test_assignments_are_exactly_bound_to_track_points() -> None:
    tracking, frames = _horizon_fixture()
    with pytest.raises(LifecycleContractError) as missing:
        qualify_lifecycle_contract(replace(tracking, assignments=tracking.assignments[:-1]), frames)
    assert "ASSIGNMENT_SET_MISMATCH" in _codes(missing.value)

    duplicate = replace(tracking, assignments=tracking.assignments + (tracking.assignments[-1],))
    with pytest.raises(LifecycleContractError) as duplicated:
        qualify_lifecycle_contract(duplicate, frames)
    assert "DUPLICATE_ASSIGNMENT" in _codes(duplicated.value)


@pytest.mark.parametrize(
    "bad_event",
    [
        _event(10, "DISSOLUTION", (0,), ((5, 0),), targets=(1,)),
        _event(10, "DISSOLUTION", (0,), ((5, 0),), resolved=False),
        _event(10, "SPLIT", (0,), ((5, 0),), ((10, 1),), (1,)),
        _event(10, "MERGE", (0,), ((5, 0),), ((10, 1),), (1,)),
        _event(10, "TRACKING_UNRESOLVED", (), (), ((10, 1),), (1,), False),
    ],
)
def test_terminal_event_cardinality_and_resolution_are_closed(bad_event: TrackEvent) -> None:
    tracking, frames = _dissolution_fixture()
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(replace(tracking, events=tracking.events[:-1] + (bad_event,)), frames)
    assert set(_codes(caught.value)) & {
        "EVENT_CARDINALITY_MISMATCH",
        "INVALID_EVENT_RESOLUTION",
        "EVENT_POLARITY_MISMATCH",
    }


def test_temporary_contact_is_exactly_two_to_same_two() -> None:
    tracking, frames = _contact_fixture()
    bad_contact = replace(
        tracking.events[-1],
        source_track_ids=(0,),
        source_components=((1, 0),),
        target_track_ids=(0,),
        target_components=((1, 0),),
    )
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(replace(tracking, events=tracking.events[:-1] + (bad_contact,)), frames)
    assert "EVENT_CARDINALITY_MISMATCH" in _codes(caught.value)


def test_target_must_begin_at_lineage_event_frame() -> None:
    tracking, frames = _split_fixture()
    delayed = replace(
        tracking.tracks[1],
        points=(TrackPoint(15, 0),),
    )
    assignments = tuple(
        (point.frame, point.component_index, track.track_id)
        for track in (tracking.tracks[0], delayed, tracking.tracks[2])
        for point in track.points
    )
    malformed = replace(
        tracking,
        tracks=(tracking.tracks[0], delayed, tracking.tracks[2]),
        assignments=assignments,
    )
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(malformed, frames)
    assert set(_codes(caught.value)) & {"EVENT_COMPONENT_UNASSIGNED", "EVENT_TEMPORAL_MISMATCH"}


def test_event_component_polarity_and_post_terminal_references_fail() -> None:
    tracking, frames = _contact_fixture()
    swapped = replace(
        tracking.events[-1],
        source_track_ids=(0, 1),
        source_components=((1, 1), (1, 0)),
        target_track_ids=(0, 1),
        target_components=((1, 0), (1, 1)),
    )
    # Component tuples are semantically unordered for a contact, so force an
    # actual polarity violation by assigning only track 1's component to track 0.
    malformed = replace(swapped, source_components=((1, 1), (1, 1)))
    with pytest.raises(LifecycleContractError) as polarity:
        qualify_lifecycle_contract(replace(tracking, events=tracking.events[:-1] + (malformed,)), frames)
    assert set(_codes(polarity.value)) & {
        "DUPLICATE_EVENT_COMPONENT",
        "EVENT_COMPONENT_POLARITY_MISMATCH",
    }

    dissolved, dissolve_frames = _dissolution_fixture()
    afterlife = _event(
        10,
        "APPEARANCE",
        target_components=((5, 0),),
        targets=(0,),
    )
    with pytest.raises(LifecycleContractError) as post_terminal:
        qualify_lifecycle_contract(replace(dissolved, events=dissolved.events + (afterlife,)), dissolve_frames)
    assert "POST_TERMINAL_EVENT" in _codes(post_terminal.value) or "MULTIPLE_ONSET_EVENTS" in _codes(post_terminal.value)


def test_lineage_cycle_and_self_link_fail() -> None:
    track0 = _track(0, ((0, 0),), parents=(1,), children=(1,))
    track1 = _track(1, ((1, 0),), parents=(0,), children=(0,))
    events = (
        _event(0, "APPEARANCE", target_components=((0, 0),), targets=(0,)),
        _event(1, "SPLIT", (0,), ((0, 0),), ((1, 0), (1, 1)), (1, 2)),
    )
    malformed = _tracking((track0, track1), events)
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(malformed, (0, 1))
    assert "CYCLIC_LINEAGE" in _codes(caught.value)

    base, frames = _horizon_fixture()
    self_link = replace(base.tracks[0], parent_track_ids=(0,))
    with pytest.raises(LifecycleContractError) as self_error:
        qualify_lifecycle_contract(replace(base, tracks=(self_link,)), frames)
    assert "SELF_LINEAGE_LINK" in _codes(self_error.value)


def test_boolean_ids_and_frames_do_not_pass_as_integers() -> None:
    tracking, frames = _horizon_fixture()
    bool_id = replace(tracking.tracks[0], track_id=True)
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(replace(tracking, tracks=(bool_id,)), frames)
    assert "INVALID_TRACK_ID" in _codes(caught.value)
    with pytest.raises(LifecycleContractError) as frame_error:
        qualify_lifecycle_contract(tracking, (0, True, 10))
    assert _codes(frame_error.value) == ("INVALID_SAMPLE_FRAME",)
    with pytest.raises(LifecycleContractError) as negative_frame:
        qualify_lifecycle_contract(TrackingResult((), (), (), ()), (-1, 0))
    assert _codes(negative_frame.value) == ("INVALID_SAMPLE_FRAME",)


def test_error_order_is_stable_under_track_event_and_assignment_permutation() -> None:
    tracking, frames = _split_fixture()
    malformed_event = _event(10, "UNKNOWN_FUTURE_KIND", (0,), ((5, 0),), (), ())
    malformed = replace(
        tracking,
        events=tracking.events + (malformed_event,),
    )
    permuted = TrackingResult(
        tuple(reversed(malformed.tracks)),
        tuple(reversed(malformed.events)),
        (),
        tuple(reversed(malformed.assignments)),
    )
    with pytest.raises(LifecycleContractError) as first:
        qualify_lifecycle_contract(malformed, frames)
    with pytest.raises(LifecycleContractError) as second:
        qualify_lifecycle_contract(permuted, frames)
    assert tuple(item.as_dict() for item in first.value.violations) == tuple(
        item.as_dict() for item in second.value.violations
    )


def test_unknown_event_diagnostic_id_is_stable_under_internal_permutation() -> None:
    tracking, frames = _contact_fixture()
    unknown = replace(tracking.events[-1], kind="UNKNOWN_FUTURE_KIND")
    permuted_unknown = replace(
        unknown,
        source_track_ids=tuple(reversed(unknown.source_track_ids)),
        source_components=tuple(reversed(unknown.source_components)),
        target_components=tuple(reversed(unknown.target_components)),
        target_track_ids=tuple(reversed(unknown.target_track_ids)),
    )
    first_tracking = replace(tracking, events=tracking.events[:-1] + (unknown,))
    second_tracking = replace(tracking, events=tracking.events[:-1] + (permuted_unknown,))
    with pytest.raises(LifecycleContractError) as first:
        qualify_lifecycle_contract(first_tracking, frames)
    with pytest.raises(LifecycleContractError) as second:
        qualify_lifecycle_contract(second_tracking, frames)
    assert tuple(item.as_dict() for item in first.value.violations) == tuple(
        item.as_dict() for item in second.value.violations
    )


def test_collision_diagnostics_are_stable_under_input_permutation() -> None:
    malformed = _tracking(
        (_track(0, ((0, 0),)), _track(1, ((0, 0),))),
        (_appearance(0, 0, 0), _appearance(0, 1, 0)),
    )
    permuted = TrackingResult(
        tuple(reversed(malformed.tracks)),
        tuple(reversed(malformed.events)),
        (),
        tuple(reversed(malformed.assignments)),
    )
    with pytest.raises(LifecycleContractError) as first:
        qualify_lifecycle_contract(malformed, (0,))
    with pytest.raises(LifecycleContractError) as second:
        qualify_lifecycle_contract(permuted, (0,))
    assert tuple(item.as_dict() for item in first.value.violations) == tuple(
        item.as_dict() for item in second.value.violations
    )


def _component(frame: int, *, index: int = 0) -> DetectedComponent:
    return DetectedComponent(
        frame=frame,
        index=index,
        shape=(5, 5),
        cells=(6, 7, 11, 12),
        area=4,
        mass=3.2,
        centroid_y=1.5,
        centroid_x=1.5,
        radius_gyration=0.75,
        wraps_y=False,
        wraps_x=False,
    )


def test_actual_generic_tracker_output_qualifies_at_declared_nonunit_cadence() -> None:
    tracker = TrackerSpec(max_centroid_displacement=2.0, max_area_ratio=2.0, dilation_radius=1)
    result = track_components(((_component(0),), (_component(5),)), tracker)
    contract = qualify_lifecycle_contract(result, (0, 5))
    assert contract.terminal_records[0].terminal_state == "RIGHT_CENSORED_AT_HORIZON"


def test_generic_tracker_empty_right_frame_cadence_mismatch_is_rejected() -> None:
    tracker = TrackerSpec(max_centroid_displacement=2.0, max_area_ratio=2.0, dilation_radius=1)
    result = track_components(((_component(0),), ()), tracker)
    with pytest.raises(LifecycleContractError) as caught:
        qualify_lifecycle_contract(result, (0, 5))
    assert "INVALID_EVENT_FRAME" in _codes(caught.value)
    assert "SILENT_PRE_HORIZON_TERMINATION" in _codes(caught.value)


def test_committed_schema_declares_closed_terminal_rows() -> None:
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "individuation"
        / "FUTURE_LIFECYCLE_CONTRACT_00_SCHEMA.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$id"] == SCHEMA_VERSION
    assert schema["additionalProperties"] is False
    terminal = schema["$defs"]["terminal_record"]
    assert terminal["additionalProperties"] is False
    assert set(terminal["properties"]["terminal_state"]["enum"]) == {
        "DISSOLVED_DETECTED_TRACK",
        "SPLIT_INTO_TRACKS",
        "MERGED_INTO_TRACK",
        "UNRESOLVED_HANDOFF",
        "RIGHT_CENSORED_AT_HORIZON",
    }
