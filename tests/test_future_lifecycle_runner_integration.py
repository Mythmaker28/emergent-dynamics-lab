"""Adversarial qualification of the future-family lifecycle runner integration.

Synthetic fixtures only.  No engine, no historical family, no scientific value.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
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

    return track_components(((_component(0),), (_component(5),)), TRACKER)


def _empty_right_nonunit() -> TrackingResult:
    """Real generic tracker output with an empty right frame: known to be rejected."""

    return track_components(((_component(0),), ()), TRACKER)


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
# 21. retained cadence limitation
# --------------------------------------------------------------------------


def test_21_empty_right_frame_at_nonunit_cadence_remains_rejected(tmp_path: Path) -> None:
    tracking = _empty_right_nonunit()
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
# 23. the bound lifecycle package is untouched
# --------------------------------------------------------------------------


def test_23_bound_lifecycle_package_remains_byte_identical() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = {
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
    for relative, digest in expected.items():
        observed = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        assert observed == digest, relative


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
