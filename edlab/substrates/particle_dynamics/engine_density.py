"""EXP03-A engine: CORE V0 + isolated density-preference (comfortable-neighbor) mechanism.

The CORE V0 force is reused verbatim from ``engine`` so the NEUTRAL LIMIT (density_strength == 0) reduces to
CORE V0 bit-for-bit. The added term is a many-body homeostatic force toward a comfortable local density; it is
type-agnostic and cannot be expressed by the pairwise type-interaction matrix. Diagnostic IDs never enter any
computation here.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from ...specs import DensityPreferenceSpec, LawSpec, RunSpec, WorldSpec
from ...state import ParticleState
from .engine import BACKENDS, SimulationSnapshot, minimum_image, _validate_force_domain

_H_EPS = 1e-12


def _validate_density_domain(density: DensityPreferenceSpec, box_size: float) -> None:
    if density.density_radius >= box_size / 2.0:
        raise ValueError("density_radius must be strictly below box_size/2 for unique minimum-image neighbours")


def density_force_reference(state: ParticleState, density: DensityPreferenceSpec, box_size: float) -> np.ndarray:
    """Readable O(N^2) scalar density-preference force."""

    _validate_density_domain(density, box_size)
    n = state.positions.shape[0]
    out = np.zeros((n, 2), dtype=np.float64)
    if density.density_strength == 0.0:
        return out  # exact neutral term; kept explicit for clarity (also covered by the general path)
    R = density.density_radius
    for i in range(n):
        rho = 0.0
        hx = 0.0
        hy = 0.0
        for j in range(n):
            if i == j:
                continue
            dx = state.positions[j, 0] - state.positions[i, 0]
            dy = state.positions[j, 1] - state.positions[i, 1]
            dx -= box_size * round(dx / box_size)
            dy -= box_size * round(dy / box_size)
            dist = float(np.hypot(dx, dy))
            if dist <= 0.0 or dist >= R:
                continue
            kernel = 1.0 - dist / R
            rho += kernel
            hx += kernel * dx
            hy += kernel * dy
        hn = float(np.hypot(hx, hy))
        if hn > _H_EPS:
            gx, gy = hx / hn, hy / hn
        else:
            gx, gy = 0.0, 0.0
        coeff = density.density_strength * (density.comfortable_density - rho)
        out[i, 0] = coeff * gx
        out[i, 1] = coeff * gy
    return out


def density_force_vectorized(state: ParticleState, density: DensityPreferenceSpec, box_size: float) -> np.ndarray:
    """Independent vectorized density-preference force (agreement-tested vs the scalar reference)."""

    _validate_density_domain(density, box_size)
    n = state.positions.shape[0]
    if density.density_strength == 0.0:
        return np.zeros((n, 2), dtype=np.float64)
    R = density.density_radius
    disp = state.positions[np.newaxis, :, :] - state.positions[:, np.newaxis, :]  # disp[i,j] = j - i
    disp -= box_size * np.rint(disp / box_size)
    dist = np.hypot(disp[:, :, 0], disp[:, :, 1])
    neighbour = (dist > 0.0) & (dist < R)
    kernel = np.where(neighbour, 1.0 - dist / R, 0.0)
    rho = kernel.sum(axis=1)
    h = np.sum(kernel[:, :, np.newaxis] * disp, axis=1)
    hn = np.hypot(h[:, 0], h[:, 1])
    ghat = np.zeros_like(h)
    active = hn > _H_EPS
    np.divide(h, hn[:, np.newaxis], out=ghat, where=active[:, np.newaxis])
    coeff = density.density_strength * (density.comfortable_density - rho)
    return coeff[:, np.newaxis] * ghat


DENSITY_BACKENDS: dict[str, Callable[[ParticleState, DensityPreferenceSpec, float], np.ndarray]] = {
    "reference": density_force_reference,
    "vectorized": density_force_vectorized,
}


def total_force(state: ParticleState, law: LawSpec, density: DensityPreferenceSpec, box_size: float,
                *, backend: str = "vectorized") -> np.ndarray:
    core = BACKENDS[backend](state, law, box_size)          # frozen CORE V0 force (unchanged)
    dens = DENSITY_BACKENDS[backend](state, density, box_size)
    return core + dens


def step_density(state: ParticleState, law: LawSpec, density: DensityPreferenceSpec, world: WorldSpec,
                 dt: float, *, backend: str = "vectorized") -> ParticleState:
    _validate_force_domain(law, world.box_size)
    _validate_density_domain(density, world.box_size)
    if law.n_types != world.n_types:
        raise ValueError("LawSpec and WorldSpec disagree on n_types")
    if state.types.min(initial=0) < 0 or state.types.max(initial=0) >= law.n_types:
        raise ValueError("particle type is outside LawSpec interaction matrix")
    force = total_force(state, law, density, world.box_size, backend=backend)
    acceleration = force - law.damping * state.velocities
    new_velocities = state.velocities + dt * acceleration
    new_positions = (state.positions + dt * new_velocities) % world.box_size
    return ParticleState(new_positions, new_velocities, state.types.copy(), state.ids.copy())


def simulate_density(initial: ParticleState, law: LawSpec, density: DensityPreferenceSpec, world: WorldSpec,
                     run: RunSpec) -> list[SimulationSnapshot]:
    """Deterministic EXP03-A run; density_strength=0 reproduces CORE V0 simulate() bit-for-bit."""

    state = initial.copy()
    snapshots = [SimulationSnapshot(step=0, time=0.0, state=state.copy())]
    for tick in range(1, run.steps + 1):
        state = step_density(state, law, density, world, run.dt, backend=run.backend)
        if tick % run.snapshot_interval == 0 or tick == run.steps:
            snapshots.append(SimulationSnapshot(step=tick, time=tick * run.dt, state=state.copy()))
    return snapshots
