"""Outcome-blind DEV mechanical executor for DIRECTED-CAUSAL-PAIR-00 Phase 0.5.

The public entry point is the standard-library-only preflight module.  This
module is imported only after authorization and hash checks have passed.  It
advances the frozen physics and records geometry, tracker, writer, turnover,
clamp, and schedule mechanics.  It never integrates or reads a per-target
feeding response and never constructs a directed scientific matrix.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import causal_confirm as cc
from experiments.individuation import material_tracer as mt
from experiments.individuation import turnover_diag_engine as de
from experiments.individuation import directed_causal_pair_phase05_mechanics as mech


TURN_CAP = 1500
MATERIAL_TARGET = 0.25
WRITER_PHASE_STEPS = 60
WRITER_SETTLE_STEPS = 120
PROBE_SETTLE_STEPS = 40
PROBE_STIMULUS_STEPS = 5
PROBE_HORIZON_STEPS = 40
PROBE_STIMULUS_AMPLITUDE = 0.25
ACCESS_ORDER = (
    "ORDINARY",
    "OWN_REPLAY_SHAM_A",
    "OWN_REPLAY_SHAM_B",
    "REFERENCE_NOSWAP_A",
    "REFERENCE_NOSWAP_B",
    "UP_REF_ZERO",
    "REFERENCE_NOSWAP_A_UP_REF_ZERO",
    "REFERENCE_NOSWAP_B_UP_REF_ZERO",
)
ALLOWED_OUTPUT_NAMES = {
    "000_50002.json.gz",
    "001_50004.json.gz",
    "002_50005.json.gz",
    "003_50007.json.gz",
    "INDEX.json",
    "COMPLETE.json",
}


def _hash_array(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(value.shape).encode("ascii"))
    digest.update(str(value.dtype).encode("ascii"))
    digest.update(value.tobytes())
    return digest.hexdigest()


def _hash_parts(parts: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part)
    return digest.hexdigest()


def _detect_masks(state) -> list[np.ndarray]:
    return [cc.mask(entity) for entity in detect(state, MCM_CONFIG.DET)]


def _selected_masks(observer: mech.PassivePairObserver) -> list[np.ndarray] | None:
    masks = []
    for track in observer.tracker.tracks:
        if track.status != "ALIVE":
            return None
        masks.append(track.mask.copy())
    return masks


def _first_failure(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    for record in records:
        if record["kill_reasons"]:
            return {
                "stage": record["stage"],
                "stage_step": int(record["stage_step"]),
                "engine_step": int(record["engine_step"]),
                "reasons": list(record["kill_reasons"]),
            }
    return None


def _append_reason(
    failure: dict[str, Any] | None,
    *,
    stage: str,
    stage_step: int,
    engine_step: int,
    reason: str,
) -> dict[str, Any]:
    if failure is not None:
        return failure
    return {
        "stage": stage,
        "stage_step": int(stage_step),
        "engine_step": int(engine_step),
        "reasons": [reason],
    }


def _outcome_blind_assignment(targets: list[Any], world_id: int) -> mech.PairAssignment:
    candidates = []
    for left in range(3):
        for right in range(left + 1, 3):
            distance = cc.pdist(targets[left].centroid, targets[right].centroid)
            candidates.append((float(distance), -left, -right, left, right))
    _distance, _nl, _nr, left, right = max(candidates)
    if world_id % 2 == 0:
        a, b = left, right
    else:
        a, b = right, left
    sentinel = next(index for index in range(3) if index not in (a, b))
    assignment = mech.PairAssignment(target_A=a, target_B=b, sentinel=sentinel)
    expected = mech.FROZEN_ASSIGNMENTS[world_id]
    if assignment != mech.PairAssignment(**expected):
        raise RuntimeError("recomputed prewriter pair differs from the frozen Phase-0 assignment")
    return assignment


def _writer_common(world_id: int, targets: list[Any]) -> tuple[dict[str, Any], list[np.ndarray]]:
    rng = np.random.default_rng(world_id)
    amplitudes = [
        float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
        float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
    ]
    patches = []
    for entity in targets:
        sigma = max(3.0, float(entity.rg) * 0.8)
        patches.append(cc.patch(*entity.centroid, sigma))
    common_schedule = {
        "writer_id": "FROZEN_03G_LOCAL_GAUSSIAN_WRITER",
        "stream_rule": "first amplitude pair from numpy default_rng(original_world_id)",
        "phase_steps": WRITER_PHASE_STEPS,
        "phase_amplitudes": amplitudes,
        "amplitude_range": [float(cc.AMP_LO), float(cc.AMP_HI)],
        "target_patch_sha256": {
            "A": None,
            "B": None,
        },
        "operation_order": ["A", "B"],
        "operations_per_writer_step": 2,
    }
    common_schedule["common_schedule_sha256"] = mech.sha256_bytes(
        mech.canonical_json_bytes(common_schedule)
    )
    return common_schedule, patches


def _build_prewriter(world_id: int, assignment: mech.PairAssignment) -> dict[str, Any]:
    engine = cc.build(cc.MEM_INTACT)
    state = cc.seed_world(world_id)
    for _ in range(cc.WARM):
        state = engine.step(state)
    targets = cc.pick(sorted(detect(state, MCM_CONFIG.DET), key=lambda entity: -entity.size))
    if len(targets) != 3:
        raise RuntimeError("frozen pair world no longer has exactly three selected prewriter targets")
    recomputed = _outcome_blind_assignment(targets, world_id)
    if recomputed != assignment:
        raise RuntimeError("manifest assignment differs from outcome-blind recomputation")
    masks = [cc.mask(entity) for entity in targets]
    if any(int(mask.sum()) < mech.MIN_COMPONENT_SIZE for mask in masks):
        raise RuntimeError("prewriter target below frozen minimum size")
    payload = ops.serialize_state(state)
    clone_hashes = [ops.state_sha256(ops.deserialize_state(payload)) for _ in mech.ARM_ORDER]
    if len(set(clone_hashes)) != 1 or clone_hashes[0] != ops.state_sha256(state):
        raise RuntimeError("exact prewriter clone hash mismatch")
    common_writer, patches = _writer_common(world_id, targets)
    common_writer["target_patch_sha256"] = {
        "A": _hash_array(patches[assignment.target_A]),
        "B": _hash_array(patches[assignment.target_B]),
    }
    without_digest = dict(common_writer)
    without_digest.pop("common_schedule_sha256", None)
    common_writer["common_schedule_sha256"] = mech.sha256_bytes(
        mech.canonical_json_bytes(without_digest)
    )
    return {
        "payload": payload,
        "state_sha256": clone_hashes[0],
        "masks": masks,
        "targets": targets,
        "patches": patches,
        "writer": common_writer,
        "clone_hashes": clone_hashes,
    }


def _run_writer_arm(
    *,
    payload: bytes,
    seed_masks: list[np.ndarray],
    assignment: mech.PairAssignment,
    patches: list[np.ndarray],
    amplitudes: list[float],
    arm: str,
) -> dict[str, Any]:
    bits = mech.ARM_BITS[arm]
    state = ops.deserialize_state(payload)
    engine = cc.build(cc.MEM_INTACT)
    observer = mech.PassivePairObserver(seed_masks, assignment)
    records = [observer.seed_snapshot(state)]
    sham_reference = ops.deserialize_state(payload) if arm == "H00" else None
    sham_reference_exact = True if arm == "H00" else None
    operation_rows = []
    active_step = 0
    for phase_index, amplitude in enumerate(amplitudes):
        for phase_step in range(1, WRITER_PHASE_STEPS + 1):
            active_step += 1
            state.N = (
                state.N
                + bits[0] * amplitude * patches[assignment.target_A]
                + bits[1] * amplitude * patches[assignment.target_B]
            )
            state = engine.step(state)
            if sham_reference is not None:
                sham_reference = engine.step(sham_reference)
                sham_reference_exact = bool(
                    sham_reference_exact
                    and ops.state_sha256(state) == ops.state_sha256(sham_reference)
                )
            record = observer.advance(
                state,
                _detect_masks(state),
                step=active_step,
                stage="WRITER",
            )
            records.append(record)
            operation_rows.append(
                {
                    "phase": int(phase_index + 1),
                    "phase_step": int(phase_step),
                    "amplitude": float(amplitude),
                    "bits": [int(bits[0]), int(bits[1])],
                    "target_order": ["A", "B"],
                }
            )
            if record["kill_reasons"]:
                break
        if records[-1]["kill_reasons"]:
            break

    if not records[-1]["kill_reasons"]:
        for settle_step in range(1, WRITER_SETTLE_STEPS + 1):
            state = engine.step(state)
            if sham_reference is not None:
                sham_reference = engine.step(sham_reference)
                sham_reference_exact = bool(
                    sham_reference_exact
                    and ops.state_sha256(state) == ops.state_sha256(sham_reference)
                )
            record = observer.advance(
                state,
                _detect_masks(state),
                step=settle_step,
                stage="POSTWRITER_SETTLE",
            )
            records.append(record)
            if record["kill_reasons"]:
                break

    failure = _first_failure(records)
    if arm == "H00" and sham_reference_exact is False:
        failure = _append_reason(
            failure,
            stage="WRITER",
            stage_step=active_step,
            engine_step=int(state.step),
            reason="H00_SHAM_NOT_BYTE_IDENTICAL_TO_NO_WRITER_CONTINUATION",
        )
    operation_digest = mech.sha256_bytes(mech.canonical_json_bytes(operation_rows))
    writer_record = {
        "operation_count": int(len(operation_rows) * 2),
        "expected_operation_count": int(2 * 2 * WRITER_PHASE_STEPS),
        "total_writer_engine_steps": int(active_step + max(0, len(records) - 1 - active_step)),
        "active_writer_steps": int(active_step),
        "settle_steps": int(max(0, len(records) - 1 - active_step)),
        "operation_digest": operation_digest,
        "postwriter_state_sha256": ops.state_sha256(state),
        "sham_reference_exact": sham_reference_exact,
    }
    complete = bool(
        failure is None
        and active_step == 2 * WRITER_PHASE_STEPS
        and writer_record["settle_steps"] == WRITER_SETTLE_STEPS
        and writer_record["operation_count"] == writer_record["expected_operation_count"]
    )
    if not complete and failure is None:
        failure = _append_reason(
            None,
            stage="WRITER",
            stage_step=active_step,
            engine_step=int(state.step),
            reason="WRITER_SCHEDULE_INCOMPLETE",
        )
    return {
        "arm": arm,
        "bits": [int(bits[0]), int(bits[1])],
        "clone_sha256": ops.state_sha256(ops.deserialize_state(payload)),
        "writer": writer_record,
        "writer_records": records,
        "writer_complete": complete,
        "first_failure": failure,
        "state": state,
        "observer": observer,
    }


def _run_turnover(
    arm_result: dict[str, Any],
    *,
    common_deep_step: int | None,
    discover_common: bool,
) -> dict[str, Any]:
    if not arm_result["writer_complete"]:
        return {
            "records": [],
            "deep_complete": False,
            "deep_joint": None,
            "deep_step": common_deep_step,
            "first_failure": arm_result["first_failure"],
            "state": None,
            "masks": None,
        }
    observer = arm_result["observer"]
    masks = _selected_masks(observer)
    if masks is None:
        raise RuntimeError("writer complete without three alive tracker masks")
    state, tracer_base = mt.seed_tracers(arm_result["state"], masks)
    engine = cc.build(cc.MEM_INTACT)
    cap = TURN_CAP if discover_common else int(common_deep_step or 0)
    mt.assert_no_feed_collision(engine.tracer, tracer_base, max(1, cap + 1))
    records = []
    failure = arm_result["first_failure"]
    found_step = None
    last_material = None
    for turnover_step in range(1, cap + 1):
        state = engine.step(state)
        record = observer.advance(
            state,
            _detect_masks(state),
            step=turnover_step,
            stage="TURNOVER",
        )
        tracked_masks = _selected_masks(observer)
        material = mt.read_material(state, tracer_base, tracked_masks or [None, None, None])
        material_values = [
            None if row is None else float(row["M"])
            for row in material
        ]
        material_gate = bool(
            tracked_masks is not None
            and not record["kill_reasons"]
            and all(
                value is not None and np.isfinite(value) and value <= MATERIAL_TARGET
                for value in material_values
            )
        )
        record["material_retention"] = material_values
        record["deep_material_gate"] = material_gate
        mech.assert_outcome_free(record)
        records.append(record)
        last_material = material_values
        if record["kill_reasons"]:
            failure = _first_failure(records)
            break
        if discover_common and material_gate:
            found_step = turnover_step
            break

    if discover_common:
        deep_step = found_step
        if deep_step is None and failure is None:
            failure = _append_reason(
                None,
                stage="TURNOVER",
                stage_step=cap,
                engine_step=int(state.step),
                reason="H00_COMMON_DEEP_STEP_NOT_REACHED_BY_1500",
            )
    else:
        deep_step = common_deep_step
        endpoint_reached = len(records) == int(common_deep_step or -1)
        endpoint_gate = bool(records and records[-1]["deep_material_gate"])
        if failure is None and (not endpoint_reached or not endpoint_gate):
            failure = _append_reason(
                None,
                stage="TURNOVER",
                stage_step=len(records),
                engine_step=int(state.step),
                reason="COMMON_H00_DEEP_MATERIAL_GATE_FAILED",
            )

    tracked_masks = _selected_masks(observer)
    deep_complete = bool(
        failure is None
        and deep_step is not None
        and len(records) == int(deep_step)
        and records[-1]["deep_material_gate"]
        and tracked_masks is not None
    )
    deep_joint = None
    if tracked_masks is not None and last_material is not None:
        order = [
            ("A", arm_result["observer"].assignment.target_A),
            ("B", arm_result["observer"].assignment.target_B),
            ("SENTINEL", arm_result["observer"].assignment.sentinel),
        ]
        final_tracks = records[-1]["tracks"] if records else []
        deep_joint = [
            {
                "target": label,
                "material_retention": last_material[index],
                "phenotype_descriptor": {
                    "component_size": int(final_tracks[index]["component_size"]),
                    "centroid": list(final_tracks[index]["centroid"]),
                    "body_core_coverage": float(final_tracks[index]["body_core_coverage"]),
                },
            }
            for label, index in order
        ]
    return {
        "records": records,
        "deep_complete": deep_complete,
        "deep_joint": deep_joint,
        "deep_step": deep_step,
        "first_failure": failure,
        "state": state if deep_complete else None,
        "masks": tracked_masks if deep_complete else None,
    }


def _probe_schedule() -> dict[str, Any]:
    schedule = {
        "schedule_id": "CORRECTED_NONFUSING_PROBE_V1",
        "N_standardized_to": float(cc.N0),
        "settle_steps": PROBE_SETTLE_STEPS,
        "stimulus_amplitude": PROBE_STIMULUS_AMPLITUDE,
        "stimulus_steps": PROBE_STIMULUS_STEPS,
        "horizon_steps": PROBE_HORIZON_STEPS,
        "total_engine_steps": PROBE_SETTLE_STEPS + PROBE_HORIZON_STEPS,
    }
    schedule["schedule_digest"] = mech.sha256_bytes(mech.canonical_json_bytes(schedule))
    return schedule


def _prepare_probe_state(state):
    prepared = state.copy()
    prepared.N = np.full_like(prepared.N, cc.N0)
    return prepared


def _apply_probe_pulse(state, schedule_step: int) -> None:
    if PROBE_SETTLE_STEPS < schedule_step <= PROBE_SETTLE_STEPS + PROBE_STIMULUS_STEPS:
        state.N = state.N + PROBE_STIMULUS_AMPLITUDE


def _stage_for_schedule(schedule_step: int) -> tuple[str, int]:
    if schedule_step <= PROBE_SETTLE_STEPS:
        return "PROBE_SETTLE", schedule_step
    return "PROBE_HORIZON", schedule_step - PROBE_SETTLE_STEPS


def _ring_frame(state, ring: np.ndarray, shift: tuple[int, int]) -> dict[str, np.ndarray]:
    ys, xs = np.where(ring)
    frame = {}
    for field in ns.STATE_FIELDS:
        array = getattr(state, field)
        rolled = np.roll(array, shift, axis=(-2, -1)) if shift != (0, 0) else array
        if array.ndim == 2:
            frame[field] = rolled[ys, xs].copy()
        else:
            frame[field] = rolled[:, ys, xs].copy()
    return frame


def _frames_sha256(frames: list[dict[str, np.ndarray]]) -> str:
    digest = hashlib.sha256()
    for frame_index, frame in enumerate(frames):
        digest.update(str(frame_index).encode("ascii"))
        for field in ns.STATE_FIELDS:
            array = np.ascontiguousarray(frame[field])
            digest.update(field.encode("ascii"))
            digest.update(str(array.shape).encode("ascii"))
            digest.update(str(array.dtype).encode("ascii"))
            digest.update(array.tobytes())
    return digest.hexdigest()


def _changed_support(before, after) -> np.ndarray:
    changed = np.zeros(before.rho.shape, dtype=bool)
    for field in ns.STATE_FIELDS:
        left = getattr(before, field)
        right = getattr(after, field)
        delta = left != right
        if delta.ndim == 3:
            delta = np.any(delta, axis=0)
        changed |= delta
    return changed


def _region_sha256(state, region: np.ndarray) -> str:
    """Opaque commitment to all persistent fields on one declared region."""
    digest = hashlib.sha256()
    digest.update(mech.packed_mask(region)["sha256"].encode("ascii"))
    for field in ns.STATE_FIELDS:
        values = np.ascontiguousarray(getattr(state, field)[..., region])
        digest.update(field.encode("ascii"))
        digest.update(str(values.shape).encode("ascii"))
        digest.update(str(values.dtype).encode("ascii"))
        digest.update(values.tobytes())
    return digest.hexdigest()


def _free_access(
    *,
    state,
    masks: list[np.ndarray],
    assignment: mech.PairAssignment,
    collars: dict[str, np.ndarray],
    up_ref_zero: bool,
    regime: str,
) -> tuple[dict[str, Any], dict[str, list[dict[str, np.ndarray]]], list[str]]:
    current = _prepare_probe_state(state)
    engine = (
        de.DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
        if up_ref_zero
        else ns.NoSwapClampEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, driver=None)
    )
    observer = mech.PassivePairObserver(masks, assignment)
    records = [observer.seed_snapshot(current, stage="PROBE_STANDARDIZE")]
    frames = {"A": [], "B": []}
    state_hashes = [ops.state_sha256(current)]
    for schedule_step in range(1, PROBE_SETTLE_STEPS + PROBE_HORIZON_STEPS + 1):
        _apply_probe_pulse(current, schedule_step)
        current = engine.step(current)
        for recipient in ("A", "B"):
            frames[recipient].append(_ring_frame(current, collars[recipient], (0, 0)))
        stage, local_step = _stage_for_schedule(schedule_step)
        record = observer.advance(
            current,
            _detect_masks(current),
            step=local_step,
            stage=stage,
        )
        records.append(record)
        state_hashes.append(ops.state_sha256(current))
        if record["kill_reasons"]:
            break
    failure = _first_failure(records)
    complete = bool(failure is None and len(records) == 81)
    operation = {
        "clamp_active": False,
        "up_ref_zero": bool(up_ref_zero),
        "recipient": None,
        "boundary_frames_sha256": None,
        "own_replay_exact": None,
        "unintended_write_cells": 0,
        "isolation_exact": None,
        "schedule_digest": _probe_schedule()["schedule_digest"],
    }
    result = {
        "regime": regime,
        "recipient": None,
        "schedule": _probe_schedule(),
        "operation": operation,
        "records": records,
        "complete": complete,
        "probe_schedule_viable": complete,
        "first_failure": failure,
    }
    return result, frames, state_hashes


def _source_frames(
    *,
    source_state,
    ring: np.ndarray,
    shift: tuple[int, int],
    up_ref_zero: bool,
) -> list[dict[str, np.ndarray]]:
    current = _prepare_probe_state(source_state)
    engine = (
        de.DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True)
        if up_ref_zero
        else ns.NoSwapClampEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, driver=None)
    )
    frames = []
    for schedule_step in range(1, PROBE_SETTLE_STEPS + PROBE_HORIZON_STEPS + 1):
        _apply_probe_pulse(current, schedule_step)
        current = engine.step(current)
        frames.append(_ring_frame(current, ring, shift))
    return frames


def _clamped_access(
    *,
    state,
    masks: list[np.ndarray],
    assignment: mech.PairAssignment,
    collar: np.ndarray,
    recipient: str,
    frames: list[dict[str, np.ndarray]],
    up_ref_zero: bool,
    regime: str,
    ordinary_hashes: list[str] | None,
) -> dict[str, Any]:
    current = _prepare_probe_state(state)
    base_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC,
        cc.MEM_INTACT,
        MCM_CONFIG.TRACER,
        driver=None,
        up_ref_zero=up_ref_zero,
    )
    driver = ns.BoundaryDriver(collar.copy(), copy.deepcopy(frames), label=regime)
    observer = mech.PassivePairObserver(masks, assignment)
    records = [
        observer.seed_snapshot(current, stage="PROBE_STANDARDIZE")
    ]
    state_hashes = [ops.state_sha256(current)]
    unintended_counts = []
    own_exact = True if ordinary_hashes is not None else None
    for schedule_step in range(1, PROBE_SETTLE_STEPS + PROBE_HORIZON_STEPS + 1):
        _apply_probe_pulse(current, schedule_step)
        pre_clamp = base_engine.step(current)
        current = driver.apply(pre_clamp.copy())
        changed = _changed_support(pre_clamp, current)
        unintended_counts.append(int(np.count_nonzero(changed & ~collar)))
        state_hash = ops.state_sha256(current)
        state_hashes.append(state_hash)
        if ordinary_hashes is not None:
            own_exact = bool(
                own_exact
                and schedule_step < len(ordinary_hashes)
                and state_hash == ordinary_hashes[schedule_step]
            )
        stage, local_step = _stage_for_schedule(schedule_step)
        record = observer.advance(
            current,
            _detect_masks(current),
            step=local_step,
            stage=stage,
            collar=collar,
            clamp_recipient=recipient,
        )
        records.append(record)
        if record["kill_reasons"]:
            break
    failure = _first_failure(records)
    if max(unintended_counts, default=0) != 0:
        failure = _append_reason(
            failure,
            stage="CLAMP",
            stage_step=len(unintended_counts),
            engine_step=int(current.step),
            reason="CLAMP_UNINTENDED_WRITE_OUTSIDE_COLLAR",
        )
    if ordinary_hashes is not None and not own_exact:
        failure = _append_reason(
            failure,
            stage="CLAMP",
            stage_step=len(unintended_counts),
            engine_step=int(current.step),
            reason="OWN_REPLAY_NOT_BYTE_IDENTICAL",
        )
    complete = bool(failure is None and len(records) == 81)
    return {
        "regime": regime,
        "recipient": recipient,
        "schedule": _probe_schedule(),
        "operation": {
            "clamp_active": True,
            "up_ref_zero": bool(up_ref_zero),
            "recipient": recipient,
            "boundary_frames_sha256": _frames_sha256(frames),
            "own_replay_exact": own_exact,
            "unintended_write_cells": int(max(unintended_counts, default=0)),
            "isolation_exact": None,
            "schedule_digest": _probe_schedule()["schedule_digest"],
        },
        "records": records,
        "complete": complete,
        "probe_schedule_viable": complete,
        "first_failure": failure,
    }


def _exact_isolation(
    *,
    state,
    masks: list[np.ndarray],
    assignment: mech.PairAssignment,
    recipient: str,
    collar: np.ndarray,
    own_upref_frames: list[dict[str, np.ndarray]],
    free_upref_hashes: list[str],
) -> dict[str, Any]:
    recipient_index = assignment.target_A if recipient == "A" else assignment.target_B
    center = mech.periodic_centroid(masks[recipient_index])
    partition, core, _barrier = ns.core_and_collar(state.rho.shape, center)
    outside = partition.distance > (ns.CORE_RADIUS + ns.BARRIER_WIDTH + 1)
    # This is an environment perturbation, not a direct perturbation of the
    # history-bearing partner or sentinel.  Their radius-12 supports remain
    # untouched and physically present in both branches.
    for index, mask in enumerate(masks):
        if index == recipient_index:
            continue
        outside &= ~mech.disk_mask(
            state.rho.shape,
            mech.periodic_centroid(mask),
            mech.HALO_RADIUS,
        )
    left = _prepare_probe_state(state)
    right = _prepare_probe_state(state)
    right.c[outside] += 0.05
    right.N[outside] += 0.05
    left_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, driver=None, up_ref_zero=True
    )
    right_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, driver=None, up_ref_zero=True
    )
    left_driver = ns.BoundaryDriver(collar.copy(), copy.deepcopy(own_upref_frames), label="isolation_left")
    right_driver = ns.BoundaryDriver(collar.copy(), copy.deepcopy(own_upref_frames), label="isolation_right")
    left_observer = mech.PassivePairObserver(masks, assignment)
    right_observer = mech.PassivePairObserver(masks, assignment)
    per_step = []
    left_failure = None
    right_failure = None
    own_upref_exact = True
    for schedule_step in range(1, PROBE_SETTLE_STEPS + PROBE_HORIZON_STEPS + 1):
        _apply_probe_pulse(left, schedule_step)
        _apply_probe_pulse(right, schedule_step)
        left = left_driver.apply(left_engine.step(left).copy())
        right = right_driver.apply(right_engine.step(right).copy())
        left_state_sha256 = ops.state_sha256(left)
        expected_free_sha256 = (
            free_upref_hashes[schedule_step]
            if schedule_step < len(free_upref_hashes)
            else None
        )
        own_upref_exact = bool(
            own_upref_exact
            and expected_free_sha256 is not None
            and left_state_sha256 == expected_free_sha256
        )
        field_diffs = {}
        for field in ns.STATE_FIELDS:
            a = getattr(left, field)[..., core]
            b = getattr(right, field)[..., core]
            field_diffs[field] = float(np.max(np.abs(a - b))) if a.size else 0.0
        per_step.append(
            {
                "schedule_step": schedule_step,
                "max_core_abs": float(max(field_diffs.values(), default=0.0)),
                "left_core_sha256": _region_sha256(left, core),
                "right_core_sha256": _region_sha256(right, core),
                "left_state_sha256": left_state_sha256,
                "free_up_ref_state_sha256": expected_free_sha256,
            }
        )
        stage, local_step = _stage_for_schedule(schedule_step)
        left_record = left_observer.advance(
            left,
            _detect_masks(left),
            step=local_step,
            stage=f"ISOLATION_LEFT_{stage}",
            collar=collar,
            clamp_recipient=recipient,
        )
        right_record = right_observer.advance(
            right,
            _detect_masks(right),
            step=local_step,
            stage=f"ISOLATION_RIGHT_{stage}",
            collar=collar,
            clamp_recipient=recipient,
        )
        if left_failure is None and left_record["kill_reasons"]:
            left_failure = {
                "schedule_step": schedule_step,
                "reasons": left_record["kill_reasons"],
            }
        if right_failure is None and right_record["kill_reasons"]:
            right_failure = {
                "schedule_step": schedule_step,
                "reasons": right_record["kill_reasons"],
            }
    maximum = float(max(row["max_core_abs"] for row in per_step))
    environment_difference = float(np.max(np.abs(left.c[outside] - right.c[outside])))
    exact = bool(
        maximum == 0.0
        and own_upref_exact
        and left_failure is None
        and right_failure is None
    )
    return {
        "recipient": recipient,
        "barrier_width": int(ns.BARRIER_WIDTH),
        "up_ref_zero": True,
        "environment_perturbation": {"fields": ["c", "N"], "amplitude": 0.05},
        "per_step": per_step,
        "maximum_core_abs_difference": maximum,
        "environment_c_max_difference_at_end": environment_difference,
        "outside_difference_nonzero": bool(environment_difference > 0.0),
        "own_replay_up_ref_zero_exact": own_upref_exact,
        "left_first_failure": left_failure,
        "right_first_failure": right_failure,
        "bit_exact_isolation": exact,
    }


def _reference_component(state) -> tuple[tuple[float, float], np.ndarray]:
    entities = [
        entity
        for entity in detect(state, MCM_CONFIG.DET)
        if 4 <= int(entity.size) < int(mech.COVERAGE_CAP * state.rho.size)
    ]
    if not entities:
        raise RuntimeError("H00 reference state contains no on-manifold reference component")
    entities.sort(
        key=lambda entity: (
            int(entity.size),
            float(entity.centroid[0]),
            float(entity.centroid[1]),
        )
    )
    entity = entities[(len(entities) - 1) // 2]
    return tuple(float(value) for value in entity.centroid), cc.mask(entity)


def _run_access_set(
    *,
    arm_state,
    arm_masks: list[np.ndarray],
    assignment: mech.PairAssignment,
    h00_reference_state,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    centers = {
        "A": mech.periodic_centroid(arm_masks[assignment.target_A]),
        "B": mech.periodic_centroid(arm_masks[assignment.target_B]),
    }
    collars = {
        recipient: ns.core_and_collar(arm_state.rho.shape, center)[2]
        for recipient, center in centers.items()
    }
    reference_center, _reference_mask = _reference_component(h00_reference_state)
    shifts = {
        recipient: ns._shift(reference_center, centers[recipient])
        for recipient in ("A", "B")
    }

    ordinary, own_frames, ordinary_hashes = _free_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collars=collars,
        up_ref_zero=False,
        regime="ORDINARY",
    )
    upref, own_upref_frames, upref_hashes = _free_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collars=collars,
        up_ref_zero=True,
        regime="UP_REF_ZERO",
    )
    own_a = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["A"],
        recipient="A",
        frames=own_frames["A"],
        up_ref_zero=False,
        regime="OWN_REPLAY_SHAM_A",
        ordinary_hashes=ordinary_hashes,
    )
    own_b = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["B"],
        recipient="B",
        frames=own_frames["B"],
        up_ref_zero=False,
        regime="OWN_REPLAY_SHAM_B",
        ordinary_hashes=ordinary_hashes,
    )

    ref_frames = {
        recipient: _source_frames(
            source_state=h00_reference_state,
            ring=collars[recipient],
            shift=shifts[recipient],
            up_ref_zero=False,
        )
        for recipient in ("A", "B")
    }
    ref_up_frames = {
        recipient: _source_frames(
            source_state=h00_reference_state,
            ring=collars[recipient],
            shift=shifts[recipient],
            up_ref_zero=True,
        )
        for recipient in ("A", "B")
    }
    ref_a = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["A"],
        recipient="A",
        frames=ref_frames["A"],
        up_ref_zero=False,
        regime="REFERENCE_NOSWAP_A",
        ordinary_hashes=None,
    )
    ref_b = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["B"],
        recipient="B",
        frames=ref_frames["B"],
        up_ref_zero=False,
        regime="REFERENCE_NOSWAP_B",
        ordinary_hashes=None,
    )
    ref_up_a = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["A"],
        recipient="A",
        frames=ref_up_frames["A"],
        up_ref_zero=True,
        regime="REFERENCE_NOSWAP_A_UP_REF_ZERO",
        ordinary_hashes=None,
    )
    ref_up_b = _clamped_access(
        state=arm_state,
        masks=arm_masks,
        assignment=assignment,
        collar=collars["B"],
        recipient="B",
        frames=ref_up_frames["B"],
        up_ref_zero=True,
        regime="REFERENCE_NOSWAP_B_UP_REF_ZERO",
        ordinary_hashes=None,
    )

    isolation = {
        recipient: _exact_isolation(
            state=arm_state,
            masks=arm_masks,
            assignment=assignment,
            recipient=recipient,
            collar=collars[recipient],
            own_upref_frames=own_upref_frames[recipient],
            free_upref_hashes=upref_hashes,
        )
        for recipient in ("A", "B")
    }
    for regime in (ref_up_a, ref_up_b):
        recipient = regime["recipient"]
        regime["operation"]["isolation_exact"] = isolation[recipient]["bit_exact_isolation"]
        regime["isolation_evidence"] = isolation[recipient]
        if not isolation[recipient]["bit_exact_isolation"] and regime["first_failure"] is None:
            regime["first_failure"] = {
                "stage": "EXACT_ISOLATION",
                "stage_step": 80,
                "engine_step": int(arm_state.step + 80),
                "reasons": ["PAIR_CONTEXT_EXACT_ISOLATION_FAILED"],
            }
            regime["complete"] = False
            regime["probe_schedule_viable"] = False
    for regime in (ordinary, own_a, own_b, ref_a, ref_b, upref):
        regime["isolation_evidence"] = None

    by_name = {
        row["regime"]: row
        for row in (ordinary, own_a, own_b, ref_a, ref_b, upref, ref_up_a, ref_up_b)
    }
    ordered = [by_name[name] for name in ACCESS_ORDER]
    failure = next((row["first_failure"] for row in ordered if row["first_failure"] is not None), None)
    return ordered, failure


def _world_shard(
    *,
    world_id: int,
    sequence_index: int,
    manifest: dict[str, Any],
    manifest_sha256: str,
    plan_sha256: str,
    previous_record_sha256: str | None,
) -> dict[str, Any]:
    assignment = mech.PairAssignment(**mech.FROZEN_ASSIGNMENTS[world_id])
    prewriter = _build_prewriter(world_id, assignment)
    writer = prewriter["writer"]
    writer_results = [
        _run_writer_arm(
            payload=prewriter["payload"],
            seed_masks=prewriter["masks"],
            assignment=assignment,
            patches=prewriter["patches"],
            amplitudes=writer["phase_amplitudes"],
            arm=arm,
        )
        for arm in mech.ARM_ORDER
    ]

    h00_turnover = _run_turnover(
        writer_results[0],
        common_deep_step=None,
        discover_common=True,
    )
    common_deep_step = h00_turnover["deep_step"] if h00_turnover["deep_complete"] else None
    turnovers = [h00_turnover]
    for arm_result in writer_results[1:]:
        turnovers.append(
            _run_turnover(
                arm_result,
                common_deep_step=common_deep_step,
                discover_common=False,
            )
            if common_deep_step is not None
            else {
                "records": [],
                "deep_complete": False,
                "deep_joint": None,
                "deep_step": None,
                "first_failure": {
                    "stage": "TURNOVER",
                    "stage_step": 0,
                    "engine_step": int(arm_result["state"].step),
                    "reasons": ["H00_COMMON_DEEP_STEP_UNAVAILABLE"],
                },
                "state": None,
                "masks": None,
            }
        )

    h00_reference_state = h00_turnover["state"]
    arm_records = []
    for arm_result, turnover in zip(writer_results, turnovers):
        access_regimes = []
        access_failure = None
        if turnover["deep_complete"] and h00_reference_state is not None:
            access_regimes, access_failure = _run_access_set(
                arm_state=turnover["state"],
                arm_masks=turnover["masks"],
                assignment=assignment,
                h00_reference_state=h00_reference_state,
            )
        elif turnover["first_failure"] is None:
            access_failure = {
                "stage": "ACCESS",
                "stage_step": 0,
                "engine_step": int(arm_result["state"].step),
                "reasons": ["DEEP_CHECKPOINT_UNAVAILABLE"],
            }
        first_failure = arm_result["first_failure"] or turnover["first_failure"] or access_failure
        complete = bool(
            first_failure is None
            and turnover["deep_complete"]
            and len(access_regimes) == len(ACCESS_ORDER)
            and all(regime["complete"] for regime in access_regimes)
        )
        arm_records.append(
            {
                "arm": arm_result["arm"],
                "bits": arm_result["bits"],
                "clone_sha256": arm_result["clone_sha256"],
                "writer": arm_result["writer"],
                "writer_records": arm_result["writer_records"],
                "common_deep_step": common_deep_step,
                "turnover_records": turnover["records"],
                "deep_complete": bool(turnover["deep_complete"]),
                "deep_joint": turnover["deep_joint"],
                "access_regimes": access_regimes,
                "arm_complete": complete,
                "first_failure": first_failure,
            }
        )

    clone_exact = len({row["clone_sha256"] for row in arm_records}) == 1
    schedules_equal = all(
        row["writer"]["expected_operation_count"] == 240
        and row["writer"]["operation_count"] == 240
        and row["writer"]["active_writer_steps"] == 120
        and row["writer"]["settle_steps"] == 120
        for row in arm_records
    )
    first_failure = next((row["first_failure"] for row in arm_records if row["first_failure"] is not None), None)
    if not clone_exact and first_failure is None:
        first_failure = {
            "stage": "CLONE",
            "stage_step": 0,
            "engine_step": int(cc.WARM),
            "reasons": ["PREWRITER_CLONE_HASH_MISMATCH"],
        }
    if not schedules_equal and first_failure is None:
        first_failure = {
            "stage": "WRITER",
            "stage_step": 0,
            "engine_step": cc.WARM,
            "reasons": ["WRITER_SCHEDULE_OR_OPERATION_COUNT_MISMATCH"],
        }
    world_complete = bool(
        first_failure is None
        and clone_exact
        and schedules_equal
        and common_deep_step is not None
        and all(row["arm_complete"] for row in arm_records)
    )
    shard = {
        "schema": mech.RAW_SHARD_SCHEMA,
        "mission": mech.MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "phase0_commit": mech.PHASE0_COMMIT,
        "sequence_index": int(sequence_index),
        "world_id": int(world_id),
        "manifest_sha256": manifest_sha256,
        "plan_sha256": plan_sha256,
        "previous_record_sha256": previous_record_sha256,
        "contract_bindings": [
            {
                "kind": kind,
                "path": path,
                "sha256": binding["sha256"],
                "git_blob": binding["git_blob"],
            }
            for kind, bindings in (
                ("INPUT", manifest["input_files"]),
                ("CODE", manifest["code_files"]),
            )
            for path, binding in sorted(bindings.items())
        ],
        "assignment": {
            "target_A": int(assignment.target_A),
            "target_B": int(assignment.target_B),
            "sentinel": int(assignment.sentinel),
        },
        "prewriter_state_sha256": prewriter["state_sha256"],
        "prewriter_clone_sha256": prewriter["clone_hashes"],
        "writer": writer,
        "common_deep_step": common_deep_step,
        "history_arms": arm_records,
        "world_complete": world_complete,
        "first_failure": first_failure,
    }
    mech.assert_outcome_free(shard)
    return shard


def _shard_name(sequence_index: int, world_id: int) -> str:
    return f"{sequence_index:03d}_{world_id}.json.gz"


def _load_existing_prefix(
    output_dir: Path,
    *,
    manifest_sha256: str,
    plan_sha256: str,
) -> tuple[list[dict[str, Any]], str | None]:
    rows = []
    previous = None
    missing_seen = False
    if output_dir.exists():
        names = {path.name for path in output_dir.iterdir()}
        unknown = sorted(names - ALLOWED_OUTPUT_NAMES)
        if unknown:
            raise ValueError(f"unexpected file(s) in fixed raw directory: {unknown}")
    for sequence_index, world_id in enumerate(mech.FROZEN_PAIR_WORLDS):
        path = output_dir / _shard_name(sequence_index, world_id)
        if not path.exists():
            missing_seen = True
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"mechanical shard is not an ordinary file: {path.name}")
        if missing_seen:
            raise ValueError("mechanical raw shards do not form an exact ordered prefix")
        compressed = path.read_bytes()
        raw = mech.deterministic_gzip(b"")  # force the deterministic codec path to import now
        del raw
        value = mech.decode_gzip_json(compressed)
        canonical = mech.canonical_json_bytes(value)
        if mech.deterministic_gzip(canonical) != compressed:
            raise ValueError(f"noncanonical deterministic shard bytes: {path.name}")
        if value.get("schema") != mech.RAW_SHARD_SCHEMA:
            raise ValueError("existing shard schema mismatch")
        if value.get("sequence_index") != sequence_index or value.get("world_id") != world_id:
            raise ValueError("existing shard plan identity mismatch")
        if value.get("manifest_sha256") != manifest_sha256 or value.get("plan_sha256") != plan_sha256:
            raise ValueError("existing shard manifest/plan binding mismatch")
        if value.get("previous_record_sha256") != previous:
            raise ValueError("existing shard predecessor chain mismatch")
        mech.assert_outcome_free(value)
        uncompressed_sha = mech.sha256_bytes(canonical)
        rows.append(
            {
                "sequence_index": sequence_index,
                "world_id": world_id,
                "path": path.name,
                "sha256": mech.sha256_bytes(compressed),
                "uncompressed_sha256": uncompressed_sha,
                "size_bytes": len(compressed),
                "world_complete": bool(value["world_complete"]),
            }
        )
        previous = uncompressed_sha
    return rows, previous


def _publish_index(
    output_dir: Path,
    *,
    manifest_sha256: str,
    plan_sha256: str,
    rows: list[dict[str, Any]],
    complete: bool,
) -> dict[str, Any]:
    index = {
        "schema": mech.INDEX_SCHEMA,
        "mission": mech.MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "manifest_sha256": manifest_sha256,
        "plan": list(mech.FROZEN_PAIR_WORLDS),
        "plan_sha256": plan_sha256,
        "completed": rows,
        "complete": bool(complete),
    }
    mech.atomic_write_json(output_dir / "INDEX.json", index)
    return index


def _terminal_record(
    *,
    manifest_sha256: str,
    plan_sha256: str,
    index: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": "DIRECTED-CAUSAL-PAIR-00-PHASE05-COMPLETE-v1",
        "mission": mech.MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "manifest_sha256": manifest_sha256,
        "plan_sha256": plan_sha256,
        "index_sha256": mech.sha256_bytes(mech.canonical_json_bytes(index)),
        "world_count": len(rows),
        "all_worlds_mechanically_complete": bool(all(row["world_complete"] for row in rows)),
    }


def execute(
    *,
    repo: Path,
    manifest: dict[str, Any],
    manifest_sha256: str,
    output_dir: Path,
    resume: bool,
) -> None:
    mech.assert_no_forbidden_analyzer_imports()
    mech.validate_dev_manifest(manifest)
    if tuple(manifest["worlds"]) != mech.FROZEN_PAIR_WORLDS:
        raise ValueError("executor plan differs from preflight plan")
    plan_sha256 = mech.sha256_bytes(mech.canonical_json_bytes(list(mech.FROZEN_PAIR_WORLDS)))
    if output_dir.exists() and any(output_dir.iterdir()) and not resume:
        raise FileExistsError("fixed raw directory is nonempty; use explicit --resume")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, previous = _load_existing_prefix(
        output_dir,
        manifest_sha256=manifest_sha256,
        plan_sha256=plan_sha256,
    )
    if len(rows) < len(mech.FROZEN_PAIR_WORLDS) and (output_dir / "COMPLETE.json").exists():
        raise ValueError("terminal COMPLETE record exists before the exact plan prefix is complete")
    if len(rows) == len(mech.FROZEN_PAIR_WORLDS):
        index = _publish_index(
            output_dir,
            manifest_sha256=manifest_sha256,
            plan_sha256=plan_sha256,
            rows=rows,
            complete=True,
        )
        terminal = _terminal_record(
            manifest_sha256=manifest_sha256,
            plan_sha256=plan_sha256,
            index=index,
            rows=rows,
        )
        terminal_path = output_dir / "COMPLETE.json"
        if terminal_path.exists():
            if terminal_path.read_bytes() != mech.canonical_json_bytes(terminal):
                raise ValueError("terminal COMPLETE record mismatch")
        else:
            # Crash recovery: verified immutable shards are authoritative, so a
            # missing last-published terminal record can be regenerated exactly.
            mech.atomic_write_json(terminal_path, terminal)
        print("Phase-0.5 raw plan already COMPLETE and verified", flush=True)
        return

    for sequence_index in range(len(rows), len(mech.FROZEN_PAIR_WORLDS)):
        world_id = mech.FROZEN_PAIR_WORLDS[sequence_index]
        print(f"world {world_id}: outcome-blind paired mechanical qualification", flush=True)
        shard = _world_shard(
            world_id=world_id,
            sequence_index=sequence_index,
            manifest=manifest,
            manifest_sha256=manifest_sha256,
            plan_sha256=plan_sha256,
            previous_record_sha256=previous,
        )
        canonical = mech.canonical_json_bytes(shard)
        compressed = mech.deterministic_gzip(canonical)
        path = output_dir / _shard_name(sequence_index, world_id)
        if path.exists():
            raise FileExistsError(f"immutable shard already exists: {path.name}")
        mech.atomic_write_bytes(path, compressed)
        if path.read_bytes() != compressed:
            raise IOError(f"shard read-back mismatch: {path.name}")
        previous = mech.sha256_bytes(canonical)
        rows.append(
            {
                "sequence_index": sequence_index,
                "world_id": world_id,
                "path": path.name,
                "sha256": mech.sha256_bytes(compressed),
                "uncompressed_sha256": previous,
                "size_bytes": len(compressed),
                "world_complete": bool(shard["world_complete"]),
            }
        )
        _publish_index(
            output_dir,
            manifest_sha256=manifest_sha256,
            plan_sha256=plan_sha256,
            rows=rows,
            complete=False,
        )
        print(
            f"world {world_id}: {'COMPLETE_VALID' if shard['world_complete'] else 'MECHANICAL_FAIL'}",
            flush=True,
        )
        mech.assert_no_forbidden_analyzer_imports()

    index = _publish_index(
        output_dir,
        manifest_sha256=manifest_sha256,
        plan_sha256=plan_sha256,
        rows=rows,
        complete=True,
    )
    terminal = _terminal_record(
        manifest_sha256=manifest_sha256,
        plan_sha256=plan_sha256,
        index=index,
        rows=rows,
    )
    mech.atomic_write_json(output_dir / "COMPLETE.json", terminal)
    mech.assert_no_forbidden_analyzer_imports()
    print("Phase-0.5 exact DEV plan executed; COMPLETE record published last", flush=True)
