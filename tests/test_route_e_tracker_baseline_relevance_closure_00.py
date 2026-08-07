"""ROUTE_E_TRACKER_BASELINE_RELEVANCE_CLOSURE_00.

The four differential controls
``test_independent_tracker_matches_split_merge_tie_and_collapse[split|merge|tie|collapse]``
were red with ``TypeError: track_components() missing 1 required keyword-only argument:
'sampled_frames'``.  That is a **qualification defect**, not a tracker defect: the call
site had not been updated when ``sampled_frames`` became mandatory, so the control never
reached the comparison at all.  Once the fixture's own schedule is declared, the four
controls pass against the frozen independent oracle **without one expectation being
touched** -- no semantic divergence is observed, so the production tracker is not
declared wrong (Case A).

This file closes the second, larger half: the four scenarios must not merely pass an
in-memory parity check, they must traverse the **real Route E disk helper**
(``future_lifecycle_owned_pipeline.rebuild_tracking_and_components``) -- persisted
frames, re-read bytes, re-run detector, re-run mandatory tracker -- and only *then* be
compared to the independent oracle.  The canonical join built from that rebuilt tracking
is persisted, re-read, and the real consumer ``verify_route_e_run`` is exercised on a
real ``run_route_e`` run.

ROUND 2 -- ROUTE_E_EMPTY_RIGHT_NONUNIT_DISK_CLOSURE_00.  The ``collapse`` scenario has
component counts ``[2, 1, 2]``: no empty right frame, no dissolution.  It is therefore
supplementary coverage and is NOT proof of the conjunction ``empty right frame x non-unit
cadence x persisted frames x rebuild_tracking_and_components x real Route E consumer``.
That conjunction is carried by the ``empty_right_nonunit_cadence_tracker_repair`` section
at the bottom of this file, on the frozen ``test_r1`` fixture: ``SEPARATED, _collapsed(),
SEPARATED, EMPTY`` at ``(0, 5, 11, 40)``, component counts ``[2, 1, 2, 0]``, with frame 40
a genuine persisted zero-component artefact.

Rules honoured here, verbatim from the brief:

* the independent oracle ``stage_b_reproduce.track_components`` is **not modified** and
  its expectations are **not replaced**;
* production and oracle do **not** derive from the same helper: production goes through
  ``rebuild_tracking_and_components`` reading bytes off disk, the oracle re-detects from
  raw masks with its own detector and tracks with its own algorithm;
* ``sampled_frames`` stays mandatory: no ``None``, no implicit default, no fallback
  reconstructing it.  Every value used here is the schedule the fixture itself realised
  and that the pipeline persisted in ``ACQUISITION.json``;
* no failure is masked by ``skip``, ``xfail``, renaming or a relaxed assertion;
* the only spy used wraps the **real** function to demonstrate the call.  No result is
  substituted.

ENGINEERING_ONLY / NOT_SCIENTIFIC_DATA / NOT_ELIGIBLE_FOR_ANALYSIS.
No scientific law, seed, family, horizon, holdout, threshold or Stage-B dataset is
opened, read or written anywhere in this file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import DetectorSpec, TrackerSpec
from edlab.substrates.lattice_bond import stage_b_reproduce as raw_reproduce
from edlab.substrates.lattice_bond.lifecycle import qualify_lifecycle_contract
from edlab.substrates.lattice_bond import future_route_e_admission as admission
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks
from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    ACQUISITION_LEDGER_NAME,
    OwnedEvidenceError,
    OwnedScheduleError,
    rebuild_tracking_and_components,
    run_owned_future_pipeline,
)

from tests.test_future_route_e_execution_boundary_00 import (  # noqa: E402
    _beacon,
    _bundle,
    _destination,
    _manifest,
    requires_verifier,
)

CANARY = ("ENGINEERING_ONLY", "NOT_SCIENTIFIC_DATA", "NOT_ELIGIBLE_FOR_ANALYSIS")

SHAPE = (10, 12)
DETECTOR = DetectorSpec(matter_threshold=0.5, min_cells=1)


def _mask(cells) -> np.ndarray:
    value = np.zeros(SHAPE, dtype=bool)
    for y, x in cells:
        value[y % SHAPE[0], x % SHAPE[1]] = True
    return value


# --------------------------------------------------------------------------------------
# The four scenario geometries.  They are *character for character* the geometries of the
# existing differential control in tests/test_lattice_bond_stage_b.py, so what is
# qualified through the Route E disk path is the very sequence the baseline compares
# against the frozen oracle -- not a look-alike.
# --------------------------------------------------------------------------------------

_JOINED = _mask({(4, x) for x in range(3, 8)})
_SEPARATED = _mask({(4, 3), (4, 4), (4, 6), (4, 7)})
_WIDE = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)})
_COLLAPSED = _WIDE.copy()
_COLLAPSED[4, 4:7] = True

#: ``scenario -> (masks, tracker spec, declared schedule, required event kind)``.
#:
#: ``collapse`` is declared at a **non-unit cadence** ``(0, 4, 9)``.  CORRECTION, round 2:
#: this scenario is SUPPLEMENTARY COVERAGE ONLY.  It has component counts ``[2, 1, 2]``,
#: no empty right frame and no dissolution, so it does NOT qualify the conjunction
#: ``empty right frame x non-unit cadence x persisted frames x rebuild_tracking_and_components
#: x real Route E consumer`` and must never be quoted as proof of it.  That conjunction is
#: carried by the ``empty_right_nonunit_cadence_tracker_repair`` section at the bottom of
#: this file, on the frozen ``test_r1`` fixture ``(0, 5, 11, 40)``.
SCENARIOS: dict[str, tuple[list[np.ndarray], TrackerSpec, tuple[int, ...], str]] = {
    "split": ([_JOINED, _SEPARATED], TrackerSpec(3.0, 4.0, 1, 1e-12), (0, 1), "SPLIT"),
    "merge": ([_SEPARATED, _JOINED], TrackerSpec(3.0, 4.0, 1, 1e-12), (0, 1), "MERGE"),
    "tie": (
        [_mask({(4, 3), (4, 7)}), _mask({(3, 5), (5, 5)})],
        TrackerSpec(5.0, 3.0, 3, 1e-12),
        (0, 1),
        "TRACKING_UNRESOLVED",
    ),
    "collapse": (
        [_WIDE, _COLLAPSED, _WIDE],
        TrackerSpec(3.0, 4.0, 1, 1e-12),
        (0, 4, 9),
        "TRACKING_UNRESOLVED",
    ),
}

NON_UNIT_CADENCE_SCENARIO = "collapse"


class _MaskSource:
    """A synthetic acquisition source.  It returns the fixture mask for a position.

    It records every ``(position, label)`` it was called with, so the schedule the
    pipeline actually drove can be compared with the schedule declared.
    """

    def __init__(self, masks) -> None:
        self._masks = list(masks)
        self.calls: list[tuple[int, int]] = []

    def __call__(self, position: int, label: int) -> np.ndarray:
        self.calls.append((int(position), int(label)))
        return self._masks[position]


def _owned_run(directory: Path, scenario: str):
    """Drive one scenario through the REAL owned pipeline, onto real disk."""
    masks, tracker, schedule, _ = SCENARIOS[scenario]
    directory.mkdir(parents=True)
    source = _MaskSource(masks)
    record = run_owned_future_pipeline(
        directory,
        acquisition_source=source,
        sampled_frames=schedule,
        detector_spec=DETECTOR,
        tracker_spec=tracker,
        acquisition_source_identity={
            "kind": "handcrafted-synthetic-mask",
            "name": f"route-e-tracker-baseline-{scenario}",
        },
    )
    return record, source


def _oracle(scenario: str):
    """The frozen independent oracle, run on the raw masks with its own detector.

    Nothing here is taken from the production detector, the production tracker or the
    disk helper: the oracle re-derives its own components from the raw field.
    """
    masks, tracker, _, _ = SCENARIOS[scenario]
    raw_frames = [
        raw_reproduce.detect_components(
            np.where(mask, 0.8, 0.1).astype(np.float64),
            raw_reproduce.DetectorConfig(0.5, 1),
        )
        for mask in masks
    ]
    raw_tracker = raw_reproduce.TrackerConfig(
        dilation_radius=tracker.dilation_radius,
        max_centroid_displacement=tracker.max_centroid_displacement,
        max_area_ratio=tracker.max_area_ratio,
        unique_score_margin=tracker.unique_score_margin,
    )
    return raw_reproduce.track_components(raw_frames, SHAPE, raw_tracker)


def _oracle_tracks(independent, schedule: tuple[int, ...]):
    """The oracle's tracks, expressed in schedule labels.

    The oracle names the onset frame ``0`` and the right frame of transition ``i`` as
    ``i + 1``: its frame axis is **positional by construction of the oracle itself**.
    Mapping position ``p`` to ``schedule[p]`` is therefore a change of unit, not a change
    of expectation -- it is the identity whenever the cadence is unitary.  The oracle's
    algorithm, its outputs and its expectations are untouched.
    """
    return [
        (
            track.track_id,
            tuple((schedule[point.frame], point.component_index) for point in track.points),
            track.parent_ids,
            track.unresolved,
        )
        for track in independent.tracks
    ]


def _production_tracks(tracking):
    return [
        (
            track.track_id,
            tuple((point.frame, point.component_index) for point in track.points),
            track.parent_track_ids,
            track.unresolved,
        )
        for track in tracking.tracks
    ]


# ======================================================================================
# 1 -- the four scenarios really traverse the Route E disk helper
# ======================================================================================


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_tb_01_scenario_is_persisted_and_rebuilt_from_disk_only(tmp_path, scenario):
    """The frames reach disk and the helper re-reads THEM, not an in-memory hand-off."""
    directory = tmp_path / "run"
    _, source = _owned_run(directory, scenario)
    masks, _, schedule, _ = SCENARIOS[scenario]

    # the pipeline drove exactly the declared schedule, one call per sample
    assert source.calls == [(position, label) for position, label in enumerate(schedule)]

    ledger = json.loads((directory / ACQUISITION_LEDGER_NAME).read_bytes().decode("utf-8"))
    assert tuple(ledger["sampled_frames"]) == schedule
    assert ledger["sample_count"] == len(masks)

    frame_directory = directory / owned.ACQUISITION_FRAME_DIRECTORY
    persisted = sorted(path.name for path in frame_directory.iterdir())
    assert len(persisted) == len(masks), "one persisted frame per declared sample"

    tracking, components_by_frame = rebuild_tracking_and_components(directory)
    # the helper indexes its support map by SCHEDULE LABEL, never by position
    assert sorted(components_by_frame) == sorted(schedule)
    assert all(point.frame in schedule for track in tracking.tracks for point in track.points)


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_tb_02_disk_rebuilt_tracking_matches_the_independent_oracle(tmp_path, scenario):
    """The differential control, now posed across the Route E disk path.

    The left-hand side comes from bytes on disk through the production detector and the
    production mandatory tracker; the right-hand side comes from the frozen independent
    oracle, which shares no helper with it.  The oracle's expectations are used as they
    are.
    """
    directory = tmp_path / "run"
    _owned_run(directory, scenario)
    _, _, schedule, event_name = SCENARIOS[scenario]

    tracking, _ = rebuild_tracking_and_components(directory)
    independent = _oracle(scenario)

    assert _oracle_tracks(independent, schedule) == _production_tracks(tracking)

    production_unresolved = any(track.unresolved for track in tracking.tracks) or any(
        event.kind == "TRACKING_UNRESOLVED" for event in tracking.events
    )
    assert independent.unresolved == production_unresolved

    assert any(event.kind == event_name for event in tracking.events)
    assert any(event["event"] == event_name for event in independent.events)

    # every event the oracle emits is emitted by the disk-rebuilt production tracking,
    # at the same schedule label.  (Production additionally emits the onset APPEARANCE
    # events, which the oracle does not model; that is a pre-existing, declared
    # difference and is not silently absorbed here -- it is asserted as a superset.)
    oracle_events = {(schedule[event["frame"]], event["event"]) for event in independent.events}
    production_events = {(event.frame, event.kind) for event in tracking.events}
    assert oracle_events <= production_events
    assert all(frame in schedule for frame, _ in production_events)


def test_tb_03_at_least_one_scenario_runs_at_non_unit_cadence(tmp_path):
    """Supplementary non-unit-cadence coverage.

    CORRECTION, round 2: this test proves the schedule is not a positional surrogate.
    It does NOT prove the empty-right-frame conjunction -- its right frames are never
    empty.  See the ``empty_right_nonunit_cadence_tracker_repair`` section below.
    """
    _, _, schedule, _ = SCENARIOS[NON_UNIT_CADENCE_SCENARIO]
    assert schedule != tuple(range(len(schedule))), "this scenario must not be unit cadence"

    directory = tmp_path / "run"
    _owned_run(directory, NON_UNIT_CADENCE_SCENARIO)
    tracking, components_by_frame = rebuild_tracking_and_components(directory)

    observed = {point.frame for track in tracking.tracks for point in track.points}
    assert observed <= set(schedule)
    assert observed & {value for value in schedule if value != schedule[0]}, (
        "the non-unit labels must actually appear; a positional cadence would give 0,1,2"
    )
    assert set(components_by_frame) == set(schedule)
    assert set(components_by_frame) != set(range(len(schedule)))


# ======================================================================================
# 2 -- the canonical join is built from the rebuilt tracking, persisted and re-read
# ======================================================================================


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_tb_04_join_is_built_persisted_and_re_read_for_every_scenario(tmp_path, scenario):
    directory = tmp_path / "run"
    _owned_run(directory, scenario)
    _, _, schedule, _ = SCENARIOS[scenario]

    tracking, components_by_frame = rebuild_tracking_and_components(directory)
    records = locks.build_track_component_join(tracking, components_by_frame)
    assert records, "an empty join is never admissible"

    path, digest = locks.write_join_evidence(directory, records)
    assert path.is_file()

    # forget everything and re-read the bytes
    del records, tracking, components_by_frame
    reread, reread_digest = locks.read_join_evidence(path)
    assert reread_digest == digest == locks.join_digest(reread)
    assert {row.frame for row in reread} <= set(schedule)
    assert all(len(row.cell_set_sha256) == 64 for row in reread)


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_tb_05_restart_from_disk_reproduces_the_same_join_digest(tmp_path, scenario):
    """A second, independent read of the same bytes yields the same canonical join."""
    directory = tmp_path / "run"
    _owned_run(directory, scenario)

    first_tracking, first_components = rebuild_tracking_and_components(directory)
    first = locks.join_digest(locks.build_track_component_join(first_tracking, first_components))

    second_tracking, second_components = rebuild_tracking_and_components(directory)
    second = locks.join_digest(
        locks.build_track_component_join(second_tracking, second_components)
    )
    assert first == second

    # and a byte-identical acquisition replayed into a fresh directory agrees too
    twin = tmp_path / "twin"
    _owned_run(twin, scenario)
    twin_tracking, twin_components = rebuild_tracking_and_components(twin)
    assert (
        locks.join_digest(locks.build_track_component_join(twin_tracking, twin_components))
        == first
    )


# ======================================================================================
# 3 -- sampled_frames stays mandatory and incompatible schedules are refused
# ======================================================================================


def test_tb_06_a_schedule_incompatible_with_the_sequence_is_refused(tmp_path):
    """No implicit default, no reconstruction: an incompatible schedule is an error."""
    masks, tracker, _, _ = SCENARIOS["collapse"]

    cases = (
        (None, OwnedScheduleError, "mandatory", False),
        ((), OwnedScheduleError, "must not be empty", False),
        ((0, 4, 4), OwnedScheduleError, "strictly increasing", False),
        ((0, -4, 9), OwnedScheduleError, "non-negative", False),
        ({0, 4, 9}, OwnedScheduleError, "ordered sequence", False),
        # well-formed in isolation, but longer than the sequence it claims to describe:
        # the acquisition is driven by the schedule, so the mismatch surfaces as a hard
        # acquisition failure rather than being quietly truncated to the shorter side.
        ((0, 4, 9, 12), owned.OwnedAcquisitionError, "sequence position 3", True),
    )
    for index, (bad, error, expected, acquired) in enumerate(cases):
        directory = tmp_path / f"bad-{index:02d}"
        directory.mkdir()
        with pytest.raises(error) as raised:
            run_owned_future_pipeline(
                directory,
                acquisition_source=_MaskSource(masks),
                sampled_frames=bad,
                detector_spec=DETECTOR,
                tracker_spec=tracker,
                acquisition_source_identity={
                    "kind": "handcrafted-synthetic-mask",
                    "name": "route-e-tracker-baseline-refusal",
                },
            )
        assert expected in str(raised.value)
        if not acquired:
            assert not (directory / owned.ACQUISITION_FRAME_DIRECTORY).exists(), (
                "a malformed schedule must be refused before any acquisition"
            )
        # in no case is a run published
        assert not (directory / ACQUISITION_LEDGER_NAME).exists()


def test_tb_07_a_tampered_persisted_schedule_is_refused_by_the_disk_helper(tmp_path):
    """The helper trusts bytes, and only bytes that still cohere."""
    directory = tmp_path / "run"
    _owned_run(directory, NON_UNIT_CADENCE_SCENARIO)
    assert rebuild_tracking_and_components(directory) is not None

    ledger_path = directory / ACQUISITION_LEDGER_NAME
    document = json.loads(ledger_path.read_bytes().decode("utf-8"))
    document["sampled_frames"] = [0, 1, 2]  # a positional surrogate, silently substituted
    ledger_path.write_bytes(
        json.dumps(
            document, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    )
    with pytest.raises(OwnedEvidenceError):
        rebuild_tracking_and_components(directory)


def test_tb_08_the_production_tracker_has_no_schedule_free_path():
    """``sampled_frames`` is keyword-only, mandatory, and ``None`` is refused."""
    import inspect

    from edlab.substrates.lattice_bond.instrumentation import track_components

    parameter = inspect.signature(track_components).parameters["sampled_frames"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty

    with pytest.raises(TypeError):
        track_components((), TrackerSpec(3.0, 4.0, 1, 1e-12))
    with pytest.raises(ValueError, match="mandatory"):
        track_components((), TrackerSpec(3.0, 4.0, 1, 1e-12), sampled_frames=None)


# ======================================================================================
# 4 -- the real consumer: run_route_e uses THIS helper, and admission requires its output
# ======================================================================================


@requires_verifier
def test_tb_09_run_route_e_calls_the_real_disk_helper_and_persists_its_join(tmp_path, monkeypatch):
    """A spy that WRAPS the real function -- no result is substituted."""
    real = execution.rebuild_tracking_and_components
    seen: list[Path] = []

    def spy(run_directory):
        seen.append(Path(run_directory))
        return real(run_directory)  # the real return value, unmodified

    monkeypatch.setattr(execution, "rebuild_tracking_and_components", spy)

    document = _manifest()
    bundle_dir, _ = _bundle(tmp_path, document)
    record = execution.run_route_e(
        bundle_dir, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"])
    )

    world = Path(record.output_directory) / execution.WORLDS_DIRECTORY / "000000"
    assert seen == [world], "run_route_e did not drive the real disk helper once per world"

    join_path = world / locks.JOIN_EVIDENCE_FILENAME
    persisted, digest = locks.read_join_evidence(join_path)
    tracking, components = real(world)
    assert locks.join_digest(locks.build_track_component_join(tracking, components)) == digest
    assert persisted, "the persisted join carries no row"


@requires_verifier
def test_tb_10_admission_accepts_intact_join_evidence_and_refuses_a_broken_one(tmp_path):
    document = _manifest()
    bundle_dir, _ = _bundle(tmp_path / "a", document)
    record = execution.run_route_e(
        bundle_dir,
        _beacon(tmp_path / "a"),
        _destination(tmp_path / "a", document["output_namespace"]),
    )
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert verdict.admissible, verdict

    other = _manifest()
    other_bundle, _ = _bundle(tmp_path / "b", other)
    broken = execution.run_route_e(
        other_bundle,
        _beacon(tmp_path / "b"),
        _destination(tmp_path / "b", other["output_namespace"]),
    )
    world = Path(broken.output_directory) / execution.WORLDS_DIRECTORY / "000000"
    join_path = world / locks.JOIN_EVIDENCE_FILENAME
    payload = json.loads(join_path.read_bytes().decode("ascii"))
    payload["join"][0][2] = int(payload["join"][0][2]) + 1
    join_path.write_bytes(
        json.dumps(
            payload, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
        ).encode("ascii")
    )
    refused = admission.verify_route_e_run(Path(broken.output_directory))
    assert not refused.admissible
    assert refused.reason_code in {
        "JOIN_EVIDENCE_INVALID",
        "JOIN_EVIDENCE_MISMATCH",
        "FILE_INVENTORY_INEXACT",
    }


def test_tb_11_engineering_canary_and_scope():
    """This file opens nothing scientific, and the oracle module is untouched here.

    The canary is asserted rather than assumed, and the independent oracle is checked to
    be reachable only through its own public tracker: this suite never reaches into it
    to build production expectations.
    """
    for token in CANARY:
        assert token in __doc__

    # the oracle is used, never patched: the attribute this suite calls is the module's
    # own function object, not a test double installed over it.
    assert raw_reproduce.track_components.__module__.endswith("stage_b_reproduce")
    assert not hasattr(raw_reproduce.track_components, "__wrapped__")

    # production and oracle do not share a helper: the disk helper lives in the owned
    # pipeline, and the oracle module deliberately imports no project code.
    assert rebuild_tracking_and_components.__module__.endswith(
        "future_lifecycle_owned_pipeline"
    )
    oracle_source = Path(raw_reproduce.__file__).read_text("utf-8")
    assert "future_lifecycle_owned_pipeline" not in oracle_source
    assert "from .instrumentation" not in oracle_source


# ======================================================================================
# 5 -- ROUTE_E_EMPTY_RIGHT_NONUNIT_DISK_CLOSURE_00
#
# The conjunction the `collapse` scenario above does NOT cover:
#
#     empty right frame
#   x non-unit cadence
#   x frames actually persisted
#   x rebuild_tracking_and_components
#   x the real Route E consumer chain
#
# The fixture is the historical witness, taken VERBATIM from
# tests/test_empty_right_nonunit_cadence_tracker_repair.py::test_r1 -- same geometry,
# same schedule, same frozen assertions.  Nothing here is re-invented and nothing there
# is modified; that file stays byte-identical and its test_r1 keeps running unchanged.
# ======================================================================================

#: Transcribed, unchanged, from tests/test_empty_right_nonunit_cadence_tracker_repair.py.
R1_SHAPE = (10, 12)
R1_DETECTOR = DetectorSpec(matter_threshold=0.5, min_cells=1)
R1_TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=4.0, dilation_radius=1)
R1_EMPTY = np.zeros(R1_SHAPE, dtype=bool)
R1_SEPARATED = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)})


def _r1_collapsed() -> np.ndarray:
    value = R1_SEPARATED.copy()
    value[4, 4:7] = True
    return value


R1_SCHEDULE = (0, 5, 11, 40)
R1_MASKS = (R1_SEPARATED, _r1_collapsed(), R1_SEPARATED, R1_EMPTY)
R1_COMPONENT_COUNTS = (2, 1, 2, 0)

#: The positional surrogates the schedule (0, 5, 11, 40) would collapse onto if any code
#: path reconstructed a cadence from transition indices.  No event may carry one.
R1_POSITIONAL_SURROGATES = (1, 2, 3)

#: The oracle names the terminal event DISSOLVE where production names it DISSOLUTION.
#: That naming difference is pre-existing and is declared here rather than absorbed.
_ORACLE_EVENT_NAMES = {"DISSOLVE": "DISSOLUTION"}


class _TrackerSpy:
    """Wraps the REAL tracker.  It records the call and returns the real result.

    No result is substituted and no argument is altered: the wrapped callable is the
    module's own ``track_components``, invoked with exactly the arguments the pipeline
    passed.  Its only purpose is to witness the ``sampled_frames`` the production tracker
    actually received from the disk path.
    """

    def __init__(self, wrapped) -> None:
        self.wrapped = wrapped
        self.calls: list[tuple[int, tuple[int, ...]]] = []

    def __call__(self, frames, spec, *, sampled_frames):
        self.calls.append((len(frames), tuple(int(value) for value in sampled_frames)))
        return self.wrapped(frames, spec, sampled_frames=sampled_frames)


def _r1_oracle():
    """The frozen independent oracle on the r1 masks.  Shares no helper with production."""
    raw_frames = [
        raw_reproduce.detect_components(
            np.where(mask, 0.8, 0.1).astype(np.float64),
            raw_reproduce.DetectorConfig(0.5, 1),
        )
        for mask in R1_MASKS
    ]
    tracking = raw_reproduce.track_components(
        raw_frames,
        R1_SHAPE,
        raw_reproduce.TrackerConfig(
            dilation_radius=R1_TRACKER.dilation_radius,
            max_centroid_displacement=R1_TRACKER.max_centroid_displacement,
            max_area_ratio=R1_TRACKER.max_area_ratio,
            unique_score_margin=R1_TRACKER.unique_score_margin,
        ),
    )
    return raw_frames, tracking


def test_tb_12_empty_right_nonunit_cadence_tracker_repair_through_the_route_e_disk_path(
    tmp_path, monkeypatch
):
    """ONE run id, ONE execution, the whole conjunction.

    Persist (0, 5, 11, 40) including a real EMPTY frame 40, forget everything, re-read the
    bytes through the real acquisition path, re-detect, re-track through the real Route E
    disk helper, and compare the complete canonical form to the frozen independent oracle
    and to the frozen test_r1 assertions.
    """
    directory = tmp_path / "r1"
    directory.mkdir()
    source = _MaskSource(list(R1_MASKS))

    # --- 8. the tracker must be witnessed receiving exactly (0, 5, 11, 40) --------------
    spy = _TrackerSpy(owned.track_components)
    monkeypatch.setattr(owned, "track_components", spy)

    # --- 1/2. persist the four frames and the exact schedule ---------------------------
    try:
        record = run_owned_future_pipeline(
            directory,
            acquisition_source=source,
            sampled_frames=R1_SCHEDULE,
            detector_spec=R1_DETECTOR,
            tracker_spec=R1_TRACKER,
            acquisition_source_identity={
                "kind": "handcrafted-synthetic-mask",
                "name": "empty-right-nonunit-disk-closure-00/r1",
            },
        )
    except OwnedEvidenceError as exc:  # pragma: no cover - reached only under a mutant
        # The acquisition itself succeeded and was re-verified; what refused is the frozen
        # lifecycle contract comparing EVENT FRAMES against the declared schedule.  Raised
        # as an assertion so the cause is unambiguous: this is a semantic frame comparison,
        # not a checksum, an acquisition or an import failure.
        raise AssertionError(
            "event-frame semantics refused on the disk path: every event frame must be a "
            f"declared label of {R1_SCHEDULE}, never a positional surrogate "
            f"{R1_POSITIONAL_SURROGATES}; frozen-contract violations: {exc}"
        ) from exc
    run_identity = str(record.run_identity) if hasattr(record, "run_identity") else str(directory)
    assert source.calls == [(0, 0), (1, 5), (2, 11), (3, 40)]

    ledger = json.loads((directory / ACQUISITION_LEDGER_NAME).read_bytes().decode("utf-8"))
    assert tuple(ledger["sampled_frames"]) == R1_SCHEDULE
    assert ledger["sample_count"] == 4

    # frame 40 is a REAL persisted artefact: a fourth file, present, non-empty as bytes,
    # decoding to a mask with zero true cells.  It is not an absent file, not an omitted
    # entry and not a list truncated before the tracker.
    entries = {int(item["requested_sample_label"]): item for item in ledger["entries"]}
    assert sorted(entries) == list(R1_SCHEDULE)
    terminal = entries[40]
    assert terminal["sequence_position"] == 3
    assert terminal["true_cell_count"] == 0
    assert terminal["shape"] == [R1_SHAPE[0], R1_SHAPE[1]]
    terminal_path = directory / terminal["frame_relative_path"]
    assert terminal_path.is_file()
    payload = terminal_path.read_bytes()
    assert len(payload) == R1_SHAPE[0] * R1_SHAPE[1]
    assert set(payload) == {0}
    assert (
        hashlib.sha256(payload).hexdigest() == terminal["frame_sha256"]
    ), "the empty frame must be covered by the ledger digest like any other frame"
    frame_files = sorted(path.name for path in (directory / owned.ACQUISITION_FRAME_DIRECTORY).iterdir())
    assert len(frame_files) == 4

    # --- 3. forget everything built above ----------------------------------------------
    del record, ledger, entries, terminal, payload

    # --- 4/5/6/7. re-read the bytes; real detector; real disk helper; real tracker ------
    spy.calls.clear()
    tracking, components_by_frame = rebuild_tracking_and_components(directory)

    # --- 8. the witness -----------------------------------------------------------------
    assert spy.calls == [(4, R1_SCHEDULE)], (
        "the production tracker did not receive exactly (0, 5, 11, 40) from the disk path"
    )
    assert spy.wrapped.__module__.endswith("instrumentation")

    assert sorted(components_by_frame) == list(R1_SCHEDULE)
    assert tuple(len(components_by_frame[label]) for label in R1_SCHEDULE) == R1_COMPONENT_COUNTS
    assert components_by_frame[40] == {}, "frame 40 must be present AND carry zero components"

    # --- 9. the complete canonical form, against the independent oracle -----------------
    raw_frames, independent = _r1_oracle()
    assert tuple(len(frame) for frame in raw_frames) == R1_COMPONENT_COUNTS

    assert _oracle_tracks(independent, R1_SCHEDULE) == _production_tracks(tracking)
    assert len(tracking.tracks) == 5
    assert len(tracking.assignments) == 5
    assert len(tracking.edges) == 4
    assert independent.unresolved is True

    production_events = sorted((event.frame, event.kind) for event in tracking.events)
    oracle_events = sorted(
        (R1_SCHEDULE[event["frame"]], _ORACLE_EVENT_NAMES.get(event["event"], event["event"]))
        for event in independent.events
    )
    assert production_events == [
        (0, "APPEARANCE"),
        (0, "APPEARANCE"),
        (5, "TRACKING_UNRESOLVED"),
        (11, "TRACKING_UNRESOLVED"),
        (40, "DISSOLUTION"),
        (40, "DISSOLUTION"),
    ]
    # the oracle emits no onset APPEARANCE; everything it does emit, production emits at
    # the same schedule label
    assert set(oracle_events) <= set(production_events)
    assert oracle_events == [
        (5, "TRACKING_UNRESOLVED"),
        (11, "TRACKING_UNRESOLVED"),
        (40, "DISSOLUTION"),
        (40, "DISSOLUTION"),
    ]

    # every association, source and target, expressed in schedule labels
    assert sorted(
        (
            event.frame,
            event.kind,
            event.source_track_ids,
            event.source_components,
            event.target_components,
            event.target_track_ids,
            event.resolved,
        )
        for event in tracking.events
    ) == [
        (0, "APPEARANCE", (), (), ((0, 0),), (0,), True),
        (0, "APPEARANCE", (), (), ((0, 1),), (1,), True),
        (5, "TRACKING_UNRESOLVED", (0, 1), ((0, 0), (0, 1)), ((5, 0),), (2,), False),
        (11, "TRACKING_UNRESOLVED", (2,), ((5, 0),), ((11, 0), (11, 1)), (3, 4), False),
        (40, "DISSOLUTION", (3,), ((11, 0),), (), (), True),
        (40, "DISSOLUTION", (4,), ((11, 1),), (), (), True),
    ]

    # --- 5 (brief section 5). the causal locks -----------------------------------------
    event_frames = {event.frame for event in tracking.events}
    assert event_frames <= set(R1_SCHEDULE)
    for surrogate in R1_POSITIONAL_SURROGATES:
        assert surrogate not in event_frames, (
            f"positional surrogate {surrogate} appeared where a schedule label was required"
        )
    assert sorted(
        event.frame for event in tracking.events if event.kind == "APPEARANCE"
    ) == [0, 0]
    assert sorted(
        event.frame for event in tracking.events if event.kind == "TRACKING_UNRESOLVED"
    ) == [5, 11]
    assert sorted(
        event.frame for event in tracking.events if event.kind == "DISSOLUTION"
    ) == [40, 40]
    assert not [
        event
        for event in tracking.events
        if event.kind == "TRACKING_UNRESOLVED" and event.frame == 40
    ], "the terminal transition into an empty right frame is a dissolution, not a handoff"

    # no ghost track, no ghost component
    assert {point.frame for track in tracking.tracks for point in track.points} == {0, 5, 11}
    assert all(
        point.component_index in components_by_frame[point.frame]
        for track in tracking.tracks
        for point in track.points
    )

    # --- the frozen test_r1 assertions themselves, re-run on the DISK-rebuilt tracking --
    unresolved = [event for event in tracking.events if event.kind == "TRACKING_UNRESOLVED"]
    assert unresolved
    assert {event.frame for event in unresolved} <= set(R1_SCHEDULE)
    assert 1 not in event_frames
    assert 2 not in event_frames
    assert unresolved[0].frame == 5
    dissolutions = sorted(
        event.frame for event in tracking.events if event.kind == "DISSOLUTION"
    )
    assert dissolutions == [40] * len(dissolutions)
    contract = qualify_lifecycle_contract(tracking, R1_SCHEDULE)
    assert {record.terminal_state for record in contract.terminal_records} == {
        "UNRESOLVED_HANDOFF",
        "DISSOLVED_DETECTED_TRACK",
    }
    assert sorted(
        (record.terminal_state, record.terminal_frame) for record in contract.terminal_records
    ) == [
        ("DISSOLVED_DETECTED_TRACK", 40),
        ("DISSOLVED_DETECTED_TRACK", 40),
        ("UNRESOLVED_HANDOFF", 5),
        ("UNRESOLVED_HANDOFF", 5),
        ("UNRESOLVED_HANDOFF", 11),
    ]
    assert contract.run_terminal_state == "ALL_TRACKS_CLOSED"

    # --- 10/11. the canonical join, its persistence, a real restart, the consumer -------
    records = locks.build_track_component_join(tracking, components_by_frame)
    assert len(records) == 5, "one row per detected component; frame 40 contributes none"
    assert sorted({row.frame for row in records}) == [0, 5, 11]
    join_path, digest = locks.write_join_evidence(directory, records)
    assert join_path.name == locks.JOIN_EVIDENCE_FILENAME

    # forget the whole in-memory chain, then restart from the bytes alone
    del tracking, components_by_frame, records, contract, unresolved
    restarted_tracking, restarted_components = rebuild_tracking_and_components(directory)
    restarted = locks.build_track_component_join(restarted_tracking, restarted_components)
    assert locks.join_digest(restarted) == digest

    # the join the consumer re-reads comes from the persisted bytes, not from memory
    on_disk_bytes = join_path.read_bytes()
    reread, reread_digest = locks.read_join_evidence(join_path)
    assert reread_digest == digest
    assert locks.canonical_join_bytes(reread) == on_disk_bytes
    assert sorted(row.as_tuple() for row in reread) == sorted(
        row.as_tuple() for row in restarted
    )
    # the rows re-read from disk carry exactly the (frame, track) assignments the
    # restarted tracking produced -- no ghost row, no missing row, no relabelling
    assert sorted((row.frame, row.track_id) for row in reread) == sorted(
        (point.frame, track.track_id)
        for track in restarted_tracking.tracks
        for point in track.points
    )
    assert sorted({row.frame for row in reread}) == [0, 5, 11]
    assert 40 not in {row.frame for row in reread}

    # the replay root the real run binds is computable from these re-read bytes alone
    root = locks.route_e_root(
        measurement_root_sha256="0" * 64,
        track_component_join_digest=reread_digest,
        family_enrolment_digest="1" * 64,
    )
    assert isinstance(root, str) and len(root) == 64
    assert run_identity


def test_tb_13_empty_right_nonunit_cadence_tracker_repair_consumer_boundary(tmp_path):
    """Why this fixture stops exactly where it stops -- asserted, not assumed.

    ``verify_route_e_run`` is not a generic evidence reader.  By design (PRB-1/PRB-4) it
    refuses any root that was not produced by the canonical ``run_route_e`` entry point,
    and ``run_route_e`` derives every world frame from the engine through
    ``run_measurement_bridge``: there is no parameter, seam or hook by which a handcrafted
    mask sequence can become a Route E world.  A fixture with an EMPTY right frame at
    non-unit cadence therefore cannot be carried into ``verify_route_e_run`` without
    modifying production source, which this mission forbids.

    That boundary is pinned here as a positive fact rather than worked around, and the
    functions the consumer uses to re-read the join are shown to be the very ones the
    fixture above went through.
    """
    directory = tmp_path / "r1"
    directory.mkdir()
    run_owned_future_pipeline(
        directory,
        acquisition_source=_MaskSource(list(R1_MASKS)),
        sampled_frames=R1_SCHEDULE,
        detector_spec=R1_DETECTOR,
        tracker_spec=R1_TRACKER,
        acquisition_source_identity={
            "kind": "handcrafted-synthetic-mask",
            "name": "empty-right-nonunit-disk-closure-00/boundary",
        },
    )
    tracking, components = rebuild_tracking_and_components(directory)
    locks.write_join_evidence(directory, locks.build_track_component_join(tracking, components))

    verdict = admission.verify_route_e_run(directory)
    assert not verdict.admissible
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"

    # the helper and the join functions this fixture used ARE the ones run_route_e uses
    assert execution.rebuild_tracking_and_components is rebuild_tracking_and_components
    assert execution._locks.build_track_component_join is locks.build_track_component_join
    assert execution._locks.write_join_evidence is locks.write_join_evidence
    assert admission._locks.read_join_evidence is locks.read_join_evidence
