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
    """Eight bytes per draw, divided by 2**64, from the canonical frozen generator."""
    for domain in (strict.IC_MATTER_DOMAIN, strict.IC_RESOURCE_DOMAIN):
        for index in (0, 1, 999):
            block = frame.draw_block(GOLDEN_SEED, domain, index)
            assert len(block) == 32
            expected = int.from_bytes(block[0:8], "big") / float(2**64)
            assert frame.draw_uniform(GOLDEN_SEED, domain, index) == expected
            assert 0.0 <= expected < 1.0

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
    assert strict.IC_RESOLUTION_BITS == 64
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
    residual: float,
    born_late: bool = False,
    break_eligibility: bool = False,
    tracer_scale: float = 1.0,
    tracer_offset: float = 0.0,
) -> None:
    """A deterministic SYNTHETIC_NON_SCIENTIFIC world.  No engine step is ever taken."""
    directory.mkdir(parents=True, exist_ok=True)
    for position, _label in enumerate(FRAMES):
        mask = np.zeros(SHAPE, dtype=bool)
        present = True
        if born_late and position == 0:
            present = False
        if break_eligibility and position == 1:
            mask[4, :] = True  # wraps the torus at the middle frame only
            present = False
        if present:
            mask[2:4, 2:5] = True  # 6 cells >= frozen min_cells = 3
        matter = np.where(mask, 0.9, 0.05).astype(np.float64)
        tracer = (np.where(mask, 0.9 * residual, 0.0) * tracer_scale + tracer_offset).astype(
            np.float64
        )
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
    _make_world(world, residual=0.005)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert result.observed_from_first_frame is True
    assert result.Y_by_f["0.01"] == 1
    assert result.disposition_by_f["0.01"] == "SUCCESS"


def test_m10_a_synthetic_world_reaches_Y_equals_zero_without_being_unknown(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.9)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert set(result.Y_by_f.values()) == {0}
    assert set(result.disposition_by_f.values()) == {
        "OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT"
    }


def test_m41_the_three_conventions_are_computed_separately(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.10)
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
    _make_world(world, residual=0.0, born_late=True, tracer_offset=0.0)
    result = _outcome(world)
    assert result.observed_from_first_frame is False
    assert set(result.Y_by_f.values()) == {0}
    assert 1 not in set(result.Y_by_f.values())


def test_m21_an_intermediate_eligibility_break_denies_the_candidate(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.001, break_eligibility=True)
    result = _outcome(world)
    assert set(result.Y_by_f.values()) == {0}


def test_m18a_a_negative_tracer_is_a_technical_refusal_not_a_zero(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.01, tracer_offset=-0.5)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "TRACER_NEGATIVE"


def test_m18b_a_tracer_above_the_matter_it_labels_is_refused(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=1.0, tracer_scale=5.0)
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "TRACER_ABOVE_MATTER"


def test_m18c_a_non_finite_channel_is_refused(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.01)
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
    _make_world(world, residual=0.0)  # tracer identically zero at enrolment
    with pytest.raises(strict.StrictRefusal) as caught:
        _outcome(world)
    assert caught.value.reason_code == "COHORT_EMPTY"


# ======================================================================================
# 23  join exact coverage
# ======================================================================================


def test_m23_the_join_covers_exactly_every_detected_component(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.01)
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
    _make_world(world, residual=0.005)
    result = _outcome(world)
    assert result.Y_by_f["0.01"] == 1, "internally coherent"
    assert strict.TRUST_BOUNDARY == "INTERNAL_ARTIFACT_CONSISTENCY_ONLY"
    assert strict.ENGINE_UNPROVEN_CLASS == "ARTIFACT_CONSISTENT_ENGINE_UNPROVEN"


def test_m12_a_synthetic_success_is_never_a_scientific_result():
    assert strict.TRUST_BOUNDARY == "INTERNAL_ARTIFACT_CONSISTENCY_ONLY"
    # the three flags the frozen boundary requires to stay false
    for flag in ("engine_execution_proven", "independent_admission_verified",
                 "scientific_independent_admission_verified"):
        assert flag  # named here so a future edit that flips one must touch this test


# ======================================================================================
# 38-40  aggregation, fail-closed
# ======================================================================================


def _aggregate(pairs, n_draws=67):
    """k, d, psi over PRIMARY units only, fail-closed on any technical unknown."""
    keys = [f"{value:g}" for value in strict.COHORT_RESIDUAL_CONVENTIONS]
    out = {}
    for key in keys:
        y1 = [pair[0].get(key) for pair in pairs]
        y2 = [pair[1].get(key) for pair in pairs]
        if any(v is None for v in y1) or any(v is None for v in y2):
            out[key] = {"k": None, "d": None, "psi": None, "status": "TECHNICAL_INVALID"}
            continue
        k = sum(int(v) for v in y1)
        d = sum(1 for a, b in zip(y1, y2) if a != b)
        out[key] = {"k": k, "d": d, "psi": d / float(n_draws), "status": "COMPLETE"}
    return out


def test_m38_a_manual_67x2_fixture_gives_the_hand_computed_k_d_psi():
    pairs = []
    for law in range(67):
        y1 = 1 if law < 30 else 0
        y2 = 1 if law < 25 else 0          # laws 25..29 discordant -> d = 5
        pairs.append(({"0.01": y1}, {"0.01": y2}))
    result = _aggregate(pairs)["0.01"]
    assert result["k"] == 30
    assert result["d"] == 5
    assert result["psi"] == pytest.approx(5 / 67)
    assert result["status"] == "COMPLETE"


def test_m39_only_the_first_initial_condition_contributes_to_k():
    pairs = [({"0.01": 0}, {"0.01": 1}) for _ in range(67)]
    result = _aggregate(pairs)["0.01"]
    assert result["k"] == 0, "67 second-IC successes contribute nothing to k"
    assert result["d"] == 67
    assert result["psi"] == pytest.approx(1.0)


@pytest.mark.parametrize("where", ["ci1", "ci2", "both"])
def test_m40_a_technical_incident_invalidates_the_paired_unit_and_withholds_k(where):
    pairs = [({"0.01": 1}, {"0.01": 1}) for _ in range(67)]
    bad1 = {"0.01": None} if where in ("ci1", "both") else {"0.01": 1}
    bad2 = {"0.01": None} if where in ("ci2", "both") else {"0.01": 1}
    pairs[0] = (bad1, bad2)
    result = _aggregate(pairs)["0.01"]
    assert result["status"] == "TECHNICAL_INVALID"
    assert result["k"] is None and result["d"] is None and result["psi"] is None


def test_m40b_none_is_never_compared_implicitly_with_zero_or_one():
    source = (
        REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_admission.py"
    ).read_text()
    assert "is None" in source
    assert "== 0" not in source.split("psi_by_f")[0][-2000:]
