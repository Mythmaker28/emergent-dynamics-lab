import numpy as np

from edlab.entities.detection import detect_entities
from edlab.observables.continuity import material_retention
from edlab.observables.phenotype import phenotype_similarity
from edlab.specs import DetectionSpec, PhenotypeSpec, WorldSpec
from edlab.state import ParticleState
from edlab.validation.nulls import (
    static_motif_material_flux_null,
    sparse_lookalike_alias_null,
    tracker_cadence_sensitivity_null,
)


def test_material_retention_controlled_overlap() -> None:
    base = frozenset({1, 2})
    assert material_retention(base, frozenset({1, 2})) == 1.0
    assert material_retention(base, frozenset({2, 3})) == 1.0 / 3.0
    assert material_retention(base, frozenset({3, 4})) == 0.0


def test_same_ids_can_have_changed_phenotype() -> None:
    world = WorldSpec(n_particles=4, n_types=1, initial_speed=0.0)
    compact_positions = np.array([[0.48, 0.48], [0.52, 0.48], [0.48, 0.52], [0.52, 0.52]])
    expanded_positions = np.array([[0.40, 0.40], [0.60, 0.40], [0.40, 0.60], [0.60, 0.60]])
    common = dict(
        velocities=np.zeros((4, 2)), types=np.zeros(4, dtype=int), ids=np.arange(4)
    )
    compact = ParticleState(positions=compact_positions, **common)
    expanded = ParticleState(positions=expanded_positions, **common)
    detection = DetectionSpec(connection_radius=0.31, min_size=4)
    phenotype_spec = PhenotypeSpec(length_scale=0.1, speed_scale=0.2)
    first = detect_entities(
        compact,
        snapshot_step=0,
        time=0.0,
        world=world,
        detection=detection,
        phenotype_spec=phenotype_spec,
    )[0]
    second = detect_entities(
        expanded,
        snapshot_step=1,
        time=1.0,
        world=world,
        detection=detection,
        phenotype_spec=phenotype_spec,
    )[0]
    assert material_retention(first.particle_ids, second.particle_ids) == 1.0
    assert phenotype_similarity(first.phenotype, second.phenotype) < 1.0


def test_static_motif_with_material_flux_is_live_false_positive_null() -> None:
    result = static_motif_material_flux_null()
    assert result.passed
    assert result.phenotype_continuity == 1.0
    assert result.material_retention == 0.0


def test_tracker_cadence_sensitivity_null_survives_predeclared_grid() -> None:
    result = tracker_cadence_sensitivity_null()
    assert result.passed
    assert result.phenotype_continuity == 1.0
    assert result.material_retention == 0.0


def test_sparse_lookalike_alias_remains_explicit_unresolved_null() -> None:
    result = sparse_lookalike_alias_null()
    assert result.passed
    assert result.phenotype_continuity == 1.0
    assert result.material_retention == 0.0
    assert "unresolved" in result.detail
