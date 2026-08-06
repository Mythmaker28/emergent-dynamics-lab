"""FUTURE-LIFECYCLE-OWNED-PIPELINE-RUNNER-00 — successor tests.

Every fixture here is a handcrafted synthetic boolean mask pushed through the real
detector, the mandatory tracker, the frozen lifecycle validator and the qualified
completion gate by the owned pipeline itself.  There is no scientific input, no engine
step, no real runner and no seed.

The point of this suite is ownership: the pipeline must *perform* acquisition, record
it, persist it, forget it, read it back, reverify it and only then track, qualify,
publish and unlock.  Tests are therefore written to attack the seam between what was
declared and what was actually done.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil

import numpy as np
import pytest

from edlab.substrates.lattice_bond import DetectorSpec, TrackerSpec
from edlab.substrates.lattice_bond.future_lifecycle_runner import (
    COMPLETION_MANIFEST_NAME,
    LIFECYCLE_DOCUMENT_NAME,
    AnalysisAccess,
)
from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    ACQUISITION_LEDGER_NAME,
    OWNED_BINDING_NAME,
    OwnedAcquisitionError,
    OwnedEvidenceError,
    OwnedPipelineError,
    OwnedPipelineState,
    OwnedPublicationError,
    OwnedScheduleError,
    open_owned_analysis_access,
    run_owned_future_pipeline,
)

SHAPE = (10, 12)
DETECTOR = DetectorSpec(matter_threshold=0.5, min_cells=1)
TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=4.0, dilation_radius=1)
NONUNIT_SCHEDULE = (0, 5, 11, 12)
UNIT_SCHEDULE = (0, 1, 2, 3)
IDENTITY = {"kind": "handcrafted-synthetic-mask", "name": "owned-pipeline-fixture"}


def _mask(cells) -> np.ndarray:
    value = np.zeros(SHAPE, dtype=bool)
    for y, x in cells:
        value[y, x] = True
    return value


EMPTY = np.zeros(SHAPE, dtype=bool)
BLOB_A = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
BLOB_A_SHIFTED = _mask({(3, 4), (3, 5), (4, 4), (4, 5)})
BLOB_B = _mask({(8, 9), (8, 10), (9, 9), (9, 10)})


class RecordingSource:
    """A synthetic acquisition source that records every invocation it receives."""

    def __init__(self, frames, *, side_effect=None) -> None:
        self._frames = list(frames)
        self._side_effect = side_effect
        self.calls: list[tuple[int, int]] = []

    def __call__(self, position: int, label: int) -> np.ndarray:
        self.calls.append((position, label))
        if self._side_effect is not None:
            self._side_effect(self, position, label)
        return self._frames[position]


def _run(directory, source, schedule=NONUNIT_SCHEDULE, *, detector=DETECTOR, tracker=TRACKER):
    return run_owned_future_pipeline(
        directory,
        acquisition_source=source,
        sampled_frames=schedule,
        detector_spec=detector,
        tracker_spec=tracker,
        acquisition_source_identity=IDENTITY,
    )


def _disappearance_source() -> RecordingSource:
    """A -> gone -> B -> B at declared cadence (0, 5, 11, 12)."""

    return RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B])


def _artifacts(directory: Path) -> tuple[bool, bool, bool]:
    return (
        (directory / ACQUISITION_LEDGER_NAME).exists(),
        (directory / COMPLETION_MANIFEST_NAME).exists(),
        (directory / OWNED_BINDING_NAME).exists(),
    )


def _canonical(value) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read(directory: Path, name: str):
    return json.loads((directory / name).read_bytes())


def _write(directory: Path, name: str, value) -> None:
    (directory / name).write_bytes(_canonical(value))


def _repin(directory: Path, **updates) -> None:
    """Rewrite the owned binding so a tamper is *not* caught by a mere digest check.

    Used to force a tamper past the owned pipeline's own bookkeeping and down onto the
    semantic checks: the re-derived tracking, the lifecycle validator and the qualified
    completion gate.
    """

    binding = _read(directory, OWNED_BINDING_NAME)
    binding.update(updates)
    _write(directory, OWNED_BINDING_NAME, binding)


def _analysis_evidence_digest(directory: Path) -> str:
    """Recompute, independently, the joint digest a completed run must carry."""

    ledger_bytes = (directory / ACQUISITION_LEDGER_NAME).read_bytes()
    ledger = json.loads(ledger_bytes)
    return _digest(
        _canonical(
            {
                "acquisition_ledger_sha256": _digest(ledger_bytes),
                "entries_sha256": ledger["entries_sha256"],
                "reverified_completion_evidence": open_owned_analysis_access(
                    directory
                ).verified_completion_evidence(),
            }
        )
    )


def _repin_ledger(directory: Path, ledger) -> None:
    """Persist a mutated ledger and re-pin every digest the owned binding keeps."""

    ledger["entries_sha256"] = _digest(_canonical(ledger["entries"]))
    _write(directory, ACQUISITION_LEDGER_NAME, ledger)
    _repin(
        directory,
        acquisition_ledger_sha256=_digest((directory / ACQUISITION_LEDGER_NAME).read_bytes()),
        entries_sha256=ledger["entries_sha256"],
    )


# --------------------------------------------------------------------------------------
# 1-4: the successful runs required by the frozen matrix
# --------------------------------------------------------------------------------------


def test_op_01_unit_cadence_run_publishes_and_unlocks(tmp_path: Path) -> None:
    source = RecordingSource([BLOB_A, BLOB_A, BLOB_A_SHIFTED, BLOB_A_SHIFTED])
    record = _run(tmp_path, source, UNIT_SCHEDULE)
    assert record.state is OwnedPipelineState.ANALYSIS_UNLOCKED
    assert source.calls == [(0, 0), (1, 1), (2, 2), (3, 3)]
    assert record.sampled_frames == UNIT_SCHEDULE
    assert record.sample_count == record.invocation_count == 4
    assert _artifacts(tmp_path) == (True, True, True)
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)
    # Reviewer B, blocker 3: neither the state enum nor this digest gates anything.  The
    # digest is a joint identity of the acquisition ledger and the reverified completion
    # evidence; what makes the final gate load-bearing is test_op_01b.
    assert record.analysis_evidence_sha256 == _analysis_evidence_digest(tmp_path)


def test_op_01b_a_failing_final_gate_aborts_the_run(tmp_path: Path, monkeypatch) -> None:
    """Reviewer B, blocker 2.  The digest in the record proves nothing on its own.

    ``canonical(verified_completion_evidence())`` is provably the completion manifest's own
    bytes, so any implementation with those bytes in scope can compute a look-alike.  What
    makes the final gate load-bearing is that the call is on the success path and its
    exception propagates.  That is what this test pins: replace the gate with one that
    refuses, and the run must refuse too.
    """

    calls: list[Path] = []
    real = owned.open_owned_analysis_access

    def refusing(directory):
        calls.append(Path(directory))
        real(directory)  # the genuine work still happens, so this is not a stub
        raise OwnedEvidenceError("synthetic final-gate refusal")

    monkeypatch.setattr(owned, "open_owned_analysis_access", refusing)
    with pytest.raises(OwnedEvidenceError):
        _run(tmp_path, _disappearance_source())
    assert calls == [tmp_path], "the run must reach the final gate exactly once"


def test_op_01c_the_recorded_evidence_digest_is_not_merely_the_manifest_digest(
    tmp_path: Path,
) -> None:
    """It is a joint identity of the acquisition ledger and the reverified evidence."""

    record = _run(tmp_path, _disappearance_source())
    assert record.analysis_evidence_sha256 != record.completion_manifest_sha256
    expected = _digest(
        _canonical(
            {
                "acquisition_ledger_sha256": record.acquisition_ledger_sha256,
                "entries_sha256": record.entries_sha256,
                "reverified_completion_evidence": open_owned_analysis_access(
                    tmp_path
                ).verified_completion_evidence(),
            }
        )
    )
    assert record.analysis_evidence_sha256 == expected


@pytest.mark.parametrize(
    "flavour", ("skip", "duplicate", "skip_and_duplicate", "trailing_extra")
)
def test_op_02c_a_skipped_or_duplicated_call_is_visible_in_the_persisted_evidence(
    tmp_path: Path, monkeypatch, flavour: str
) -> None:
    """Reviewer A blocker 1 / Reviewer B blocker 1, round two.

    The first attempt advanced the counter once per loop iteration, which is the loop index
    by construction and witnessed nothing.  Here the source is genuinely called the wrong
    number of times, and the refusal must come from the PERSISTED evidence -- not from a
    spy that only exists inside this test.
    """

    real_counter = owned._InvocationCounter

    class DriftingCounter(real_counter):
        def __call__(self, position, label):
            if flavour in {"duplicate", "skip_and_duplicate"} and position == 1:
                super().__call__(position, label)
            if flavour in {"skip", "skip_and_duplicate"} and position == 2:
                # the call is skipped entirely; the previous frame is reused
                return self._previous
            self._previous = super().__call__(position, label)
            if flavour == "trailing_extra" and position == 3:
                # an extra acquisition AFTER the ordinal was recorded: the ordinals stay
                # consecutive, so only the invocation count can object.  The two flavours
                # above and this one separate the two fields, so neither is redundant.
                self._source(position, label)
                self.calls += 1
            return self._previous

    monkeypatch.setattr(owned, "_InvocationCounter", DriftingCounter)
    source = _disappearance_source()
    with pytest.raises(OwnedEvidenceError):
        _run(tmp_path, source)
    expected_calls = {
        "skip": 3, "duplicate": 5, "skip_and_duplicate": 4, "trailing_extra": 5
    }[flavour]
    assert len(source.calls) == expected_calls, "the source really was called the wrong number of times"
    assert not (tmp_path / OWNED_BINDING_NAME).exists()


def test_op_02_nonunit_cadence_disappearance_run_is_owned_end_to_end(tmp_path: Path) -> None:
    """The full required example at (0, 5, 11, 12), acquired by the runner itself."""

    source = _disappearance_source()
    record = _run(tmp_path, source)

    # ownership: exactly one invocation per schedule element, in schedule order
    assert source.calls == [(0, 0), (1, 5), (2, 11), (3, 12)]
    assert record.invocation_count == 4 == record.sample_count

    document = _read(tmp_path, LIFECYCLE_DOCUMENT_NAME)
    assert document["sampled_frames"] == list(NONUNIT_SCHEDULE)
    fates = sorted(
        (row["terminal_state"], row["terminal_frame"]) for row in document["terminal_records"]
    )
    assert fates == [("DISSOLVED_DETECTED_TRACK", 5), ("RIGHT_CENSORED_AT_HORIZON", 12)]
    # exactly-one-terminal accounting, through the owned chain
    assert len(document["terminal_records"]) == record.track_count == record.terminal_record_count
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)


def test_op_02b_exactly_one_invocation_per_schedule_element_reaches_the_ledger(
    tmp_path: Path,
) -> None:
    """The named killer for a skipped or duplicated acquisition call.

    Reviewer B, blocker 1: ``sequence_position`` is a loop index and proves nothing on its
    own.  ``invocation_ordinal`` and ``invocation_count`` are taken from a counter
    incremented on each ACTUAL call to the source, so an implementation that skips or
    duplicates a call writes a non-consecutive ordinal and is refused on re-read.  That is
    a within-process witness (OP-L4), not an externally verifiable one: an actor rewriting
    the ledger afterwards can write any counts.  The in-test spy remains the direct check.
    """

    source = _disappearance_source()
    record = _run(tmp_path, source)
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    assert source.calls == [(0, 0), (1, 5), (2, 11), (3, 12)]
    assert len(source.calls) == len(NONUNIT_SCHEDULE)
    assert record.invocation_count == len(source.calls)
    assert ledger["sample_count"] == len(source.calls)
    assert ledger["invocation_count"] == len(source.calls)
    assert len(ledger["entries"]) == len(source.calls)
    assert [row["invocation_ordinal"] for row in ledger["entries"]] == [0, 1, 2, 3]
    assert [row["sequence_position"] for row in ledger["entries"]] == [0, 1, 2, 3]
    assert [row["requested_sample_label"] for row in ledger["entries"]] == list(
        NONUNIT_SCHEDULE
    )
    # the four persisted frames are the four distinct masks handed over, in order
    digests = [row["frame_sha256"] for row in ledger["entries"]]
    assert digests[0] != digests[1] != digests[2]
    assert digests[2] == digests[3], "frames 11 and 12 really are the same mask"
    assert record.frame_digests == tuple(digests)


def test_op_03_disappearance_plus_surviving_track_is_countable(tmp_path: Path) -> None:
    record = _run(tmp_path, _disappearance_source())
    assert record.track_count == 2
    assert record.terminal_record_count == 2
    assert record.detected_component_count == 3  # A, then B twice; nothing at frame 5


def test_op_04_zero_detection_acquisition_still_proves_the_schedule(tmp_path: Path) -> None:
    """No detected entity is NOT no acquisition: the ledger still proves four samples."""

    source = RecordingSource([EMPTY, EMPTY, EMPTY, EMPTY])
    record = _run(tmp_path, source)
    assert source.calls == [(0, 0), (1, 5), (2, 11), (3, 12)]
    assert record.detected_component_count == 0
    assert record.track_count == 0
    assert record.terminal_record_count == 0
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    assert ledger["sample_count"] == 4
    assert ledger["sampled_frames"] == list(NONUNIT_SCHEDULE)
    assert [row["requested_sample_label"] for row in ledger["entries"]] == list(NONUNIT_SCHEDULE)
    assert all(row["true_cell_count"] == 0 for row in ledger["entries"])
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)


# --------------------------------------------------------------------------------------
# 5-7: schedule ownership, validated BEFORE acquisition
# --------------------------------------------------------------------------------------


def test_op_05_an_omitted_schedule_fails_at_the_api_boundary(tmp_path: Path) -> None:
    source = _disappearance_source()
    with pytest.raises(TypeError):
        run_owned_future_pipeline(
            tmp_path,
            acquisition_source=source,
            detector_spec=DETECTOR,
            tracker_spec=TRACKER,
            acquisition_source_identity=IDENTITY,
        )
    assert source.calls == []
    assert _artifacts(tmp_path) == (False, False, False)


def test_op_06_an_explicit_none_schedule_is_refused_before_acquisition(tmp_path: Path) -> None:
    source = _disappearance_source()
    with pytest.raises(OwnedScheduleError):
        _run(tmp_path, source, None)
    assert source.calls == []
    assert _artifacts(tmp_path) == (False, False, False)


@pytest.mark.parametrize(
    "schedule",
    (
        pytest.param((), id="empty"),
        pytest.param((0, 5, 5), id="not strictly increasing"),
        pytest.param((5, 0), id="decreasing"),
        pytest.param((-1, 5), id="negative"),
        pytest.param((0, 1.5), id="non-integer"),
        pytest.param((0, True), id="bool is not an admissible frame"),
        pytest.param("0,5", id="string is not an ordered schedule"),
        pytest.param(b"05", id="bytes is not an ordered schedule"),
        pytest.param(bytearray(b"05"), id="bytearray is not an ordered schedule"),
        pytest.param({0: "a", 5: "b"}, id="mapping is not an ordered schedule"),
        pytest.param(frozenset({0, 5}), id="set is not an ordered schedule"),
    ),
)
def test_op_07_malformed_schedules_are_refused_and_nothing_is_acquired(
    tmp_path: Path, schedule
) -> None:
    source = _disappearance_source()
    with pytest.raises(OwnedScheduleError):
        _run(tmp_path, source, schedule)
    assert source.calls == [], "the schedule is validated BEFORE acquisition"
    assert _artifacts(tmp_path) == (False, False, False)


# --------------------------------------------------------------------------------------
# 8-9: acquisition failure and malformed frames, at every position
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("failing", (0, 1, 2, 3))
def test_op_08_an_acquisition_exception_at_any_position_fails_closed(
    tmp_path: Path, failing: int
) -> None:
    def explode(source, position, label):
        if position == failing:
            raise RuntimeError(f"synthetic acquisition failure at {position}")

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B], side_effect=explode)
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, source)
    assert len(source.calls) == failing + 1, "acquisition stops at the failing position"
    assert _artifacts(tmp_path) == (False, False, False)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("position", (0, 1, 2, 3))
@pytest.mark.parametrize(
    "bad",
    (
        pytest.param([[True, False], [False, True]], id="not an array"),
        pytest.param(np.zeros(SHAPE, dtype=np.uint8), id="not a boolean mask"),
        pytest.param(np.zeros((4,), dtype=bool), id="not 2-D"),
        pytest.param(np.zeros((1, 6), dtype=bool), id="degenerate lattice"),
    ),
)
def test_op_09_a_malformed_frame_at_any_position_fails_closed(
    tmp_path: Path, position: int, bad
) -> None:
    frames = [BLOB_A, EMPTY, BLOB_B, BLOB_B]
    frames[position] = bad
    source = RecordingSource(frames)
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, source)
    assert len(source.calls) == position + 1
    assert _artifacts(tmp_path) == (False, False, False)


def test_op_09b_a_frame_whose_shape_changes_mid_run_is_refused(tmp_path: Path) -> None:
    source = RecordingSource([BLOB_A, np.zeros((6, 6), dtype=bool), BLOB_B, BLOB_B])
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, source)
    assert _artifacts(tmp_path) == (False, False, False)


# --------------------------------------------------------------------------------------
# 10: the mutable-buffer attack
# --------------------------------------------------------------------------------------


def test_op_10_post_return_mutation_cannot_change_persisted_evidence(tmp_path: Path) -> None:
    """The source keeps one buffer, hands it over, and rewrites it after every return."""

    buffer = BLOB_A.copy()
    handed_over: list[np.ndarray] = []

    class MutatingSource:
        def __init__(self) -> None:
            self.calls: list[tuple[int, int]] = []

        def __call__(self, position, label):
            self.calls.append((position, label))
            buffer[:] = [EMPTY, BLOB_A, EMPTY, BLOB_B][position]
            handed_over.append(buffer.copy())
            return buffer

    source = MutatingSource()
    record = _run(tmp_path, source)
    # after the run the caller scribbles all over its own buffer
    buffer[:] = True
    assert bool(buffer.all())

    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    for position, row in enumerate(ledger["entries"]):
        payload = (tmp_path / row["frame_relative_path"]).read_bytes()
        expected = handed_over[position].astype(np.uint8).tobytes(order="C")
        assert payload == expected, "the persisted frame is the value at return time"
        assert row["frame_sha256"] == _digest(payload)
    assert record.frame_digests == tuple(row["frame_sha256"] for row in ledger["entries"])
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)


# --------------------------------------------------------------------------------------
# 11-14: acquisition-ledger tampering.  Each field is attacked twice where it matters:
# once as a naive edit (caught by bookkeeping) and once re-pinned (caught semantically).
# --------------------------------------------------------------------------------------


def test_op_11a_schedule_padding_after_persistence_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = [0, 5, 11, 1_000_000]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_11b_schedule_truncation_after_persistence_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = [0, 5, 11]
    ledger["sample_count"] = 3
    _repin_ledger(tmp_path, ledger)
    _repin(tmp_path, sample_count=3, sampled_frames=[0, 5, 11])
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_11c_a_naive_schedule_edit_is_caught_by_the_ledger_digest(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = [0, 5, 11, 99]
    _write(tmp_path, ACQUISITION_LEDGER_NAME, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_11d_a_relabelled_but_consistent_schedule_is_refused_by_the_gate(
    tmp_path: Path,
) -> None:
    """Every internal digest re-pinned; the published COMPLETE still disagrees."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = [0, 5, 11, 20]
    ledger["entries"][3]["requested_sample_label"] = 20
    _repin_ledger(tmp_path, ledger)
    _repin(tmp_path, sampled_frames=[0, 5, 11, 20])
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12a_reordering_ledger_rows_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0], ledger["entries"][1] = ledger["entries"][1], ledger["entries"][0]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12b_a_rewritten_sequence_position_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][2]["sequence_position"] = 3
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12c_a_rewritten_invocation_ordinal_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][1]["invocation_ordinal"] = 0
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12c2_permuting_row_labels_alone_is_refused(tmp_path: Path) -> None:
    """Reviewer B, material 4.  ``sampled_frames`` is left untouched; only the per-row
    labels are swapped, so nothing downstream re-derives them and the per-row binding is
    the only thing that can object."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    rows = ledger["entries"]
    rows[1]["requested_sample_label"], rows[2]["requested_sample_label"] = (
        rows[2]["requested_sample_label"],
        rows[1]["requested_sample_label"],
    )
    assert ledger["sampled_frames"] == list(NONUNIT_SCHEDULE), "the schedule is untouched"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12d_an_additional_ledger_row_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    extra = dict(ledger["entries"][3])
    extra["sequence_position"] = 4
    extra["invocation_ordinal"] = 4
    ledger["entries"].append(extra)
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12e_a_missing_ledger_row_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    del ledger["entries"][2]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12f_a_ledger_row_with_an_extra_key_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["provenance"] = "trust me"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12g_a_ledger_sample_count_disagreement_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sample_count"] = 3
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_12h_a_forged_entries_digest_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries_sha256"] = "0" * 64
    _write(tmp_path, ACQUISITION_LEDGER_NAME, ledger)
    _repin(
        tmp_path,
        acquisition_ledger_sha256=_digest(
            (tmp_path / ACQUISITION_LEDGER_NAME).read_bytes()
        ),
        entries_sha256="0" * 64,
    )
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13a_frame_substitution_is_refused_by_the_recomputed_digest(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    target = tmp_path / ledger["entries"][1]["frame_relative_path"]
    target.write_bytes(BLOB_B.astype(np.uint8).tobytes(order="C"))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13b_frame_substitution_with_every_digest_repinned_is_refused_semantically(
    tmp_path: Path,
) -> None:
    """The disappearance frame is replaced by an occupied one and all digests re-pinned.

    Nothing in the acquisition bookkeeping can object any more, so the refusal has to
    come from the re-derived tracking disagreeing with the published lifecycle document.
    """

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    row = ledger["entries"][1]
    payload = BLOB_A.astype(np.uint8).tobytes(order="C")
    (tmp_path / row["frame_relative_path"]).write_bytes(payload)
    row["frame_sha256"] = _digest(payload)
    row["true_cell_count"] = int(np.count_nonzero(BLOB_A))
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13a2_a_detection_neutral_frame_edit_is_still_caught_by_the_digest(
    tmp_path: Path,
) -> None:
    """The only signal is the recomputed digest.

    With ``min_cells=3`` a single isolated cell is never detected, so this substitution
    leaves the tracker output, the lifecycle document and the completion manifest
    bit-identical.  A pipeline that trusted the digest recorded in the ledger instead of
    recomputing it from the persisted bytes would accept this frame.
    """

    detector = DetectorSpec(matter_threshold=0.5, min_cells=3)
    speck_here = BLOB_A.copy()
    speck_here[0, 0] = True  # an isolated cell: below min_cells, never detected
    speck_there = BLOB_A.copy()
    speck_there[0, 5] = True  # the same isolated cell, moved
    _run(tmp_path, RecordingSource([speck_here, EMPTY, BLOB_B, BLOB_B]), detector=detector)
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    row = ledger["entries"][0]
    assert row["true_cell_count"] == int(np.count_nonzero(speck_there))
    (tmp_path / row["frame_relative_path"]).write_bytes(
        speck_there.astype(np.uint8).tobytes(order="C")
    )
    # shape, dtype, cell count, detection, tracking and lifecycle are all unchanged
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13a3_a_repinned_detection_equivalent_frame_is_accepted_and_disclosed(
    tmp_path: Path,
) -> None:
    """LIMITATION OP-L3, pinned rather than hidden.  Reviewer A, blocker 1.

    Once the row digest, the entries digest and the ledger digest are all re-pinned, the
    acquisition chain is self-consistent again, and the only anchor outside it -- the
    lifecycle document -- binds the TRACKING, not the pixels.  Any frame whose detected
    components are unchanged is therefore accepted, and the frame that is analysed is not
    the frame the source returned.

    The honest wording is reproduction, not attestation: the persisted evidence reproduces
    the published lifecycle document.  It is not evidence of what was acquired.  This test
    exists to make that limitation impossible to overlook, not to celebrate a capability.
    """

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B])
    _run(tmp_path, source)
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    row = ledger["entries"][0]
    acquired_digest = row["frame_sha256"]
    # Reviewer A, round two: with the suite's DEFAULT detector, the four-cell blob that
    # dissolves at frame 5 can be replaced by the ENTIRE LATTICE.  One component in, one
    # component out, same track topology -- area 4 -> 120, mass and radius of gyration
    # completely different, and the lifecycle document does not bind any of it.
    speckled = np.ones(SHAPE, dtype=bool)
    payload = speckled.astype(np.uint8).tobytes(order="C")
    (tmp_path / row["frame_relative_path"]).write_bytes(payload)
    row["frame_sha256"] = _digest(payload)
    row["true_cell_count"] = int(np.count_nonzero(speckled))
    _repin_ledger(tmp_path, ledger)

    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)
    assert row["frame_sha256"] != acquired_digest, "the analysed frame is not the acquired one"
    assert row["true_cell_count"] == SHAPE[0] * SHAPE[1] != int(np.count_nonzero(BLOB_A))


def test_op_13m_a_symlinked_frame_is_refused(tmp_path: Path) -> None:
    """Reviewer B, minor 1.  The evidence directory must be self-contained."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    target = tmp_path / ledger["entries"][0]["frame_relative_path"]
    outside = tmp_path / "outside.bin"
    outside.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(outside)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13n_a_symlink_smuggled_into_the_frame_directory_is_refused(
    tmp_path: Path,
) -> None:
    _run(tmp_path, _disappearance_source())
    outside = tmp_path / "outside.bin"
    outside.write_bytes(EMPTY.astype(np.uint8).tobytes(order="C"))
    (tmp_path / owned.ACQUISITION_FRAME_DIRECTORY / "frame_000004.bin").symlink_to(outside)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13c_a_missing_frame_file_is_refused(tmp_path: Path) -> None:
    record = _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    (tmp_path / ledger["entries"][2]["frame_relative_path"]).unlink()
    assert record.sample_count == 4
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13d_an_additional_frame_file_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    (tmp_path / owned.ACQUISITION_FRAME_DIRECTORY / "frame_000004.bin").write_bytes(
        EMPTY.astype(np.uint8).tobytes(order="C")
    )
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13e_a_rewritten_frame_path_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][1]["frame_relative_path"] = ledger["entries"][0]["frame_relative_path"]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13f_a_rewritten_frame_shape_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["shape"] = [12, 10]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "shape",
    (
        pytest.param("10x12", id="not a list"),
        pytest.param([10, 12, 1], id="wrong arity"),
        pytest.param([10, True], id="bool is not a dimension"),
        pytest.param([10, "12"], id="non-integer dimension"),
    ),
)
def test_op_13g_a_malformed_frame_shape_is_refused(tmp_path: Path, shape) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["shape"] = shape
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13h_a_shape_disagreement_between_rows_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][2]["shape"] = [12, 10]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13i_a_rewritten_dtype_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["dtype"] = "uint8"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13j_a_rewritten_true_cell_count_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["true_cell_count"] = 99
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13k_a_truncated_frame_file_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    row = ledger["entries"][0]
    payload = (tmp_path / row["frame_relative_path"]).read_bytes()[:-1]
    (tmp_path / row["frame_relative_path"]).write_bytes(payload)
    row["frame_sha256"] = _digest(payload)
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_13l_a_non_canonical_frame_encoding_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    row = ledger["entries"][0]
    payload = bytes([2]) * (SHAPE[0] * SHAPE[1])
    (tmp_path / row["frame_relative_path"]).write_bytes(payload)
    row["frame_sha256"] = _digest(payload)
    row["true_cell_count"] = SHAPE[0] * SHAPE[1]
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_14a_source_identity_tampering_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["acquisition_source_identity"]["declared"]["name"] = "a real detector, honest"
    _write(tmp_path, ACQUISITION_LEDGER_NAME, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_14b_an_identity_claiming_authority_is_refused(tmp_path: Path) -> None:
    """The identity document may never be promoted from declaration to authority."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["acquisition_source_identity"]["authority"] = "CERTIFIED"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_14c_a_non_object_identity_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["acquisition_source_identity"] = "synthetic"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "mutation",
    (
        pytest.param({"authority_certificate": "ISO-17025 cert 4471"}, id="extra sibling key"),
        pytest.param({"declared_by": "a calibrated instrument"}, id="rewritten declared_by"),
        pytest.param({"declared": None}, id="declaration removed"),
        pytest.param({"declared": ["synthetic"]}, id="declaration is not an object"),
        pytest.param({"declared": {}}, id="declaration is empty"),
        pytest.param({"declared": {"kind": 1}}, id="declaration is not strings"),
    ),
)
def test_op_14e_a_repinned_identity_mutation_is_refused(tmp_path: Path, mutation) -> None:
    """Reviewer A material 1 / Reviewer B blocker 4.

    The write side enforced an exact three-key str->str shape; the read side did not, so
    every re-pinned decoration of the identity block was previously accepted -- including
    an added ``authority_certificate`` key and a ``declared_by`` of "a calibrated
    instrument".  The read side is now exactly as strict as the write side.
    """

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    identity = ledger["acquisition_source_identity"]
    for key, value in mutation.items():
        if value is None:
            del identity[key]
        else:
            identity[key] = value
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "identity",
    (
        pytest.param("synthetic", id="not a mapping"),
        pytest.param({}, id="empty"),
        pytest.param({1: "synthetic"}, id="non-string key"),
        pytest.param({"kind": 1}, id="non-string value"),
    ),
)
def test_op_14d_a_malformed_identity_is_refused_before_acquisition(
    tmp_path: Path, identity
) -> None:
    source = _disappearance_source()
    with pytest.raises(OwnedAcquisitionError):
        run_owned_future_pipeline(
            tmp_path,
            acquisition_source=source,
            sampled_frames=NONUNIT_SCHEDULE,
            detector_spec=DETECTOR,
            tracker_spec=TRACKER,
            acquisition_source_identity=identity,
        )
    assert source.calls == []


# --------------------------------------------------------------------------------------
# 15: specification and source-code bindings
# --------------------------------------------------------------------------------------


def test_op_15a_tracker_spec_tampering_that_changes_tracking_is_refused(
    tmp_path: Path,
) -> None:
    """The blob moves one cell per sample; forbidding that displacement splits the track."""

    _run(tmp_path, RecordingSource([BLOB_A, BLOB_A, BLOB_A_SHIFTED, BLOB_A_SHIFTED]),
         UNIT_SCHEDULE)
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["tracker_spec"]["max_centroid_displacement"] = 0.1
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_15a2_a_naive_tracker_spec_edit_is_caught_by_the_ledger_digest(
    tmp_path: Path,
) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["tracker_spec"]["max_centroid_displacement"] = 99.0
    _write(tmp_path, ACQUISITION_LEDGER_NAME, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_15a3_an_inert_specification_perturbation_is_accepted_and_this_is_disclosed(
    tmp_path: Path,
) -> None:
    """LIMITATION OP-L2, pinned rather than hidden.

    What is bound is not "the specification that was used during acquisition" but "a
    specification that reproduces the published lifecycle document from the persisted
    frames".  A re-pinned perturbation that leaves the tracker's output identical is
    therefore accepted: raising ``max_centroid_displacement`` from 3.0 to 99.0 on this
    fixture changes nothing, because the only association in the run is a zero-distance
    one.  No false evidence results -- the recorded specification really does reproduce
    the evidence -- but the claim must be worded as reproduction, not as attestation.
    """

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["tracker_spec"]["max_centroid_displacement"] = 99.0
    _repin_ledger(tmp_path, ledger)
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)


def test_op_15b_detector_spec_tampering_changes_detection_and_is_refused(
    tmp_path: Path,
) -> None:
    """Raising the threshold above the materialised matter erases every component."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["detector_spec"]["matter_threshold"] = 0.95
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "field",
    ("detector_spec", "tracker_spec"),
)
def test_op_15c_a_specification_with_a_wrong_key_set_is_refused(
    tmp_path: Path, field: str
) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger[field] = {"unexpected": 1}
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("field", ("detector_spec", "tracker_spec"))
def test_op_15d_a_non_object_specification_is_refused(tmp_path: Path, field: str) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger[field] = "default"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_15e_a_specification_with_an_unusable_value_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["detector_spec"]["min_cells"] = "several"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        pytest.param("dilation_radius", 1_000_000_000, id="tracker radius beyond the lattice"),
        pytest.param("dilation_radius", -1, id="negative tracker radius"),
        pytest.param("max_centroid_displacement", -1.0, id="negative displacement"),
        pytest.param("max_area_ratio", -1.0, id="negative area ratio"),
        pytest.param("unique_score_margin", -1.0, id="negative score margin"),
    ),
)
def test_op_15i_an_out_of_range_tracker_specification_is_refused(
    tmp_path: Path, field, value
) -> None:
    """Reviewer A, material 2.  A persisted ``dilation_radius`` of 10**9 previously made
    the supported analysis entry point run effectively forever instead of failing closed.
    A radius beyond the lattice is geometrically inert, so bounding it costs nothing."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["tracker_spec"][field] = value
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        pytest.param("min_cells", 0, id="detector min_cells below one"),
        pytest.param("matter_threshold", 0.0, id="detector threshold at zero"),
        pytest.param("matter_threshold", 1.5, id="detector threshold above one"),
    ),
)
def test_op_15j_an_out_of_range_detector_specification_is_refused(
    tmp_path: Path, field, value
) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["detector_spec"][field] = value
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "field",
    (
        "future_lifecycle_owned_pipeline_sha256",
        "future_lifecycle_runner_sha256",
        "instrumentation_sha256",
        "lifecycle_sha256",
    ),
)
def test_op_15f_tampering_a_source_binding_is_refused(tmp_path: Path, field: str) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["source_bindings"][field] = "0" * 64
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_15g_tampering_a_binding_source_digest_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    binding = _read(tmp_path, OWNED_BINDING_NAME)
    binding["source_bindings"]["lifecycle_sha256"] = "0" * 64
    _write(tmp_path, OWNED_BINDING_NAME, binding)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_15h_the_recorded_source_bindings_are_the_real_module_digests(
    tmp_path: Path,
) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    root = Path(owned.__file__).parent
    expected = {
        "future_lifecycle_owned_pipeline_sha256": "future_lifecycle_owned_pipeline.py",
        "future_lifecycle_runner_sha256": "future_lifecycle_runner.py",
        "instrumentation_sha256": "instrumentation.py",
        "lifecycle_sha256": "lifecycle.py",
    }
    for key, name in expected.items():
        assert ledger["source_bindings"][key] == _digest((root / name).read_bytes())


# --------------------------------------------------------------------------------------
# 16-18: forged downstream evidence and stale reuse
# --------------------------------------------------------------------------------------


def test_op_16_a_forged_lifecycle_disposition_never_unlocks_analysis(tmp_path: Path) -> None:
    """A hand-authored QUALIFIED lifecycle document, canonically encoded, is worthless."""

    _run(tmp_path, _disappearance_source())
    document = _read(tmp_path, LIFECYCLE_DOCUMENT_NAME)
    document["terminal_records"] = []
    payload = _canonical(document)
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(payload)
    _repin(tmp_path, lifecycle_document_sha256=_digest(payload))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_16b_a_naive_lifecycle_edit_is_caught_by_the_owned_binding(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    document = _read(tmp_path, LIFECYCLE_DOCUMENT_NAME)
    document["terminal_records"] = []
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(_canonical(document))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_16c_a_deleted_lifecycle_document_locks_analysis(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    (tmp_path / LIFECYCLE_DOCUMENT_NAME).unlink()
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_17a_a_forged_complete_manifest_never_unlocks_analysis(tmp_path: Path) -> None:
    honest = tmp_path / "honest"
    honest.mkdir()
    _run(honest, _disappearance_source())
    forged = tmp_path / "forged"
    forged.mkdir()
    for name in (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME):
        shutil.copy2(honest / name, forged / name)
    shutil.copy2(honest / COMPLETION_MANIFEST_NAME, forged / COMPLETION_MANIFEST_NAME)
    # a complete manifest, byte-identical to a genuine one, with no acquisition at all
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(forged)


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("canonicalization", {"encoding": "utf-16"}),
        ("disposition", "PROVISIONAL"),
        ("integration_version", "9.9.9"),
        ("lifecycle_document_relative_path", "OTHER.json"),
        ("lifecycle_document_sha256", "0" * 64),
        ("lifecycle_input_sha256", "0" * 64),
        ("lifecycle_records_sha256", "0" * 64),
        ("lifecycle_schema_version", "other/v9"),
        ("lifecycle_validator_version", "9.9.9"),
        ("sampled_frames", [0, 5, 11, 13]),
        ("schema_version", "other/v9"),
        ("terminal_record_count", 99),
    ),
)
def test_op_17b_every_completion_manifest_field_remains_tamper_covered(
    tmp_path: Path, key, value
) -> None:
    """Twelve fields, each re-pinned in the owned binding so the refusal is semantic."""

    _run(tmp_path, _disappearance_source())
    manifest = _read(tmp_path, COMPLETION_MANIFEST_NAME)
    assert key in manifest, "the manifest field set must not have drifted"
    manifest[key] = value
    payload = _canonical(manifest)
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(payload)
    _repin(tmp_path, completion_manifest_sha256=_digest(payload))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_17c_a_naive_manifest_edit_is_caught_by_the_owned_binding(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    manifest = _read(tmp_path, COMPLETION_MANIFEST_NAME)
    manifest["terminal_record_count"] = 99
    (tmp_path / COMPLETION_MANIFEST_NAME).write_bytes(_canonical(manifest))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_17d_a_deleted_completion_manifest_locks_analysis(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    (tmp_path / COMPLETION_MANIFEST_NAME).unlink()
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_18a_stale_acquisition_evidence_cannot_be_reused_for_a_new_run(
    tmp_path: Path,
) -> None:
    _run(tmp_path, _disappearance_source())
    with pytest.raises(OwnedPublicationError):
        _run(tmp_path, _disappearance_source())


def test_op_18b_a_stale_acquisition_directory_alone_blocks_a_fresh_run(
    tmp_path: Path,
) -> None:
    (tmp_path / owned.ACQUISITION_FRAME_DIRECTORY).mkdir()
    with pytest.raises(OwnedPublicationError):
        _run(tmp_path, _disappearance_source())
    assert _artifacts(tmp_path) == (False, False, False)


def test_op_18c_transplanted_evidence_from_another_run_is_refused(tmp_path: Path) -> None:
    """Whole-directory copying is the documented content-addressed limitation.

    A *partial* transplant, however, must fail: here a genuine acquisition ledger from a
    different run is dropped next to this run's completion evidence.
    """

    first = tmp_path / "first"
    first.mkdir()
    _run(first, _disappearance_source())
    second = tmp_path / "second"
    second.mkdir()
    _run(second, RecordingSource([BLOB_B, BLOB_B, BLOB_B, BLOB_B]))
    shutil.copy2(first / ACQUISITION_LEDGER_NAME, second / ACQUISITION_LEDGER_NAME)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(second)


# --------------------------------------------------------------------------------------
# 19-20: rival publication and access before completion
# --------------------------------------------------------------------------------------


def test_op_19a_a_rival_acquisition_ledger_published_mid_flight_fails_closed(
    tmp_path: Path,
) -> None:
    """The rival appears during acquisition, i.e. after any pre-check would have run."""

    sentinel = b'{"rival":true}'

    def plant(source, position, label):
        if position == 3:
            (tmp_path / ACQUISITION_LEDGER_NAME).write_bytes(sentinel)

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B], side_effect=plant)
    with pytest.raises(OwnedPublicationError):
        _run(tmp_path, source)
    assert (tmp_path / ACQUISITION_LEDGER_NAME).read_bytes() == sentinel
    assert not (tmp_path / OWNED_BINDING_NAME).exists()
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_19a2_a_dangling_symlink_at_the_target_cannot_be_written_through(
    tmp_path: Path,
) -> None:
    """Reviewer B, blocker 2.  The named killer for an ``exists()``-guarded plain write.

    ``Path.exists()`` follows symlinks, so a dangling symlink reports False and a guarded
    ``write_bytes`` would create the file at the symlink's target -- outside the run
    directory.  ``os.link`` refuses the name outright, which is why creation, not a
    pre-check, is the check.
    """

    outside = tmp_path / "outside" / "SMUGGLED.json"
    outside.parent.mkdir()
    run = tmp_path / "run"
    run.mkdir()
    (run / ACQUISITION_LEDGER_NAME).symlink_to(outside)
    with pytest.raises(OwnedPublicationError):
        _run(run, _disappearance_source())
    assert not outside.exists(), "no evidence may be written outside the run directory"
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(run)


def test_op_19b_a_rival_frame_file_published_mid_flight_fails_closed(tmp_path: Path) -> None:
    def plant(source, position, label):
        if position == 0:
            (tmp_path / owned.ACQUISITION_FRAME_DIRECTORY / "frame_000001.bin").write_bytes(
                b"rival"
            )

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B], side_effect=plant)
    with pytest.raises(OwnedPublicationError):
        _run(tmp_path, source)
    assert not (tmp_path / ACQUISITION_LEDGER_NAME).exists()


def test_op_19c_a_rival_lifecycle_document_blocks_the_qualified_gate(tmp_path: Path) -> None:
    def plant(source, position, label):
        if position == 3:
            (tmp_path / LIFECYCLE_DOCUMENT_NAME).write_bytes(b"{}")

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B], side_effect=plant)
    with pytest.raises(OwnedEvidenceError):
        _run(tmp_path, source)
    assert (tmp_path / ACQUISITION_LEDGER_NAME).exists()
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()
    assert not (tmp_path / OWNED_BINDING_NAME).exists()
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_19d_in_flight_corruption_of_persisted_evidence_is_caught_on_re_read(
    tmp_path: Path,
) -> None:
    """The source corrupts an already-persisted frame while the run is still going.

    Nothing in memory notices.  The post-publication re-read does.
    """

    def corrupt(source, position, label):
        if position == 3:
            target = tmp_path / owned.ACQUISITION_FRAME_DIRECTORY / "frame_000000.bin"
            target.write_bytes(BLOB_B.astype(np.uint8).tobytes(order="C"))

    source = RecordingSource([BLOB_A, EMPTY, BLOB_B, BLOB_B], side_effect=corrupt)
    with pytest.raises(OwnedEvidenceError):
        _run(tmp_path, source)
    assert (tmp_path / ACQUISITION_LEDGER_NAME).exists()
    assert not (tmp_path / COMPLETION_MANIFEST_NAME).exists()
    assert not (tmp_path / OWNED_BINDING_NAME).exists()


def test_op_20a_analysis_access_before_completion_is_locked(tmp_path: Path) -> None:
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_20b_analysis_access_on_a_missing_directory_is_locked(tmp_path: Path) -> None:
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path / "absent")


def test_op_20c_a_run_directory_that_does_not_exist_is_refused(tmp_path: Path) -> None:
    with pytest.raises(OwnedPublicationError):
        _run(tmp_path / "absent", _disappearance_source())


def test_op_20d_acquisition_evidence_alone_never_unlocks_analysis(tmp_path: Path) -> None:
    """Delete only the owned binding: COMPLETE exists, analysis stays locked."""

    _run(tmp_path, _disappearance_source())
    (tmp_path / OWNED_BINDING_NAME).unlink()
    assert (tmp_path / COMPLETION_MANIFEST_NAME).exists()
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


# --------------------------------------------------------------------------------------
# API-boundary ownership: nothing may be injected
# --------------------------------------------------------------------------------------


def test_op_21a_the_public_signature_accepts_no_injectable_artifact() -> None:
    import inspect

    run = inspect.signature(owned.run_owned_future_pipeline).parameters
    assert list(run) == [
        "run_directory",
        "acquisition_source",
        "sampled_frames",
        "detector_spec",
        "tracker_spec",
        "acquisition_source_identity",
    ]
    for name in ("acquisition_source", "sampled_frames", "detector_spec", "tracker_spec",
                 "acquisition_source_identity"):
        assert run[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert run[name].default is inspect.Parameter.empty
    forbidden = (
        "frames", "frame_sequence", "masks", "tracking", "tracking_result", "lifecycle",
        "lifecycle_records", "disposition", "qualification", "manifest", "completion",
        "access", "analysis_access", "ledger", "acquisition_ledger", "evidence_directory",
    )
    assert not set(run) & set(forbidden)
    opened = inspect.signature(owned.open_owned_analysis_access).parameters
    assert list(opened) == ["run_directory"], "analysis re-reads everything from disk"


@pytest.mark.parametrize(
    "source",
    (
        pytest.param([BLOB_A, EMPTY, BLOB_B, BLOB_B], id="a list of prebuilt frames"),
        pytest.param((BLOB_A, EMPTY, BLOB_B, BLOB_B), id="a tuple of prebuilt frames"),
        pytest.param({0: BLOB_A}, id="a mapping of prebuilt frames"),
        pytest.param(np.zeros((4, *SHAPE), dtype=bool), id="a prebuilt frame stack"),
    ),
)
def test_op_21b_a_prebuilt_frame_container_is_not_an_acquisition_source(
    tmp_path: Path, source
) -> None:
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, source)
    assert _artifacts(tmp_path) == (False, False, False)


def test_op_21c_a_callable_prebuilt_container_is_still_refused(tmp_path: Path) -> None:
    """A container does not become a source by growing a ``__call__``."""

    invoked: list[int] = []

    class CallableSequence(list):
        def __call__(self, position, label):
            invoked.append(position)
            return self[position]

    with pytest.raises(OwnedAcquisitionError) as caught:
        _run(tmp_path, CallableSequence([BLOB_A, EMPTY, BLOB_B, BLOB_B]))
    # Reviewer B, material 5: assert the guard fired, not merely that *something* raised.
    assert invoked == [], "a container must never be invoked as a source"
    assert "prebuilt frame container" in str(caught.value)


def test_op_21d_a_non_callable_source_is_refused(tmp_path: Path) -> None:
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, 7)


@pytest.mark.parametrize(
    ("detector", "tracker"),
    (
        pytest.param("default", TRACKER, id="detector is not a DetectorSpec"),
        pytest.param(DETECTOR, "default", id="tracker is not a TrackerSpec"),
    ),
)
def test_op_21e_specifications_must_be_the_committed_types(
    tmp_path: Path, detector, tracker
) -> None:
    source = _disappearance_source()
    with pytest.raises(OwnedAcquisitionError):
        _run(tmp_path, source, detector=detector, tracker=tracker)
    assert source.calls == []


def test_op_21f_the_tracker_is_called_by_the_pipeline_with_the_re_read_schedule(
    tmp_path: Path, monkeypatch
) -> None:
    """Not a stub: the real ``track_components`` runs.  The spy only records the call."""

    seen: list[dict] = []
    real = owned.track_components

    def spy(frames, spec, *, sampled_frames):
        seen.append(
            {
                "frame_count": len(frames),
                "spec": spec,
                "sampled_frames": tuple(sampled_frames),
            }
        )
        return real(frames, spec, sampled_frames=sampled_frames)

    monkeypatch.setattr(owned, "track_components", spy)
    _run(tmp_path, _disappearance_source())
    assert seen, "the owned pipeline must call track_components itself"
    for call in seen:
        assert call["frame_count"] == 4
        assert call["sampled_frames"] == NONUNIT_SCHEDULE
        assert call["spec"] == TRACKER


@pytest.mark.parametrize(
    "injected",
    (
        "frames",
        "tracking",
        "tracking_result",
        "lifecycle_records",
        "disposition",
        "manifest",
        "completion",
        "access",
        "analysis_access",
        "acquisition_ledger",
        "evidence_directory",
    ),
)
def test_op_21h_no_downstream_artifact_can_be_handed_to_the_pipeline(
    tmp_path: Path, injected: str
) -> None:
    """Every injection attempt is a ``TypeError`` at the boundary, not a silent override."""

    source = _disappearance_source()
    with pytest.raises(TypeError):
        run_owned_future_pipeline(
            tmp_path,
            acquisition_source=source,
            sampled_frames=NONUNIT_SCHEDULE,
            detector_spec=DETECTOR,
            tracker_spec=TRACKER,
            acquisition_source_identity=IDENTITY,
            **{injected: "smuggled"},
        )
    assert source.calls == []
    assert _artifacts(tmp_path) == (False, False, False)


def test_op_21g_the_progress_state_machine_refuses_an_illegal_transition() -> None:
    progress = owned._Progress()
    assert progress.state is OwnedPipelineState.UNSTARTED
    with pytest.raises(OwnedPipelineError):
        progress.advance(OwnedPipelineState.TRACKED)
    progress.advance(OwnedPipelineState.SCHEDULE_VALIDATED)
    assert progress.state is OwnedPipelineState.SCHEDULE_VALIDATED


# --------------------------------------------------------------------------------------
# canonical-object hygiene for both owned documents
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME))
def test_op_22a_a_non_json_owned_document_is_refused(tmp_path: Path, name: str) -> None:
    _run(tmp_path, _disappearance_source())
    (tmp_path / name).write_bytes(b"{not json")
    if name == ACQUISITION_LEDGER_NAME:
        _repin(tmp_path, acquisition_ledger_sha256=_digest(b"{not json"))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("name", (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME))
def test_op_22b_a_non_object_owned_document_is_refused(tmp_path: Path, name: str) -> None:
    _run(tmp_path, _disappearance_source())
    (tmp_path / name).write_bytes(b"[]")
    if name == ACQUISITION_LEDGER_NAME:
        _repin(tmp_path, acquisition_ledger_sha256=_digest(b"[]"))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("name", (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME))
def test_op_22c_an_owned_document_with_an_extra_key_is_refused(
    tmp_path: Path, name: str
) -> None:
    _run(tmp_path, _disappearance_source())
    value = _read(tmp_path, name)
    value["provenance"] = "trust me"
    _write(tmp_path, name, value)
    if name == ACQUISITION_LEDGER_NAME:
        _repin(
            tmp_path,
            acquisition_ledger_sha256=_digest((tmp_path / name).read_bytes()),
        )
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("name", (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME))
def test_op_22d_a_non_canonically_encoded_owned_document_is_refused(
    tmp_path: Path, name: str
) -> None:
    _run(tmp_path, _disappearance_source())
    value = _read(tmp_path, name)
    payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
    (tmp_path / name).write_bytes(payload)
    if name == ACQUISITION_LEDGER_NAME:
        _repin(tmp_path, acquisition_ledger_sha256=_digest(payload))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("name", (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME))
def test_op_22e_a_non_canonically_representable_owned_document_is_refused(
    tmp_path: Path, name: str
) -> None:
    """``json.loads`` accepts NaN; the canonical form does not."""

    _run(tmp_path, _disappearance_source())
    value = _read(tmp_path, name)
    value["sample_count"] = float("nan")
    payload = json.dumps(
        value, allow_nan=True, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    (tmp_path / name).write_bytes(payload)
    if name == ACQUISITION_LEDGER_NAME:
        _repin(tmp_path, acquisition_ledger_sha256=_digest(payload))
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    ("name", "key", "value"),
    (
        (ACQUISITION_LEDGER_NAME, "schema_version", "other/v9"),
        (ACQUISITION_LEDGER_NAME, "pipeline_version", "9.9.9"),
        (ACQUISITION_LEDGER_NAME, "canonicalization", {"encoding": "utf-16"}),
        (ACQUISITION_LEDGER_NAME, "frame_encoding", {"dtype": "uint8"}),
        (ACQUISITION_LEDGER_NAME, "frame_materialization", {"absent_matter": 0.4}),
        (ACQUISITION_LEDGER_NAME, "frame_directory_relative_path", "elsewhere"),
        (ACQUISITION_LEDGER_NAME, "provenance_disclosure", "audited and certified"),
        (ACQUISITION_LEDGER_NAME, "invocation_count", 3),
        (OWNED_BINDING_NAME, "provenance_disclosure", "audited and certified"),
        (OWNED_BINDING_NAME, "schema_version", "other/v9"),
        (OWNED_BINDING_NAME, "pipeline_version", "9.9.9"),
        (OWNED_BINDING_NAME, "canonicalization", {"encoding": "utf-16"}),
        (OWNED_BINDING_NAME, "acquisition_ledger_relative_path", "ELSEWHERE.json"),
        (OWNED_BINDING_NAME, "completion_manifest_relative_path", "ELSEWHERE.json"),
        (OWNED_BINDING_NAME, "lifecycle_document_relative_path", "ELSEWHERE.json"),
        (OWNED_BINDING_NAME, "sample_count", 3),
        (OWNED_BINDING_NAME, "sampled_frames", [0, 5, 11, 13]),
        (OWNED_BINDING_NAME, "entries_sha256", "0" * 64),
        (OWNED_BINDING_NAME, "acquisition_ledger_sha256", "0" * 64),
        (OWNED_BINDING_NAME, "completion_manifest_sha256", "0" * 64),
        (OWNED_BINDING_NAME, "lifecycle_document_sha256", "0" * 64),
    ),
)
def test_op_22f_every_declared_owned_field_is_tamper_covered(
    tmp_path: Path, name: str, key, value
) -> None:
    _run(tmp_path, _disappearance_source())
    document = _read(tmp_path, name)
    assert key in document
    document[key] = value
    _write(tmp_path, name, document)
    if name == ACQUISITION_LEDGER_NAME:
        _repin(
            tmp_path,
            acquisition_ledger_sha256=_digest((tmp_path / name).read_bytes()),
        )
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    "schedule",
    (
        pytest.param("0,5", id="not a list"),
        pytest.param([], id="empty"),
        pytest.param([0, 5, 5, 12], id="not strictly increasing"),
        pytest.param([0, 5, -1, 12], id="negative"),
        pytest.param([0, 5, True, 12], id="bool"),
        pytest.param([0, 5, "11", 12], id="non-integer"),
    ),
)
def test_op_22g_a_malformed_persisted_schedule_is_refused(tmp_path: Path, schedule) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = schedule
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    ("document", "path", "value"),
    (
        pytest.param(ACQUISITION_LEDGER_NAME, ("sample_count",), True, id="ledger count is a bool"),
        pytest.param(
            ACQUISITION_LEDGER_NAME, ("invocation_count",), True, id="invocation count is a bool"
        ),
        pytest.param(
            ACQUISITION_LEDGER_NAME, ("entries", 0, "sequence_position"), False,
            id="row position is a bool",
        ),
        pytest.param(
            ACQUISITION_LEDGER_NAME, ("entries", 0, "invocation_ordinal"), False,
            id="row ordinal is a bool",
        ),
        pytest.param(
            ACQUISITION_LEDGER_NAME, ("entries", 0, "true_cell_count"), True,
            id="row cell count is a bool",
        ),
        pytest.param(OWNED_BINDING_NAME, ("sample_count",), 4.0, id="binding count is a float"),
    ),
)
def test_op_22j_boolean_and_float_slop_is_refused_in_integer_fields(
    tmp_path: Path, document, path, value
) -> None:
    """Reviewer A minor 1 / Reviewer B minor 2.  ``True == 1`` must not satisfy a count."""

    _run(tmp_path, RecordingSource([BLOB_A]), (0,))
    value_document = _read(tmp_path, document)
    target = value_document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    if document == ACQUISITION_LEDGER_NAME:
        _repin_ledger(tmp_path, value_document)
    else:
        _write(tmp_path, document, value_document)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_22g2_a_non_increasing_schedule_matching_its_rows_is_typed(tmp_path: Path) -> None:
    """Reviewer B, minor 3.  The per-row label check cannot stand in for this one.

    Here the rows agree with the schedule, so only the monotonicity check on the re-read
    schedule can object.  Without it the failure would surface as an untyped ``ValueError``
    out of the accepted tracker instead of an ``OwnedEvidenceError``.
    """

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["sampled_frames"] = [0, 5, 5, 12]
    ledger["entries"][2]["requested_sample_label"] = 5
    _repin_ledger(tmp_path, ledger)
    _repin(tmp_path, sampled_frames=[0, 5, 5, 12])
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize(
    ("block", "field", "value"),
    (
        ("detector_spec", "min_cells", "1"),
        ("detector_spec", "min_cells", 1.9),
        ("detector_spec", "min_cells", True),
        ("detector_spec", "matter_threshold", "0.5"),
        ("detector_spec", "matter_threshold", True),
        ("tracker_spec", "dilation_radius", "1"),
        ("tracker_spec", "dilation_radius", 1.9),
        ("tracker_spec", "dilation_radius", True),
        ("tracker_spec", "max_area_ratio", "4.0"),
        ("tracker_spec", "max_centroid_displacement", True),
    ),
)
def test_op_22k_specification_type_slop_is_refused(
    tmp_path: Path, block, field, value
) -> None:
    """Reviewer A, round two, material 2.  The coercion made the recorded specification
    need not be the one applied: ``1.9`` silently ran as ``1``."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger[block][field] = value
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


@pytest.mark.parametrize("shape", ([-1, -120], [-10, -12], [1, 240], [2, 60]))
def test_op_22l_a_degenerate_or_negative_persisted_shape_is_typed(
    tmp_path: Path, shape
) -> None:
    """Reviewer A, round two, material 3.  A negative shape reached ``reshape`` and left an
    untyped ``ValueError`` escaping ``OwnedPipelineError``."""

    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["shape"] = shape
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_22m_a_boolean_requested_sample_label_is_refused(tmp_path: Path) -> None:
    """Reviewer A, round two, material 4.  ``false == 0`` matched the label ``0``."""

    _run(tmp_path, RecordingSource([BLOB_A, BLOB_A]), (0, 1))
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0]["requested_sample_label"] = False
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_22n_an_array_that_misreports_its_geometry_cannot_describe_its_bytes(
    tmp_path: Path,
) -> None:
    """Reviewer A round one, minor 3, now pinned.  Geometry comes from the owned copy."""

    class LyingMask(np.ndarray):
        @property
        def shape(self):
            return (SHAPE[1], SHAPE[0])

    def source(position, label):
        return BLOB_A.copy().view(LyingMask)

    record = _run(tmp_path, source, (0, 1, 2, 3))
    assert record.frame_shape == SHAPE
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    assert ledger["entries"][0]["shape"] == [SHAPE[0], SHAPE[1]]


def test_op_22h_a_non_list_entries_block_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"] = {"0": "row"}
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


def test_op_22i_a_non_object_ledger_row_is_refused(tmp_path: Path) -> None:
    _run(tmp_path, _disappearance_source())
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    ledger["entries"][0] = "row"
    _repin_ledger(tmp_path, ledger)
    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path)


# --------------------------------------------------------------------------------------
# the recorded limitation: invocation provenance, not physical time
# --------------------------------------------------------------------------------------


def test_op_23a_a_far_future_label_records_an_invocation_not_elapsed_time(
    tmp_path: Path,
) -> None:
    """Three samples, the last labelled 1,000,000.

    The run is valid and the ledger records three invocations at three declared labels.
    It proves nothing whatsoever about a million elapsed physical steps, and -- per OP-L4 --
    the recorded count is a within-process witness, not an externally verifiable one.  This
    test exists to pin the limitation, not to celebrate a capability.
    """

    source = RecordingSource([BLOB_A, BLOB_A, BLOB_A])
    record = _run(tmp_path, source, (0, 1, 1_000_000))
    assert source.calls == [(0, 0), (1, 1), (2, 1_000_000)]
    assert record.invocation_count == 3
    assert record.sample_count == 3
    ledger = _read(tmp_path, ACQUISITION_LEDGER_NAME)
    assert ledger["sample_count"] == 3
    assert ledger["invocation_count"] == 3
    assert ledger["sampled_frames"] == [0, 1, 1_000_000]
    assert "not evidence of physical elapsed time" in ledger["provenance_disclosure"]
    assert isinstance(open_owned_analysis_access(tmp_path), AnalysisAccess)


def test_op_23b_the_external_clock_limitation_is_stated_where_a_reader_will_meet_it(
    tmp_path: Path,
) -> None:
    """Reviewer B, observation 1.  Prose in one docstring is not a disclosure."""

    text = Path(owned.__file__).read_text(encoding="utf-8")
    assert "one million physical engine steps elapsed" in text
    assert "never an authority certificate" in text
    # every limitation carries an identifier, and OP-L1 exists
    for limitation in ("OP-L1", "OP-L2", "OP-L3", "OP-L4", "OP-L5", "OP-L6", "OP-L7"):
        assert limitation in text, limitation
    # both public entry points repeat it, not just the module header
    assert "physical engine steps elapsed" in owned.run_owned_future_pipeline.__doc__
    assert "REPRODUCTION, not acquisition" in owned.open_owned_analysis_access.__doc__
    # and it is legible on disk, to a consumer who never reads the source
    _run(tmp_path, _disappearance_source())
    for name in (ACQUISITION_LEDGER_NAME, OWNED_BINDING_NAME):
        disclosure = _read(tmp_path, name)["provenance_disclosure"]
        assert "not evidence of physical elapsed time" in disclosure
        assert "caller-declared and carries no authority" in disclosure
        assert "bind bytes, not authority" in disclosure


def test_op_23c_the_identity_document_is_stored_as_a_caller_declaration(
    tmp_path: Path,
) -> None:
    _run(tmp_path, _disappearance_source())
    identity = _read(tmp_path, ACQUISITION_LEDGER_NAME)["acquisition_source_identity"]
    assert identity == {
        "authority": "NONE",
        "declared": dict(IDENTITY),
        "declared_by": "caller",
    }


def test_op_23f_the_returned_capability_carries_no_owned_evidence(tmp_path: Path) -> None:
    """LIMITATION OP-L6, pinned.  Reviewer A, material 5.

    The capability is the accepted runner's.  It reports the twelve completion-manifest
    fields and nothing about the acquisition ledger, so a downstream consumer holding one
    cannot tell an owned run from an unowned one.  The owned guarantee attaches to the call
    that produced it, not to the object.
    """

    _run(tmp_path, _disappearance_source())
    evidence = open_owned_analysis_access(tmp_path).verified_completion_evidence()
    assert set(evidence) == {
        "canonicalization",
        "disposition",
        "integration_version",
        "lifecycle_document_relative_path",
        "lifecycle_document_sha256",
        "lifecycle_input_sha256",
        "lifecycle_records_sha256",
        "lifecycle_schema_version",
        "lifecycle_validator_version",
        "sampled_frames",
        "schema_version",
        "terminal_record_count",
    }
    for owned_field in ("acquisition", "ledger", "invocation", "frame_sha256", "source_bindings"):
        assert owned_field not in evidence


def test_op_23g_a_copied_run_directory_verifies_elsewhere_and_this_is_disclosed(
    tmp_path: Path,
) -> None:
    """LIMITATION OP-L3, second half, pinned.  Evidence is content-addressed."""

    first = tmp_path / "first"
    first.mkdir()
    _run(first, _disappearance_source())
    second = tmp_path / "second"
    shutil.copytree(first, second)
    assert isinstance(open_owned_analysis_access(second), AnalysisAccess)
    text = Path(owned.__file__).read_text(encoding="utf-8")
    assert "Copying a whole genuine run directory to another directory" in text


def test_op_23d_no_engine_or_scientific_surface_is_introduced() -> None:
    text = Path(owned.__file__).read_text(encoding="utf-8")
    assert "LatticeBondEngine" not in text
    assert "stage_b" not in text.lower()
    assert "step(" not in text
    assert set(owned.__all__) == {
        "ACQUISITION_FRAME_DIRECTORY",
        "ACQUISITION_LEDGER_NAME",
        "OWNED_BINDING_NAME",
        "PIPELINE_VERSION",
        "SCHEMA_VERSION",
        "OwnedAcquisitionError",
        "OwnedAcquisitionEvidence",
        "OwnedEvidenceError",
        "OwnedPipelineError",
        "OwnedPipelineRecord",
        "OwnedPipelineState",
        "OwnedPublicationError",
        "OwnedScheduleError",
        "open_owned_analysis_access",
        "run_owned_future_pipeline",
    }


def test_op_23e_the_accepted_stack_sources_change_only_under_a_declared_mission() -> None:
    """The owned pipeline is additive.  The only permitted divergence is the Route E
    guard installed by FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_FINAL, and it must be
    declared in the successor qualification, never silent."""

    import hashlib as _h
    import json as _j

    repo = Path(owned.__file__).resolve().parents[3]
    successor = _j.loads(
        (repo / "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json")
        .read_text(encoding="utf-8")
    )
    declared = successor["route_e_guard_installation"]
    assert declared["mission"] == "FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_FINAL"
    for relative, entry in declared["sources_changed"].items():
        observed = _h.sha256((repo / relative).read_bytes()).hexdigest()
        assert observed == entry["current_sha256"], relative
        assert "_refuse_route_e_signal" in (repo / relative).read_text(encoding="utf-8")

    root = Path(owned.__file__).parent
    expected = {
        "instrumentation.py": (
            "65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef"
        ),
        "lifecycle.py": "3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053",
        "future_lifecycle_runner.py": (
            "7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08"
        ),
        "__init__.py": "9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0",
    }
    for name, digest in expected.items():
        relative = f"edlab/substrates/lattice_bond/{name}"
        if relative in declared["sources_changed"]:
            continue  # declared above, with its current digest
        assert _digest((root / name).read_bytes()) == digest, name
