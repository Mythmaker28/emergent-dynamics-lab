"""Independent force-path comparison on controlled random worlds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..specs import LawSpec, WorldSpec
from ..substrates.particle_dynamics.engine import forces_reference, forces_vectorized, initialize_world


@dataclass(frozen=True)
class ForceValidationResult:
    fixtures: int
    max_absolute_error: float
    max_scaled_error: float
    absolute_tolerance: float
    relative_tolerance: float
    passed: bool


def validate_force_paths(
    *,
    fixtures: int = 32,
    absolute_tolerance: float = 1e-12,
    relative_tolerance: float = 1e-10,
) -> ForceValidationResult:
    max_absolute_error = 0.0
    max_scaled_error = 0.0
    passed = True
    for fixture in range(fixtures):
        rng = np.random.default_rng(10_000 + fixture)
        n_types = 1 + fixture % 4
        world = WorldSpec(
            n_particles=2 + fixture % 15,
            n_types=n_types,
            box_size=0.7 + 0.03 * (fixture % 7),
            initial_speed=0.03,
        )
        law = LawSpec(
            interaction=rng.uniform(-1.0, 1.0, size=(n_types, n_types)),
            repulsion_strength=float(rng.uniform(0.5, 2.5)),
            short_range=float(rng.uniform(0.015, 0.04)),
            interaction_range=float(rng.uniform(0.12, 0.24)),
            damping=float(rng.uniform(0.1, 1.5)),
        )
        state = initialize_world(world, 20_000 + fixture)
        reference = forces_reference(state, law, world.box_size)
        vectorized = forces_vectorized(state, law, world.box_size)
        absolute = np.abs(reference - vectorized)
        tolerance = absolute_tolerance + relative_tolerance * np.abs(reference)
        scaled = np.divide(absolute, tolerance, out=np.zeros_like(absolute), where=tolerance > 0)
        max_absolute_error = max(max_absolute_error, float(absolute.max(initial=0.0)))
        max_scaled_error = max(max_scaled_error, float(scaled.max(initial=0.0)))
        passed = passed and bool(np.all(absolute <= tolerance))
    return ForceValidationResult(
        fixtures=fixtures,
        max_absolute_error=max_absolute_error,
        max_scaled_error=max_scaled_error,
        absolute_tolerance=absolute_tolerance,
        relative_tolerance=relative_tolerance,
        passed=passed,
    )

