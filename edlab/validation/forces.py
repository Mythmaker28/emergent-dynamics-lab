"""Independent force-path comparison on controlled random worlds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..specs import LawSpec, WorldSpec
from ..substrates.particle_dynamics.engine import (
    forces_reference,
    forces_vectorized,
    initialize_world,
    step,
)


@dataclass(frozen=True)
class ForceValidationResult:
    fixtures: int
    max_absolute_error: float
    max_scaled_error: float
    max_one_step_absolute_error: float
    max_one_step_scaled_error: float
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
    max_one_step_absolute_error = 0.0
    max_one_step_scaled_error = 0.0
    passed = True
    for fixture in range(fixtures):
        rng = np.random.default_rng(10_000 + fixture)
        n_types = 1 + fixture % 4
        particle_counts = (2, 3, 8, 16, 32, 64)
        world = WorldSpec(
            n_particles=particle_counts[fixture % len(particle_counts)],
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
        reference_step = step(state, law, world, 0.01, backend="reference")
        vectorized_step = step(state, law, world, 0.01, backend="vectorized")
        reference_arrays = np.concatenate(
            [reference_step.positions.ravel(), reference_step.velocities.ravel()]
        )
        vectorized_arrays = np.concatenate(
            [vectorized_step.positions.ravel(), vectorized_step.velocities.ravel()]
        )
        step_absolute = np.abs(reference_arrays - vectorized_arrays)
        step_tolerance = absolute_tolerance + relative_tolerance * np.abs(reference_arrays)
        step_scaled = np.divide(
            step_absolute,
            step_tolerance,
            out=np.zeros_like(step_absolute),
            where=step_tolerance > 0,
        )
        max_one_step_absolute_error = max(
            max_one_step_absolute_error, float(step_absolute.max(initial=0.0))
        )
        max_one_step_scaled_error = max(
            max_one_step_scaled_error, float(step_scaled.max(initial=0.0))
        )
        passed = passed and bool(np.all(step_absolute <= step_tolerance))
    return ForceValidationResult(
        fixtures=fixtures,
        max_absolute_error=max_absolute_error,
        max_scaled_error=max_scaled_error,
        max_one_step_absolute_error=max_one_step_absolute_error,
        max_one_step_scaled_error=max_one_step_scaled_error,
        absolute_tolerance=absolute_tolerance,
        relative_tolerance=relative_tolerance,
        passed=passed,
    )
