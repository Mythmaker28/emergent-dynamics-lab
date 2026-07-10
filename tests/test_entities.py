import numpy as np

from edlab.entities.detection import detect_entities
from edlab.entities.detection import connected_components_periodic
from edlab.observables.phenotype import phenotype_similarity
from edlab.specs import DetectionSpec, PhenotypeSpec, WorldSpec
from edlab.state import ParticleState


def _detect(state: ParticleState, world: WorldSpec):
    return detect_entities(
        state,
        snapshot_step=0,
        time=0.0,
        world=world,
        detection=DetectionSpec(connection_radius=0.065, min_size=4),
        phenotype_spec=PhenotypeSpec(length_scale=0.065, speed_scale=0.2),
    )


def test_periodic_seam_detector_matches_translated_interior_and_ids() -> None:
    world = WorldSpec(n_particles=4, n_types=2, initial_speed=0.0)
    seam_positions = np.array([[0.98, 0.48], [0.02, 0.48], [0.98, 0.52], [0.02, 0.52]])
    velocities = np.array([[0.1, 0.0], [0.1, 0.0], [0.1, 0.0], [0.1, 0.0]])
    types = np.array([0, 1, 0, 1])
    seam = ParticleState(seam_positions, velocities, types, np.arange(4))
    translated = ParticleState(
        (seam_positions + np.array([0.25, 0.0])) % 1.0,
        velocities.copy(),
        types.copy(),
        np.array([400, 300, 200, 100]),
    )
    left = _detect(seam, world)
    right = _detect(translated, world)
    assert len(left) == len(right) == 1
    assert phenotype_similarity(left[0].phenotype, right[0].phenotype) == 1.0


def test_particle_order_and_id_labels_do_not_change_phenotype() -> None:
    world = WorldSpec(n_particles=5, n_types=2, initial_speed=0.0)
    positions = np.array(
        [[0.48, 0.48], [0.50, 0.48], [0.52, 0.48], [0.49, 0.52], [0.51, 0.52]]
    )
    velocities = np.array([[0.1, 0.0], [0.0, 0.1], [-0.1, 0.0], [0.0, -0.1], [0.0, 0.0]])
    types = np.array([0, 1, 0, 1, 0])
    original = ParticleState(positions, velocities, types, np.arange(5))
    order = np.array([4, 2, 0, 3, 1])
    reordered = ParticleState(
        positions[order], velocities[order], types[order], np.array([90, 91, 92, 93, 94])
    )
    left = _detect(original, world)[0]
    right = _detect(reordered, world)[0]
    np.testing.assert_allclose(left.phenotype.vector, right.phenotype.vector, atol=1e-14)


def test_detector_threshold_is_inclusive_and_bridge_chain_is_explicit() -> None:
    positions = np.array([[0.10, 0.5], [0.20, 0.5], [0.30, 0.5]])
    components = connected_components_periodic(positions, 1.0, 0.1)
    assert components == [(0, 1, 2)]
    separated = connected_components_periodic(
        np.array([[0.10, 0.5], [0.2000001, 0.5]]), 1.0, 0.1
    )
    assert separated == [(0,), (1,)]
