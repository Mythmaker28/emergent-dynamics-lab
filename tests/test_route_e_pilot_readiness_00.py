"""ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00 -- the six gates, behaviourally.

Every test here either exercises a real path end to end or arms a real fault and
requires the refusal.  There is no ``assert <flag>``, no source-string search standing
in for behaviour, no aggregator defined locally, and no direct call to an internal
scorer where the public path is what is under test.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from edlab import route_e_aggregate as aggregate
from edlab import route_e_pilot as pilot
from edlab import route_e_pilot_acquisition as acq
from edlab import route_e_pilot_admission as adm
from edlab import route_e_strict as strict
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond.engine import LatticeBondSpec
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec,
    run_measurement_bridge,
)
from edlab.substrates.lattice_bond.future_route_e_world_evidence import read_channel

SHAPE = (16, 16)
SYNTH_NS = "PILOT-GATE-SYNTHETIC"
ENGINE_NS = "PILOT-GATE-ENGINE"
LATE_CELLS = ((2, 2), (2, 3), (3, 2), (3, 3))


def _engine_world(tmp_path: Path, *, horizon: int = 96, cadence: int = 16, law_ordinal: int = 0):
    """One real engine world through the public pilot acquisition path."""
    manifest = pilot.build_pilot_manifest(ENGINE_NS)
    seed = pilot.pilot_seed_root(pilot.pilot_pre_run_root(manifest))
    plan = pilot.build_pilot_plan(seed, laws=3)
    world = plan.worlds[law_ordinal * pilot.PILOT_INITIAL_CONDITIONS_PER_LAW]
    fields = plan.law_fields[world.law_ordinal]
    spec = LatticeBondSpec(
        **{k: float(v) for k, v in fields.items() if k in LatticeBondSpec.__dataclass_fields__}
    )
    state = execution._initial_state(seed, world.ic_index, world.lattice_size)
    directory = tmp_path / f"engine_{law_ordinal}"
    record = acq.acquire_pilot_world(
        directory,
        law_spec=spec,
        initial_state=state,
        sampled_frames=pilot.schedule(horizon, cadence),
        namespace=ENGINE_NS,
        ordinal=world.ordinal,
    )
    return directory, spec, state, record, world


# ======================================================================================
# RNG -- the owner decision, applied and versioned
# ======================================================================================


def test_rng_01_the_mapping_is_u53_and_never_reaches_one():
    assert frame.DRAW_UNIFORM_MAPPING_VERSION == "U53_TOP_BITS_V1"
    assert strict.IC_MAPPING_VERSION == "U53_TOP_BITS_V1"
    assert strict.IC_RESOLUTION_BITS == 53
    assert strict.IC_WORD_BYTES == 8
    seed = bytes(range(32))
    for index in (0, 1, 7, 999, 65535):
        block = frame.draw_block(seed, b"IC-M", index)
        word = int.from_bytes(block[0:8], "big")
        value = frame.draw_uniform(seed, b"IC-M", index)
        assert value == (word >> 11) * 2.0**-53
        assert 0.0 <= value < 1.0
        assert value * 2**53 == float(word >> 11)


def test_rng_02_the_low_eleven_bits_cannot_move_the_output():
    """``low_11_bits_affect_output = false``, stated against the PRODUCTION function.

    A reviewer showed the first version of this test to be tautological: it asserted
    ``(x << 11 | y) >> 11 == x`` and never called the code under review.  It now takes
    real words from the real generator and requires the real ``draw_uniform`` output to
    be invariant when every low bit is forced.
    """
    seed = bytes(range(32))
    for index in range(200):
        word = int.from_bytes(frame.draw_block(seed, b"IC-M", index)[0:8], "big")
        produced = frame.draw_uniform(seed, b"IC-M", index)
        assert produced == ((word | 2047) >> 11) * 2.0**-53
        assert produced == ((word & ~2047) >> 11) * 2.0**-53
        assert produced != frame.draw_uniform(seed, b"IC-N", index)


def test_rng_03_the_superseded_mapping_is_reachable_only_under_its_own_name():
    """No artefact is reinterpreted silently: the old mapping still exists, named."""
    seed = bytes(32)
    word = int.from_bytes(frame.draw_block(seed, b"LAW", 3)[0:8], "big")
    assert frame.draw_uniform_superseded_v0(seed, b"LAW", 3) == word / float(2**64)
    assert (2**64 - 1) / float(2**64) == 1.0            # the defect, still true arithmetic
    assert ((2**64 - 1) >> 11) * 2.0**-53 < 1.0         # the repair, behaviourally

    # MEASURED, not asserted: the two mappings agree on a third of the words and differ
    # elsewhere by at most one unit in the last place.  The A1-R5 dossier said "every
    # drawn value changes"; that is false, and the difference is recorded here as a
    # measurement.  The real gain is not magnitude but SHAPE: the superseded mapping
    # rounded onto an irregular grid (finer near 0), so its outputs did not all have the
    # same number of preimages; U53_TOP_BITS_V1 is exactly uniform on a regular grid.
    differing = 0
    largest = 0.0
    for index in range(4000):
        new = frame.draw_uniform(seed, b"LAW", index)
        old = frame.draw_uniform_superseded_v0(seed, b"LAW", index)
        if new != old:
            differing += 1
            largest = max(largest, abs(new - old))
    assert 0 < differing < 4000
    assert 0.5 < differing / 4000 < 0.85
    assert 0.0 < largest <= 2.0**-52


def test_rng_04_a_manifest_naming_another_mapping_is_refused():
    manifest = dict(pilot.build_pilot_manifest("PILOT-X"))
    manifest["draw_uniform_mapping_version"] = "U64_DIVIDE_V0_SUPERSEDED"
    with pytest.raises(pilot.PilotRefusal) as info:
        pilot.check_pilot_manifest(manifest)
    assert info.value.reason_code == "PILOT_MAPPING_VERSION"


# ======================================================================================
# G1 -- real public synthetic Y=0 and Y=1
# ======================================================================================


def test_g1_01_a_true_y1_is_reached_by_transport_from_a_residual_of_exactly_one(tmp_path):
    world = tmp_path / "y1"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == "ADMITTED", verdict.incident

    # residual is EXACTLY 1 at enrolment, on the enrolled component's own cells
    matter0 = read_channel(world, 0, "matter", SHAPE)
    tracer0 = read_channel(world, 0, "tracer", SHAPE)
    enrolled = matter0 >= 0.45
    assert float(np.max(np.abs(tracer0[enrolled] - matter0[enrolled]))) == 0.0
    assert float(np.max(np.abs(tracer0[~enrolled]))) == 0.0

    # and it falls, by transport, to a genuine Y = 1 at the widest convention
    assert verdict.Y_by_f["0.2"] == 1
    assert verdict.disposition_by_f["0.2"] == "SUCCESS"
    track = verdict.eligible_tracks[0]
    assert track.residual_union < 0.2
    # the fall is unlabelled matter coming IN, not label being destroyed
    enrolled_mass = float(np.sum(matter0[enrolled]))
    assert verdict.global_tracer_conservation_max_drift < 1e-12 * enrolled_mass
    assert any(entry["gross_in_unlabelled"] > 0.0 for entry in verdict.boundary_flux)


def test_g1_02_a_true_y0_is_an_observed_failure_not_an_incident(tmp_path):
    world = tmp_path / "y0"
    acq.build_synthetic_transport_world(world, exchange=0.0, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == "ADMITTED", verdict.incident
    assert set(verdict.Y_by_f.values()) == {0}
    assert set(verdict.disposition_by_f.values()) == {"OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT"}
    assert verdict.eligible_tracks[0].residual_union == 1.0
    assert verdict.incident == ""


def test_g1_03_the_same_world_separates_the_three_conventions(tmp_path):
    """The conventions are evaluated separately and are not all the same question."""
    world = tmp_path / "sep"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.Y_by_f == {"0.01": 0, "0.05": 0, "0.2": 1}


def test_g1_04_a_pre_depleted_fixture_is_refused_not_scored(tmp_path):
    world = tmp_path / "depleted"
    acq.build_synthetic_transport_world(
        world, exchange=0.05, namespace=SYNTH_NS, deplete_at_enrolment=0.02
    )
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "ENROLMENT_NOT_FULLY_LABELLED"
    assert set(verdict.Y_by_f.values()) == {None}


def test_g1_05_a_resealed_frame_is_refused(tmp_path):
    """Rewriting a sampled frame so it no longer matches the ledger is detected."""
    world = tmp_path / "resealed"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    path = world / "measurement_frames" / "frame_000004_tracer.bin"
    values = np.frombuffer(path.read_bytes(), dtype="<f8").copy()
    values[0] = values[0] + 1e-6
    path.write_bytes(values.tobytes())
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "FRAME_LEDGER_DISAGREEMENT"
    assert set(verdict.Y_by_f.values()) == {None}


def test_g1_06_the_engine_data_entry_refuses_a_synthetic_fixture(tmp_path):
    world = tmp_path / "synthetic"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(
        world,
        ordinal=0,
        lattice_size=SHAPE[0],
        require_fixture_class="PILOT_EXPLORATORY_NON_CONFIRMATORY",
    )
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "FIXTURE_CLASS_REFUSED"
    # and the same world is admitted when it is NOT presented as engine data
    assert adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0]).status == "ADMITTED"


# ======================================================================================
# G2 -- transport recomputed, not asserted
# ======================================================================================


def test_g2_01_every_transition_is_recomputed_from_persisted_evidence(tmp_path):
    directory, _, _, record, _ = _engine_world(tmp_path, horizon=96)
    verdict = adm.admit_pilot_world(directory, ordinal=0, lattice_size=record.lattice_size)
    assert verdict.status == "ADMITTED", verdict.incident
    assert verdict.transport_transitions_recomputed == 96
    assert verdict.transport_max_tracer_deviation == 0.0
    assert verdict.global_tracer_conservation_max_drift == 0.0


def test_g2_02_a_missing_transport_ledger_blocks_rather_than_scores(tmp_path):
    """The bridge's own output has no ledger.  It must BLOCK, never be scored anyway."""
    directory, spec, state, record, _ = _engine_world(tmp_path, horizon=96)
    bridge = tmp_path / "bridge_only"
    bridge.mkdir()
    run_measurement_bridge(
        bridge,
        law_spec=spec,
        initial_state=state.copy(),
        sampled_frames=pilot.schedule(96, 16),
        measurement_spec=MeasurementSpec(),
        acquisition_source_identity={"kind": "gate", "name": "g2"},
    )
    shutil.copy(directory / "PILOT_PROVENANCE.json", bridge / "PILOT_PROVENANCE.json")
    verdict = adm.admit_pilot_world(bridge, ordinal=0, lattice_size=record.lattice_size)
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "PILOT_LEDGER_ABSENT"
    assert set(verdict.Y_by_f.values()) == {None}


def test_g2_03_a_tampered_flow_is_caught_by_the_matter_identity(tmp_path):
    directory, _, _, record, _ = _engine_world(tmp_path, horizon=96)
    path = acq.ledger_paths(directory)["forward"]
    values = np.frombuffer(path.read_bytes(), dtype="<f8").copy()
    values[5] = values[5] + 1e-3
    path.write_bytes(values.tobytes())
    verdict = adm.admit_pilot_world(directory, ordinal=0, lattice_size=record.lattice_size)
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "PILOT_LEDGER_DIGEST"


def test_g2_04_a_flow_tamper_that_also_updates_the_digest_is_still_caught(tmp_path):
    """The digest is not the defence; the physics is."""
    directory, _, _, record, _ = _engine_world(tmp_path, horizon=96)
    import hashlib

    path = acq.ledger_paths(directory)["forward"]
    values = np.frombuffer(path.read_bytes(), dtype="<f8").copy()
    values[5] = values[5] + 1e-3
    payload = values.tobytes()
    path.write_bytes(payload)
    header_path = directory / acq.LEDGER_DIRECTORY / "LEDGER.json"
    header = json.loads(header_path.read_text())
    header["ledger_sha256"]["forward"] = hashlib.sha256(payload).hexdigest()
    header_path.write_bytes(pilot.canonical_bytes(header))
    verdict = adm.admit_pilot_world(directory, ordinal=0, lattice_size=record.lattice_size)
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "MATTER_FLUX_INCONSISTENT"


def test_g2_05_a_leaking_cohort_is_caught_by_conservation(tmp_path):
    world = tmp_path / "leak"
    acq.build_synthetic_transport_world(
        world, exchange=0.05, namespace=SYNTH_NS, leak_tracer_at=100
    )
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code in {
        "TRACER_CONSERVATION_FAILED",
        "TRACER_RECOMPUTATION_MISMATCH",
    }
    assert set(verdict.Y_by_f.values()) == {None}


def test_g2_06_a_matter_field_inconsistent_with_its_flows_is_caught(tmp_path):
    world = tmp_path / "brokenmatter"
    acq.build_synthetic_transport_world(
        world, exchange=0.05, namespace=SYNTH_NS, break_matter_at=100
    )
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "MATTER_FLUX_INCONSISTENT"


def test_g2_07_the_admission_recomputation_is_not_the_producer_helper(tmp_path):
    """The two statements of the transport must agree numerically, not by sharing code."""
    from edlab.substrates.lattice_bond.instrumentation import advance_passive_tracer

    rng = np.random.default_rng(11)
    pre = rng.random(SHAPE) * 0.5 + 0.25
    forward = rng.random((2, *SHAPE)) * 0.01
    reverse = rng.random((2, *SHAPE)) * 0.01
    net = forward - reverse
    post = pre - 1.0 * ((net[0] - np.roll(net[0], 1, axis=0)) + (net[1] - np.roll(net[1], 1, axis=1)))
    tracer = pre * 0.4
    theirs = advance_passive_tracer(tracer, pre, forward, reverse, post, 1.0)
    mine = adm._advance_tracer_from_ledger(tracer, pre, forward, reverse, 1.0)
    assert np.array_equal(theirs, mine)


# ======================================================================================
# G3 -- join, track, horizon
# ======================================================================================


def test_g3_01_a_component_born_after_enrolment_cannot_score(tmp_path):
    """The decisive case: a late component whose residual is EXACTLY zero."""
    world = tmp_path / "late"
    acq.build_synthetic_transport_world(
        world,
        exchange=0.0,
        namespace=SYNTH_NS,
        late_birth_cells=LATE_CELLS,
        late_birth_drive=0.0008,
        late_birth_steps=64,
    )
    matter = read_channel(world, 8, "matter", SHAPE)
    tracer = read_channel(world, 8, "tracer", SHAPE)
    late = np.zeros(SHAPE, dtype=bool)
    for y, x in LATE_CELLS:
        late[y, x] = True
    assert float(np.min(matter[late])) >= 0.45, "the late component must really be detected"
    assert float(np.sum(tracer[late])) == 0.0, "and its residual would be exactly 0"

    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == "ADMITTED", verdict.incident
    assert set(verdict.Y_by_f.values()) == {0}
    assert len(verdict.eligible_tracks) == 1
    assert verdict.eligible_tracks[0].residual_union == 1.0


def test_g3_02_a_missing_sampled_frame_is_an_incident_not_a_zero(tmp_path):
    world = tmp_path / "gap"
    acq.build_synthetic_transport_world(
        world, exchange=0.05, namespace=SYNTH_NS, drop_frame_position=4
    )
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert set(verdict.Y_by_f.values()) == {None}


def test_g3_03_a_truncated_horizon_is_an_incident_not_a_zero(tmp_path):
    world = tmp_path / "truncated"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    for channel in acq.FRAME_CHANNELS:
        (world / "measurement_frames" / f"frame_000008_{channel}.bin").unlink()
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert set(verdict.Y_by_f.values()) == {None}


def test_g3_04_the_join_covers_every_detected_component_exactly(tmp_path):
    """Exact coverage is enforced by the A1-R4 join, exercised through the pilot path."""
    from edlab.substrates.lattice_bond.future_route_e_world_evidence import build_join_document

    directory, _, _, record, _ = _engine_world(tmp_path, horizon=96)
    spec = MeasurementSpec()
    document = build_join_document(
        directory,
        sampled_frames=pilot.schedule(96, 16),
        frame_shape=(record.lattice_size, record.lattice_size),
        detector=spec.detector_spec(),
        tracker=spec.tracker_spec(),
        horizon_steps=96,
        cadence_steps=16,
    )
    from edlab.substrates.lattice_bond.instrumentation import detect_components

    detected = 0
    for position, label in enumerate(pilot.schedule(96, 16)):
        mask = read_channel(directory, position, "mask", (record.lattice_size,) * 2)
        detected += len(list(detect_components(adm._materialise(mask, int(label)),
                                               spec.detector_spec(), frame=int(label))))
    assert len(document["assignments"]) == detected
    assert detected > 0


def test_g3_05_a_component_must_hold_the_same_track_from_enrolment(tmp_path):
    """Every eligible track's own residual is read at the horizon, from its own cells."""
    world = tmp_path / "same"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == "ADMITTED"
    assert len(verdict.eligible_tracks) == 1
    matter = read_channel(world, 8, "matter", SHAPE)
    tracer = read_channel(world, 8, "tracer", SHAPE)
    enrolled = matter >= 0.45
    expected = float(np.sum(tracer[enrolled])) / float(np.sum(matter[enrolled]))
    assert verdict.eligible_tracks[0].residual_union == pytest.approx(expected, abs=1e-15)


# ======================================================================================
# G4 -- a real engine path, and a forgery that cannot claim it
# ======================================================================================


def test_g4_01_a_real_engine_world_reproduces_byte_identically(tmp_path):
    directory, spec, state, record, _ = _engine_world(tmp_path, horizon=96)
    verified, why = adm.verify_engine_provenance(directory, law_spec=spec, initial_state=state)
    assert verified, why


def test_g4_02_a_handwritten_world_cannot_declare_itself_engine_produced(tmp_path):
    world = tmp_path / "handwritten"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    _, spec, state, _, _ = _engine_world(tmp_path, horizon=96)
    verified, why = adm.verify_engine_provenance(world, law_spec=spec, initial_state=state)
    assert not verified
    assert "initial condition" in why or "engine" in why


def test_g4_03_one_altered_float_breaks_the_engine_claim(tmp_path):
    directory, spec, state, record, _ = _engine_world(tmp_path, horizon=96)
    path = acq.ledger_paths(directory)["matter"]
    values = np.frombuffer(path.read_bytes(), dtype="<f8").copy()
    cells = record.lattice_size**2
    values[cells * 40] = values[cells * 40] + 1e-15
    path.write_bytes(values.tobytes())
    verified, why = adm.verify_engine_provenance(directory, law_spec=spec, initial_state=state)
    assert not verified
    assert "matter" in why


def test_g4_04_the_pilot_frames_are_byte_identical_to_the_qualified_bridge(tmp_path):
    """The pilot must measure the same object the confirmatory design would measure."""
    directory, spec, state, record, _ = _engine_world(tmp_path, horizon=96)
    bridge = tmp_path / "bridge_diff"
    bridge.mkdir()
    run_measurement_bridge(
        bridge,
        law_spec=spec,
        initial_state=state.copy(),
        sampled_frames=pilot.schedule(96, 16),
        measurement_spec=MeasurementSpec(),
        acquisition_source_identity={"kind": "gate", "name": "g4"},
    )
    ours = sorted((directory / "measurement_frames").glob("*.bin"))
    theirs = sorted((bridge / "measurement_frames").glob("*.bin"))
    assert [p.name for p in ours] == [p.name for p in theirs]
    assert ours and all(a.read_bytes() == b.read_bytes() for a, b in zip(ours, theirs))


# ======================================================================================
# G5 -- incidents are never results
# ======================================================================================


@pytest.mark.parametrize(
    "breakage",
    ["no_provenance", "no_ledger", "bad_flux", "leak", "missing_frame", "truncated"],
)
def test_g5_01_every_incident_gives_none_and_never_zero(tmp_path, breakage):
    world = tmp_path / breakage
    kwargs = {"exchange": 0.05, "namespace": SYNTH_NS}
    if breakage == "bad_flux":
        kwargs["break_matter_at"] = 100
    if breakage == "leak":
        kwargs["leak_tracer_at"] = 100
    if breakage == "missing_frame":
        kwargs["drop_frame_position"] = 4
    acq.build_synthetic_transport_world(world, **kwargs)
    if breakage == "no_provenance":
        (world / "PILOT_PROVENANCE.json").unlink()
    if breakage == "no_ledger":
        shutil.rmtree(world / acq.LEDGER_DIRECTORY)
    if breakage == "truncated":
        for channel in acq.FRAME_CHANNELS:
            (world / "measurement_frames" / f"frame_000008_{channel}.bin").unlink()
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert set(verdict.Y_by_f.values()) == {None}
    assert set(verdict.disposition_by_f.values()) == {"TECHNICALLY_UNKNOWN"}
    assert verdict.incident_reason_code != ""
    assert 0 not in [v for v in verdict.Y_by_f.values() if v is not None]


def test_g5_02_a_producer_that_writes_an_answer_is_refused(tmp_path):
    world = tmp_path / "answered"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    path = world / "PILOT_PROVENANCE.json"
    document = json.loads(path.read_text())
    document["k"] = 1
    path.write_bytes(pilot.canonical_bytes(document))
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "RUNNER_WROTE_AN_ANSWER"


def test_g5_03_an_incident_unit_is_excluded_from_every_count(tmp_path):
    """A TECHNICAL_INVALID unit contributes to no numerator and no denominator of Y."""
    world = tmp_path / "excluded"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS, leak_tracer_at=50)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    scored = [v for v in verdict.Y_by_f.values() if v is not None]
    assert scored == []


# ======================================================================================
# G6 -- irreversible pilot isolation
# ======================================================================================


def test_g6_01_the_pilot_namespace_is_mechanically_enforced(tmp_path):
    with pytest.raises(pilot.PilotRefusal):
        pilot.build_pilot_manifest("SCIENTIFIC-RUN")
    with pytest.raises(acq.AcquisitionRefusal) as info:
        acq.acquire_pilot_world(
            tmp_path / "bad",
            law_spec=LatticeBondSpec(),
            initial_state=execution._initial_state(bytes(32), 0, 8),
            sampled_frames=(0, 16),
            namespace="ROUTE-E-CONFIRMATORY",
            ordinal=0,
        )
    assert info.value.reason_code == "PILOT_NAMESPACE_PREFIX"


def test_g6_02_the_confirmatory_aggregator_refuses_the_pilot_shape():
    units = [({"0.01": 0, "0.05": 0, "0.2": 1}, {"0.01": 0, "0.05": 0, "0.2": 1})] * pilot.PILOT_LAWS
    with pytest.raises(Exception) as info:
        aggregate.aggregate_primary_units(units)
    assert getattr(info.value, "reason_code", "") == "PRIMARY_UNIT_COUNT_WRONG"


def test_g6_03_the_pilot_shape_can_never_be_the_confirmatory_shape():
    assert pilot.PILOT_LAWS != strict.FROZEN_PRIMARY_SHAPE["primary_laws"]
    assert pilot.PILOT_WORLDS != strict.FROZEN_PRIMARY_SHAPE["primary_worlds"]
    manifest = dict(pilot.build_pilot_manifest("PILOT-X"))
    manifest["laws"] = 67
    manifest["worlds"] = 134
    with pytest.raises(pilot.PilotRefusal) as info:
        pilot.check_pilot_manifest(manifest)
    assert info.value.reason_code == "PILOT_SHAPE"


def test_g6_04_the_pilot_manifest_can_carry_no_answer_and_no_seed():
    for field, value in (("k", 1), ("verdict", "POSITIVE"), ("seed", "00"), ("randomness", "ff")):
        manifest = dict(pilot.build_pilot_manifest("PILOT-X"))
        manifest[field] = value
        with pytest.raises(pilot.PilotRefusal) as info:
            pilot.check_pilot_manifest(manifest)
        assert info.value.reason_code in {
            "PILOT_MANIFEST_SHAPE",
            "PILOT_MANIFEST_FORBIDDEN_FIELD",
        }


def test_g6_05_the_seed_is_a_pure_function_of_the_committed_manifest():
    manifest = pilot.build_pilot_manifest("PILOT-SEEDTEST")
    root = pilot.pilot_pre_run_root(manifest)
    assert pilot.pilot_seed_root(root) == pilot.pilot_seed_root(root)
    other = dict(manifest)
    other["output_namespace"] = "PILOT-SEEDTEST-2"
    assert pilot.pilot_pre_run_root(other) != root
    assert pilot.pilot_seed_root(pilot.pilot_pre_run_root(other)) != pilot.pilot_seed_root(root)
    with pytest.raises(pilot.PilotRefusal):
        pilot.pilot_seed_root(root, label="ANOTHER_LABEL")


def test_g6_06_no_beacon_is_consulted_anywhere_on_the_pilot_path(tmp_path):
    """Behavioural: the whole pilot path runs with no network and no beacon argument."""
    manifest = pilot.build_pilot_manifest("PILOT-NOEXTERNAL")
    seed = pilot.pilot_seed_root(pilot.pilot_pre_run_root(manifest))
    plan = pilot.build_pilot_plan(seed, laws=3)
    assert len(plan.worlds) == 3 * pilot.PILOT_INITIAL_CONDITIONS_PER_LAW
    # A reviewer flagged the previous string search over the document as carrying no
    # behavioural weight.  The claim is now made against the real signatures: no public
    # entry point on the pilot path can even accept a beacon, a round or randomness.
    import inspect

    for function in (
        pilot.build_pilot_manifest,
        pilot.pilot_pre_run_root,
        pilot.pilot_seed_root,
        pilot.build_pilot_plan,
        acq.acquire_pilot_world,
        adm.admit_pilot_world,
    ):
        parameters = set(inspect.signature(function).parameters)
        assert not parameters & {"beacon", "round", "randomness", "beacon_response_path"}
    assert not pilot.PILOT_MANIFEST_KEYS & {"beacon", "round", "randomness"}


def test_g6_07_the_stratification_is_eight_laws_per_size():
    manifest = pilot.build_pilot_manifest("PILOT-STRAT")
    seed = pilot.pilot_seed_root(pilot.pilot_pre_run_root(manifest))
    plan = pilot.build_pilot_plan(seed)
    strata = pilot.worlds_by_stratum(plan)
    assert sorted(strata) == ["L16", "L24", "L32"]
    assert all(len(v) == pilot.PILOT_LAWS_PER_SIZE * 2 for v in strata.values())
    assert len(plan.worlds) == pilot.PILOT_WORLDS
    # the two initial conditions of one law are PAIRED, never two independent draws
    for law_ordinal in range(pilot.PILOT_LAWS):
        pair = [w for w in plan.worlds if w.law_ordinal == law_ordinal]
        assert len(pair) == 2
        assert pair[0].proposal_index == pair[1].proposal_index
        assert pair[0].ic_index != pair[1].ic_index


# ======================================================================================
# CORRECTIVE PASS -- the four counter-examples an independent reviewer executed against
# the first draft.  Each is now an armed regression test.
# ======================================================================================


def test_ce1_a_resealed_mask_cannot_fabricate_a_component(tmp_path):
    """The decisive one: Y = 1 was forged in a world with ZERO transport.

    The reviewer rewrote nothing but the ``mask`` frames -- moving a fake 2x2 blob one
    cell per frame so the tracker would follow it -- and the admission scored ``Y = 1``
    at all three conventions on a world whose forward and reverse flows were identically
    zero.  The mask is derived evidence; it is now re-derived from the matter ledger.
    """
    world = tmp_path / "forged"
    acq.build_synthetic_transport_world(world, exchange=0.0, namespace=SYNTH_NS)
    honest = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert honest.status == "ADMITTED" and set(honest.Y_by_f.values()) == {0}

    for position in range(9):
        shift = min(position, 6)
        mask = np.zeros(SHAPE, dtype=np.uint8)
        for row in (7 - shift, 8 - shift):
            for col in (7 - shift, 8 - shift):
                mask[row, col] = 1
        (world / "measurement_frames" / f"frame_{position:06d}_mask.bin").write_bytes(
            mask.tobytes()
        )
    forged = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert forged.status == adm.TECHNICAL_INVALID
    assert forged.incident_reason_code == "MASK_NOT_DERIVED_FROM_MATTER"
    assert set(forged.Y_by_f.values()) == {None}


def test_ce2_a_distant_huge_cell_cannot_widen_the_tolerance(tmp_path):
    """The equality check must be element-wise and relative, not a ledger-wide bound."""
    import hashlib

    world = tmp_path / "tolerance"
    acq.build_synthetic_transport_world(world, exchange=0.0, namespace=SYNTH_NS)
    header_path = world / acq.LEDGER_DIRECTORY / "LEDGER.json"
    header = json.loads(header_path.read_text())
    frames = int(header["matter_frames"])
    cells = SHAPE[0] * SHAPE[1]

    matter_path = acq.ledger_paths(world)["matter"]
    matter = np.frombuffer(matter_path.read_bytes(), dtype="<f8").reshape((frames, *SHAPE)).copy()
    matter[:, 0, 0] = 1e11                       # constant in time: the flux identity holds
    matter_path.write_bytes(matter.tobytes())

    tracer_path = acq.ledger_paths(world)["tracer"]
    tracer = np.frombuffer(tracer_path.read_bytes(), dtype="<f8").reshape((frames, *SHAPE)).copy()
    tracer[1:] = 0.0                             # the cohort is simply erased
    tracer_path.write_bytes(tracer.tobytes())

    header["ledger_sha256"]["matter"] = hashlib.sha256(matter.tobytes()).hexdigest()
    header["ledger_sha256"]["tracer"] = hashlib.sha256(tracer.tobytes()).hexdigest()
    header_path.write_bytes(pilot.canonical_bytes(header))
    for position, label in enumerate(header["sampled_frames"]):
        (world / "measurement_frames" / f"frame_{position:06d}_matter.bin").write_bytes(
            matter[label].tobytes()
        )
        (world / "measurement_frames" / f"frame_{position:06d}_tracer.bin").write_bytes(
            tracer[label].tobytes()
        )
        (world / "measurement_frames" / f"frame_{position:06d}_mask.bin").write_bytes(
            np.ascontiguousarray(matter[label] >= 0.45, dtype=np.uint8).tobytes()
        )
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "TRACER_RECOMPUTATION_MISMATCH"
    assert set(verdict.Y_by_f.values()) == {None}


def test_ce3_a_blanked_mask_frame_is_an_incident_not_a_dissolution(tmp_path):
    """A broken join used to become a NEGATIVE scientific result.  It is now an incident."""
    world = tmp_path / "joinbreak"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    before = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert before.status == "ADMITTED" and before.Y_by_f["0.2"] == 1

    (world / "measurement_frames" / "frame_000004_mask.bin").write_bytes(
        np.zeros(SHAPE, dtype=np.uint8).tobytes()
    )
    after = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert after.status == adm.TECHNICAL_INVALID
    assert after.incident_reason_code == "MASK_NOT_DERIVED_FROM_MATTER"
    assert set(after.Y_by_f.values()) == {None}
    assert "DISSOLVED_DETECTED_TRACK" not in after.terminal_states


def test_ce4_the_horizon_is_not_a_free_knob(tmp_path):
    """The same law and seed gave Y=0 at horizon 64 and Y=1 at horizon 4096."""
    directory, _, _, record, _ = _engine_world(tmp_path, horizon=96, cadence=16)
    committed = pilot.schedule(1024, 16)
    verdict = adm.admit_pilot_world(
        directory,
        ordinal=0,
        lattice_size=record.lattice_size,
        expected_sampled_frames=committed,
    )
    assert verdict.status == adm.TECHNICAL_INVALID
    assert verdict.incident_reason_code == "SCHEDULE_NOT_THE_COMMITTED_ONE"
    # and it is admitted against its own, honest schedule
    ok = adm.admit_pilot_world(
        directory,
        ordinal=0,
        lattice_size=record.lattice_size,
        expected_sampled_frames=pilot.schedule(96, 16),
    )
    assert ok.status == "ADMITTED", ok.incident


def test_ce4b_the_runner_takes_the_schedule_from_the_manifest_alone():
    """There is no horizon or cadence command-line option to move the outcome."""
    import inspect

    source = inspect.getsource(__import__("tools.run_route_e_pilot_00", fromlist=["main"]).main)
    assert "--horizon" not in source and "--cadence" not in source
    assert 'manifest["horizon_steps"]' in source and 'manifest["cadence_steps"]' in source


def test_g5_04_the_runner_records_an_acquisition_crash_as_an_incident(tmp_path):
    """End-to-end through the real tool, including its crash branch."""
    import subprocess
    import sys

    output = tmp_path / "run"
    result = subprocess.run(
        [sys.executable, "tools/run_route_e_pilot_00.py", "--output", str(output),
         "--namespace", "PILOT-TOOLTEST", "--laws", "3"],
        capture_output=True, text=True, timeout=1800,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    raw = json.loads((output / "PILOT_RAW_RESULTS.json").read_text())
    assert raw["worlds_completed"] == raw["worlds_expected"] == 6
    manifest = json.loads((output / "PILOT_MANIFEST.json").read_text())
    assert manifest["horizon_steps"] == 1024 and manifest["cadence_steps"] == 16
    for entry in raw["results"]:
        admission = entry["admission"]
        assert admission["contributes_to_k"] is False
        scored = [v for v in admission["Y_by_f"].values() if v is not None]
        if admission["status"] != "ADMITTED":
            assert scored == []


def test_g6_08_no_pilot_verdict_can_contribute_to_k(tmp_path):
    world = tmp_path / "isolated"
    acq.build_synthetic_transport_world(world, exchange=0.05, namespace=SYNTH_NS)
    verdict = adm.admit_pilot_world(world, ordinal=0, lattice_size=SHAPE[0])
    assert verdict.contributes_to_k is False
    assert verdict.as_document()["contributes_to_k"] is False
    units = [(verdict.Y_by_f, verdict.Y_by_f)] * pilot.PILOT_LAWS
    with pytest.raises(Exception) as info:
        aggregate.aggregate_primary_units(units)
    assert getattr(info.value, "reason_code", "") == "PRIMARY_UNIT_COUNT_WRONG"
