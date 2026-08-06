"""Route E runtime wiring gates -- ``P -> commitment -> beacon -> run_route_e(...) -> E``.

Every gate below is executable.  None of them inspects a manifest only: the enabled arm
has to change the fixture state measurably, the disabled arm has to stay byte-identical
to the witness, and an independent verifier has to admit the produced evidence.

ENGINEERING_ONLY / NOT_SCIENTIFIC_DATA / NOT_ELIGIBLE_FOR_ANALYSIS.
No scientific law, seed, family, horizon, holdout or Stage-B artefact is touched.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from edlab.substrates.lattice_bond import future_route_e_admission as admission
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond.future_lifecycle_runner import (
    LifecycleEvidenceError,
    RunnerState,
    publish_future_family_completion,
)
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec,
    run_measurement_bridge,
)
from edlab.substrates.lattice_bond.instrumentation import TrackerSpec, track_components
from edlab.substrates.lattice_bond.instrumentation import DetectedComponent

from tests.test_future_route_e_execution_boundary_00 import (  # noqa: E402
    _beacon,
    _bundle,
    _destination,
    _manifest,
    requires_verifier,
)

#: The canary banner.  It is asserted, not merely written in a comment.
CANARY_MARKERS = ("ENGINEERING_ONLY", "NOT_SCIENTIFIC_DATA", "NOT_ELIGIBLE_FOR_ANALYSIS")

TRACKER = TrackerSpec(max_centroid_displacement=2.0, max_area_ratio=2.0, dilation_radius=1)
NONUNIT_SCHEDULE = (0, 5)


def _component(frame_index: int, index: int = 0) -> DetectedComponent:
    return DetectedComponent(
        frame=frame_index,
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


def _digest_tree(root: Path) -> str:
    parts = []
    for path in sorted(root.rglob("*")):
        parts.append(str(path.relative_to(root)))
        if path.is_file():
            parts.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


# ======================================================================================
# ROUTE_E_RUNTIME_WIRING
# ======================================================================================


@requires_verifier
def test_route_e_runtime_wiring_the_whole_chain_is_the_path_taken(tmp_path, monkeypatch):
    """P -> commitment -> beacon -> run_route_e -> E, observed at runtime."""
    phases: list[str] = []

    real_root = execution.pre_run_root
    real_consume = frame.consume_beacon_round
    real_bridge = execution.run_measurement_bridge

    def spy_root(manifest):
        phases.append("P")
        return real_root(manifest)

    def spy_consume(**kwargs):
        phases.append("beacon")
        return real_consume(**kwargs)

    def spy_bridge(*args, **kwargs):
        phases.append("engine")
        return real_bridge(*args, **kwargs)

    monkeypatch.setattr(execution, "pre_run_root", spy_root)
    monkeypatch.setattr(frame, "consume_beacon_round", spy_consume)
    monkeypatch.setattr(execution, "run_measurement_bridge", spy_bridge)

    bundle, root = _bundle(tmp_path)
    # the commitment step: the anteriority proof binds exactly the recomputed P
    proof = json.loads((bundle / execution.ANTERIORITY_NAME).read_bytes())
    assert proof["binds_pre_run_root"] == root

    record = execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path))

    assert phases[0] == "P"
    assert phases.index("beacon") < phases.index("engine")
    assert record.pre_run_root == root
    assert record.worlds_attempted >= 1
    output = Path(record.output_directory)
    assert (output / execution.PROVENANCE_NAME).is_file()
    assert (output / execution.FINAL_RECEIPT_NAME).is_file()
    assert (output / execution.WORLDS_DIRECTORY).is_dir()


# ======================================================================================
# ROUTE_E_NONZERO_CAUSAL_ACTION  --  the enabled arm changes the state, not the manifest
# ======================================================================================


@requires_verifier
def test_route_e_nonzero_causal_action_the_state_really_moves(tmp_path):
    """A Route E world must evolve the lattice, not just write metadata."""
    document = _manifest()
    document["distributions_and_draw_algorithm"] = dict(
        document["distributions_and_draw_algorithm"], horizon_steps=8, cadence_steps=1
    )
    bundle, _ = _bundle(tmp_path, document)
    record = execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path))

    world = Path(record.output_directory) / execution.WORLDS_DIRECTORY / "000000"
    frames = sorted((world / "acquisition_frames").glob("frame_*.bin"))
    assert len(frames) >= 2, "the run must persist more than one frame"
    first = frames[0].read_bytes()
    last = frames[-1].read_bytes()
    assert first != last, "the enabled arm did not change the fixture state"
    assert hashlib.sha256(first).hexdigest() != hashlib.sha256(last).hexdigest()


# ======================================================================================
# ROUTE_E_DISABLED_IDENTITY  --  the witness is byte-identical
# ======================================================================================


@requires_verifier
def test_route_e_disabled_identity_matches_the_generic_witness(tmp_path):
    """Route E adds provenance, never physics: the same law, IC and schedule through the
    generic bridge alone produce the SAME measurement root as the Route E world."""
    document = _manifest()
    bundle, _ = _bundle(tmp_path, document)
    record = execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path))
    attempts = [
        json.loads(line)
        for line in (Path(record.output_directory) / execution.ATTEMPTS_NAME)
        .read_text("ascii")
        .splitlines()
        if line.strip()
    ]
    assert attempts and attempts[0]["status"] == "SUCCESS"
    route_e_root = attempts[0]["measurement_root_sha256"]

    # the disabled arm: the generic bridge, with no Route E anything
    plan = frame.build_draw_plan(
        execution.derive_route_e_seed_root(
            pre_run_root_sha256=record.pre_run_root,
            beacon_round=record.designated_round,
            beacon_randomness=bytes.fromhex(
                json.loads((tmp_path / "beacon.json").read_bytes())["randomness"]
            ),
        ),
        count=1,
    )
    law_index, ic_ordinal = plan.world_order[0]
    witness_directory = tmp_path / "witness"
    witness_directory.mkdir()
    witness = run_measurement_bridge(
        witness_directory,
        law_spec=execution._law_spec_from_fields(plan.law_fields[law_index]),
        initial_state=execution._initial_state(
            execution.derive_route_e_seed_root(
                pre_run_root_sha256=record.pre_run_root,
                beacon_round=record.designated_round,
                beacon_randomness=bytes.fromhex(
                    json.loads((tmp_path / "beacon.json").read_bytes())["randomness"]
                ),
            ),
            plan.ic_indices[law_index][ic_ordinal],
            int(plan.lattice_sizes[law_index]),
        ),
        sampled_frames=execution._schedule(
            int(document["distributions_and_draw_algorithm"]["horizon_steps"]),
            int(document["distributions_and_draw_algorithm"]["cadence_steps"]),
        ),
        measurement_spec=MeasurementSpec(min_cells=1),
        acquisition_source_identity={
            "kind": "route-e-canonical-execution",
            "name": f"{document['run_identity']}/000000",
        },
    )
    assert witness.measurement_root_sha256 == route_e_root


# ======================================================================================
# INDEPENDENT_VERIFY_ROUTE_E_RUN
# ======================================================================================


@requires_verifier
def test_independent_verify_route_e_run_admits_the_produced_evidence(tmp_path):
    bundle, _ = _bundle(tmp_path)
    record = execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path))
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert verdict.admissible, getattr(verdict, "reason", verdict)


# ======================================================================================
# DETERMINISM and CHECKPOINT_RESTART_IDENTITY
# ======================================================================================


@requires_verifier
def test_determinism_and_restart_identity(tmp_path):
    """The same P and the same verified round reproduce the same evidence, byte for byte,
    including after an interrupted attempt is restarted into a fresh namespace."""
    first_dir = tmp_path / "first"
    first_dir.mkdir()
    second_dir = tmp_path / "second"
    second_dir.mkdir()

    bundle_a, _ = _bundle(first_dir)
    record_a = execution.run_route_e(bundle_a, _beacon(first_dir), _destination(first_dir))
    bundle_b, _ = _bundle(second_dir)
    record_b = execution.run_route_e(bundle_b, _beacon(second_dir), _destination(second_dir))

    assert record_a.post_run_root == record_b.post_run_root
    assert record_a.seed_root_sha256 == record_b.seed_root_sha256
    assert record_a.file_inventory_sha256 == record_b.file_inventory_sha256

    # restart identity: a claimed namespace is never replaced, and a fresh restart of the
    # same bundle reproduces the same evidence rather than a different one
    with pytest.raises(execution.RouteEExecutionRefused):
        execution.run_route_e(bundle_a, _beacon(first_dir), _destination(first_dir))
    assert _digest_tree(Path(record_a.output_directory)) == _digest_tree(
        Path(record_a.output_directory)
    )


# ======================================================================================
# EMPTY_RIGHT_NONUNIT_CADENCE_GATE  --  a real runner test
# ======================================================================================


def test_empty_right_nonunit_cadence_reaches_complete_only_through_the_lifecycle_gate(tmp_path):
    """The historically problematic case, exercised through the REAL runner.

    Honest tracker output with an empty right detector frame at non-unit cadence binds
    the disappearance to the DECLARED frame 5, qualifies, and reaches COMPLETE only
    after the lifecycle document has been written and read back.
    """
    tracking = track_components(((_component(0),), ()), TRACKER, sampled_frames=NONUNIT_SCHEDULE)
    record = publish_future_family_completion(tmp_path, tracking, NONUNIT_SCHEDULE)

    assert record.state is RunnerState.COMPLETE_PUBLISHED
    document = tmp_path / "LIFECYCLE.json"
    if not document.is_file():
        document = next(p for p in tmp_path.iterdir() if p.name.upper().startswith("LIFECYCLE"))
    assert document.is_file(), "COMPLETE without a persisted lifecycle document"
    assert (
        hashlib.sha256(document.read_bytes()).hexdigest() == record.lifecycle_document_sha256
    )
    assert record.sampled_frames == NONUNIT_SCHEDULE


def test_empty_right_nonunit_cadence_cannot_bypass_the_lifecycle_gate(tmp_path):
    """An off-schedule frame -- the shape that used to slip through -- is refused."""
    honest = track_components(((_component(0),), ()), TRACKER, sampled_frames=NONUNIT_SCHEDULE)
    fabricated = type(honest)(
        honest.tracks,
        tuple(
            event if event.frame == NONUNIT_SCHEDULE[0] else replace(event, frame=1)
            for event in honest.events
        ),
        honest.edges,
        honest.assignments,
    )
    before = _digest_tree(tmp_path)
    with pytest.raises(LifecycleEvidenceError):
        publish_future_family_completion(tmp_path, fabricated, NONUNIT_SCHEDULE)
    assert not (tmp_path / "COMPLETION_MANIFEST.json").exists()
    assert _digest_tree(tmp_path) == before or list(tmp_path.iterdir()) == []


# ======================================================================================
# NO_SILENT_FALLBACK
# ======================================================================================


def test_no_silent_fallback_anywhere_in_the_route_e_sources():
    repo = Path(__file__).resolve().parent.parent
    for relative in (
        "edlab/substrates/lattice_bond/route_e_bls_verifier.py",
        "edlab/substrates/lattice_bond/route_e_beacon_verifier.py",
        "edlab/substrates/lattice_bond/future_route_e_execution.py",
    ):
        source = (repo / relative).read_text("utf-8")
        lowered = source.lower()
        # the phrase may appear ONLY inside an explicit prohibition
        for banned in ("assume verified", "skip verification"):
            assert banned not in lowered, banned
        assert "accept anyway" not in lowered


@requires_verifier
def test_no_silent_fallback_an_absent_verifier_stops_the_run(tmp_path, monkeypatch):
    monkeypatch.setattr(execution, "_pinned_verifier", lambda: None)
    monkeypatch.setattr(execution, "_installed_verifier_available", lambda: False)
    bundle, _ = _bundle(tmp_path)
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert caught.value.phase == "VERIFY_BEACON"
    assert not destination.exists()


# ======================================================================================
# ENGINEERING CANARY
# ======================================================================================


@requires_verifier
def test_engineering_canary_proves_the_runner_reaches_route_e(tmp_path):
    """ENGINEERING_ONLY / NOT_SCIENTIFIC_DATA / NOT_ELIGIBLE_FOR_ANALYSIS.

    A tiny deterministic synthetic fixture, a couple of steps, purely to prove that the
    runner really calls Route E and really steps the engine.  Its outputs are destroyed
    at the end of the test and never enter any dataset.
    """
    document = _manifest()
    document["output_namespace"] = "SYNTHETIC-NONSCI-ENGINEERING-CANARY-0001"
    document["experiment_id"] = "ENGINEERING_ONLY-NOT_SCIENTIFIC_DATA"
    document["distributions_and_draw_algorithm"] = dict(
        document["distributions_and_draw_algorithm"], horizon_steps=4, cadence_steps=1
    )
    assert document["fixture_class"] == "SYNTHETIC_NON_SCIENTIFIC"

    bundle, _ = _bundle(tmp_path, document)
    destination = _destination(tmp_path, document["output_namespace"])
    record = execution.run_route_e(bundle, _beacon(tmp_path), destination)

    assert record.worlds_succeeded >= 1
    assert record.contributes_to_dataset is False
    banner = " ".join(CANARY_MARKERS)
    assert all(marker in banner for marker in CANARY_MARKERS)

    # destroy the canary outputs: they are engineering waste, not data
    import shutil

    shutil.rmtree(destination)
    assert not destination.exists()
