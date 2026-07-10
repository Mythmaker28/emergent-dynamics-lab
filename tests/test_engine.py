import numpy as np
import pytest

from edlab.specs import LawSpec, RunSpec, WorldSpec
from edlab.state import ParticleState
from edlab.substrates.particle_dynamics.engine import (
    forces_reference,
    forces_vectorized,
    initialize_world,
    simulate,
    step,
)
from edlab.validation.forces import validate_force_paths


def test_force_paths_agree_on_32_controlled_worlds() -> None:
    result = validate_force_paths(fixtures=32)
    assert result.passed
    assert result.max_scaled_error <= 1.0
    assert result.max_one_step_scaled_error <= 1.0


def test_asymmetric_matrix_direction_is_receiver_source_ordered() -> None:
    state = ParticleState(
        positions=np.array([[0.40, 0.50], [0.50, 0.50]]),
        velocities=np.zeros((2, 2)),
        types=np.array([0, 1]),
        ids=np.array([10, 20]),
    )
    law = LawSpec(
        interaction=np.array([[0.0, 1.0], [-0.5, 0.0]]),
        short_range=0.02,
        interaction_range=0.2,
    )
    force = forces_reference(state, law, 1.0)
    assert force[0, 0] > 0.0
    assert force[1, 0] > 0.0
    np.testing.assert_allclose(force[:, 1], 0.0, atol=1e-15)


def test_periodic_seam_matches_equivalent_interior_pair() -> None:
    law = LawSpec(np.ones((1, 1)), short_range=0.005, interaction_range=0.2)
    seam = ParticleState(
        np.array([[0.99, 0.5], [0.01, 0.5]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    interior = ParticleState(
        np.array([[0.49, 0.5], [0.51, 0.5]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    np.testing.assert_allclose(
        forces_reference(seam, law, 1.0),
        forces_reference(interior, law, 1.0),
        atol=1e-13,
    )


def test_cutoff_zero_distance_and_empty_states_are_finite() -> None:
    law = LawSpec(np.ones((1, 1)), short_range=0.02, interaction_range=0.2)
    cutoff = ParticleState(
        np.array([[0.2, 0.2], [0.4, 0.2]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    coincident = ParticleState(
        np.array([[0.2, 0.2], [0.2, 0.2]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    empty = ParticleState(
        np.empty((0, 2)), np.empty((0, 2)), np.empty(0, dtype=int), np.empty(0, dtype=int)
    )
    for backend in (forces_reference, forces_vectorized):
        np.testing.assert_allclose(backend(cutoff, law, 1.0), 0.0, atol=1e-15)
        assert np.isfinite(backend(coincident, law, 1.0)).all()
        assert backend(empty, law, 1.0).shape == (0, 2)


def test_vectorized_distance_does_not_underflow_for_subnormal_separation() -> None:
    law = LawSpec(np.ones((1, 1)))
    state = ParticleState(
        np.array([[0.0, 0.0], [1e-162, 0.0]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    reference = forces_reference(state, law, 1.0)
    vectorized = forces_vectorized(state, law, 1.0)
    assert np.linalg.norm(reference) > 0
    np.testing.assert_allclose(vectorized, reference, atol=1e-12, rtol=1e-10)


def test_non_unique_half_box_interaction_domain_is_rejected() -> None:
    state = ParticleState(
        np.array([[0.0, 0.0], [0.5, 0.0]]),
        np.zeros((2, 2)),
        np.zeros(2, dtype=int),
        np.arange(2),
    )
    law = LawSpec(np.ones((1, 1)), interaction_range=0.5)
    for backend in (forces_reference, forces_vectorized):
        with pytest.raises(ValueError, match="box_size/2"):
            backend(state, law, 1.0)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_spec_values_are_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        LawSpec(np.ones((1, 1)), damping=value)
    with pytest.raises(ValueError, match="finite"):
        WorldSpec(n_particles=2, n_types=1, box_size=value)
    with pytest.raises(ValueError, match="finite"):
        RunSpec(seed=1, dt=value)


def test_determinism_and_diagnostic_id_permutation() -> None:
    world = WorldSpec(n_particles=20, n_types=3)
    law = LawSpec(
        np.array([[0.2, -0.3, 0.8], [0.1, 0.5, -0.7], [-0.4, 0.9, 0.0]])
    )
    initial = initialize_world(world, seed=123)
    permuted = ParticleState(
        initial.positions.copy(),
        initial.velocities.copy(),
        initial.types.copy(),
        initial.ids[::-1].copy(),
    )
    run = RunSpec(seed=123, steps=25, snapshot_interval=5)
    left = simulate(initial, law, world, run)
    repeated = simulate(initial, law, world, run)
    right = simulate(permuted, law, world, run)
    for a, b, c in zip(left, repeated, right, strict=True):
        np.testing.assert_array_equal(a.state.positions, b.state.positions)
        np.testing.assert_array_equal(a.state.velocities, b.state.velocities)
        np.testing.assert_allclose(a.state.positions, c.state.positions, atol=0.0)
        np.testing.assert_allclose(a.state.velocities, c.state.velocities, atol=0.0)


def test_step_retains_ids_without_reading_them() -> None:
    world = WorldSpec(n_particles=4, n_types=1)
    law = LawSpec(np.array([[0.5]]))
    state = initialize_world(world, 7)
    result = step(state, law, world, 0.02)
    np.testing.assert_array_equal(result.ids, state.ids)


def test_particle_storage_order_permutation_preserves_physics() -> None:
    world = WorldSpec(n_particles=12, n_types=2)
    law = LawSpec(np.array([[0.7, -0.2], [0.4, -0.5]]))
    original = initialize_world(world, 999)
    permutation = np.array([7, 2, 10, 0, 5, 11, 1, 9, 4, 8, 6, 3])
    permuted = ParticleState(
        original.positions[permutation],
        original.velocities[permutation],
        original.types[permutation],
        original.ids[permutation],
    )
    for _ in range(15):
        original = step(original, law, world, 0.02)
        permuted = step(permuted, law, world, 0.02)
    inverse = np.argsort(permutation)
    np.testing.assert_allclose(original.positions, permuted.positions[inverse], atol=2e-15)
    np.testing.assert_allclose(original.velocities, permuted.velocities[inverse], atol=2e-15)


def test_snapshot_schedule_is_observer_only_at_common_times() -> None:
    world = WorldSpec(n_particles=10, n_types=2)
    law = LawSpec(np.array([[0.2, -0.8], [0.6, 0.1]]))
    initial = initialize_world(world, 321)
    by_cadence = {}
    for cadence in (10, 30, 60):
        snapshots = simulate(
            initial,
            law,
            world,
            RunSpec(seed=321, steps=120, snapshot_interval=cadence),
        )
        by_cadence[cadence] = {snapshot.step: snapshot.state for snapshot in snapshots}
    for step_index in (0, 60, 120):
        reference = by_cadence[10][step_index]
        for cadence in (30, 60):
            np.testing.assert_array_equal(reference.positions, by_cadence[cadence][step_index].positions)
            np.testing.assert_array_equal(reference.velocities, by_cadence[cadence][step_index].velocities)
