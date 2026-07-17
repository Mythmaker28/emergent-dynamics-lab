"""Unexecuted prospective runner for ``DOWNSTREAM-ORDER-READER-01``.

The module contains no seed family.  Importing it cannot initialize a world or
import the simulator.  Scientific imports occur only inside
``execute_scientific_world`` after a separately human-sealed manifest has
passed every preflight gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import replace
from pathlib import Path
from typing import Callable, Mapping, Sequence

from experiments.individuation import downstream_order_reader_contract as contract


RUN_STATE_SCHEMA = "DOWNSTREAM-ORDER-READER-01-RUN-STATE-v1"
RESULTS_SCHEMA = "DOWNSTREAM-ORDER-READER-01-RESULTS-v1"
PACKAGE_MODE = "PROSPECTIVE_UNSEALED_NO_SEEDS"
SEALED_MODE = "PROSPECTIVE_HUMAN_SEALED"
PARENT_COMMIT = "75e405627e0b48428a5c71f31b8a2025726b763c"

HISTORY_NAMES = contract.HISTORY_NAMES
SOURCE_VALUES = {"zero": 0.0, "intact": 0.15}
RAMP_VALUES = {"minus": -1, "sham": 0, "plus": 1}
SETTLE_STEPS = 40
SOURCE_STEPS = 1
RESPONSE_STEPS = 1
RAMP_EPSILON_C = 0.01
CORE_RADIUS = 10
EXPECTED_CORE_CELLS = 317
EXPECTED_INTERNAL_X_FACES = 296


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: Mapping) -> str:
    """Write one finite JSON object atomically and return its byte hash."""

    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return sha256_bytes(encoded)


def _is_placeholder(value) -> bool:
    return isinstance(value, str) and value.startswith("<") and value.endswith(">")


def validate_manifest_payload(manifest: Mapping, *, require_execution: bool) -> None:
    """Validate either the seedless template or a future human-sealed manifest."""

    if manifest.get("schema") != contract.MANIFEST_SCHEMA:
        raise RuntimeError("manifest schema mismatch")
    if manifest.get("accepted_parent") != PARENT_COMMIT:
        raise RuntimeError("accepted parent mismatch")
    if manifest.get("statistical_unit") != "original source world":
        raise RuntimeError("statistical unit mismatch")
    if manifest.get("branches_and_arms_increase_n") is not False:
        raise RuntimeError("pseudoreplication contract mismatch")
    if int(manifest.get("fixed_maximum_source_worlds", -1)) != contract.MAX_SOURCE_WORLDS:
        raise RuntimeError("fixed family maximum mismatch")
    if int(manifest.get("minimum_complete_worlds", -1)) != contract.MINIMUM_VALID_WORLDS:
        raise RuntimeError("minimum complete-world gate mismatch")
    if manifest.get("adaptive_extension_after_outcomes") is not False:
        raise RuntimeError("adaptive extension must be forbidden")
    design = manifest.get("design", {})
    expected_design = {
        "histories": list(HISTORY_NAMES),
        "source_lam_minus": SOURCE_VALUES,
        "ramp_arms": RAMP_VALUES,
        "settle_steps": SETTLE_STEPS,
        "source_expression_steps": SOURCE_STEPS,
        "response_steps": RESPONSE_STEPS,
        "ramp_epsilon_c": RAMP_EPSILON_C,
        "core_radius": CORE_RADIUS,
        "response_lam_minus": 0.15,
        "up_ref_zero": True,
    }
    if design != expected_design:
        raise RuntimeError("prospective design binding mismatch")
    if manifest.get("equivalence_margin") is not None:
        raise RuntimeError("this package freezes no scientific equivalence margin")
    slots = manifest.get("world_slots", [])
    if len(slots) != contract.MAX_SOURCE_WORLDS:
        raise RuntimeError("manifest must contain exactly 48 fixed world slots")
    world_ids = [slot.get("world_id") for slot in slots]
    if world_ids != [f"W{index:03d}" for index in range(1, contract.MAX_SOURCE_WORLDS + 1)]:
        raise RuntimeError("world slot identifiers/order mismatch")
    if len(set(world_ids)) != len(world_ids):
        raise RuntimeError("duplicate world identifiers")

    seeds = [slot.get("seed") for slot in slots]
    if require_execution:
        if manifest.get("mode") != SEALED_MODE:
            raise RuntimeError("REFUSED: prospective manifest is not human sealed")
        if manifest.get("execution_authorized") is not True:
            raise RuntimeError("REFUSED: execution_authorized is not true")
        if manifest.get("human_review", {}).get("status") != "APPROVED_FOR_EXECUTION":
            raise RuntimeError("REFUSED: human review is not APPROVED_FOR_EXECUTION")
        if manifest.get("namespace_audit", {}).get("status") != "PASS":
            raise RuntimeError("REFUSED: future namespace audit is not PASS")
        if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
            raise RuntimeError("REFUSED: every sealed slot requires one integer seed")
        if len(set(seeds)) != len(seeds):
            raise RuntimeError("REFUSED: duplicate scientific seeds")
    else:
        if manifest.get("mode") != PACKAGE_MODE:
            raise RuntimeError("seedless template mode mismatch")
        if manifest.get("execution_authorized") is not False:
            raise RuntimeError("seedless template cannot authorize execution")
        if any(not _is_placeholder(seed) for seed in seeds):
            raise RuntimeError("seedless template unexpectedly contains a seed value")
        if manifest.get("namespace_audit", {}).get("status") != "NOT_PERFORMED":
            raise RuntimeError("seedless package must not select or audit a namespace")


def load_manifest(path: Path, *, require_execution: bool) -> tuple[dict, str]:
    raw = path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    validate_manifest_payload(manifest, require_execution=require_execution)
    return manifest, sha256_bytes(raw)


def prospective_execution_order(seed: int) -> tuple[str, ...]:
    """Outcome-independent history order; accepts a seed only after preflight."""

    return tuple(sorted(HISTORY_NAMES, key=lambda name: hashlib.sha256(
        f"DOWNSTREAM-ORDER-READER-01|{int(seed)}|{name}".encode("ascii")
    ).digest()))


def _frame_sha256(frame: Mapping) -> str:
    import numpy as np

    digest = hashlib.sha256()
    for field in sorted(frame):
        array = np.ascontiguousarray(frame[field])
        digest.update(str(field).encode("utf-8"))
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _mask_sha256(mask) -> str:
    import numpy as np

    return hashlib.sha256(np.ascontiguousarray(mask, dtype=np.uint8).tobytes()).hexdigest()


def _copy_driver(ns, ring, frames: Sequence[Mapping], label: str):
    copied = [
        {field: values.copy() for field, values in frame.items()}
        for frame in frames
    ]
    return ns.BoundaryDriver(ring.copy(), copied, label=label)


def _public_settle(settled: Mapping) -> dict:
    return {key: value for key, value in settled.items() if key not in {"state", "region"}}


def _settle_history(*, deep, core, boundary, modules) -> dict:
    np, ns, bh, cc, parent, _, mcm_config, _ = modules
    current = bh.standardized_probe_start(deep["state"])
    tracker = parent._new_tracker([deep["region"]], current.step)
    engine = ns.NoSwapClampEngine(
        mcm_config.SPEC,
        cc.MEM_INTACT,
        mcm_config.TRACER,
        driver=_copy_driver(ns, boundary.ring, boundary.frames[:SETTLE_STEPS], "common-settle"),
        up_ref_zero=True,
    )
    events = {}
    max_coverage = 0.0
    for elapsed in range(1, SETTLE_STEPS + 1):
        current = engine.step(current)
        update = parent._tracker_update(tracker, current)
        max_coverage = max(max_coverage, float(update["coverage"]))
        for track_id, status in update["events"].items():
            events.setdefault(str(track_id), {
                "elapsed_step": elapsed,
                "absolute_step": int(current.step),
                "status": status,
            })
    alive = parent._focal_alive(tracker, 0)
    region = tracker.tracks[0].mask.copy() if alive else np.zeros_like(core)
    body_inside = bool(alive and not np.any(region & ~core))
    valid = bool(alive and not events and max_coverage < parent.COVER_CAP and body_inside)
    return {
        "valid": valid,
        "state": current,
        "region": region,
        "events": events,
        "max_coverage": max_coverage,
        "body_inside_core": body_inside,
        "state_sha256": parent.state_hash(current),
        "core_mass": float(current.rho[core].sum()),
        "reason": None if valid else "common_settle_viability_or_geometry_fail",
    }


def _history_probe(*, deep, reference, modules) -> dict:
    np, ns, bh, cc, parent, inst, mcm_config, eps = modules
    geometry = parent._geometry(deep)
    if not geometry["valid"]:
        return {"valid": False, "mechanical_invalid": False, "reason": geometry["reason"]}
    core = geometry["core"]
    ring = geometry["ring"]
    if np.any(core & ring):
        return {"valid": False, "mechanical_invalid": True, "reason": "core_collar_overlap"}
    ramp_geometry = inst.integer_disk_ramp_geometry(
        deep["state"].rho.shape,
        tuple(int(value) for value in geometry["partition"].center),
        CORE_RADIUS,
    )
    if not np.array_equal(core, ramp_geometry.core):
        return {"valid": False, "mechanical_invalid": True, "reason": "core_geometry_mismatch"}
    internal_mask = inst.positive_face_masks(core, axis=-1).internal
    if int(core.sum()) != EXPECTED_CORE_CELLS or int(internal_mask.sum()) != EXPECTED_INTERNAL_X_FACES:
        return {"valid": False, "mechanical_invalid": True, "reason": "core_or_face_count_mismatch"}

    shift = ns._shift(reference["center"], deep["center"])
    source_engine = parent.DiagEngine(
        mcm_config.SPEC, cc.MEM_INTACT, mcm_config.TRACER, up_ref_zero=True,
    )
    boundary = ns.record_boundary(
        bh.standardized_probe_start(reference["state"]),
        source_engine,
        ring,
        SETTLE_STEPS + SOURCE_STEPS + RESPONSE_STEPS,
        shift=shift,
        label="same-seed-no-history-no-drive-common-42-step-boundary",
    )
    settled = _settle_history(deep=deep, core=core, boundary=boundary, modules=modules)
    if not settled["valid"]:
        return {
            "valid": False,
            "mechanical_invalid": False,
            "reason": settled["reason"],
            "settle": _public_settle(settled),
        }

    settled_hash = parent.state_hash(settled["state"])
    source_inputs = {label: settled["state"].copy() for label in contract.SOURCE_LABELS}
    source_input_hashes = {label: parent.state_hash(state) for label, state in source_inputs.items()}
    exact_source_clones = len(set(source_input_hashes.values())) == 1
    source_frame = boundary.frames[SETTLE_STEPS]
    response_frame = boundary.frames[SETTLE_STEPS + SOURCE_STEPS]
    source_outputs = {}
    for label in contract.SOURCE_LABELS:
        mem = replace(cc.MEM_INTACT, lam_minus=SOURCE_VALUES[label])
        engine = ns.NoSwapClampEngine(
            mcm_config.SPEC, mem, mcm_config.TRACER,
            driver=_copy_driver(ns, ring, [source_frame], f"source:{label}"),
            up_ref_zero=True,
        )
        source_outputs[label] = engine.step(source_inputs[label])

    non_c_exact = all(
        np.array_equal(getattr(source_outputs["zero"], field), getattr(source_outputs["intact"], field))
        for field in ns.STATE_FIELDS if field != "c"
    ) and source_outputs["zero"].step == source_outputs["intact"].step
    source_only_valid = bool(exact_source_clones and non_c_exact)

    intact_output = source_outputs["intact"]
    memory = intact_output.Mf / np.maximum(intact_output.rho, eps)[None, :, :]
    m_minus = np.tanh(memory[0] - memory[1])
    weighted_mminus = float((source_inputs["intact"].rho * m_minus)[core].sum())
    source_calibration = float(
        mcm_config.SPEC.dt * mcm_config.SPEC.s * SOURCE_VALUES["intact"] * weighted_mminus
    )

    sources = {}
    mechanical_valid = source_only_valid
    all_viable = True
    ramp_totals_reference = None
    for source_label in contract.SOURCE_LABELS:
        source_output = source_outputs[source_label]
        core_mass = float(source_output.rho[core].sum())
        if not math.isfinite(core_mass) or core_mass <= 0.0:
            return {"valid": False, "mechanical_invalid": True, "reason": "nonpositive_core_mass"}
        arms = {}
        ramp_totals = {}
        ramp_directions = {}
        for arm_label in contract.RAMP_LABELS:
            arm_value = RAMP_VALUES[arm_label]
            response_input = source_output.copy()
            response_input.c = inst.apply_matched_c_ramp(
                source_output.c,
                ramp_geometry,
                arm=arm_value,
                epsilon_c=RAMP_EPSILON_C,
            )
            addition = response_input.c - source_output.c
            ramp_totals[arm_label] = float(addition.sum())
            ramp_directions[arm_label] = hashlib.sha256(
                np.ascontiguousarray(addition).tobytes()
            ).hexdigest()
            nonnegative = bool(np.isfinite(response_input.c).all() and np.all(response_input.c >= 0.0))
            non_c_ramp_exact = all(
                np.array_equal(getattr(response_input, field), getattr(source_output, field))
                for field in ns.STATE_FIELDS if field != "c"
            ) and response_input.step == source_output.step

            logged_engine = inst.PassiveFluxNoSwapClampEngine(
                mcm_config.SPEC, cc.MEM_INTACT, mcm_config.TRACER,
                driver=_copy_driver(ns, ring, [response_frame], f"response-logged:{source_label}:{arm_label}"),
                up_ref_zero=True,
            )
            response_output = logged_engine.step(response_input.copy())
            records = logged_engine.face_flux_records
            x_records = [record for record in records if record.axis == -1]
            axes_exact = tuple(record.axis for record in records) == (-2, -1)
            if len(x_records) != 1:
                return {"valid": False, "mechanical_invalid": True, "reason": "x_flux_record_count"}
            flux_x = x_records[0].flux
            j_value = inst.mass_specific_internal_x_face_flux_sum(
                flux_x, core, mass=core_mass, dt=mcm_config.SPEC.dt,
            )

            unlogged_engine = ns.NoSwapClampEngine(
                mcm_config.SPEC, cc.MEM_INTACT, mcm_config.TRACER,
                driver=_copy_driver(ns, ring, [response_frame], f"response-unlogged:{source_label}:{arm_label}"),
                up_ref_zero=True,
            )
            unlogged_output = unlogged_engine.step(response_input.copy())
            logger_identity = parent.state_hash(response_output) == parent.state_hash(unlogged_output)

            tracker = parent._new_tracker([settled["region"]], settled["state"].step)
            source_update = parent._tracker_update(tracker, source_output)
            response_update = parent._tracker_update(tracker, response_output)
            tracker_events = {
                "source": {str(key): value for key, value in source_update["events"].items()},
                "response": {str(key): value for key, value in response_update["events"].items()},
            }
            alive = parent._focal_alive(tracker, 0)
            final_region = tracker.tracks[0].mask.copy() if alive else np.zeros_like(core)
            body_inside = bool(alive and not np.any(final_region & ~core))
            viability = bool(
                alive and not tracker_events["source"] and not tracker_events["response"]
                and max(float(source_update["coverage"]), float(response_update["coverage"])) < parent.COVER_CAP
                and body_inside
            )
            all_viable = all_viable and viability
            arm_mechanical = bool(nonnegative and non_c_ramp_exact and axes_exact and logger_identity)
            mechanical_valid = mechanical_valid and arm_mechanical
            arms[arm_label] = {
                "J_internal_x": float(j_value),
                "flux_abs_sum": float(np.abs(flux_x[internal_mask]).sum()),
                "n_internal_faces": int(internal_mask.sum()),
                "dt": float(mcm_config.SPEC.dt),
                "core_mass": core_mass,
                "response_input_sha256": parent.state_hash(response_input),
                "response_output_sha256": parent.state_hash(response_output),
                "unlogged_output_sha256": parent.state_hash(unlogged_output),
                "face_mask_sha256": _mask_sha256(internal_mask),
                "flux_x_sha256": hashlib.sha256(np.ascontiguousarray(flux_x).tobytes()).hexdigest(),
                "gates": {
                    "ramp_nonnegative": nonnegative,
                    "ramp_changes_only_c": non_c_ramp_exact,
                    "passive_logger_identity": logger_identity,
                    "logged_axis_order_exact": axes_exact,
                    "tracker_viability": viability,
                    "body_inside_fixed_core": body_inside,
                },
                "tracker_events": tracker_events,
            }
        ramp_mass_equal = bool(
            np.allclose(
                [ramp_totals[label] for label in contract.RAMP_LABELS],
                [ramp_totals["sham"]] * 3,
                atol=contract.FLOAT_ATOL,
                rtol=contract.FLOAT_RTOL,
            )
        )
        ramp_sign_reversal = bool(np.allclose(
            inst.apply_matched_c_ramp(source_output.c, ramp_geometry, arm=1, epsilon_c=RAMP_EPSILON_C)
            - inst.apply_matched_c_ramp(source_output.c, ramp_geometry, arm=0, epsilon_c=RAMP_EPSILON_C),
            -(inst.apply_matched_c_ramp(source_output.c, ramp_geometry, arm=-1, epsilon_c=RAMP_EPSILON_C)
              - inst.apply_matched_c_ramp(source_output.c, ramp_geometry, arm=0, epsilon_c=RAMP_EPSILON_C)),
            atol=contract.FLOAT_ATOL,
            rtol=contract.FLOAT_RTOL,
        ))
        mechanical_valid = mechanical_valid and ramp_mass_equal and ramp_sign_reversal
        if ramp_totals_reference is None:
            ramp_totals_reference = ramp_totals
        else:
            mechanical_valid = mechanical_valid and all(
                np.isclose(ramp_totals[label], ramp_totals_reference[label],
                           atol=contract.FLOAT_ATOL, rtol=contract.FLOAT_RTOL)
                for label in contract.RAMP_LABELS
            )
        sources[source_label] = {
            "lam_minus_during_source_only": SOURCE_VALUES[source_label],
            "source_input_sha256": source_input_hashes[source_label],
            "source_output_sha256": parent.state_hash(source_output),
            "pre_ramp_core_mass": core_mass,
            "arms": arms,
            "ramp_total_addition": ramp_totals,
            "ramp_pattern_sha256": ramp_directions,
            "gates": {
                "ramp_mass_equal": ramp_mass_equal,
                "ramp_direction_sign_reversal": ramp_sign_reversal,
            },
        }

    raw_history = {
        "valid": bool(mechanical_valid and all_viable),
        "mechanical_invalid": not mechanical_valid,
        "settle": _public_settle(settled),
        "deep_state_sha256": deep["state_sha256"],
        "settled_state_sha256": settled_hash,
        "source_input_clone_sha256": source_input_hashes,
        "source_calibration": {
            "chi_source": source_calibration,
            "weighted_mminus": weighted_mminus,
            "direction_is_not_a_validity_gate": True,
        },
        "support": {
            "core_sha256": _mask_sha256(core),
            "internal_x_face_mask_sha256": _mask_sha256(internal_mask),
            "core_cells": int(core.sum()),
            "internal_x_faces": int(internal_mask.sum()),
        },
        "diagnostic_baselines_not_used_for_correction": {
            "body_mass": float(deep["entity"].mass),
            "body_size": int(deep["entity"].size),
            "body_rg": float(deep["entity"].rg),
            "nearest_neighbor_distance": float(parent._nearest_neighbor_distance(deep["state"], deep["entity"])),
            "global_up_ref_pre_settle": float(
                deep["state"].uptake[deep["state"].rho > 1e-4].mean()
            ) if np.any(deep["state"].rho > 1e-4) else 0.0,
            "global_N_mean_pre_settle": float(deep["state"].N.mean()),
            "global_c_mean_pre_settle": float(deep["state"].c.mean()),
            "global_rho_mass_pre_settle": float(deep["state"].rho.sum()),
            "up_ref_zero_during_standardized_assay": True,
        },
        "boundary": {
            "label": boundary.label,
            "translation": list(shift),
            "settle_frame_sha256": [_frame_sha256(frame) for frame in boundary.frames[:SETTLE_STEPS]],
            "source_frame_sha256": _frame_sha256(source_frame),
            "response_frame_sha256": _frame_sha256(response_frame),
        },
        "sources": sources,
        "gates": {
            "one_common_settle": True,
            "exact_source_input_clones": exact_source_clones,
            "source_outputs_differ_only_in_c_if_at_all": non_c_exact,
            "source_lam_varies_one_update_only": True,
            "common_response_lam_minus": True,
            "common_source_and_response_frames": True,
            "tracker_independent_primary_endpoint": True,
            "viability_all_arms": all_viable,
        },
    }
    raw_history.update(contract.recompute_history_contrasts(raw_history))
    return raw_history


def execute_scientific_world(slot: Mapping, manifest: Mapping) -> dict:
    """Run one future world, reachable only after sealed-manifest preflight.

    This function is intentionally never called by package qualification tests.
    """

    import numpy as np
    from edlab.experiments.sc_mcm import config as mcm_config
    from edlab.substrates.scaffold.engine import EPS
    from experiments.individuation import access_structure_noswap_operators as ns
    from experiments.individuation import balanced_history_isolation_dev as bh
    from experiments.individuation import causal_confirm as cc
    from experiments.individuation import counterfactual_history_core_dev as parent
    from experiments.individuation import downstream_order_reader_instrumentation as inst

    modules = (np, ns, bh, cc, parent, inst, mcm_config, EPS)
    seed = int(slot["seed"])
    world_id = str(slot["world_id"])
    checkpoint = parent.make_checkpoint(seed)
    clone_gate = parent.validate_four_clones(checkpoint)
    base = {
        "schema": contract.RAW_SCHEMA,
        "world_id": world_id,
        "seed": seed,
        "original_world_statistical_unit": True,
        "complete_block": False,
        "manipulation_invalid": False,
        "numerical_failure": False,
        "prehistory_eligible": checkpoint["focal_id"] is not None,
        "checkpoint_bundle_sha256": checkpoint["checkpoint_bundle_sha256"],
        "clone_gate": clone_gate,
        "execution_order": list(prospective_execution_order(seed)),
    }
    if checkpoint["focal_id"] is None:
        base["world_disposition"] = "PREHISTORY_INELIGIBLE"
        return base
    if not clone_gate["valid"]:
        base.update(manipulation_invalid=True, world_disposition="EXACT_CLONE_GATE_FAIL")
        return base

    histories = parent.run_histories(checkpoint, prospective_execution_order(seed))
    if not all(histories[name]["valid"] for name in HISTORY_NAMES):
        base["world_disposition"] = "INCOMPLETE_HISTORY_SURVIVAL"
        return base
    deep = {
        name: parent.turnover_fixed(histories[name]["state"], histories[name]["focal_region"])
        for name in HISTORY_NAMES
    }
    if not all(deep[name]["valid"] for name in HISTORY_NAMES):
        base["world_disposition"] = "INCOMPLETE_DEEP_TURNOVER"
        return base
    reference = parent.no_drive_reference(checkpoint)
    if not reference["valid"]:
        base["world_disposition"] = "INCOMPLETE_BOUNDARY_REFERENCE"
        return base

    probed = {
        name: _history_probe(deep=deep[name], reference=reference, modules=modules)
        for name in HISTORY_NAMES
    }
    base["histories"] = probed
    if any(history.get("mechanical_invalid") for history in probed.values()):
        base.update(manipulation_invalid=True, world_disposition="MANIPULATION_INVALID")
        return base
    if not all(history.get("valid") for history in probed.values()):
        base["world_disposition"] = "INCOMPLETE_PROBE_VIABILITY"
        return base

    try:
        recomputed = contract.recompute_world_contrast(base)
    except (ValueError, KeyError, FloatingPointError):
        base.update(numerical_failure=True, world_disposition="NUMERICAL_FAILURE")
        return base
    base.update(recomputed)
    base.update(complete_block=True, world_disposition="COMPLETE")
    return base


def _validate_existing_shards(output_dir: Path, manifest: Mapping, manifest_sha256: str) -> list[dict]:
    slots = manifest["world_slots"]
    expected = {slot["world_id"]: slot for slot in slots}
    shard_dir = output_dir / "worlds"
    all_json = sorted(shard_dir.glob("*.json")) if shard_dir.exists() else []
    if any(path.name != f"W{index:03d}.json" for index, path in enumerate(all_json, start=1)):
        raise RuntimeError("world shard directory is not the fixed ordered prefix")
    shards = all_json
    rows = []
    seen_seeds = set()
    for shard in shards:
        payload = json.loads(shard.read_text(encoding="utf-8"))
        world_id = payload.get("world_id")
        if world_id not in expected or shard.name != f"{world_id}.json":
            raise RuntimeError(f"unexpected or misnamed world shard: {shard}")
        if payload.get("manifest_sha256") != manifest_sha256:
            raise RuntimeError(f"manifest binding mismatch in {shard}")
        if payload.get("seed") != expected[world_id]["seed"]:
            raise RuntimeError(f"seed/slot mismatch in {shard}")
        if payload.get("seed") in seen_seeds:
            raise RuntimeError("duplicate completed scientific seed")
        seen_seeds.add(payload.get("seed"))
        rows.append(payload)
    expected_prefix = [slot["world_id"] for slot in slots[:len(rows)]]
    if [row["world_id"] for row in rows] != expected_prefix:
        raise RuntimeError("resume shards are not the fixed ordered prefix")
    return rows


def run_sealed_family(
    manifest_path: Path,
    output_dir: Path,
    *,
    executor: Callable[[Mapping, Mapping], dict] = execute_scientific_world,
) -> dict:
    """Execute/resume the fixed family after human sealing; never extend it."""

    manifest, manifest_sha256 = load_manifest(manifest_path, require_execution=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = _validate_existing_shards(output_dir, manifest, manifest_sha256)
    slots = manifest["world_slots"]
    run_state_path = output_dir / "run_state.json"
    for slot in slots[len(rows):]:
        run_state = {
            "schema": RUN_STATE_SCHEMA,
            "status": "RUNNING",
            "manifest_sha256": manifest_sha256,
            "fixed_world_count": len(slots),
            "completed_world_ids": [row["world_id"] for row in rows],
            "next_world_id": slot["world_id"],
        }
        atomic_write_json(run_state_path, run_state)
        row = executor(slot, manifest)
        if row.get("schema") != contract.RAW_SCHEMA:
            raise RuntimeError("executor returned a raw schema mismatch")
        if row.get("world_id") != slot["world_id"] or row.get("seed") != slot["seed"]:
            raise RuntimeError("executor returned a mismatched or duplicate world")
        row = dict(row)
        row["manifest_sha256"] = manifest_sha256
        atomic_write_json(output_dir / "worlds" / f"{slot['world_id']}.json", row)
        rows.append(row)

    classification = contract.classify_worlds(
        rows,
        minimum_valid_worlds=manifest["minimum_complete_worlds"],
        equivalence_margin=manifest.get("equivalence_margin"),
    )
    results = {
        "schema": RESULTS_SCHEMA,
        "status": "COMPLETE",
        "manifest_sha256": manifest_sha256,
        "n_fixed_source_worlds": len(slots),
        "n_complete_worlds": sum(bool(row.get("complete_block")) for row in rows),
        "classification": classification,
        "world_shards": [f"worlds/{row['world_id']}.json" for row in rows],
    }
    results_sha256 = atomic_write_json(output_dir / "results.json", results)
    atomic_write_json(run_state_path, {
        "schema": RUN_STATE_SCHEMA,
        "status": "COMPLETE",
        "manifest_sha256": manifest_sha256,
        "fixed_world_count": len(slots),
        "completed_world_ids": [row["world_id"] for row in rows],
        "results_sha256": results_sha256,
    })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--validate-template", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.validate_template == args.execute:
        parser.error("select exactly one of --validate-template or --execute")
    if args.validate_template:
        _, digest = load_manifest(args.manifest, require_execution=False)
        print(json.dumps({"status": "VALID_UNSEALED_TEMPLATE", "manifest_sha256": digest}, sort_keys=True))
        return
    if args.output_dir is None:
        parser.error("--output-dir is required with --execute")
    results = run_sealed_family(args.manifest, args.output_dir)
    print(json.dumps(results["classification"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
