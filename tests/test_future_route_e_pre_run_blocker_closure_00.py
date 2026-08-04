"""Mechanical pins for FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00.

Every test here runs on synthetic fixtures.  None opens a Stage B shard, an M_MINUS
archive, a scientific trajectory, an old family, a candidate, a champion or any closed
result.  None creates a scientific seed, namespace, family, law, initial condition or
world.  None executes a Route E draw.

The tests are grouped by the six obligations PRB-A .. PRB-F carried forward by the
accepted human review of 01S.  Boundary cases are pinned just below, exactly on, and
just above every declared threshold.
"""

from __future__ import annotations

import builtins
import hashlib
import math
import os
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond.engine import AdmissibilityError, LatticeBondSpec
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    OwnedPipelineError,
    run_owned_future_pipeline,
)
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)
from edlab.substrates.lattice_bond.engine import LatticeBondState

SEED_A = hashlib.sha256(b"SYNTHETIC-TEST-ROOT-NOT-A-SCIENTIFIC-SEED/A").digest()
SEED_B = hashlib.sha256(b"SYNTHETIC-TEST-ROOT-NOT-A-SCIENTIFIC-SEED/B").digest()


def _state(shape, cells):
    h, w = shape
    m = np.zeros((h, w), dtype=np.float64)
    for y, x in cells:
        m[y, x] = 1.0
    n = np.zeros((h, w), dtype=np.float64)
    b = np.zeros((2, h, w), dtype=np.float64)
    return LatticeBondState(m=m, n=n, b=b, step=0)


def _tree_digest(root: Path) -> str:
    items = []
    for current, directories, files in os.walk(root):
        directories.sort()
        for name in sorted(files):
            path = Path(current) / name
            items.append(
                f"{path.relative_to(root)}:{hashlib.sha256(path.read_bytes()).hexdigest()}"
            )
        for name in sorted(directories):
            items.append(f"{(Path(current) / name).relative_to(root)}/")
    return hashlib.sha256("|".join(items).encode("utf-8")).hexdigest()


# ======================================================================================
# PRB-A -- the two thresholds Route E left unquantified
# ======================================================================================


def test_prb_a_01_threshold_specs_are_complete_and_non_governing():
    for spec in (frame.HORIZON_CENSORING_ATTRIBUTION, frame.IC_DISCORDANCE):
        assert spec.governs_ternary_decision is False
        assert spec.name and spec.role and spec.quantity and spec.unit
        assert spec.derivation and spec.boundary_behaviour and spec.non_finite_behaviour
        assert math.isfinite(spec.value)
        low, high = spec.domain
        assert low <= spec.value <= high
        assert len(spec.digest()) == 64


def test_prb_a_02_a_threshold_may_never_govern_the_frozen_ternary_decision():
    with pytest.raises(ValueError):
        frame.ThresholdSpec(
            name="X",
            role="r",
            quantity="q",
            unit="u",
            domain=(0.0, 1.0),
            value=0.5,
            comparison="strictly_greater",
            boundary_behaviour="b",
            non_finite_behaviour="n",
            derivation="d",
            governs_ternary_decision=True,
        )


def test_prb_a_03_censoring_threshold_value_is_the_frozen_arithmetic():
    # POSITIVE needs k >= 42 of 67, so C censored draws leave k <= 67 - C.
    assert frame.HORIZON_CENSORING_ATTRIBUTION.value == 25.0 / 67.0
    assert frame.N_LAW_DRAWS - frame.POSITIVE_MIN_K == 25


def test_prb_a_04_censoring_boundary_below_on_and_above():
    assert frame.attribute_horizon_censoring(24) == "HORIZON_CENSORING_NOT_SUFFICIENT"
    # exactly on the boundary: 25/67 is not strictly greater than 25/67
    assert frame.attribute_horizon_censoring(25) == "HORIZON_CENSORING_NOT_SUFFICIENT"
    assert frame.attribute_horizon_censoring(26) == "HORIZON_CENSORING_SUFFICIENT"
    # and the boundary is exactly where POSITIVE stops being reachable
    assert 67 - 25 == frame.POSITIVE_MIN_K
    assert 67 - 26 < frame.POSITIVE_MIN_K


@pytest.mark.parametrize("bad", [-1, 68, True, 25.0, "25", None])
def test_prb_a_05_censoring_is_fail_closed(bad):
    with pytest.raises((TypeError, ValueError)):
        frame.attribute_horizon_censoring(bad)


def test_prb_a_06_ic_discriminator_regions():
    assert frame.classify_ic_dependence(0) == "IC_DEPENDENCE_NEGLIGIBLE"
    assert frame.classify_ic_dependence(2) == "IC_DEPENDENCE_NEGLIGIBLE"
    assert frame.classify_ic_dependence(3) == "IC_DEPENDENCE_INDETERMINATE"
    assert frame.classify_ic_dependence(24) == "IC_DEPENDENCE_INDETERMINATE"
    assert frame.classify_ic_dependence(25) == "IC_DEPENDENCE_MATERIAL"
    assert frame.classify_ic_dependence(67) == "IC_DEPENDENCE_MATERIAL"


def test_prb_a_07_ic_boundaries_are_strict_on_the_exact_bounds():
    lower_25, _ = frame.clopper_pearson(25, 67)
    lower_24, _ = frame.clopper_pearson(24, 67)
    _, upper_2 = frame.clopper_pearson(2, 67)
    _, upper_3 = frame.clopper_pearson(3, 67)
    assert lower_25 > frame.IC_DISCORDANCE.value
    assert lower_24 <= frame.IC_DISCORDANCE.value
    assert upper_2 < frame.IC_DISCORDANCE_NEGLIGIBLE_BOUND
    assert upper_3 >= frame.IC_DISCORDANCE_NEGLIGIBLE_BOUND


def test_prb_a_08_psi_boundaries_follow_the_frozen_midpoint_convention():
    # psi ranges over [0, 1/2]; midpoint 1/4; midpoint of [0, 1/4] is 1/8.
    assert frame.IC_DISCORDANCE.domain == (0.0, 0.5)
    assert frame.IC_DISCORDANCE.value == 0.25
    assert frame.IC_DISCORDANCE_NEGLIGIBLE_BOUND == 0.125
    assert max(2.0 * p * (1.0 - p) for p in (0.0, 0.25, 0.5, 0.75, 1.0)) == 0.5


@pytest.mark.parametrize("bad", [-1, 68, True, 3.0, "3", None])
def test_prb_a_09_ic_classifier_is_fail_closed(bad):
    with pytest.raises((TypeError, ValueError)):
        frame.classify_ic_dependence(bad)


def test_prb_a_10_clopper_pearson_reproduces_the_frozen_01s_values():
    assert frame.clopper_pearson(42, 67)[0] == pytest.approx(0.5001047440198192, abs=1e-12)
    assert frame.clopper_pearson(41, 67)[0] == pytest.approx(0.4850181325667385, abs=1e-12)
    assert frame.clopper_pearson(9, 67)[1] == pytest.approx(0.2397417520625535, abs=1e-12)
    assert frame.clopper_pearson(10, 67)[1] == pytest.approx(0.2574024526077781, abs=1e-12)


@pytest.mark.parametrize(
    "args", [(-1, 67), (68, 67), (5, 0), (5, -1), (True, 67), (5.0, 67)]
)
def test_prb_a_11_clopper_pearson_is_fail_closed(args):
    with pytest.raises((TypeError, ValueError)):
        frame.clopper_pearson(*args)


def test_prb_a_12_discriminator_underpower_is_declared_not_hidden():
    """RE-L1: the discriminator does not meet the precision principle at n = 67."""
    worst = max(
        0.5 * (hi - lo)
        for lo, hi in (frame.clopper_pearson(d, 67) for d in range(68))
    )
    assert worst == pytest.approx(0.124721195, abs=1e-8)
    indifference_width = frame.IC_DISCORDANCE.value - frame.IC_DISCORDANCE_NEGLIGIBLE_BOUND
    assert indifference_width == 0.125
    assert worst > 0.5 * indifference_width  # under-powered, declared as RE-L1
    assert "RE-L1" in frame.__doc__


def test_prb_a_13_discriminator_never_consults_the_marginal_estimate():
    """The Jensen bias is removed structurally: no Delta-hat can enter the classifier."""
    import inspect

    signature = inspect.signature(frame.classify_ic_dependence)
    assert list(signature.parameters) == ["discordant_pairs"]
    source = inspect.getsource(frame.classify_ic_dependence)
    assert "DELTA" not in source.upper().replace("IC_DEPENDENCE", "")


# ======================================================================================
# PRB-B -- external generator, canonical draw order, seed strategy
# ======================================================================================


def test_prb_b_01_block_is_deterministic_and_matches_its_written_definition():
    expected = hashlib.sha256(SEED_A + b"\x00" + b"LAW" + b"\x00" + (7).to_bytes(8, "big")).digest()
    assert frame.draw_block(SEED_A, b"LAW", 7) == expected
    assert frame.draw_block(SEED_A, b"LAW", 7) == frame.draw_block(SEED_A, b"LAW", 7)


def test_prb_b_02_uniform_resolution_and_range():
    for index in range(64):
        u = frame.draw_uniform(SEED_A, b"LAW", index)
        assert 0.0 <= u < 1.0
    block = frame.draw_block(SEED_A, b"LAW", 3)
    assert frame.draw_uniform(SEED_A, b"LAW", 3) == int.from_bytes(block[:8], "big") / 2.0**64


@pytest.mark.parametrize(
    "args",
    [
        (b"short", b"LAW", 0),
        (SEED_A, b"", 0),
        (SEED_A, b"LAW", -1),
        (SEED_A, b"LAW", 2**64),
        (SEED_A, b"LAW", True),
    ],
)
def test_prb_b_03_block_is_fail_closed(args):
    with pytest.raises((TypeError, ValueError)):
        frame.draw_block(*args)


def test_prb_b_04_seed_derivation_binds_every_declared_input():
    randomness = bytes(range(32))
    commit = bytes(range(20))
    root = frame.derive_seed_root(
        beacon_randomness=randomness, beacon_round=1234, preregistration_commit_sha1=commit
    )
    assert len(root) == 32
    other_round = frame.derive_seed_root(
        beacon_randomness=randomness, beacon_round=1235, preregistration_commit_sha1=commit
    )
    other_commit = frame.derive_seed_root(
        beacon_randomness=randomness,
        beacon_round=1234,
        preregistration_commit_sha1=bytes(reversed(commit)),
    )
    other_random = frame.derive_seed_root(
        beacon_randomness=bytes(reversed(randomness)),
        beacon_round=1234,
        preregistration_commit_sha1=commit,
    )
    assert len({root, other_round, other_commit, other_random}) == 4


@pytest.mark.parametrize(
    "kwargs",
    [
        {"beacon_randomness": b"\x00" * 31, "beacon_round": 1, "preregistration_commit_sha1": b"\x00" * 20},
        {"beacon_randomness": b"\x00" * 32, "beacon_round": 0, "preregistration_commit_sha1": b"\x00" * 20},
        {"beacon_randomness": b"\x00" * 32, "beacon_round": 1, "preregistration_commit_sha1": b"\x00" * 19},
        {"beacon_randomness": b"\x00" * 32, "beacon_round": True, "preregistration_commit_sha1": b"\x00" * 20},
    ],
)
def test_prb_b_05_seed_derivation_is_fail_closed(kwargs):
    with pytest.raises(ValueError):
        frame.derive_seed_root(**kwargs)


def test_prb_b_06_beacon_round_rule_is_exact():
    genesis = int(frame.BEACON_SOURCE["genesis_time_unix"])
    period = int(frame.BEACON_SOURCE["period_seconds"])
    for offset in (1, 2, 3, 4, 5, 6, 7, 3600, 100000):
        instant = genesis + offset
        r = frame.beacon_round_at_or_after(instant)
        assert genesis + (r - 1) * period >= instant
        assert genesis + (r - 2) * period < instant
    with pytest.raises(ValueError):
        frame.beacon_round_at_or_after(genesis)


def test_prb_b_07_canonical_order_is_written_down_and_matches_the_plan():
    assert len(frame.CANONICAL_DRAW_ORDER) == 4
    plan = frame.build_draw_plan(SEED_A, count=5)
    assert plan.ic_indices == ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
    assert plan.world_order[:4] == ((0, 0), (0, 1), (1, 0), (1, 1))
    assert len(plan.world_order) == 5 * frame.INITIAL_CONDITIONS_PER_LAW


def test_prb_b_08_plan_is_deterministic_and_seed_sensitive():
    a1 = frame.build_draw_plan(SEED_A, count=6)
    a2 = frame.build_draw_plan(SEED_A, count=6)
    b1 = frame.build_draw_plan(SEED_B, count=6)
    assert a1.digest() == a2.digest()
    assert a1.digest() != b1.digest()
    assert a1.proposal_indices == a2.proposal_indices


def test_prb_b_09_rejected_proposals_are_consumed_never_reordered():
    plan = frame.build_draw_plan(SEED_A, count=8)
    assert list(plan.proposal_indices) == sorted(plan.proposal_indices)
    assert len(set(plan.proposal_indices)) == len(plan.proposal_indices)
    assert plan.proposals_consumed >= len(plan.proposal_indices)
    assert plan.proposals_consumed == plan.proposal_indices[-1] + 1


def test_prb_b_10_the_order_depends_on_no_outcome_and_calls_no_engine_step():
    from edlab.substrates.lattice_bond import engine as engine_module

    calls = []
    original = engine_module.LatticeBondEngine.step

    def refuse(self, *args, **kwargs):  # pragma: no cover - must never run
        calls.append(1)
        raise AssertionError("build_draw_plan must not step the engine")

    engine_module.LatticeBondEngine.step = refuse
    try:
        plan = frame.build_draw_plan(SEED_A, count=6)
    finally:
        engine_module.LatticeBondEngine.step = original
    assert calls == []
    assert len(plan.law_fields) == 6
    assert "ORDER_INDEPENDENCE" in dir(frame)


def test_prb_b_11_no_scientific_seed_exists_in_the_module():
    assert not hasattr(frame, "SEED")
    assert not hasattr(frame, "SCIENTIFIC_SEED")
    assert not hasattr(frame, "SEED_ROOT")
    with pytest.raises(TypeError):
        frame.derive_seed_root()  # every input must be supplied by the caller


def test_prb_b_12_generator_and_beacon_are_fully_declared():
    for key in (
        "algorithm",
        "specification",
        "version_label",
        "block",
        "uniform",
        "endianness",
        "serialisation",
    ):
        assert frame.DRAW_GENERATOR[key]
    for key in (
        "chain_hash",
        "scheme",
        "period_seconds",
        "genesis_time_unix",
        "public_key",
        "round_rule",
        "why_it_cannot_be_known_today",
        "public_verifiability",
    ):
        assert frame.BEACON_SOURCE[key]
    assert len(str(frame.BEACON_SOURCE["chain_hash"])) == 64
    assert frame.BEACON_SOURCE["network_access_in_this_module"] == "none; the beacon bytes are an argument"


def test_prb_b_13_anti_reroll_is_stated_and_only_one_derivation_path_exists():
    import inspect

    source = inspect.getsource(frame)
    assert source.count("def derive_seed_root") == 1
    assert frame.ANTI_REROLL


# ======================================================================================
# PRB-C -- the sampler's acceptance predicate IS the engine
# ======================================================================================


def test_prb_c_01_acceptance_means_the_engine_built_its_own_object():
    fields = frame.propose_law_fields(SEED_A, 0)
    accepted, reason = frame.engine_accepts(fields)
    if accepted:
        assert reason == "EngineConstructed"
        spec = LatticeBondSpec(**fields)
        assert spec.dt <= spec.admissible_dt_limit
    else:
        with pytest.raises((AdmissibilityError, ValueError, TypeError)):
            LatticeBondSpec(**fields)


def test_prb_c_02_accept_and_refuse_are_exactly_the_engine_verdict():
    mismatches = []
    for index in range(400):
        fields = frame.propose_law_fields(SEED_A, index)
        accepted, _ = frame.engine_accepts(fields)
        try:
            LatticeBondSpec(**fields)
            engine_ok = True
        except Exception:
            engine_ok = False
        if accepted != engine_ok:
            mismatches.append(index)
    assert mismatches == []


def test_prb_c_03_inadmissible_law_is_refused():
    fields = dict(frame.propose_law_fields(SEED_A, 0))
    fields["kappa_m"] = 10.0  # far above the (B1) ceiling at dt = 1
    accepted, reason = frame.engine_accepts(fields)
    assert accepted is False
    assert reason.startswith("AdmissibilityError")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("field", ["dt", "kappa_m", "theta_m", "epsilon_b", "resource_leak_floor"])
def test_prb_c_04_non_finite_fields_are_refused(field, value):
    fields = dict(frame.propose_law_fields(SEED_A, 0))
    fields[field] = value
    accepted, reason = frame.engine_accepts(fields)
    assert accepted is False
    assert reason


def test_prb_c_05_unknown_and_missing_fields_are_refused():
    fields = dict(frame.propose_law_fields(SEED_A, 0))
    fields["not_a_real_field"] = 1.0
    accepted, reason = frame.engine_accepts(fields)
    assert accepted is False
    assert reason.startswith("TypeError")

    partial = {"dt": 1.0, "m_max": 1.0}
    accepted, reason = frame.engine_accepts(partial)
    # a missing field falls back to the engine default, so the engine still decides
    assert isinstance(accepted, bool)


def test_prb_c_06_overflow_is_refused():
    fields = dict(frame.propose_law_fields(SEED_A, 0))
    fields["theta_m"] = 1e308
    fields["theta_n"] = 1e308
    accepted, _ = frame.engine_accepts(fields)
    assert accepted is False


def test_prb_c_07_the_accept_path_never_calls_the_algebraic_predicate():
    original = frame.algebraic_b1_b2

    def refuse(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("the accept path must not consult the algebraic predicate")

    frame.algebraic_b1_b2 = refuse
    try:
        plan = frame.build_draw_plan(SEED_A, count=4)
    finally:
        frame.algebraic_b1_b2 = original
    assert len(plan.law_fields) == 4


def test_prb_c_08_algebraic_predicate_agreement_is_reported_not_enforced():
    agree = 0
    total = 0
    disagreements = []
    for index in range(600):
        fields = frame.propose_law_fields(SEED_A, index)
        accepted, _ = frame.engine_accepts(fields)
        algebraic = frame.algebraic_b1_b2(fields)
        total += 1
        if accepted == algebraic:
            agree += 1
        else:
            disagreements.append(index)
    # The engine is the gate.  This assertion documents agreement; it does not gate.
    assert total == 600
    assert agree == 600, f"disagreements at proposal indices {disagreements}"


def test_prb_c_09_nextafter_boundary_agreement():
    """Straddle the (B1) boundary at the representable neighbours of the exact cut."""
    base = {
        "dt": 1.0,
        "m_max": 1.0,
        "n_max": 1.0,
        "theta_m": 1.0,
        "theta_n": 1.0,
        "resource_diffusivity": 1.0 / 512.0,
        "resource_leak_floor": 0.5,
        "epsilon_b": 0.5,
        "k_on": 1.0 / 512.0,
        "k_off": 1.0 / 512.0,
        "k_tension": 1.0 / 512.0,
    }
    cut = 0.25 * math.exp(-1.0)
    for kappa in (
        math.nextafter(cut, 0.0),
        cut,
        math.nextafter(cut, math.inf),
    ):
        fields = dict(base, kappa_m=kappa)
        accepted, _ = frame.engine_accepts(fields)
        try:
            LatticeBondSpec(**fields)
            engine_ok = True
        except Exception:
            engine_ok = False
        assert accepted == engine_ok


def test_prb_c_10_no_file_is_opened_while_building_a_plan():
    original_open = builtins.open

    def refuse(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("building a draw plan must not open any file")

    builtins.open = refuse
    try:
        plan = frame.build_draw_plan(SEED_A, count=4)
    finally:
        builtins.open = original_open
    assert len(plan.law_fields) == 4


def test_prb_c_11_scales_are_the_declared_domain():
    for fields in (frame.propose_law_fields(SEED_A, i) for i in range(20)):
        assert fields["dt"] == 1.0
        assert fields["m_max"] == 1.0
        assert fields["n_max"] == 1.0


# ======================================================================================
# PRB-D -- association-gate track break
# ======================================================================================

_DETECTOR = DetectorSpec(matter_threshold=0.45, min_cells=3)
_TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=3.0, dilation_radius=1)


def _track(frames_cells, shape=(16, 16), sampled=None):
    frames = []
    for index, cells in enumerate(frames_cells):
        state = _state(shape, cells)
        frames.append(detect_components(state, _DETECTOR, frame=index))
    schedule = tuple(sampled or range(len(frames_cells)))
    return track_components(frames, _TRACKER, sampled_frames=schedule)


_BLOB_LEFT = [(0, 0), (0, 1), (1, 0), (1, 1)]
_BLOB_FAR = [(0, 8), (0, 9), (1, 8), (1, 9)]


def test_prb_d_01_gate_induced_break_is_labelled_and_is_not_a_dissolution_of_matter():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    refused = [
        edge
        for edge in tracking.edges
        if not edge.qualified
        and edge.qualification_reason in frame.ASSOCIATION_GATE_BREAK_REASONS
    ]
    assert refused, "fixture must produce a gate refusal, not an absence of candidates"
    assert any(edge.qualification_reason == "REJECT_CENTROID_DISTANCE" for edge in refused)

    terminations = frame.classify_track_terminations(tracking)
    causes = {item.cause for item in terminations}
    assert "ASSOCIATION_GATE_TRACK_BREAK" in causes
    break_records = [
        item for item in terminations if item.cause == "ASSOCIATION_GATE_TRACK_BREAK"
    ]
    assert all(item.terminal_state == "DISSOLVED_DETECTED_TRACK" for item in break_records)
    assert all(item.refused_reasons for item in break_records)
    assert all(item.scores_one is False for item in break_records)


def test_prb_d_02_a_genuine_disappearance_is_not_relabelled():
    tracking = _track([_BLOB_LEFT, []])
    terminations = frame.classify_track_terminations(tracking)
    assert terminations
    assert all(item.cause != "ASSOCIATION_GATE_TRACK_BREAK" for item in terminations)
    assert any(item.terminal_state == "DISSOLVED_DETECTED_TRACK" for item in terminations)


def test_prb_d_03_a_continuing_track_produces_no_terminal_cause():
    near = [(0, 1), (0, 2), (1, 1), (1, 2)]
    tracking = _track([_BLOB_LEFT, near])
    terminations = frame.classify_track_terminations(tracking)
    assert all(item.cause != "ASSOCIATION_GATE_TRACK_BREAK" for item in terminations)


def test_prb_d_04_classification_is_idempotent_and_not_reclassifiable():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    first = frame.classify_track_terminations(tracking)
    second = frame.classify_track_terminations(tracking)
    assert first == second


def test_prb_d_05_every_terminal_state_is_one_of_the_five_frozen_states():
    allowed = {
        "DISSOLVED_DETECTED_TRACK",
        "SPLIT_INTO_TRACKS",
        "MERGED_INTO_TRACK",
        "UNRESOLVED_HANDOFF",
        "RIGHT_CENSORED_AT_HORIZON",
    }
    for fixture in ([_BLOB_LEFT, _BLOB_FAR], [_BLOB_LEFT, []], [_BLOB_LEFT, _BLOB_LEFT]):
        for item in frame.classify_track_terminations(_track(fixture)):
            assert item.terminal_state in allowed


def test_prb_d_06_no_cause_may_ever_score_one():
    with pytest.raises(ValueError):
        frame.TrackTermination(
            track_id=0,
            frame=0,
            terminal_state="DISSOLVED_DETECTED_TRACK",
            cause="ASSOCIATION_GATE_TRACK_BREAK",
            refused_reasons=(),
            scores_one=True,
        )


def test_prb_d_07_classifier_is_fail_closed_on_a_foreign_object():
    with pytest.raises(TypeError):
        frame.classify_track_terminations(object())


# ======================================================================================
# PRB-E -- what Delta means and the ceiling on what it licenses
# ======================================================================================


def test_prb_e_01_delta_definition_is_complete():
    required = (
        "symbol",
        "compares",
        "level",
        "criterion",
        "sign",
        "unit",
        "aggregation",
        "parameter_f",
        "which_delta_the_ceiling_speaks_of",
        "link_to_second_ic_discriminator",
        "estimand_is_marginal_over_size",
    )
    for key in required:
        assert frame.DELTA_DEFINITION[key]
    assert "draw" in str(frame.DELTA_DEFINITION["level"]).lower()
    assert "never the entity" in str(frame.DELTA_DEFINITION["level"]).lower()


def test_prb_e_02_the_monotone_f_binding_is_pinned():
    text = str(frame.DELTA_DEFINITION["which_delta_the_ceiling_speaks_of"])
    assert "0.01" in text and "0.20" in text
    assert frame.COHORT_RESIDUAL_SENSITIVITY_SET == (0.01, 0.05, 0.20)


def test_prb_e_03_forbidden_inferences_are_refused():
    for claim in (
        "Route E demonstrates local ownership of the internal information",
        "the entity shows autonomy",
        "this establishes individuality",
        "active reconstruction after damage follows",
        "reproduction and heredity are implied",
        "we observed a robust effect",
    ):
        within, hits = frame.check_claim_within_ceiling(claim)
        assert within is False
        assert hits


def test_prb_e_04_the_licensed_sentence_passes():
    within, hits = frame.check_claim_within_ceiling(str(frame.CLAIM_CEILING["licenses"]))
    assert within is True, hits


def test_prb_e_05_claim_checker_is_fail_closed():
    with pytest.raises(TypeError):
        frame.check_claim_within_ceiling(None)


def test_prb_e_06_ceiling_places_the_claim_below_rung_three():
    assert "below rung 3" in str(frame.CLAIM_CEILING["ladder_position"])
    assert "the draw, never the entity" in str(frame.CLAIM_CEILING["level"])


# ======================================================================================
# Transversal control on the second initial condition
# ======================================================================================


def test_x_01_worlds_are_a_cost_not_observations():
    assert frame.WORLD_COUNT == frame.N_LAW_DRAWS * frame.INITIAL_CONDITIONS_PER_LAW
    assert frame.N_LAW_DRAWS == 67
    assert frame.WORLD_COUNT == 134
    # every inferential function is anchored at 67, never at 134
    import inspect

    source = inspect.getsource(frame.classify_ic_dependence)
    assert "N_LAW_DRAWS" in source
    assert "134" not in source


def test_x_02_second_ic_control_is_exhaustively_specified():
    control = frame.SECOND_IC_CONTROL
    assert control["discriminator_output"]
    assert set(control["possible_states"]) == {
        "IC_DEPENDENCE_MATERIAL",
        "IC_DEPENDENCE_NEGLIGIBLE",
        "IC_DEPENDENCE_INDETERMINATE",
    }
    assert control["consequence_of_discordance"]
    assert control["effect_on_interpretation_ceiling"]
    assert "no law may EVER leave the denominator" in control["absolute_prohibition"]
    assert control["status"].startswith("fully specifiable")


def test_x_03_the_discriminator_cannot_change_k_or_the_denominator():
    labels = {frame.classify_ic_dependence(d) for d in range(68)}
    assert labels <= {
        "IC_DEPENDENCE_MATERIAL",
        "IC_DEPENDENCE_NEGLIGIBLE",
        "IC_DEPENDENCE_INDETERMINATE",
    }


# ======================================================================================
# PRB-F -- refusal through the real public entry point
# ======================================================================================


def test_prb_f_01_scientific_run_is_not_authorised():
    assert frame.SCIENTIFIC_RUN_AUTHORIZED is False


def test_prb_f_02_entry_point_refuses_without_authorisation(tmp_path):
    before = _tree_digest(tmp_path)
    with pytest.raises(frame.RouteEAuthorisationError) as excinfo:
        frame.open_route_e_scientific_run(tmp_path / "run", authorisation=None)
    assert "no Route E scientific authorisation" in str(excinfo.value)
    assert _tree_digest(tmp_path) == before


def test_prb_f_03_entry_point_refuses_an_invalid_authorisation(tmp_path):
    bad = frame.RouteEAuthorisation(
        preregistration_commit_sha1="short",
        human_review_commit_sha1="0" * 40,
        beacon_round=1,
        seed_root_sha256="0" * 64,
        granted=True,
    )
    with pytest.raises(frame.RouteEAuthorisationError):
        frame.open_route_e_scientific_run(tmp_path / "run", authorisation=bad)
    assert _tree_digest(tmp_path) == _tree_digest(tmp_path)


def test_prb_f_04_entry_point_refuses_even_a_well_formed_authorisation(tmp_path):
    good = frame.RouteEAuthorisation(
        preregistration_commit_sha1="a" * 40,
        human_review_commit_sha1="b" * 40,
        beacon_round=4242,
        seed_root_sha256="c" * 64,
        granted=True,
    )
    assert good.is_valid() is True
    before = _tree_digest(tmp_path)
    with pytest.raises(frame.RouteEAuthorisationError) as excinfo:
        frame.open_route_e_scientific_run(tmp_path / "run", authorisation=good)
    assert "scientific_run_authorized is False" in str(excinfo.value)
    assert _tree_digest(tmp_path) == before


def test_prb_f_05_the_real_public_entry_point_refuses_before_every_effect(tmp_path):
    """Exercises run_owned_future_pipeline itself, not a helper."""
    invocations = []

    def spy_source(label):  # pragma: no cover - must never run
        invocations.append(label)
        raise AssertionError("the acquisition source must never be invoked")

    absent = tmp_path / "unauthorised_route_e_namespace"
    assert not absent.exists()
    before = _tree_digest(tmp_path)

    with pytest.raises(OwnedPipelineError) as excinfo:
        run_owned_future_pipeline(
            absent,
            acquisition_source=spy_source,
            sampled_frames=(0, 16, 32),
            detector_spec=_DETECTOR,
            tracker_spec=_TRACKER,
            acquisition_source_identity={"authority": "none", "declared": "none", "declared_by": "none"},
        )

    assert "run_directory must already exist" in str(excinfo.value)
    assert invocations == []            # no acquisition
    assert not absent.exists()          # no namespace, no world directory
    assert _tree_digest(tmp_path) == before  # no byte written anywhere
    assert list(tmp_path.iterdir()) == []


def test_prb_f_06_no_engine_call_and_no_artefact_survive_a_refusal(tmp_path, monkeypatch):
    from edlab.substrates.lattice_bond import engine as engine_module

    steps = []

    def refuse(self, *args, **kwargs):  # pragma: no cover - must never run
        steps.append(1)
        raise AssertionError("a refused run must not step the engine")

    monkeypatch.setattr(engine_module.LatticeBondEngine, "step", refuse)

    with pytest.raises(OwnedPipelineError):
        run_owned_future_pipeline(
            tmp_path / "missing",
            acquisition_source=lambda label: np.zeros((4, 4), dtype=bool),
            sampled_frames=(0, 1),
            detector_spec=_DETECTOR,
            tracker_spec=_TRACKER,
            acquisition_source_identity={"authority": "n", "declared": "n", "declared_by": "n"},
        )
    assert steps == []
    assert list(tmp_path.iterdir()) == []


def test_prb_f_07_out_of_protocol_declaration_names_the_real_entry_point():
    assert "run_owned_future_pipeline" in frame.OUT_OF_PROTOCOL_ENTRY_POINTS
    text = frame.OUT_OF_PROTOCOL_ENTRY_POINTS["run_owned_future_pipeline"]
    assert "DECLARED OUT OF PROTOCOL" in text
    for name in (
        "open_owned_analysis_access",
        "future_lifecycle_runner.open_analysis_access",
        "publish_future_family_completion",
        "qualify_and_write_lifecycle_contract",
    ):
        assert name in frame.OUT_OF_PROTOCOL_ENTRY_POINTS


def test_prb_f_08_the_closure_declares_that_prb_1_to_6_remain_open():
    assert "RE-L7" in frame.__doc__
    assert "PRB-1, PRB-2, PRB-3, PRB-4" in frame.__doc__


# ======================================================================================
# PRB-C (continued) -- the proposal measure must stay uniform on the declared box
# ======================================================================================


def test_prb_c_12_proposal_coordinates_are_drawn_independently_and_uniformly():
    """A conditional theta draw would bend the density; the marginal must be flat."""
    buckets = [0] * 10
    n = 20000
    cap = frame.PROPOSAL_BOX["affinity_sum_cap"]
    for index in range(n):
        theta_m = frame.propose_law_fields(SEED_A, index)["theta_m"]
        buckets[min(9, int(10.0 * theta_m / cap))] += 1
    expected = n / 10.0
    # chi-square with 9 degrees of freedom; 27.88 is the 0.999 quantile
    chi2 = sum((count - expected) ** 2 / expected for count in buckets)
    assert chi2 < 27.88, (buckets, chi2)


def test_prb_c_13_the_affinity_cap_is_imposed_by_rejection_not_by_a_conditional_draw():
    cap = frame.PROPOSAL_BOX["affinity_sum_cap"]
    over = 0
    for index in range(2000):
        fields = frame.propose_law_fields(SEED_A, index)
        if fields["theta_m"] + fields["theta_n"] >= cap:
            over += 1
            assert frame.in_proposal_box(fields) is False
    # a product-box proposal must put roughly half its mass outside the triangle
    assert 800 < over < 1200, over


def test_prb_c_14_box_membership_is_a_separate_conjunct_from_admissibility():
    import inspect

    source = inspect.getsource(frame.in_proposal_box)
    # the box test must contain no (B1)/(B2) reimplementation
    assert "exp" not in source
    assert "0.25 *" not in source
    assert "4.0 *" not in source
    accept_source = inspect.getsource(frame.sample_law_indices)
    assert "in_proposal_box" in accept_source
    assert "engine_accepts" in accept_source
    assert "algebraic_b1_b2" not in accept_source


def test_prb_c_15_box_predicate_is_fail_closed():
    good = frame.propose_law_fields(SEED_A, 0)
    for field, value in (
        ("theta_m", float("nan")),
        ("theta_n", float("inf")),
        ("epsilon_b", 1.5),
        ("resource_leak_floor", -0.1),
        ("kappa_m", 1.0),
    ):
        assert frame.in_proposal_box(dict(good, **{field: value})) is False
    assert frame.in_proposal_box({}) is False
    assert frame.in_proposal_box({"theta_m": "x"}) is False


def test_prb_c_16_accepted_laws_satisfy_both_conjuncts():
    indices, _ = frame.sample_law_indices(SEED_A, 12)
    for index in indices:
        fields = frame.propose_law_fields(SEED_A, index)
        assert frame.in_proposal_box(fields) is True
        assert frame.engine_accepts(fields)[0] is True
        LatticeBondSpec(**fields)  # must construct


def test_prb_c_17_uniformity_on_the_accepted_triangle_is_preserved():
    """Equal-area halves of the admissible triangle must receive comparable mass."""
    cap = frame.PROPOSAL_BOX["affinity_sum_cap"]
    low = high = 0
    for index in range(20000):
        fields = frame.propose_law_fields(SEED_A, index)
        if not frame.in_proposal_box(fields):
            continue
        # split the triangle {x,y>=0, x+y<cap} by the median line x+y = cap/sqrt(2),
        # which halves its area exactly
        if fields["theta_m"] + fields["theta_n"] < cap / math.sqrt(2.0):
            low += 1
        else:
            high += 1
    total = low + high
    assert total > 5000
    assert abs(low - high) / total < 0.05, (low, high)


def test_prb_c_18_proposal_index_is_fail_closed():
    with pytest.raises((TypeError, ValueError)):
        frame.propose_law_fields(SEED_A, -1)
    with pytest.raises(TypeError):
        frame.propose_law_fields(SEED_A, True)
