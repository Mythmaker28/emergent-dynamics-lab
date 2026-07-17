"""Independent raw-only reproducer for ``DOWNSTREAM-ORDER-READER-01``.

This file deliberately imports neither the prospective runner, the scientific
contract module, nor any simulation engine.  It recomputes the numerical floor,
world contrasts, intervals, sign counts, and frozen classification directly
from persisted JSON face-flux summaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import t as student_t


RAW_SCHEMA = "DOWNSTREAM-ORDER-READER-01-RAW-v1"
MANIFEST_SCHEMA = "DOWNSTREAM-ORDER-READER-01-MANIFEST-v1"
REPRODUCER_SCHEMA = "DOWNSTREAM-ORDER-READER-01-RAW-REPRODUCTION-v1"
CLASSIFIER_VERSION = "DOWNSTREAM-ORDER-READER-01-CLASSIFIER-v1"
HISTORIES = ("H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE")
SOURCES = ("zero", "intact")
MINIMUM_VALID_WORLDS = 18
EXPECTED_WORLDS = 48
SIGN_FRACTION = 0.75
FLOAT_ATOL = 1e-12
FLOAT_RTOL = 1e-10
CLOSED_IDENTITY_RESIDUAL = 5.551115123125783e-17
LOGGER_IDENTITY_RESIDUAL = 0.0
DETERMINISTIC_REPLAY_RESIDUAL = 0.0


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: Mapping) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return sha256_bytes(encoded)


def gamma_n(operation_count: int) -> float:
    unit_roundoff = np.finfo(np.float64).eps / 2.0
    product = int(operation_count) * unit_roundoff
    if operation_count < 0 or product >= 1.0:
        raise ValueError("invalid float64 operation count")
    return float(product / (1.0 - product))


def arm_error(arm: Mapping) -> float:
    flux_abs_sum = float(arm["flux_abs_sum"])
    n_faces = int(arm["n_internal_faces"])
    j_abs = abs(float(arm["J_internal_x"]))
    dt = float(arm["dt"])
    mass = float(arm["core_mass"])
    if not all(math.isfinite(value) for value in (flux_abs_sum, j_abs, dt, mass)):
        raise ValueError("non-finite arm input")
    if flux_abs_sum < 0.0 or n_faces <= 0 or dt <= 0.0 or mass <= 0.0:
        raise ValueError("invalid arm input")
    per_face_input = n_faces * FLOAT_ATOL + FLOAT_RTOL * flux_abs_sum
    sum_roundoff = gamma_n(n_faces - 1) * (flux_abs_sum + per_face_input)
    propagated = abs(dt / mass) * (per_face_input + sum_roundoff)
    return float(propagated + gamma_n(2) * (j_abs + propagated))


def linear_error(values: Sequence[float], errors: Sequence[float], coefficients: Sequence[float]) -> float:
    propagated = sum(abs(coef) * error for coef, error in zip(coefficients, errors))
    magnitude = sum(abs(coef * value) for coef, value in zip(coefficients, values))
    return float(propagated + gamma_n(2 * len(values)) * (magnitude + propagated))


def history_contrast(history: Mapping) -> dict:
    d_values = {}
    d_errors = {}
    for source in SOURCES:
        arms = history["sources"][source]["arms"]
        values = [float(arms["plus"]["J_internal_x"]), float(arms["minus"]["J_internal_x"])]
        errors = [arm_error(arms["plus"]), arm_error(arms["minus"])]
        d_values[source] = 0.5 * (values[0] - values[1])
        d_errors[source] = linear_error(values, errors, (0.5, -0.5))
    a_value = d_values["zero"] - d_values["intact"]
    a_error = linear_error(
        [d_values["zero"], d_values["intact"]],
        [d_errors["zero"], d_errors["intact"]],
        (1.0, -1.0),
    )
    return {"D": d_values, "D_error_bound": d_errors, "A": a_value, "A_error_bound": a_error}


def world_contrast(world: Mapping) -> dict:
    histories = {name: history_contrast(world["histories"][name]) for name in HISTORIES}
    a_values = [histories[name]["A"] for name in HISTORIES]
    a_errors = [histories[name]["A_error_bound"] for name in HISTORIES]
    coefficients = (0.5, -0.5, 0.5, -0.5)
    primary = float(sum(coef * value for coef, value in zip(coefficients, a_values)))
    propagated = linear_error(a_values, a_errors, coefficients)
    zero_d = [histories[name]["D"]["zero"] for name in HISTORIES]
    zero_order = 0.5 * (zero_d[0] - zero_d[1] + zero_d[2] - zero_d[3])
    result = {
        "history_contrasts": histories,
        "delta_A_order": primary,
        "delta_num_world": max(
            propagated,
            CLOSED_IDENTITY_RESIDUAL,
            LOGGER_IDENTITY_RESIDUAL,
            DETERMINISTIC_REPLAY_RESIDUAL,
        ),
        "source_zero_order_response": float(zero_order),
    }
    calibration = []
    for name in HISTORIES:
        value = world["histories"][name].get("source_calibration", {}).get("chi_source")
        if value is None:
            calibration = []
            break
        calibration.append(float(value))
    if calibration:
        result["source_calibration_order"] = float(
            0.5 * (calibration[0] - calibration[1] + calibration[2] - calibration[3])
        )
    return result


def summary(values: Iterable[float]) -> dict:
    array = np.asarray([float(value) for value in values], dtype=float)
    if not np.isfinite(array).all():
        raise ValueError("non-finite world contrast")
    n = int(array.size)
    if n == 0:
        return {"n_worlds": 0, "mean": None, "median": None, "sd": None,
                "ci95_t": [None, None], "positive": 0, "negative": 0, "zero": 0, "values": []}
    mean = float(array.mean())
    sd = float(array.std(ddof=1)) if n > 1 else 0.0
    if n > 1:
        half = float(student_t.ppf(0.975, n - 1)) * sd / math.sqrt(n)
        interval = [mean - half, mean + half]
    else:
        interval = [None, None]
    return {
        "n_worlds": n,
        "mean": mean,
        "median": float(np.median(array)),
        "sd": sd,
        "ci95_t": [float(value) if value is not None else None for value in interval],
        "positive": int(np.sum(array > 0.0)),
        "negative": int(np.sum(array < 0.0)),
        "zero": int(np.sum(array == 0.0)),
        "values": [float(value) for value in array],
    }


def classify(worlds: Sequence[Mapping], equivalence_margin=None) -> dict:
    if any(bool(world.get("numerical_failure")) for world in worlds):
        return {"run_disposition": "NUMERICAL_FAILURE", "scientific_classification": "UNRESOLVED",
                "reason": "one_or_more_worlds_failed_numerical_gates"}
    if any(bool(world.get("manipulation_invalid")) for world in worlds):
        return {"run_disposition": "MANIPULATION_INVALID", "scientific_classification": "MANIPULATION_INVALID",
                "reason": "one_or_more_worlds_failed_mechanical_gates"}
    complete = [world for world in worlds if bool(world.get("complete_block"))]
    if len(complete) < MINIMUM_VALID_WORLDS:
        return {
            "run_disposition": "FEASIBILITY_FAIL",
            "scientific_classification": "UNRESOLVED",
            "reason": "minimum_complete_original_worlds_not_met",
            "n_complete_worlds": len(complete),
            "minimum_valid_worlds": MINIMUM_VALID_WORLDS,
        }
    recomputed = [world_contrast(world) for world in complete]
    primary = summary(row["delta_A_order"] for row in recomputed)
    delta_num = max(row["delta_num_world"] for row in recomputed)
    lower, upper = primary["ci95_t"]
    required = int(math.ceil(SIGN_FRACTION * len(complete)))
    positive = primary["positive"] >= required
    negative = primary["negative"] >= required
    if equivalence_margin is not None:
        equivalence_margin = float(equivalence_margin)
        if not math.isfinite(equivalence_margin) or equivalence_margin <= delta_num:
            raise ValueError("invalid independently declared equivalence margin")
    if equivalence_margin is not None and lower >= -equivalence_margin and upper <= equivalence_margin:
        outcome = "EQUIVALENT_AT_DECLARED_SCALE"
        reason = "two_sided_interval_within_independently_declared_scientific_margin"
    elif lower > delta_num and positive:
        outcome = "PREDICTED_ATTENUATION"
        reason = "positive_two_sided_interval_beyond_numerical_floor_with_sign_convergence"
    elif upper < -delta_num and negative:
        outcome = "OPPOSITE_SIGN_FUNCTIONAL_ACCESS"
        reason = "negative_two_sided_interval_beyond_numerical_floor_with_sign_convergence"
    elif lower <= delta_num and upper >= -delta_num and not (positive or negative):
        outcome = "NO_ACCESS_ESTABLISHED"
        reason = "interval_includes_numerical_null_without_directional_convergence_or_equivalence"
    else:
        outcome = "UNRESOLVED"
        reason = "interval_and_directional_convergence_do_not_support_a_unique_claim"
    result = {
        "run_disposition": "SCIENTIFIC_CLASSIFIED",
        "scientific_classification": outcome,
        "classification_reason": reason,
        "classifier_version": CLASSIFIER_VERSION,
        "n_complete_worlds": len(complete),
        "minimum_valid_worlds": MINIMUM_VALID_WORLDS,
        "delta_num": float(delta_num),
        "numerical_null": [-float(delta_num), float(delta_num)],
        "equivalence_margin": equivalence_margin,
        "required_directional_signs": required,
        "primary_summary": primary,
        "source_zero_order_secondary": summary(row["source_zero_order_response"] for row in recomputed),
    }
    if all("source_calibration_order" in row for row in recomputed):
        result["direct_source_calibration_secondary"] = summary(
            row["source_calibration_order"] for row in recomputed
        )
    return result


def reproduce(manifest_path: Path, raw_dir: Path) -> dict:
    manifest_raw = manifest_path.read_bytes()
    manifest_sha256 = sha256_bytes(manifest_raw)
    manifest = json.loads(manifest_raw.decode("utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("manifest schema mismatch")
    slots = manifest.get("world_slots", [])
    if len(slots) != EXPECTED_WORLDS:
        raise RuntimeError("expected exactly 48 fixed source-world slots")
    world_ids = [slot["world_id"] for slot in slots]
    if len(set(world_ids)) != EXPECTED_WORLDS:
        raise RuntimeError("duplicate manifest world identifier")
    shards = sorted((raw_dir / "worlds").glob("W*.json"))
    if [path.stem for path in shards] != world_ids:
        raise RuntimeError("raw shard set/order differs from fixed manifest")
    rows = []
    seed_tokens = set()
    shard_hashes = {}
    stored_contrast_checks = []
    for path, slot in zip(shards, slots):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("schema") != RAW_SCHEMA:
            raise RuntimeError(f"raw schema mismatch: {path}")
        if row.get("world_id") != slot["world_id"] or row.get("seed") != slot["seed"]:
            raise RuntimeError(f"manifest/raw world mismatch: {path}")
        if row.get("manifest_sha256") != manifest_sha256:
            raise RuntimeError(f"manifest hash mismatch: {path}")
        if row.get("seed") in seed_tokens:
            raise RuntimeError("duplicate raw world seed")
        seed_tokens.add(row.get("seed"))
        shard_hashes[path.name] = sha256_file(path)
        if row.get("complete_block"):
            computed = world_contrast(row)
            stored_ok = bool(
                np.isclose(computed["delta_A_order"], float(row["delta_A_order"]), atol=0.0, rtol=0.0)
                and np.isclose(computed["delta_num_world"], float(row["delta_num_world"]), atol=0.0, rtol=0.0)
                and np.isclose(computed["source_zero_order_response"],
                              float(row["source_zero_order_response"]), atol=0.0, rtol=0.0)
            )
            stored_contrast_checks.append({"world_id": row["world_id"], "exact": stored_ok})
            if not stored_ok:
                raise RuntimeError(f"stored contrast mismatch: {path}")
        rows.append(row)
    classification = classify(rows, manifest.get("equivalence_margin"))
    return {
        "schema": REPRODUCER_SCHEMA,
        "status": "PASS",
        "manifest_sha256": manifest_sha256,
        "n_raw_worlds": len(rows),
        "n_complete_worlds": sum(bool(row.get("complete_block")) for row in rows),
        "duplicate_worlds_absent": len(seed_tokens) == len(rows),
        "all_stored_complete_world_contrasts_exact": all(
            check["exact"] for check in stored_contrast_checks
        ),
        "stored_contrast_checks": stored_contrast_checks,
        "classification": classification,
        "raw_shard_sha256": shard_hashes,
        "engine_or_runner_imported": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = reproduce(args.manifest, args.raw_dir)
    digest = atomic_write_json(args.output, report)
    print(json.dumps({"status": report["status"], "output_sha256": digest,
                      "classification": report["classification"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
