"""COUNTERFACTUAL-HISTORY-CORE-00 — bounded DEV-only exact-clone factorial.

One pre-history focal target is selected before treatment.  The complete Markov
state and canonical tracker mapping are serialized once and cloned into four
byte-identical branches.  Each branch receives exactly one fixed focal history;
all non-focal targets remain on the common no-direct-drive protocol.  Branches
are potential outcomes, not replicates.  The original source world is the only
statistical unit.

No prospective/confirmation namespace is accepted by this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import balanced_history_isolation_dev as bh
from experiments.individuation import bijective_tracker as bt
from experiments.individuation import causal_confirm as cc
from experiments.individuation import material_tracer as mt
from experiments.individuation.turnover_diag_engine import DiagEngine


SCHEMA = "COUNTERFACTUAL-HISTORY-CORE-00-DEV-v1"
MANIFEST_SCHEMA = "COUNTERFACTUAL-HISTORY-CORE-00-MANIFEST-v1"
CANONICAL_PARENT = "4ef4bed0ee43a8d6edaec2b597e205eeb2393327"
MANIFEST_SHA256 = "298dcc02d391eb8952d3d293fdaf1bcd9ceef2c032d8e521771ee50cce569457"
MODE = "DEV_ONLY_NO_PROSPECTIVE_AUTHORIZATION"

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_MANIFEST.json"
DEV_SEEDS = tuple(range(57001, 57025))

N = cc.N
GRID = N * N
WARM = cc.WARM
PHASE = cc.PHASE
SETTLE = cc.SETTLE
MINSIZE = cc.MINSIZE
SEP = cc.SEP
M_TARGET = 0.25
DEEP_STEPS = 1000
COVER_CAP = bh.COVER_CAP
THETA = bh.THETA
SETTLE_STD = bh.SETTLE_STD
STIM_AMP = bh.STIM_AMP
STIM_DUR = bh.STIM_DUR
HORIZON = bh.HORIZON
CORE_RADIUS = ns.CORE_RADIUS
BARRIER_WIDTH = ns.BARRIER_WIDTH
SIGN_FRACTION = 0.75
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10

HISTORY_NAMES = (
    "H_L_EARLY",
    "H_L_LATE",
    "H_H_EARLY",
    "H_H_LATE",
)
HISTORIES = {
    "H_L_EARLY": (0.0175, 0.0075),
    "H_L_LATE": (0.0075, 0.0175),
    "H_H_EARLY": (0.0325, 0.0225),
    "H_H_LATE": (0.0225, 0.0325),
}
PRIMARY_ARMS = ("coupled", "isolated")
CONTROL_ARMS = ("coupled_g0", "sham_own_replay_g0")
SECONDARY_ARMS = ("coupled_lamplus0", "isolated_lamplus0")
ALL_ARMS = PRIMARY_ARMS + CONTROL_ARMS + SECONDARY_ARMS
FIRST_STAGE_SCALARS = bh.FIRST_STAGE_SCALARS + (
    "nearest_neighbor_distance",
    "world_up_ref",
    "world_N_mean",
    "world_c_mean",
    "world_rho_mass",
    "deep_material_M",
    "deep_elapsed_steps",
)


def sha256_file(path: Path) -> str:
    return bh.sha256_file(path)


def state_hash(state) -> str:
    return ops.state_sha256(state)


def _safe(value):
    return bh._safe(value)


def validate_manifest_payload(manifest: dict) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("manifest schema mismatch")
    if manifest.get("mode") != MODE:
        raise RuntimeError("manifest mode mismatch")
    if manifest.get("canonical_parent") != CANONICAL_PARENT:
        raise RuntimeError("manifest parent mismatch")
    if tuple(manifest.get("seeds", ())) != DEV_SEEDS:
        raise RuntimeError("manifest seed family mismatch")
    if int(manifest.get("episode_duration_steps", -1)) != PHASE:
        raise RuntimeError("episode duration mismatch")
    if int(manifest.get("post_history_settle_steps", -1)) != SETTLE:
        raise RuntimeError("post-history settle mismatch")
    if int(manifest.get("fixed_deep_elapsed_steps", -1)) != DEEP_STEPS:
        raise RuntimeError("fixed deep step mismatch")
    recovered = {
        name: tuple(manifest["histories"][name][key] for key in ("a1", "a2"))
        for name in HISTORY_NAMES
    }
    if recovered != HISTORIES:
        raise RuntimeError("history values mismatch")
    if manifest.get("focal_selection", {}).get("rule") != "lowest_canonical_tracker_id_among_eligible":
        raise RuntimeError("focal selection mismatch")
    if manifest.get("execution_order", {}).get("rule") != "sha256_seed_history_permutation":
        raise RuntimeError("execution-order rule mismatch")
    if manifest.get("isolated", {}).get("up_ref") != 0:
        raise RuntimeError("isolated global rule mismatch")
    if manifest.get("statistical_unit") != "original source world":
        raise RuntimeError("statistical unit mismatch")
    if manifest.get("counterfactual_branches_are_replicates") is not False:
        raise RuntimeError("branch pseudoreplication contract mismatch")
    audit = manifest.get("namespace_audit", {})
    if not audit.get("fresh_decimal_integer_audit_pass"):
        raise RuntimeError("namespace audit is not frozen PASS")
    prohibited = set(range(50001, 50011)) | set(range(51000, 55025))
    if prohibited.intersection(DEV_SEEDS):
        raise RuntimeError("historical DEV namespace reuse")


def load_and_validate_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    if sha256_file(path) != MANIFEST_SHA256:
        raise RuntimeError("manifest SHA-256 mismatch")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest_payload(manifest)
    return manifest


def execution_order(seed: int) -> tuple[str, ...]:
    """Seed-derived order with no mutable RNG and no scientific inputs."""
    if int(seed) not in DEV_SEEDS and int(seed) != 50002:
        raise ValueError("execution order accepts only the frozen family or open test seed 50002")
    return tuple(sorted(HISTORY_NAMES, key=lambda name: hashlib.sha256(
        f"COUNTERFACTUAL-HISTORY-CORE-00|{int(seed)}|{name}".encode("ascii")
    ).digest()))


def canonical_state_bytes(state) -> bytes:
    """Deterministic bytes for every persistent array plus absolute scheduler step."""
    parts = [b"COUNTERFACTUAL-HISTORY-CORE-00-STATE-v1\0", int(state.step).to_bytes(8, "little", signed=True)]
    for field in ns.STATE_FIELDS:
        array = np.ascontiguousarray(getattr(state, field))
        header = json.dumps(
            {"field": field, "shape": list(array.shape), "dtype": array.dtype.str},
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii")
        parts.extend([len(header).to_bytes(4, "little"), header,
                      array.nbytes.to_bytes(8, "little"), array.tobytes()])
    return b"".join(parts)


def canonical_mask_bytes(masks: Sequence[np.ndarray]) -> bytes:
    parts = [len(masks).to_bytes(4, "little")]
    for track_id, region in enumerate(masks):
        array = np.ascontiguousarray(region, dtype=np.bool_)
        parts.extend([track_id.to_bytes(4, "little"), array.tobytes()])
    return b"".join(parts)


def periodic_distance(a: Sequence[float], b: Sequence[float]) -> float:
    return bh.periodic_distance(a, b)


def mask(entity) -> np.ndarray:
    return bh.mask(entity)


def _canonical_entities(state) -> list:
    entities = list(detect(state, MCM_CONFIG.DET))
    return sorted(entities, key=lambda entity: (
        round(float(entity.centroid[0]), 12),
        round(float(entity.centroid[1]), 12),
        -int(entity.size),
        round(float(entity.mass), 12),
        round(float(entity.rg), 12),
    ))


def _mask_digest(region: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(region, dtype=np.bool_).tobytes()).hexdigest()


def focal_eligibility(state, entities: Sequence) -> tuple[list[dict], list, list[np.ndarray]]:
    """Frozen size-first separated set, then canonical tracker IDs.

    This is the existing target-selection geometry repaired for one focal target:
    eligible bodies are greedily separated by ``SEP`` in descending size order.
    Bodies must also fit the already-qualified radius-10 core.  The resulting
    separated set is then assigned stable spatial tracker IDs; the focal is the
    lowest such ID.  Small disconnected fragments are not tracker targets.
    """
    detected_masks = [mask(entity) for entity in entities]
    priority = sorted(range(len(entities)), key=lambda index: (
        -int(entities[index].size),
        round(float(entities[index].centroid[0]), 12),
        round(float(entities[index].centroid[1]), 12),
    ))
    selected_indices = []
    base_metrics = {}
    for index in priority:
        entity = entities[index]
        region = detected_masks[index]
        _, core, _ = ns.core_and_collar(state.rho.shape, entity.centroid)
        size_ok = int(entity.size) >= MINSIZE
        coverage_ok = int(entity.size) < int(COVER_CAP * GRID)
        core_contains_body = not bool(np.any(region & ~core))
        distance_to_selected = min(
            (periodic_distance(entity.centroid, entities[other].centroid) for other in selected_indices),
            default=float("inf"),
        )
        separation_ok = distance_to_selected >= SEP
        tracker_seed_ok = bool(region.any())
        selected = bool(size_ok and coverage_ok and core_contains_body and separation_ok and tracker_seed_ok)
        if selected:
            selected_indices.append(index)
        base_metrics[index] = {
            "size_ok": size_ok,
            "coverage_ok": coverage_ok,
            "core_contains_body": core_contains_body,
            "distance_to_previously_selected_target": (
                float(distance_to_selected) if math.isfinite(distance_to_selected) else None
            ),
            "separation_ok": separation_ok,
            "greedy_selected": selected,
            "tracker_seed_ok": tracker_seed_ok,
        }

    selected_indices.sort(key=lambda index: (
        round(float(entities[index].centroid[0]), 12),
        round(float(entities[index].centroid[1]), 12),
        -int(entities[index].size),
    ))
    tracker_id_by_detected = {index: tracker_id for tracker_id, index in enumerate(selected_indices)}
    selected_entities = [entities[index] for index in selected_indices]
    selected_masks = [detected_masks[index] for index in selected_indices]
    metrics = []
    for detected_id, entity in enumerate(entities):
        region = detected_masks[detected_id]
        tracker_id = tracker_id_by_detected.get(detected_id)
        barrier_clear = False
        if tracker_id is not None:
            _, _, ring = ns.core_and_collar(state.rho.shape, entity.centroid)
            other_selected = [selected_masks[index] for index in range(len(selected_masks)) if index != tracker_id]
            other_union = np.logical_or.reduce(other_selected) if other_selected else np.zeros_like(region)
            barrier_clear = not bool(np.any(ring & other_union))
        eligible = bool(tracker_id is not None and barrier_clear)
        metrics.append({
            "detected_component_id": int(detected_id),
            "canonical_tracker_id": int(tracker_id) if tracker_id is not None else None,
            "centroid": [float(value) for value in entity.centroid],
            "size": int(entity.size),
            "mass": float(entity.mass),
            "rg": float(entity.rg),
            "mask_sha256": _mask_digest(region),
            **base_metrics[detected_id],
            "two_cell_barrier_clear_of_other_selected_targets": barrier_clear,
            "eligible": eligible,
        })
    return metrics, selected_entities, selected_masks


def make_checkpoint(seed: int) -> dict:
    engine = cc.build(cc.MEM_INTACT)
    state = cc.seed_world(int(seed))
    for _ in range(WARM):
        state = engine.step(state)
    detected_entities = _canonical_entities(state)
    metrics, entities, masks = focal_eligibility(state, detected_entities)
    eligible = [row["canonical_tracker_id"] for row in metrics if row["eligible"]]
    focal_id = min(eligible) if eligible else None
    payload = ops.serialize_state(state)
    state_bytes = canonical_state_bytes(state)
    mapping_bytes = canonical_mask_bytes(masks)
    scheduler = {
        "absolute_step": int(state.step),
        "active_feed_cohort": int(MCM_CONFIG.TRACER.active_feed_cohort(state.step)),
        "rule": "active_feed_cohort is a pure function of IOMState.step",
    }
    rng_state = {
        "kind": "none_after_initialization",
        "initial_world_seed": int(seed),
        "explanation": "seed_state consumes initialization RNG; engine.step has no stochastic draw or retained RNG",
    }
    metadata = json.dumps(
        {"scheduler": scheduler, "rng_state": rng_state, "focal_id": focal_id},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    bundle_hash = hashlib.sha256(state_bytes + mapping_bytes + metadata).hexdigest()
    return {
        "seed": int(seed),
        "state_payload": payload,
        "state": state,
        "entities": entities,
        "n_detected_components": len(detected_entities),
        "tracker_masks": masks,
        "eligibility": metrics,
        "focal_id": focal_id,
        "state_sha256": state_hash(state),
        "canonical_state_bytes_sha256": hashlib.sha256(state_bytes).hexdigest(),
        "tracker_mapping_sha256": hashlib.sha256(mapping_bytes).hexdigest(),
        "checkpoint_bundle_sha256": bundle_hash,
        "serialized_state_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "scheduler": scheduler,
        "rng_state": rng_state,
    }


def clone_checkpoint(checkpoint: dict) -> dict:
    return {
        "state": ops.deserialize_state(checkpoint["state_payload"]),
        "tracker_masks": [region.copy() for region in checkpoint["tracker_masks"]],
        "focal_id": checkpoint["focal_id"],
    }


def validate_four_clones(checkpoint: dict) -> dict:
    clones = [clone_checkpoint(checkpoint) for _ in HISTORY_NAMES]
    state_bytes = [canonical_state_bytes(branch["state"]) for branch in clones]
    mapping_bytes = [canonical_mask_bytes(branch["tracker_masks"]) for branch in clones]
    reference = clones[0]
    max_errors = [ops.exact_state_errors(reference["state"], branch["state"]) for branch in clones]
    exact = bool(
        all(payload == state_bytes[0] for payload in state_bytes)
        and all(payload == mapping_bytes[0] for payload in mapping_bytes)
        and all(branch["focal_id"] == reference["focal_id"] for branch in clones)
        and all(all(value == 0 for value in errors.values()) for errors in max_errors)
    )
    return {
        "valid": exact,
        "n_branches": len(clones),
        "state_byte_lengths": [len(payload) for payload in state_bytes],
        "state_byte_sha256": [hashlib.sha256(payload).hexdigest() for payload in state_bytes],
        "tracker_mapping_sha256": [hashlib.sha256(payload).hexdigest() for payload in mapping_bytes],
        "focal_ids": [branch["focal_id"] for branch in clones],
        "max_abs_errors_vs_branch0": max_errors,
    }


def _new_tracker(masks: Sequence[np.ndarray], absolute_step: int) -> bt.BijectiveTracker:
    tracker = bt.BijectiveTracker(theta=THETA)
    tracker.seed([region.copy() for region in masks], int(absolute_step))
    return tracker


def _tracker_update(tracker: bt.BijectiveTracker, state) -> dict:
    entities = list(detect(state, MCM_CONFIG.DET))
    masks = [mask(entity) for entity in entities]
    events = tracker.update(masks, int(state.step))
    coverage = max((int(region.sum()) for region in masks), default=0) / GRID
    return {"entities": entities, "events": events, "coverage": float(coverage)}


def _focal_alive(tracker: bt.BijectiveTracker, focal_id: int) -> bool:
    return bool(0 <= int(focal_id) < len(tracker.tracks)
                and tracker.tracks[int(focal_id)].status == bt.ALIVE)


def history_treatment_plan(checkpoint: dict, history_name: str) -> dict:
    focal_id = int(checkpoint["focal_id"])
    return {
        "history": history_name,
        "focal_tracker_id": focal_id,
        "focal_amplitudes": list(HISTORIES[history_name]),
        "focal_episode_steps": [PHASE, PHASE],
        "nonfocal_direct_amplitudes": {
            str(track_id): [0.0, 0.0]
            for track_id in range(len(checkpoint["tracker_masks"])) if track_id != focal_id
        },
        "unselected_detected_components_direct_history": "none",
        "n_unselected_detected_components": int(
            checkpoint["n_detected_components"] - len(checkpoint["tracker_masks"])
        ),
        "nonfocal_rule": "no direct assigned drive; physical spillover from the focal Gaussian is a treatment consequence",
    }


def apply_history(checkpoint: dict, history_name: str) -> dict:
    if history_name not in HISTORIES:
        raise ValueError(history_name)
    branch = clone_checkpoint(checkpoint)
    state = branch["state"]
    focal_id = int(branch["focal_id"])
    tracker = _new_tracker(branch["tracker_masks"], state.step)
    focal_entity = checkpoint["entities"][focal_id]
    patch = bh.gaussian_patch(focal_entity.centroid, max(3.0, 0.8 * float(focal_entity.rg)))
    engine = cc.build(cc.MEM_INTACT)
    focal_event = None
    all_events = {}
    max_coverage = 0.0
    for phase, amplitude in enumerate(HISTORIES[history_name]):
        for _ in range(PHASE):
            state.N = state.N + float(amplitude) * patch
            state = engine.step(state)
            update = _tracker_update(tracker, state)
            max_coverage = max(max_coverage, update["coverage"])
            for track_id, status in update["events"].items():
                all_events.setdefault(str(track_id), {"absolute_step": int(state.step), "status": status})
                if int(track_id) == focal_id and focal_event is None:
                    focal_event = {"absolute_step": int(state.step), "status": status, "phase": phase}
            if focal_event is not None or update["coverage"] >= COVER_CAP:
                return {
                    "history": history_name, "valid": False, "state": state,
                    "tracker": tracker, "patch": patch, "focal_event": focal_event,
                    "all_tracker_events": all_events, "max_coverage": max_coverage,
                    "treatment_plan": history_treatment_plan(checkpoint, history_name),
                    "reason": "history_focal_tracker_event" if focal_event else "history_coverage_fail",
                }
    for _ in range(SETTLE):
        state = engine.step(state)
        update = _tracker_update(tracker, state)
        max_coverage = max(max_coverage, update["coverage"])
        for track_id, status in update["events"].items():
            all_events.setdefault(str(track_id), {"absolute_step": int(state.step), "status": status})
            if int(track_id) == focal_id and focal_event is None:
                focal_event = {"absolute_step": int(state.step), "status": status, "phase": "settle"}
        if focal_event is not None or update["coverage"] >= COVER_CAP:
            return {
                "history": history_name, "valid": False, "state": state,
                "tracker": tracker, "patch": patch, "focal_event": focal_event,
                "all_tracker_events": all_events, "max_coverage": max_coverage,
                "treatment_plan": history_treatment_plan(checkpoint, history_name),
                "reason": "posthistory_focal_tracker_event" if focal_event else "posthistory_coverage_fail",
            }
    valid = _focal_alive(tracker, focal_id)
    return {
        "history": history_name,
        "valid": valid,
        "state": state,
        "tracker": tracker,
        "focal_region": tracker.tracks[focal_id].mask.copy() if valid else None,
        "patch": patch,
        "focal_event": focal_event,
        "all_tracker_events": all_events,
        "max_coverage": max_coverage,
        "treatment_plan": history_treatment_plan(checkpoint, history_name),
        "posthistory_state_sha256": state_hash(state),
        "reason": None if valid else "posthistory_focal_not_alive",
    }


def run_histories(checkpoint: dict, order: Sequence[str]) -> dict[str, dict]:
    if tuple(sorted(order)) != tuple(sorted(HISTORY_NAMES)):
        raise ValueError("execution order must contain each fixed history exactly once")
    return {name: apply_history(checkpoint, name) for name in order}


def turnover_fixed(state, focal_region: np.ndarray) -> dict:
    engine = cc.build(cc.MEM_INTACT)
    traced, base = mt.seed_tracers(state, [focal_region])
    mt.assert_no_feed_collision(engine.tracer, base, DEEP_STEPS + HORIZON + SETTLE_STD + 2)
    tracker = _new_tracker([focal_region], traced.step)
    first_event = None
    max_coverage = 0.0
    material = None
    last_entities = []
    for elapsed in range(1, DEEP_STEPS + 1):
        traced = engine.step(traced)
        update = _tracker_update(tracker, traced)
        max_coverage = max(max_coverage, update["coverage"])
        last_entities = update["entities"]
        if update["events"] and first_event is None:
            status = update["events"].get(0)
            if status is not None:
                first_event = {"elapsed_step": elapsed, "absolute_step": int(traced.step), "status": status}
        if first_event is not None or update["coverage"] >= COVER_CAP:
            return {
                "valid": False, "state": traced, "region": None, "entity": None,
                "material": material, "first_event": first_event,
                "max_coverage": max_coverage,
                "reason": "turnover_focal_tracker_event" if first_event else "turnover_coverage_fail",
            }
    region = tracker.tracks[0].mask.copy() if _focal_alive(tracker, 0) else None
    material = mt.read_material(traced, base, [region])[0] if region is not None else None
    entity = bh._entity_for_track(last_entities, region) if region is not None else None
    deep_ok = bool(
        region is not None and entity is not None and material is not None
        and np.isfinite(material["M"]) and float(material["M"]) <= M_TARGET
    )
    return {
        "valid": deep_ok,
        "state": traced,
        "region": region,
        "entity": entity,
        "center": [float(value) for value in entity.centroid] if entity is not None else None,
        "material": material,
        "first_event": first_event,
        "max_coverage": max_coverage,
        "state_sha256": state_hash(traced),
        "elapsed_steps": DEEP_STEPS,
        "reason": None if deep_ok else "fixed_step_not_deep_or_entity_missing",
    }


def no_drive_reference(checkpoint: dict) -> dict:
    """One history-independent same-seed boundary source at the common absolute time."""
    state = ops.deserialize_state(checkpoint["state_payload"])
    engine = cc.build(cc.MEM_INTACT)
    for _ in range(2 * PHASE + SETTLE):
        state = engine.step(state)
    base = int(state.C.shape[0])
    state.C = np.concatenate([state.C, np.zeros((1, N, N), dtype=state.C.dtype)], axis=0)
    mt.assert_no_feed_collision(engine.tracer, base, DEEP_STEPS + HORIZON + SETTLE_STD + 2)
    for _ in range(DEEP_STEPS):
        state = engine.step(state)
    entities = [entity for entity in detect(state, MCM_CONFIG.DET)
                if 4 <= int(entity.size) < int(COVER_CAP * GRID)]
    entities.sort(key=lambda entity: (
        int(entity.size), round(float(entity.centroid[0]), 12), round(float(entity.centroid[1]), 12)
    ))
    if not entities:
        return {"valid": False, "reason": "no_history_independent_reference_component"}
    entity = entities[(len(entities) - 1) // 2]
    return {
        "valid": True,
        "state": state,
        "center": tuple(float(value) for value in entity.centroid),
        "entity": entity,
        "state_sha256": state_hash(state),
        "absolute_step": int(state.step),
        "selection": "median size then centroid among on-manifold components",
    }


def _nearest_neighbor_distance(state, entity) -> float:
    candidates = list(detect(state, MCM_CONFIG.DET))
    distances = [periodic_distance(entity.centroid, other.centroid) for other in candidates
                 if periodic_distance(entity.centroid, other.centroid) > 1e-12]
    return float(min(distances)) if distances else float(N)


def first_stage(deep: dict, pre_entity, patch: np.ndarray) -> dict:
    state = deep["state"]
    region = deep["region"]
    entity = deep["entity"]
    result = bh.first_stage_target(state, region, deep["center"], entity, pre_entity, patch)
    alive = state.rho > 1e-4
    result.update({
        "nearest_neighbor_distance": _nearest_neighbor_distance(state, entity),
        "world_up_ref": float(state.uptake[alive].mean()) if alive.any() else 0.0,
        "world_N_mean": float(state.N.mean()),
        "world_c_mean": float(state.c.mean()),
        "world_rho_mass": float(state.rho.sum()),
        "deep_material_M": float(deep["material"]["M"]),
        "deep_elapsed_steps": float(DEEP_STEPS),
    })
    return result


def _geometry(deep: dict) -> dict:
    partition, core, ring = ns.core_and_collar(deep["state"].rho.shape, deep["center"])
    body_inside = not bool(np.any(deep["region"] & ~core))
    return {"valid": body_inside, "partition": partition, "core": core, "ring": ring,
            "reason": None if body_inside else "body_outside_qualified_core"}


def measure_arm(state, region: np.ndarray, engine) -> dict:
    if getattr(engine, "driver", None) is not None:
        engine.driver.reset()
    current = bh.standardized_probe_start(state)
    tracker = _new_tracker([region], current.step)
    fixed = None
    integrated_tracked = 0.0
    integrated_fixed = 0.0
    step40 = None
    events = {}
    max_coverage = 0.0
    for step in range(1, SETTLE_STD + HORIZON + 1):
        if SETTLE_STD < step <= SETTLE_STD + STIM_DUR:
            current.N = current.N + STIM_AMP
        current = engine.step(current)
        update = _tracker_update(tracker, current)
        max_coverage = max(max_coverage, update["coverage"])
        for track_id, status in update["events"].items():
            events.setdefault(str(track_id), {"step": step, "absolute_step": int(current.step), "status": status})
        if step == SETTLE_STD:
            fixed = tracker.tracks[0].mask.copy() if _focal_alive(tracker, 0) else np.zeros((N, N), bool)
        if step > SETTLE_STD:
            integrated_fixed += float(current.uptake[fixed].sum())
            if _focal_alive(tracker, 0):
                value = float(current.uptake[tracker.tracks[0].mask].sum())
                integrated_tracked += value
                if step == SETTLE_STD + HORIZON:
                    step40 = value
    valid = bool(
        _focal_alive(tracker, 0) and not events and max_coverage < COVER_CAP
        and np.isfinite(integrated_tracked) and np.isfinite(integrated_fixed)
    )
    return {
        "integrated_tracked_step40": integrated_tracked,
        "integrated_fixed_step40": integrated_fixed,
        "instantaneous_tracked_at_step40": step40,
        "status": tracker.tracks[0].status,
        "events": events,
        "max_coverage": float(max_coverage),
        "valid": valid,
        "final_state_sha256": state_hash(current),
    }


def _numeric_equal(a: float, b: float) -> bool:
    return bool(np.isclose(float(a), float(b), atol=NUMERIC_ATOL, rtol=NUMERIC_RTOL))


def probe_branch(deep: dict, reference: dict, pre_entity, patch: np.ndarray) -> dict:
    geometry = _geometry(deep)
    if not geometry["valid"]:
        return {"valid": False, "reason": geometry["reason"]}
    state = deep["state"]
    region = deep["region"]
    center = deep["center"]
    ring = geometry["ring"]
    shift = ns._shift(reference["center"], center)
    mem_lam0 = replace(cc.MEM_INTACT, lam_plus=0.0)

    own_driver = bh.record_probe_boundary(
        state, DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True),
        [ring], [(0, 0)], label="own_replay_sham_g0",
    )
    reference_driver = bh.record_probe_boundary(
        reference["state"],
        DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True),
        [ring], [shift], label="common_no_drive_reference_g0",
    )
    reference_driver_lam0 = bh.record_probe_boundary(
        reference["state"],
        DiagEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER, up_ref_zero=True),
        [ring], [shift], label="common_no_drive_reference_g0_lamplus0",
    )

    arms = {
        "coupled": measure_arm(
            state, region, MultiChannelMemoryEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER)
        ),
        "isolated": measure_arm(
            state, region, ns.NoSwapClampEngine(
                MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
                driver=ns.BoundaryDriver(reference_driver.ring, reference_driver.frames,
                                         label=reference_driver.label), up_ref_zero=True,
            )
        ),
        "coupled_g0": measure_arm(
            state, region, DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
        ),
        "sham_own_replay_g0": measure_arm(
            state, region, ns.NoSwapClampEngine(
                MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
                driver=ns.BoundaryDriver(own_driver.ring, own_driver.frames, label=own_driver.label),
                up_ref_zero=True,
            )
        ),
        "coupled_lamplus0": measure_arm(
            state, region, MultiChannelMemoryEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER)
        ),
        "isolated_lamplus0": measure_arm(
            state, region, ns.NoSwapClampEngine(
                MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER,
                driver=ns.BoundaryDriver(reference_driver_lam0.ring, reference_driver_lam0.frames,
                                         label=reference_driver_lam0.label), up_ref_zero=True,
            )
        ),
    }
    sham_exact = bool(
        arms["coupled_g0"]["valid"] and arms["sham_own_replay_g0"]["valid"]
        and _numeric_equal(arms["coupled_g0"]["integrated_tracked_step40"],
                           arms["sham_own_replay_g0"]["integrated_tracked_step40"])
        and _numeric_equal(arms["coupled_g0"]["integrated_fixed_step40"],
                           arms["sham_own_replay_g0"]["integrated_fixed_step40"])
        and arms["coupled_g0"]["final_state_sha256"] == arms["sham_own_replay_g0"]["final_state_sha256"]
    )
    primary_valid = all(arms[name]["valid"] for name in PRIMARY_ARMS)
    controls_valid = all(arms[name]["valid"] for name in CONTROL_ARMS)
    return {
        "valid": bool(primary_valid and controls_valid and sham_exact),
        "first_stage": first_stage(deep, pre_entity, patch),
        "arms": arms,
        "sham_exact": sham_exact,
        "geometry": {
            "body_inside_core": True,
            "core_radius": CORE_RADIUS,
            "barrier_width": BARRIER_WIDTH,
            "center": list(center),
            "body_size": int(deep["entity"].size),
            "body_mass": float(deep["entity"].mass),
            "body_rg": float(deep["entity"].rg),
        },
        "boundary": {
            "common_reference_state_sha256": reference["state_sha256"],
            "common_reference_absolute_step": reference["absolute_step"],
            "reference_center": list(reference["center"]),
            "translation": list(shift),
            "history_state_used": False,
            "up_ref_zero": True,
        },
        "core_preservation": {
            "Mf_erased_standardized_grafted_or_replaced": False,
            "deep_input_Mf_sha256": hashlib.sha256(np.ascontiguousarray(state.Mf).tobytes()).hexdigest(),
        },
        "reason": None if (primary_valid and controls_valid and sham_exact) else "probe_arm_or_sham_invalid",
    }


def factorial_scalar(values_by_history: dict[str, float]) -> dict[str, float]:
    return bh.factorial_scalar(values_by_history)


def factorial_vector(values_by_history: dict[str, Sequence[float]]) -> dict[str, np.ndarray]:
    return bh.factorial_vector(values_by_history)


def _branch_public(history: dict) -> dict:
    out = {key: value for key, value in history.items()
           if key not in {"state", "tracker", "patch", "focal_region", "entity", "region"}}
    if "deep" in out:
        out["deep"] = {
            key: value for key, value in out["deep"].items()
            if key not in {"state", "region", "entity"}
        }
    return _safe(out)


def _run_world_unchecked(seed: int, manifest: dict) -> dict:
    checkpoint = make_checkpoint(int(seed))
    focal_id = checkpoint["focal_id"]
    base = {
        "seed": int(seed),
        "prehistory_eligible": focal_id is not None,
        "n_detected_prehistory_components": checkpoint["n_detected_components"],
        "n_eligible_focal_candidates": sum(row["eligible"] for row in checkpoint["eligibility"]),
        "eligibility_metrics": checkpoint["eligibility"],
        "focal_tracker_id": focal_id,
        "execution_order": list(execution_order(seed)),
        "complete_block": False,
    }
    if focal_id is None:
        base["reason"] = "no_pre_history_eligible_focal_target"
        return base
    focal_entity = checkpoint["entities"][focal_id]
    base["focal_target"] = {
        "canonical_tracker_id": int(focal_id),
        "centroid": [float(value) for value in focal_entity.centroid],
        "size": int(focal_entity.size),
        "mass": float(focal_entity.mass),
        "rg": float(focal_entity.rg),
        "mask_sha256": _mask_digest(checkpoint["tracker_masks"][focal_id]),
        "selection_rule": "lowest canonical tracker ID among eligible targets",
    }
    clone_validation = validate_four_clones(checkpoint)
    base["clone_checkpoint"] = {
        "valid": clone_validation["valid"],
        "checkpoint_bundle_sha256": checkpoint["checkpoint_bundle_sha256"],
        "serialized_state_payload_sha256": checkpoint["serialized_state_payload_sha256"],
        "canonical_state_bytes_sha256": checkpoint["canonical_state_bytes_sha256"],
        "tracker_mapping_sha256": checkpoint["tracker_mapping_sha256"],
        "scheduler": checkpoint["scheduler"],
        "rng_state": checkpoint["rng_state"],
        "four_branch_validation": clone_validation,
    }
    if not clone_validation["valid"]:
        raise RuntimeError(f"exact clone failure in world {seed}")

    histories = run_histories(checkpoint, execution_order(seed))
    for name in HISTORY_NAMES:
        branch = histories[name]
        branch["posthistory_alive"] = bool(branch["valid"])
        branch["deep_valid"] = False
        branch["complete_probe"] = False
        if not branch["valid"]:
            continue
        deep = turnover_fixed(branch["state"], branch["focal_region"])
        branch["deep"] = deep
        branch["deep_valid"] = bool(deep["valid"])
        if not deep["valid"]:
            branch["reason"] = deep["reason"]

    reference = no_drive_reference(checkpoint) if any(
        histories[name]["deep_valid"] for name in HISTORY_NAMES
    ) else {"valid": False, "reason": "no_deep_branch"}
    base["common_boundary_reference"] = (
        {key: _safe(value) for key, value in reference.items() if key not in {"state", "entity"}}
        if reference["valid"] else reference
    )
    if reference["valid"]:
        for name in HISTORY_NAMES:
            branch = histories[name]
            if not branch["deep_valid"]:
                continue
            probe = probe_branch(branch["deep"], reference, focal_entity, branch["patch"])
            branch["probe"] = probe
            branch["complete_probe"] = bool(probe["valid"])
            if not probe["valid"]:
                branch["reason"] = probe["reason"]

    base["branches"] = {name: _branch_public(histories[name]) for name in HISTORY_NAMES}
    complete = bool(reference["valid"] and all(histories[name]["complete_probe"] for name in HISTORY_NAMES))
    base["complete_block"] = complete
    if not complete:
        base["reason"] = "one_or_more_history_branches_incomplete"
        return base

    first_stage_contrasts = {}
    for feature in FIRST_STAGE_SCALARS:
        first_stage_contrasts[feature] = factorial_scalar({
            name: histories[name]["probe"]["first_stage"][feature] for name in HISTORY_NAMES
        })
    vector_contrasts = factorial_vector({
        name: histories[name]["probe"]["first_stage"]["full_field_vector"] for name in HISTORY_NAMES
    })
    first_stage_contrasts["full_field"] = {
        contrast: {
            "vector": vector.tolist(),
            "rms": float(np.sqrt(np.mean(vector * vector))),
            "l2": float(np.linalg.norm(vector)),
        }
        for contrast, vector in vector_contrasts.items()
    }
    arm_contrasts = {}
    for arm in ALL_ARMS:
        arm_contrasts[arm] = {
            "tracked": factorial_scalar({
                name: histories[name]["probe"]["arms"][arm]["integrated_tracked_step40"]
                for name in HISTORY_NAMES
            }),
            "fixed": factorial_scalar({
                name: histories[name]["probe"]["arms"][arm]["integrated_fixed_step40"]
                for name in HISTORY_NAMES
            }),
            "instantaneous_step40": factorial_scalar({
                name: histories[name]["probe"]["arms"][arm]["instantaneous_tracked_at_step40"]
                for name in HISTORY_NAMES
            }),
        }
    base["first_stage_contrasts"] = first_stage_contrasts
    base["arm_contrasts"] = arm_contrasts
    base["transport"] = {
        contrast: float(arm_contrasts["isolated"]["tracked"][contrast]
                        - arm_contrasts["coupled"]["tracked"][contrast])
        for contrast in ("dose", "order", "interaction")
    }
    base["lam_plus_mediation"] = {
        condition: {
            contrast: float(arm_contrasts[f"{condition}_lamplus0"]["tracked"][contrast]
                            - arm_contrasts[condition]["tracked"][contrast])
            for contrast in ("dose", "order", "interaction")
        }
        for condition in ("coupled", "isolated")
    }
    base["reason"] = None
    return _safe(base)


def run_world(seed: int, manifest: dict) -> dict:
    if int(seed) not in DEV_SEEDS:
        raise ValueError(f"REFUSED seed {seed}: exact DEV family is 57001-57024")
    return _run_world_unchecked(int(seed), manifest)


def _summary(values: Sequence[float], expected: str | None = None) -> dict:
    return bh._summary(values, expected=expected)


def _two_sided_gate(summary: dict) -> bool:
    if int(summary.get("n_worlds", 0)) < 4:
        return False
    lo, hi = summary.get("ci95_t", [None, None])
    if lo is None or hi is None or not (lo > 0 or hi < 0):
        return False
    return max(summary.get("positive", 0), summary.get("negative", 0)) >= summary.get(
        "required_same_orientation", 10**9
    )


def aggregate(worlds: list[dict]) -> dict:
    complete = [world for world in worlds if world.get("complete_block")]
    eligible = [world for world in worlds if world.get("prehistory_eligible")]
    first_stage = {
        feature: {
            contrast: _summary(
                [world["first_stage_contrasts"][feature][contrast] for world in complete],
                expected=("positive" if feature == "mplus_mean" and contrast == "dose" else
                          "negative" if feature == "mminus_mean" and contrast == "order" else None),
            )
            for contrast in ("dose", "order", "interaction")
        }
        for feature in FIRST_STAGE_SCALARS
    }
    first_stage["full_field"] = {
        contrast: bh._vector_alignment([
            world["first_stage_contrasts"]["full_field"][contrast]["vector"] for world in complete
        ]) for contrast in ("dose", "order", "interaction")
    }
    feeding = {
        arm: {
            contrast: _summary(
                [world["arm_contrasts"][arm]["tracked"][contrast] for world in complete],
                expected=("positive" if arm in PRIMARY_ARMS and contrast == "dose" else None),
            )
            for contrast in ("dose", "order", "interaction")
        }
        for arm in ALL_ARMS
    }
    fixed_control = {
        arm: {
            contrast: _summary([
                world["arm_contrasts"][arm]["fixed"][contrast] for world in complete
            ]) for contrast in ("dose", "order", "interaction")
        }
        for arm in PRIMARY_ARMS
    }
    transport = {
        contrast: _summary([world["transport"][contrast] for world in complete])
        for contrast in ("dose", "order", "interaction")
    }
    survival = {
        name: {"assigned": 0, "posthistory_alive": 0, "deep_alive": 0, "complete_probe": 0}
        for name in HISTORY_NAMES
    }
    survival_world_contrasts = {contrast: [] for contrast in ("dose", "order", "interaction")}
    for world in eligible:
        outcomes = {}
        for name in HISTORY_NAMES:
            branch = world["branches"][name]
            survival[name]["assigned"] += 1
            survival[name]["posthistory_alive"] += int(branch.get("posthistory_alive", False))
            survival[name]["deep_alive"] += int(branch.get("deep_valid", False))
            survival[name]["complete_probe"] += int(branch.get("complete_probe", False))
            outcomes[name] = float(branch.get("deep_valid", False))
        contrasts = factorial_scalar(outcomes)
        for contrast, value in contrasts.items():
            survival_world_contrasts[contrast].append(value)
    survival_contrasts = {
        contrast: _summary(values) for contrast, values in survival_world_contrasts.items()
    }
    survival_effect = any(_two_sided_gate(summary) for summary in survival_contrasts.values())

    enough = len(complete) >= 4
    manipulation_valid = bool(enough and all(
        world["branches"][name]["probe"]["sham_exact"]
        for world in complete for name in HISTORY_NAMES
    ))
    dose_stage = bool(enough and first_stage["mplus_mean"]["dose"].get(
        "passes_expected_orientation_and_ci"
    ))
    order_stage = bool(enough and first_stage["mminus_mean"]["order"].get(
        "passes_expected_orientation_and_ci"
    ))
    dose_feed = bool(enough and feeding["isolated"]["dose"].get(
        "passes_expected_orientation_and_ci"
    ))
    coupled_dose_direction = bool(
        enough and feeding["coupled"]["dose"].get("median", 0.0) > 0
    )
    iso_order = feeding["isolated"]["order"]
    coupled_order = feeding["coupled"]["order"]
    order_feed = bool(
        enough and _two_sided_gate(iso_order)
        and iso_order.get("median", 0.0) != 0 and coupled_order.get("median", 0.0) != 0
        and math.copysign(1.0, iso_order["median"]) == math.copysign(1.0, coupled_order["median"])
    )

    if not enough:
        conclusion = "DEV-FEASIBILITY-FAIL"
    elif not manipulation_valid:
        conclusion = "MANIPULATION_INVALID"
    elif survival_effect:
        conclusion = "SURVIVAL_EFFECT"
    elif not dose_stage and not order_stage:
        conclusion = "NO_MEMORY_FIRST_STAGE"
    elif order_stage and not order_feed:
        conclusion = "ORDER_STATE_WITHOUT_FEEDING"
    elif dose_stage and dose_feed and coupled_dose_direction and order_stage and order_feed:
        conclusion = "DOSE_AND_ORDER"
    elif dose_stage and dose_feed and coupled_dose_direction and not (order_stage and order_feed):
        conclusion = "DOSE_ONLY"
    elif (dose_stage or order_stage) and not (dose_feed or order_feed):
        conclusion = "NO_TRANSPORT"
    else:
        conclusion = "UNRESOLVED"
    full_order = first_stage["full_field"]["order"]
    prereg_go = bool(
        conclusion == "DOSE_AND_ORDER" and manipulation_valid and enough
        and full_order.get("median_loo_cosine") is not None
        and full_order["median_loo_cosine"] > 0
    )
    return {
        "n_planned_original_worlds": len(DEV_SEEDS),
        "n_pre_history_eligible_worlds": len(eligible),
        "pre_history_eligibility_rate": len(eligible) / len(DEV_SEEDS),
        "n_complete_valid_worlds": len(complete),
        "complete_block_rate_all_worlds": len(complete) / len(DEV_SEEDS),
        "complete_block_rate_eligible_worlds": len(complete) / len(eligible) if eligible else None,
        "complete_world_seeds": [world["seed"] for world in complete],
        "survival_by_history": survival,
        "survival_factorial_contrasts": survival_contrasts,
        "survival_effect_detected": survival_effect,
        "first_stage": first_stage,
        "feeding_contrasts": feeding,
        "fixed_mask_convergence_control": fixed_control,
        "transport_isolated_minus_coupled": transport,
        "lam_plus_mediation": {
            condition: {
                contrast: _summary([
                    world["lam_plus_mediation"][condition][contrast] for world in complete
                ]) for contrast in ("dose", "order", "interaction")
            }
            for condition in ("coupled", "isolated")
        },
        "gates": {
            "minimum_four_complete_original_worlds": enough,
            "exact_clone_valid_all_eligible_worlds": all(
                world["clone_checkpoint"]["valid"] for world in eligible
            ),
            "manipulation_sham_exact": manipulation_valid if enough else None,
            "dose_first_stage_positive": dose_stage if enough else None,
            "order_first_stage_protocol_negative": order_stage if enough else None,
            "isolated_dose_feeding_positive": dose_feed if enough else None,
            "coupled_dose_compatible_direction": coupled_dose_direction if enough else None,
            "isolated_order_feeding_nonzero_consistent_and_coupled_compatible": order_feed if enough else None,
            "common_history_independent_boundary": True,
            "isolated_up_ref_zero": True,
            "core_Mf_manipulated": False,
        },
        "conclusion": conclusion,
        "conclusion_reason": "FEWER_THAN_FOUR_COMPLETE_WORLDS" if not enough else None,
        "prereg_candidate_go": prereg_go,
        "prospective_execution_authorized": False,
        "statistical_unit": "original source world",
        "counterfactual_branches_count_toward_n": False,
    }


def build_result(manifest: dict, worlds: list[dict], *, status: str) -> dict:
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "canonical_parent": CANONICAL_PARENT,
        "manifest_sha256": MANIFEST_SHA256,
        "seeds": list(DEV_SEEDS),
        "design": {
            "statistical_unit": "original source world",
            "potential_outcomes_per_world": 4,
            "potential_outcomes_are_replicates": False,
            "primary_continuations_per_complete_world": 8,
            "fixed_deep_elapsed_steps": DEEP_STEPS,
            "deep_material_threshold": M_TARGET,
            "primary_endpoint": "integrated tracked uptake through frozen step 40",
            "fixed_mask_role": "tracker-independent convergence control",
            "common_random_numbers": "no stochastic draws exist after initialization; exact deterministic continuations",
            "independence_limit": (
                "The simulator can generate all potential outcomes from one pre-treatment state; "
                "a physical experiment observes only one. External generalization uses independent source worlds."
            ),
        },
        "worlds": worlds,
    }
    if status == "COMPLETE":
        result["summary"] = aggregate(worlds)
    return _safe(result)


def atomic_write_json(path: Path, payload: dict) -> str:
    text = json.dumps(_safe(payload), indent=2, sort_keys=True) + "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
    return sha256_file(path)


def run_family(manifest: dict, output: Path) -> dict:
    worlds = []
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing.get("schema") != SCHEMA or existing.get("manifest_sha256") != MANIFEST_SHA256:
            raise RuntimeError("refusing incompatible partial result")
        worlds = list(existing.get("worlds", []))
    done = {int(world["seed"]) for world in worlds}
    for seed in DEV_SEEDS:
        if seed in done:
            print(f"seed {seed}: resume-skip", flush=True)
            continue
        world = run_world(seed, manifest)
        worlds.append(world)
        atomic_write_json(output, build_result(manifest, worlds, status="PARTIAL"))
        print(
            f"seed {seed}: eligible={world.get('prehistory_eligible')} "
            f"complete={world.get('complete_block')} reason={world.get('reason')}",
            flush=True,
        )
    result = build_result(manifest, worlds, status="COMPLETE")
    digest = atomic_write_json(output, result)
    print(json.dumps(result["summary"], indent=2, sort_keys=True), flush=True)
    print("RESULT_SHA256", digest, flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_and_validate_manifest(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    run_family(manifest, args.output)


if __name__ == "__main__":
    main()
