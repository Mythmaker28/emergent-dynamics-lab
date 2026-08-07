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

import json
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import DetectorSpec, TrackerSpec
from edlab.substrates.lattice_bond import stage_b_reproduce as raw_reproduce
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
#: ``collapse`` is deliberately declared at a **non-unit cadence** ``(0, 4, 9)``: the
#: schedule is not the positional index, so any code path that silently reconstructed a
#: cadence from transition indices would produce frame stamps ``0, 1, 2`` and fail here.
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
    """A positional surrogate for the schedule would be visible here and nowhere else."""
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
