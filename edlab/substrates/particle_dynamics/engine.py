"""Deterministic CORE V0 particle dynamics on a two-dimensional torus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ...specs import LawSpec, RunSpec, WorldSpec
from ...state import ParticleState


FORCE_TOLERANCE = 1e-12


@dataclass(frozen=True)
class SimulationSnapshot:
    step: int
    time: float
    state: ParticleState


def minimum_image(delta: np.ndarray, box_size: float) -> np.ndarray:
    """Return the shortest periodic displacement for each coordinate."""

    return delta - box_size * np.round(delta / box_size)


def _validate_force_domain(law: LawSpec, box_size: float) -> None:
    if not np.isfinite(box_size) or box_size <= 0:
        raise ValueError("box_size must be finite and positive")
    if law.interaction_range >= box_size / 2.0:
        raise ValueError(
            "interaction_range must be strictly below box_size/2; "
            "the minimum-image direction is non-unique at the antipode"
        )


def initialize_world(
    world: WorldSpec,
    seed: int,
    *,
    ids: np.ndarray | None = None,
) -> ParticleState:
    rng = np.random.default_rng(seed)
    positions = rng.uniform(0.0, world.box_size, size=(world.n_particles, 2))
    velocities = rng.normal(0.0, world.initial_speed, size=(world.n_particles, 2))
    velocities -= velocities.mean(axis=0, keepdims=True)
    types = rng.integers(0, world.n_types, size=world.n_particles, dtype=np.int64)
    diagnostic_ids = np.arange(world.n_particles, dtype=np.int64) if ids is None else np.asarray(ids)
    return ParticleState(positions, velocities, types, diagnostic_ids)


def forces_reference(state: ParticleState, law: LawSpec, box_size: float) -> np.ndarray:
    """Readable O(N^2) scalar reference implementation."""

    _validate_force_domain(law, box_size)
    n = state.positions.shape[0]
    forces = np.zeros((n, 2), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = state.positions[j, 0] - state.positions[i, 0]
            dy = state.positions[j, 1] - state.positions[i, 1]
            dx -= box_size * round(dx / box_size)
            dy -= box_size * round(dy / box_size)
            distance = float(np.hypot(dx, dy))
            if distance == 0.0 or distance >= law.interaction_range:
                continue
            if distance < law.short_range:
                magnitude = -law.repulsion_strength * (1.0 - distance / law.short_range)
            else:
                phase = (distance - law.short_range) / (
                    law.interaction_range - law.short_range
                )
                envelope = 1.0 - abs(2.0 * phase - 1.0)
                magnitude = law.interaction[state.types[i], state.types[j]] * envelope
            forces[i, 0] += magnitude * dx / distance
            forces[i, 1] += magnitude * dy / distance
    return forces


def forces_vectorized(state: ParticleState, law: LawSpec, box_size: float) -> np.ndarray:
    """Independent vectorized all-pairs path used for screening.

    The formula is deliberately expressed separately from ``forces_reference``
    so agreement tests can catch indexing, periodicity, type-direction, and
    masking errors rather than merely exercising a shared helper.
    """

    _validate_force_domain(law, box_size)
    displacement = state.positions[np.newaxis, :, :] - state.positions[:, np.newaxis, :]
    displacement -= box_size * np.rint(displacement / box_size)
    # hypot is scale-stable for subnormal and very large finite components;
    # sqrt(dx*dx + dy*dy) can underflow to zero while the displacement is nonzero.
    distance = np.hypot(displacement[:, :, 0], displacement[:, :, 1])

    active = (distance > 0.0) & (distance < law.interaction_range)
    short = active & (distance < law.short_range)
    middle = active & ~short

    magnitude = np.zeros_like(distance)
    magnitude[short] = -law.repulsion_strength * (
        1.0 - distance[short] / law.short_range
    )

    receiver = state.types[:, np.newaxis]
    source = state.types[np.newaxis, :]
    coefficients = law.interaction[receiver, source]
    phase = np.zeros_like(distance)
    phase[middle] = (distance[middle] - law.short_range) / (
        law.interaction_range - law.short_range
    )
    envelope = np.zeros_like(distance)
    envelope[middle] = 1.0 - np.abs(2.0 * phase[middle] - 1.0)
    magnitude[middle] = coefficients[middle] * envelope[middle]

    direction = np.zeros_like(displacement)
    np.divide(
        displacement,
        distance[:, :, np.newaxis],
        out=direction,
        where=active[:, :, np.newaxis],
    )
    return np.sum(direction * magnitude[:, :, np.newaxis], axis=1)


BACKENDS: dict[str, Callable[[ParticleState, LawSpec, float], np.ndarray]] = {
    "reference": forces_reference,
    "vectorized": forces_vectorized,
}


def step(
    state: ParticleState,
    law: LawSpec,
    world: WorldSpec,
    dt: float,
    *,
    backend: str = "vectorized",
) -> ParticleState:
    _validate_force_domain(law, world.box_size)
    if law.n_types != world.n_types:
        raise ValueError("LawSpec and WorldSpec disagree on n_types")
    if state.types.min(initial=0) < 0 or state.types.max(initial=0) >= law.n_types:
        raise ValueError("particle type is outside LawSpec interaction matrix")
    try:
        force_fn = BACKENDS[backend]
    except KeyError as exc:
        raise ValueError(f"unknown backend: {backend}") from exc
    interaction_force = force_fn(state, law, world.box_size)
    acceleration = interaction_force - law.damping * state.velocities
    new_velocities = state.velocities + dt * acceleration
    new_positions = (state.positions + dt * new_velocities) % world.box_size
    return ParticleState(new_positions, new_velocities, state.types.copy(), state.ids.copy())


def simulate(
    initial: ParticleState,
    law: LawSpec,
    world: WorldSpec,
    run: RunSpec,
) -> list[SimulationSnapshot]:
    """Run deterministically and retain t=0 plus configured snapshots."""

    state = initial.copy()
    snapshots = [SimulationSnapshot(step=0, time=0.0, state=state.copy())]
    for tick in range(1, run.steps + 1):
        state = step(state, law, world, run.dt, backend=run.backend)
        if tick % run.snapshot_interval == 0 or tick == run.steps:
            snapshots.append(
                SimulationSnapshot(step=tick, time=tick * run.dt, state=state.copy())
            )
    return snapshots
