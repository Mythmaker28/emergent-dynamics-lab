"""Validation of the ALIAS-INTERVENTION harness BEFORE any causal execution.

These tests encode the no-op / sham / validated-reference controls required by D-015:
sham == control bit-for-bit, conservation under perturbation, a real off-site displacement,
diagnostic IDs never entering physics, determinism, and enrollment reproducing HOLDOUT04.
"""

from __future__ import annotations

import numpy as np
import pytest

from edlab.experiments.causal_intervention import (
    CausalConfig, enroll, apply_displacement, periodic_distance, run_causal_experiment,
)
from edlab.substrates.particle_dynamics.engine import initialize_world, simulate, minimum_image
from edlab.specs import RunSpec, WorldSpec
from edlab.experiments.baseline import law_from_halton

CFG = CausalConfig()
BOX = 1.0


def _enrolled_example():
    # law 0 seed 3002 is a frozen HOLDOUT04 survivor-seed: it enrolls.
    enr, snaps, ents = enroll(CFG, 0, 3002)
    assert enr.enrolled
    return enr


def test_enroll_reproduces_holdout04_disposition():
    # Independent path must reproduce D-015: law 0 -> {3002,3004}, law 52 -> {3001,3003}; others censored.
    got = {0: set(), 52: set()}
    for law in (0, 52):
        for seed in (3001, 3002, 3003, 3004, 3005):
            enr, _, _ = enroll(CFG, law, seed)
            if enr.enrolled:
                got[law].add(seed)
    assert got[0] == {3002, 3004}
    assert got[52] == {3001, 3003}


def test_sham_is_pipeline_exact_noop():
    enr = _enrolled_example()
    sham = apply_displacement(enr.state, enr.candidate_indices, (0.0, 0.0), BOX)
    assert np.array_equal(sham.positions, enr.state.positions)
    assert np.array_equal(sham.velocities, enr.state.velocities)
    assert np.array_equal(sham.types, enr.state.types)
    assert np.array_equal(sham.ids, enr.state.ids)


def test_sham_trajectory_equals_control_bit_for_bit():
    enr = _enrolled_example()
    law = law_from_halton(0, 3)
    world = WorldSpec(64, 3, initial_speed=0.04)
    run = RunSpec(seed=1, dt=CFG.dt, steps=120, snapshot_interval=CFG.base_cadence)
    control = simulate(enr.state.copy(), law, world, run)
    sham0 = apply_displacement(enr.state, enr.candidate_indices, (0.0, 0.0), BOX)
    sham = simulate(sham0, law, world, run)
    for a, b in zip(control, sham):
        assert np.array_equal(a.state.positions, b.state.positions)
        assert np.array_equal(a.state.velocities, b.state.velocities)


def test_perturbation_moves_candidate_offsite_only():
    enr = _enrolled_example()
    pert = apply_displacement(enr.state, enr.candidate_indices, CFG.delta, BOX)
    idx = np.asarray(enr.candidate_indices)
    mask = np.ones(enr.state.positions.shape[0], dtype=bool); mask[idx] = False
    # non-candidates untouched
    assert np.array_equal(pert.positions[mask], enr.state.positions[mask])
    # candidate centroid moved by > tracker gate (off-site)
    old_c = np.asarray(enr.old_centroid)
    from edlab.entities.detection import periodic_centroid
    new_c = periodic_centroid(pert.positions[idx], BOX)
    assert periodic_distance(new_c, old_c, BOX) > CFG.tracker_distance


def test_perturbation_conserves_globals_and_internal_geometry():
    enr = _enrolled_example()
    pert = apply_displacement(enr.state, enr.candidate_indices, CFG.delta, BOX)
    # global conservation
    assert np.allclose(pert.velocities.sum(0), enr.state.velocities.sum(0), atol=1e-12)
    assert np.array_equal(np.sort(pert.types), np.sort(enr.state.types))
    assert pert.positions.shape == enr.state.positions.shape
    assert set(pert.ids.tolist()) == set(enr.state.ids.tolist())
    # rigid translation preserves internal minimum-image geometry of the candidate exactly
    idx = np.asarray(enr.candidate_indices)
    def pdists(P):
        d = minimum_image(P[idx][:, None, :] - P[idx][None, :, :], BOX)
        return np.linalg.norm(d, axis=2)
    assert np.allclose(pdists(pert.positions), pdists(enr.state.positions), atol=1e-12)


def test_diagnostic_ids_never_affect_physics():
    enr = _enrolled_example()
    law = law_from_halton(0, 3)
    world = WorldSpec(64, 3, initial_speed=0.04)
    run = RunSpec(seed=1, dt=CFG.dt, steps=60, snapshot_interval=CFG.base_cadence)
    base = simulate(apply_displacement(enr.state, enr.candidate_indices, CFG.delta, BOX), law, world, run)
    permuted = enr.state.copy()
    rng = np.random.default_rng(0)
    permuted.ids = rng.permutation(permuted.ids)
    perm = simulate(apply_displacement(permuted, enr.candidate_indices, CFG.delta, BOX), law, world, run)
    for a, b in zip(base, perm):
        assert np.array_equal(a.state.positions, b.state.positions)
        assert np.array_equal(a.state.velocities, b.state.velocities)


def test_enroll_deterministic():
    a, _, _ = enroll(CFG, 52, 3001)
    b, _, _ = enroll(CFG, 52, 3001)
    assert a.candidate_ids == b.candidate_ids
    assert a.first_eligible_end == b.first_eligible_end
    assert np.array_equal(a.state.positions, b.state.positions)


def test_run_experiment_smoke(tmp_path):
    # Small run: one law, a censored + an enrolled seed, short horizon. Validates outputs + sham identity.
    cfg = CausalConfig(laws=(0,), seed_plan=(5001, 5004), horizon_post=120)
    out = tmp_path / "smoke"
    summ = run_causal_experiment(output_dir=out, experiment_id="TEST", git_commit="TEST", config=cfg,
                                 protocol_sha="TEST")
    assert (out / "enrollment.csv").exists()
    assert (out / "branch_readouts.csv").exists()
    assert (out / "manifest.json").exists()
    # 5004 enrolls, 5001 censored (from prior probe); at least one enrolled unit with sham==control
    assert summ["n_enrolled_total"] >= 1
    law0 = summ["by_law"]["0"]
    assert law0["all_sham_equals_control"] in (True, None)
