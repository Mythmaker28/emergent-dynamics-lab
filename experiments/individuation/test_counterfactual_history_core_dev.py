"""Before-data gates for COUNTERFACTUAL-HISTORY-CORE-00.

Dynamic engine tests use already-open DEV seed 50002 only.  They must pass
before any seed in the fresh 57001-57024 family is initialized.
"""
from __future__ import annotations

import inspect
import json

import numpy as np
import pytest

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import causal_confirm as cc
from experiments.individuation import counterfactual_history_core_dev as chc
from experiments.individuation.turnover_diag_engine import DiagEngine


@pytest.fixture(scope="module")
def open_checkpoint():
    checkpoint = chc.make_checkpoint(50002)
    assert checkpoint["focal_id"] is not None
    return checkpoint


@pytest.fixture(scope="module")
def ordered_history_runs(open_checkpoint):
    canonical = chc.run_histories(open_checkpoint, chc.HISTORY_NAMES)
    reversed_run = chc.run_histories(open_checkpoint, tuple(reversed(chc.HISTORY_NAMES)))
    return canonical, reversed_run


def _noswap(driver=None, *, up_ref_zero=False):
    return ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=driver, up_ref_zero=up_ref_zero,
    )


def test_four_branches_are_byte_identical_before_history(open_checkpoint):
    validation = chc.validate_four_clones(open_checkpoint)
    assert validation["valid"] is True
    assert len(set(validation["state_byte_sha256"])) == 1
    assert len(set(validation["tracker_mapping_sha256"])) == 1
    assert all(all(value == 0 for value in row.values())
               for row in validation["max_abs_errors_vs_branch0"])


def test_exact_focal_identity_across_clones(open_checkpoint):
    branches = [chc.clone_checkpoint(open_checkpoint) for _ in chc.HISTORY_NAMES]
    focal_id = open_checkpoint["focal_id"]
    focal_hashes = [chc._mask_digest(branch["tracker_masks"][focal_id]) for branch in branches]
    assert [branch["focal_id"] for branch in branches] == [focal_id] * 4
    assert len(set(focal_hashes)) == 1
    eligible_ids = [row["canonical_tracker_id"] for row in open_checkpoint["eligibility"] if row["eligible"]]
    assert focal_id == min(eligible_ids)


def test_exact_history_amplitudes_and_temporal_order(open_checkpoint):
    assert chc.HISTORIES == {
        "H_L_EARLY": (0.0175, 0.0075),
        "H_L_LATE": (0.0075, 0.0175),
        "H_H_EARLY": (0.0325, 0.0225),
        "H_H_LATE": (0.0225, 0.0325),
    }
    for name in chc.HISTORY_NAMES:
        plan = chc.history_treatment_plan(open_checkpoint, name)
        assert plan["focal_amplitudes"] == list(chc.HISTORIES[name])
        assert plan["focal_episode_steps"] == [60, 60]
    assert sum(chc.HISTORIES["H_L_EARLY"]) == sum(chc.HISTORIES["H_L_LATE"])
    assert sum(chc.HISTORIES["H_H_EARLY"]) == sum(chc.HISTORIES["H_H_LATE"])
    assert chc.HISTORIES["H_L_EARLY"][0] > chc.HISTORIES["H_L_EARLY"][1]
    assert chc.HISTORIES["H_L_LATE"][0] < chc.HISTORIES["H_L_LATE"][1]


def test_nonfocal_targets_have_identical_no_direct_drive(open_checkpoint):
    plans = [chc.history_treatment_plan(open_checkpoint, name) for name in chc.HISTORY_NAMES]
    assert all(plan["nonfocal_rule"].startswith("no direct assigned drive") for plan in plans)
    keys = set(plans[0]["nonfocal_direct_amplitudes"])
    assert all(set(plan["nonfocal_direct_amplitudes"]) == keys for plan in plans)
    assert all(value == [0.0, 0.0] for plan in plans
               for value in plan["nonfocal_direct_amplitudes"].values())


def test_execution_order_does_not_change_branch_results(ordered_history_runs):
    canonical, reversed_run = ordered_history_runs
    for name in chc.HISTORY_NAMES:
        assert chc.state_hash(canonical[name]["state"]) == chc.state_hash(reversed_run[name]["state"])
        assert canonical[name]["valid"] == reversed_run[name]["valid"]
        assert canonical[name]["reason"] == reversed_run[name]["reason"]


def test_deterministic_replay_from_same_checkpoint(ordered_history_runs):
    first, second = ordered_history_runs
    for name in chc.HISTORY_NAMES:
        left = chc.canonical_state_bytes(first[name]["state"])
        right = chc.canonical_state_bytes(second[name]["state"])
        assert left == right


def test_clamp_disabled_is_bit_identical(open_checkpoint):
    ordinary = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER)
    disabled = _noswap()
    left = open_checkpoint["state"].copy()
    right = open_checkpoint["state"].copy()
    for _ in range(8):
        left = ordinary.step(left)
        right = disabled.step(right)
    assert chc.canonical_state_bytes(left) == chc.canonical_state_bytes(right)


def test_qualified_two_cell_spatial_isolation(open_checkpoint):
    state = open_checkpoint["state"]
    center = open_checkpoint["entities"][open_checkpoint["focal_id"]].centroid
    partition, core, barrier = ns.core_and_collar(state.rho.shape, center)
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


def test_up_ref_zero_and_common_probe_standardization(open_checkpoint):
    source = open_checkpoint["state"].copy()
    source.N = source.N + np.arange(source.N.size).reshape(source.N.shape) / source.N.size
    reset = chc.bh.standardized_probe_start(source)
    assert np.all(reset.N == cc.N0)
    for field in ("rho", "U", "V", "c", "C", "uptake", "Mf"):
        assert np.array_equal(getattr(reset, field), getattr(source, field))
    isolated = _noswap(up_ref_zero=True)
    global_matched = DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
    assert isolated.up_ref_zero is True
    assert global_matched.up_ref_zero is True


def _fake_complete_world(seed: int) -> dict:
    first_stage = {
        feature: {"dose": 1.0, "order": -1.0, "interaction": 0.0}
        for feature in chc.FIRST_STAGE_SCALARS
    }
    first_stage["full_field"] = {
        "dose": {"vector": [1.0, 0.0]},
        "order": {"vector": [0.0, -1.0]},
        "interaction": {"vector": [0.0, 0.0]},
    }
    arm_contrasts = {
        arm: {
            "tracked": {"dose": 1.0, "order": -0.5, "interaction": 0.0},
            "fixed": {"dose": 1.0, "order": -0.5, "interaction": 0.0},
        }
        for arm in chc.ALL_ARMS
    }
    return {
        "seed": seed,
        "prehistory_eligible": True,
        "complete_block": True,
        "clone_checkpoint": {"valid": True},
        "branches": {
            name: {
                "posthistory_alive": True,
                "deep_valid": True,
                "complete_probe": True,
                "probe": {"sham_exact": True},
                "rows_that_must_never_count_as_replicates": list(range(100)),
            }
            for name in chc.HISTORY_NAMES
        },
        "first_stage_contrasts": first_stage,
        "arm_contrasts": arm_contrasts,
        "transport": {"dose": 0.0, "order": 0.0, "interaction": 0.0},
        "lam_plus_mediation": {
            condition: {"dose": -0.5, "order": 0.25, "interaction": 0.0}
            for condition in ("coupled", "isolated")
        },
    }


def test_world_level_factorial_aggregation():
    worlds = [_fake_complete_world(seed) for seed in range(4)]
    summary = chc.aggregate(worlds)
    assert summary["n_complete_valid_worlds"] == 4
    assert summary["feeding_contrasts"]["isolated"]["dose"]["n_worlds"] == 4
    assert summary["first_stage"]["mplus_mean"]["dose"]["n_worlds"] == 4


def test_no_target_or_branch_pseudoreplication():
    worlds = [_fake_complete_world(seed) for seed in range(4)]
    failed = _fake_complete_world(99)
    failed["complete_block"] = False
    for branch in failed["branches"].values():
        branch["complete_probe"] = False
    summary = chc.aggregate(worlds + [failed])
    assert summary["n_complete_valid_worlds"] == 4
    assert summary["counterfactual_branches_count_toward_n"] is False
    assert summary["feeding_contrasts"]["coupled"]["order"]["n_worlds"] == 4
    assert all(row["assigned"] == 5 for row in summary["survival_by_history"].values())


def test_fresh_namespace_manifest_and_runtime_guard():
    manifest = chc.load_and_validate_manifest()
    assert tuple(manifest["seeds"]) == chc.DEV_SEEDS
    assert manifest["namespace_audit"]["fresh_decimal_integer_audit_pass"] is True
    assert not (set(chc.DEV_SEEDS) & set(range(55001, 55025)))
    assert len(chc.DEV_SEEDS) == 24
    assert chc.execution_order(57001) == chc.execution_order(57001)
    for bad in (50002, 55001, 57000, 57025, 54001):
        with pytest.raises(ValueError):
            chc.run_world(bad, manifest)


def test_manifest_horizon_fixed_time_and_no_future_allocator_inputs():
    manifest = chc.load_and_validate_manifest()
    assert chc.sha256_file(chc.DEFAULT_MANIFEST) == chc.MANIFEST_SHA256
    assert chc.DEEP_STEPS == 1000
    assert chc.HORIZON == 40
    assert manifest["probe"]["primary_endpoint"] == "integrated tracked uptake through step 40"
    assert manifest["isolated"]["up_ref"] == 0
    assert manifest["isolated"]["focal_core_Mf_erased_standardized_grafted_or_replaced"] is False
    assert tuple(inspect.signature(chc.execution_order).parameters) == ("seed",)


def test_atomic_writer_reports_persisted_raw_digest(tmp_path):
    path = tmp_path / "result.json"
    announced = chc.atomic_write_json(path, {"line": "one\ntwo"})
    assert announced == chc.sha256_file(path)


def test_public_branch_payload_excludes_runtime_objects():
    sentinel = object()
    public = chc._branch_public({
        "state": sentinel,
        "tracker": sentinel,
        "patch": np.ones((2, 2)),
        "deep": {"state": sentinel, "region": np.ones((2, 2), bool), "entity": sentinel,
                 "material": {"M": 0.2}},
        "valid": True,
    })
    assert set(public["deep"]) == {"material"}
    json.dumps(public)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
