"""Validation of the EXP03-B orbital/transverse mechanism BEFORE any screening.

Critical gate: neutral limit (orbital_strength == 0) reproduces CORE V0 bit-for-bit on several worlds. Also:
determinism, diagnostic-ID independence, reference/vector agreement, momentum conservation, circulation
(angular-momentum injection) signature, finite/domain guards, periodic correctness, non-triviality, and the
frozen detector/tracker/P/M pipeline running on orbital dynamics.
"""

from __future__ import annotations

import numpy as np
import pytest

from edlab.specs import (WorldSpec, RunSpec, OrbitalSpec, DetectionSpec, PhenotypeSpec, TrackerSpec)
from edlab.state import ParticleState
from edlab.substrates.particle_dynamics.engine import initialize_world, simulate, forces_reference, forces_vectorized
from edlab.substrates.particle_dynamics.engine_orbital import (
    simulate_orbital, step_orbital, total_force, orbital_force_reference, orbital_force_vectorized,
)
from edlab.entities.detection import detect_entities
from edlab.entities.tracking import LineageTracker
from edlab.observables.continuity import measure_tracks
from edlab.experiments.baseline import law_from_halton

W = WorldSpec(64, 3, initial_speed=0.04)
RUN = RunSpec(seed=1, dt=0.02, steps=120, snapshot_interval=10, backend="vectorized")


@pytest.mark.parametrize("law_index,seed", [(0, 11), (3, 202), (17, 7001), (52, 3001), (63, 999)])
def test_neutral_limit_equals_core_v0_bitwise(law_index, seed):
    law = law_from_halton(law_index, 3); initial = initialize_world(W, seed)
    core = simulate(initial, law, W, RUN)
    orb = simulate_orbital(initial, law, OrbitalSpec(0.0, 0.18), W, RUN)
    for a, b in zip(core, orb):
        assert np.array_equal(a.state.positions, b.state.positions)
        assert np.array_equal(a.state.velocities, b.state.velocities)


def test_neutral_force_is_exactly_core():
    law = law_from_halton(5, 3); st = initialize_world(W, 42)
    assert np.array_equal(total_force(st, law, OrbitalSpec(0.0, 0.18), W.box_size), forces_vectorized(st, law, W.box_size))


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_reference_vector_agreement_frozen_criterion(seed):
    law = law_from_halton(seed, 3); o = OrbitalSpec(0.9, 0.2); st = initialize_world(W, seed * 13)
    ref = orbital_force_reference(st, o, W.box_size); vec = orbital_force_vectorized(st, o, W.box_size)
    assert np.all(np.abs(ref - vec) <= 1e-12 + 1e-10 * np.abs(ref))
    tref = forces_reference(st, law, W.box_size) + ref
    tvec = total_force(st, law, o, W.box_size, backend="vectorized")
    assert np.all(np.abs(tref - tvec) <= 1e-12 + 1e-10 * np.abs(tref))


def test_momentum_conserved():
    o = OrbitalSpec(1.3, 0.2); st = initialize_world(W, 7)
    f = orbital_force_vectorized(st, o, W.box_size)
    assert np.allclose(f.sum(axis=0), 0.0, atol=1e-12)  # equal-and-opposite transverse pair forces


def test_circulation_injected_vs_radial_from_rest():
    # ring of particles at rest: orbital force injects angular momentum; central (core) force does not.
    k = 12
    ang = np.linspace(0, 2 * np.pi, k, endpoint=False)
    ring = 0.5 + 0.12 * np.stack([np.cos(ang), np.sin(ang)], axis=1)
    filler = np.array([[0.05, 0.05]] * (64 - k))
    pos = np.vstack([ring, filler]); vel = np.zeros((64, 2))
    st = ParticleState(pos, vel, np.zeros(64, dtype=int), np.arange(64))
    law = law_from_halton(0, 3)
    def ang_mom(state):
        rel = state.positions - state.positions.mean(axis=0)
        return float(np.sum(rel[:, 0] * state.velocities[:, 1] - rel[:, 1] * state.velocities[:, 0]))
    orb = step_orbital(st, law, OrbitalSpec(2.0, 0.28), W, 0.02)
    core = step_orbital(st, law, OrbitalSpec(0.0, 0.28), W, 0.02)  # neutral == core
    assert abs(ang_mom(orb)) > 1e-6          # circulation injected
    assert abs(ang_mom(core)) < 1e-9         # radial-only conserves L (~0 from rest)


def test_determinism_and_id_independence():
    law = law_from_halton(9, 3); o = OrbitalSpec(0.7, 0.2); base = initialize_world(W, 8)
    a = simulate_orbital(base, law, o, W, RUN); b = simulate_orbital(base, law, o, W, RUN)
    for x, y in zip(a, b):
        assert np.array_equal(x.state.positions, y.state.positions)
    perm = base.copy(); perm.ids = np.random.default_rng(0).permutation(perm.ids)
    c = simulate_orbital(perm, law, o, W, RUN)
    for x, y in zip(a, c):
        assert np.array_equal(x.state.positions, y.state.positions)


def test_domain_and_finite_guards():
    with pytest.raises(ValueError):
        OrbitalSpec(1.0, 0.0)
    with pytest.raises(ValueError):
        OrbitalSpec(float("nan"), 0.2)
    st = initialize_world(W, 1)
    with pytest.raises(ValueError):
        orbital_force_vectorized(st, OrbitalSpec(1.0, 0.6), W.box_size)  # range >= box/2


def test_periodic_transverse_across_boundary():
    pos = np.array([[0.02, 0.5], [0.98, 0.5]] + [[0.2, 0.2]] * 62)
    st = ParticleState(pos, np.zeros((64, 2)), np.zeros(64, dtype=int), np.arange(64))
    f = orbital_force_vectorized(st, OrbitalSpec(1.0, 0.2), W.box_size)
    # particle 0 sees neighbour across the seam (short way through x=0); transverse force is non-zero and vertical
    assert abs(f[0, 1]) > 1e-9


def test_mechanism_is_non_trivial():
    law = law_from_halton(4, 3); initial = initialize_world(W, 77)
    core = simulate(initial, law, W, RUN)
    orb = simulate_orbital(initial, law, OrbitalSpec(1.2, 0.2), W, RUN)
    assert not np.allclose(core[-1].state.positions, orb[-1].state.positions)


def test_detector_tracker_pm_run_on_orbital_sim():
    law = law_from_halton(2, 3); o = OrbitalSpec(1.0, 0.2)
    snaps = simulate_orbital(initialize_world(W, 21), law, o, W, RunSpec(seed=1, dt=0.02, steps=200, snapshot_interval=10))
    det = DetectionSpec(0.11, 4); phe = PhenotypeSpec(0.11, 0.25); trk = TrackerSpec(0.16, 0.25)
    tracker = LineageTracker(trk, box_size=W.box_size)
    for s in snaps:
        tracker.update(detect_entities(s.state, snapshot_step=s.step, time=s.time, world=W, detection=det, phenotype_spec=phe),
                       snapshot_step=s.step, time=s.time)
    assert isinstance(measure_tracks(tracker.tracks, lag_indices=(1, 3, 6), events=tracker.events), list)
