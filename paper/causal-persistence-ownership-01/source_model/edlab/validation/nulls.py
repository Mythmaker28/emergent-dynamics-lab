"""Required null models that remain executable throughout the project."""

from __future__ import annotations

from dataclasses import dataclass
import json

import numpy as np

from ..entities.detection import EntityObservation, detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import material_retention
from ..observables.phenotype import Phenotype, phenotype_similarity
from ..specs import DetectionSpec, LawSpec, PhenotypeSpec, TrackerSpec, WorldSpec
from ..state import ParticleState
from ..substrates.particle_dynamics.engine import step


@dataclass(frozen=True)
class NullResult:
    name: str
    passed: bool
    phenotype_continuity: float | None
    material_retention: float | None
    detail: str


def id_permutation_null(*, steps: int = 20) -> NullResult:
    """Permuting diagnostic IDs must not change physical dynamics."""

    world = WorldSpec(n_particles=12, n_types=2, initial_speed=0.03)
    law = LawSpec(np.array([[0.8, -0.4], [0.25, 0.6]], dtype=float))
    rng = np.random.default_rng(1234)
    positions = rng.uniform(0.0, world.box_size, size=(world.n_particles, 2))
    velocities = rng.normal(0.0, world.initial_speed, size=(world.n_particles, 2))
    types = rng.integers(0, world.n_types, size=world.n_particles)
    ids = np.arange(world.n_particles)
    left = ParticleState(positions.copy(), velocities.copy(), types.copy(), ids.copy())
    right = ParticleState(positions.copy(), velocities.copy(), types.copy(), ids[::-1].copy())
    for _ in range(steps):
        left = step(left, law, world, 0.02, backend="vectorized")
        right = step(right, law, world, 0.02, backend="vectorized")
    error = max(
        float(np.max(np.abs(left.positions - right.positions))),
        float(np.max(np.abs(left.velocities - right.velocities))),
    )
    return NullResult(
        name="ID_PERMUTATION",
        passed=error <= 1e-14,
        phenotype_continuity=None,
        material_retention=None,
        detail=f"maximum physical-array difference after {steps} steps: {error:.6g}",
    )


def static_motif_material_flux_null() -> NullResult:
    """Known false positive: same morphology with completely fresh IDs."""

    world = WorldSpec(n_particles=8, n_types=2, initial_speed=0.0)
    positions = np.array(
        [
            [0.46, 0.46],
            [0.50, 0.46],
            [0.54, 0.46],
            [0.46, 0.50],
            [0.54, 0.50],
            [0.46, 0.54],
            [0.50, 0.54],
            [0.54, 0.54],
        ]
    )
    velocities = np.zeros_like(positions)
    types = np.array([0, 1, 0, 1, 1, 0, 1, 0])
    before = ParticleState(positions, velocities, types, np.arange(8))
    after = ParticleState(positions.copy(), velocities.copy(), types.copy(), np.arange(100, 108))
    detection = DetectionSpec(connection_radius=0.061, min_size=4)
    phenotype_spec = PhenotypeSpec(length_scale=0.061, speed_scale=0.25)
    first = detect_entities(
        before,
        snapshot_step=0,
        time=0.0,
        world=world,
        detection=detection,
        phenotype_spec=phenotype_spec,
    )
    second = detect_entities(
        after,
        snapshot_step=1,
        time=1.0,
        world=world,
        detection=detection,
        phenotype_spec=phenotype_spec,
    )
    if len(first) != 1 or len(second) != 1:
        return NullResult(
            "STATIC_MOTIF_WITH_MATERIAL_FLUX",
            False,
            None,
            None,
            f"detector returned {len(first)} and {len(second)} entities",
        )
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.1, min_size_ratio=0.5),
        box_size=world.box_size,
    )
    first_tracked = tracker.update(first)
    second_tracked = tracker.update(second)
    p_value = phenotype_similarity(first[0].phenotype, second[0].phenotype)
    m_value = material_retention(first[0].particle_ids, second[0].particle_ids)
    same_lineage = first_tracked[0].track_id == second_tracked[0].track_id
    passed = same_lineage and p_value > 0.8 and m_value == 0.0
    return NullResult(
        name="STATIC_MOTIF_WITH_MATERIAL_FLUX",
        passed=passed,
        phenotype_continuity=p_value,
        material_retention=m_value,
        detail=(
            f"same_lineage={same_lineage}; this is an expected probe-positive null, "
            "not evidence of dynamical individuality"
        ),
    )


def tracker_cadence_sensitivity_null() -> NullResult:
    """Known physical continuation must survive cadences and a frozen gate grid."""

    base_steps = tuple(range(0, 121, 10))

    def observation(step: int, local_index: int = 0) -> EntityObservation:
        count = 6
        phenotype = Phenotype(
            ("fixture_geometry", "fixture_speed"),
            np.array([0.4, 0.1]),
            {"fixture_geometry": 0.4, "fixture_speed": 0.1},
        )
        return EntityObservation(
            local_index=local_index,
            snapshot_step=step,
            time=step * 0.02,
            particle_indices=tuple(range(count)),
            particle_ids=frozenset(range(10_000 + step * 10, 10_000 + step * 10 + count)),
            centroid=np.array([(0.40 + 0.001 * step) % 1.0, 0.5]),
            phenotype=phenotype,
        )

    cells: dict[str, dict[str, float | int | bool]] = {}
    passed = True
    endpoint_p = 1.0
    endpoint_m = 0.0
    for cadence in (10, 30, 60):
        selected_steps = [step for step in base_steps if step % cadence == 0]
        for distance_scale in (0.8, 1.0, 1.2):
            for size_ratio in (0.2, 0.25, 0.3):
                tracker = LineageTracker(
                    TrackerSpec(
                        max_centroid_distance=0.16 * distance_scale,
                        min_size_ratio=size_ratio,
                    ),
                    box_size=1.0,
                )
                tracked = []
                for step in selected_steps:
                    tracked.extend(
                        tracker.update(
                            [observation(step)],
                            snapshot_step=step,
                            time=step * 0.02,
                        )
                    )
                track_ids = {item.track_id for item in tracked}
                cell_passed = len(track_ids) == 1 and len(tracker.tracks) == 1
                passed = passed and cell_passed
                first = tracked[0].entity
                last = tracked[-1].entity
                p_value = phenotype_similarity(first.phenotype, last.phenotype)
                m_value = material_retention(first.particle_ids, last.particle_ids)
                endpoint_p = min(endpoint_p, p_value)
                endpoint_m = max(endpoint_m, m_value)
                cells[
                    f"cadence={cadence},distance_scale={distance_scale},size_ratio={size_ratio}"
                ] = {
                    "passed": cell_passed,
                    "tracks": len(track_ids),
                    "endpoint_p": p_value,
                    "endpoint_m": m_value,
                }
    detector_world = WorldSpec(n_particles=6, n_types=1, initial_speed=0.0)
    detector_positions = np.array(
        [
            [0.47, 0.48],
            [0.50, 0.48],
            [0.53, 0.48],
            [0.47, 0.52],
            [0.50, 0.52],
            [0.53, 0.52],
        ]
    )
    detector_state = ParticleState(
        detector_positions,
        np.zeros_like(detector_positions),
        np.zeros(6, dtype=int),
        np.arange(6),
    )
    for radius_scale in (0.8, 1.0, 1.2):
        for min_size in (3, 4, 5):
            detected = detect_entities(
                detector_state,
                snapshot_step=0,
                time=0.0,
                world=detector_world,
                detection=DetectionSpec(
                    connection_radius=0.06 * radius_scale,
                    min_size=min_size,
                ),
                phenotype_spec=PhenotypeSpec(length_scale=0.06, speed_scale=0.25),
            )
            cell_passed = len(detected) == 1 and len(detected[0].particle_ids) == 6
            passed = passed and cell_passed
            cells[
                f"detector_radius_scale={radius_scale},detector_min_size={min_size}"
            ] = {
                "passed": cell_passed,
                "entities": len(detected),
            }
    return NullResult(
        name="TRACKER_CADENCE_SENSITIVITY",
        passed=passed,
        phenotype_continuity=endpoint_p,
        material_retention=endpoint_m,
        detail=json.dumps(cells, sort_keys=True),
    )


def sparse_lookalike_alias_null() -> NullResult:
    """Expose an observational alias that P/M and sparse occupancy tracking cannot resolve.

    Two identical occupancies exchange complete material sets between snapshots.
    Geometry/size association remains at each location, so the tracker produces
    high-P/low-M continuity without a competing edge. Passing this null means
    the limitation remains visible; it is never evidence for individuality.
    """

    phenotype = Phenotype(
        ("fixture_geometry", "fixture_speed"),
        np.array([0.4, 0.0]),
        {"fixture_geometry": 0.4, "fixture_speed": 0.0},
    )

    def entity(local_index: int, step: int, x: float, ids: range) -> EntityObservation:
        return EntityObservation(
            local_index=local_index,
            snapshot_step=step,
            time=float(step),
            particle_indices=tuple(range(6)),
            particle_ids=frozenset(ids),
            centroid=np.array([x, 0.5]),
            phenotype=phenotype,
        )

    left_ids = range(0, 6)
    right_ids = range(100, 106)
    first = [entity(0, 0, 0.35, left_ids), entity(1, 0, 0.65, right_ids)]
    second = [entity(0, 1, 0.35, right_ids), entity(1, 1, 0.65, left_ids)]
    tracker = LineageTracker(
        TrackerSpec(max_centroid_distance=0.12, min_size_ratio=0.5), box_size=1.0
    )
    first_tracked = tracker.update(first)
    second_tracked = tracker.update(second)
    p_values = [
        phenotype_similarity(first[index].phenotype, second[index].phenotype)
        for index in range(2)
    ]
    m_values = [
        material_retention(first[index].particle_ids, second[index].particle_ids)
        for index in range(2)
    ]
    same_location_tracks = all(
        first_tracked[index].track_id == second_tracked[index].track_id
        for index in range(2)
    )
    ambiguity_logged = any(
        event.kind == "ambiguous_association" for event in tracker.events
    )
    passed = (
        same_location_tracks
        and all(value == 1.0 for value in p_values)
        and all(value == 0.0 for value in m_values)
        and not ambiguity_logged
    )
    return NullResult(
        name="SPARSE_LOOKALIKE_ALIAS",
        passed=passed,
        phenotype_continuity=min(p_values),
        material_retention=max(m_values),
        detail=(
            "expected unresolved observational alias: occupancy tracks persist with P=1/M=0 "
            "and no competing spatial edge; hold-out cannot by itself reject this null"
        ),
    )
