"""A1-R4 adversarial tests.  Trust boundary: INTERNAL_ARTIFACT_CONSISTENCY_ONLY.

No scientific run, no scientific seed, no engine campaign.  Every fixture is deterministic
and explicitly SYNTHETIC_NON_SCIENTIFIC.  A synthetic success is never a scientific result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from edlab import route_e_aggregate as aggregate
from edlab import route_e_strict as strict
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import future_route_e_world_evidence as evidence
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import MeasurementSpec

REPO_ROOT = Path(__file__).resolve().parents[1]
APPEND_ONLY_RECORD = (
    "docs/individuation/FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00_"
    "CURRENT_SOURCE_QUALIFICATION.json"
)
APPEND_ONLY_SHA256 = "89e824bd27703e8264d52f99b243679035b440a8b46eba6c6a91790a153c234d"

SHAPE = (8, 8)
FRAMES = (0, 16, 32)
SPEC = MeasurementSpec()


# ======================================================================================
# 1-2  append-only governance
# ======================================================================================


def test_m01_the_append_only_record_is_byte_identical_to_its_authoritative_sha256():
    payload = (REPO_ROOT / APPEND_ONLY_RECORD).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == APPEND_ONLY_SHA256


def test_m02_the_restored_record_still_declares_itself_append_only():
    record = json.loads((REPO_ROOT / APPEND_ONLY_RECORD).read_text("utf-8"))
    assert record["append_only"] is True
    assert record["supersedes_nothing_historical"] is True
    assert record["human_review"] == "PENDING"
    # A1-R3 had rewritten this file to bind four modules; the restored A1-R2 record binds two
    assert set(record["current_source_bound_by_this_mission"]) == {
        "edlab/substrates/lattice_bond/future_route_e_execution.py",
        "edlab/substrates/lattice_bond/future_route_e_admission.py",
    }


# ======================================================================================
# 3  frozen measurement specification
# ======================================================================================


def test_m03_min_cells_one_is_refused_and_the_frozen_spec_is_accepted():
    with pytest.raises(strict.StrictRefusal) as caught:
        strict.check_frozen_measurement_spec(MeasurementSpec(min_cells=1))
    assert caught.value.reason_code == "MEASUREMENT_SPEC_NOT_FROZEN"
    assert "frozen at 3" in str(caught.value)
    strict.check_frozen_measurement_spec(MeasurementSpec())


@pytest.mark.parametrize(
    "field,bad",
    [
        ("matter_threshold", 0.5),
        ("min_cells", 2),
        ("max_centroid_displacement", 4.0),
        ("max_area_ratio", 2.0),
        ("dilation_radius", 0),
        ("unique_score_margin", 1e-9),
    ],
)
def test_m03b_every_frozen_constant_is_enforced(field, bad):
    with pytest.raises(strict.StrictRefusal):
        strict.check_frozen_measurement_spec(MeasurementSpec(**{field: bad}))


def test_m03c_the_producer_and_the_admission_share_one_authority():
    producer = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_execution.py"
    ).read_text()
    verifier = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_admission.py"
    ).read_text()
    for text in (producer, verifier):
        assert "MeasurementSpec(min_cells=1)" not in text
        assert "check_frozen_measurement_spec" in text


# ======================================================================================
# 4-5  the canonical 64-bit initial-condition generator
# ======================================================================================


GOLDEN_SEED = bytes.fromhex(
    "1111111111111111111111111111111111111111111111111111111111111111"
)


def test_m04_golden_vectors_bind_the_bytes_consumed_and_the_values_obtained():
    """Eight bytes per draw; the top 53 bits are the value (U53_TOP_BITS_V1).

    PILOT_READINESS_00 owner decision SELECT_OPTION_1_TOP_53_BITS.  The superseded
    expectation on this line was ``word / float(2**64)``; it is replaced, not deleted,
    and the superseded mapping stays reachable under its explicit name so that a
    historical artefact could never be reinterpreted silently.
    """
    for domain in (strict.IC_MATTER_DOMAIN, strict.IC_RESOURCE_DOMAIN):
        for index in (0, 1, 999):
            block = frame.draw_block(GOLDEN_SEED, domain, index)
            assert len(block) == 32
            word = int.from_bytes(block[0:8], "big")
            expected = (word >> 11) * 2.0**-53
            assert frame.draw_uniform(GOLDEN_SEED, domain, index) == expected
            assert 0.0 <= expected < 1.0
            assert expected * 2**53 == float(word >> 11)  # exactly representable
            # the superseded mapping is still callable, and is a DIFFERENT function
            assert frame.draw_uniform_superseded_v0(GOLDEN_SEED, domain, index) == (
                word / float(2**64)
            )

    state = execution._initial_state(GOLDEN_SEED, 0, 4)
    assert state.m[0, 0] == frame.draw_uniform(GOLDEN_SEED, b"IC-M", 0)
    assert state.n[0, 0] == frame.draw_uniform(GOLDEN_SEED, b"IC-N", 0)
    assert state.m[0, 1] == frame.draw_uniform(GOLDEN_SEED, b"IC-M", 1)
    assert float(np.max(np.abs(state.b))) == 0.0


def test_m05_the_four_byte_and_2_pow_32_generator_is_gone():
    source = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_execution.py"
    ).read_text()
    body = source.split("def _uniform_field")[1].split("def _initial_state")[0]
    for forbidden in ("1 << 32", "2**32", "np.random", "default_rng", "import random"):
        assert forbidden not in body, forbidden
    assert strict.IC_WORD_BYTES == 8
    # PILOT_READINESS_00: the declared resolution was 64 and binary64 made that false;
    # under U53_TOP_BITS_V1 it is 53 and the grid is uniform everywhere.
    assert strict.IC_RESOLUTION_BITS == 53
    assert strict.IC_MAPPING_VERSION == "U53_TOP_BITS_V1"
    assert "draw_uniform" in body


def test_m05b_m_and_n_are_two_effectively_separate_streams():
    state = execution._initial_state(GOLDEN_SEED, 0, 16)
    assert not np.array_equal(state.m, state.n)
    correlation = float(np.corrcoef(state.m.ravel(), state.n.ravel())[0, 1])
    assert abs(correlation) < 0.5


# ======================================================================================
# 6-7  the frozen primary shape
# ======================================================================================


def test_m06_the_frozen_primary_shape_is_67_times_2_equals_134():
    assert strict.FROZEN_PRIMARY_SHAPE == {
        "primary_laws": 67, "initial_conditions_per_law": 2, "primary_worlds": 134
    }
    assert (
        strict.FROZEN_PRIMARY_SHAPE["primary_laws"]
        * strict.FROZEN_PRIMARY_SHAPE["initial_conditions_per_law"]
        == strict.FROZEN_PRIMARY_SHAPE["primary_worlds"]
    )


# ======================================================================================
# 31-33  strict manifest validation
# ======================================================================================


def test_m31_a_boolean_is_never_accepted_where_an_integer_is_required():
    with pytest.raises(strict.StrictRefusal) as caught:
        strict.require_plain_int(True, "n_draws", code="X")
    assert "boolean" in str(caught.value)
    assert strict.require_plain_int(67, "n_draws", code="X") == 67


def test_m33a_duplicate_json_keys_are_refused_not_silently_collapsed():
    payload = b'{"kind":"a","kind":"b"}'
    assert json.loads(payload.decode()) == {"kind": "b"}, "json.loads collapses silently"
    with pytest.raises(strict.StrictRefusal) as caught:
        strict.strict_json_object(payload, "doc", "X")
    assert caught.value.reason_code == "DUPLICATE_JSON_KEY"


@pytest.mark.parametrize("literal", [b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'])
def test_m33b_non_finite_json_constants_are_refused(literal):
    with pytest.raises(strict.StrictRefusal):
        strict.strict_json_object(literal, "doc", "X")


def test_m32_a_frozen_float_that_differs_is_refused():
    with pytest.raises(strict.StrictRefusal):
        strict.require_exact_float(0.46, 0.45, "matter_threshold", code="X")
    assert strict.require_exact_float(0.45, 0.45, "matter_threshold", code="X") == 0.45


# ======================================================================================
# 26  path containment
# ======================================================================================


@pytest.mark.parametrize(
    "bad",
    [
        "/etc/passwd", "C:\\windows", "\\\\server\\share", "../escape", "a/../../b",
        "a//b", "a/./b", "a/", "", "with\x00nul", "back\\slash",
    ],
)
def test_m26_absolute_traversal_and_malformed_paths_are_refused(bad):
    with pytest.raises(strict.StrictRefusal):
        strict.contained_relative_path(bad, name="world_relative_path", code="PATH")


def test_m26b_a_well_formed_relative_path_is_accepted():
    assert strict.contained_relative_path("worlds/000000", name="p", code="PATH") == "worlds/000000"


def test_m26c_a_symlink_leaf_or_ancestor_is_refused(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "file.bin").write_bytes(b"x")
    (tmp_path / "link").symlink_to(tmp_path / "real")
    strict.resolve_contained(tmp_path, "real/file.bin", name="p", code="PATH")
    with pytest.raises(strict.StrictRefusal) as caught:
        strict.resolve_contained(tmp_path, "link/file.bin", name="p", code="PATH")
    assert "symlink" in str(caught.value)


def test_m26d_escape_after_resolution_is_refused(tmp_path):
    outside = tmp_path.parent / "outside_target"
    outside.mkdir(exist_ok=True)
    (tmp_path / "esc").symlink_to(outside)
    with pytest.raises(strict.StrictRefusal):
        strict.resolve_contained(tmp_path, "esc", name="p", code="PATH")


# ======================================================================================
# synthetic worlds -- deterministic fixtures, SYNTHETIC_NON_SCIENTIFIC
# ======================================================================================


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _make_world(
    directory: Path,
    *,
    final_residual: float,
    born_late: bool = False,
    break_eligibility: bool = False,
    pre_depleted: bool = False,
    leak_label_outside: bool = False,
    negative_tracer_at_middle: bool = False,
) -> None:
    """A deterministic SYNTHETIC_NON_SCIENTIFIC world with a REAL replacement history.

    At the enrolment frame the tracer equals the matter inside the detected components and
    is zero everywhere else, so ``cohort_residual(t0) == 1`` exactly.  Labelled material
    then leaves and unlabelled material enters, so the residual falls to
    ``final_residual`` at the horizon.  A pre-depleted fixture -- one that starts below 1 --
    is exactly what ``pre_depleted=True`` builds, and the admission must refuse it.
    """
    directory.mkdir(parents=True, exist_ok=True)
    n = len(FRAMES)
    for position, _label in enumerate(FRAMES):
        mask = np.zeros(SHAPE, dtype=bool)
        present = True
        if born_late and position == 0:
            present = False
        if break_eligibility and position == 1:
            mask[4, :] = True
            present = False
        if present:
            mask[2:4, 2:5] = True
        matter = np.where(mask, 0.9, 0.05).astype(np.float64)
        # residual goes 1 -> final_residual linearly in the frame index
        share = 1.0 if position == 0 else (
            1.0 + (final_residual - 1.0) * position / float(n - 1)
        )
        if pre_depleted:
            share = final_residual
        tracer = np.where(mask, 0.9 * share, 0.0).astype(np.float64)
        if leak_label_outside and position == 0:
            tracer[0, 0] = 0.01
        if negative_tracer_at_middle and position == 1:
            tracer[0, 0] = -0.01
        for channel, array in (
            ("mask", mask), ("matter", matter), ("tracer", tracer),
            ("resource", np.full(SHAPE, 0.5)), ("bond", np.zeros(SHAPE)),
        ):
            payload = (
                np.ascontiguousarray(array, dtype=np.bool_).astype(np.uint8).tobytes()
                if channel == "mask"
                else np.ascontiguousarray(array, dtype="<f8").tobytes()
            )
            _write(directory / "measurement_frames" / f"frame_{position:06d}_{channel}.bin", payload)


def _outcome(world: Path):
    return evidence.derive_world_outcome(
        world, sampled_frames=FRAMES, frame_shape=SHAPE,
        detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
    )


# ======================================================================================
# 11 / 10 / 41  Y=1, Y=0, and the three conventions kept separate
# ======================================================================================


def test_m11_a_synthetic_world_reaches_Y_equals_one(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert result.observed_from_first_frame is True
    assert result.Y_by_f["0.01"] == 1
    assert result.disposition_by_f["0.01"] == "SUCCESS"


def test_m10_a_synthetic_world_reaches_Y_equals_zero_without_being_unknown(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.9)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert set(result.Y_by_f.values()) == {0}
    assert set(result.disposition_by_f.values()) == {
        "OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT"
    }


def test_m41_the_three_conventions_are_computed_separately(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.10)
    result = _outcome(world)
    assert result.Y_by_f["0.01"] == 0
    assert result.Y_by_f["0.05"] == 0
    assert result.Y_by_f["0.2"] == 1
    assert len(set(result.Y_by_f.values())) == 2


# ======================================================================================
# 18-21  physical bounds, late birth, eligibility break
# ======================================================================================


def test_m20_a_track_absent_at_enrolment_can_never_produce_Y_equals_one(tmp_path):
    """The trivial-success channel, now closed: residual ~0 but born after enrolment."""
    world = tmp_path / "w"
    _make_world(world, final_residual=0.0, born_late=True)
    result = _outcome(world)
    assert result.observed_from_first_frame is False
    assert set(result.Y_by_f.values()) == {0}
    assert 1 not in set(result.Y_by_f.values())


def test_m21_an_intermediate_eligibility_break_denies_the_candidate(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.001, break_eligibility=True)
    result = _outcome(world)
    assert set(result.Y_by_f.values()) == {0}


def test_m18a_a_negative_tracer_is_a_technical_refusal_not_a_zero(tmp_path):
    """A negative tracer anywhere is a typed refusal, never a silent Y=0."""
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005)
    corrupt = np.full(SHAPE, -0.5, dtype=np.float64)
    _write(
        world / "measurement_frames" / "frame_000002_tracer.bin",
        np.ascontiguousarray(corrupt, dtype="<f8").tobytes(),
    )
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "TRACER_NEGATIVE"


def test_m18b_a_tracer_above_the_matter_it_labels_is_refused(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=1.0, leak_label_outside=True)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "ENROLMENT_LABEL_LEAKED"


def test_m18c_a_non_finite_channel_is_refused(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.01)
    corrupt = np.full(SHAPE, np.nan, dtype=np.float64)
    _write(
        world / "measurement_frames" / "frame_000002_tracer.bin",
        np.ascontiguousarray(corrupt, dtype="<f8").tobytes(),
    )
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "CHANNEL_NON_FINITE"


def test_m19_an_empty_enrolled_cohort_is_a_technical_refusal(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.0, pre_depleted=True)  # tracer identically zero at enrolment
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code in {"ENROLMENT_NOT_FULLY_LABELLED", "ENROLMENT_RESIDUAL_NOT_ONE"}


# ======================================================================================
# 23  join exact coverage
# ======================================================================================


def test_m23_the_join_covers_exactly_every_detected_component(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.01)
    join = evidence.build_join_document(
        world, sampled_frames=FRAMES, frame_shape=SHAPE,
        detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
        horizon_steps=32, cadence_steps=16,
    )
    assert join["assignments"], "a world with components must produce assignments"
    for _frame_label, digest, track_id in join["assignments"]:
        assert track_id >= 0, "A1-R4 refuses track_id < 0 rather than recording it"
        assert len(digest) == 64
    identifiers = [item[2] for item in join["assignments"]]
    assert min(identifiers) >= 0


def test_m23b_a_negative_track_identifier_is_refused_by_construction():
    source = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_world_evidence.py"
    ).read_text()
    assert "JOIN_NEGATIVE_TRACK_ID" in source
    assert "JOIN_ORPHAN_COMPONENT" in source
    assert "JOIN_DUPLICATE" in source
    assert "JOIN_COVERAGE_INEXACT" in source
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert "track_id = -1" not in code
    assert "-1)" not in code


# ======================================================================================
# 36  the trust boundary
# ======================================================================================


def test_m36_a_resealed_but_transitionally_impossible_world_is_engine_unproven(tmp_path):
    """Every frame here was WRITTEN BY HAND.  No engine produced any transition.

    It is internally coherent and it passes recomputation.  That is exactly the point of
    ``INTERNAL_ARTIFACT_CONSISTENCY_ONLY``: internal coherence is not provenance.
    """
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005)
    result = _outcome(world)
    assert result.Y_by_f["0.01"] == 1, "internally coherent"
    assert strict.TRUST_BOUNDARY == "INTERNAL_ARTIFACT_CONSISTENCY_ONLY"
    assert strict.ENGINE_UNPROVEN_CLASS == "ARTIFACT_CONSISTENT_ENGINE_UNPROVEN"


# ======================================================================================
# 38-40  aggregation, fail-closed
# ======================================================================================


def test_m38_a_manual_67x2_fixture_gives_the_hand_computed_k_d_psi():
    pairs = []
    for law in range(67):
        y1 = 1 if law < 30 else 0
        y2 = 1 if law < 25 else 0          # laws 25..29 discordant -> d = 5
        pairs.append(({"0.01": y1}, {"0.01": y2}))
    result = aggregate.aggregate_primary_units(pairs, conventions=(0.01,))["0.01"]
    assert result.k == 30
    assert result.d == 5
    assert result.psi == pytest.approx(5 / 67)
    assert result.status == "COMPLETE"


def test_m39_only_the_first_initial_condition_contributes_to_k():
    pairs = [({"0.01": 0}, {"0.01": 1}) for _ in range(67)]
    result = aggregate.aggregate_primary_units(pairs, conventions=(0.01,))["0.01"]
    assert result.k == 0, "67 second-IC successes contribute nothing to k"
    assert result.d == 67
    assert result.psi == pytest.approx(1.0)


@pytest.mark.parametrize("where", ["ci1", "ci2", "both"])
def test_m40_a_technical_incident_invalidates_the_paired_unit_and_withholds_k(where):
    pairs = [({"0.01": 1}, {"0.01": 1}) for _ in range(67)]
    bad1 = {"0.01": None} if where in ("ci1", "both") else {"0.01": 1}
    bad2 = {"0.01": None} if where in ("ci2", "both") else {"0.01": 1}
    pairs[0] = (bad1, bad2)
    result = aggregate.aggregate_primary_units(pairs, conventions=(0.01,))["0.01"]
    assert result.status == "TECHNICAL_INVALID"
    assert result.k is None and result.d is None and result.psi is None


def test_m40b_none_is_never_compared_implicitly_with_zero_or_one():
    source = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_admission.py"
    ).read_text()
    assert "is None" in source
    assert "== 0" not in source.split("psi_by_f")[0][-2000:]


# ======================================================================================
# A1-R5  Phase 1 -- the enrolment proof
# ======================================================================================


def test_r5_enrolment_residual_is_exactly_one_and_replacement_is_real(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005)
    result = _outcome(world)
    assert result.Y_by_f["0.01"] == 1
    assert min(result.residual_at_horizon.values()) == pytest.approx(0.005, abs=1e-12)


def test_r5_a_pre_depleted_fixture_is_refused(tmp_path):
    """It would satisfy residual <= f without any replacement having occurred."""
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005, pre_depleted=True)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code in {"ENROLMENT_NOT_FULLY_LABELLED", "ENROLMENT_RESIDUAL_NOT_ONE"}


def test_r5_a_label_outside_the_enrolled_union_is_refused(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005, leak_label_outside=True)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "ENROLMENT_LABEL_LEAKED"


def test_r5_bounds_are_checked_at_every_frame_not_only_two(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005, negative_tracer_at_middle=True)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "TRACER_NEGATIVE"
    assert "@16" in str(caught.value), "the MIDDLE frame is the one that must fire"


# ======================================================================================
# A1-R5  Phase 2 -- the classification is a returned field
# ======================================================================================


def test_r5_the_classification_is_returned_not_documented(tmp_path):
    world = tmp_path / "w"
    _make_world(world, final_residual=0.005)
    result = _outcome(world)
    assert result.classification == "ARTIFACT_CONSISTENT_ENGINE_UNPROVEN"
    assert "classification" in type(result).__dataclass_fields__


# ======================================================================================
# A1-R5  Phase 7 -- the PUBLIC aggregator, adversarially
# ======================================================================================


def _ok_pairs(k_true=0):
    return [({"0.01": 1 if i < k_true else 0}, {"0.01": 1 if i < k_true else 0}) for i in range(67)]


@pytest.mark.parametrize("count", [0, 66, 68])
def test_r5_the_aggregator_refuses_any_count_but_67(count):
    with pytest.raises(strict.StrictRefusal) as caught:
        aggregate.aggregate_primary_units(
            _ok_pairs()[:count] if count <= 67 else _ok_pairs() + [({"0.01": 0}, {"0.01": 0})],
            conventions=(0.01,),
        )
    assert caught.value.reason_code == "PRIMARY_UNIT_COUNT_WRONG"


@pytest.mark.parametrize("bad", [2, True, False, 1.0, "1"])
def test_r5_the_aggregator_refuses_a_non_indicator(bad):
    pairs = _ok_pairs()
    pairs[3] = ({"0.01": bad}, {"0.01": 0})
    with pytest.raises(strict.StrictRefusal) as caught:
        aggregate.aggregate_primary_units(pairs, conventions=(0.01,))
    assert caught.value.reason_code in {"INDICATOR_NOT_PLAIN_INT", "INDICATOR_OUT_OF_RANGE"}


def test_r5_the_aggregator_refuses_a_missing_convention_key():
    pairs = _ok_pairs()
    pairs[5] = ({}, {"0.01": 0})
    with pytest.raises(strict.StrictRefusal) as caught:
        aggregate.aggregate_primary_units(pairs, conventions=(0.01,))
    assert caught.value.reason_code == "CONVENTION_ABSENT"


def test_r5_none_is_a_declared_incident_and_invalidates_the_confirmatory_result():
    pairs = _ok_pairs(k_true=40)
    pairs[9] = ({"0.01": None}, {"0.01": 1})
    result = aggregate.aggregate_primary_units(pairs, conventions=(0.01,))["0.01"]
    assert result.status == "TECHNICAL_INVALID"
    assert result.k is None and result.d is None and result.psi is None
    assert result.invalid_units == (9,)


# ======================================================================================
# A1-R5  Phase 8 -- the 64-bit mapping defect, demonstrated not asserted
# ======================================================================================


def test_r5_the_top_of_the_range_maps_to_exactly_one_point_zero():
    """(2**64 - 1) / 2**64 == 1.0 in binary64, so the declared [0,1) is FALSE."""
    assert (2**64 - 1) / float(2**64) == 1.0
    smallest = 18446744073709550592
    assert smallest / float(2**64) == 1.0
    assert (smallest - 1) / float(2**64) < 1.0
    assert 2**64 - smallest == 1024, "exactly 1024 of the 2**64 words round up to 1.0"


def test_r5_the_output_grid_is_not_2_pow_minus_64_near_one():
    """Near 1 the binary64 step is 2**-53, so 1024 distinct words share one output."""
    base = 2**64 - 4096
    values = {(base + offset) / float(2**64) for offset in range(2048)}
    assert len(values) == 2, "2048 consecutive words -> only 2 distinct binary64 outputs"
    # far from 1 the mapping is injective, which is what makes the defect scale-dependent
    small = {offset / float(2**64) for offset in range(2048)}
    assert len(small) == 2048
    assert int(2.0**-53 / 2.0**-64) == 2048


def test_r5_option_one_is_strictly_inside_the_unit_interval():
    """The recommended repair: exact mapping on the top 53 bits."""
    for word in (0, 1, 2**63, 2**64 - 1):
        value = (word >> 11) / float(2**53)
        assert 0.0 <= value < 1.0
        assert value * 2**53 == float(word >> 11), "exactly representable in binary64"
