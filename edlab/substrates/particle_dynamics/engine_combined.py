"""EXP03-C engine: CORE V0 + density preference + orbital interaction (both mechanisms combined).

Reuses the frozen CORE V0 force and the validated EXP03-A density and EXP03-B orbital terms verbatim. Neutral
limit (density_strength == 0 AND orbital_strength == 0) reduces to CORE V0 bit-for-bit. Setting only one strength
to zero recovers the EXP03-B or EXP03-A path respectively. Diagnostic IDs never enter any computation.
"""

from __future__ import annotations

import numpy as np

from ...specs import DensityPreferenceSpec, LawSpec, OrbitalSpec, RunSpec, WorldSpec
from ...state import ParticleState
from .engine import BACKENDS, SimulationSnapshot, _validate_force_domain
from .engine_density import DENSITY_BACKENDS, _validate_density_domain
from .engine_orbital import ORBITAL_BACKENDS, _validate_orbital_domain


def total_force(state: ParticleState, law: LawSpec, density: DensityPreferenceSpec, orbital: OrbitalSpec,
                box_size: float, *, backend: str = "vectorized") -> np.ndarray:
    return (BACKENDS[backend](state, law, box_size)
            + DENSITY_BACKENDS[backend](state, density, box_size)
            + ORBITAL_BACKENDS[backend](state, orbital, box_size))


def step_combined(state: ParticleState, law: LawSpec, density: DensityPreferenceSpec, orbital: OrbitalSpec,
                  world: WorldSpec, dt: float, *, backend: str = "vectorized") -> ParticleState:
    _validate_force_domain(law, world.box_size)
    _validate_density_domain(density, world.box_size)
    _validate_orbital_domain(orbital, world.box_size)
    if law.n_types != world.n_types:
        raise ValueError("LawSpec and WorldSpec disagree on n_types")
    if state.types.min(initial=0) < 0 or state.types.max(initial=0) >= law.n_types:
        raise ValueError("particle type is outside LawSpec interaction matrix")
    force = total_force(state, law, density, orbital, world.box_size, backend=backend)
    acceleration = force - law.damping * state.velocities
    new_velocities = state.velocities + dt * acceleration
    new_positions = (state.positions + dt * new_velocities) % world.box_size
    return ParticleState(new_positions, new_velocities, state.types.copy(), state.ids.copy())


def simulate_combined(initial: ParticleState, law: LawSpec, density: DensityPreferenceSpec, orbital: OrbitalSpec,
                      world: WorldSpec, run: RunSpec) -> list[SimulationSnapshot]:
    state = initial.copy()
    snapshots = [SimulationSnapshot(step=0, time=0.0, state=state.copy())]
    for tick in range(1, run.steps + 1):
        state = step_combined(state, law, density, orbital, world, run.dt, backend=run.backend)
        if tick % run.snapshot_interval == 0 or tick == run.steps:
            snapshots.append(SimulationSnapshot(step=tick, time=tick * run.dt, state=state.copy()))
    return snapshots
