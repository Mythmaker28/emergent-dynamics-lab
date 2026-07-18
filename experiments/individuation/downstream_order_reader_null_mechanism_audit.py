"""Standard-library raw-only audit for DOWNSTREAM-ORDER-READER-01.

This module deliberately imports neither the prospective runner, the sealed
reproducer, nor any engine. It verifies immutable persisted artefacts and
fails closed when numerical face-level quantities required by the frozen
mechanistic decomposition are absent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Mapping, Sequence


SCHEMA = "DOWNSTREAM-ORDER-READER-01-NULL-MECHANISM-RAW-AUDIT-v1"
EXPECTED_HEAD = "d71c7ebb14cb74d47bbaac7858f4ec0286240bdb"
EXPECTED_MANIFEST_SHA256 = "0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4"
EXPECTED_RAW_COLLECTION_SHA256 = "8d4baaac198cf5e5526359ad723d4cebd0c0614ffa2441fead41144ef573adf1"
EXPECTED_REPRODUCTION_SHA256 = "35616172409424d28d765acecb2c29ac1f2527fb7acd48196a9113e85081b679"
EXPECTED_CLASSIFICATION = "NO_ACCESS_ESTABLISHED"
EXPECTED_COMPLETE = 35
EXPECTED_WORLDS = 48


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def raw_collection_sha256(raw_dir: Path) -> str:
    lines = []
    for path in sorted(path for path in raw_dir.rglob("*") if path.is_file()):
        relative = path.relative_to(raw_dir).as_posix()
        lines.append(f"{relative}\t{sha256_file(path)}\n")
    return sha256_bytes("".join(lines).encode("utf-8"))


def cancellation_index(contributions: Sequence[float]) -> dict:
    signed = float(sum(float(value) for value in contributions))
    absolute = float(sum(abs(float(value)) for value in contributions))
    if absolute == 0.0:
        if signed != 0.0:
            raise ArithmeticError("nonzero signed sum with zero absolute sum")
        return {
            "signed_sum": 0.0,
            "absolute_sum": 0.0,
            "cancellation_index": 0.0,
            "cancellation_zero_denominator": True,
        }
    return {
        "signed_sum": signed,
        "absolute_sum": absolute,
        "cancellation_index": abs(signed) / absolute,
        "cancellation_zero_denominator": False,
    }


def _face_array_available(arm: Mapping, n_faces: int) -> bool:
    # The sealed raw schema stores scalars and hashes. A numerical list of the
    # exact internal-face length would be minimally necessary for decomposition.
    return any(
        isinstance(value, list)
        and len(value) == n_faces
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        for value in arm.values()
    )


def _source_c_array_available(source: Mapping, core_cells: int) -> bool:
    return any(
        isinstance(value, list)
        and len(value) == core_cells
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        for value in source.values()
    )


def _boundary_numeric_flux_available(boundary: Mapping) -> bool:
    for key, value in boundary.items():
        if "flux" not in str(key).lower():
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if isinstance(value, list) and value and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
        ):
            return True
    return False


def audit(repo_root: Path, plan_path: Path) -> dict:
    manifest_path = repo_root / "docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json"
    raw_dir = repo_root / "results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001"
    reproduction_path = repo_root / "results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001-independent-reproduction.json"

    manifest = read_json(manifest_path)
    results = read_json(raw_dir / "results.json")
    run_state = read_json(raw_dir / "run_state.json")
    reproduction = read_json(reproduction_path)
    shards = sorted((raw_dir / "worlds").glob("W*.json"))
    worlds = [read_json(path) for path in shards]

    expected_ids = [f"W{index:03d}" for index in range(1, EXPECTED_WORLDS + 1)]
    expected_seeds = list(range(58001, 58049))
    manifest_sha = sha256_file(manifest_path)
    collection_sha = raw_collection_sha256(raw_dir)
    reproduction_sha = sha256_file(reproduction_path)

    immutability = {
        "manifest_sha256_exact": manifest_sha == EXPECTED_MANIFEST_SHA256,
        "raw_collection_sha256_exact": collection_sha == EXPECTED_RAW_COLLECTION_SHA256,
        "reproduction_sha256_exact": reproduction_sha == EXPECTED_REPRODUCTION_SHA256,
        "all_48_ordered_records": [row.get("world_id") for row in worlds] == expected_ids,
        "all_48_ordered_seeds": [row.get("seed") for row in worlds] == expected_seeds,
        "run_state_complete_48": run_state.get("status") == "COMPLETE"
        and run_state.get("completed_world_ids") == expected_ids,
        "complete_world_count_35": sum(bool(row.get("complete_block")) for row in worlds) == EXPECTED_COMPLETE,
        "stored_complete_world_contrasts_exact": len(reproduction.get("stored_contrast_checks", []))
        == EXPECTED_COMPLETE
        and all(check.get("exact") is True for check in reproduction.get("stored_contrast_checks", [])),
        "classification_object_exact": results.get("classification") == reproduction.get("classification"),
        "frozen_classification_exact": results.get("classification", {}).get("scientific_classification")
        == EXPECTED_CLASSIFICATION,
        "no_manipulation_or_numerical_failure": not any(
            bool(row.get("manipulation_invalid")) or bool(row.get("numerical_failure")) for row in worlds
        ),
        "all_parent_bound_files_exact": all(
            sha256_file(repo_root / path) == expected for path, expected in manifest.get("bound_files", {}).items()
        ),
        "existing_reproduction_engine_or_runner_imported_false": reproduction.get(
            "engine_or_runner_imported"
        ) is False,
    }
    if not all(immutability.values()):
        raise RuntimeError("immutable prospective input audit failed")

    world_rows = []
    for world in worlds:
        if not world.get("complete_block"):
            continue
        histories = world["histories"]
        source_c_arrays = []
        face_arrays = []
        boundary_values = []
        for history in histories.values():
            core_cells = int(history["support"]["core_cells"])
            n_faces = int(history["support"]["internal_x_faces"])
            boundary_values.append(_boundary_numeric_flux_available(history["boundary"]))
            for source in history["sources"].values():
                source_c_arrays.append(_source_c_array_available(source, core_cells))
                for arm in source["arms"].values():
                    face_arrays.append(_face_array_available(arm, n_faces))
        world_rows.append(
            {
                "world_id": world["world_id"],
                "seed": world["seed"],
                "stored_delta_A_O": world["delta_A_order"],
                "source_core_c_values_available": all(source_c_arrays),
                "internal_face_values_available": all(face_arrays),
                "boundary_flux_values_available": all(boundary_values),
                "mechanism_status": "RAW_INSUFFICIENT",
            }
        )

    aggregate_fields_present = all(
        all(
            all(
                {"J_internal_x", "flux_abs_sum", "n_internal_faces", "flux_x_sha256"}.issubset(arm)
                for source in history["sources"].values()
                for arm in source["arms"].values()
            )
            for history in world["histories"].values()
        )
        for world in worlds
        if world.get("complete_block")
    )
    source_values_available = all(row["source_core_c_values_available"] for row in world_rows)
    face_values_available = all(row["internal_face_values_available"] for row in world_rows)
    boundary_values_available = all(row["boundary_flux_values_available"] for row in world_rows)
    sufficient = source_values_available and face_values_available

    if sufficient:
        raise RuntimeError("raw unexpectedly sufficient; this fail-closed auditor has no authorized output path")

    return {
        "schema": SCHEMA,
        "status": "PASS_IMMUTABILITY_RAW_INSUFFICIENT",
        "accepted_result_commit": EXPECTED_HEAD,
        "manifest_sha256": manifest_sha,
        "raw_collection_sha256": collection_sha,
        "reproduction_sha256": reproduction_sha,
        "frozen_plan_sha256": sha256_file(plan_path),
        "immutability_checks": immutability,
        "frozen_result": results["classification"],
        "n_raw_worlds": len(worlds),
        "n_complete_worlds": len(world_rows),
        "raw_availability": {
            "aggregate_J_flux_abs_count_and_hash_present": aggregate_fields_present,
            "source_core_c_values_available": source_values_available,
            "internal_face_values_available": face_values_available,
            "boundary_flux_values_available": boundary_values_available,
            "hashes_are_not_numerical_face_values": True,
            "required_missing_quantities": [
                "source-conditioned core c values",
                "internal face c_i and c_p",
                "internal face rho_i and rho_p",
                "exact per-face cbar, dc, chi, upwind and free-capacity terms",
                "executed numerical internal +x face-flux values",
                "prospectively persisted numerical boundary face flux",
            ],
        },
        "world_rows": world_rows,
        "decomposition_values_computed": False,
        "mechanistic_diagnosis": "RAW_INSUFFICIENT",
        "roadmap_recommendation": "UNRESOLVED_RAW_INSUFFICIENT",
        "prospective_classification_preserved": True,
        "engine_or_runner_imported": False,
        "worlds_initialized_or_reconstructed": 0,
        "claim_boundary": (
            "The persisted aggregates and hashes cannot identify buffering, cancellation, saturation regime, "
            "gradient/upwind gating, or boundary partition. NO_ACCESS_ESTABLISHED remains unchanged and is not "
            "absence or equivalence."
        ),
    }


def atomic_write_json(path: Path, payload: Mapping) -> str:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return sha256_bytes(encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    plan_path = args.plan if args.plan.is_absolute() else repo_root / args.plan
    report = audit(repo_root, plan_path)
    output_path = args.output if args.output.is_absolute() else repo_root / args.output
    digest = atomic_write_json(output_path, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "mechanistic_diagnosis": report["mechanistic_diagnosis"],
                "roadmap_recommendation": report["roadmap_recommendation"],
                "output_sha256": digest,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
