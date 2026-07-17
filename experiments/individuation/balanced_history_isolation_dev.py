"""BALANCED-HISTORY-ISOLATION-00 — bounded DEV-only factorial experiment.

This runner implements one pre-data 2 (dose) x 2 (temporal order) history
assignment in four spatially separated targets per original world.  It then
follows all four targets longitudinally to deep material turnover and compares
ordinary coupled continuation with the already-qualified two-cell in-place
boundary clamp under a history-independent global rule (``up_ref = 0``).

The original world is the statistical unit.  Target outcomes are combined into
factorial contrasts inside a world; targets are never treated as replicates.
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
from scipy.optimize import linear_sum_assignment
from scipy.stats import t as student_t

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import bijective_tracker as bt
from experiments.individuation import causal_confirm as cc
from experiments.individuation import material_tracer as mt
from experiments.individuation import nonmerging_confirm as nm
from experiments.individuation.turnover_diag_engine import DiagEngine


SCHEMA = "BALANCED-HISTORY-ISOLATION-00-DEV-v1"
MANIFEST_SCHEMA = "BALANCED-HISTORY-ISOLATION-00-ASSIGNMENT-v1"
CANONICAL_PARENT = "6d1a5f718b965d2896f2a3e4d6cbcf5c8c83542f"
MANIFEST_SHA256 = "83eaffd530cfb82d07010f0e5171fc631dc98251de9b4c3be2dd2af98a33f08b"
MODE = "DEV_ONLY_NO_PROSPECTIVE_AUTHORIZATION"

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "docs" / "individuation" / "BALANCED_HISTORY_ISOLATION_00_ASSIGNMENT_MANIFEST.json"
DEV_SEEDS = tuple(range(55001, 55025))

K = 4
N = cc.N
GRID = N * N
WARM = cc.WARM
PHASE = cc.PHASE
SETTLE = cc.SETTLE
MINSIZE = cc.MINSIZE
SEP = cc.SEP
M_TARGET = 0.25
TURN_CAP = 1500
COVER_CAP = nm.COVER_CAP
THETA = nm.THETA
SETTLE_STD = nm.SETTLE_STD
STIM_AMP = nm.STIM_AMP
STIM_DUR = nm.STIM_DUR
HORIZON = nm.HORIZON
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
FIRST_STAGE_SCALARS = (
    "m1_mean", "m2_mean", "mplus_mean", "mminus_mean", "mf_m1_std",
    "mf_m2_std", "mf_diff_std", "mf_spatial_corr", "mf_roughness",
    "body_size", "body_mass", "body_rg", "core_rho_mass", "core_N_mean",
    "core_c_mean", "core_u_mean", "core_v_mean", "core_sigma_mean",
    "prehistory_size", "prehistory_mass", "prehistory_rg", "patch_total",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def state_hash(state) -> str:
    return ops.state_sha256(state)


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


def expected_assignment(seed: int) -> tuple[str, ...]:
    """Cyclic Latin square, keyed only by the frozen world seed."""
    seed = int(seed)
    if seed not in DEV_SEEDS:
        raise ValueError(f"REFUSED seed {seed}: exact DEV family is 55001-55024")
    rotation = (seed - DEV_SEEDS[0]) % K
    return tuple(HISTORY_NAMES[(slot + rotation) % K] for slot in range(K))


def manifest_assignment(seed: int, manifest: dict) -> tuple[str, ...]:
    row = manifest["assignments"][str(int(seed))]
    return tuple(row[str(slot)] for slot in range(K))


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
        raise RuntimeError("manifest episode duration mismatch")
    if int(manifest.get("inter_episode_gap_steps", -1)) != 0:
        raise RuntimeError("manifest inter-episode gap mismatch")
    recovered = {name: tuple(manifest["histories"][name][key] for key in ("a1", "a2"))
                 for name in HISTORY_NAMES}
    if recovered != HISTORIES:
        raise RuntimeError("manifest history values mismatch")
    if manifest.get("primary_global_rule", {}).get("up_ref") != 0:
        raise RuntimeError("manifest primary global rule mismatch")
    for seed in DEV_SEEDS:
        actual = manifest_assignment(seed, manifest)
        expected = expected_assignment(seed)
        if actual != expected:
            raise RuntimeError(f"manifest/runtime assignment mismatch for seed {seed}: {actual} != {expected}")
        if set(actual) != set(HISTORY_NAMES):
            raise RuntimeError(f"seed {seed} does not receive all four histories")
    counts = {slot: {name: 0 for name in HISTORY_NAMES} for slot in range(K)}
    for seed in DEV_SEEDS:
        for slot, name in enumerate(expected_assignment(seed)):
            counts[slot][name] += 1
    if any(value != len(DEV_SEEDS) // K for row in counts.values() for value in row.values()):
        raise RuntimeError(f"Latin-square imbalance: {counts}")
    prohibited = set(range(50001, 50011)) | set(range(51000, 54121))
    if prohibited.intersection(DEV_SEEDS):
        raise RuntimeError("forbidden seed namespace reuse")
    if not manifest.get("namespace_audit", {}).get("fresh_semantic_integer_audit_pass"):
        raise RuntimeError("namespace audit not frozen PASS")


def load_and_validate_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    if sha256_file(path) != MANIFEST_SHA256:
        raise RuntimeError("assignment manifest SHA-256 mismatch")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest_payload(manifest)
    return manifest


def periodic_distance(a: Sequence[float], b: Sequence[float]) -> float:
    delta = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    delta = np.minimum(delta, N - delta)
    return float(np.hypot(*delta))


def pick_four(entities: Iterable) -> list:
    selected = []
    for entity in sorted(entities, key=lambda item: -item.size):
        if entity.size < MINSIZE:
            continue
        if all(periodic_distance(entity.centroid, other.centroid) >= SEP for other in selected):
            selected.append(entity)
        if len(selected) == K:
            break
    return selected


def mask(entity) -> np.ndarray:
    out = np.zeros((N, N), dtype=bool)
    out[entity.cells[:, 0], entity.cells[:, 1]] = True
    return out


def gaussian_patch(center: Sequence[float], sigma: float) -> np.ndarray:
    return cc.patch(float(center[0]), float(center[1]), float(sigma))


def _entities_and_masks(state):
    entities = list(detect(state, MCM_CONFIG.DET))
    return entities, [mask(entity) for entity in entities]


def _entity_for_track(entities: list, region: np.ndarray):
    return max(entities, key=lambda entity: int((mask(entity) & region).sum()), default=None)


def _tracker_update(tracker: bt.BijectiveTracker, state, step: int) -> dict:
    entities, masks = _entities_and_masks(state)
    events = tracker.update(masks, step)
    coverage = (max((int(item.sum()) for item in masks), default=0) / GRID)
    return {"entities": entities, "masks": masks, "events": events, "coverage": float(coverage)}


def _all_tracks_alive(tracker: bt.BijectiveTracker) -> bool:
    return len(tracker.tracks) == K and all(track.status == bt.ALIVE for track in tracker.tracks)


def _history_survival(tracker: bt.BijectiveTracker, assignments: Sequence[str]) -> dict:
    return {assignments[slot]: bool(tracker.tracks[slot].status == bt.ALIVE) for slot in range(K)}


def apply_histories(warm_state, targets: list, assignments: Sequence[str], engine) -> dict:
    """Apply two genuine consecutive episodes while tracking all four targets."""
    state = warm_state.copy()
    patches = [gaussian_patch(entity.centroid, max(3.0, 0.8 * entity.rg)) for entity in targets]
    tracker = bt.BijectiveTracker(theta=THETA)
    tracker.seed([mask(entity) for entity in targets], 0)
    first_events = {}
    step = 0
    for phase in (0, 1):
        for _ in range(PHASE):
            for slot, history_name in enumerate(assignments):
                state.N = state.N + HISTORIES[history_name][phase] * patches[slot]
            state = engine.step(state)
            step += 1
            update = _tracker_update(tracker, state, step)
            for track_id, status in update["events"].items():
                first_events.setdefault(str(track_id), {"step": step, "status": status})
            if first_events:
                return {
                    "valid": False, "state": state, "tracker": tracker,
                    "first_events": first_events, "patches": patches,
                    "history_survival": _history_survival(tracker, assignments),
                    "reason": "history_tracker_event",
                }
    for _ in range(SETTLE):
        state = engine.step(state)
        step += 1
        update = _tracker_update(tracker, state, step)
        for track_id, status in update["events"].items():
            first_events.setdefault(str(track_id), {"step": step, "status": status})
        if first_events:
            return {
                "valid": False, "state": state, "tracker": tracker,
                "first_events": first_events, "patches": patches,
                "history_survival": _history_survival(tracker, assignments),
                "reason": "posthistory_tracker_event",
            }
    return {
        "valid": _all_tracks_alive(tracker), "state": state, "tracker": tracker,
        "first_events": first_events, "patches": patches,
        "history_survival": _history_survival(tracker, assignments),
        "reason": None,
    }


def turnover_to_deep(state, region_masks: list[np.ndarray], assignments: Sequence[str], engine) -> dict:
    traced, base = mt.seed_tracers(state, region_masks)
    mt.assert_no_feed_collision(engine.tracer, base, TURN_CAP + 2)
    tracker = bt.BijectiveTracker(theta=THETA)
    tracker.seed([region.copy() for region in region_masks], 0)
    first_events = {}
    final_material = None
    for step in range(1, TURN_CAP + 1):
        traced = engine.step(traced)
        update = _tracker_update(tracker, traced, step)
        for track_id, status in update["events"].items():
            first_events.setdefault(str(track_id), {"step": step, "status": status})
        alive_masks = [track.mask if track.status == bt.ALIVE else None for track in tracker.tracks]
        material = mt.read_material(traced, base, alive_masks)
        final_material = material
        if first_events:
            return {
                "valid": False, "deep": None, "first_events": first_events,
                "history_survival": _history_survival(tracker, assignments),
                "last_material": material, "reason": "turnover_tracker_event",
            }
        if update["coverage"] >= COVER_CAP:
            return {
                "valid": False, "deep": None, "first_events": first_events,
                "history_survival": _history_survival(tracker, assignments),
                "last_material": material, "reason": "turnover_coverage_fail",
            }
        if all(item is not None and np.isfinite(item["M"]) and item["M"] <= M_TARGET for item in material):
            entities = update["entities"]
            matched = [_entity_for_track(entities, track.mask) for track in tracker.tracks]
            if all(entity is not None for entity in matched):
                return {
                    "valid": True,
                    "deep": {
                        "step": step,
                        "state": traced.copy(),
                        "regions": [track.mask.copy() for track in tracker.tracks],
                        "centroids": [[float(v) for v in entity.centroid] for entity in matched],
                        "entities": matched,
                        "material": material,
                    },
                    "first_events": first_events,
                    "history_survival": {name: True for name in assignments},
                    "last_material": material,
                    "reason": None,
                }
    return {
        "valid": False, "deep": None, "first_events": first_events,
        "history_survival": _history_survival(tracker, assignments),
        "last_material": final_material, "reason": "turnover_cap",
    }


def _centered_patch(array: np.ndarray, center: Sequence[float], radius: int = CORE_RADIUS) -> np.ndarray:
    cy, cx = (int(round(float(center[0]))) % N, int(round(float(center[1]))) % N)
    offsets = np.arange(-radius, radius + 1)
    ys = (cy + offsets) % N
    xs = (cx + offsets) % N
    return array[np.ix_(ys, xs)]


def _roughness(values: np.ndarray, region: np.ndarray) -> float:
    terms = []
    for axis in (-2, -1):
        valid = region & np.roll(region, -1, axis)
        if valid.any():
            delta = values - np.roll(values, -1, axis)
            terms.append(np.square(delta[valid]))
    return float(np.mean(np.concatenate(terms))) if terms else 0.0


def first_stage_target(state, region: np.ndarray, center: Sequence[float], entity, pre_entity, patch_array) -> dict:
    rho_safe = np.maximum(state.rho, 1e-12)
    memory = state.Mf / rho_safe[None]
    m1 = memory[0][region]
    m2 = memory[1][region]
    mplus = np.tanh(m1 + m2)
    mminus = np.tanh(m1 - m2)
    summaries = []
    for values in (m1, m2):
        summaries.extend([
            float(values.mean()), float(values.std()), float(np.percentile(values, 10)),
            float(np.percentile(values, 50)), float(np.percentile(values, 90)),
        ])
    summaries.append(float((m1 - m2).std()))
    corr = 0.0
    if m1.size > 1 and float(m1.std()) > 0 and float(m2.std()) > 0:
        corr = float(np.corrcoef(m1, m2)[0, 1])
    _, core, _ = ns.core_and_collar(state.rho.shape, center)
    circle = np.fromfunction(
        lambda y, x: (y - CORE_RADIUS) ** 2 + (x - CORE_RADIUS) ** 2 <= CORE_RADIUS ** 2,
        (2 * CORE_RADIUS + 1, 2 * CORE_RADIUS + 1), dtype=int,
    ).astype(bool)
    vec = np.concatenate([
        _centered_patch(memory[0], center)[circle],
        _centered_patch(memory[1], center)[circle],
    ])
    u = state.U / rho_safe
    v = state.V / rho_safe
    sigma = (u - v) / (u + v + 1e-12)
    return {
        "m1_mean": float(m1.mean()),
        "m2_mean": float(m2.mean()),
        "mplus_mean": float(mplus.mean()),
        "mminus_mean": float(mminus.mean()),
        "mf_m1_std": float(m1.std()),
        "mf_m2_std": float(m2.std()),
        "mf_diff_std": float((m1 - m2).std()),
        "mf_spatial_corr": corr,
        "mf_roughness": float(_roughness(memory[0], region) + _roughness(memory[1], region)),
        "frozen_11d": summaries,
        "full_field_vector": vec.tolist(),
        "body_size": int(entity.size),
        "body_mass": float(entity.mass),
        "body_rg": float(entity.rg),
        "core_rho_mass": float(state.rho[core].sum()),
        "core_N_mean": float(state.N[core].mean()),
        "core_c_mean": float(state.c[core].mean()),
        "core_u_mean": float(u[core].mean()),
        "core_v_mean": float(v[core].mean()),
        "core_sigma_mean": float(sigma[core].mean()),
        "prehistory_size": int(pre_entity.size),
        "prehistory_mass": float(pre_entity.mass),
        "prehistory_rg": float(pre_entity.rg),
        "patch_total": float(patch_array.sum()),
    }


def factorial_scalar(values_by_history: dict[str, float]) -> dict[str, float]:
    le = float(values_by_history["H_L_EARLY"])
    ll = float(values_by_history["H_L_LATE"])
    he = float(values_by_history["H_H_EARLY"])
    hl = float(values_by_history["H_H_LATE"])
    return {
        "dose": 0.5 * (he + hl) - 0.5 * (le + ll),
        "order": 0.5 * ((le - ll) + (he - hl)),
        "interaction": (he - hl) - (le - ll),
    }


def factorial_vector(values_by_history: dict[str, Sequence[float]]) -> dict[str, np.ndarray]:
    arrays = {key: np.asarray(value, dtype=float) for key, value in values_by_history.items()}
    le, ll = arrays["H_L_EARLY"], arrays["H_L_LATE"]
    he, hl = arrays["H_H_EARLY"], arrays["H_H_LATE"]
    return {
        "dose": 0.5 * (he + hl) - 0.5 * (le + ll),
        "order": 0.5 * ((le - ll) + (he - hl)),
        "interaction": (he - hl) - (le - ll),
    }


def _reference_world(seed: int, deep_step: int, n_extra_cohorts: int = K):
    """Same seed/time, no history drive; extra tracer cohorts are passive zeros."""
    engine = cc.build(cc.MEM_INTACT)
    state = cc.seed_world(seed)
    for _ in range(WARM + 2 * PHASE + SETTLE):
        state = engine.step(state)
    zeros = np.zeros((n_extra_cohorts, N, N), dtype=state.C.dtype)
    state.C = np.concatenate([state.C, zeros], axis=0)
    for _ in range(deep_step):
        state = engine.step(state)
    entities = [entity for entity in detect(state, MCM_CONFIG.DET)
                if 4 <= int(entity.size) < int(COVER_CAP * GRID)]
    if not entities:
        raise RuntimeError("no on-manifold history-independent reference component")
    entities.sort(key=lambda entity: (int(entity.size), float(entity.centroid[0]), float(entity.centroid[1])))
    reference = entities[(len(entities) - 1) // 2]
    return state, tuple(float(value) for value in reference.centroid)


def core_rings(state, centroids: Sequence[Sequence[float]], regions: Sequence[np.ndarray]) -> dict:
    cores, rings, partitions = [], [], []
    for center, region in zip(centroids, regions):
        partition, core, ring = ns.core_and_collar(state.rho.shape, center)
        if np.any(region & ~core):
            return {"valid": False, "reason": "body_outside_qualified_core"}
        cores.append(core); rings.append(ring); partitions.append(partition)
    for i in range(K):
        for j in range(i + 1, K):
            if np.any(rings[i] & rings[j]) or np.any(cores[i] & rings[j]) or np.any(cores[j] & rings[i]):
                return {"valid": False, "reason": "overlapping_core_or_barrier"}
    union = np.logical_or.reduce(rings)
    return {"valid": True, "cores": cores, "rings": rings, "union": union, "partitions": partitions}


def _empty_frame_for_union(state, union: np.ndarray) -> dict:
    count = int(union.sum())
    frame = {}
    for field in ns.STATE_FIELDS:
        array = getattr(state, field)
        shape = (count,) if array.ndim == 2 else (array.shape[0], count)
        frame[field] = np.empty(shape, dtype=array.dtype)
    return frame


def record_probe_boundary(source_state, source_engine, rings: Sequence[np.ndarray],
                          shifts: Sequence[tuple[int, int]], *, label: str) -> ns.BoundaryDriver:
    """Record one common predeclared standardized-input trajectory for all rings."""
    union = np.logical_or.reduce(rings)
    uy, ux = np.where(union)
    index_map = np.full((N, N), -1, dtype=int)
    index_map[uy, ux] = np.arange(len(uy))
    current = standardized_probe_start(source_state)
    frames = []
    for step in range(1, SETTLE_STD + HORIZON + 1):
        if SETTLE_STD < step <= SETTLE_STD + STIM_DUR:
            current.N = current.N + STIM_AMP
        current = source_engine.step(current)
        frame = _empty_frame_for_union(current, union)
        for ring, shift in zip(rings, shifts):
            ys, xs = np.where(ring)
            positions = index_map[ys, xs]
            for field in ns.STATE_FIELDS:
                array = getattr(current, field)
                rolled = np.roll(array, shift, axis=(-2, -1)) if shift != (0, 0) else array
                if array.ndim == 2:
                    frame[field][positions] = rolled[ys, xs]
                else:
                    frame[field][:, positions] = rolled[:, ys, xs]
        frames.append(frame)
    return ns.BoundaryDriver(ring=union, frames=frames, label=label)


def standardized_probe_start(state):
    """Clone a state and apply the frozen common nutrient reset without touching other fields."""
    current = state.copy()
    current.N = np.full_like(current.N, cc.N0)
    return current


def measure_arm(state, regions: Sequence[np.ndarray], engine) -> dict:
    if getattr(engine, "driver", None) is not None:
        engine.driver.reset()
    current = standardized_probe_start(state)
    tracker = bt.BijectiveTracker(theta=THETA)
    tracker.seed([region.copy() for region in regions], 0)
    events = {}
    max_coverage = 0.0
    fixed = None
    tracked = [0.0] * K
    fixed_uptake = [0.0] * K
    step40_uptake = [None] * K
    for step in range(1, SETTLE_STD + HORIZON + 1):
        if SETTLE_STD < step <= SETTLE_STD + STIM_DUR:
            current.N = current.N + STIM_AMP
        current = engine.step(current)
        update = _tracker_update(tracker, current, step)
        max_coverage = max(max_coverage, update["coverage"])
        for track_id, status in update["events"].items():
            events.setdefault(str(track_id), {"step": step, "status": status})
        if step == SETTLE_STD:
            fixed = [track.mask.copy() if track.status == bt.ALIVE else np.zeros((N, N), bool)
                     for track in tracker.tracks]
        if step > SETTLE_STD:
            for slot, track in enumerate(tracker.tracks):
                fixed_uptake[slot] += float(current.uptake[fixed[slot]].sum())
                if track.status == bt.ALIVE:
                    value = float(current.uptake[track.mask].sum())
                    tracked[slot] += value
                    if step == SETTLE_STD + HORIZON:
                        step40_uptake[slot] = value
    finite = all(np.isfinite(value) for value in tracked + fixed_uptake)
    valid = bool(_all_tracks_alive(tracker) and not events and max_coverage < COVER_CAP and finite)
    return {
        "integrated_tracked": tracked,
        "integrated_fixed": fixed_uptake,
        "step40_instantaneous_tracked": step40_uptake,
        "statuses": [track.status for track in tracker.tracks],
        "events": events,
        "max_coverage": float(max_coverage),
        "valid": valid,
        "final_state_hash": state_hash(current),
    }


def _arm_contrasts(arm: dict, assignments: Sequence[str], key: str) -> dict[str, float] | None:
    if not arm["valid"]:
        return None
    values = {assignments[slot]: arm[key][slot] for slot in range(K)}
    return factorial_scalar(values)


def _pairwise_numeric_equal(a: Sequence[float], b: Sequence[float]) -> bool:
    return bool(np.allclose(np.asarray(a), np.asarray(b), atol=NUMERIC_ATOL, rtol=NUMERIC_RTOL))


def run_world(seed: int, manifest: dict) -> dict:
    planned_assignments = expected_assignment(seed)
    intact_engine = cc.build(cc.MEM_INTACT)
    state = cc.seed_world(seed)
    for _ in range(WARM):
        state = intact_engine.step(state)
    targets = pick_four(detect(state, MCM_CONFIG.DET))
    base = {
        "seed": int(seed),
        "planned_assignment": {str(slot): planned_assignments[slot] for slot in range(K)},
        "prehistory_eligible": len(targets) == K,
        "n_selected_targets": len(targets),
        "assignment_applied": False,
        "deep_valid": False,
        "complete_block": False,
    }
    if len(targets) < K:
        base["reason"] = "fewer_than_four_pre_history_eligible_targets"
        return base
    assignments = manifest_assignment(seed, manifest)
    if assignments != planned_assignments:
        raise RuntimeError(f"runtime assignment mismatch after eligibility for seed {seed}")
    base["assignment_applied"] = True
    base["prehistory_targets"] = [{
        "slot": slot, "history": assignments[slot], "size": int(entity.size),
        "mass": float(entity.mass), "rg": float(entity.rg),
        "centroid": [float(value) for value in entity.centroid],
    } for slot, entity in enumerate(targets)]

    written = apply_histories(state, targets, assignments, intact_engine)
    base["history_survival"] = written["history_survival"]
    base["history_events"] = written["first_events"]
    if not written["valid"]:
        base["reason"] = written["reason"]
        return base
    s0 = written["state"]
    regions0 = [track.mask.copy() for track in written["tracker"].tracks]
    turnover = turnover_to_deep(s0, regions0, assignments, intact_engine)
    base["deep_survival"] = turnover["history_survival"]
    base["turnover_events"] = turnover["first_events"]
    base["last_material"] = turnover["last_material"]
    if not turnover["valid"]:
        base["reason"] = turnover["reason"]
        return base

    deep = turnover["deep"]
    base["deep_valid"] = True
    base["deep_step"] = int(deep["step"])
    base["deep_material"] = deep["material"]
    deep_state = deep["state"]
    regions = deep["regions"]
    centroids = deep["centroids"]
    geometry = core_rings(deep_state, centroids, regions)
    if not geometry["valid"]:
        base["reason"] = geometry["reason"]
        base["manipulation_geometry_valid"] = False
        return base
    base["manipulation_geometry_valid"] = True

    target_first_stage = []
    for slot in range(K):
        target_first_stage.append(first_stage_target(
            deep_state, regions[slot], centroids[slot], deep["entities"][slot],
            targets[slot], written["patches"][slot],
        ))
    first_stage = {}
    for feature in FIRST_STAGE_SCALARS:
        first_stage[feature] = factorial_scalar({assignments[slot]: target_first_stage[slot][feature]
                                                  for slot in range(K)})
    vector_contrasts = factorial_vector({assignments[slot]: target_first_stage[slot]["full_field_vector"]
                                         for slot in range(K)})
    first_stage["full_field"] = {
        name: {"vector": vector.tolist(), "rms": float(np.sqrt(np.mean(vector * vector)))}
        for name, vector in vector_contrasts.items()
    }
    base["first_stage_targets"] = target_first_stage
    base["first_stage_contrasts"] = first_stage

    reference_state, reference_center = _reference_world(seed, deep["step"])
    shifts = [ns._shift(reference_center, center) for center in centroids]
    zero_shifts = [(0, 0)] * K
    g0_engine = DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
    ordinary_engine = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER)
    mem_lam0 = replace(cc.MEM_INTACT, lam_plus=0.0)
    ordinary_lam0 = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER)
    g0_lam0 = DiagEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER, up_ref_zero=True)

    own_driver = record_probe_boundary(
        deep_state, DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True),
        geometry["rings"], zero_shifts, label="own_replay_sham_g0",
    )
    reference_driver = record_probe_boundary(
        reference_state, DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True),
        geometry["rings"], shifts, label="no_history_reference_g0",
    )
    reference_driver_lam0 = record_probe_boundary(
        reference_state, DiagEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER, up_ref_zero=True),
        geometry["rings"], shifts, label="no_history_reference_g0_lamplus0",
    )

    arms = {
        "coupled": measure_arm(deep_state, regions, ordinary_engine),
        "coupled_g0": measure_arm(deep_state, regions, g0_engine),
        "sham_own_replay_g0": measure_arm(
            deep_state, regions,
            ns.NoSwapClampEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
                                 driver=ns.BoundaryDriver(own_driver.ring, own_driver.frames,
                                                          label=own_driver.label), up_ref_zero=True),
        ),
        "isolated": measure_arm(
            deep_state, regions,
            ns.NoSwapClampEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
                                 driver=ns.BoundaryDriver(reference_driver.ring, reference_driver.frames,
                                                          label=reference_driver.label), up_ref_zero=True),
        ),
        "coupled_lamplus0": measure_arm(deep_state, regions, ordinary_lam0),
        "isolated_lamplus0": measure_arm(
            deep_state, regions,
            ns.NoSwapClampEngine(MCM_CONFIG.SPEC, mem_lam0, MCM_CONFIG.TRACER,
                                 driver=ns.BoundaryDriver(reference_driver_lam0.ring,
                                                          reference_driver_lam0.frames,
                                                          label=reference_driver_lam0.label),
                                 up_ref_zero=True),
        ),
    }
    for arm in arms.values():
        arm["tracked_contrasts"] = _arm_contrasts(arm, assignments, "integrated_tracked")
        arm["fixed_contrasts"] = _arm_contrasts(arm, assignments, "integrated_fixed")
    sham_equal = (
        arms["coupled_g0"]["valid"] and arms["sham_own_replay_g0"]["valid"]
        and _pairwise_numeric_equal(arms["coupled_g0"]["integrated_tracked"],
                                    arms["sham_own_replay_g0"]["integrated_tracked"])
        and _pairwise_numeric_equal(arms["coupled_g0"]["integrated_fixed"],
                                    arms["sham_own_replay_g0"]["integrated_fixed"])
        and arms["coupled_g0"]["final_state_hash"] == arms["sham_own_replay_g0"]["final_state_hash"]
    )
    primary_valid = all(arms[name]["valid"] for name in ("coupled", "coupled_g0", "sham_own_replay_g0", "isolated"))
    base["boundary_reference"] = {
        "reference_center": list(reference_center),
        "target_shifts": [list(shift) for shift in shifts],
        "qualified_history_independent_references_available": 1,
        "second_reference_evaluated": False,
    }
    base["arms"] = arms
    base["sham_exact"] = bool(sham_equal)
    base["complete_block"] = bool(primary_valid and sham_equal)
    base["reason"] = None if base["complete_block"] else "primary_arm_or_sham_invalid"
    if base["complete_block"]:
        base["transport"] = {
            name: float(arms["isolated"]["tracked_contrasts"][name]
                        - arms["coupled"]["tracked_contrasts"][name])
            for name in ("dose", "order", "interaction")
        }
        base["transport_global_matched"] = {
            name: float(arms["isolated"]["tracked_contrasts"][name]
                        - arms["coupled_g0"]["tracked_contrasts"][name])
            for name in ("dose", "order", "interaction")
        }
    return base


def _summary(values: Sequence[float], expected: str | None = None) -> dict:
    array = np.asarray(values, dtype=float)
    n = int(array.size)
    if n == 0:
        return {"n_worlds": 0, "values": []}
    mean = float(array.mean())
    sd = float(array.std(ddof=1)) if n > 1 else None
    if n > 1:
        half = float(student_t.ppf(0.975, n - 1) * array.std(ddof=1) / math.sqrt(n))
        ci = [mean - half, mean + half]
    else:
        ci = [None, None]
    positive = int((array > 0).sum())
    negative = int((array < 0).sum())
    required = int(math.ceil(SIGN_FRACTION * n))
    oriented = None
    if expected == "positive":
        oriented = bool(positive >= required and ci[0] is not None and ci[0] > 0)
    elif expected == "negative":
        oriented = bool(negative >= required and ci[1] is not None and ci[1] < 0)
    return {
        "n_worlds": n,
        "values": array.tolist(),
        "mean": mean,
        "median": float(np.median(array)),
        "sd": sd,
        "ci95_t": ci,
        "positive": positive,
        "negative": negative,
        "required_same_orientation": required,
        "expected_orientation": expected,
        "passes_expected_orientation_and_ci": oriented,
    }


def _vector_alignment(vectors: Sequence[Sequence[float]]) -> dict:
    arrays = [np.asarray(vector, dtype=float) for vector in vectors]
    if not arrays:
        return {"n_worlds": 0, "loo_cosines": []}
    rms = [float(np.sqrt(np.mean(vector * vector))) for vector in arrays]
    cosines = []
    if len(arrays) > 1:
        for index, vector in enumerate(arrays):
            reference = np.mean([other for j, other in enumerate(arrays) if j != index], axis=0)
            denom = float(np.linalg.norm(vector) * np.linalg.norm(reference))
            cosines.append(float(np.dot(vector, reference) / denom) if denom > 0 else 0.0)
    return {
        "n_worlds": len(arrays),
        "rms_by_world": rms,
        "loo_cosines": cosines,
        "median_loo_cosine": float(np.median(cosines)) if cosines else None,
    }


def aggregate(worlds: list[dict]) -> dict:
    complete = [world for world in worlds if world.get("complete_block")]
    by_arm = {}
    for arm_name in ("coupled", "coupled_g0", "isolated", "coupled_lamplus0", "isolated_lamplus0"):
        by_arm[arm_name] = {}
        for contrast in ("dose", "order", "interaction"):
            values = [world["arms"][arm_name]["tracked_contrasts"][contrast]
                      for world in complete if world["arms"][arm_name]["tracked_contrasts"] is not None]
            expected = "positive" if contrast == "dose" and arm_name in ("coupled", "coupled_g0", "isolated") else None
            by_arm[arm_name][contrast] = _summary(values, expected=expected)
    first_stage = {}
    for feature in FIRST_STAGE_SCALARS:
        first_stage[feature] = {
            contrast: _summary(
                [world["first_stage_contrasts"][feature][contrast] for world in complete],
                expected=("positive" if (feature == "mplus_mean" and contrast == "dose") else
                          "negative" if (feature == "mminus_mean" and contrast == "order") else None),
            )
            for contrast in ("dose", "order", "interaction")
        }
    first_stage["full_field"] = {
        contrast: _vector_alignment([
            world["first_stage_contrasts"]["full_field"][contrast]["vector"] for world in complete
        ]) for contrast in ("dose", "order", "interaction")
    }
    transport = {
        contrast: _summary([world["transport"][contrast] for world in complete])
        for contrast in ("dose", "order", "interaction")
    }
    transport_global_matched = {
        contrast: _summary([world["transport_global_matched"][contrast] for world in complete])
        for contrast in ("dose", "order", "interaction")
    }
    survival = {name: {"assigned": 0, "posthistory_alive": 0, "deep_alive": 0, "complete_probe": 0}
                for name in HISTORY_NAMES}
    for world in worlds:
        if not world.get("assignment_applied"):
            continue
        for name in HISTORY_NAMES:
            survival[name]["assigned"] += 1
            survival[name]["posthistory_alive"] += int(world.get("history_survival", {}).get(name, False))
            survival[name]["deep_alive"] += int(world.get("deep_survival", {}).get(name, False))
            survival[name]["complete_probe"] += int(world.get("complete_block", False))

    enough = len(complete) >= 4
    manipulation_valid = bool(enough and all(world.get("sham_exact") for world in complete))
    dose_stage = bool(enough and first_stage["mplus_mean"]["dose"]["passes_expected_orientation_and_ci"])
    order_stage = bool(enough and first_stage["mminus_mean"]["order"]["passes_expected_orientation_and_ci"])
    dose_feed = bool(enough and by_arm["isolated"]["dose"]["passes_expected_orientation_and_ci"])
    iso_order = by_arm["isolated"]["order"]
    coupled_order = by_arm["coupled"]["order"]
    order_ci_excludes = bool(
        enough and iso_order.get("ci95_t", [None, None])[0] is not None
        and (iso_order["ci95_t"][0] > 0 or iso_order["ci95_t"][1] < 0)
    )
    order_sign_consistent = bool(
        enough and max(iso_order.get("positive", 0), iso_order.get("negative", 0))
        >= iso_order.get("required_same_orientation", 10**9)
    )
    same_coupled_direction = bool(
        enough and iso_order.get("median", 0.0) != 0.0 and coupled_order.get("median", 0.0) != 0.0
        and math.copysign(1.0, iso_order["median"]) == math.copysign(1.0, coupled_order["median"])
    )
    order_feed = bool(order_ci_excludes and order_sign_consistent and same_coupled_direction)

    if not enough:
        conclusion = "DEV-FEASIBILITY-FAIL"
    elif not manipulation_valid:
        conclusion = "MANIPULATION_INVALID"
    elif not dose_stage:
        conclusion = "STOP"
    elif dose_stage and dose_feed and not order_stage:
        conclusion = "DOSE_ONLY"
    elif order_stage and not order_feed:
        conclusion = "ORDER_STATE_WITHOUT_FEEDING"
    elif dose_stage and order_stage and dose_feed and order_feed:
        conclusion = "DOSE_AND_ORDER"
    elif dose_stage and not dose_feed and not order_feed:
        conclusion = "NO_LOCAL_TRANSPORT"
    else:
        conclusion = "UNRESOLVED"
    prereg_go = bool(
        conclusion == "DOSE_AND_ORDER" and enough and manipulation_valid
        and first_stage["full_field"]["order"]["median_loo_cosine"] is not None
        and first_stage["full_field"]["order"]["median_loo_cosine"] > 0
    )
    return {
        "n_planned_worlds": len(DEV_SEEDS),
        "n_pre_history_eligible_worlds": sum(bool(world.get("prehistory_eligible")) for world in worlds),
        "n_deep_valid_worlds": sum(bool(world.get("deep_valid")) for world in worlds),
        "n_complete_valid_worlds": len(complete),
        "complete_world_seeds": [world["seed"] for world in complete],
        "itt_survival_by_history": survival,
        "first_stage": first_stage,
        "feeding_contrasts": by_arm,
        "transport_isolated_minus_ordinary_coupled": transport,
        "transport_isolated_minus_global_matched_coupled": transport_global_matched,
        "lam_plus_mediation": {
            "intact_isolated": by_arm["isolated"],
            "lam_plus_zero_isolated": by_arm["isolated_lamplus0"],
            "interpretation": "contrast comparison only; endpoint availability is not a mediation result",
        },
        "gates": {
            "minimum_four_complete_worlds": enough,
            "manipulation_sham_exact": manipulation_valid if enough else None,
            "dose_first_stage_expected_orientation_and_ci": dose_stage if enough else None,
            "order_first_stage_expected_orientation_and_ci": order_stage if enough else None,
            "isolated_dose_feeding_expected_orientation_and_ci": dose_feed if enough else None,
            "isolated_order_feeding_consistent_ci_and_coupled_direction": order_feed if enough else None,
            "global_primary_up_ref_zero": True,
            "qualified_boundary_reference_count": 1,
            "reference_reversal_test_applicable": False,
        },
        "conclusion": conclusion,
        "conclusion_reason": (
            "FEWER_THAN_FOUR_COMPLETE_WORLDS" if conclusion == "DEV-FEASIBILITY-FAIL"
            else "FIRST_STAGE_FAIL" if conclusion == "STOP"
            else None
        ),
        "prereg_candidate_go": prereg_go,
        "prospective_execution_authorized": False,
    }


def build_result(manifest: dict, worlds: list[dict], *, status: str) -> dict:
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "canonical_parent": CANONICAL_PARENT,
        "manifest_sha256": MANIFEST_SHA256,
        "seeds": list(DEV_SEEDS),
        "semantic_gate": {
            "pass": True,
            "a1_a2_control": "local Gaussian nutrient amplitude in two consecutive episodes",
            "episode_duration_steps": PHASE,
            "inter_episode_gap_steps": 0,
            "support": [cc.AMP_LO, cc.AMP_HI],
            "global_or_other_target_paths": ["N diffusion", "body/geometry", "uptake", "world-global up_ref"],
            "eligibility_fixed_before_assignment": True,
        },
        "allocation_gate": {
            "pass": True,
            "rule": "cyclic Latin square; rotation=(world_seed-55001) mod 4",
            "outcome_inputs": [],
            "targets_are_replicates": False,
            "statistical_unit": "original world",
        },
        "global_primary": {
            "rule": "validated up_ref=0 ablation",
            "history_independent": True,
            "ordinary_up_ref_control": "coupled",
            "global_matched_control": "coupled_g0",
        },
        "boundary": {
            "rule": "qualified two-cell no-swap clamp",
            "core_radius": CORE_RADIUS,
            "barrier_width": BARRIER_WIDTH,
            "reference": "same-seed same-time no-history on-manifold median component",
            "references_available_before_outcomes": 1,
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
    # Hash the bytes actually persisted. On Windows, text-mode newline
    # translation can otherwise make the announced digest differ from raw data.
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
            print(f"seed {seed}: resume-skip")
            continue
        world = run_world(seed, manifest)
        worlds.append(world)
        atomic_write_json(output, build_result(manifest, worlds, status="PARTIAL"))
        print(
            f"seed {seed}: eligible={world.get('prehistory_eligible')} "
            f"deep={world.get('deep_valid')} complete={world.get('complete_block')} "
            f"reason={world.get('reason')}"
        )
    result = build_result(manifest, worlds, status="COMPLETE")
    digest = atomic_write_json(output, result)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print("RESULT_SHA256", digest)
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
