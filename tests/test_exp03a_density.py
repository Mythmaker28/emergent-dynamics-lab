"""Validation of the EXP03-A density-preference mechanism BEFORE any screening.

Critical gate: the neutral limit (density_strength == 0) must reproduce CORE V0 bit-for-bit on several
controlled worlds. Also: determinism, diagnostic-ID independence, reference/vector agreement at the frozen
float64 criterion, finite/domain guards, periodic correctness, homeostatic sign, and mechanism non-triviality.
"""

from __future__ import annotations

import numpy as np
import pytest

from edlab.specs import WorldSpec, LawSpec, RunSpec, DensityPreferenceSpec, DetectionSpec, PhenotypeSpec, TrackerSpec
from edlab.state import ParticleState
from edlab.substrates.particle_dynamics.engine import initialize_world, simulate, forces_reference, forces_vectorized
from edlab.substrates.particle_dynamics.engine_density import (
    simulate_density, step_density, total_force, density_force_reference, density_force_vectorized,
)
from edlab.entities.detection import detect_entities
from edlab.entities.tracking import LineageTracker
from edlab.observables.continuity import measure_tracks
from edlab.experiments.baseline import law_from_halton

W = WorldSpec(64, 3, initial_speed=0.04)
RUN = RunSpec(seed=1, dt=0.02, steps=120, snapshot_interval=10, backend="vectorized")


def _neutral(c=3.0, R=0.2):
    return DensityPreferenceSpec(0.0, c, R)


@pytest.mark.parametrize("law_index,seed", [(0, 11), (3, 202), (17, 7001), (52, 3001), (63, 999)])
def test_neutral_limit_equals_core_v0_bitwise(law_index, seed):
    law = law_from_halton(law_index, 3)
    initial = initialize_world(W, seed)
    core = simulate(initial, law, W, RUN)
    dens = simulate_density(initial, law, _neutral(), W, RUN)
    assert len(core) == len(dens)
    for a, b in zip(core, dens):
        assert np.array_equal(a.state.positions, b.state.positions)
        assert np.array_equal(a.state.velocities, b.state.velocities)
        assert np.array_equal(a.state.types, b.state.types)


def test_neutral_force_is_exactly_core():
    law = law_from_halton(5, 3); st = initialize_world(W, 42)
    assert np.array_equal(total_force(st, law, _neutral(), W.box_size), forces_vectorized(st, law, W.box_size))


def test_determinism():
    law = law_from_halton(7, 3); d = DensityPreferenceSpec(1.1, 3.0, 0.2); initial = initialize_world(W, 5)
    a = simulate_density(initial, law, d, W, RUN); b = simulate_density(initial, law, d, W, RUN)
    for x, y in zip(a, b):
        assert np.array_equal(x.state.positions, y.state.positions)


def test_diagnostic_ids_never_affect_physics():
    law = law_from_halton(9, 3); d = DensityPreferenceSpec(1.5, 4.0, 0.22)
    base_init = initialize_world(W, 8)
    perm = base_init.copy(); perm.ids = np.random.default_rng(0).permutation(perm.ids)
    a = simulate_density(base_init, law, d, W, RUN); b = simulate_density(perm, law, d, W, RUN)
    for x, y in zip(a, b):
        assert np.array_equal(x.state.positions, y.state.positions)
        assert np.array_equal(x.state.velocities, y.state.velocities)


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_reference_vector_agreement_frozen_criterion(seed):
    law = law_from_halton(seed, 3); d = DensityPreferenceSpec(1.7, 3.5, 0.2); st = initialize_world(W, seed * 13)
    ref = density_force_reference(st, d, W.box_size); vec = density_force_vectorized(st, d, W.box_size)
    assert np.all(np.abs(ref - vec) <= 1e-12 + 1e-10 * np.abs(ref))
    tref = forces_reference(st, law, W.box_size) + ref
    tvec = total_force(st, law, d, W.box_size, backend="vectorized")
    assert np.all(np.abs(tref - tvec) <= 1e-12 + 1e-10 * np.abs(tref))


def test_domain_and_finite_guards():
    with pytest.raises(ValueError):
        DensityPreferenceSpec(-0.1, 3.0, 0.2)           # negative strength
    with pytest.raises(ValueError):
        DensityPreferenceSpec(1.0, 3.0, 0.0)            # non-positive radius
    with pytest.raises(ValueError):
        DensityPreferenceSpec(1.0, -1.0, 0.2)           # negative comfortable
    st = initialize_world(W, 1)
    with pytest.raises(ValueError):
        density_force_vectorized(st, DensityPreferenceSpec(1.0, 3.0, 0.6), W.box_size)  # radius >= box/2


def test_periodic_neighbour_counted_across_boundary():
    # two particles straddling the periodic seam are neighbours under minimum image
    pos = np.array([[0.02, 0.5], [0.98, 0.5]] + [[0.5, 0.5]] * 62)
    vel = np.zeros((64, 2)); types = np.zeros(64, dtype=int); ids = np.arange(64)
    st = ParticleState(pos, vel, types, ids)
    d = DensityPreferenceSpec(1.0, 10.0, 0.2)  # comfortable high -> attraction toward neighbour
    f = density_force_vectorized(st, d, W.box_size)
    # particle 0 should be pulled toward particle 1 across the seam (negative x direction, wrapping)
    assert f[0, 0] < 0  # toward x=0.98 via the short way (decreasing x through 0)


def test_homeostatic_sign_below_and_above_comfortable():
    # a lone particle near a tight cluster: below comfortable -> pulled toward cluster centroid
    cluster = np.array([[0.50, 0.50], [0.51, 0.50], [0.50, 0.51], [0.49, 0.50], [0.50, 0.49]])
    lone = np.array([[0.62, 0.50]])
    filler = np.array([[0.1, 0.1]] * 58)
    pos = np.vstack([cluster, lone, filler]); vel = np.zeros((64, 2))
    st = ParticleState(pos, vel, np.zeros(64, dtype=int), np.arange(64))
    d_low = DensityPreferenceSpec(1.0, 20.0, 0.2)   # comfortable >> local density -> attraction
    f = density_force_vectorized(st, d_low, W.box_size)
    # lone particle index 5 pulled toward cluster (negative x, toward 0.50)
    assert f[5, 0] < 0
    # a central cluster particle with comfortable very low -> pushed away from local centroid
    d_high = DensityPreferenceSpec(1.0, 0.0, 0.2)
    f2 = density_force_vectorized(st, d_high, W.box_size)
    assert np.linalg.norm(f2[0]) > 0  # experiences a (repulsive) homeostatic force


def test_mechanism_is_non_trivial():
    law = law_from_halton(4, 3); initial = initialize_world(W, 77)
    core = simulate(initial, law, W, RUN)
    dens = simulate_density(initial, law, DensityPreferenceSpec(1.5, 3.0, 0.2), W, RUN)
    # active density must change the trajectory (not a no-op)
    assert not np.allclose(core[-1].state.positions, dens[-1].state.positions)


def test_detector_tracker_pm_run_on_density_sim():
    law = law_from_halton(2, 3); d = DensityPreferenceSpec(1.2, 3.0, 0.2)
    snaps = simulate_density(initialize_world(W, 21), law, d, W, RunSpec(seed=1, dt=0.02, steps=200, snapshot_interval=10))
    det = DetectionSpec(0.11, 4); phe = PhenotypeSpec(0.11, 0.25); trk = TrackerSpec(0.16, 0.25)
    tracker = LineageTracker(trk, box_size=W.box_size)
    for s in snaps:
        ents = detect_entities(s.state, snapshot_step=s.step, time=s.time, world=W, detection=det, phenotype_spec=phe)
        tracker.update(ents, snapshot_step=s.step, time=s.time)
    meas = measure_tracks(tracker.tracks, lag_indices=(1, 3, 6), events=tracker.events)
    assert isinstance(meas, list)  # pipeline runs end-to-end on EXP03-A dynamics
