"""ACCESS-STRUCTURE-00 Phase 0.6A DEV-only operator qualification.

The runner accepts only the already-open seeds 50001--50010.  It re-runs the
Phase 0.5 engineering audit, localizes the hard-cut failure, and evaluates the
complete four-configuration/two-family grid frozen in
ACCESS_STRUCTURE_00_PHASE06A_OPERATOR_SPEC.md.  It never measures active-arm
future feeding and cannot answer the scientific storage-location question.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from edlab.experiments.sc_iom.engine import IOMState
from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import access_structure_dev_qualification as p05
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import bijective_tracker as bt
from experiments.individuation import causal_confirm as cc
from experiments.individuation import nonmerging_confirm as nm
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation.turnover_scope_features import memory_features


HERE = Path(__file__).resolve().parent
DEV_RAW = HERE / "turnover_dev_raw.json"
SNAPSHOT_STEPS = (0, 1, 5, 10, 20, 40)
QUAL_HORIZON = max(SNAPSHOT_STEPS)
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10
PAYLOAD_PROJECTION_MIN = 0.50
PAYLOAD_BODY_COVERAGE_MIN = 0.90
SEAM_RATIO_ENVELOPE = 1.25
SEAM_SENSITIVITY = (1.25, 1.5, 2.0, 3.0, 5.0)
K = cc.K
GRID = cc.N * cc.N


def _safe(value):
    return p05._safe(value)


def _mask(entity) -> np.ndarray:
    return p05._mask(entity)


def _translated_state(state: IOMState, shift: tuple[int, int]) -> IOMState:
    values = {
        field: np.roll(getattr(state, field), shift, axis=(-2, -1))
        for field in ops.STATE_FIELDS
    }
    return IOMState(step=state.step, **values)


def _views(state: IOMState) -> dict[str, np.ndarray]:
    rho = np.maximum(state.rho, 1e-12)
    m = state.Mf / rho[None]
    return {
        "rho": state.rho,
        "u": state.U / rho,
        "v": state.V / rho,
        "c": state.c,
        "N": state.N,
        "m1": m[0],
        "m2": m[1],
        "m_plus": np.tanh(m[0] + m[1]),
        "uptake_previous_readout": state.uptake,
    }


def _simulate(state: IOMState, expected_target: np.ndarray, engine) -> dict:
    seed_masks, seed_audit = p05._tracker_seed_masks(state, expected_target)
    if len(seed_masks) < K:
        return {
            "valid": False,
            "reason": "fewer_than_three_post_surgery_components",
            "seed_audit": seed_audit,
            "snapshots": {0: state.copy()},
        }
    tracker = bt.BijectiveTracker(theta=nm.THETA)
    tracker.seed(seed_masks, 0)
    current = state.copy()
    snapshots = {0: current.copy()}
    events = {}
    finite = True
    max_coverage = 0.0
    min_distinct = K
    for step in range(1, QUAL_HORIZON + 1):
        current = engine.step(current)
        finite = finite and all(np.isfinite(getattr(current, field)).all() for field in ops.STATE_FIELDS)
        entities = detect(current, MCM_CONFIG.DET)
        masks = [_mask(entity) for entity in entities]
        for track_id, status in tracker.update(masks, step).items():
            events.setdefault(str(track_id), [step, status])
        max_coverage = max(max_coverage, max((item.sum() for item in masks), default=0) / GRID)
        min_distinct = min(min_distinct, len(tracker.alive()))
        if step in SNAPSHOT_STEPS:
            snapshots[step] = current.copy()
    summary = tracker.summary()
    return {
        "valid": bool(
            finite
            and summary["alive"] == K
            and max_coverage < nm.COVER_CAP
            and min_distinct == K
        ),
        "seed_audit": seed_audit,
        "tracker": summary,
        "events": events,
        "finite": bool(finite),
        "max_coverage": float(max_coverage),
        "min_distinct": int(min_distinct),
        "snapshots": snapshots,
    }


def _clean_run(run: dict) -> dict:
    return {key: value for key, value in run.items() if key != "snapshots"}


def _band_change(reference: IOMState, candidate: IOMState, bands: dict[str, np.ndarray]) -> dict:
    before = _views(reference)
    after = _views(candidate)
    result = {}
    for band_name, mask in bands.items():
        result[band_name] = {}
        for field in before:
            delta = after[field][mask] - before[field][mask]
            result[band_name][field] = {
                "rms": float(np.sqrt(np.mean(delta * delta))) if delta.size else 0.0,
                "max_abs": float(np.max(np.abs(delta))) if delta.size else 0.0,
            }
    return result


def _transient_bands(baseline_run: dict, branch_run: dict, bands: dict[str, np.ndarray]) -> dict:
    result = {}
    for step in SNAPSHOT_STEPS:
        if step in baseline_run["snapshots"] and step in branch_run["snapshots"]:
            result[str(step)] = _band_change(
                baseline_run["snapshots"][step], branch_run["snapshots"][step], bands
            )
    return result


def _interface_faces(weight: np.ndarray) -> list[tuple[int, np.ndarray]]:
    faces = []
    for axis in (0, 1):
        changed = np.abs(weight - np.roll(weight, -1, axis=axis)) > 1e-15
        if changed.any():
            faces.append((axis, changed))
    return faces


def _interface_audit(
    recipient: IOMState,
    candidate: IOMState,
    donor_shifted: IOMState,
    weight: np.ndarray,
    engine,
) -> dict:
    faces = _interface_faces(weight)
    rec_views = _views(recipient)
    can_views = _views(candidate)
    don_views = _views(donor_shifted)
    fields = {}
    for field in rec_views:
        natural = []
        after = []
        donor = []
        for axis, face in faces:
            natural.append(np.abs(rec_views[field] - np.roll(rec_views[field], -1, axis=axis))[face])
            after.append(np.abs(can_views[field] - np.roll(can_views[field], -1, axis=axis))[face])
            donor.append(np.abs(don_views[field] - np.roll(don_views[field], -1, axis=axis))[face])
        nat = np.concatenate(natural) if natural else np.zeros(0)
        aft = np.concatenate(after) if after else np.zeros(0)
        don = np.concatenate(donor) if donor else np.zeros(0)
        before_mean = float(nat.mean()) if nat.size else 0.0
        after_mean = float(aft.mean()) if aft.size else 0.0
        fields[field] = {
            "recipient_natural_mean_abs": before_mean,
            "candidate_mean_abs": after_mean,
            "donor_natural_mean_abs": float(don.mean()) if don.size else 0.0,
            "candidate_to_recipient_ratio": float(after_mean / before_mean) if before_mean > 0.0 else None,
            "candidate_max_abs": float(aft.max()) if aft.size else 0.0,
        }

    flux = {}
    for axis, face in faces:
        natural_flux = engine._face_flux(recipient.rho, recipient.c, axis)
        candidate_flux = engine._face_flux(candidate.rho, candidate.c, axis)
        delta = candidate_flux[face] - natural_flux[face]
        denom = float(np.sqrt(np.mean(natural_flux[face] ** 2))) if face.any() else 0.0
        rms = float(np.sqrt(np.mean(delta * delta))) if delta.size else 0.0
        flux[f"axis_{axis}"] = {
            "delta_rms": rms,
            "delta_max_abs": float(np.max(np.abs(delta))) if delta.size else 0.0,
            "natural_rms": denom,
            "relative_rms": float(rms / denom) if denom > 0.0 else None,
        }
    return {"n_faces": int(sum(mask.sum() for _, mask in faces)), "fields": fields, "flux": flux}


def _outer_seam_audit(recipient: IOMState, candidate: IOMState, partition: ops.StatePartition) -> dict:
    before = p05._seam(recipient, partition)
    after = p05._seam(candidate, partition)
    result = {}
    for field in before:
        b = before[field]["mean_abs"]
        a = after[field]["mean_abs"]
        result[field] = {
            "before_mean_abs": b,
            "after_mean_abs": a,
            "ratio": float(a / b) if b > 0.0 else None,
        }
    return result


def _array_totals(state: IOMState, mask: np.ndarray) -> dict:
    result = {}
    for field in ops.STATE_FIELDS:
        values = getattr(state, field)[..., mask]
        result[field] = _safe(values.sum(axis=-1))
    return result


def _energy_proxy(state: IOMState, mask: np.ndarray) -> dict:
    # The engine has no energy state or Hamiltonian.  These frozen diagnostics
    # quantify bulk field magnitude and local gradient magnitude without
    # pretending either is conserved.
    bulk = 0.5 * (state.c * state.c + state.N * state.N)
    gradient = np.zeros_like(state.c)
    for field in (state.c, state.N):
        for axis in (0, 1):
            delta = np.roll(field, -1, axis=axis) - field
            gradient += 0.5 * delta * delta
    return {
        "engine_energy_variable_exists": False,
        "bulk_cN_l2_proxy": float(bulk[mask].sum()),
        "gradient_cN_proxy": float(gradient[mask].sum()),
    }


def _body_state(state: IOMState, mask: np.ndarray) -> dict:
    if not mask.any():
        return {"cells": 0}
    rho = np.maximum(state.rho[mask], 1e-12)
    return {
        "cells": int(mask.sum()),
        "mass": float(state.rho[mask].sum()),
        "rho_mean": float(state.rho[mask].mean()),
        "rho_std": float(state.rho[mask].std()),
        "u_mean": float((state.U[mask] / rho).mean()),
        "v_mean": float((state.V[mask] / rho).mean()),
        "N_mean": float(state.N[mask].mean()),
        "c_mean": float(state.c[mask].mean()),
    }


def _balance_ledger(
    recipient: IOMState,
    candidate: IOMState,
    partition: ops.StatePartition,
    expected_donor_mask: np.ndarray,
) -> dict:
    regions = {
        "C": partition.core,
        "H": partition.halo,
        "E": partition.environment,
    }
    regional = {}
    for name, mask in regions.items():
        before = _array_totals(recipient, mask)
        after = _array_totals(candidate, mask)
        delta = {}
        for field in before:
            delta[field] = _safe(np.asarray(after[field], dtype=float) - np.asarray(before[field], dtype=float))
        regional[name] = {
            "before": before,
            "after": after,
            "delta": delta,
            "environmental_energy_proxy_before": _energy_proxy(recipient, mask),
            "environmental_energy_proxy_after": _energy_proxy(candidate, mask),
        }
    global_before = _array_totals(recipient, np.ones_like(partition.core, dtype=bool))
    global_after = _array_totals(candidate, np.ones_like(partition.core, dtype=bool))
    global_delta = {}
    criterion = {}
    for field in global_before:
        before = np.asarray(global_before[field], dtype=float)
        delta = np.asarray(global_after[field], dtype=float) - before
        global_delta[field] = _safe(delta)
        criterion[field] = bool(np.all(np.abs(delta) <= NUMERIC_ATOL + NUMERIC_RTOL * np.abs(before)))
    alive = candidate.rho > 1e-4
    return {
        "global_before": global_before,
        "global_after": global_after,
        "global_delta": global_delta,
        "within_float64_criterion": criterion,
        "required_physical_fields_pass": bool(all(criterion[field] for field in ops.BALANCED_PHYSICAL_FIELDS)),
        "regions": regional,
        "material": {
            "rho_mass_delta": float(candidate.rho.sum() - recipient.rho.sum()),
            "cohort_channel_totals_match": criterion["C"],
            "base_cohort_sum_minus_rho_max_abs": p05._cohort_error(candidate),
        },
        "body_on_expected_donor_support_before": _body_state(recipient, expected_donor_mask),
        "body_on_expected_donor_support_after": _body_state(candidate, expected_donor_mask),
        "stored_previous_uptake_mean_alive": float(candidate.uptake[alive].mean()) if alive.any() else 0.0,
        "up_ref_at_surgery": None,
        "up_ref_note": "not persistent; recomputed from next-step uptake inside the update",
    }


def _correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    if a.size < 2 or float(a.std()) == 0.0 or float(b.std()) == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _payload_metrics(
    recipient: IOMState,
    candidate: IOMState,
    donor_shifted: IOMState,
    expected_donor_mask: np.ndarray,
    weight: np.ndarray,
) -> dict:
    payload_core = weight >= 1.0 - 1e-15
    occupied = (donor_shifted.rho > 1e-4) & (candidate.rho > 1e-4)
    mask = payload_core & occupied
    rec = _views(recipient)
    can = _views(candidate)
    don = _views(donor_shifted)
    per_field = {}
    for field in ("rho", "u", "v", "c", "N", "m1", "m2", "m_plus"):
        baseline = rec[field][mask]
        target = don[field][mask]
        observed = can[field][mask]
        direction = target - baseline
        denom = float(np.dot(direction, direction))
        projection = float(np.dot(observed - baseline, direction) / denom) if denom > 1e-24 else None
        nrmse = float(np.sqrt(np.dot(observed - target, observed - target) / denom)) if denom > 1e-24 else None
        per_field[field] = {
            "contrast_projection": projection,
            "donor_normalized_rmse": nrmse,
            "donor_correlation": _correlation(observed, target),
            "n_cells": int(mask.sum()),
        }

    donor_L = memory_features(donor_shifted, expected_donor_mask)
    recipient_L = memory_features(recipient, expected_donor_mask)
    candidate_L = memory_features(candidate, expected_donor_mask)
    direction_L = donor_L - recipient_L
    denom_L = float(np.dot(direction_L, direction_L))
    projection_L = (
        float(np.dot(candidate_L - recipient_L, direction_L) / denom_L)
        if denom_L > 1e-24
        else None
    )
    body_coverage = float((expected_donor_mask & payload_core).sum() / max(1, expected_donor_mask.sum()))
    memory_projections = [
        per_field[field]["contrast_projection"]
        for field in ("m1", "m2", "m_plus")
        if per_field[field]["contrast_projection"] is not None
    ]
    memory_min = min(memory_projections, default=None)
    meaningful = bool(
        projection_L is not None
        and projection_L >= PAYLOAD_PROJECTION_MIN
        and memory_min is not None
        and memory_min >= PAYLOAD_PROJECTION_MIN
        and body_coverage >= PAYLOAD_BODY_COVERAGE_MIN
    )
    return {
        "body_fraction_inside_full_donor_weight": body_coverage,
        "per_field": per_field,
        "L_recipient": _safe(recipient_L),
        "L_donor": _safe(donor_L),
        "L_candidate": _safe(candidate_L),
        "L_contrast_projection": projection_L,
        "memory_field_min_contrast_projection": memory_min,
        "meaningful_payload_pass": meaningful,
        "frozen_gate": {
            "L_and_each_memory_projection_min": PAYLOAD_PROJECTION_MIN,
            "donor_body_full_weight_coverage_min": PAYLOAD_BODY_COVERAGE_MIN,
        },
    }


def _geometry_mismatch(
    recipient: IOMState,
    donor_shifted: IOMState,
    recipient_mask: np.ndarray,
    donor_mask: np.ndarray,
    partition: ops.StatePartition,
) -> dict:
    union = int((recipient_mask | donor_mask).sum())
    boundary = (partition.distance > 9.0) & (partition.distance <= 10.0)
    threshold = 0.30 * MCM_CONFIG.SPEC.rho_max
    return {
        "recipient_body_cells": int(recipient_mask.sum()),
        "donor_body_cells": int(donor_mask.sum()),
        "body_iou": float((recipient_mask & donor_mask).sum() / max(1, union)),
        "recipient_body_mass": float(recipient.rho[recipient_mask].sum()),
        "donor_body_mass": float(donor_shifted.rho[donor_mask].sum()),
        "outer_interface_occupied_cells_recipient": int((recipient.rho[boundary] > threshold).sum()),
        "outer_interface_occupied_cells_donor": int((donor_shifted.rho[boundary] > threshold).sum()),
    }


def _audit_branch(
    *,
    recipient: IOMState,
    candidate: IOMState,
    donor: IOMState,
    recipient_partition: ops.StatePartition,
    donor_partition: ops.StatePartition,
    recipient_mask: np.ndarray,
    expected_donor_mask: np.ndarray,
    weight: np.ndarray,
    bands: dict[str, np.ndarray],
    engine,
    operator_record: dict,
    baseline_run: dict,
) -> dict:
    shift = tuple(recipient_partition.center[i] - donor_partition.center[i] for i in range(2))
    donor_shifted = _translated_state(donor, shift)
    branch_run = _simulate(candidate, expected_donor_mask, engine)
    return {
        "operator_record": operator_record,
        "state_hash": ops.state_sha256(candidate),
        "phase": {
            "scheduler_step_delta": int(candidate.step - recipient.step),
            "persistent_previous_buffer": None,
            "persistent_flux_or_gradient_buffer": None,
            "persistent_cache": None,
            "persistent_rng": None,
            "tracker": "external; outcome-independent geometry re-seed",
        },
        "balance_ledger": _balance_ledger(recipient, candidate, recipient_partition, expected_donor_mask),
        "outer_C_boundary_seam": _outer_seam_audit(recipient, candidate, recipient_partition),
        "all_changed_interface_faces": _interface_audit(recipient, candidate, donor_shifted, weight, engine),
        "geometry_mismatch": _geometry_mismatch(
            recipient, donor_shifted, recipient_mask, expected_donor_mask, recipient_partition
        ),
        "payload": _payload_metrics(recipient, candidate, donor_shifted, expected_donor_mask, weight),
        "immediate_and_transient_bands": _transient_bands(baseline_run, branch_run, bands),
        "short_continuation": _clean_run(branch_run),
    }


def _world_context(raw_record: dict) -> dict:
    seed = ops.require_dev_seed(raw_record["seed"])
    deep_step = int(raw_record["deep"]["step"])
    base = tdd.to_S0(seed)
    intact = tdd.run_to(base["eng"], base["S0"], base["reg0"], deep_step)
    state = intact["S"]
    regions = intact["regs"]
    centers = p05._centers_for_regions(state, regions)
    partitions = [ops.partition_state(state.rho.shape, center) for center in centers]
    pair = p05._history_pair(raw_record)
    index_a, index_b = pair["A"], pair["B"]
    no_history = p05._build_no_history_world(seed, deep_step)
    reference_entity, reference_region = p05._standard_reference(no_history)
    reference_partition = ops.partition_state(no_history.rho.shape, reference_entity.centroid)
    return {
        "seed": seed,
        "deep_step": deep_step,
        "engine": base["eng"],
        "state": state,
        "regions": regions,
        "partitions": partitions,
        "pair": pair,
        "a": index_a,
        "b": index_b,
        "no_history": no_history,
        "reference_region": reference_region,
        "reference_partition": reference_partition,
    }


def _branch_definitions(context: dict) -> list[dict]:
    state = context["state"]
    no_history = context["no_history"]
    a, b = context["a"], context["b"]
    regions = context["regions"]
    parts = context["partitions"]
    ref_region = context["reference_region"]
    ref_part = context["reference_partition"]
    return [
        {"name": "C_B_E_A", "recipient": state, "donor": state, "rp": parts[a], "dp": parts[b], "rm": regions[a], "dm": regions[b]},
        {"name": "C_A_E_B", "recipient": state, "donor": state, "rp": parts[b], "dp": parts[a], "rm": regions[b], "dm": regions[a]},
        {"name": "C_0_E_A", "recipient": state, "donor": no_history, "rp": parts[a], "dp": ref_part, "rm": regions[a], "dm": ref_region},
        {"name": "C_A_E_0", "recipient": no_history, "donor": state, "rp": ref_part, "dp": parts[a], "rm": ref_region, "dm": regions[a]},
        {"name": "C_0_E_B", "recipient": state, "donor": no_history, "rp": parts[b], "dp": ref_part, "rm": regions[b], "dm": ref_region},
        {"name": "C_B_E_0", "recipient": no_history, "donor": state, "rp": ref_part, "dp": parts[b], "rm": ref_region, "dm": regions[b]},
    ]


def _expected_mask(branch: dict) -> np.ndarray:
    shift = tuple(branch["rp"].center[i] - branch["dp"].center[i] for i in range(2))
    return np.roll(branch["dm"], shift, axis=(-2, -1))


def _hard_failure_audit(context: dict) -> dict:
    state = context["state"]
    a, b = context["a"], context["b"]
    parts = context["partitions"]
    regions = context["regions"]
    cb_ea, ca_eb, record = ops.exchange_cores(state, state, parts[a], parts[b])
    branches = [
        ("C_B_E_A", state, cb_ea, parts[a], parts[b], regions[a], regions[b]),
        ("C_A_E_B", state, ca_eb, parts[b], parts[a], regions[b], regions[a]),
    ]
    result = {"operator_record": _safe(record.__dict__), "arms": {}}
    for name, recipient, candidate, rp, dp, recipient_mask, donor_mask in branches:
        expected = np.roll(
            donor_mask,
            tuple(rp.center[i] - dp.center[i] for i in range(2)),
            axis=(-2, -1),
        )
        baseline_run = _simulate(recipient, recipient_mask, context["engine"])
        weight = rp.core.astype(float)
        bands = {
            "payload_core": rp.distance <= 9.0,
            "interface_collar": (rp.distance > 9.0) & (rp.distance <= 10.0),
            "inner_halo": (rp.distance > 10.0) & (rp.distance <= 11.0),
            "outer_halo": (rp.distance > 11.0) & (rp.distance <= 13.0),
            "far_environment": rp.distance > 13.0,
        }
        result["arms"][name] = _audit_branch(
            recipient=recipient,
            candidate=candidate,
            donor=state,
            recipient_partition=rp,
            donor_partition=dp,
            recipient_mask=recipient_mask,
            expected_donor_mask=expected,
            weight=weight,
            bands=bands,
            engine=context["engine"],
            operator_record={"family": "PHASE05_EXACT_HARD_CUT_REAUDIT"},
            baseline_run=baseline_run,
        )
    return result


def _candidate_world(context: dict) -> dict:
    engine = context["engine"]
    result = {
        "seed": context["seed"],
        "deep_step": context["deep_step"],
        "history_pair": context["pair"],
        "phase05_hard_cut_localization": _hard_failure_audit(context),
        "configurations": {},
    }
    baseline_cache = {}
    branches = _branch_definitions(context)
    for spec in ops.BOUNDARY_SAFE_SPECS:
        config = {"spec": _safe(spec.__dict__), "active_operation_shams": {}, "arms": {}}
        for branch in branches:
            cache_key = (ops.state_sha256(branch["recipient"]), int(np.flatnonzero(branch["rm"])[0]))
            if cache_key not in baseline_cache:
                baseline_cache[cache_key] = _simulate(branch["recipient"], branch["rm"], engine)
            expected = _expected_mask(branch)
            try:
                candidate, record = ops.boundary_safe_transplant(
                    branch["recipient"], branch["donor"], branch["rp"], branch["dp"], spec
                )
                config["arms"][branch["name"]] = _audit_branch(
                    recipient=branch["recipient"],
                    candidate=candidate,
                    donor=branch["donor"],
                    recipient_partition=branch["rp"],
                    donor_partition=branch["dp"],
                    recipient_mask=branch["rm"],
                    expected_donor_mask=expected,
                    weight=ops.boundary_safe_weights(branch["rp"], spec),
                    bands=ops.boundary_safe_bands(branch["rp"], spec),
                    engine=engine,
                    operator_record=record,
                    baseline_run=baseline_cache[cache_key],
                )
            except (ValueError, ops.BalanceProjectionError) as exc:
                config["arms"][branch["name"]] = {
                    "operator_failed": True,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }

        # Minimum active-operation sham: same operator, same numerical path,
        # but recipient is also donor.  No scientific feeding readout occurs.
        for label, state, part in (
            ("history_A", context["state"], context["partitions"][context["a"]]),
            ("no_history_0", context["no_history"], context["reference_partition"]),
        ):
            sham, sham_record = ops.boundary_safe_transplant(state, state, part, part, spec)
            config["active_operation_shams"][label] = {
                "max_abs_state_error": p05._max_error(ops.exact_state_errors(state, sham)),
                "record": sham_record,
            }
        result["configurations"][spec.name] = config
    return result


def _iter_arms(worlds: list[dict], config_name: str):
    for world in worlds:
        if not world.get("feasible"):
            continue
        for arm_name, arm in world["qualification"]["configurations"][config_name]["arms"].items():
            yield world["seed"], arm_name, arm


def _max_band_rms(arms: list[dict], band: str, step: int) -> float | None:
    values = []
    for arm in arms:
        if arm.get("operator_failed"):
            continue
        transient = arm["immediate_and_transient_bands"].get(str(step), {})
        if band in transient:
            values.extend(float(metric["rms"]) for metric in transient[band].values())
    return max(values, default=None)


def _summarize(phase05: dict, worlds: list[dict]) -> dict:
    summary = {
        "phase05_exact_reaudit": phase05["summary"],
        "phase05_expected_failure_reproduced": bool(
            abs(phase05["summary"]["seam_ratio_DEV"]["max_observed"] - 22.872170460755093) <= 1e-12
            and phase05["summary"]["individual_arm_balance_matched"] is False
        ),
        "configurations": {},
    }
    for spec in ops.BOUNDARY_SAFE_SPECS:
        records = list(_iter_arms(worlds, spec.name))
        arms = [arm for _, _, arm in records]
        failures = [arm for arm in arms if arm.get("operator_failed")]
        interface_ratios = []
        outer_ratios = []
        payload_L = []
        payload_memory_min = []
        payload_coverage = []
        valid = []
        balance = []
        for arm in arms:
            if arm.get("operator_failed"):
                continue
            interface_ratios.extend(
                field["candidate_to_recipient_ratio"]
                for field in arm["all_changed_interface_faces"]["fields"].values()
                if field["candidate_to_recipient_ratio"] is not None
            )
            outer_ratios.extend(
                field["ratio"] for field in arm["outer_C_boundary_seam"].values()
                if field["ratio"] is not None
            )
            payload_L.append(arm["payload"]["L_contrast_projection"])
            payload_memory_min.append(arm["payload"]["memory_field_min_contrast_projection"])
            payload_coverage.append(arm["payload"]["body_fraction_inside_full_donor_weight"])
            valid.append(bool(arm["short_continuation"]["valid"]))
            balance.append(bool(arm["balance_ledger"]["required_physical_fields_pass"]))

        seam_pass = bool(interface_ratios and max(interface_ratios) <= SEAM_RATIO_ENVELOPE)
        outer_pass = bool(outer_ratios and max(outer_ratios) <= SEAM_RATIO_ENVELOPE)
        payload_pass = bool(
            payload_L
            and all(value is not None and value >= PAYLOAD_PROJECTION_MIN for value in payload_L)
            and all(value is not None and value >= PAYLOAD_PROJECTION_MIN for value in payload_memory_min)
            and all(value >= PAYLOAD_BODY_COVERAGE_MIN for value in payload_coverage)
        )
        all_balance = bool(balance and all(balance) and not failures)
        all_valid = bool(valid and all(valid) and not failures)
        config_summary = {
            "family": spec.family,
            "n_arms": len(arms),
            "operator_failures": len(failures),
            "per_arm_physical_balance_pass": all_balance,
            "all_40_step_viable_trackable": all_valid,
            "outer_boundary_seam_ratio_max": max(outer_ratios, default=None),
            "all_changed_interface_seam_ratio_max": max(interface_ratios, default=None),
            "seam_sensitivity_pass_counts": {
                str(threshold): int(sum(value <= threshold for value in interface_ratios))
                for threshold in SEAM_SENSITIVITY
            },
            "seam_value_count": len(interface_ratios),
            "payload_L_projection_min": min(payload_L, default=None),
            "payload_memory_projection_min": min(payload_memory_min, default=None),
            "payload_body_full_weight_coverage_min": min(payload_coverage, default=None),
            "payload_pass": payload_pass,
            "propagation_max_rms": {
                str(step): {
                    band: _max_band_rms(arms, band, step)
                    for band in ("payload_core", "interface_collar", "inner_halo", "outer_halo", "far_environment")
                }
                for step in SNAPSHOT_STEPS
            },
            "technical_go": bool(all_balance and all_valid and outer_pass and seam_pass and payload_pass),
        }
        summary["configurations"][spec.name] = config_summary

    go = [name for name, item in summary["configurations"].items() if item["technical_go"]]
    summary["technical_go_configurations"] = go
    summary["scientific_feeding_contrast_evaluated"] = False
    summary["storage_location_inferred"] = False
    summary["decision"] = "TECHNICAL_GO" if go else "PENDING_SCIENTIFIC_JUDGMENT_AFTER_FULL_TRADEOFF_AUDIT"
    return summary


def run(seeds: list[int]) -> dict:
    seeds = [ops.require_dev_seed(seed) for seed in seeds]
    if len(seeds) != len(set(seeds)):
        raise ValueError("duplicate DEV seeds are not permitted")
    if tuple(seeds) != ops.DEV_SEEDS:
        raise ValueError("Phase 0.6A requires the complete already-open DEV namespace 50001-50010")

    print("re-run Phase 0.5 exact qualification", flush=True)
    phase05 = p05.run(seeds)
    raw_by_seed = {int(record["seed"]): record for record in json.loads(DEV_RAW.read_text())}
    worlds = []
    for seed in seeds:
        raw = raw_by_seed[seed]
        if not raw.get("feasible"):
            reason = raw.get("deep_reason") or ("ineligible" if not raw.get("eligible") else "not_deep_feasible")
            worlds.append({"seed": seed, "feasible": False, "reason": reason, "operator_executed": False})
            print(f"seed {seed}: existing disposition, no Phase 0.6A operator ({reason})", flush=True)
            continue
        print(f"seed {seed}: hard-cut re-audit plus complete frozen boundary grid", flush=True)
        context = _world_context(raw)
        worlds.append({"seed": seed, "feasible": True, "qualification": _candidate_world(context)})

    result = {
        "schema": "ACCESS-STRUCTURE-00-PHASE06A-BOUNDARY-SAFE-QUALIFICATION-v1",
        "mode": "DEV_ONLY_ALREADY_OPEN_SEEDS",
        "allowed_seed_namespace": list(ops.DEV_SEEDS),
        "seeds_requested": seeds,
        "new_seed_or_prospective_family_opened": False,
        "scientific_crossed_feeding_evaluated": False,
        "scientific_storage_question_answered": False,
        "frozen_operator_grid": [_safe(spec.__dict__) for spec in ops.BOUNDARY_SAFE_SPECS],
        "frozen_gates": {
            "float64": "abs(error) <= 1e-12 + 1e-10*abs(reference)",
            "seam_ratio_max": SEAM_RATIO_ENVELOPE,
            "seam_sensitivity": list(SEAM_SENSITIVITY),
            "payload_projection_min": PAYLOAD_PROJECTION_MIN,
            "payload_body_coverage_min": PAYLOAD_BODY_COVERAGE_MIN,
            "qualification_steps": list(SNAPSHOT_STEPS),
        },
        "phase05_reaudit": {
            "summary": phase05["summary"],
            "world_dispositions": [
                {"seed": world["seed"], "feasible": world.get("feasible", False), "reason": world.get("reason")}
                for world in phase05["worlds"]
            ],
        },
        "worlds": worlds,
    }
    result["summary"] = _summarize(phase05, worlds)
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
