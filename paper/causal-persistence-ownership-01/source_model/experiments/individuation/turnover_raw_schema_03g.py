"""Versioned raw schema, atomic persistence, manifest generation, and validation for turnover 03G."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable

RAW_SCHEMA = "LCI-TURNOVER-RAW-03G-v1"
RAW_MANIFEST_SCHEMA = "LCI-TURNOVER-RAW-MANIFEST-03G-v1"
FEASIBILITY_FIELDS = (
    "seed",
    "eligible",
    "deep_reached",
    "rest_assay_valid",
    "deep_assay_valid",
    "valid",
    "reason",
)
SCIENTIFIC_REQUIRED = (
    "histories",
    "target_ids",
    "g0",
    "target_centroids",
    "material_tracer",
    "tracking_event_evidence",
    "scopes",
    "causal_intervention_battery",
    "lambda_plus_only_control",
    "censoring_reason",
    "snapshot_time",
)


class RawSchemaError(ValueError):
    pass


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: os.PathLike[str] | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_bytes(path: os.PathLike[str] | str, data: bytes, *, overwrite: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite {path}")
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        with open(tmp, "xb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        if path.exists() and not overwrite:
            raise FileExistsError(f"refusing to overwrite {path}")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_json(path: os.PathLike[str] | str, value, *, overwrite: bool = False) -> None:
    atomic_write_bytes(path, canonical_bytes(value) + b"\n", overwrite=overwrite)


def feasibility_projection(record: dict) -> dict:
    f = record["feasibility"]
    return {
        "seed": int(record["seed"]),
        "eligible": bool(f["eligible"]),
        "deep_reached": bool(f["deep_reached"]),
        "rest_assay_valid": bool(f["rest_assay_valid"]),
        "deep_assay_valid": bool(f["deep_assay_valid"]),
        "valid": bool(f["valid"]),
        "reason": f.get("reason"),
    }


def validate_feasibility_projection(projection: dict) -> None:
    if set(projection) != set(FEASIBILITY_FIELDS):
        raise RawSchemaError(
            f"reserve projection must contain feasibility fields only: {sorted(projection)}"
        )
    if not isinstance(projection["seed"], int):
        raise RawSchemaError("feasibility seed must be an integer")
    for field in ("eligible", "deep_reached", "rest_assay_valid", "deep_assay_valid", "valid"):
        if not isinstance(projection[field], bool):
            raise RawSchemaError(f"feasibility field {field} must be Boolean")
    if projection["reason"] is not None and not isinstance(projection["reason"], str):
        raise RawSchemaError("feasibility reason must be null or text")


def validate_raw_record(record: dict, *, expected_mode: str | None = None) -> dict:
    required = {
        "schema",
        "mode",
        "watermark",
        "seed",
        "world_id",
        "bindings",
        "feasibility",
        "scientific",
    }
    missing = required - set(record)
    if missing:
        raise RawSchemaError(f"raw record missing fields: {sorted(missing)}")
    if record["schema"] != RAW_SCHEMA:
        raise RawSchemaError(f"unsupported raw schema: {record['schema']}")
    if expected_mode is not None and record["mode"] != expected_mode:
        raise RawSchemaError(f"raw mode mismatch: {record['mode']} != {expected_mode}")
    if record["mode"] != "PROSPECTIVE" and "DEV/EXPLORATORY" not in record["watermark"]:
        raise RawSchemaError("non-prospective raw records require a DEV/EXPLORATORY watermark")
    if int(record["seed"]) != int(record["world_id"]):
        raise RawSchemaError("world_id must equal the original seed/world identifier")
    bindings = record["bindings"]
    for field in (
        "seal_sha256",
        "execution_manifest_sha256",
        "execution_manifest_git_blob",
        "environment_lock_sha256",
        "code_git_blobs",
        "code_sha256",
    ):
        if field not in bindings:
            raise RawSchemaError(f"raw bindings missing {field}")
    projection = {"seed": int(record["seed"]), **record["feasibility"]}
    validate_feasibility_projection(projection)
    scientific = record["scientific"]
    missing_science = set(SCIENTIFIC_REQUIRED) - set(scientific)
    if missing_science:
        raise RawSchemaError(f"scientific payload missing fields: {sorted(missing_science)}")
    if scientific["scopes"] is not None:
        values = scientific["scopes"].get("values", {})
        for scope in ("L", "N", "P", "E", "Gm", "Gf", "B"):
            if scope not in values:
                raise RawSchemaError(f"scope payload missing {scope}")
    canonical_bytes(record)
    return record


def write_raw_record(path: os.PathLike[str] | str, record: dict) -> dict:
    validate_raw_record(record)
    atomic_write_json(path, record, overwrite=False)
    return {
        "seed": int(record["seed"]),
        "world_id": int(record["world_id"]),
        "path": str(Path(path)),
        "sha256": sha256_file(path),
        "schema": record["schema"],
        "valid": bool(record["feasibility"]["valid"]),
    }


def load_raw_record(
    path: os.PathLike[str] | str,
    *,
    expected_sha256: str | None = None,
    expected_mode: str | None = None,
) -> dict:
    path = Path(path)
    if expected_sha256 is not None and sha256_file(path) != expected_sha256:
        raise RawSchemaError(f"raw hash mismatch for {path}")
    return validate_raw_record(json.loads(path.read_text(encoding="utf-8")), expected_mode=expected_mode)


def generate_raw_manifest(entries: Iterable[dict], *, mode: str, seal_sha256: str) -> dict:
    rows = sorted((dict(entry) for entry in entries), key=lambda row: int(row["seed"]))
    seeds = [int(row["seed"]) for row in rows]
    if len(seeds) != len(set(seeds)):
        raise RawSchemaError("raw manifest contains duplicate seeds/worlds")
    schemas = {row["schema"] for row in rows}
    if schemas - {RAW_SCHEMA}:
        raise RawSchemaError(f"mixed or unknown raw schemas: {sorted(schemas)}")
    return {
        "schema": RAW_MANIFEST_SCHEMA,
        "mode": mode,
        "seal_sha256": seal_sha256,
        "raw_schema": RAW_SCHEMA,
        "entries": rows,
        "n_records": len(rows),
        "n_valid_worlds": sum(bool(row["valid"]) for row in rows),
    }


def validate_raw_manifest(manifest: dict, run_dir: os.PathLike[str] | str) -> list[dict]:
    if manifest.get("schema") != RAW_MANIFEST_SCHEMA or manifest.get("raw_schema") != RAW_SCHEMA:
        raise RawSchemaError("wrong raw manifest/schema version")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or manifest.get("n_records") != len(entries):
        raise RawSchemaError("raw manifest count mismatch")
    seeds = [int(row["seed"]) for row in entries]
    if len(seeds) != len(set(seeds)):
        raise RawSchemaError("duplicate world in raw manifest")
    loaded = []
    root = Path(run_dir).resolve()
    for row in entries:
        if row.get("schema") != RAW_SCHEMA:
            raise RawSchemaError(
                f"raw manifest entry has mixed/unknown schema for seed {row.get('seed')}"
            )
        path = Path(row["path"])
        if not path.is_absolute():
            path = Path(run_dir) / path
        path = path.resolve()
        if root not in path.parents:
            raise RawSchemaError(f"raw path escapes canonical run directory: {path}")
        record = load_raw_record(
            path,
            expected_sha256=row["sha256"],
            expected_mode=manifest["mode"],
        )
        if int(record["seed"]) != int(row["seed"]) or bool(record["feasibility"]["valid"]) != bool(row["valid"]):
            raise RawSchemaError(f"raw manifest metadata mismatch for seed {row['seed']}")
        loaded.append(record)
    if manifest.get("n_valid_worlds") != sum(r["feasibility"]["valid"] for r in loaded):
        raise RawSchemaError("raw manifest valid-world count mismatch")
    return loaded
