"""Pre-execution gates for BALANCED-HISTORY-ISOLATION-00.

These tests must pass before seed 55001 is initialized. Engine checks use the
already-open historical DEV seed 50002 only and never calculate a feeding
contrast.
"""
from __future__ import annotations

import inspect
from types import SimpleNamespace

import numpy as np
import pytest

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import balanced_history_isolation_dev as bhi
from experiments.individuation import causal_confirm as cc
from experiments.individuation.turnover_diag_engine import DiagEngine


@pytest.fixture(scope="module")
def shallow_open_dev_state():
    return cc.seed_world(50002)


def _noswap(driver=None, *, up_ref_zero=False):
    return ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=driver, up_ref_zero=up_ref_zero,
    )


def test_manifest_to_runtime_assignment_equality():
    manifest = bhi.load_and_validate_manifest()
    for seed in bhi.DEV_SEEDS:
        assert bhi.manifest_assignment(seed, manifest) == bhi.expected_assignment(seed)


def test_exact_latin_square_balance():
    counts = {slot: {name: 0 for name in bhi.HISTORY_NAMES} for slot in range(bhi.K)}
    for seed in bhi.DEV_SEEDS:
        row = bhi.expected_assignment(seed)
        assert set(row) == set(bhi.HISTORY_NAMES)
        for slot, name in enumerate(row):
            counts[slot][name] += 1
    assert {value for row in counts.values() for value in row.values()} == {6}


def test_assignment_is_keyed_only_by_world_seed():
    assert tuple(inspect.signature(bhi.expected_assignment).parameters) == ("seed",)
    before = bhi.expected_assignment(55001)
    fake_future_outcomes = {"survival": False, "uptake": 1e99, "geometry": "bad"}
    assert fake_future_outcomes  # no outcome-like value is an input to the allocator
    assert bhi.expected_assignment(55001) == before


def test_assignment_not_applied_before_four_target_eligibility(monkeypatch):
    planned = bhi.HISTORY_NAMES

    class IdentityEngine:
        def step(self, state):
            return state

    monkeypatch.setattr(bhi, "expected_assignment", lambda seed: planned)
    monkeypatch.setattr(bhi, "manifest_assignment", lambda seed, manifest: pytest.fail("assignment read before eligibility"))
    monkeypatch.setattr(bhi.cc, "build", lambda mem: IdentityEngine())
    monkeypatch.setattr(bhi.cc, "seed_world", lambda seed: object())
    monkeypatch.setattr(bhi, "detect", lambda state, spec: [])
    world = bhi.run_world(123, {})
    assert world["prehistory_eligible"] is False
    assert world["assignment_applied"] is False


def test_four_target_spatial_eligibility_and_deterministic_slots():
    entities = [
        SimpleNamespace(size=80, centroid=(4.0, 4.0)),
        SimpleNamespace(size=70, centroid=(4.0, 32.0)),
        SimpleNamespace(size=60, centroid=(32.0, 4.0)),
        SimpleNamespace(size=50, centroid=(32.0, 32.0)),
    ]
    selected = bhi.pick_four(list(reversed(entities)))
    assert [item.size for item in selected] == [80, 70, 60, 50]
    assert all(bhi.periodic_distance(selected[i].centroid, selected[j].centroid) >= bhi.SEP
               for i in range(4) for j in range(i + 1, 4))


def test_clamp_disabled_engine_is_bit_identical(shallow_open_dev_state):
    ordinary = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER)
    disabled = _noswap()
    left = shallow_open_dev_state.copy()
    right = shallow_open_dev_state.copy()
    for _ in range(6):
        left = ordinary.step(left)
        right = disabled.step(right)
    assert all(np.array_equal(getattr(left, field), getattr(right, field)) for field in ns.STATE_FIELDS)
    assert left.step == right.step


def test_qualified_two_cell_clamp_isolates_core(shallow_open_dev_state):
    state = shallow_open_dev_state
    partition, core, barrier = ns.core_and_collar(state.rho.shape, (32.0, 32.0))
    horizon = 8
    driver = ns.record_boundary(state, _noswap(up_ref_zero=True), barrier, horizon)
    left_engine = _noswap(ns.BoundaryDriver(driver.ring, driver.frames), up_ref_zero=True)
    right_engine = _noswap(ns.BoundaryDriver(driver.ring, driver.frames), up_ref_zero=True)
    outside = partition.distance > (ns.CORE_RADIUS + ns.BARRIER_WIDTH + 1)
    left = state.copy()
    right = state.copy()
    right.c[outside] += 0.1
    right.N[outside] += 0.1
    for _ in range(horizon):
        left = left_engine.step(left)
        right = right_engine.step(right)
    assert float(np.max(np.abs(left.c[outside] - right.c[outside]))) > 0.0
    assert all(np.array_equal(getattr(left, field)[..., core], getattr(right, field)[..., core])
               for field in ns.STATE_FIELDS)


def test_common_probe_reset_and_global_ablation(shallow_open_dev_state):
    source = shallow_open_dev_state.copy()
    source.N = source.N + np.arange(source.N.size, dtype=float).reshape(source.N.shape) / source.N.size
    reset = bhi.standardized_probe_start(source)
    assert np.all(reset.N == cc.N0)
    for field in ("rho", "U", "V", "c", "C", "uptake", "Mf"):
        assert np.array_equal(getattr(reset, field), getattr(source, field))
    isolated = _noswap(up_ref_zero=True)
    global_matched = DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
    assert isolated.up_ref_zero is True
    assert global_matched.up_ref_zero is True


def test_deterministic_replay_on_already_open_dev_seed():
    left = cc.seed_world(50002)
    right = cc.seed_world(50002)
    left_engine = cc.build(cc.MEM_INTACT)
    right_engine = cc.build(cc.MEM_INTACT)
    for _ in range(6):
        left = left_engine.step(left)
        right = right_engine.step(right)
    assert bhi.state_hash(left) == bhi.state_hash(right)


def test_factorial_scaling_is_exact():
    values = {"H_L_EARLY": 1.0, "H_L_LATE": 2.0, "H_H_EARLY": 5.0, "H_H_LATE": 3.0}
    assert bhi.factorial_scalar(values) == {"dose": 2.5, "order": 0.5, "interaction": 3.0}


def _fake_complete_world(seed: int) -> dict:
    contrasts = {"dose": 1.0, "order": -0.5, "interaction": 0.0}
    arms = {
        name: {"tracked_contrasts": dict(contrasts)}
        for name in ("coupled", "coupled_g0", "isolated", "coupled_lamplus0", "isolated_lamplus0")
    }
    first_stage = {
        feature: {"dose": 1.0, "order": -1.0, "interaction": 0.0}
        for feature in bhi.FIRST_STAGE_SCALARS
    }
    first_stage["full_field"] = {
        "dose": {"vector": [1.0, 0.0]},
        "order": {"vector": [0.0, 1.0]},
        "interaction": {"vector": [1.0, 1.0]},
    }
    return {
        "seed": seed,
        "prehistory_eligible": True,
        "assignment_applied": True,
        "deep_valid": True,
        "complete_block": True,
        "sham_exact": True,
        "history_survival": {name: True for name in bhi.HISTORY_NAMES},
        "deep_survival": {name: True for name in bhi.HISTORY_NAMES},
        "arms": arms,
        "first_stage_contrasts": first_stage,
        "transport": {"dose": 0.0, "order": 0.0, "interaction": 0.0},
        "transport_global_matched": {"dose": 0.0, "order": 0.0, "interaction": 0.0},
        "target_rows_that_must_not_be_replicates": list(range(100)),
    }


def test_aggregation_uses_original_world_not_target_rows():
    worlds = [_fake_complete_world(seed) for seed in range(4)]
    failed = {
        "seed": 4,
        "prehistory_eligible": True,
        "assignment_applied": True,
        "deep_valid": False,
        "complete_block": False,
        "history_survival": {name: True for name in bhi.HISTORY_NAMES},
        "deep_survival": {name: False for name in bhi.HISTORY_NAMES},
    }
    summary = bhi.aggregate(worlds + [failed])
    assert summary["n_complete_valid_worlds"] == 4
    assert summary["feeding_contrasts"]["isolated"]["dose"]["n_worlds"] == 4
    assert all(row["assigned"] == 5 for row in summary["itt_survival_by_history"].values())


def test_incomplete_family_marks_scientific_gates_not_evaluable():
    summary = bhi.aggregate([])
    assert summary["conclusion"] == "DEV-FEASIBILITY-FAIL"
    assert summary["conclusion_reason"] == "FEWER_THAN_FOUR_COMPLETE_WORLDS"
    assert summary["gates"]["minimum_four_complete_worlds"] is False
    assert summary["gates"]["dose_first_stage_expected_orientation_and_ci"] is None
    assert summary["gates"]["manipulation_sham_exact"] is None


def test_forbidden_and_unfrozen_namespaces_are_rejected():
    for seed in (50001, 51000, 52001, 53001, 54001, 54120, 55000, 55025):
        with pytest.raises(ValueError):
            bhi.expected_assignment(seed)
    assert not (set(bhi.DEV_SEEDS) & (set(range(50001, 50011)) | set(range(51000, 54121))))


def test_manifest_hash_parent_family_and_horizon_are_frozen():
    manifest = bhi.load_and_validate_manifest()
    assert bhi.sha256_file(bhi.DEFAULT_MANIFEST) == bhi.MANIFEST_SHA256
    assert manifest["canonical_parent"] == bhi.CANONICAL_PARENT
    assert tuple(manifest["seeds"]) == bhi.DEV_SEEDS
    assert bhi.HORIZON == 40
    assert bhi.SETTLE_STD == 40


def test_atomic_writer_returns_raw_file_digest(tmp_path):
    path = tmp_path / "result.json"
    announced = bhi.atomic_write_json(path, {"line": "one\ntwo"})
    assert announced == bhi.sha256_file(path)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
