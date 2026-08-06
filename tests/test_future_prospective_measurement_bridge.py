"""FUTURE-PROSPECTIVE-MEASUREMENT-BRIDGE-00 — tests.

Every fixture here is a handcrafted small lattice pushed through the real engine,
the real passive tracer, the real detector, the owned pipeline, the frozen lifecycle
validator and the qualified completion gate by the bridge itself.  There is no
scientific input and no seed: the engine is deterministic and has none.

The suite is written to attack the seams: between what the engine did and what was
persisted, between the persisted floats and the persisted mask, between the local
evidence and the external anchor, and between the anchor gate and the owned
analysis capability it protects.
"""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import math
from pathlib import Path
import shutil
import struct
from types import SimpleNamespace

import numpy as np
import pytest

from edlab.substrates.lattice_bond.engine import (
    FaceIntervention,
    LatticeBondEngine,
    LatticeBondSpec,
    LatticeBondState,
    StepResult,
)
from edlab.substrates.lattice_bond.instrumentation import (
    advance_passive_tracer,
    detect_components,
)
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    ACQUISITION_FRAME_DIRECTORY,
    OWNED_BINDING_NAME,
)
from edlab.substrates.lattice_bond import future_prospective_measurement_bridge as mb
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    ANCHOR_RECEIPT_NAME,
    BRIDGE_BINDING_NAME,
    BRIDGE_VERSION,
    MEASUREMENT_DOCUMENT_NAME,
    MEASUREMENT_FRAME_DIRECTORY,
    SCHEMA_VERSION,
    AnchorReceipt,
    BridgeAnchorError,
    BridgeChannelError,
    BridgeError,
    BridgeEvidenceError,
    BridgeScheduleError,
    BridgeSpecificationError,
    DeterministicAppendOnlyLog,
    MeasurementSpec,
    open_measured_analysis_access,
    _open_measured_analysis_access_with_injected_verifier,
    run_measurement_bridge,
    write_anchor_receipt,
)

LAW = LatticeBondSpec()
SHAPE = (8, 8)
IDENTITY = {"kind": "lattice-bond-engine", "name": "measurement-bridge-fixture"}
SPEC = MeasurementSpec(min_cells=1)
SCHEDULE = (0, 1, 2, 3)


# --------------------------------------------------------------------------------------
# handcrafted lattices
# --------------------------------------------------------------------------------------


def _state(matter: np.ndarray, *, step: int = 0, resource: float = 0.8) -> LatticeBondState:
    shape = (int(matter.shape[0]), int(matter.shape[1]))
    return LatticeBondState(
        np.array(matter, dtype=np.float64, copy=True),
        np.full(shape, resource, dtype=np.float64),
        np.zeros((2, *shape), dtype=np.float64),
        step,
    )


def _splitting_matter() -> np.ndarray:
    """Two 2x2 blobs bridged by two cells that sit a hair above the threshold."""

    matter = np.zeros(SHAPE, dtype=np.float64)
    for y, x in ((2, 2), (2, 3), (3, 2), (3, 3), (2, 6), (2, 7), (3, 6), (3, 7)):
        matter[y, x] = 1.0
    matter[2, 4] = 0.4502
    matter[2, 5] = 0.4502
    return matter


def _merging_matter() -> np.ndarray:
    """Two vertical bars separated by a column that sits a hair below the threshold."""

    matter = np.zeros(SHAPE, dtype=np.float64)
    for column in (2, 3, 5, 6):
        matter[:, column] = 1.0
    matter[:, 4] = 0.4495
    return matter


def _dissolving_matter() -> np.ndarray:
    """One three-cell blob just above the threshold, with nothing to associate with."""

    matter = np.zeros(SHAPE, dtype=np.float64)
    for y, x in ((6, 1), (6, 2), (7, 1)):
        matter[y, x] = 0.4503
    return matter


#: Schedule for the turnover fixture below.  Sixteen engine steps, five samples.
TURNOVER_SCHEDULE = (0, 4, 8, 12, 16)


def _turnover_matter() -> np.ndarray:
    """A 2x2 saturated blob standing in a sea of UNLABELLED sub-threshold matter.

    The sea sits at 0.449, one ten-thousandth below ``SPEC.matter_threshold``, so
    at the enrolment frame it belongs to no detected component and is therefore
    never labelled.  As the blob relaxes it lifts its neighbours across the
    threshold, and those neighbours join the component carrying matter that was
    not in the cohort: the component's ``cohort_residual`` then falls strictly
    below 1.0 while staying strictly above 0.0.  That is genuine partial
    material replacement, and it is unobservable when the cohort is enrolled as
    the whole matter field.
    """

    matter = np.full(SHAPE, 0.449, dtype=np.float64)
    for y, x in ((3, 3), (3, 4), (4, 3), (4, 4)):
        matter[y, x] = 1.0
    return matter


def _component_cells(directory: Path, position: int, label: int) -> list[tuple[int, ...]]:
    """Re-detect components from the PERSISTED matter of one sampled frame."""

    matter = _floats(directory, position, "matter", SHAPE)
    state = LatticeBondState(
        np.array(matter), np.full(SHAPE, 0.8), np.zeros((2, *SHAPE)), label
    )
    return [
        component.cells
        for component in detect_components(state, SPEC.detector_spec(), frame=label)
    ]


def _run(directory, *, matter=None, schedule=SCHEDULE, spec=SPEC, state=None, **kwargs):
    return run_measurement_bridge(
        directory,
        law_spec=kwargs.pop("law_spec", LAW),
        initial_state=state if state is not None else _state(
            _splitting_matter() if matter is None else matter
        ),
        sampled_frames=schedule,
        measurement_spec=spec,
        acquisition_source_identity=kwargs.pop("acquisition_source_identity", IDENTITY),
        **kwargs,
    )


# --------------------------------------------------------------------------------------
# canonical helpers, reimplemented here so a test never trusts the module under test
# --------------------------------------------------------------------------------------


def _canonical(value) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_json(directory: Path, name: str):
    return json.loads((directory / name).read_bytes())


def _write_json(directory: Path, name: str, value) -> None:
    (directory / name).write_bytes(_canonical(value))


def _channel(directory: Path, position: int, channel: str) -> Path:
    return directory / MEASUREMENT_FRAME_DIRECTORY / f"frame_{position:06d}_{channel}.bin"


def _floats(directory: Path, position: int, channel: str, shape) -> np.ndarray:
    return np.frombuffer(_channel(directory, position, channel).read_bytes(), dtype="<f8").reshape(
        shape
    )


def _repin(directory: Path) -> None:
    """Rewrite the root and the binding so a tamper survives every digest check."""

    document = _read_json(directory, MEASUREMENT_DOCUMENT_NAME)
    document["measurement_root_sha256"] = mb._root_from_document(document)
    payload = _canonical(document)
    (directory / MEASUREMENT_DOCUMENT_NAME).write_bytes(payload)
    binding = _read_json(directory, BRIDGE_BINDING_NAME)
    binding["measurement_document_sha256"] = _digest(payload)
    binding["measurement_root_sha256"] = document["measurement_root_sha256"]
    binding["owned_root_sha256"] = document["owned_root_sha256"]
    _write_json(directory, BRIDGE_BINDING_NAME, binding)


# --------------------------------------------------------------------------------------
# shared runs
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def anchored(tmp_path_factory):
    directory = tmp_path_factory.mktemp("anchored_bridge_run")
    record = _run(directory)
    log = DeterministicAppendOnlyLog()
    receipt = log.publish(
        record.measurement_root_sha256, published_at_label="2026-01-01T00:00:00Z"
    )
    write_anchor_receipt(directory, receipt)
    return SimpleNamespace(directory=directory, record=record, log=log, receipt=receipt)


@pytest.fixture
def run_dir(anchored, tmp_path) -> Path:
    target = tmp_path / "run"
    shutil.copytree(anchored.directory, target)
    return target


@pytest.fixture
def fresh(tmp_path) -> Path:
    directory = tmp_path / "fresh"
    directory.mkdir()
    return directory


# --------------------------------------------------------------------------------------
# 1. specification validation
# --------------------------------------------------------------------------------------


def test_spec_defaults_are_admissible():
    spec = MeasurementSpec()
    assert spec.matter_threshold == 0.45
    assert spec.detector_spec().min_cells == 3
    assert spec.tracker_spec().dilation_radius == 1
    assert set(spec.as_dict()) == {
        "cohort_residual_fraction",
        "dilation_radius",
        "matter_threshold",
        "max_area_ratio",
        "max_centroid_displacement",
        "min_cells",
        "unique_score_margin",
    }


def test_spec_materialization_interval_is_read_from_the_owned_pipeline():
    from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
        _FRAME_MATERIALIZATION,
    )

    assert mb.ABSENT_MATTER == _FRAME_MATERIALIZATION["absent_matter"]
    assert mb.PRESENT_MATTER == _FRAME_MATERIALIZATION["present_matter"]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"matter_threshold": float("nan")}, "must be finite"),
        ({"max_area_ratio": float("inf")}, "must be finite"),
        ({"min_cells": 0}, "min_cells"),
        ({"dilation_radius": -1}, "dilation_radius"),
        ({"max_area_ratio": 0.5}, "max_area_ratio"),
        ({"max_centroid_displacement": 0.0}, "max_centroid_displacement"),
        ({"unique_score_margin": 0.0}, "unique_score_margin"),
        ({"cohort_residual_fraction": 0.0}, "declared convention"),
        ({"cohort_residual_fraction": 1.0}, "declared convention"),
        ({"matter_threshold": 0.1}, "matter_threshold must satisfy"),
        ({"matter_threshold": 0.05}, "matter_threshold must satisfy"),
        ({"matter_threshold": 0.9}, "matter_threshold must satisfy"),
    ],
)
def test_spec_rejects_inadmissible_declarations(kwargs, message):
    with pytest.raises(BridgeSpecificationError, match=message):
        MeasurementSpec(**kwargs)


def test_spec_accepts_the_closed_upper_end_of_the_materialization_interval():
    assert MeasurementSpec(matter_threshold=mb.PRESENT_MATTER).matter_threshold == 0.8
    assert MeasurementSpec(matter_threshold=0.1000001).matter_threshold > mb.ABSENT_MATTER


# --------------------------------------------------------------------------------------
# 2. produced-never-accepted
# --------------------------------------------------------------------------------------


def test_no_public_parameter_accepts_a_produced_artifact():
    forbidden = {
        "frames",
        "frame",
        "masks",
        "mask",
        "tracking",
        "lifecycle",
        "manifest",
        "manifests",
        "digest",
        "digests",
        "root",
        "roots",
        "receipt",
        "receipts",
        "acquisition_source",
        "ledger",
        "access",
    }
    for function in (run_measurement_bridge, open_measured_analysis_access):
        assert forbidden.isdisjoint(inspect.signature(function).parameters)


def test_the_acquisition_source_is_a_private_closure_reading_the_persisted_mask(anchored):
    """The owned ledger's frame digests must be digests of the PERSISTED masks."""

    ledger = _read_json(anchored.directory, "ACQUISITION.json")
    for position, entry in enumerate(ledger["entries"]):
        persisted = _channel(anchored.directory, position, "mask").read_bytes()
        assert entry["frame_sha256"] == _digest(persisted)


# --------------------------------------------------------------------------------------
# 3. channel extraction
# --------------------------------------------------------------------------------------


def test_every_channel_is_extracted_bit_exactly_from_the_engine(anchored):
    engine = LatticeBondEngine(LAW)
    state = _state(_splitting_matter())
    tracer = state.m.copy()
    expected = {}
    for label in SCHEDULE:
        while state.step < label:
            pre = state
            result = engine.step(pre)
            tracer = advance_passive_tracer(
                tracer,
                pre.m,
                result.ledger.matter_forward * result.ledger.matter_scale,
                result.ledger.matter_reverse * result.ledger.matter_scale,
                result.state.m,
                LAW.dt,
            )
            state = result.state
        expected[label] = (state.m.copy(), state.n.copy(), state.b.copy(), tracer.copy())

    for position, label in enumerate(SCHEDULE):
        matter, resource, bond, cohort = expected[label]
        assert np.array_equal(_floats(anchored.directory, position, "matter", SHAPE), matter)
        assert np.array_equal(_floats(anchored.directory, position, "resource", SHAPE), resource)
        assert np.array_equal(
            _floats(anchored.directory, position, "bond", (2, *SHAPE)), bond
        )
        assert np.array_equal(_floats(anchored.directory, position, "tracer", SHAPE), cohort)


def test_channel_digests_and_totals_match_the_persisted_bytes(anchored):
    for position, frame in enumerate(anchored.record.frames):
        for channel, recorded in (
            ("matter", frame.matter_sha256),
            ("resource", frame.resource_sha256),
            ("bond", frame.bond_sha256),
            ("tracer", frame.tracer_sha256),
            ("mask", frame.mask_sha256),
        ):
            assert recorded == _digest(_channel(anchored.directory, position, channel).read_bytes())
        matter = _floats(anchored.directory, position, "matter", SHAPE)
        assert frame.total_matter == math.fsum(float(v) for v in matter.reshape(-1))


def test_frame_labels_are_read_from_the_engine_state(anchored):
    assert tuple(frame.frame for frame in anchored.record.frames) == SCHEDULE
    assert tuple(frame.ordinal for frame in anchored.record.frames) == (0, 1, 2, 3)
    assert anchored.record.step_count == SCHEDULE[-1]
    assert anchored.record.sampled_frames == SCHEDULE


# --------------------------------------------------------------------------------------
# 4. float -> mask cross binding
# --------------------------------------------------------------------------------------


def test_persisted_mask_is_the_threshold_of_the_persisted_float_matter(anchored):
    for position in range(len(SCHEDULE)):
        matter = _floats(anchored.directory, position, "matter", SHAPE)
        mask = np.frombuffer(
            _channel(anchored.directory, position, "mask").read_bytes(), dtype=np.uint8
        ).reshape(SHAPE)
        assert np.array_equal(mask.astype(bool), matter >= SPEC.matter_threshold)


def test_a_corrupted_persisted_mask_is_refused(run_dir):
    path = _channel(run_dir, 1, "mask")
    payload = bytearray(path.read_bytes())
    payload[0] = 1 - payload[0]
    path.write_bytes(bytes(payload))
    with pytest.raises(BridgeEvidenceError, match="not the threshold of the persisted float"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_non_canonical_mask_byte_is_refused(run_dir):
    path = _channel(run_dir, 0, "mask")
    payload = bytearray(path.read_bytes())
    payload[0] = 2
    path.write_bytes(bytes(payload))
    with pytest.raises(BridgeChannelError, match="canonical 0/1 mask"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_truncated_mask_is_refused(run_dir):
    path = _channel(run_dir, 0, "mask")
    path.write_bytes(path.read_bytes()[:-1])
    with pytest.raises(BridgeChannelError, match="mask channel has the wrong byte length"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


# --------------------------------------------------------------------------------------
# 5. per-channel tampering
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("channel", ["matter", "resource", "bond", "tracer"])
def test_a_tampered_float_channel_is_refused(run_dir, channel):
    """A sub-threshold edit keeps the mask valid, so the frame digest must catch it."""

    path = _channel(run_dir, 2, channel)
    payload = bytearray(path.read_bytes())
    payload[:8] = struct.pack("<d", 0.05)
    path.write_bytes(bytes(payload))
    with pytest.raises(BridgeEvidenceError) as excinfo:
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)
    assert "do not reproduce" in str(excinfo.value) or "threshold" in str(excinfo.value)


@pytest.mark.parametrize("channel", ["matter", "resource", "bond", "tracer"])
def test_a_non_finite_float_channel_is_refused(run_dir, channel):
    path = _channel(run_dir, 0, channel)
    payload = bytearray(path.read_bytes())
    payload[:8] = struct.pack("<d", float("nan"))
    path.write_bytes(bytes(payload))
    with pytest.raises(BridgeChannelError, match="is not finite"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_truncated_float_channel_is_refused(run_dir):
    path = _channel(run_dir, 0, "resource")
    path.write_bytes(path.read_bytes()[:-8])
    with pytest.raises(BridgeChannelError, match="resource channel has the wrong byte length"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_missing_channel_file_is_refused(run_dir):
    _channel(run_dir, 1, "bond").unlink()
    with pytest.raises(BridgeEvidenceError, match="missing or unexpected entries"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_an_extra_channel_file_is_refused(run_dir):
    (run_dir / MEASUREMENT_FRAME_DIRECTORY / "frame_000009_matter.bin").write_bytes(b"")
    with pytest.raises(BridgeEvidenceError, match="missing or unexpected entries"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_non_regular_frame_entry_is_refused(run_dir):
    (run_dir / MEASUREMENT_FRAME_DIRECTORY / "smuggled").mkdir()
    with pytest.raises(BridgeEvidenceError, match="non-regular entry"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_missing_frame_directory_is_refused(run_dir):
    shutil.rmtree(run_dir / MEASUREMENT_FRAME_DIRECTORY)
    with pytest.raises(BridgeEvidenceError, match="no measurement frame directory"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


# --------------------------------------------------------------------------------------
# 6. cohort identity, conservation and morphology
# --------------------------------------------------------------------------------------


def test_cohort_is_enrolled_component_locally_at_the_first_sampled_frame(anchored):
    """Every cell of the splitting fixture's matter is inside the one component."""

    first = anchored.record.frames[0]
    assert first.total_cohort == first.total_matter
    assert [component.cohort_residual for component in first.components] == [1.0]
    tracer = _floats(anchored.directory, 0, "tracer", SHAPE).reshape(-1)
    matter = _floats(anchored.directory, 0, "matter", SHAPE).reshape(-1)
    labelled = {cell for cells in _component_cells(anchored.directory, 0, 0) for cell in cells}
    for cell in range(tracer.size):
        assert tracer[cell] == (matter[cell] if cell in labelled else 0.0)


def test_cohort_enrolment_is_deferred_to_the_first_sampled_frame(fresh):
    """Steps before the first sample advect nothing: there is no cohort yet."""

    record = _run(fresh, schedule=(2, 3))
    engine = LatticeBondEngine(LAW)
    state = _state(_splitting_matter())
    while state.step < 2:
        state = engine.step(state).state
    assert record.step_count == 3
    expected = np.zeros(SHAPE, dtype=np.float64).reshape(-1)
    flat = np.ascontiguousarray(state.m).reshape(-1)
    for component in detect_components(state, SPEC.detector_spec(), frame=2):
        for cell in component.cells:
            expected[cell] = flat[cell]
    assert np.array_equal(_floats(fresh, 0, "tracer", SHAPE), expected.reshape(SHAPE))
    # Two engine steps have spread matter into cells no component owns, so the
    # enrolled cohort is now strictly smaller than the whole matter field.
    assert not np.array_equal(expected.reshape(SHAPE), state.m)
    assert record.frames[0].total_cohort < record.frames[0].total_matter


def test_a_component_reports_genuine_partial_material_replacement(fresh):
    """cohort_residual falls strictly below 1.0 and stays strictly above 0.0.

    The enrolled cohort is the 2x2 blob.  Four steps later the component has
    absorbed eight neighbouring cells lifted across the threshold by matter that
    was never labelled, so barely half of the component's CURRENT material was
    present at enrolment.  The residual then keeps decreasing, monotonically,
    at every later sampled frame.
    """

    record = _run(fresh, matter=_turnover_matter(), schedule=TURNOVER_SCHEDULE)
    assert [len(frame.components) for frame in record.frames] == [1, 1, 1, 1, 1]
    residuals = [frame.components[0].cohort_residual for frame in record.frames]
    areas = [frame.components[0].area for frame in record.frames]

    assert residuals[0] == 1.0
    assert areas == [4, 12, 12, 12, 12]
    for value in residuals[1:]:
        assert 0.0 < value < 1.0
    # Genuine replacement, not a rounding wobble: about 47% of the component's
    # material at frame 4 arrived after enrolment.
    assert residuals[1] < 0.53
    # Monotone decrease across every sampled frame, five frames in all.
    for earlier, later in zip(residuals, residuals[1:]):
        assert later < earlier
    # The residual is cohort_mass / mass of the CURRENT component, and the
    # cohort itself is conserved on the whole lattice.
    for frame in record.frames:
        component = frame.components[0]
        assert component.cohort_residual == component.cohort_mass / component.mass
        assert component.cohort_mass < component.mass or frame.frame == 0
        assert frame.total_cohort == pytest.approx(4.0, abs=1e-12)
        assert frame.total_matter == pytest.approx(30.94, abs=1e-12)


def test_matter_outside_every_detected_component_is_not_labelled_at_enrolment(fresh):
    """The enrolled tracer is exactly zero in every cell no component owns."""

    record = _run(fresh, matter=_turnover_matter(), schedule=TURNOVER_SCHEDULE)
    tracer = _floats(fresh, 0, "tracer", SHAPE).reshape(-1)
    matter = _floats(fresh, 0, "matter", SHAPE).reshape(-1)
    labelled = {cell for cells in _component_cells(fresh, 0, 0) for cell in cells}
    assert labelled == {27, 28, 35, 36}
    outside = [cell for cell in range(tracer.size) if cell not in labelled]
    # There is matter out there, and none of it carries a label.
    assert all(matter[cell] > 0.0 for cell in outside)
    assert all(tracer[cell] == 0.0 for cell in outside)
    assert all(tracer[cell] == matter[cell] for cell in labelled)
    assert record.frames[0].total_cohort == pytest.approx(4.0, abs=1e-12)
    assert record.frames[0].total_cohort < record.frames[0].total_matter


@pytest.mark.parametrize(
    "matter, schedule",
    [
        (None, SCHEDULE),
        (_turnover_matter(), TURNOVER_SCHEDULE),
        (_merging_matter(), SCHEDULE),
        (_dissolving_matter(), (0, 1, 2)),
    ],
)
def test_the_enrolment_frame_residual_is_exactly_one_for_every_component(
    fresh, matter, schedule
):
    """Not approximately one: the enrolled cohort IS the component's matter."""

    record = _run(fresh, matter=matter, schedule=schedule)
    first = record.frames[0]
    assert first.components
    for component in first.components:
        assert component.cohort_mass == component.mass
        assert component.cohort_residual == 1.0


def test_enrolling_the_cohort_at_the_initial_state_would_change_an_observable(fresh):
    """M17: enrolment time is observable, so moving it to the initial state is a kill.

    The schedule starts at frame 4, by which time the component has grown from
    four cells to twelve.  A cohort enrolled at the initial state labels only
    the original 2x2 blob (mass 4.0); a cohort enrolled at the first SAMPLED
    frame labels the whole twelve-cell component (mass ~7.594).  Both the
    published ``total_cohort`` and the enrolment-frame residual separate them.
    """

    record = _run(fresh, matter=_turnover_matter(), schedule=(4, 8, 12))
    first = record.frames[0]

    engine = LatticeBondEngine(LAW)
    state = _state(_turnover_matter())
    at_initial = math.fsum(
        float(state.m[divmod(cell, SHAPE[1])])
        for component in detect_components(state, SPEC.detector_spec(), frame=0)
        for cell in component.cells
    )
    while state.step < 4:
        state = engine.step(state).state
    at_first_sample = math.fsum(
        float(state.m[divmod(cell, SHAPE[1])])
        for component in detect_components(state, SPEC.detector_spec(), frame=4)
        for cell in component.cells
    )

    assert at_initial == pytest.approx(4.0, abs=1e-12)
    assert at_first_sample == pytest.approx(7.594333441345, abs=1e-9)
    assert first.total_cohort == pytest.approx(at_first_sample, abs=1e-12)
    assert abs(first.total_cohort - at_initial) > 3.0
    # The mutant also cannot reproduce an exactly-unit residual at enrolment.
    assert [component.cohort_residual for component in first.components] == [1.0]
    assert first.components[0].cohort_mass == first.components[0].mass


def test_cohort_mass_is_conserved_across_every_sampled_frame(anchored):
    totals = [frame.total_cohort for frame in anchored.record.frames]
    for value in totals[1:]:
        assert value == pytest.approx(totals[0], abs=1e-12)
    for frame in anchored.record.frames:
        assert frame.total_matter == pytest.approx(totals[0], abs=1e-12)


def test_cohort_residual_is_a_declared_convention_and_not_an_api_tolerance():
    parameters = inspect.signature(advance_passive_tracer).parameters
    assert "epsilon" not in parameters
    assert not any("epsilon" in name or "tolerance" in name for name in parameters)
    assert "cohort_residual_fraction" in MeasurementSpec().as_dict()
    source = Path(mb.__file__).read_text(encoding="utf-8")
    body = source.split('"""', 2)[2]
    assert "cohort_residual_fraction" in body
    # The declared convention is recorded, never compared against a residual.
    assert "cohort_residual_fraction" not in body.split("def _reread_frames", 1)[1]


def test_cohort_residual_is_the_labelled_mass_still_inside_each_component(anchored):
    for position, frame in enumerate(anchored.record.frames):
        tracer = _floats(anchored.directory, position, "tracer", SHAPE).reshape(-1)
        matter = _floats(anchored.directory, position, "matter", SHAPE)
        state = LatticeBondState(
            np.array(matter), np.full(SHAPE, 0.8), np.zeros((2, *SHAPE)), frame.frame
        )
        detected = detect_components(state, SPEC.detector_spec(), frame=frame.frame)
        assert len(detected) == len(frame.components)
        for component, measured in zip(detected, frame.components):
            expected = math.fsum(float(tracer[cell]) for cell in component.cells)
            assert measured.cohort_mass == expected
            assert measured.cohort_residual == expected / component.mass


def test_morphology_matches_detect_components_exactly(anchored):
    engine = LatticeBondEngine(LAW)
    state = _state(_splitting_matter())
    for position, label in enumerate(SCHEDULE):
        while state.step < label:
            state = engine.step(state).state
        detected = detect_components(state, SPEC.detector_spec(), frame=label)
        measured = anchored.record.frames[position].components
        assert len(detected) == len(measured)
        for expected, actual in zip(detected, measured):
            assert actual.index == expected.index
            assert actual.area == expected.area
            assert actual.mass == expected.mass
            assert actual.centroid_y == expected.centroid_y
            assert actual.centroid_x == expected.centroid_x
            assert actual.radius_gyration == expected.radius_gyration
            assert actual.wraps_y == expected.wraps_y
            assert actual.wraps_x == expected.wraps_x
            assert actual.pixel_support_sha256 == _digest(
                b"".join(struct.pack("<q", int(cell)) for cell in sorted(expected.cells))
            )


def test_morphology_is_bound_by_the_bridge_but_not_by_the_lifecycle(anchored):
    """MB-L5: the lifecycle document binds tracking, never pixels."""

    lifecycle = _read_json(anchored.directory, "LIFECYCLE.json")
    text = json.dumps(lifecycle)
    for absent in ("radius_gyration", "centroid", "pixel_support", "area", "mass"):
        assert absent not in text
    document = _read_json(anchored.directory, MEASUREMENT_DOCUMENT_NAME)
    assert "radius_gyration" in json.dumps(document)


# --------------------------------------------------------------------------------------
# 7. schedule
# --------------------------------------------------------------------------------------


def test_sampled_frames_is_mandatory_and_keyword_only(fresh):
    with pytest.raises(TypeError):
        run_measurement_bridge(
            fresh,
            law_spec=LAW,
            initial_state=_state(_splitting_matter()),
            acquisition_source_identity=IDENTITY,
        )


@pytest.mark.parametrize(
    "schedule, message",
    [
        (None, "mandatory"),
        ("012", "ordered sequence"),
        ({0, 1, 2}, "ordered sequence"),
        (3, "ordered sequence"),
        ((), "must not be empty"),
        ((True, 2), "plain integers"),
        ((np.int64(0), np.int64(1)), "plain integers"),
        ((0, 2, 1), "strictly increasing"),
        ((0, 0, 1), "strictly increasing"),
        ((2, 1, 0), "strictly increasing"),
        ((-1, 0), "must not precede"),
    ],
)
def test_malformed_schedules_are_refused(fresh, schedule, message):
    with pytest.raises(BridgeScheduleError, match=message):
        _run(fresh, schedule=schedule)
    assert not (fresh / MEASUREMENT_FRAME_DIRECTORY).exists()


def test_a_frame_before_the_initial_engine_step_is_refused(fresh):
    initial = _state(_splitting_matter(), step=5)
    with pytest.raises(BridgeScheduleError, match="must not precede the initial engine step 5"):
        _run(fresh, state=initial, schedule=(3, 6))


def test_a_schedule_starting_at_the_initial_engine_step_is_accepted(fresh):
    record = _run(fresh, state=_state(_splitting_matter(), step=4), schedule=(4, 5))
    assert record.sampled_frames == (4, 5)
    assert record.step_count == 1


def test_an_engine_that_overshoots_a_label_is_refused(fresh, monkeypatch):
    class _DoubleStepEngine:
        def __init__(self, spec):
            self._inner = LatticeBondEngine(spec)

        def step(self, state, intervention=None, *, backend="vectorized"):
            result = self._inner.step(state, intervention, backend=backend)
            return StepResult(
                LatticeBondState(
                    result.state.m,
                    result.state.n,
                    result.state.b,
                    int(result.state.step) + 1,
                ),
                result.ledger,
            )

    monkeypatch.setattr(mb, "LatticeBondEngine", _DoubleStepEngine)
    with pytest.raises(BridgeScheduleError, match="does not equal declared frame 1"):
        _run(fresh, schedule=(0, 1))


# --------------------------------------------------------------------------------------
# 8. run-level failures
# --------------------------------------------------------------------------------------


def test_a_missing_run_directory_is_refused(tmp_path):
    with pytest.raises(BridgeEvidenceError, match="must already exist"):
        _run(tmp_path / "absent")


def test_an_existing_measurement_frame_directory_is_refused(fresh):
    (fresh / MEASUREMENT_FRAME_DIRECTORY).mkdir()
    with pytest.raises(BridgeEvidenceError, match="could not create the measurement frame"):
        _run(fresh)


def test_an_existing_measurement_document_is_never_overwritten(fresh):
    (fresh / MEASUREMENT_DOCUMENT_NAME).write_bytes(b"squatter")
    with pytest.raises(BridgeEvidenceError, match="without overwriting"):
        _run(fresh)
    assert (fresh / MEASUREMENT_DOCUMENT_NAME).read_bytes() == b"squatter"


def test_an_owned_pipeline_refusal_is_typed(fresh):
    with pytest.raises(BridgeEvidenceError, match="owned pipeline refused"):
        _run(fresh, acquisition_source_identity={})


# --------------------------------------------------------------------------------------
# 9. zero acquisition vs zero detection
# --------------------------------------------------------------------------------------


def test_zero_acquisition_is_an_error(fresh):
    with pytest.raises(BridgeScheduleError, match="must not be empty"):
        _run(fresh, schedule=())


def test_zero_detection_still_produces_frames(fresh):
    record = _run(fresh, matter=np.full(SHAPE, 0.2), schedule=(0, 1, 2))
    assert len(record.frames) == 3
    assert all(frame.components == () for frame in record.frames)
    assert record.owned_record.detected_component_count == 0
    assert record.owned_record.track_count == 0
    # Distinguishable from zero acquisition: frames exist, components do not.
    assert record.owned_record.sample_count == 3


# --------------------------------------------------------------------------------------
# 10. lifecycle terminal states reached through split, merge and disappearance
# --------------------------------------------------------------------------------------


def _terminal_states(directory: Path) -> set[str]:
    lifecycle = _read_json(directory, "LIFECYCLE.json")
    return {record["terminal_state"] for record in lifecycle["terminal_records"]}


def test_split_reaches_the_split_terminal_state(anchored):
    assert _terminal_states(anchored.directory) == {
        "SPLIT_INTO_TRACKS",
        "RIGHT_CENSORED_AT_HORIZON",
    }
    assert [len(frame.components) for frame in anchored.record.frames] == [1, 2, 2, 2]


def test_merge_reaches_the_merged_terminal_state(fresh):
    record = _run(fresh, matter=_merging_matter())
    assert "MERGED_INTO_TRACK" in _terminal_states(fresh)
    assert [len(frame.components) for frame in record.frames] == [2, 1, 1, 1]


def test_disappearance_reaches_the_dissolved_terminal_state(fresh):
    record = _run(fresh, matter=_dissolving_matter(), schedule=(0, 1, 2))
    assert _terminal_states(fresh) == {"DISSOLVED_DETECTED_TRACK"}
    assert [len(frame.components) for frame in record.frames] == [1, 0, 0]


def test_a_six_by_six_lattice_with_an_intervention_and_the_reference_backend(fresh):
    matter = np.zeros((6, 6), dtype=np.float64)
    for y, x in ((1, 1), (1, 2), (2, 1), (2, 2)):
        matter[y, x] = 1.0
    intervention = FaceIntervention.from_cuts((6, 6), matter_faces=[(0, 2, 1), (1, 1, 2)])
    record = _run(
        fresh,
        state=_state(matter),
        schedule=(0, 2),
        intervention=intervention,
        backend="reference",
    )
    assert record.frame_shape == (6, 6)
    assert record.intervention_sha256 == _digest(intervention.canonical_bytes())
    assert record.frames[0].total_cohort == pytest.approx(4.0, abs=1e-12)
    assert record.frames[1].total_cohort == pytest.approx(4.0, abs=1e-12)


# --------------------------------------------------------------------------------------
# 11. nesting and source bindings
# --------------------------------------------------------------------------------------


def test_owned_root_digests_the_owned_record_digest_fields(anchored):
    owned = anchored.record.owned_record
    payload = {
        name: (list(value) if isinstance(value, tuple) else value)
        for name, value in (
            (field, getattr(owned, field)) for field in mb._OWNED_ROOT_FIELDS
        )
    }
    assert anchored.record.owned_root_sha256 == _digest(_canonical(payload))
    assert "run_directory" not in payload
    assert "state" not in payload


def test_measurement_root_binds_every_declared_field(anchored):
    document = _read_json(anchored.directory, MEASUREMENT_DOCUMENT_NAME)
    expected = _digest(
        _canonical(
            {
                "bridge_version": BRIDGE_VERSION,
                "frame_digests": [
                    frame.frame_digest_sha256 for frame in anchored.record.frames
                ],
                "initial_state_sha256": document["initial_state_sha256"],
                "intervention_sha256": None,
                "law_spec_sha256": document["law_spec_sha256"],
                "measurement_spec_sha256": anchored.record.measurement_spec_sha256,
                "owned_root_sha256": anchored.record.owned_root_sha256,
                "sampled_frames": list(SCHEDULE),
                "schema_version": SCHEMA_VERSION,
                "source_bindings": dict(anchored.record.source_bindings),
                "unavailable_channels": dict(anchored.record.unavailable_channels),
            }
        )
    )
    assert anchored.record.measurement_root_sha256 == expected
    assert document["measurement_root_sha256"] == expected


def test_frame_digests_bind_every_channel_and_every_component(anchored):
    document = _read_json(anchored.directory, MEASUREMENT_DOCUMENT_NAME)
    for persisted, frame in zip(document["frames"], anchored.record.frames):
        core = {key: value for key, value in persisted.items() if key != "frame_digest_sha256"}
        assert frame.frame_digest_sha256 == _digest(_canonical(core))
        assert set(core) == {
            "bond_sha256",
            "components",
            "frame",
            "mask_sha256",
            "matter_sha256",
            "ordinal",
            "resource_sha256",
            "total_cohort",
            "total_matter",
            "tracer_sha256",
        }


def test_the_bridge_pins_its_own_module_bytes(anchored):
    recorded = anchored.record.source_bindings["future_prospective_measurement_bridge_sha256"]
    assert recorded == _digest(Path(mb.__file__).read_bytes())
    assert set(anchored.record.source_bindings) == {
        "engine_sha256",
        "future_lifecycle_owned_pipeline_sha256",
        "future_lifecycle_runner_sha256",
        "future_prospective_measurement_bridge_sha256",
        "instrumentation_sha256",
        "lifecycle_sha256",
    }


def test_the_unavailable_channel_register_is_recorded(anchored):
    channels = anchored.record.unavailable_channels
    assert channels["signed_internal_state_variable"] == (
        "engine state fields m>=0, n>=0, b in [0,1]; none takes both signs"
    )
    assert channels["symmetry_partnered_convention_observable"] == (
        "matter flux is M*(chi - chi_plus) with M>=0; sign is fixed by a scalar "
        "potential difference"
    )
    assert channels["transverse_orbital_chirality_term"] == (
        "absent from the lattice-bond update; OrbitalSpec belongs to the CORE V0 "
        "particle substrate"
    )


def test_the_documents_are_canonical_and_atomically_published(anchored):
    for name in (MEASUREMENT_DOCUMENT_NAME, BRIDGE_BINDING_NAME, ANCHOR_RECEIPT_NAME):
        raw = (anchored.directory / name).read_bytes()
        assert raw == _canonical(json.loads(raw))
    assert not list(anchored.directory.glob(".*partial"))


# --------------------------------------------------------------------------------------
# 12. document and binding tampering
# --------------------------------------------------------------------------------------


def _tamper_document(directory: Path, **updates) -> None:
    document = _read_json(directory, MEASUREMENT_DOCUMENT_NAME)
    document.update(updates)
    (directory / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))


def _tamper_binding(directory: Path, **updates) -> None:
    binding = _read_json(directory, BRIDGE_BINDING_NAME)
    binding.update(updates)
    (directory / BRIDGE_BINDING_NAME).write_bytes(_canonical(binding))


def test_a_missing_measurement_document_is_refused(run_dir):
    (run_dir / MEASUREMENT_DOCUMENT_NAME).unlink()
    with pytest.raises(BridgeEvidenceError, match="no measurement document"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_an_invalid_json_measurement_document_is_refused(run_dir):
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(b"{not json")
    with pytest.raises(BridgeEvidenceError, match="not valid JSON"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_non_object_measurement_document_is_refused(run_dir):
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(b"[]")
    with pytest.raises(BridgeEvidenceError, match="must be a JSON object"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_measurement_document_key_set_mismatch_is_refused(run_dir):
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    document.pop("step_count")
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))
    with pytest.raises(BridgeEvidenceError, match="key set mismatch"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_non_canonical_measurement_document_bytes_are_refused(run_dir):
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(
        json.dumps(document, sort_keys=True, indent=1).encode("utf-8")
    )
    with pytest.raises(BridgeEvidenceError, match="not canonical"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_non_canonically_representable_binding_is_refused(run_dir):
    binding = _read_json(run_dir, BRIDGE_BINDING_NAME)
    binding["owned_root_sha256"] = float("nan")
    (run_dir / BRIDGE_BINDING_NAME).write_bytes(
        json.dumps(binding, allow_nan=True, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    with pytest.raises(BridgeEvidenceError, match="not canonically representable"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


@pytest.mark.parametrize(
    "updates, message",
    [
        ({"schema_version": "other/v9"}, "static declarations"),
        ({"bridge_version": "9.9.9"}, "static declarations"),
        ({"canonicalization": {}}, "static declarations"),
        ({"channel_encoding": {}}, "static declarations"),
        ({"frame_directory_relative_path": "elsewhere"}, "static declarations"),
        ({"provenance_disclosure": "trust me"}, "static declarations"),
        ({"unavailable_channels": {}}, "unavailable-channel register"),
        ({"sampled_frames": []}, "schedule is malformed"),
        ({"sampled_frames": ["a", 1, 2, 3]}, "schedule is malformed"),
        ({"sampled_frames": [0, 2, 1, 3]}, "strictly increasing"),
        ({"frame_shape": [1, 8]}, "frame shape is malformed"),
        ({"frame_shape": [8]}, "frame shape is malformed"),
        ({"frame_shape": [8, "8"]}, "frame shape is malformed"),
        ({"frame_shape": "8x8"}, "frame shape is malformed"),
        ({"step_count": -1}, "step count is malformed"),
        ({"step_count": True}, "step count is malformed"),
        ({"measurement_spec": []}, "specification is malformed"),
        ({"measurement_spec": {"min_cells": 1}}, "specification is malformed"),
        ({"measurement_spec": {**SPEC.as_dict(), "min_cells": 1.5}}, "specification is malformed"),
        (
            {"measurement_spec": {**SPEC.as_dict(), "dilation_radius": 1.5}},
            "specification is malformed",
        ),
        (
            {"measurement_spec": {**SPEC.as_dict(), "matter_threshold": True}},
            "specification is malformed",
        ),
        (
            {"measurement_spec": {**SPEC.as_dict(), "max_area_ratio": "3"}},
            "specification is malformed",
        ),
        ({"measurement_spec_sha256": "0" * 64}, "specification digest mismatch"),
        ({"measurement_root_sha256": "0" * 64}, "recomputed measurement root"),
        ({"owned_root_sha256": "0" * 64}, "recomputed measurement root"),
        ({"law_spec_sha256": "0" * 64}, "recomputed measurement root"),
        ({"initial_state_sha256": "0" * 64}, "recomputed measurement root"),
        ({"intervention_sha256": "0" * 64}, "recomputed measurement root"),
    ],
)
def test_a_tampered_measurement_document_is_refused(run_dir, updates, message):
    _tamper_document(run_dir, **updates)
    with pytest.raises(BridgeEvidenceError, match=message):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_substituted_source_binding_is_refused(run_dir):
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    document["source_bindings"]["instrumentation_sha256"] = "0" * 64
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))
    with pytest.raises(BridgeEvidenceError, match="source bindings do not match"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_an_inadmissible_persisted_specification_is_refused(run_dir):
    _tamper_document(
        run_dir, measurement_spec={**SPEC.as_dict(), "matter_threshold": 0.05}
    )
    with pytest.raises(BridgeSpecificationError, match="matter_threshold must satisfy"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_reordered_frame_list_is_refused(run_dir):
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    document["frames"] = list(reversed(document["frames"]))
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))
    with pytest.raises(BridgeEvidenceError, match="do not reproduce"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_dropped_frame_row_is_refused(run_dir):
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    document["frames"] = document["frames"][:-1]
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))
    with pytest.raises(BridgeEvidenceError, match="do not reproduce"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


@pytest.mark.parametrize(
    "updates, message",
    [
        ({"schema_version": "other/v9"}, "binding static declarations"),
        ({"bridge_version": "9.9.9"}, "binding static declarations"),
        ({"canonicalization": {}}, "binding static declarations"),
        ({"measurement_document_relative_path": "elsewhere"}, "binding static declarations"),
        ({"owned_binding_relative_path": "elsewhere"}, "binding static declarations"),
        ({"measurement_document_sha256": "0" * 64}, "does not match the measurement document"),
        ({"measurement_root_sha256": "0" * 64}, "does not match the measurement document"),
        ({"owned_root_sha256": "0" * 64}, "does not match the measurement document"),
        ({"owned_binding_sha256": "0" * 64}, "does not match the owned pipeline binding"),
    ],
)
def test_a_tampered_bridge_binding_is_refused(run_dir, updates, message):
    _tamper_binding(run_dir, **updates)
    with pytest.raises(BridgeEvidenceError, match=message):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_missing_bridge_binding_is_refused(run_dir):
    (run_dir / BRIDGE_BINDING_NAME).unlink()
    with pytest.raises(BridgeEvidenceError, match="no bridge binding"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_a_missing_owned_pipeline_binding_is_refused(run_dir):
    (run_dir / OWNED_BINDING_NAME).unlink()
    with pytest.raises(BridgeEvidenceError, match="no owned pipeline binding"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


# --------------------------------------------------------------------------------------
# 13. the deterministic append-only fake anchor
# --------------------------------------------------------------------------------------


def test_the_fake_log_is_an_append_only_hash_chain():
    log = DeterministicAppendOnlyLog(venue="unit-test-log")
    assert log.venue == "unit-test-log"
    head = hashlib.sha256(b"genesis").digest()
    first_digest = "11" * 32
    second_digest = "22" * 32
    first = log.publish(first_digest)
    head = hashlib.sha256(head + bytes.fromhex(first_digest)).digest()
    assert first.reference == head.hex()
    second = log.publish(second_digest, published_at_label="whenever")
    head = hashlib.sha256(head + bytes.fromhex(second_digest)).digest()
    assert second.reference == head.hex()
    assert second.published_at_label == "whenever"
    assert log.verify(first) and log.verify(second)


def test_the_fake_log_refuses_an_unpublished_or_forged_receipt():
    log = DeterministicAppendOnlyLog()
    receipt = log.publish("33" * 32)
    assert not log.verify(
        AnchorReceipt(root_sha256="44" * 32, venue=log.venue, reference=receipt.reference,
                      published_at_label="x")
    )
    assert not log.verify(
        AnchorReceipt(root_sha256="33" * 32, venue=log.venue, reference="ff" * 32,
                      published_at_label="x")
    )
    assert not DeterministicAppendOnlyLog().verify(receipt)


def test_the_receipt_label_is_opaque_and_unauthenticated(anchored):
    receipt = anchored.receipt
    assert receipt.published_at_label == "2026-01-01T00:00:00Z"
    payload = receipt.as_dict()
    assert payload["schema_version"] == SCHEMA_VERSION
    assert set(payload) == {
        "published_at_label",
        "reference",
        "root_sha256",
        "schema_version",
        "venue",
    }
    forged = AnchorReceipt(
        root_sha256=receipt.root_sha256,
        venue=receipt.venue,
        reference=receipt.reference,
        published_at_label="1970-01-01T00:00:00Z",
    )
    # The label is not part of the chain, so the log cannot tell the two apart.
    assert anchored.log.verify(forged)


# --------------------------------------------------------------------------------------
# 14. the anchor gate
# --------------------------------------------------------------------------------------


class _Spy:
    def __init__(self):
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError("owned analysis access must not be reached")


def test_a_valid_anchor_unlocks_owned_analysis(anchored, run_dir):
    access = _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    evidence = access.owned_access.verified_completion_evidence()
    assert evidence["disposition"] == "COMPLETE"
    assert access.anchor_receipt.root_sha256 == anchored.record.measurement_root_sha256
    assert access.verified_record.measurement_root_sha256 == (
        anchored.record.measurement_root_sha256
    )
    assert access.verified_record.frames == anchored.record.frames
    assert access.verified_record.measurement_spec == SPEC
    assert access.verified_record.sampled_frames == SCHEDULE
    assert access.verified_record.owned_root_sha256 == anchored.record.owned_root_sha256


def test_analysis_before_the_anchor_is_refused(fresh, monkeypatch):
    record = _run(fresh, schedule=(0, 1))
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="no anchor receipt"):
        _open_measured_analysis_access_with_injected_verifier(fresh, verifier=lambda receipt: True)
    assert spy.calls == 0
    assert record.measurement_root_sha256


def test_a_receipt_binding_a_different_root_is_refused(run_dir, monkeypatch):
    log = DeterministicAppendOnlyLog()
    (run_dir / ANCHOR_RECEIPT_NAME).unlink()
    write_anchor_receipt(run_dir, log.publish("ab" * 32))
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="does not bind the recomputed measurement root"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=log.verify)
    assert spy.calls == 0


def test_a_forged_reference_is_refused(anchored, run_dir, monkeypatch):
    receipt = anchored.receipt
    (run_dir / ANCHOR_RECEIPT_NAME).unlink()
    write_anchor_receipt(
        run_dir,
        AnchorReceipt(
            root_sha256=receipt.root_sha256,
            venue=receipt.venue,
            reference="ff" * 32,
            published_at_label=receipt.published_at_label,
        ),
    )
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="verifier refused"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0


def test_a_verifier_returning_false_is_refused(run_dir, monkeypatch):
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="verifier refused"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: False)
    assert spy.calls == 0


def test_a_malformed_anchor_receipt_is_refused(run_dir):
    (run_dir / ANCHOR_RECEIPT_NAME).write_bytes(b"[]")
    with pytest.raises(BridgeAnchorError, match="must be a JSON object"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_an_anchor_receipt_with_the_wrong_schema_is_refused(run_dir):
    receipt = _read_json(run_dir, ANCHOR_RECEIPT_NAME)
    receipt["schema_version"] = "other/v9"
    (run_dir / ANCHOR_RECEIPT_NAME).write_bytes(_canonical(receipt))
    with pytest.raises(BridgeAnchorError, match="unsupported anchor receipt schema version"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=lambda receipt: True)


def test_an_anchor_receipt_is_never_overwritten(run_dir, anchored):
    with pytest.raises(BridgeEvidenceError, match="without overwriting"):
        write_anchor_receipt(run_dir, anchored.receipt)


def test_write_anchor_receipt_verifies_nothing(fresh):
    """The publication step is deliberately blind; the gate is the reader."""

    record = _run(fresh, schedule=(0, 1))
    write_anchor_receipt(
        fresh,
        AnchorReceipt(
            root_sha256="00" * 32,
            venue="nowhere",
            reference="deadbeef",
            published_at_label="never",
        ),
    )
    assert (fresh / ANCHOR_RECEIPT_NAME).is_file()
    with pytest.raises(BridgeAnchorError, match="does not bind"):
        _open_measured_analysis_access_with_injected_verifier(fresh, verifier=lambda receipt: True)
    assert record.measurement_root_sha256 != "00" * 32


# --------------------------------------------------------------------------------------
# 15. post-anchor mutation
# --------------------------------------------------------------------------------------


def test_a_post_anchor_byte_mutation_is_refused(anchored, run_dir, monkeypatch):
    path = _channel(run_dir, 3, "tracer")
    payload = bytearray(path.read_bytes())
    payload[:8] = struct.pack("<d", 0.0)
    path.write_bytes(bytes(payload))
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeEvidenceError, match="do not reproduce"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0


def test_a_fully_repinned_post_anchor_mutation_still_fails_the_anchor(
    anchored, run_dir, monkeypatch
):
    """Every local digest is re-minted; only the anchored root cannot be re-minted."""

    _tamper_document(run_dir, intervention_sha256="0" * 64)
    _repin(run_dir)
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="does not bind the recomputed measurement root"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0


def test_owned_evidence_removed_after_the_anchor_is_refused(anchored, run_dir):
    (run_dir / ACQUISITION_FRAME_DIRECTORY / "frame_000000.bin").unlink()
    with pytest.raises(BridgeEvidenceError, match="owned analysis access refused"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)


# --------------------------------------------------------------------------------------
# 16. determinism and error hierarchy
# --------------------------------------------------------------------------------------


def test_two_independent_runs_produce_the_same_measurement_root(tmp_path):
    roots = []
    for name in ("first", "second"):
        directory = tmp_path / name
        directory.mkdir()
        roots.append(_run(directory, schedule=(0, 1, 2)).measurement_root_sha256)
    assert roots[0] == roots[1]


def test_every_bridge_error_is_a_bridge_error():
    for error in (
        BridgeSpecificationError,
        BridgeScheduleError,
        BridgeChannelError,
        BridgeEvidenceError,
        BridgeAnchorError,
    ):
        assert issubclass(error, BridgeError)
    assert issubclass(BridgeError, RuntimeError)


def test_the_module_docstring_carries_the_limitation_register():
    docstring = mb.__doc__
    for marker in (f"MB-L{index}" for index in range(1, 11)):
        assert marker in docstring
    assert "no ``epsilon`` parameter" in docstring
    assert "DECLARED\n  CONVENTION" in docstring or "DECLARED CONVENTION" in docstring


def test_the_module_docstring_records_why_enrolment_is_component_local():
    """The degenerate whole-field cohort must be visible as a CONSIDERED choice."""

    docstring = mb.__doc__
    assert "ENTITY-LOCALLY" in docstring
    assert "ENTIRE matter field is degenerate" in docstring
    assert "identically ``1.0``" in docstring
    assert "can never\nmeasure material replacement" in docstring
    assert "not\nlabelled" in docstring or "NOT\nlabelled" in docstring
    assert mb._enrolled_cohort.__doc__ is not None
    assert "degenerate" in mb._enrolled_cohort.__doc__


def test_a_tracer_contract_violation_is_typed_as_a_bridge_error(fresh, monkeypatch):
    """A bare ValueError from the tracer must not escape the Bridge hierarchy."""

    def _refusing(*args, **kwargs):
        raise ValueError("tracer must lie in [0,pre_matter]")

    monkeypatch.setattr(mb, "advance_passive_tracer", _refusing)
    with pytest.raises(BridgeChannelError) as excinfo:
        _run(fresh, schedule=(0, 1))
    assert "passive cohort refused" in str(excinfo.value)
    assert "tracer must lie in [0,pre_matter]" in str(excinfo.value)
    assert isinstance(excinfo.value, BridgeError)
    assert type(excinfo.value.__cause__) is ValueError
    assert str(excinfo.value.__cause__) == "tracer must lie in [0,pre_matter]"


def test_the_real_tracer_refusal_path_is_typed(fresh, monkeypatch):
    """The same seam reached through the real tracer, by corrupting the flows."""

    real = mb.advance_passive_tracer

    def _corrupting(tracer, pre_matter, forward, reverse, post_matter, dt):
        return real(tracer, pre_matter, forward, reverse, post_matter + 1.0, dt)

    monkeypatch.setattr(mb, "advance_passive_tracer", _corrupting)
    with pytest.raises(BridgeChannelError, match="passive cohort refused"):
        _run(fresh, schedule=(0, 1))


def test_an_owned_evidence_error_is_typed_as_a_bridge_evidence_error(
    anchored, run_dir, monkeypatch
):
    """OwnedEvidenceError must never leave open_measured_analysis_access untyped."""

    from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
        OwnedEvidenceError,
    )

    original = OwnedEvidenceError("persisted owned evidence is inconsistent")

    def _refusing(directory):
        raise original

    monkeypatch.setattr(mb, "open_owned_analysis_access", _refusing)
    with pytest.raises(BridgeEvidenceError) as excinfo:
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert "owned analysis access refused" in str(excinfo.value)
    assert isinstance(excinfo.value, BridgeError)
    assert excinfo.value.__cause__ is original
    assert not isinstance(excinfo.value, OwnedEvidenceError)


def test_a_real_owned_evidence_error_is_typed_and_keeps_its_cause(anchored, run_dir):
    """The same guarantee on the unpatched path, with the real owned evidence."""

    from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
        OwnedEvidenceError,
    )

    (run_dir / ACQUISITION_FRAME_DIRECTORY / "frame_000001.bin").unlink()
    with pytest.raises(BridgeEvidenceError) as excinfo:
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert isinstance(excinfo.value.__cause__, OwnedEvidenceError)


# --------------------------------------------------------------------------------------
# 17. seams reached only by a targeted probe
#
# Every test below fails for a behavioural reason -- a mask bit, an array handed to the
# owned pipeline, an unrefused inconsistency, or analysis capability granted where it
# must be refused -- and not merely because a recomputed digest differs.
# --------------------------------------------------------------------------------------


def test_a_cell_exactly_at_the_matter_threshold_is_inside_the_persisted_mask(fresh):
    """The persisted mask is ``matter >= threshold``: the lower end is CLOSED."""

    matter = np.zeros(SHAPE, dtype=np.float64)
    for y, x in ((2, 2), (2, 3), (3, 2), (3, 3)):
        matter[y, x] = 1.0
    matter[4, 2] = SPEC.matter_threshold
    record = _run(fresh, matter=matter, schedule=(0, 1))
    mask = np.frombuffer(
        _channel(fresh, 0, "mask").read_bytes(), dtype=np.uint8
    ).reshape(SHAPE)
    assert mask[4, 2] == 1
    assert mask.sum() == 5
    assert record.frames[0].components[0].area == 5


def test_the_acquisition_source_rereads_the_mask_after_the_bytes_change_on_disk(
    fresh, monkeypatch
):
    """MB-L9: the pipeline is handed the bytes on disk, never a remembered array."""

    captured = {}
    real = mb.run_owned_future_pipeline

    def _capturing(directory, *, acquisition_source, **kwargs):
        captured["source"] = acquisition_source
        return real(directory, acquisition_source=acquisition_source, **kwargs)

    monkeypatch.setattr(mb, "run_owned_future_pipeline", _capturing)
    _run(fresh, schedule=(0, 1))
    source = captured["source"]
    before = np.array(source(1, 1), copy=True)

    path = _channel(fresh, 1, "mask")
    payload = bytearray(path.read_bytes())
    payload[0] = 1 - payload[0]
    path.write_bytes(bytes(payload))

    after = source(1, 1)
    assert not np.array_equal(after, before)
    assert np.array_equal(
        after, np.frombuffer(bytes(payload), dtype=np.uint8).reshape(SHAPE).astype(bool)
    )


def test_the_reread_itself_refuses_a_mask_that_is_not_the_persisted_threshold(run_dir):
    """The cross-binding is enforced inside the re-read, before any digest is compared."""

    path = _channel(run_dir, 1, "mask")
    payload = bytearray(path.read_bytes())
    payload[0] = 1 - payload[0]
    path.write_bytes(bytes(payload))
    with pytest.raises(BridgeEvidenceError, match="not the threshold of the persisted float"):
        mb._reread_frames(run_dir, SPEC, SCHEDULE, SHAPE)


def _patched_morphology(monkeypatch) -> None:
    """Re-detect with one morphology value changed and every channel byte untouched."""

    real = mb.detect_components

    def _inflated(state, spec, *, frame):
        return tuple(
            dataclasses.replace(item, radius_gyration=item.radius_gyration + 1.0)
            for item in real(state, spec, frame=frame)
        )

    monkeypatch.setattr(mb, "detect_components", _inflated)


def test_a_repinned_morphology_only_change_is_still_refused_by_the_anchor(
    anchored, run_dir, monkeypatch
):
    """MB-L5: morphology is inside the root, so it cannot be repinned away locally."""

    _patched_morphology(monkeypatch)
    document = _read_json(run_dir, MEASUREMENT_DOCUMENT_NAME)
    document["frames"] = [
        frame.as_dict() for frame in mb._reread_frames(run_dir, SPEC, SCHEDULE, SHAPE)
    ]
    (run_dir / MEASUREMENT_DOCUMENT_NAME).write_bytes(_canonical(document))
    _repin(run_dir)
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="does not bind the recomputed measurement root"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0


def test_a_repinned_owned_root_substitution_is_refused_by_the_anchor(
    anchored, run_dir, monkeypatch
):
    """Nothing else re-derives the owned root, so only the measurement root binds it."""

    _tamper_document(run_dir, owned_root_sha256="0" * 64)
    _repin(run_dir)
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="does not bind the recomputed measurement root"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0


def test_a_repinned_source_binding_substitution_is_refused_by_the_anchor(
    anchored, run_dir, monkeypatch
):
    """MB-L3: edited sources reproduce a different root, which the anchor cannot match."""

    substituted = {**dict(anchored.record.source_bindings), "instrumentation_sha256": "0" * 64}
    monkeypatch.setattr(mb, "_source_bindings", lambda: dict(substituted))
    _tamper_document(run_dir, source_bindings=substituted)
    _repin(run_dir)
    spy = _Spy()
    monkeypatch.setattr(mb, "open_owned_analysis_access", spy)
    with pytest.raises(BridgeAnchorError, match="does not bind the recomputed measurement root"):
        _open_measured_analysis_access_with_injected_verifier(run_dir, verifier=anchored.log.verify)
    assert spy.calls == 0
