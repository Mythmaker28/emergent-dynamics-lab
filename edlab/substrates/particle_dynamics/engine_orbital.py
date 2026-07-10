"""EXP03-B engine: CORE V0 + isolated orbital/transverse interaction.

The CORE V0 force is reused verbatim so the NEUTRAL LIMIT (orbital_strength == 0) reduces to CORE V0 bit-for-bit.
The added term is a transverse pair force perpendicular to the connecting line: equal-and-opposite (linear
momentum conserved) but torque-producing (injects circulation). Type-agnostic and isolated. Diagnostic IDs never
enter any computation.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from ...specs import LawSpec, OrbitalSpec, RunSpec, WorldSpec
from ...state import ParticleState
from .engine import BACKENDS, SimulationSnapshot, minimum_image, _validate_force_domain


def _validate_orbital_domain(orbital: OrbitalSpec, box_size: float) -> None:
    if orbital.orbital_range >= box_size / 2.0:
        raise ValueError("orbital_range must be strictly below box_size/2 for unique minimum-image geometry")


def orbital_force_reference(state: ParticleState, orbital: OrbitalSpec, box_size: float) -> np.ndarray:
    _validate_orbital_domain(orbital, box_size)
    n = state.positions.shape[0]
    out = np.zeros((n, 2), dtype=np.float64)
    if orbital.orbital_strength == 0.0:
        return out
    R = orbital.orbital_range
    for i in range(n):
        fx = 0.0
        fy = 0.0
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
            phase = dist / R
            env = 1.0 - abs(2.0 * phase - 1.0)          # triangular peak at R/2
            ux, uy = dx / dist, dy / dist
            # transverse direction = rot90(unit) = (-uy, ux)
            fx += orbital.orbital_strength * env * (-uy)
            fy += orbital.orbital_strength * env * (ux)
        out[i, 0] = fx
        out[i, 1] = fy
    return out


def orbital_force_vectorized(state: ParticleState, orbital: OrbitalSpec, box_size: float) -> np.ndarray:
    _validate_orbital_domain(orbital, box_size)
    n = state.positions.shape[0]
    if orbital.orbital_strength == 0.0:
        return np.zeros((n, 2), dtype=np.float64)
    R = orbital.orbital_range
    disp = state.positions[np.newaxis, :, :] - state.positions[:, np.newaxis, :]  # j - i
    disp -= box_size * np.rint(disp / box_size)
    dist = np.hypot(disp[:, :, 0], disp[:, :, 1])
    active = (dist > 0.0) & (dist < R)
    phase = np.where(active, dist / R, 0.0)
    env = np.where(active, 1.0 - np.abs(2.0 * phase - 1.0), 0.0)
    unit = np.zeros_like(disp)
    np.divide(disp, dist[:, :, np.newaxis], out=unit, where=active[:, :, np.newaxis])
    # transverse = rot90(unit): (-uy, ux)
    trans = np.stack([-unit[:, :, 1], unit[:, :, 0]], axis=2)
    contrib = orbital.orbital_strength * env[:, :, np.newaxis] * trans
    return contrib.sum(axis=1)


ORBITAL_BACKENDS: dict[str, Callable[[ParticleState, OrbitalSpec, float], np.ndarray]] = {
    "reference": orbital_force_reference,
    "vectorized": orbital_force_vectorized,
}


def total_force(state: ParticleState, law: LawSpec, orbital: OrbitalSpec, box_size: float,
                *, backend: str = "vectorized") -> np.ndarray:
    return BACKENDS[backend](state, law, box_size) + ORBITAL_BACKENDS[backend](state, orbital, box_size)


def step_orbital(state: ParticleState, law: LawSpec, orbital: OrbitalSpec, world: WorldSpec,
                 dt: float, *, backend: str = "vectorized") -> ParticleState:
    _validate_force_domain(law, world.box_size)
    _validate_orbital_domain(orbital, world.box_size)
    if law.n_types != world.n_types:
        raise ValueError("LawSpec and WorldSpec disagree on n_types")
    if state.types.min(initial=0) < 0 or state.types.max(initial=0) >= law.n_types:
        raise ValueError("particle type is outside LawSpec interaction matrix")
    force = total_force(state, law, orbital, world.box_size, backend=backend)
    acceleration = force - law.damping * state.velocities
    new_velocities = state.velocities + dt * acceleration
    new_positions = (state.positions + dt * new_velocities) % world.box_size
    return ParticleState(new_positions, new_velocities, state.types.copy(), state.ids.copy())


def simulate_orbital(initial: ParticleState, law: LawSpec, orbital: OrbitalSpec, world: WorldSpec,
                     run: RunSpec) -> list[SimulationSnapshot]:
    state = initial.copy()
    snapshots = [SimulationSnapshot(step=0, time=0.0, state=state.copy())]
    for tick in range(1, run.steps + 1):
        state = step_orbital(state, law, orbital, world, run.dt, backend=run.backend)
        if tick % run.snapshot_interval == 0 or tick == run.steps:
            snapshots.append(SimulationSnapshot(step=tick, time=tick * run.dt, state=state.copy()))
    return snapshots
