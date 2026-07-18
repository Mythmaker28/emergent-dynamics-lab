"""Deterministic synthetic qualification of the passive Stage-B stack."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from edlab.substrates.lattice_bond import (
    DetectorSpec,
    LatticeBondEngine,
    LatticeBondSpec,
    LatticeBondState,
    RegimeThresholds,
    TrackMetrics,
    TrackObservation,
    TrackerSpec,
    WorldMetrics,
    advance_passive_tracer,
    assemble_world_metrics,
    classify_regime,
    component_diagnostics,
    detect_components,
    track_components,
)


SHAPE = (10, 12)
DETECTOR = DetectorSpec(matter_threshold=0.5, min_cells=1)
TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=4.0, dilation_radius=1)


def _mask(cells: set[tuple[int, int]], shape: tuple[int, int] = SHAPE) -> np.ndarray:
    value = np.zeros(shape, dtype=bool)
    for y, x in cells:
        value[y % shape[0], x % shape[1]] = True
    return value


def _state(mask: np.ndarray, frame: int, *, bonded: bool = False) -> LatticeBondState:
    m = np.where(mask, 0.8, 0.1).astype(np.float64)
    n = np.full(mask.shape, 0.8, dtype=np.float64)
    b = np.zeros((2, *mask.shape), dtype=np.float64)
    if bonded:
        for axis in (0, 1):
            b[axis] = np.where(mask & np.roll(mask, -1, axis=axis), 0.95, 0.0)
    return LatticeBondState(m, n, b, frame)


def _detected(*masks: np.ndarray):
    return tuple(detect_components(_state(mask, frame), DETECTOR, frame=frame) for frame, mask in enumerate(masks))


def _kinds(result) -> list[str]:
    return [event.kind for event in result.events]


def test_detector_is_instantaneous_matter_only_and_tracker_independent():
    mask = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
    ordinary = _state(mask, 0)
    altered = ordinary.copy()
    altered.n[:] = np.linspace(0.0, 1.0, altered.n.size).reshape(altered.shape)
    altered.b[:] = np.linspace(0.0, 1.0, altered.b.size).reshape(altered.face_shape)
    first = detect_components(ordinary, DETECTOR)
    second = detect_components(altered, DETECTOR)
    assert [(item.cells, item.area, item.centroid_y, item.centroid_x) for item in first] == [
        (item.cells, item.area, item.centroid_y, item.centroid_x) for item in second
    ]


def test_periodic_percolation_and_boundary_crossing_are_distinguished():
    crossing = _mask({(4, 11), (4, 0), (4, 1)})
    component = detect_components(_state(crossing, 0), DETECTOR)[0]
    assert not component.percolates
    assert component.radius_gyration < 1.0

    winding = _mask({(4, x) for x in range(SHAPE[1])})
    component = detect_components(_state(winding, 0), DETECTOR)[0]
    assert component.wraps_x
    assert not component.wraps_y


def test_stationary_component_keeps_one_track():
    square = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
    result = track_components(_detected(square, square, square), TRACKER)
    assert len(result.tracks) == 1
    assert len(result.tracks[0].points) == 3
    assert _kinds(result).count("CONTINUATION") == 2


def test_translating_component_keeps_one_track_across_periodic_boundary():
    masks = [
        _mask({(3, (x + shift) % SHAPE[1]) for x in (10, 11)} | {(4, (x + shift) % SHAPE[1]) for x in (10, 11)})
        for shift in (0, 1, 2)
    ]
    result = track_components(_detected(*masks), TRACKER)
    assert len(result.tracks) == 1
    assert len(result.tracks[0].points) == 3
    assert not result.tracks[0].unresolved


def test_deformation_does_not_switch_identity():
    square = _mask({(4, 4), (4, 5), (5, 4), (5, 5)})
    cross = _mask({(4, 4), (4, 5), (4, 6), (3, 5), (5, 5)})
    rectangle = _mask({(4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6)})
    result = track_components(_detected(square, cross, rectangle), TRACKER)
    assert len(result.tracks) == 1
    assert [point.component_index for point in result.tracks[0].points] == [0, 0, 0]


def test_split_is_explicit_and_children_reference_parent():
    joined = _mask({(4, x) for x in range(3, 8)})
    split = _mask({(4, 3), (4, 4), (4, 6), (4, 7)})
    result = track_components(_detected(joined, split), TRACKER)
    event = next(event for event in result.events if event.kind == "SPLIT")
    assert len(event.source_track_ids) == 1
    assert len(event.target_track_ids) == 2
    assert all(result.tracks[child].parent_track_ids == event.source_track_ids for child in event.target_track_ids)


def test_merge_is_explicit_and_child_references_all_parents():
    split = _mask({(4, 3), (4, 4), (4, 6), (4, 7)})
    joined = _mask({(4, x) for x in range(3, 8)})
    result = track_components(_detected(split, joined), TRACKER)
    event = next(event for event in result.events if event.kind == "MERGE")
    assert len(event.source_track_ids) == 2
    assert len(event.target_track_ids) == 1
    assert result.tracks[event.target_track_ids[0]].parent_track_ids == event.source_track_ids


def test_one_frame_contact_is_resolved_without_merge_or_split():
    separated = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)})
    contact = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 5), (4, 6), (5, 5), (5, 6)})
    result = track_components(_detected(separated, contact, separated), TRACKER)
    kinds = _kinds(result)
    assert "TEMPORARY_CONTACT" in kinds
    assert "MERGE" not in kinds
    assert "SPLIT" not in kinds
    assert len(result.tracks) == 2
    assert all(len(track.points) == 3 for track in result.tracks)


def test_detector_collapse_then_reseparation_is_unresolved_not_retrospective_contact():
    separated = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)})
    collapsed = separated.copy()
    collapsed[4, 4:7] = True
    result = track_components(_detected(separated, collapsed, separated), TRACKER)
    assert "TRACKING_UNRESOLVED" in _kinds(result)
    assert any(track.unresolved for track in result.tracks)
    assert "TEMPORARY_CONTACT" not in _kinds(result)


def test_appearance_and_dissolution_are_explicit():
    empty = np.zeros(SHAPE, dtype=bool)
    square = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
    result = track_components(_detected(empty, square, empty), TRACKER)
    assert _kinds(result).count("APPEARANCE") == 1
    assert _kinds(result).count("DISSOLUTION") == 1


def test_many_to_many_association_is_unresolved_not_forced():
    first = _mask({(2, x) for x in range(2, 9)} | {(6, x) for x in range(2, 9)})
    second = _mask({(y, 2) for y in range(2, 7)} | {(y, 8) for y in range(2, 7)})
    frames = _detected(first, second)
    assert [len(frame) for frame in frames] == [2, 2]
    # Each old horizontal component overlaps each new vertical component: the
    # association graph is genuinely many-to-many and must remain unresolved.
    permissive = TrackerSpec(max_centroid_displacement=5.0, max_area_ratio=10.0, dilation_radius=2)
    result = track_components(frames, permissive)
    assert "TRACKING_UNRESOLVED" in _kinds(result)
    assert "MERGE" not in _kinds(result)
    assert "SPLIT" not in _kinds(result)
    assert any(track.unresolved for track in result.tracks)


def test_symmetric_qualified_geometry_tie_is_unresolved_not_disappear_reappear():
    source = _mask({(4, 3), (4, 7)})
    target = _mask({(3, 5), (5, 5)})
    frames = _detected(source, target)
    tracker = TrackerSpec(max_centroid_displacement=5.0, max_area_ratio=3.0, dilation_radius=3)
    result = track_components(frames, tracker)
    edges = [edge for edge in result.edges if edge.qualified]
    assert len(edges) == 4
    assert max(edge.score for edge in edges) - min(edge.score for edge in edges) <= tracker.unique_score_margin
    assert not any(edge.selected for edge in edges)
    assert all(edge.selection_reason == "QUALIFIED_AMBIGUOUS_UNSELECTED" for edge in edges)
    assert "TRACKING_UNRESOLVED" in _kinds(result)
    assert not any(
        event.kind in {"DISSOLUTION", "APPEARANCE"} and event.frame == 1
        for event in result.events
    )
    assert all(track.unresolved for track in result.tracks)


def test_every_association_edge_records_selection_and_reason_for_raw_reproduction():
    source = _mask({(4, 4)})
    targets = _mask({(4, 4), (4, 6)})
    frames = _detected(source, targets)
    result = track_components(frames, TRACKER)
    assert len(result.edges) == 2
    selected = [edge for edge in result.edges if edge.selected]
    unselected = [edge for edge in result.edges if edge.qualified and not edge.selected]
    assert len(selected) == 1
    assert selected[0].selection_reason == "SELECTED_RAW_OVERLAP"
    assert len(unselected) == 1
    assert unselected[0].selection_reason == "QUALIFIED_NOT_SELECTED_LOWER_SCORE"


def test_passive_tracer_exactly_tracks_complete_replacement_and_recirculation():
    shape = (2, 2)
    matter = np.ones(shape, dtype=np.float64)
    tracer = np.zeros(shape, dtype=np.float64)
    tracer[0] = 1.0
    forward = np.zeros((2, *shape), dtype=np.float64)
    reverse = np.zeros_like(forward)
    forward[0, 0] = 1.0
    reverse[0, 0] = 1.0
    replaced = advance_passive_tracer(tracer, matter, forward, reverse, matter, 1.0)
    assert np.array_equal(replaced[0], np.zeros(2))
    assert np.array_equal(replaced[1], np.ones(2))
    assert float(np.sum(replaced)) == float(np.sum(tracer))

    returned = advance_passive_tracer(replaced, matter, reverse, forward, matter, 1.0)
    assert np.array_equal(returned, tracer)
    # Gross boundary flux alone would say two complete replacements; current
    # cohort retention correctly records complete return after recirculation.


def test_passive_tracer_matches_actual_engine_transport_and_never_exceeds_matter():
    mask = _mask({(4, 4), (4, 5), (5, 4), (5, 5)})
    state = _state(mask, 0)
    engine = LatticeBondEngine()
    tracer = np.where(mask, state.m, 0.0).astype(np.float64)
    before_total = float(np.sum(tracer))
    for _ in range(20):
        result = engine.step(state)
        tracer = advance_passive_tracer(
            tracer,
            state.m,
            result.ledger.matter_forward,
            result.ledger.matter_reverse,
            result.state.m,
            engine.spec.dt,
        )
        state = result.state
    assert float(np.min(tracer)) >= -1e-12
    assert float(np.max(tracer - state.m)) <= 1e-12
    assert float(np.sum(tracer)) == pytest.approx(before_total, abs=1e-12)


def test_passive_tracer_rejects_nonfinite_flows_dt_and_inconsistent_matter():
    matter = np.ones((2, 2), dtype=np.float64)
    tracer = np.full((2, 2), 0.5, dtype=np.float64)
    forward = np.zeros((2, 2, 2), dtype=np.float64)
    reverse = np.zeros_like(forward)
    bad = forward.copy()
    bad[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="matter_forward"):
        advance_passive_tracer(tracer, matter, bad, reverse, matter, 0.1)
    with pytest.raises(ValueError, match="dt"):
        advance_passive_tracer(tracer, matter, forward, reverse, matter, float("nan"))
    inconsistent = matter.copy()
    inconsistent[0, 0] = 0.9
    with pytest.raises(ValueError, match="inconsistent"):
        advance_passive_tracer(tracer, matter, forward, reverse, inconsistent, 0.1)
    with pytest.raises(ValueError, match="same shape"):
        advance_passive_tracer(tracer, matter, forward, reverse, matter[:1], 0.1)


@pytest.mark.parametrize("margin", [float("nan"), float("inf"), float("-inf")])
def test_tracker_rejects_nonfinite_unique_score_margin(margin):
    with pytest.raises(ValueError, match="finite"):
        TrackerSpec(unique_score_margin=margin)


def test_logged_and_unlogged_physics_and_ledgers_are_byte_identical():
    mask = _mask({(4, 4), (4, 5), (5, 4), (5, 5)})
    initial = _state(mask, 0, bonded=True)
    engine = LatticeBondEngine()

    def run(logged: bool):
        state = initial.copy()
        result_bytes: list[bytes] = []
        tracer = np.where(mask, state.m, 0.0).astype(np.float64)
        for frame in range(12):
            result = engine.step(state)
            result_bytes.append(result.canonical_bytes())
            if logged:
                components = detect_components(state, DETECTOR, frame=frame)
                for component in components:
                    component_diagnostics(component, state, result.ledger, engine.spec)
                tracer = advance_passive_tracer(
                    tracer,
                    state.m,
                    result.ledger.matter_forward,
                    result.ledger.matter_reverse,
                    result.state.m,
                    engine.spec.dt,
                )
            state = result.state
        return state.canonical_bytes(), b"".join(result_bytes)

    assert run(False) == run(True)


def test_activity_energy_geometry_and_leakage_are_raw_and_passive():
    mask = _mask({(4, 4), (4, 5), (5, 4), (5, 5)})
    state = _state(mask, 0, bonded=True)
    engine = LatticeBondEngine()
    before = state.canonical_bytes()
    result = engine.step(state)
    ledger_before = result.ledger.canonical_bytes()
    component = detect_components(state, DETECTOR)[0]
    diagnostics = component_diagnostics(component, state, result.ledger, engine.spec)
    assert diagnostics.matter_internal_gross >= 0.0
    assert diagnostics.matter_boundary_gross >= 0.0
    assert diagnostics.resource_boundary_exchange >= 0.0
    assert diagnostics.bond_work_throughput > 0.0
    assert diagnostics.mean_internal_bond == pytest.approx(0.95)
    assert state.canonical_bytes() == before
    assert result.ledger.canonical_bytes() == ledger_before


def _track(
    *,
    persistence: int = 20,
    bounded: float = 1.0,
    percolated: float = 0.0,
    activity: float = 0.02,
    energy: float = 0.01,
    turnover: float = 0.8,
    post: int = 5,
    unresolved: bool = False,
    maximum_area: float = 0.1,
) -> TrackMetrics:
    return TrackMetrics(
        track_id=0,
        observed_frames=persistence,
        span_frames=persistence,
        maximum_area_fraction=maximum_area,
        bounded_fraction=bounded,
        percolated_fraction=percolated,
        mean_activity_per_mass=activity,
        mean_energy_throughput_per_mass=energy,
        maximum_turnover_fraction=turnover,
        post_turnover_frames=post,
        unresolved=unresolved,
    )


THRESHOLDS = RegimeThresholds(
    min_persistence_frames=12,
    max_area_fraction=0.25,
    min_bounded_fraction=0.9,
    min_activity_per_mass=0.01,
    min_energy_throughput_per_mass=0.005,
    min_turnover_fraction=0.6,
    min_post_turnover_frames=4,
)


@pytest.mark.parametrize(
    ("metrics", "expected"),
    [
        (WorldMetrics(False, 0, False, False, False, False, ()), "EMPTY_OR_GAS"),
        (WorldMetrics(True, 0, False, False, False, False, ()), "DISSOLVED"),
        (WorldMetrics(True, 1, True, False, False, False, ()), "PERCOLATED"),
        (WorldMetrics(True, 1, True, True, False, False, ()), "ACTIVE_UNBOUNDED"),
        (WorldMetrics(True, 1, False, False, False, True, (_track(unresolved=True),)), "TRACKING_UNRESOLVED"),
        (WorldMetrics(True, 1, False, False, False, False, (_track(activity=0.0, energy=0.0, turnover=0.0),)), "STATIC_CRYSTAL_OR_SHELL"),
        (WorldMetrics(True, 1, False, False, False, False, (_track(turnover=0.1),)), "PERSISTENT_NO_TURNOVER"),
        (WorldMetrics(True, 1, False, False, True, False, (_track(persistence=4),)), "TURNOVER_WITHOUT_PERSISTENCE"),
        (WorldMetrics(True, 1, False, False, False, False, (_track(),)), "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"),
    ],
)
def test_regime_classifier_is_total_deterministic_and_precedence_frozen(metrics, expected):
    assert classify_regime(metrics, THRESHOLDS) == expected


def test_raw_to_metrics_assembler_enforces_area_chronology_and_missing_data():
    square = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
    frames = _detected(*([square] * 12))
    tracking = track_components(frames, TRACKER)
    assert len(tracking.tracks) == 1
    track_id = tracking.tracks[0].track_id
    observations = tuple(
        TrackObservation(
            track_id,
            frame,
            0,
            4 / (SHAPE[0] * SHAPE[1]),
            False,
            0.02,
            0.01,
            0.8 if frame >= 7 else 0.05 * frame,
        )
        for frame in range(12)
    )
    metrics = assemble_world_metrics(frames, tracking, observations, THRESHOLDS)
    assert classify_regime(metrics, THRESHOLDS) == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    assert metrics.tracks[0].post_turnover_frames == 4

    oversized = tuple(replace(item, area_fraction=0.4) for item in observations)
    oversized_metrics = assemble_world_metrics(frames, tracking, oversized, THRESHOLDS)
    assert "AREA_EXCEEDS_MAX" in oversized_metrics.tracks[0].reason_codes
    assert classify_regime(oversized_metrics, THRESHOLDS) != "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"

    missing_metrics = assemble_world_metrics(frames, tracking, observations[:-1], THRESHOLDS)
    assert missing_metrics.tracking_unresolved
    assert classify_regime(missing_metrics, THRESHOLDS) == "TRACKING_UNRESOLVED"

    nonfinite = list(observations)
    nonfinite[4] = replace(nonfinite[4], activity_per_mass=float("nan"))
    nonfinite_metrics = assemble_world_metrics(frames, tracking, tuple(nonfinite), THRESHOLDS)
    assert nonfinite_metrics.tracking_unresolved
    assert classify_regime(nonfinite_metrics, THRESHOLDS) == "TRACKING_UNRESOLVED"

    invalid = list(observations)
    invalid[4] = replace(invalid[4], area_fraction=-0.1)
    invalid_metrics = assemble_world_metrics(frames, tracking, tuple(invalid), THRESHOLDS)
    assert invalid_metrics.tracking_unresolved
    assert "INVALID_AREA_FRACTION" in invalid_metrics.tracks[0].reason_codes
    assert classify_regime(invalid_metrics, THRESHOLDS) == "TRACKING_UNRESOLVED"

    orphan = observations + (replace(observations[0], track_id=track_id + 99),)
    orphan_metrics = assemble_world_metrics(frames, tracking, orphan, THRESHOLDS)
    assert orphan_metrics.tracking_unresolved
    assert "ORPHAN_TRACK_OBSERVATION" in orphan_metrics.reason_codes
    assert classify_regime(orphan_metrics, THRESHOLDS) == "TRACKING_UNRESOLVED"


def test_raw_to_metrics_assembler_does_not_trust_claimed_detector_geometry():
    winding = _mask({(3, x) for x in range(SHAPE[1])})
    frames = _detected(*([winding] * 12))
    assert frames[0][0].percolates
    tracking = track_components(frames, TRACKER)
    track_id = tracking.tracks[0].track_id
    observations = tuple(
        TrackObservation(
            track_id,
            frame,
            0,
            frames[frame][0].area / (SHAPE[0] * SHAPE[1]),
            False,
            0.02,
            0.01,
            0.8 if frame >= 7 else 0.05 * frame,
        )
        for frame in range(12)
    )
    metrics = assemble_world_metrics(frames, tracking, observations, THRESHOLDS)
    assert metrics.tracking_unresolved
    assert "PERCOLATION_GEOMETRY_MISMATCH" in metrics.tracks[0].reason_codes
    assert classify_regime(metrics, THRESHOLDS) == "TRACKING_UNRESOLVED"


def test_static_bonded_shell_and_active_unbounded_wave_do_not_become_individuality_claims():
    shell = _mask({(3, x) for x in range(3, 8)} | {(7, x) for x in range(3, 8)} | {(y, 3) for y in range(4, 7)} | {(y, 7) for y in range(4, 7)})
    frozen_engine = LatticeBondEngine(
        LatticeBondSpec(kappa_m=0.0, resource_diffusivity=0.0, k_on=0.0, k_off=0.0, k_tension=0.0)
    )
    state = _state(shell, 0, bonded=True)
    result = frozen_engine.step(state)
    component = detect_components(state, DETECTOR)[0]
    diagnostics = component_diagnostics(component, state, result.ledger, frozen_engine.spec)
    assert diagnostics.matter_internal_gross == 0.0
    assert diagnostics.bond_work_throughput == 0.0
    static_metrics = WorldMetrics(True, 1, False, False, False, False, (_track(activity=0.0, energy=0.0, turnover=0.0),))
    assert classify_regime(static_metrics, THRESHOLDS) == "STATIC_CRYSTAL_OR_SHELL"

    wave = _mask({(4, x) for x in range(SHAPE[1])})
    assert detect_components(_state(wave, 0), DETECTOR)[0].percolates
    active_metrics = WorldMetrics(True, 1, True, True, False, False, ())
    assert classify_regime(active_metrics, THRESHOLDS) == "ACTIVE_UNBOUNDED"


def test_complete_material_replacement_with_structural_persistence_is_not_identity():
    shape = (7, 7)
    m = np.full(shape, 0.1, dtype=np.float64)
    centre = (3, 3)
    m[centre] = 0.8
    for neighbour in ((2, 3), (4, 3), (3, 2), (3, 4)):
        m[neighbour] = 0.2
    n = np.full(shape, 0.8, dtype=np.float64)
    b = np.zeros((2, *shape), dtype=np.float64)
    b[:, centre[0], centre[1]] = 0.9
    states = tuple(LatticeBondState(m.copy(), n.copy(), b.copy(), frame) for frame in range(3))
    detector = DetectorSpec(matter_threshold=0.5, min_cells=1)
    frames = tuple(detect_components(state, detector, frame=frame) for frame, state in enumerate(states))
    tracking = track_components(frames, TRACKER)
    assert len(tracking.tracks) == 1 and len(tracking.tracks[0].points) == 3

    original = np.zeros(shape, dtype=np.float64)
    original[centre] = m[centre]
    forward = np.zeros((2, *shape), dtype=np.float64)
    reverse = np.zeros_like(forward)
    forward[0, 3, 3] = reverse[0, 3, 3] = 0.2
    forward[0, 2, 3] = reverse[0, 2, 3] = 0.2
    forward[1, 3, 3] = reverse[1, 3, 3] = 0.2
    forward[1, 3, 2] = reverse[1, 3, 2] = 0.2
    replaced = advance_passive_tracer(original, m, forward, reverse, m, 1.0)
    support = frames[1][0].mask()
    retention = float(np.sum(replaced[support]) / np.sum(original[support]))
    assert retention == 0.0
    returned = advance_passive_tracer(replaced, m, reverse, forward, m, 1.0)
    assert np.array_equal(returned, original)
    # The fixture proves the measurement stack can represent this conjunction;
    # it intentionally makes no identity, memory, or autonomy inference.


def test_tracker_spec_changes_do_not_change_detector_or_physics():
    square = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
    state = _state(square, 0)
    engine = LatticeBondEngine()
    physical = engine.step(state).canonical_bytes()
    components = detect_components(state, DETECTOR)
    track_components((components, components), TRACKER)
    track_components((components, components), replace(TRACKER, max_centroid_displacement=6.0))
    assert engine.step(state).canonical_bytes() == physical
    assert detect_components(state, DETECTOR) == components
