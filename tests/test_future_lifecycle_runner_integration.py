"""Adversarial qualification of the future-family lifecycle runner integration.

Synthetic fixtures only.  No engine, no historical family, no scientific value.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import inspect
import json
import os
from pathlib import Path

import pytest

from edlab.substrates.lattice_bond.instrumentation import (
    DetectedComponent,
    TrackerSpec,
    TrackEvent,
    TrackPoint,
    TrackRecord,
    TrackingResult,
    track_components,
)
from edlab.substrates.lattice_bond.lifecycle import (
    LifecycleRunClosure,
    LifecycleTerminalRecord,
    canonical_lifecycle_bytes,
    qualify_and_write_lifecycle_contract,
)
from edlab.substrates.lattice_bond import future_lifecycle_runner as runner
from edlab.substrates.lattice_bond.future_lifecycle_runner import (
    COMPLETION_MANIFEST_NAME,
    INTEGRATION_VERSION,
    LIFECYCLE_DOCUMENT_NAME,
    SCHEMA_VERSION,
    AnalysisAccess,
    CompletionEvidenceError,
    CompletionPublicationError,
    CompletionRecord,
    LifecycleEvidenceError,
    RunnerIntegrationError,
    RunnerState,
    open_analysis_access,
    publish_future_family_completion,
)

NONUNIT_SCHEDULE = (0, 5)
TRACKER = TrackerSpec(max_centroid_displacement=2.0, max_area_ratio=2.0, dilation_radius=1)


# --------------------------------------------------------------------------
# synthetic fixture builders
# --------------------------------------------------------------------------


def _component(frame: int, index: int = 0) -> DetectedComponent:
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


def _real_tracker_nonunit() -> TrackingResult:
    """Real generic tracker output at declared non-unit cadence, known to qualify."""

    return track_components(
        ((_component(0),), (_component(5),)), TRACKER, sampled_frames=NONUNIT_SCHEDULE
    )


def _empty_right_nonunit() -> TrackingResult:
    """Real generic tracker output with an empty right detector frame.

    01R: with the schedule mandatory this now QUALIFIES — the disappearance is bound
    to the declared frame 5 instead of a fabricated frame 1.
    """

    return track_components(((_component(0),), ()), TRACKER, sampled_frames=NONUNIT_SCHEDULE)


def _fabricated_off_schedule() -> TrackingResult:
    """Handcrafted off-schedule tracker-shaped input.

    The tracker cannot produce this any more; it is rebuilt by hand so that the
    runner's fail-closed lifecycle evidence path stays covered.
    """

    honest = _empty_right_nonunit()
    return TrackingResult(
        honest.tracks,
        tuple(
            event if event.frame == NONUNIT_SCHEDULE[0] else replace(event, frame=1)
            for event in honest.events
        ),
        honest.edges,
        honest.assignments,
    )


def _track(track_id, points, *, parents=(), children=(), unresolved=False) -> TrackRecord:
    return TrackRecord(
        track_id,
        tuple(TrackPoint(frame, component) for frame, component in points),
        parents,
        children,
        unresolved,
    )


def _event(frame, kind, sources=(), source_components=(), target_components=(), targets=(), resolved=True):
    return TrackEvent(frame, kind, sources, source_components, target_components, targets, resolved)


def _appearance(frame, track_id, component):
    return _event(frame, "APPEARANCE", target_components=((frame, component),), targets=(track_id,))


def _continuation(track_id, source, target):
    return _event(target[0], "CONTINUATION", (track_id,), (source,), (target,), (track_id,))


def _tracking(tracks, events) -> TrackingResult:
    assignments = tuple(
        (point.frame, point.component_index, track.track_id)
        for track in tracks
        for point in track.points
    )
    return TrackingResult(tracks, events, (), assignments)


def _silent_end_tracking() -> TrackingResult:
    """A track that stops before the horizon with no terminal event: zero terminal rows."""

    track = _track(0, ((0, 0),))
    return _tracking((track,), (_appearance(0, 0, 0),))


def _multiple_terminal_tracking() -> TrackingResult:
    """One track carrying two competing terminal events."""

    track = _track(0, ((0, 0),))
    events = (
        _appearance(0, 0, 0),
        _event(5, "DISSOLUTION", (0,), ((0, 0),), (), ()),
        _event(5, "TRACKING_UNRESOLVED", (0,), ((0, 0),), ((5, 1),), (1,), False),
    )
    return _tracking((track,), events)


def _one_invalid_track_tracking() -> TrackingResult:
    """Two tracks: one structurally valid to the horizon, one silently truncated."""

    good = _track(0, ((0, 0), (5, 0)))
    bad = _track(1, ((0, 1),))
    events = (
        _appearance(0, 0, 0),
        _continuation(0, (0, 0), (5, 0)),
        _appearance(0, 1, 1),
    )
    return _tracking((good, bad), events)


def _empty_track_set_tracking() -> TrackingResult:
    return TrackingResult((), (), (), ())


def _artifacts(directory: Path) -> tuple[bool, bool]:
    return (
        (directory / LIFECYCLE_DOCUMENT_NAME).exists(),
        (directory / COMPLETION_MANIFEST_NAME).exists(),
    )


def _leftovers(directory: Path) -> list[str]:
    return sorted(
        entry.name
        for entry in directory.iterdir()
        if entry.name not in {LIFECYCLE_DOCUMENT_NAME, COMPLETION_MANIFEST_NAME}
    )


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _read_manifest(directory: Path) -> dict:
    return json.loads((directory / COMPLETION_MANIFEST_NAME).read_bytes())


def _rewrite_manifest(directory: Path, manifest: dict) -> None:
    (directory / COMPLETION_MANIFEST_NAME).write_bytes(_canonical(manifest))


def _forged_manifest(document: bytes, closure: LifecycleRunClosure) -> dict:
    """A manifest an attacker can build unaided from a forged closure."""

    return {
        "canonicalization": {
            "encoding": "utf-8",
            "json_ensure_ascii": True,
            "json_nan_allowed": False,
            "json_separators": ",:",
            "json_sort_keys": True,
        },
        "disposition": "COMPLETE",
        "integration_version": INTEGRATION_VERSION,
        "lifecycle_document_relative_path": LIFECYCLE_DOCUMENT_NAME,
        "lifecycle_document_sha256": hashlib.sha256(document).hexdigest(),
        "lifecycle_input_sha256": closure.lifecycle_input_digest_sha256,
        "lifecycle_records_sha256": closure.records_digest_sha256,
        "lifecycle_schema_version": "future-lifecycle-contract/v1",
        "lifecycle_validator_version": "1.0.0",
        "sampled_frames": list(closure.sampled_frames),
        "schema_version": SCHEMA_VERSION,
        "terminal_record_count": len(closure.terminal_records),
    }


# --------------------------------------------------------------------------
# 1. positive path
# --------------------------------------------------------------------------


def test_01_real_generic_tracker_at_nonunit_cadence_publishes_completion(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)

    assert isinstance(record, CompletionRecord)
    assert record.state is RunnerState.COMPLETE_PUBLISHED
    assert record.sampled_frames == NONUNIT_SCHEDULE
    assert record.terminal_record_count == 1
    assert _artifacts(tmp_path) == (True, True)
    assert _leftovers(tmp_path) == []

    document = (tmp_path / LIFECYCLE_DOCUMENT_NAME).read_bytes()
    assert hashlib.sha256(document).hexdigest() == record.lifecycle_document_sha256
    assert json.loads(document)["terminal_records"][0]["terminal_state"] == "RIGHT_CENSORED_AT_HORIZON"

    access = open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert isinstance(access, AnalysisAccess)
    evidence = access.verified_completion_evidence()
    assert evidence["disposition"] == "COMPLETE"
    assert evidence["lifecycle_document_sha256"] == record.lifecycle_document_sha256


def test_01b_empty_track_set_run_publishes_explicit_closure(tmp_path: Path) -> None:
    tracking = _empty_track_set_tracking()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert record.terminal_record_count == 0
    assert json.loads((tmp_path / LIFECYCLE_DOCUMENT_NAME).read_bytes())["qualification"][
        "run_terminal_state"
    ] == "EMPTY_TRACK_SET"
    assert isinstance(open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE), AnalysisAccess)


# --------------------------------------------------------------------------
# 2-5. lifecycle validation failures block completion
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "factory", "expected_code"),
    (
        ("silent_end", _silent_end_tracking, "SILENT_PRE_HORIZON_TERMINATION"),
        ("multiple_terminals", _multiple_terminal_tracking, "MULTIPLE_TERMINAL_EVENTS"),
        ("one_invalid_track", _one_invalid_track_tracking, "SILENT_PRE_HORIZON_TERMINATION"),
    ),
)
def test_02_to_05_lifecycle_failure_blocks_completion(
    tmp_path: Path, name: str, factory, expected_code: str
) -> None:
    tracking = factory()
    with pytest.raises(LifecycleEvidenceError) as caught:
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert expected_code in str(caught.value)
    assert _artifacts(tmp_path) == (False, False)
    assert _leftovers(tmp_path) == []
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_05b_global_rejection_discards_the_valid_track_too(tmp_path: Path) -> None:
    """One invalid track rejects the complete run, including its valid sibling."""

    with pytest.raises(LifecycleEvidenceError):
        publish_future_family_completion(tmp_path, _one_invalid_track_tracking(), NONUNIT_SCHEDULE)
    assert _artifacts(tmp_path) == (False, False)


# --------------------------------------------------------------------------
# 6-13. on-disk evidence tampering blocks analysis
# --------------------------------------------------------------------------


def test_06_missing_lifecycle_file_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).unlink()
    with pytest.raises(CompletionEvidenceError, match="missing lifecycle document"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_07_tampered_lifecycle_bytes_block_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    document = json.loads((tmp_path / LIFECYCLE_DOCUMENT_NAME).read_bytes())
    document["terminal_records"][0]["terminal_state"] = "DISSOLVED_DETECTED_TRACK"
    tampered = _canonical(document)
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(tampered)
    manifest = _read_manifest(tmp_path)
    manifest["lifecycle_document_sha256"] = hashlib.sha256(tampered).hexdigest()
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(LifecycleEvidenceError, match="independent reverification"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_08_non_canonical_lifecycle_bytes_block_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    document = json.loads((tmp_path / LIFECYCLE_DOCUMENT_NAME).read_bytes())
    pretty = json.dumps(document, indent=2, sort_keys=True).encode("utf-8")
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(pretty)
    manifest = _read_manifest(tmp_path)
    manifest["lifecycle_document_sha256"] = hashlib.sha256(pretty).hexdigest()
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(LifecycleEvidenceError) as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert "DOCUMENT_NOT_CANONICAL" in str(caught.value)


def test_09_swapped_tracking_input_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    swapped = _tracking(
        (_track(0, ((0, 0),)),),
        (_appearance(0, 0, 0), _event(5, "DISSOLUTION", (0,), ((0, 0),), (), ())),
    )
    with pytest.raises(LifecycleEvidenceError) as caught:
        open_analysis_access(tmp_path, swapped, NONUNIT_SCHEDULE)
    assert "DOCUMENT_BINDING_MISMATCH" in str(caught.value)


def test_09b_binding_is_over_content_not_object_identity(tmp_path: Path) -> None:
    """Scope note: the binding is content-addressed.

    A different ``TrackingResult`` object carrying the *same* lifecycle content
    verifies, by design.  The gate proves the persisted document matches the
    supplied lifecycle input, not that the caller passed the same Python object.
    """

    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    equivalent = _tracking(
        (_track(0, ((0, 0), (5, 0))),),
        (_appearance(0, 0, 0), _continuation(0, (0, 0), (5, 0))),
    )
    assert equivalent is not tracking
    assert isinstance(
        open_analysis_access(tmp_path, equivalent, NONUNIT_SCHEDULE), AnalysisAccess
    )


def test_10_changed_sampling_schedule_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    with pytest.raises(RunnerIntegrationError):
        open_analysis_access(tmp_path, tracking, (0, 6))


def test_11_mismatched_lifecycle_digest_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    manifest["lifecycle_document_sha256"] = "0" * 64
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(CompletionEvidenceError, match="digest does not match"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_12_tampered_completion_manifest_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    manifest["terminal_record_count"] = 99
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(CompletionEvidenceError, match="bindings do not match"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_12b_tampered_manifest_disposition_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    manifest["disposition"] = "NOT_COMPLETE"
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(CompletionEvidenceError, match="does not declare COMPLETE"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_13_non_canonical_completion_manifest_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    )
    with pytest.raises(CompletionEvidenceError, match="not canonical"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_13b_manifest_key_set_mismatch_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    manifest["extra_key"] = "smuggled"
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(CompletionEvidenceError, match="key set mismatch"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


# --------------------------------------------------------------------------
# 14-16. forged in-memory objects and nominal dispositions cannot satisfy the gate
# --------------------------------------------------------------------------


def _forged_closure(frames=NONUNIT_SCHEDULE) -> LifecycleRunClosure:
    row = LifecycleTerminalRecord(
        0, frames[0], frames[-1], 0, frames[-1],
        "RIGHT_CENSORED_AT_HORIZON", "DECLARED_HORIZON", None, (), (), "RESOLVED",
    )
    return LifecycleRunClosure(
        sampled_frames=tuple(frames),
        lifecycle_input_digest_sha256="a" * 64,
        records_digest_sha256="b" * 64,
        track_count=1,
        event_count=0,
        assignment_count=0,
        terminal_records=(row,),
    )


def test_14_no_public_entry_point_accepts_a_lifecycle_closure() -> None:
    forbidden = ("LifecycleRunClosure", "LifecycleTerminalRecord",
                 "lifecycle_document", "disposition", "status", "closure")
    allowed_annotations = {
        "run_directory": "str | os.PathLike[str]",
        "tracking": "TrackingResult",
        "sampled_frames": "Sequence[int]",
    }
    for name in ("publish_future_family_completion", "open_analysis_access"):
        signature = inspect.signature(getattr(runner, name))
        assert set(signature.parameters) == set(allowed_annotations)
        for parameter in signature.parameters.values():
            annotation = str(parameter.annotation)
            assert annotation == allowed_annotations[parameter.name], (name, annotation)
            assert not any(token in annotation for token in forbidden), (name, annotation)
        assert signature.return_annotation in ("CompletionRecord", "AnalysisAccess")


def test_14b_hand_constructed_closure_cannot_satisfy_the_gate(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    closure = _forged_closure()
    document = canonical_lifecycle_bytes(closure)
    assert json.loads(document)["qualification"]["disposition"] == "QUALIFIED"
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(document)
    _rewrite_manifest(tmp_path, _forged_manifest(document, closure))
    with pytest.raises(LifecycleEvidenceError) as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert "DOCUMENT_BINDING_MISMATCH" in str(caught.value)


def test_15_hand_constructed_terminal_rows_cannot_satisfy_the_gate(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    genuine = publish_future_family_completion(tmp_path / _make(tmp_path), tracking, NONUNIT_SCHEDULE)
    victim = tmp_path / "victim"
    victim.mkdir()
    document = json.loads(
        (Path(genuine.run_directory) / LIFECYCLE_DOCUMENT_NAME).read_bytes()
    )
    document["terminal_records"].append(dict(document["terminal_records"][0], track_id=1))
    document["lifecycle_binding"]["terminal_record_count"] = 2
    forged_bytes = _canonical(document)
    (victim / LIFECYCLE_DOCUMENT_NAME).write_bytes(forged_bytes)
    manifest = _read_manifest(Path(genuine.run_directory))
    manifest["lifecycle_document_sha256"] = hashlib.sha256(forged_bytes).hexdigest()
    manifest["terminal_record_count"] = 2
    _rewrite_manifest(victim, manifest)
    with pytest.raises(LifecycleEvidenceError):
        open_analysis_access(victim, tracking, NONUNIT_SCHEDULE)


def _make(root: Path) -> str:
    (root / "genuine").mkdir()
    return "genuine"


def test_16_nominal_qualified_disposition_cannot_satisfy_the_gate(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    hand_written = {
        "lifecycle_binding": {"records_sha256": "c" * 64, "terminal_record_count": 1},
        "qualification": {
            "all_tracks_closed": True,
            "disposition": "QUALIFIED",
            "run_terminal_state": "ALL_TRACKS_CLOSED",
        },
        "sampled_frames": [0, 5],
        "schema_version": "future-lifecycle-contract/v1",
        "source_binding": {
            "assignment_count": 0,
            "event_count": 0,
            "lifecycle_input_sha256": "d" * 64,
            "track_count": 1,
        },
        "terminal_records": [],
        "validator_version": "1.0.0",
    }
    document = _canonical(hand_written)
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(document)
    manifest = {
        "canonicalization": {
            "encoding": "utf-8",
            "json_ensure_ascii": True,
            "json_nan_allowed": False,
            "json_separators": ",:",
            "json_sort_keys": True,
        },
        "disposition": "COMPLETE",
        "integration_version": INTEGRATION_VERSION,
        "lifecycle_document_relative_path": LIFECYCLE_DOCUMENT_NAME,
        "lifecycle_document_sha256": hashlib.sha256(document).hexdigest(),
        "lifecycle_input_sha256": "d" * 64,
        "lifecycle_records_sha256": "c" * 64,
        "lifecycle_schema_version": "future-lifecycle-contract/v1",
        "lifecycle_validator_version": "1.0.0",
        "sampled_frames": [0, 5],
        "schema_version": SCHEMA_VERSION,
        "terminal_record_count": 1,
    }
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(LifecycleEvidenceError):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_16b_analysis_access_cannot_be_constructed_directly() -> None:
    with pytest.raises(CompletionEvidenceError, match="cannot be constructed directly"):
        AnalysisAccess(object(), {"disposition": "COMPLETE"})


# --------------------------------------------------------------------------
# 17-20. failure semantics and ordering
# --------------------------------------------------------------------------


def test_17_persistence_exception_leaves_no_completion_manifest(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(b"pre-existing")
    with pytest.raises(LifecycleEvidenceError, match="existing lifecycle document"):
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert (tmp_path / LIFECYCLE_DOCUMENT_NAME).read_bytes() == b"pre-existing"
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()


def test_17b_missing_run_directory_is_refused(tmp_path: Path) -> None:
    with pytest.raises(CompletionPublicationError, match="run_directory must already exist"):
        publish_future_family_completion(tmp_path / "absent", _real_tracker_nonunit(), NONUNIT_SCHEDULE)
    with pytest.raises(CompletionEvidenceError, match="run_directory must already exist"):
        open_analysis_access(tmp_path / "absent", _real_tracker_nonunit(), NONUNIT_SCHEDULE)


def test_18_verification_exception_leaves_no_completion_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tracking = _real_tracker_nonunit()
    monkeypatch.setattr(runner, "_read_exact_bytes", lambda path: b'{"corrupted":true}')
    with pytest.raises(LifecycleEvidenceError, match="read-back verification"):
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    monkeypatch.undo()
    assert (tmp_path / LIFECYCLE_DOCUMENT_NAME).exists()
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()
    assert _leftovers(tmp_path) == []
    with pytest.raises(CompletionEvidenceError, match="analysis access remains locked"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_19_existing_completion_target_is_never_overwritten(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    sentinel = b"pre-existing completion evidence"
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(sentinel)
    with pytest.raises(CompletionPublicationError, match="existing completion manifest"):
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert (tmp_path / COMPLETION_MANIFEST_NAME).read_bytes() == sentinel
    assert not (tmp_path / LIFECYCLE_DOCUMENT_NAME).exists()


def test_19b_republishing_into_a_completed_directory_is_refused(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    before = (tmp_path / COMPLETION_MANIFEST_NAME).read_bytes()
    with pytest.raises(CompletionPublicationError):
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert (tmp_path / COMPLETION_MANIFEST_NAME).read_bytes() == before


def test_20_lifecycle_document_alone_does_not_unlock_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    qualify_and_write_lifecycle_contract(
        tmp_path / LIFECYCLE_DOCUMENT_NAME, tracking, NONUNIT_SCHEDULE
    )
    assert (tmp_path / LIFECYCLE_DOCUMENT_NAME).exists()
    with pytest.raises(CompletionEvidenceError, match="analysis access remains locked"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


def test_20b_state_machine_transitions_are_monotonic() -> None:
    progress = runner._Progress()
    assert progress.state is RunnerState.UNSTARTED
    with pytest.raises(RunnerIntegrationError, match="illegal completion transition"):
        progress.advance(RunnerState.COMPLETE_PUBLISHED)
    progress.advance(RunnerState.LIFECYCLE_PERSISTED)
    with pytest.raises(RunnerIntegrationError):
        progress.advance(RunnerState.LIFECYCLE_PERSISTED)
    progress.advance(RunnerState.LIFECYCLE_VERIFIED)
    progress.advance(RunnerState.COMPLETE_PUBLISHED)
    assert progress.state is RunnerState.COMPLETE_PUBLISHED


def test_20c_completion_record_is_inert_and_frozen(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    with pytest.raises(FrozenInstanceError):
        record.state = RunnerState.UNSTARTED  # type: ignore[misc]
    assert not hasattr(record, "verified_completion_evidence")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(elsewhere, tracking, NONUNIT_SCHEDULE)


# --------------------------------------------------------------------------
# 21. the cadence limitation is lifted; the guard behind it is not
# --------------------------------------------------------------------------


def test_21_empty_right_frame_at_nonunit_cadence_now_publishes(tmp_path: Path) -> None:
    """01R supersedes ``test_21_empty_right_frame_at_nonunit_cadence_remains_rejected``.

    With the schedule mandatory the disappearance is bound to the declared frame, so
    the run is published with the disappearance retained as terminal information
    instead of being discarded by a global rejection.
    """

    tracking = _empty_right_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert _artifacts(tmp_path) == (True, True)
    document = json.loads((tmp_path / LIFECYCLE_DOCUMENT_NAME).read_text(encoding="utf-8"))
    states = [row["terminal_state"] for row in document["terminal_records"]]
    assert states == ["DISSOLVED_DETECTED_TRACK"]
    assert document["terminal_records"][0]["terminal_frame"] == 5
    assert record.state is RunnerState.COMPLETE_PUBLISHED
    access = open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert isinstance(access, AnalysisAccess)


def test_21b_a_fabricated_off_schedule_frame_is_still_refused(tmp_path: Path) -> None:
    """The runner's fail-closed lifecycle evidence path must stay live.

    The tracker can no longer produce off-schedule frames, so this input is
    handcrafted; the runner must still refuse it and write nothing.
    """

    tracking = _fabricated_off_schedule()
    with pytest.raises(LifecycleEvidenceError) as caught:
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    message = str(caught.value)
    assert "INVALID_EVENT_FRAME" in message
    assert "SILENT_PRE_HORIZON_TERMINATION" in message
    assert _artifacts(tmp_path) == (False, False)
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


# --------------------------------------------------------------------------
# 22. supported API surface
# --------------------------------------------------------------------------


def test_22_no_public_api_exposes_an_unchecked_completion_emitter() -> None:
    assert set(runner.__all__) == {
        "COMPLETION_MANIFEST_NAME",
        "INTEGRATION_VERSION",
        "LIFECYCLE_DOCUMENT_NAME",
        "SCHEMA_VERSION",
        "AnalysisAccess",
        "CompletionEvidenceError",
        "CompletionPublicationError",
        "CompletionRecord",
        "LifecycleEvidenceError",
        "RunnerIntegrationError",
        "RunnerState",
        "open_analysis_access",
        "publish_future_family_completion",
    }
    banned = ("emit", "mark", "force", "skip", "unsafe", "override", "bypass", "_ok", "trust")
    for name in runner.__all__:
        assert not any(token in name.lower() for token in banned), name
    functions = sorted(
        name for name in runner.__all__ if inspect.isfunction(getattr(runner, name))
    )
    assert functions == ["open_analysis_access", "publish_future_family_completion"]
    assert "future_lifecycle_runner" not in getattr(
        __import__("edlab.substrates.lattice_bond", fromlist=["__all__"]), "__all__"
    )


# --------------------------------------------------------------------------
# 23. historical / current lineage
#
# MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01R replaces the former
# current-tree hash tripwire (``test_23_bound_lifecycle_package_remains_byte_identical``).
# That tripwire pinned the CURRENT tree to the digests recorded by the historical
# FUTURE-LIFECYCLE-CONTRACT-00 qualification, so any authorized change to the tracker
# made it fail.  Overwriting its expected digest would have destroyed the evidence it
# carries.  Instead the pin is split in two: the historical package keeps its own
# digests and must stay byte-identical, and the current tree is pinned to the
# SUCCESSOR qualification.  The two are then asserted to differ, in exactly one file,
# for exactly one authorized reason.
# --------------------------------------------------------------------------

HISTORICAL_PACKAGE_DIGESTS = {
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SCHEMA.json":
        "629bfdc3e6d3017948ad1b07472bea881419c86ea9fa283494a418f27913966c",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SOURCE_ALLOWLIST.json":
        "d8743e1f2eb98de610df22d67059ce1132472e8eea405faf7b91ed4c9bb8253a",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SPEC.md":
        "81c5af7cd91b9a780d560b7b7bed52b80b56348e29499c385b696a25e8686974",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_REPORT.md":
        "8015262ae4e1f49713ab422e7aa059a39081d058510fffd884dedac4344e2d16",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json":
        "8f423bb0f0ece04a3e576b76cb2c7704d5edf6c82c827110bd5608e8e5514ece",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md":
        "f1d082e37ca036f516ad22e20a30d0148e6f97d5997999b9a3f90f20f8af4864",
}

HISTORICAL_TRACKER_SHA256 = "f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88"
MANDATORY_TRACKER_SHA256 = "65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef"
UNCHANGED_LIFECYCLE_SHA256 = "3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053"

SUCCESSOR_QUALIFICATION = (
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json"
)
HISTORICAL_QUALIFICATION = "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_23a_historical_package_documents_remain_byte_identical() -> None:
    """The historical 00 package is immutable and stays historically valid."""

    root = Path(__file__).resolve().parents[1]
    for relative, digest in HISTORICAL_PACKAGE_DIGESTS.items():
        assert _digest(root / relative) == digest, relative


def test_23b_historical_qualification_still_records_the_historical_tracker_hash() -> None:
    root = Path(__file__).resolve().parents[1]
    historical = json.loads((root / HISTORICAL_QUALIFICATION).read_text(encoding="utf-8"))
    recorded = historical["source_hashes_sha256"]
    assert recorded["edlab/substrates/lattice_bond/instrumentation.py"] == HISTORICAL_TRACKER_SHA256
    assert recorded["edlab/substrates/lattice_bond/lifecycle.py"] == UNCHANGED_LIFECYCLE_SHA256


def test_23c_successor_qualification_records_the_repaired_mandatory_tracker_hash() -> None:
    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    recorded = successor["source_hashes_sha256"]
    assert recorded["edlab/substrates/lattice_bond/instrumentation.py"] == MANDATORY_TRACKER_SHA256
    assert recorded["edlab/substrates/lattice_bond/lifecycle.py"] == UNCHANGED_LIFECYCLE_SHA256


def test_23d_the_two_tracker_hashes_differ_for_the_authorized_reason() -> None:
    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    lineage = successor["lineage"]
    assert HISTORICAL_TRACKER_SHA256 != MANDATORY_TRACKER_SHA256
    assert lineage["historical_tracker_sha256"] == HISTORICAL_TRACKER_SHA256
    assert lineage["mandatory_tracker_sha256"] == MANDATORY_TRACKER_SHA256
    assert lineage["tracker_hash_change_reason"] == "MANDATORY_SAMPLED_FRAMES_SCHEDULE"
    assert lineage["historical_package"] == "FUTURE-LIFECYCLE-CONTRACT-00"
    assert lineage["historical_package_remains_valid"] is True


def test_23e_lifecycle_source_is_unchanged_across_the_succession() -> None:
    root = Path(__file__).resolve().parents[1]
    observed = _digest(root / "edlab/substrates/lattice_bond/lifecycle.py")
    assert observed == UNCHANGED_LIFECYCLE_SHA256
    historical = json.loads((root / HISTORICAL_QUALIFICATION).read_text(encoding="utf-8"))
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    key = "edlab/substrates/lattice_bond/lifecycle.py"
    assert historical["source_hashes_sha256"][key] == successor["source_hashes_sha256"][key]


def test_23f_current_source_matches_the_successor_qualification() -> None:
    """The current tree is pinned to the successor package, not to the historical one."""

    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    for relative, digest in successor["source_hashes_sha256"].items():
        assert _digest(root / relative) == digest, relative
    # Every test file the successor binds is checked here EXCEPT this one: a file
    # cannot contain the digest of its own final bytes.  Its digest is recorded in the
    # successor qualification and verified out of band at seal time.
    own = "tests/test_future_lifecycle_runner_integration.py"
    assert own in successor["test_hashes_sha256"], "this file must still be bound"
    for relative, digest in successor["test_hashes_sha256"].items():
        if relative == own:
            continue
        assert _digest(root / relative) == digest, relative


def test_23g_runner_integration_remains_pending_formal_requalification() -> None:
    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    assert successor["runner_integration"]["status"] == "PENDING_FORMAL_REQUALIFICATION"
    assert successor["runner_integration"]["requalified_by_this_mission"] is False
    assert successor["claim_boundary"]["not_qualified"], "the boundary must not be empty"
    assert any(
        "runner integration" in item.lower()
        for item in successor["claim_boundary"]["not_qualified"]
    )
    # the historical runner-integration package is untouched by this mission
    assert _digest(
        root / "edlab/substrates/lattice_bond/future_lifecycle_runner.py"
    ) == successor["lineage"]["unchanged_runner_sha256"]


HISTORICALLY_PINNED_ARTIFACTS = {
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SCHEMA.json":
        "629bfdc3e6d3017948ad1b07472bea881419c86ea9fa283494a418f27913966c",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SOURCE_ALLOWLIST.json":
        "d8743e1f2eb98de610df22d67059ce1132472e8eea405faf7b91ed4c9bb8253a",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SPEC.md":
        "81c5af7cd91b9a780d560b7b7bed52b80b56348e29499c385b696a25e8686974",
    "edlab/substrates/lattice_bond/__init__.py":
        "9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0",
    "edlab/substrates/lattice_bond/instrumentation.py":
        "f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88",
    "edlab/substrates/lattice_bond/lifecycle.py":
        "3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053",
    "tests/test_future_lifecycle_contract.py":
        "e940199e7befaf7e60535867525d163e3abc807a951265c78a5f7b1d0acddd47",
}


def test_23i_every_historically_pinned_artifact_is_explicitly_accounted_for() -> None:
    """Reviewer B, OBS-1: the deleted tripwire pinned SEVEN artifacts, and more than one
    of them has moved.  Each must be either byte-identical today, or declared divergent
    in the successor qualification with both digests — never silently different.
    """

    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    divergent = successor["lineage"]["divergent_from_historical_pin"]
    assert set(HISTORICALLY_PINNED_ARTIFACTS) == set(
        successor["lineage"]["historically_pinned_artifacts"]
    )
    for relative, historical in HISTORICALLY_PINNED_ARTIFACTS.items():
        observed = _digest(root / relative)
        if observed == historical:
            assert relative not in divergent, f"{relative} is identical but declared divergent"
            continue
        assert relative in divergent, f"{relative} diverged without being declared"
        assert divergent[relative]["historical_sha256"] == historical
        assert divergent[relative]["current_sha256"] == observed
        assert divergent[relative]["reason"]
    assert divergent, "the divergence set must not be silently empty"


def test_23h_the_bound_test_node_list_is_complete_and_unaltered() -> None:
    """A test cannot be quietly dropped from the successor qualification.

    Re-collects the four bound selectors and compares the canonical node-list digest
    with the one the successor qualification records.  Collection only: no test is
    executed, so this cannot recurse.
    """

    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    successor = json.loads((root / SUCCESSOR_QUALIFICATION).read_text(encoding="utf-8"))
    binding = successor["test_binding"]
    selectors = list(binding["selectors"])
    assert selectors == [
        "tests/test_empty_right_nonunit_cadence_tracker_repair.py",
        "tests/test_future_lifecycle_contract.py",
        "tests/test_future_lifecycle_runner_integration.py",
        "tests/test_lattice_bond_instrumentation.py",
    ]
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header",
         "-p", "no:cacheprovider", *selectors],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    collected = sorted(
        line.strip()
        for line in completed.stdout.splitlines()
        if "::" in line and line.strip().startswith("tests/")
    )
    digest = hashlib.sha256("\n".join(collected).encode("utf-8")).hexdigest()
    assert collected == sorted(binding["node_ids"]), "collected node list differs"
    assert len(collected) == binding["node_count"]
    assert digest == binding["node_list_sha256"]


# --------------------------------------------------------------------------
# 24. determinism
# --------------------------------------------------------------------------


def test_24_identical_inputs_produce_byte_identical_completion_evidence(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    publish_future_family_completion(first, tracking, NONUNIT_SCHEDULE)
    publish_future_family_completion(second, tracking, NONUNIT_SCHEDULE)
    assert (first / COMPLETION_MANIFEST_NAME).read_bytes() == (
        second / COMPLETION_MANIFEST_NAME
    ).read_bytes()
    assert (first / LIFECYCLE_DOCUMENT_NAME).read_bytes() == (
        second / LIFECYCLE_DOCUMENT_NAME
    ).read_bytes()


# --------------------------------------------------------------------------
# white-box coverage of the defensive publication and evidence branches
# --------------------------------------------------------------------------


def test_25_publication_refuses_missing_parent_and_existing_target(tmp_path: Path) -> None:
    with pytest.raises(CompletionPublicationError, match="parent must already exist"):
        runner._publish_new_canonical_file(tmp_path / "absent" / "x.json", b"{}")
    target = tmp_path / "x.json"
    target.write_bytes(b"sentinel")
    with pytest.raises(CompletionPublicationError, match="existing completion manifest"):
        runner._publish_new_canonical_file(target, b"{}")
    assert target.read_bytes() == b"sentinel"


def test_26_concurrent_creation_is_refused_and_partial_is_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def racing_link(source, destination):
        raise FileExistsError(destination)

    monkeypatch.setattr(runner.os, "link", racing_link)
    with pytest.raises(CompletionPublicationError, match="concurrent"):
        runner._publish_new_canonical_file(tmp_path / "x.json", b"{}")
    assert sorted(entry.name for entry in tmp_path.iterdir()) == []


def test_27_vanished_partial_during_cleanup_is_tolerated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def vanishing_link(source, destination):
        os.unlink(source)
        raise FileExistsError(destination)

    monkeypatch.setattr(runner.os, "link", vanishing_link)
    with pytest.raises(CompletionPublicationError, match="concurrent"):
        runner._publish_new_canonical_file(tmp_path / "x.json", b"{}")
    assert sorted(entry.name for entry in tmp_path.iterdir()) == []


def test_28_substituted_publication_target_is_rejected_and_not_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def substituting_link(source, destination):
        Path(destination).write_bytes(b"substituted")

    monkeypatch.setattr(runner.os, "link", substituting_link)
    with pytest.raises(CompletionPublicationError, match="identity or canonical bytes changed"):
        runner._publish_new_canonical_file(tmp_path / "x.json", b"{}")
    assert (tmp_path / "x.json").read_bytes() == b"substituted"
    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["x.json"]


def test_29_failure_before_ownership_leaves_no_owned_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_fdopen(descriptor, mode):
        os.close(descriptor)
        raise OSError("cannot open descriptor")

    monkeypatch.setattr(runner.os, "fdopen", failing_fdopen)
    with pytest.raises(OSError, match="cannot open descriptor"):
        runner._publish_new_canonical_file(tmp_path / "x.json", b"{}")
    assert not (tmp_path / "x.json").exists()


def test_30_noncanonical_persisted_bytes_block_completion_and_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tracking = _real_tracker_nonunit()
    monkeypatch.setattr(runner, "canonical_lifecycle_bytes", lambda contract: b"different")
    with pytest.raises(LifecycleEvidenceError, match="not the canonical bytes"):
        publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()

    monkeypatch.undo()
    complete = tmp_path / "complete"
    complete.mkdir()
    publish_future_family_completion(complete, tracking, NONUNIT_SCHEDULE)
    monkeypatch.setattr(runner, "canonical_lifecycle_bytes", lambda contract: b"different")
    with pytest.raises(LifecycleEvidenceError, match="not the canonical bytes"):
        open_analysis_access(complete, tracking, NONUNIT_SCHEDULE)


def test_31_malformed_completion_manifest_blocks_analysis(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(b"{not json")
    with pytest.raises(CompletionEvidenceError, match="not valid JSON"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(b"[]")
    with pytest.raises(CompletionEvidenceError, match="must be a JSON object"):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


@pytest.mark.parametrize(
    ("key", "value", "message"),
    (
        ("schema_version", "other/v9", "unsupported completion manifest schema version"),
        ("integration_version", "9.9.9", "unsupported integration version"),
        ("lifecycle_schema_version", "other/v9", "unsupported lifecycle schema version"),
        ("lifecycle_validator_version", "9.9.9", "unsupported lifecycle validator version"),
        ("canonicalization", {"encoding": "utf-16"}, "canonicalization declaration mismatch"),
        ("lifecycle_document_relative_path", "OTHER.json", "unsupported lifecycle document identity"),
    ),
)
def test_32_declared_manifest_fields_must_match(tmp_path: Path, key, value, message) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    manifest[key] = value
    _rewrite_manifest(tmp_path, manifest)
    with pytest.raises(CompletionEvidenceError, match=message):
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)


# --------------------------------------------------------------------------
# review fixes: the atomic publisher must be proven wired into the gate
# --------------------------------------------------------------------------


class _PlantingTracking:
    """A tracking input that plants a rival COMPLETION.json mid-publication.

    The plant happens *after* the pre-flight existence check and *before* the
    manifest is written, which is exactly the window a non-atomic writer would
    silently clobber.
    """

    def __init__(self, inner: TrackingResult, directory: Path, payload: bytes) -> None:
        self._inner = inner
        self._directory = directory
        self._payload = payload
        self.planted = False

    @property
    def tracks(self):
        if not self.planted:
            self.planted = True
            (self._directory / COMPLETION_MANIFEST_NAME).write_bytes(self._payload)
        return self._inner.tracks

    @property
    def events(self):
        return self._inner.events

    @property
    def edges(self):
        return self._inner.edges

    @property
    def assignments(self):
        return self._inner.assignments


def test_33_completion_published_mid_flight_is_never_clobbered(tmp_path: Path) -> None:
    """The supported path must route through the atomic non-overwriting writer.

    Without that routing this test fails: a plain write would destroy the rival
    manifest that appeared after the pre-flight check.
    """

    sentinel = b"rival completion evidence"
    hostile = _PlantingTracking(_real_tracker_nonunit(), tmp_path, sentinel)
    with pytest.raises(CompletionPublicationError, match="existing completion manifest"):
        publish_future_family_completion(tmp_path, hostile, NONUNIT_SCHEDULE)
    assert hostile.planted
    assert (tmp_path / COMPLETION_MANIFEST_NAME).read_bytes() == sentinel
    assert _leftovers(tmp_path) == []
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(tmp_path, _real_tracker_nonunit(), NONUNIT_SCHEDULE)


def test_34_non_finite_manifest_numbers_stay_inside_the_error_hierarchy(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    raw = (tmp_path / COMPLETION_MANIFEST_NAME).read_bytes().decode("utf-8")
    poisoned = raw.replace('"terminal_record_count":1', '"terminal_record_count":NaN')
    assert poisoned != raw
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(poisoned.encode("utf-8"))
    with pytest.raises(RunnerIntegrationError) as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert isinstance(caught.value, CompletionEvidenceError)
    assert "not canonically representable" in str(caught.value)


def test_35_returned_evidence_is_a_deep_copy(tmp_path: Path) -> None:
    tracking = _real_tracker_nonunit()
    publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    access = open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    evidence = access.verified_completion_evidence()
    evidence["disposition"] = "TAMPERED"
    evidence["canonicalization"]["encoding"] = "utf-16"
    evidence["sampled_frames"].append(99)
    fresh = access.verified_completion_evidence()
    assert fresh["disposition"] == "COMPLETE"
    assert fresh["canonicalization"]["encoding"] == "utf-8"
    assert fresh["sampled_frames"] == list(NONUNIT_SCHEDULE)
    assert runner._CANONICALIZATION["encoding"] == "utf-8"


def test_36_filesystem_errors_from_the_frozen_writer_stay_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A filesystem without hard links must not leak a bare OSError."""

    import edlab.substrates.lattice_bond.lifecycle as lifecycle

    def unlinkable(source, destination):
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(lifecycle.os, "link", unlinkable)
    with pytest.raises(RunnerIntegrationError) as caught:
        publish_future_family_completion(tmp_path, _real_tracker_nonunit(), NONUNIT_SCHEDULE)
    assert isinstance(caught.value, LifecycleEvidenceError)
    assert isinstance(caught.value.__cause__, OSError)
    monkeypatch.undo()
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(tmp_path, _real_tracker_nonunit(), NONUNIT_SCHEDULE)


# --------------------------------------------------------------------------
# 12. FUTURE-LIFECYCLE-RUNNER-HARDENING-00 — MIN-2 manifest-binding regressions
#
# Each case tampers with exactly one semantically meaningful manifest field,
# keeps the replacement structurally well formed and canonically serialised,
# and proves that analysis access fails closed at the rebuilt-manifest binding
# comparison rather than at any earlier syntactic or shape check.
# --------------------------------------------------------------------------


_ALTERNATE_INPUT_DIGEST = "a1" * 32
_ALTERNATE_RECORDS_DIGEST = "b2" * 32
_ALTERNATE_SCHEDULE = [0, 6]


def _assert_well_formed_digest(value: object) -> None:
    assert isinstance(value, str)
    assert len(value) == 64
    assert all(character in "0123456789abcdef" for character in value)


def _assert_reaches_binding_comparison(directory: Path, manifest: dict) -> None:
    """The tampered manifest must survive every check that precedes the binding.

    If any earlier guard fired, the test would prove nothing about the binding
    comparison, so the preconditions are asserted explicitly.
    """

    raw = (directory / COMPLETION_MANIFEST_NAME).read_bytes()
    assert raw == _canonical(manifest), "tampered manifest must remain canonical bytes"
    assert json.loads(raw) == manifest
    assert set(manifest) == set(runner._MANIFEST_KEYS)
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["integration_version"] == INTEGRATION_VERSION
    assert manifest["lifecycle_schema_version"] == runner.LIFECYCLE_SCHEMA_VERSION
    assert manifest["lifecycle_validator_version"] == runner.LIFECYCLE_VALIDATOR_VERSION
    assert manifest["canonicalization"] == runner._CANONICALIZATION
    assert manifest["disposition"] == "COMPLETE"
    assert manifest["lifecycle_document_relative_path"] == LIFECYCLE_DOCUMENT_NAME
    document = (directory / LIFECYCLE_DOCUMENT_NAME).read_bytes()
    assert hashlib.sha256(document).hexdigest() == manifest["lifecycle_document_sha256"]


def test_37_tampered_lifecycle_input_digest_blocks_analysis(tmp_path: Path) -> None:
    """MIN-2 A: a well-formed but wrong ``lifecycle_input_sha256`` must fail closed."""

    tracking = _real_tracker_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    original = manifest["lifecycle_input_sha256"]
    assert original == record.lifecycle_input_sha256
    assert original != _ALTERNATE_INPUT_DIGEST
    manifest["lifecycle_input_sha256"] = _ALTERNATE_INPUT_DIGEST
    _rewrite_manifest(tmp_path, manifest)
    _assert_well_formed_digest(manifest["lifecycle_input_sha256"])
    _assert_reaches_binding_comparison(tmp_path, manifest)
    assert manifest["lifecycle_records_sha256"] == record.lifecycle_records_sha256
    assert manifest["sampled_frames"] == list(NONUNIT_SCHEDULE)
    assert manifest["terminal_record_count"] == record.terminal_record_count

    with pytest.raises(CompletionEvidenceError, match="bindings do not match") as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert not isinstance(caught.value, LifecycleEvidenceError)


def test_38_tampered_lifecycle_records_digest_blocks_analysis(tmp_path: Path) -> None:
    """MIN-2 B: a well-formed but wrong ``lifecycle_records_sha256`` must fail closed."""

    tracking = _real_tracker_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    original = manifest["lifecycle_records_sha256"]
    assert original == record.lifecycle_records_sha256
    assert original != _ALTERNATE_RECORDS_DIGEST
    manifest["lifecycle_records_sha256"] = _ALTERNATE_RECORDS_DIGEST
    _rewrite_manifest(tmp_path, manifest)
    _assert_well_formed_digest(manifest["lifecycle_records_sha256"])
    _assert_reaches_binding_comparison(tmp_path, manifest)
    assert manifest["lifecycle_input_sha256"] == record.lifecycle_input_sha256
    assert manifest["sampled_frames"] == list(NONUNIT_SCHEDULE)
    assert manifest["terminal_record_count"] == record.terminal_record_count

    with pytest.raises(CompletionEvidenceError, match="bindings do not match") as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert not isinstance(caught.value, LifecycleEvidenceError)


def test_39_tampered_manifest_sampling_schedule_blocks_analysis(tmp_path: Path) -> None:
    """MIN-2 C: a valid but different ``sampled_frames`` schedule must fail closed."""

    tracking = _real_tracker_nonunit()
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)
    manifest = _read_manifest(tmp_path)
    assert manifest["sampled_frames"] == list(NONUNIT_SCHEDULE)
    assert _ALTERNATE_SCHEDULE != list(NONUNIT_SCHEDULE)
    manifest["sampled_frames"] = list(_ALTERNATE_SCHEDULE)
    _rewrite_manifest(tmp_path, manifest)

    schedule = manifest["sampled_frames"]
    assert isinstance(schedule, list) and len(schedule) == len(NONUNIT_SCHEDULE)
    assert all(isinstance(frame, int) and frame >= 0 for frame in schedule)
    assert all(later > earlier for earlier, later in zip(schedule, schedule[1:]))
    _assert_reaches_binding_comparison(tmp_path, manifest)
    assert manifest["lifecycle_input_sha256"] == record.lifecycle_input_sha256
    assert manifest["lifecycle_records_sha256"] == record.lifecycle_records_sha256
    assert manifest["terminal_record_count"] == record.terminal_record_count

    with pytest.raises(CompletionEvidenceError, match="bindings do not match") as caught:
        open_analysis_access(tmp_path, tracking, NONUNIT_SCHEDULE)
    assert not isinstance(caught.value, LifecycleEvidenceError)
