"""ACCESS-STRUCTURE-00 Phase 0.5 DEV-only operator qualification.

No prospective seed is accepted.  Active crossed feeding outcomes are never
computed here: the common feeding probe is run only on bit-identical no-op and
sham states to measure manipulation bias.  All other branches are assessed on
state fidelity, seams, short transients, tracker geometry, and viability.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import bijective_tracker as bt
from experiments.individuation import causal_confirm as cc
from experiments.individuation import material_tracer as mt
from experiments.individuation import nonmerging_confirm as nm
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation import turnover_diag_engine as diag_engine


HERE = Path(__file__).resolve().parent
DEV_RAW = HERE / "turnover_dev_raw.json"
SNAPSHOT_STEPS = (1, 5, 20, 40)
QUAL_HORIZON = max(SNAPSHOT_STEPS)
K = cc.K
GRID = cc.N * cc.N
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10


def _safe(value):
    if isinstance(value, dict):
        return {str(key): _safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def _mask(entity) -> np.ndarray:
    return cc.mask(entity)


def _centers_for_regions(state, regions: list[np.ndarray]) -> list[tuple[float, float]]:
    entities = detect(state, MCM_CONFIG.DET)
    centers = []
    for region in regions:
        entity = max(entities, key=lambda item: int((_mask(item) & region).sum()))
        centers.append(tuple(float(value) for value in entity.centroid))
    return centers


def _history_pair(raw_record: dict) -> dict:
    """Maximum fixed-range contrast in (dose, order); never reads future feeding."""
    dose = [float(value) for value in raw_record["dose"]]
    order = [float(value) for value in raw_record["order"]]
    dose_span = 2.0 * (cc.AMP_HI - cc.AMP_LO)
    order_span = 2.0 * (cc.AMP_HI - cc.AMP_LO)
    candidates = []
    for i in range(K):
        for j in range(i + 1, K):
            score = math.hypot((dose[i] - dose[j]) / dose_span, (order[i] - order[j]) / order_span)
            candidates.append((score, -i, -j, i, j))
    _, _, _, i, j = max(candidates)
    a, b = (i, j) if (dose[i], order[i], -i) >= (dose[j], order[j], -j) else (j, i)
    return {
        "rule": "max normalized Euclidean contrast in frozen written (dose,order); A is higher lexicographic (dose,order)",
        "A": int(a),
        "B": int(b),
        "history_A": {"dose": dose[a], "order": order[a]},
        "history_B": {"dose": dose[b], "order": order[b]},
        "future_feeding_used": False,
    }


def _build_no_history_world(seed: int, deep_step: int):
    """On-manifold standard reference: same seed/law/time, no phase drive."""
    engine = cc.build(cc.MEM_INTACT)
    state = cc.seed_world(seed)
    for _ in range(cc.WARM):
        state = engine.step(state)
    targets = cc.pick(sorted(detect(state, MCM_CONFIG.DET), key=lambda entity: -entity.size))
    if len(targets) < K:
        raise RuntimeError("no-history reconstruction lost initial eligibility")
    initial_centers = [entity.centroid for entity in targets]
    for _ in range(2 * cc.PHASE + cc.SETTLE):
        state = engine.step(state)
    regions, _ = cc.region_masks(state, initial_centers)
    state, _ = mt.seed_tracers(state, regions)
    for _ in range(deep_step):
        state = engine.step(state)
    return state


def _standard_reference(state) -> tuple[object, np.ndarray]:
    """Median-area viable component, with deterministic geometric tie breaks."""
    entities = [
        entity for entity in detect(state, MCM_CONFIG.DET)
        if 4 <= int(entity.size) < int(nm.COVER_CAP * GRID)
    ]
    if not entities:
        raise RuntimeError("no on-manifold reference body at the matched deep time")
    entities.sort(key=lambda entity: (int(entity.size), float(entity.centroid[0]), float(entity.centroid[1])))
    entity = entities[(len(entities) - 1) // 2]
    return entity, _mask(entity)


def _state_views(state) -> dict[str, np.ndarray]:
    rho_safe = np.maximum(state.rho, 1e-12)
    memory = state.Mf / rho_safe[None]
    return {
        "rho": state.rho,
        "u": state.U / rho_safe,
        "v": state.V / rho_safe,
        "c": state.c,
        "N": state.N,
        "m_plus": np.tanh(memory[0] + memory[1]),
        "uptake_previous_readout": state.uptake,
    }


def _band_delta(reference, candidate, partition: ops.StatePartition) -> dict:
    bands = ops.concentric_bands(partition)
    views_ref = _state_views(reference)
    views_candidate = _state_views(candidate)
    result = {}
    for band_name, mask in bands.items():
        result[band_name] = {}
        for field in views_ref:
            delta = views_candidate[field][mask] - views_ref[field][mask]
            result[band_name][field] = {
                "rms": float(np.sqrt(np.mean(delta * delta))) if delta.size else 0.0,
                "max_abs": float(np.max(np.abs(delta))) if delta.size else 0.0,
            }
    return result


def _seam(state, partition: ops.StatePartition) -> dict:
    views = _state_views(state)
    result = {}
    for name, values in views.items():
        jumps = []
        for axis in (0, 1):
            for shift in (-1, 1):
                outside_neighbor = partition.core & ~np.roll(partition.core, shift, axis=axis)
                if outside_neighbor.any():
                    jumps.append(np.abs(values[outside_neighbor] - np.roll(values, shift, axis=axis)[outside_neighbor]))
        joined = np.concatenate(jumps) if jumps else np.zeros(0)
        result[name] = {
            "mean_abs": float(joined.mean()) if joined.size else 0.0,
            "max_abs": float(joined.max()) if joined.size else 0.0,
        }
    return result


def _totals(state) -> dict:
    result = {}
    for field in ops.STATE_FIELDS:
        values = getattr(state, field)
        result[field] = _safe(values.sum(axis=(-2, -1)))
    return result


def _total_delta(reference, candidate) -> dict:
    before = _totals(reference)
    after = _totals(candidate)
    result = {}
    for field in before:
        a = np.asarray(before[field], dtype=float)
        b = np.asarray(after[field], dtype=float)
        delta = b - a
        result[field] = {
            "delta": _safe(delta),
            "max_abs": float(np.max(np.abs(delta))),
            "within_float64_criterion": bool(
                np.all(np.abs(delta) <= NUMERIC_ATOL + NUMERIC_RTOL * np.abs(a))
            ),
        }
    return result


def _pair_total_delta(a0, b0, a1, b1) -> dict:
    result = {}
    for field in ops.STATE_FIELDS:
        before = getattr(a0, field).sum(axis=(-2, -1)) + getattr(b0, field).sum(axis=(-2, -1))
        after = getattr(a1, field).sum(axis=(-2, -1)) + getattr(b1, field).sum(axis=(-2, -1))
        delta = after - before
        result[field] = {
            "max_abs": float(np.max(np.abs(delta))),
            "within_float64_criterion": bool(
                np.all(np.abs(delta) <= NUMERIC_ATOL + NUMERIC_RTOL * np.abs(before))
            ),
        }
    return result


def _cohort_error(state, appended_tracers: int = K) -> float:
    base_count = state.C.shape[0] - appended_tracers
    return float(np.max(np.abs(state.C[:base_count].sum(axis=0) - state.rho)))


def _geometry(state, expected_mask: np.ndarray) -> dict:
    entities = detect(state, MCM_CONFIG.DET)
    if not entities:
        return {"detected": False, "overlap_fraction": 0.0, "iou": 0.0}
    entity = max(entities, key=lambda item: int((_mask(item) & expected_mask).sum()))
    mask = _mask(entity)
    overlap = int((mask & expected_mask).sum())
    union = int((mask | expected_mask).sum())
    return {
        "detected": True,
        "overlap_fraction": float(overlap / max(1, int(expected_mask.sum()))),
        "iou": float(overlap / max(1, union)),
        "size": int(mask.sum()),
        "mass": float(state.rho[mask].sum()),
        "centroid": [float(value) for value in entity.centroid],
        "rg": float(entity.rg),
        "coverage": float(mask.sum() / GRID),
    }


def _tracker_seed_masks(state, expected_target: np.ndarray) -> tuple[list[np.ndarray], dict]:
    entities = detect(state, MCM_CONFIG.DET)
    if not entities:
        return [], {"reason": "no_components"}
    target_index = max(range(len(entities)), key=lambda index: int((_mask(entities[index]) & expected_target).sum()))
    target_mask = _mask(entities[target_index])
    overlap = float((target_mask & expected_target).sum() / max(1, expected_target.sum()))
    others = [
        (index, entity) for index, entity in enumerate(entities)
        if index != target_index
    ]
    others.sort(key=lambda item: (-int(item[1].size), float(item[1].centroid[0]), float(item[1].centroid[1])))
    chosen = [target_mask] + [_mask(entity) for _, entity in others[: K - 1]]
    return chosen, {"target_overlap_fraction": overlap, "n_detected": len(entities)}


def _simulate(state, expected_target: np.ndarray, engine) -> dict:
    seed_masks, seed_audit = _tracker_seed_masks(state, expected_target)
    if len(seed_masks) < K:
        return {
            "valid": False,
            "seed_audit": seed_audit,
            "reason": "fewer_than_three_post_surgery_components",
            "snapshots": {0: state.copy()},
            "final_state": state.copy(),
        }
    tracker = bt.BijectiveTracker(theta=nm.THETA)
    tracker.seed(seed_masks, 0)
    current = state.copy()
    snapshots = {0: current.copy()}
    events = {}
    max_coverage = 0.0
    min_distinct = K
    finite = True
    uptake_present_steps = 0
    for step in range(1, QUAL_HORIZON + 1):
        current = engine.step(current)
        finite = finite and all(np.isfinite(getattr(current, field)).all() for field in ops.STATE_FIELDS)
        uptake_present_steps += int(bool(np.any(current.uptake > 0.0)))
        entities = detect(current, MCM_CONFIG.DET)
        masks = [_mask(entity) for entity in entities]
        for track_id, status in tracker.update(masks, step).items():
            events.setdefault(str(track_id), [step, status])
        max_coverage = max(max_coverage, max((mask.sum() for mask in masks), default=0) / GRID)
        min_distinct = min(min_distinct, len(tracker.alive()))
        if step in SNAPSHOT_STEPS:
            snapshots[step] = current.copy()
    summary = tracker.summary()
    valid = bool(
        finite
        and summary["alive"] == K
        and max_coverage < nm.COVER_CAP
        and min_distinct == K
    )
    return {
        "valid": valid,
        "seed_audit": seed_audit,
        "tracker": summary,
        "events": events,
        "max_coverage": float(max_coverage),
        "min_distinct": int(min_distinct),
        "finite": bool(finite),
        "uptake_endpoint_present_all_steps": bool(uptake_present_steps == QUAL_HORIZON),
        "snapshots": snapshots,
        "final_state": current,
    }


def _branch_metrics(
    baseline,
    branch,
    partition: ops.StatePartition,
    expected_target: np.ndarray,
    baseline_run: dict,
    engine,
) -> dict:
    branch_run = _simulate(branch, expected_target, engine)
    seam_before = _seam(baseline, partition)
    seam_after = _seam(branch, partition)
    seam_change = {}
    for field in seam_before:
        before = seam_before[field]["mean_abs"]
        after = seam_after[field]["mean_abs"]
        seam_change[field] = {
            "before_mean_abs": before,
            "after_mean_abs": after,
            "increment": float(after - before),
            "ratio": float(after / before) if before > 0.0 else None,
        }
    transient = {}
    if "snapshots" in branch_run and "snapshots" in baseline_run:
        for step in SNAPSHOT_STEPS:
            if step in branch_run["snapshots"] and step in baseline_run["snapshots"]:
                transient[str(step)] = _band_delta(
                    baseline_run["snapshots"][step], branch_run["snapshots"][step], partition
                )
    clean_run = {key: value for key, value in branch_run.items() if key not in ("snapshots", "final_state")}
    immediate = _band_delta(baseline, branch, partition)
    non_target_max = max(
        metric["max_abs"]
        for band in ("H_d1", "E_d2_3", "E_d4_6", "E_far")
        for metric in immediate[band].values()
    )
    return {
        "state_hash": ops.state_sha256(branch),
        "scheduler_step_delta": int(branch.step - baseline.step),
        "immediate_band_change": immediate,
        "immediate_non_target_max_abs": float(non_target_max),
        "total_delta_vs_recipient": _total_delta(baseline, branch),
        "cohort_base_sum_minus_rho_max_abs": _cohort_error(branch),
        "seam": seam_change,
        "geometry": _geometry(branch, expected_target),
        "short_continuation": clean_run,
        "transient_band_change_vs_recipient_continuation": transient,
    }


def _advance(state, engine, steps: int):
    current = state.copy()
    for _ in range(steps):
        current = engine.step(current)
    return current


def _max_error(errors: dict) -> float:
    values = [abs(float(value)) for value in errors.values()]
    return max(values, default=0.0)


def _qualify_world(raw_record: dict) -> dict:
    seed = ops.require_dev_seed(raw_record["seed"])
    deep_step = int(raw_record["deep"]["step"])
    base = tdd.to_S0(seed)
    intact = tdd.run_to(base["eng"], base["S0"], base["reg0"], deep_step)
    state = intact["S"]
    regions = intact["regs"]
    centers = _centers_for_regions(state, regions)
    partitions = [ops.partition_state(state.rho.shape, center) for center in centers]
    coverage = [bool(np.all(~region | partition.core)) for region, partition in zip(regions, partitions)]
    pair = _history_pair(raw_record)
    index_a, index_b = pair["A"], pair["B"]
    part_a, part_b = partitions[index_a], partitions[index_b]
    region_a, region_b = regions[index_a], regions[index_b]

    no_history = _build_no_history_world(seed, deep_step)
    reference_entity, reference_region = _standard_reference(no_history)
    reference_center = tuple(float(value) for value in reference_entity.centroid)
    reference_part = ops.partition_state(no_history.rho.shape, reference_center)
    reference_coverage = bool(np.all(~reference_region | reference_part.core))

    no_op = ops.no_op_continuation(state)
    restored = ops.deserialize_state(ops.serialize_state(state))
    same_a = ops.same_source_reinsert(state, part_a)
    transform_a = ops.coordinate_transform_sham(state, part_a)
    matched_a, matched_a_recip, _ = ops.exchange_cores(state, state, part_a, part_a)
    cb_ea, ca_eb, cross_record = ops.exchange_cores(state, state, part_a, part_b)
    c0_ea, ca_e0, reset_record_a = ops.paired_environment_body_standardization(
        state, no_history, part_a, reference_part
    )
    c0_eb, cb_e0, reset_record_b = ops.paired_environment_body_standardization(
        state, no_history, part_b, reference_part
    )

    no_op_10 = _advance(no_op, base["eng"], 10)
    roundtrip_10 = _advance(restored, base["eng"], 10)
    sham_feed = nm.measure(transform_a, centers, base["eng"], None)
    noop_feed = nm.measure(no_op, centers, base["eng"], None)
    sham_bias = {
        "tracked_max_abs": float(np.max(np.abs(np.asarray(sham_feed["tracked"]) - np.asarray(noop_feed["tracked"])))),
        "fixed_max_abs": float(np.max(np.abs(np.asarray(sham_feed["fixed"]) - np.asarray(noop_feed["fixed"])))),
        "statuses_equal": bool(sham_feed["statuses"] == noop_feed["statuses"]),
        "branch_valid_equal": bool(sham_feed["branch_valid"] == noop_feed["branch_valid"]),
        "active_crossed_feeding_evaluated": False,
    }

    original_run_a = _simulate(state, region_a, base["eng"])
    original_run_b = _simulate(state, region_b, base["eng"])
    nohistory_run = _simulate(no_history, reference_region, base["eng"])

    shift_ab = cross_record.shift_a_to_b
    shift_ba = cross_record.shift_b_to_a
    expected_a_at_b = np.roll(region_a, shift_ab, axis=(-2, -1))
    expected_b_at_a = np.roll(region_b, shift_ba, axis=(-2, -1))
    expected_c0_at_a = np.roll(reference_region, reset_record_a.shift_b_to_a, axis=(-2, -1))
    expected_a_at_0 = np.roll(region_a, reset_record_a.shift_a_to_b, axis=(-2, -1))
    expected_c0_at_b = np.roll(reference_region, reset_record_b.shift_b_to_a, axis=(-2, -1))
    expected_b_at_0 = np.roll(region_b, reset_record_b.shift_a_to_b, axis=(-2, -1))

    upref_engine = diag_engine.DiagEngine(
        MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, up_ref_zero=True
    )
    readout_mem = replace(tdd.MEM, lam_plus=0.0)
    readout_engine = cc.build(readout_mem)
    upref_run = _simulate(state, region_a, upref_engine)
    readout_run = _simulate(state, region_a, readout_engine)
    ablations = {
        "global_up_ref": {
            "definition": "up_ref is set to 0 only inside each future memory-writing update",
            "initial_state_changed": False,
            "up_ref_zero_flag": bool(upref_engine.up_ref_zero),
            "short_continuation": {k: v for k, v in upref_run.items() if k not in ("snapshots", "final_state")},
        },
        "readout": {
            "definition": "lam_plus=0 removes m_plus modulation of feeding; lam_minus remains frozen",
            "lam_plus": float(readout_mem.lam_plus),
            "lam_minus": float(readout_mem.lam_minus),
            "primary_uptake_endpoint_disabled": False,
            "short_continuation": {k: v for k, v in readout_run.items() if k not in ("snapshots", "final_state")},
        },
    }

    world = {
        "seed": seed,
        "feasible": True,
        "deep_step": deep_step,
        "state_hash": ops.state_sha256(state),
        "scheduler_step": int(state.step),
        "history_pair": pair,
        "centers": centers,
        "body_inside_C": coverage,
        "C_blocks_pairwise_disjoint": bool(
            all(not (partitions[i].core & partitions[j].core).any() for i in range(K) for j in range(i + 1, K))
        ),
        "reference": {
            "kind": "same seed/law/time no-phase-drive on-manifold world; median-area detected component",
            "center": reference_center,
            "body_inside_C": reference_coverage,
            "state_hash": ops.state_sha256(no_history),
            "literal_zero_or_blank": False,
        },
        "exact_controls": {
            "no_op_max_abs": _max_error(ops.exact_state_errors(state, no_op)),
            "serialization_roundtrip_max_abs": _max_error(ops.exact_state_errors(state, restored)),
            "serialization_10_step_continuation_max_abs": _max_error(ops.exact_state_errors(no_op_10, roundtrip_10)),
            "same_source_reinsert_max_abs": _max_error(ops.exact_state_errors(state, same_a)),
            "coordinate_transform_sham_max_abs": _max_error(ops.exact_state_errors(state, transform_a)),
            "matched_CE_exchange_kernel_max_abs": max(
                _max_error(ops.exact_state_errors(state, matched_a)),
                _max_error(ops.exact_state_errors(state, matched_a_recip)),
            ),
            "sham_future_feeding_bias": sham_bias,
        },
        "operations": {
            "matched_C_A_E_A": {
                "state_hash": ops.state_sha256(state),
                "operator": "unmanipulated matched arm plus exact exchange-kernel sham",
            },
            "matched_C_B_E_B": {
                "state_hash": ops.state_sha256(state),
                "operator": "unmanipulated matched arm plus exact exchange-kernel sham",
            },
            "crossed_reciprocal_A_B": {
                "operator_record": _safe(cross_record.__dict__),
                "pair_total_delta": _pair_total_delta(state, state, cb_ea, ca_eb),
                "C_B_E_A": _branch_metrics(state, cb_ea, part_a, expected_b_at_a, original_run_a, base["eng"]),
                "C_A_E_B": _branch_metrics(state, ca_eb, part_b, expected_a_at_b, original_run_b, base["eng"]),
                "environment_standardization_role": "same exact state as crossed arm; no redundant operator",
            },
            "paired_no_history_exchange_A": {
                "operator_record": _safe(reset_record_a.__dict__),
                "pair_total_delta": _pair_total_delta(state, no_history, c0_ea, ca_e0),
                "C_0_E_A_body_core_standardized": _branch_metrics(
                    state, c0_ea, part_a, expected_c0_at_a, original_run_a, base["eng"]
                ),
                "C_A_E_0_environment_reset": _branch_metrics(
                    no_history, ca_e0, reference_part, expected_a_at_0, nohistory_run, base["eng"]
                ),
            },
            "paired_no_history_exchange_B": {
                "operator_record": _safe(reset_record_b.__dict__),
                "pair_total_delta": _pair_total_delta(state, no_history, c0_eb, cb_e0),
                "C_0_E_B_body_core_standardized": _branch_metrics(
                    state, c0_eb, part_b, expected_c0_at_b, original_run_b, base["eng"]
                ),
                "C_B_E_0_environment_reset": _branch_metrics(
                    no_history, cb_e0, reference_part, expected_b_at_0, nohistory_run, base["eng"]
                ),
            },
        },
        "ablations": ablations,
        "dynamical_phase_inventory": {
            "persistent": ["rho", "U", "V", "c", "N", "C", "Mf", "uptake(previous readout)", "step"],
            "derived_each_step": ["face fluxes", "laplacians", "concentrations", "sigma", "m", "m_plus", "m_minus", "up_ref"],
            "persistent_velocity_or_momentum": None,
            "persistent_flux_gradient_or_previous_state_buffer": None,
            "persistent_rng_state": None,
            "tracker_state": "external observer; re-seeded from outcome-independent post-surgery geometry for qualification",
            "scheduler_step_preserved": True,
        },
    }
    return world


def _operation_records(worlds: list[dict]) -> Iterable[dict]:
    for world in worlds:
        if not world.get("feasible"):
            continue
        for operation_name, operation in world["operations"].items():
            if operation_name.startswith("matched"):
                continue
            for arm_name, arm in operation.items():
                if isinstance(arm, dict) and "short_continuation" in arm:
                    yield {
                        "seed": world["seed"],
                        "operation": operation_name,
                        "arm": arm_name,
                        "arm_record": arm,
                    }


def _summarize(worlds: list[dict]) -> dict:
    feasible = [world for world in worlds if world.get("feasible")]
    records = list(_operation_records(worlds))
    exact_fields = [
        "no_op_max_abs",
        "serialization_roundtrip_max_abs",
        "serialization_10_step_continuation_max_abs",
        "same_source_reinsert_max_abs",
        "coordinate_transform_sham_max_abs",
        "matched_CE_exchange_kernel_max_abs",
    ]
    exact_max = {
        field: max((world["exact_controls"][field] for world in feasible), default=None)
        for field in exact_fields
    }
    sham_bias = max(
        (
            max(
                world["exact_controls"]["sham_future_feeding_bias"]["tracked_max_abs"],
                world["exact_controls"]["sham_future_feeding_bias"]["fixed_max_abs"],
            )
            for world in feasible
        ),
        default=None,
    )
    valid_by_arm = {}
    seam_ratios = []
    outside_errors = []
    pair_conservation = []
    branch_total_deltas: dict[str, list[float]] = {field: [] for field in ops.STATE_FIELDS}
    cohort_errors = []
    geometry_overlaps = []
    halo_transient_rms: dict[int, list[float]] = {step: [] for step in SNAPSHOT_STEPS}
    for record in records:
        key = f"{record['operation']}::{record['arm']}"
        arm = record["arm_record"]
        valid_by_arm.setdefault(key, []).append(bool(arm["short_continuation"]["valid"]))
        outside_errors.append(float(arm["immediate_non_target_max_abs"]))
        cohort_errors.append(float(arm["cohort_base_sum_minus_rho_max_abs"]))
        geometry_overlaps.append(float(arm["geometry"].get("overlap_fraction", 0.0)))
        for field, total in arm["total_delta_vs_recipient"].items():
            branch_total_deltas[field].append(float(total["max_abs"]))
        for step, transient in arm["transient_band_change_vs_recipient_continuation"].items():
            halo_transient_rms[int(step)].extend(
                float(metric["rms"]) for metric in transient["H_d1"].values()
            )
        seam_ratios.extend(
            value["ratio"] for value in arm["seam"].values() if value["ratio"] is not None
        )
    for world in feasible:
        for operation in world["operations"].values():
            if "pair_total_delta" in operation:
                pair_conservation.extend(
                    field["max_abs"] for field in operation["pair_total_delta"].values()
                )
    all_valid = all(all(values) for values in valid_by_arm.values()) if valid_by_arm else False
    all_exact = bool(feasible) and all(value == 0.0 for value in exact_max.values())
    all_bodies_covered = bool(feasible) and all(all(world["body_inside_C"]) for world in feasible)
    all_references_covered = bool(feasible) and all(world["reference"]["body_inside_C"] for world in feasible)
    sensitivity = {
        str(multiplier): int(sum(ratio <= multiplier for ratio in seam_ratios))
        for multiplier in (1.25, 1.5, 2.0, 3.0, 5.0)
    }
    total_seams = len(seam_ratios)
    blockers = []
    if len(feasible) < 4:
        blockers.append("fewer than four already-feasible DEV worlds reconstructed")
    if not all_exact:
        blockers.append("exact no-op/serialization/sham equivalence failed")
    if not all_bodies_covered or not all_references_covered:
        blockers.append("radius-10 C failed to contain a source body")
    if max(outside_errors, default=0.0) != 0.0:
        blockers.append("an operator changed H/E at surgery")
    if not all_valid:
        blockers.append("at least one active operator failed 40-step tracker/viability qualification")
    if any(max(values, default=0.0) > NUMERIC_ATOL for values in branch_total_deltas.values()):
        blockers.append("paired exchanges conserve totals only across reciprocal branches; individual-arm balance is not matched")
    if max(seam_ratios, default=0.0) > 1.25:
        blockers.append("active boundary seams exceed the candidate 1.25x natural-boundary engineering envelope")
    # Even if mechanics pass, this DEV set is too small and the seam envelope is
    # fitted on these same worlds.  That requires a human-reviewed preregistration,
    # not an automatic prospective GO.
    recommendation = "REVISE"
    blockers.append("seam envelope and practical/equivalence margins remain unsealed design quantities")
    return {
        "n_open_dev_worlds": len(worlds),
        "n_deep_feasible_worlds": len(feasible),
        "exact_control_max_abs": exact_max,
        "sham_future_feeding_bias_max_abs": sham_bias,
        "all_source_bodies_inside_C": all_bodies_covered,
        "all_reference_bodies_inside_C": all_references_covered,
        "immediate_H_or_E_change_max_abs": max(outside_errors, default=None),
        "paired_exchange_conservation_max_abs": max(pair_conservation, default=None),
        "individual_arm_total_delta_max_abs_by_field": {
            field: max(values, default=None) for field, values in branch_total_deltas.items()
        },
        "individual_arm_balance_matched": False,
        "cohort_base_sum_minus_rho_max_abs": max(cohort_errors, default=None),
        "post_surgery_geometry_overlap_fraction_min": min(geometry_overlaps, default=None),
        "H_d1_transient_rms_max_by_step": {
            str(step): max(values, default=None) for step, values in halo_transient_rms.items()
        },
        "valid_40_step_counts_by_arm": {
            key: {"valid": int(sum(values)), "total": len(values)} for key, values in valid_by_arm.items()
        },
        "all_active_operator_arms_40_step_valid": all_valid,
        "seam_ratio_DEV": {
            "n_field_arm_world_values": total_seams,
            "max_observed": max(seam_ratios, default=None),
            "candidate_unsealed_engineering_envelope": "post/pre natural seam ratio <= 1.25 in every causal field",
            "sensitivity_pass_counts": sensitivity,
            "warning": "candidate is based on the exact sham/no-op natural ratio of 1; it is not sealed",
        },
        "hypothesis_outcomes_evaluated": False,
        "active_crossed_future_feeding_evaluated": False,
        "recommendation": recommendation,
        "blockers_or_required_freezes": blockers,
    }


def run(seeds: list[int]) -> dict:
    seeds = [ops.require_dev_seed(seed) for seed in seeds]
    if len(seeds) != len(set(seeds)):
        raise ValueError("duplicate DEV seeds are not permitted")
    raw_by_seed = {int(record["seed"]): record for record in json.loads(DEV_RAW.read_text())}
    worlds = []
    for seed in seeds:
        raw = raw_by_seed[seed]
        if not raw.get("feasible"):
            worlds.append({
                "seed": seed,
                "feasible": False,
                "reason": raw.get("deep_reason") or ("ineligible" if not raw.get("eligible") else "not_deep_feasible"),
                "operator_executed": False,
            })
            print(f"seed {seed}: existing DEV disposition, no operator ({worlds[-1]['reason']})", flush=True)
            continue
        print(f"seed {seed}: reconstruct and qualify DEV operators", flush=True)
        worlds.append(_qualify_world(raw))
    result = {
        "schema": "ACCESS-STRUCTURE-00-PHASE05-DEV-QUALIFICATION-v1",
        "mode": "DEV_ONLY_ALREADY_OPEN_SEEDS",
        "seeds_requested": seeds,
        "allowed_seed_namespace": list(ops.DEV_SEEDS),
        "new_seed_or_prospective_family_opened": False,
        "primary_scientific_question_answered": False,
        "core_radius": ops.CORE_RADIUS,
        "halo_width": ops.HALO_WIDTH,
        "qualification_horizon": QUAL_HORIZON,
        "worlds": worlds,
    }
    result["summary"] = _summarize(worlds)
    return _safe(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    args = parser.parse_args()
    result = run(args.seeds)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
