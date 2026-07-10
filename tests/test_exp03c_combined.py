"""Validation of the EXP03-C combined (density + orbital) mechanism BEFORE any screening."""

from __future__ import annotations

import numpy as np
import pytest

from edlab.specs import WorldSpec, RunSpec, DensityPreferenceSpec, OrbitalSpec
from edlab.substrates.particle_dynamics.engine import initialize_world, simulate, forces_vectorized
from edlab.substrates.particle_dynamics.engine_density import simulate_density
from edlab.substrates.particle_dynamics.engine_orbital import simulate_orbital
from edlab.substrates.particle_dynamics.engine_combined import simulate_combined, total_force
from edlab.experiments.baseline import law_from_halton
from edlab.experiments.exp03c_combined import exp03c_law

W = WorldSpec(64, 3, initial_speed=0.04)
RUN = RunSpec(seed=1, dt=0.02, steps=120, snapshot_interval=10)
D0 = DensityPreferenceSpec(0.0, 3.0, 0.2); O0 = OrbitalSpec(0.0, 0.18)


@pytest.mark.parametrize("li,seed", [(0, 11), (3, 202), (17, 7001), (52, 3001), (63, 999)])
def test_neutral_limit_both_zero_equals_core_bitwise(li, seed):
    law = law_from_halton(li, 3); initial = initialize_world(W, seed)
    core = simulate(initial, law, W, RUN); comb = simulate_combined(initial, law, D0, O0, W, RUN)
    for a, b in zip(core, comb):
        assert np.array_equal(a.state.positions, b.state.positions)
        assert np.array_equal(a.state.velocities, b.state.velocities)


def test_neutral_force_exact():
    law = law_from_halton(5, 3); st = initialize_world(W, 42)
    assert np.array_equal(total_force(st, law, D0, O0, W.box_size), forces_vectorized(st, law, W.box_size))


@pytest.mark.parametrize("li,seed", [(1, 5), (7, 21), (30, 700)])
def test_partial_limits_recover_single_mechanisms(li, seed):
    law = law_from_halton(li, 3); initial = initialize_world(W, seed)
    dA = DensityPreferenceSpec(1.2, 3.0, 0.2); oB = OrbitalSpec(0.8, 0.18)
    cd = simulate_combined(initial, law, dA, O0, W, RUN); dd = simulate_density(initial, law, dA, W, RUN)
    co = simulate_combined(initial, law, D0, oB, W, RUN); oo = simulate_orbital(initial, law, oB, W, RUN)
    for a, b in zip(cd, dd):
        assert np.array_equal(a.state.positions, b.state.positions)   # (density, 0) == density path
    for a, b in zip(co, oo):
        assert np.array_equal(a.state.positions, b.state.positions)   # (0, orbital) == orbital path


def test_determinism_and_id_independence():
    law = law_from_halton(9, 3); d = DensityPreferenceSpec(1.1, 4.0, 0.2); o = OrbitalSpec(0.7, 0.2)
    base = initialize_world(W, 8)
    a = simulate_combined(base, law, d, o, W, RUN); b = simulate_combined(base, law, d, o, W, RUN)
    for x, y in zip(a, b):
        assert np.array_equal(x.state.positions, y.state.positions)
    perm = base.copy(); perm.ids = np.random.default_rng(0).permutation(perm.ids)
    c = simulate_combined(perm, law, d, o, W, RUN)
    for x, y in zip(a, c):
        assert np.array_equal(x.state.positions, y.state.positions)


def test_on_law_is_non_trivial_and_off_is_core():
    core_law, d_off, o_off = exp03c_law(4, 3, on=False)
    assert d_off.is_neutral and o_off.is_neutral        # OFF == CORE V0
    _, d_on, o_on = exp03c_law(4, 3, on=True)
    assert (not d_on.is_neutral) and (not o_on.is_neutral)
    initial = initialize_world(W, 77)
    core = simulate(initial, law_from_halton(4, 3), W, RUN)
    comb = simulate_combined(initial, law_from_halton(4, 3), d_on, o_on, W, RUN)
    assert not np.allclose(core[-1].state.positions, comb[-1].state.positions)
