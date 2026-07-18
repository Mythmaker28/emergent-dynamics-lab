"""Standard-library-only raw reproducer for DIRECTED-CAUSAL-PAIR-00 Phase 0.5.

The reproducer reads explicitly named mechanical world shards, validates their
strict structure and hash chain, reconstructs canonical packed/RLE masks, and
recomputes geometry, association terms, and mechanical gates.  It deliberately
does not import an engine, tracker implementation, reader, decoder, statistics
package, or scientific analyzer.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import dataclass
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence


MISSION = "DIRECTED-CAUSAL-PAIR-00"
MODE = "DEV_ONLY_MECHANICAL"
RAW_SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-MECHANICAL-SHARD-v1"
REPRODUCTION_SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-RAW-REPRODUCTION-v1"
FINAL_SCHEMA_ID = "DIRECTED-CAUSAL-PAIR-00-PHASE05-FINAL-RAW-SCHEMA-v1"
PHASE0_COMMIT = "4bcb551092291b7383c4168f653818d4bade14f6"
WORLD_ORDER = (50002, 50004, 50005, 50007)
WORLD_ASSIGNMENTS = {
    50002: (0, 2, 1),
    50004: (0, 1, 2),
    50005: (1, 0, 2),
    50007: (1, 0, 2),
}
EXPECTED_PLAN_SHA256 = "0c3c75fe8142373dcf6d1aa765dd4247c11570b993e4ea5d1cf4379f958826c3"
EXPECTED_INPUT_PATHS = frozenset(
    {
        "AGENTS.md",
        "docs/DECISION_LOG.md",
        "docs/PROJECT_STATE.md",
        "docs/RESEARCH_CHARTER.md",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md",
    }
)
EXPECTED_CODE_PATHS = frozenset(
    {
        ".gitattributes",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json",
        "edlab/__init__.py",
        "edlab/entities/__init__.py",
        "edlab/entities/detection.py",
        "edlab/entities/tracking.py",
        "edlab/experiments/__init__.py",
        "edlab/experiments/analyze_streaming.py",
        "edlab/experiments/baseline.py",
        "edlab/experiments/exp_sc_00.py",
        "edlab/experiments/sc_hmc/__init__.py",
        "edlab/experiments/sc_hmc/config.py",
        "edlab/experiments/sc_iom/__init__.py",
        "edlab/experiments/sc_iom/config.py",
        "edlab/experiments/sc_iom/engine.py",
        "edlab/experiments/sc_mcm/__init__.py",
        "edlab/experiments/sc_mcm/config.py",
        "edlab/experiments/sc_mcm/engine.py",
        "edlab/experiments/streaming.py",
        "edlab/observables/__init__.py",
        "edlab/observables/continuity.py",
        "edlab/observables/phenotype.py",
        "edlab/specs.py",
        "edlab/state.py",
        "edlab/substrates/__init__.py",
        "edlab/substrates/chemotaxis/__init__.py",
        "edlab/substrates/chemotaxis/diagnostics.py",
        "edlab/substrates/chemotaxis/engine.py",
        "edlab/substrates/particle_dynamics/__init__.py",
        "edlab/substrates/particle_dynamics/engine.py",
        "edlab/substrates/reaction_diffusion/__init__.py",
        "edlab/substrates/reaction_diffusion/engine.py",
        "edlab/substrates/scaffold/__init__.py",
        "edlab/substrates/scaffold/engine.py",
        "edlab/substrates/scaffold/observables.py",
        "edlab/validation/__init__.py",
        "edlab/validation/forces.py",
        "edlab/validation/nulls.py",
        "experiments/individuation/access_structure_noswap_operators.py",
        "experiments/individuation/access_structure_operators.py",
        "experiments/individuation/bijective_tracker.py",
        "experiments/individuation/causal_confirm.py",
        "experiments/individuation/directed_causal_pair_phase05_executor.py",
        "experiments/individuation/directed_causal_pair_phase05_mechanics.py",
        "experiments/individuation/directed_causal_pair_phase05_reproduce.py",
        "experiments/individuation/directed_causal_pair_phase05_runner.py",
        "experiments/individuation/material_tracer.py",
        "experiments/individuation/test_directed_causal_pair_phase05_mechanics.py",
        "experiments/individuation/test_directed_causal_pair_phase05_reproduce.py",
        "experiments/individuation/turnover_diag_engine.py",
        "requirements-lock.txt",
    }
)
ARM_ORDER = ("H00", "H10", "H01", "H11")
ARM_BITS = {
    "H00": (0, 0),
    "H10": (1, 0),
    "H01": (0, 1),
    "H11": (1, 1),
}
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
ACCESS_RECIPIENT = {
    "ORDINARY": None,
    "OWN_REPLAY_SHAM_A": "A",
    "OWN_REPLAY_SHAM_B": "B",
    "REFERENCE_NOSWAP_A": "A",
    "REFERENCE_NOSWAP_B": "B",
    "UP_REF_ZERO": None,
    "REFERENCE_NOSWAP_A_UP_REF_ZERO": "A",
    "REFERENCE_NOSWAP_B_UP_REF_ZERO": "B",
}
GRID_SHAPE = (64, 64)
GRID_CELLS = 64 * 64
PACKED_BYTES = GRID_CELLS // 8
CORE_RADIUS = 10.0
HALO_RADIUS = 12.0
MIN_SEPARATION = 24.0
MIN_COMPONENT_SIZE = 45
COVERAGE_CAP = 0.15
TRACK_THETA = 0.10
TRACK_SPLIT_FRAC = 0.30
FLOAT_ABS_TOL = 1e-12
FLOAT_REL_TOL = 1e-12
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_BLOB_RE = re.compile(r"^[0-9a-f]{40}$")
TOKEN_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


class RawContractError(ValueError):
    """Raised when persisted raw is not independently reproducible."""


# Exact and prefix checks are defense in depth.  The strict object key sets
# below are the primary firewall.  Physical state is represented only by an
# opaque state hash, so no physical ``C`` or uptake array is admitted here.
FORBIDDEN_EXACT_KEYS = frozenset(
    {
        "y",
        "y_a",
        "y_b",
        "c_aa",
        "c_ab",
        "c_ba",
        "c_bb",
        "i_a",
        "i_b",
        "delta_ind",
        "pair_total",
        "asymmetry",
        "integrated_tracked_uptake",
        "integrated_fixed_mask_uptake",
    }
)
FORBIDDEN_KEY_PREFIXES = (
    "outcome",
    "feeding",
    "uptake",
    "contrast",
    "effect",
    "estimand",
    "directed_matrix",
    "analyzer",
    "analysis",
    "decoder",
    "reader",
    "scientific_",
)


def _walk_keys(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            text = str(key)
            yield path, text
            yield from _walk_keys(child, path + (text,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, path + (str(index),))


def assert_outcome_free(value: Any) -> None:
    bad: list[str] = []
    for path, key in _walk_keys(value):
        folded = key.casefold()
        if folded in FORBIDDEN_EXACT_KEYS or any(folded.startswith(prefix) for prefix in FORBIDDEN_KEY_PREFIXES):
            bad.append("/".join(path + (key,)))
    if bad:
        raise RawContractError(f"OUTCOME_FIREWALL_FORBIDDEN_KEYS:{','.join(bad)}")


def canonical_json_bytes(value: Any) -> bytes:
    assert_outcome_free(value)
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise RawContractError(f"NONCANONICAL_JSON_VALUE:{exc}") from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_constant(token: str) -> None:
    raise RawContractError(f"NONFINITE_JSON_NUMBER:{token}")


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RawContractError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def strict_json_loads(payload: bytes) -> Any:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            parse_constant=_reject_constant,
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except UnicodeDecodeError as exc:
        raise RawContractError("RAW_NOT_UTF8") from exc
    except json.JSONDecodeError as exc:
        raise RawContractError(f"RAW_NOT_JSON:{exc.msg}") from exc
    assert_outcome_free(value)
    return value


def read_raw_shard(path: Path) -> tuple[dict[str, Any], bytes]:
    """Read one explicitly named shard; never enumerate or infer siblings."""
    if path.is_symlink():
        raise RawContractError("SYMLINK_RAW_SHARD_REFUSED")
    stored = path.read_bytes()
    if path.name.endswith(".json.gz"):
        try:
            payload = gzip.decompress(stored)
        except (gzip.BadGzipFile, EOFError, OSError) as exc:
            raise RawContractError("INVALID_GZIP_SHARD") from exc
    elif path.name.endswith(".json"):
        payload = stored
    else:
        raise RawContractError("RAW_SHARD_SUFFIX_MUST_BE_JSON_OR_JSON_GZ")
    value = strict_json_loads(payload)
    if not isinstance(value, dict):
        raise RawContractError("RAW_SHARD_ROOT_NOT_OBJECT")
    canonical = canonical_json_bytes(value)
    if payload != canonical:
        raise RawContractError("RAW_SHARD_NOT_CANONICAL_JSON")
    return value, canonical


def _expect_object(value: Any, keys: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RawContractError(f"{context}:EXPECTED_OBJECT")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise RawContractError(f"{context}:KEYS:missing={missing}:extra={extra}")
    return value


def _expect_list(value: Any, context: str, *, length: int | None = None) -> list[Any]:
    if not isinstance(value, list):
        raise RawContractError(f"{context}:EXPECTED_ARRAY")
    if length is not None and len(value) != length:
        raise RawContractError(f"{context}:LENGTH:{len(value)}!=${length}".replace("$", ""))
    return value


def _expect_bool(value: Any, context: str) -> bool:
    if type(value) is not bool:
        raise RawContractError(f"{context}:EXPECTED_BOOLEAN")
    return value


def _expect_int(value: Any, context: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise RawContractError(f"{context}:EXPECTED_INTEGER")
    if minimum is not None and value < minimum:
        raise RawContractError(f"{context}:INTEGER_BELOW_MINIMUM")
    return value


def _expect_finite(value: Any, context: str) -> float:
    if type(value) not in (int, float):
        raise RawContractError(f"{context}:EXPECTED_NUMBER")
    result = float(value)
    if not math.isfinite(result):
        raise RawContractError(f"{context}:NONFINITE")
    return result


def _expect_sha256(value: Any, context: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise RawContractError(f"{context}:EXPECTED_SHA256")
    return value


def _expect_git_blob(value: Any, context: str) -> str:
    if not isinstance(value, str) or GIT_BLOB_RE.fullmatch(value) is None:
        raise RawContractError(f"{context}:EXPECTED_LOWERCASE_GIT_BLOB_OID")
    return value


def _expect_token(value: Any, context: str) -> str:
    if not isinstance(value, str) or TOKEN_RE.fullmatch(value) is None:
        raise RawContractError(f"{context}:EXPECTED_UPPERCASE_TOKEN")
    return value


def _close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=FLOAT_REL_TOL, abs_tol=FLOAT_ABS_TOL)


@dataclass(frozen=True)
class DecodedMask:
    shape: tuple[int, int]
    cells: frozenset[int]
    packed: bytes

    @property
    def count(self) -> int:
        return len(self.cells)


def _pack_cells(cells: Iterable[int], shape: tuple[int, int]) -> bytes:
    total = shape[0] * shape[1]
    payload = bytearray((total + 7) // 8)
    for flat in cells:
        if type(flat) is not int or flat < 0 or flat >= total:
            raise RawContractError("MASK_CELL_OUT_OF_RANGE")
        payload[flat // 8] |= 1 << (flat % 8)
    return bytes(payload)


def decode_mask(value: Any, context: str = "mask") -> DecodedMask:
    if not isinstance(value, dict):
        raise RawContractError(f"{context}:EXPECTED_OBJECT")
    encoding = value.get("encoding")
    if encoding == "PACKED_BITS_BASE64_V1":
        obj = _expect_object(
            value,
            {"encoding", "shape", "bitorder", "data_base64", "sha256"},
            context,
        )
        if obj["bitorder"] != "little":
            raise RawContractError(f"{context}:BITORDER_MUST_BE_LITTLE")
        try:
            packed = base64.b64decode(obj["data_base64"], validate=True)
        except (binascii.Error, ValueError, TypeError) as exc:
            raise RawContractError(f"{context}:INVALID_BASE64") from exc
        shape = _mask_shape(obj["shape"], context)
        expected_bytes = (shape[0] * shape[1] + 7) // 8
        if len(packed) != expected_bytes:
            raise RawContractError(f"{context}:PACKED_LENGTH")
        cells = frozenset(
            flat
            for flat in range(shape[0] * shape[1])
            if packed[flat // 8] & (1 << (flat % 8))
        )
        # Require unused high bits to be zero for non-byte-aligned future grids.
        if _pack_cells(cells, shape) != packed:
            raise RawContractError(f"{context}:NONCANONICAL_PACKED_BITS")
    elif encoding == "RLE_ONES_V1":
        obj = _expect_object(value, {"encoding", "shape", "runs", "sha256"}, context)
        shape = _mask_shape(obj["shape"], context)
        total = shape[0] * shape[1]
        runs = _expect_list(obj["runs"], f"{context}.runs")
        cells_mutable: set[int] = set()
        previous_end = 0
        for index, run_value in enumerate(runs):
            run = _expect_list(run_value, f"{context}.runs[{index}]", length=2)
            start = _expect_int(run[0], f"{context}.runs[{index}].start", minimum=0)
            length = _expect_int(run[1], f"{context}.runs[{index}].length", minimum=1)
            if start < previous_end or start + length > total:
                raise RawContractError(f"{context}:NONCANONICAL_OR_OUT_OF_RANGE_RLE")
            cells_mutable.update(range(start, start + length))
            previous_end = start + length
        cells = frozenset(cells_mutable)
        packed = _pack_cells(cells, shape)
    else:
        raise RawContractError(f"{context}:UNKNOWN_MASK_ENCODING")
    digest = _expect_sha256(obj["sha256"], f"{context}.sha256")
    if sha256_bytes(packed) != digest:
        raise RawContractError(f"{context}:MASK_SHA256_MISMATCH")
    return DecodedMask(shape=shape, cells=cells, packed=packed)


def _mask_shape(value: Any, context: str) -> tuple[int, int]:
    row = _expect_list(value, f"{context}.shape", length=2)
    shape = (
        _expect_int(row[0], f"{context}.shape[0]", minimum=1),
        _expect_int(row[1], f"{context}.shape[1]", minimum=1),
    )
    if shape != GRID_SHAPE:
        raise RawContractError(f"{context}:SHAPE_MUST_BE_64_BY_64")
    return shape


def periodic_centroid(mask: DecodedMask) -> tuple[float, float]:
    if not mask.cells:
        raise RawContractError("EMPTY_MASK_HAS_NO_CENTROID")
    coordinates = (
        [flat // mask.shape[1] for flat in mask.cells],
        [flat % mask.shape[1] for flat in mask.cells],
    )
    result: list[float] = []
    for size, values in zip(mask.shape, coordinates):
        real = sum(math.cos(2.0 * math.pi * value / size) for value in values) / len(values)
        imag = sum(math.sin(2.0 * math.pi * value / size) for value in values) / len(values)
        if math.hypot(real, imag) <= 1e-12:
            raise RawContractError("PERIODIC_CENTROID_UNDEFINED")
        angle = math.atan2(imag, real) % (2.0 * math.pi)
        result.append(angle * size / (2.0 * math.pi))
    return (result[0], result[1])


def toroidal_distance(left: Sequence[float], right: Sequence[float], shape: tuple[int, int] = GRID_SHAPE) -> float:
    deltas: list[float] = []
    for first, second, size in zip(left, right, shape):
        raw = abs(float(first) - float(second))
        deltas.append(min(raw, float(size) - raw))
    return math.hypot(*deltas)


def disk_cells(center: Sequence[float], radius: float, shape: tuple[int, int] = GRID_SHAPE) -> frozenset[int]:
    # Frozen operator convention: NumPy rint (IEEE ties-to-even), then modulo.
    # Python's round on finite binary64 uses the same ties-to-even rule.
    integer_center = (
        int(round(float(center[0]))) % shape[0],
        int(round(float(center[1]))) % shape[1],
    )
    result: set[int] = set()
    for row in range(shape[0]):
        dr = abs(row - integer_center[0])
        dr = min(dr, float(shape[0]) - dr)
        for column in range(shape[1]):
            dc = abs(column - integer_center[1])
            dc = min(dc, float(shape[1]) - dc)
            if math.hypot(dr, dc) <= radius:
                result.add(row * shape[1] + column)
    return frozenset(result)


def masks_contact_four_neighbour(left: DecodedMask, right: DecodedMask) -> bool:
    if left.shape != right.shape:
        raise RawContractError("CONTACT_MASK_SHAPE_MISMATCH")
    if left.cells & right.cells:
        return True
    rows, columns = left.shape
    for flat in left.cells:
        row, column = divmod(flat, columns)
        neighbours = (
            ((row - 1) % rows) * columns + column,
            ((row + 1) % rows) * columns + column,
            row * columns + (column - 1) % columns,
            row * columns + (column + 1) % columns,
        )
        if any(neighbour in right.cells for neighbour in neighbours):
            return True
    return False


def _decode_named_masks(value: Any, context: str) -> dict[str, DecodedMask]:
    names = {"A", "B", "SENTINEL", "core_A", "core_B", "halo_A", "halo_B", "collar"}
    obj = _expect_object(value, names, context)
    decoded = {name: decode_mask(obj[name], f"{context}.{name}") for name in sorted(names)}
    if any(mask.shape != GRID_SHAPE for mask in decoded.values()):
        raise RawContractError(f"{context}:SHAPE_MISMATCH")
    return decoded


def _read_centroid(value: Any, context: str) -> tuple[float, float]:
    row = _expect_list(value, context, length=2)
    centroid = (
        _expect_finite(row[0], f"{context}[0]"),
        _expect_finite(row[1], f"{context}[1]"),
    )
    if any(coordinate < 0.0 or coordinate >= float(size) for coordinate, size in zip(centroid, GRID_SHAPE)):
        raise RawContractError(f"{context}:CENTROID_OUT_OF_CANONICAL_RANGE")
    return centroid


def _validate_centroid(value: Any, expected: tuple[float, float], context: str) -> None:
    actual = _read_centroid(value, context)
    if not (_close(actual[0], expected[0]) and _close(actual[1], expected[1])):
        raise RawContractError(f"{context}:CENTROID_MISMATCH")


def _validate_assignment(value: Any, world_id: int, context: str) -> tuple[int, int, int]:
    obj = _expect_object(
        value,
        {"A_target_index", "B_target_index", "sentinel_target_index", "pair_order"},
        context,
    )
    assignment = (
        _expect_int(obj["A_target_index"], f"{context}.A_target_index", minimum=0),
        _expect_int(obj["B_target_index"], f"{context}.B_target_index", minimum=0),
        _expect_int(obj["sentinel_target_index"], f"{context}.sentinel_target_index", minimum=0),
    )
    if assignment != WORLD_ASSIGNMENTS[world_id]:
        raise RawContractError(f"{context}:FIXED_ASSIGNMENT_MISMATCH")
    if obj["pair_order"] != ["A", "B"]:
        raise RawContractError(f"{context}:PAIR_ORDER_MISMATCH")
    return assignment


def _validate_root_assignment(value: Any, world_id: int, context: str) -> tuple[int, int, int]:
    obj = _expect_object(value, {"target_A", "target_B", "sentinel"}, context)
    assignment = (
        _expect_int(obj["target_A"], f"{context}.target_A", minimum=0),
        _expect_int(obj["target_B"], f"{context}.target_B", minimum=0),
        _expect_int(obj["sentinel"], f"{context}.sentinel", minimum=0),
    )
    if assignment != WORLD_ASSIGNMENTS[world_id]:
        raise RawContractError(f"{context}:FIXED_ASSIGNMENT_MISMATCH")
    return assignment


def _validate_contract_bindings(value: Any, context: str) -> None:
    rows = _expect_list(value, context)
    if not rows:
        raise RawContractError(f"{context}:EMPTY")
    identities: set[tuple[str, str]] = set()
    for index, row_value in enumerate(rows):
        row = _expect_object(row_value, {"kind", "path", "sha256", "git_blob"}, f"{context}[{index}]")
        if row["kind"] not in ("INPUT", "CODE"):
            raise RawContractError(f"{context}[{index}].kind:INVALID")
        path = row["path"]
        if not isinstance(path, str) or not path or "\\" in path or path.startswith("/") or ".." in path.split("/"):
            raise RawContractError(f"{context}[{index}].path:NOT_CANONICAL_REPOSITORY_RELATIVE")
        _expect_sha256(row["sha256"], f"{context}[{index}].sha256")
        _expect_git_blob(row["git_blob"], f"{context}[{index}].git_blob")
        identity = (row["kind"], path)
        if identity in identities:
            raise RawContractError(f"{context}[{index}]:DUPLICATE")
        identities.add(identity)
    kind_order = {"INPUT": 0, "CODE": 1}
    sorted_identities = sorted(identities, key=lambda item: (kind_order[item[0]], item[1]))
    if [(row["kind"], row["path"]) for row in rows] != sorted_identities:
        raise RawContractError(f"{context}:NOT_SORTED")
    expected_identities = {
        *(("INPUT", path) for path in EXPECTED_INPUT_PATHS),
        *(("CODE", path) for path in EXPECTED_CODE_PATHS),
    }
    if identities != expected_identities:
        missing = sorted(expected_identities - identities)
        extra = sorted(identities - expected_identities)
        raise RawContractError(f"{context}:FROZEN_SET_MISMATCH:missing={missing}:extra={extra}")


def _validate_failure(value: Any, context: str) -> dict[str, Any] | None:
    if value is None:
        return None
    obj = _expect_object(
        value,
        {"stage", "stage_step", "engine_step", "reasons"},
        context,
    )
    _expect_token(obj["stage"], f"{context}.stage")
    _expect_int(obj["stage_step"], f"{context}.stage_step", minimum=0)
    _expect_int(obj["engine_step"], f"{context}.engine_step", minimum=0)
    reasons = _expect_list(obj["reasons"], f"{context}.reasons")
    if not reasons or reasons != sorted(set(reasons)):
        raise RawContractError(f"{context}.reasons:MUST_BE_NONEMPTY_SORTED_UNIQUE")
    for index, reason in enumerate(reasons):
        _expect_token(reason, f"{context}.reasons[{index}]")
    return obj


def _first_trace_failure(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    for record in records:
        if record["kill_reasons"]:
            return {
                "stage": record["stage"],
                "stage_step": record["stage_step"],
                "engine_step": record["engine_step"],
                "reasons": list(record["kill_reasons"]),
            }
    return None


def _synthetic_failure(record: dict[str, Any], *, stage: str, stage_step: int, reason: str) -> dict[str, Any]:
    return {
        "stage": stage,
        "stage_step": stage_step,
        "engine_step": record["engine_step"],
        "reasons": [reason],
    }


@dataclass
class StepSummary:
    gate_pass: bool
    distance: float | None
    halo_gap: float | None
    core_overlap: int
    halo_overlap: int
    body_overlap: int
    body_contact: bool
    largest_coverage: float
    kill_reason_count: int
    tracker_event_count: int
    collar_intrusion_cells: int
    association_edges_checked: int
    current_track_masks: dict[int, DecodedMask]
    current_track_centroids: dict[int, tuple[float, float] | None]
    collar_mask: DecodedMask | None


def validate_step_record(
    value: Any,
    *,
    world_id: int,
    context: str,
    prior_track_masks: Mapping[int, DecodedMask] | None = None,
    prior_track_centroids: Mapping[int, tuple[float, float] | None] | None = None,
    fixed_collar_mask: DecodedMask | None = None,
) -> StepSummary:
    keys = {
        "stage",
        "stage_step",
        "engine_step",
        "state_sha256",
        "assignment",
        "components",
        "association_edges",
        "tracks",
        "events",
        "pair_geometry",
        "component_switch",
        "largest_component_coverage",
        "collar",
        "sentinel_valid",
        "state_finite",
        "logger_state_unchanged",
        "kill_reasons",
        "masks",
        "material_retention",
        "deep_material_gate",
    }
    obj = _expect_object(value, keys, context)
    _expect_token(obj["stage"], f"{context}.stage")
    _expect_int(obj["stage_step"], f"{context}.stage_step", minimum=0)
    _expect_int(obj["engine_step"], f"{context}.engine_step", minimum=0)
    _expect_sha256(obj["state_sha256"], f"{context}.state_sha256")
    assignment = _validate_assignment(obj["assignment"], world_id, f"{context}.assignment")
    named_masks = _decode_named_masks(obj["masks"], f"{context}.masks")

    material_retention: tuple[float | None, float | None, float | None] | None
    if obj["material_retention"] is None:
        material_retention = None
    else:
        retention_values = _expect_list(obj["material_retention"], f"{context}.material_retention", length=3)
        material_retention = tuple(
            None if item is None else _expect_finite(item, f"{context}.material_retention[{index}]")
            for index, item in enumerate(retention_values)
        )
        if any(item is not None and (item < 0.0 or item > 1.0) for item in material_retention):
            raise RawContractError(f"{context}.material_retention:OUTSIDE_UNIT_INTERVAL")
    deep_material_gate = obj["deep_material_gate"]
    if obj["stage"] == "TURNOVER":
        if material_retention is None or type(deep_material_gate) is not bool:
            raise RawContractError(f"{context}:TURNOVER_REQUIRES_MATERIAL_GATE_PRIMITIVES")
    elif material_retention is not None or deep_material_gate is not None:
        raise RawContractError(f"{context}:MATERIAL_GATE_ONLY_ALLOWED_ON_TURNOVER")

    component_values = _expect_list(obj["components"], f"{context}.components")
    component_masks: dict[int, DecodedMask] = {}
    component_centroids: dict[int, tuple[float, float]] = {}
    component_sizes: dict[int, int] = {}
    for index, component_value in enumerate(component_values):
        component = _expect_object(
            component_value,
            {"component_id", "size", "centroid", "mask"},
            f"{context}.components[{index}]",
        )
        component_id = _expect_int(component["component_id"], f"{context}.components[{index}].component_id", minimum=0)
        if component_id != index:
            raise RawContractError(f"{context}.components:NONCANONICAL_COMPONENT_ORDER")
        mask = decode_mask(component["mask"], f"{context}.components[{index}].mask")
        size = _expect_int(component["size"], f"{context}.components[{index}].size", minimum=1)
        if size != mask.count:
            raise RawContractError(f"{context}.components[{index}]:SIZE_MISMATCH")
        # The detector's physical centroid is rho-weighted.  Rho is deliberately
        # absent from mechanical raw, so the persisted finite centroid is the
        # primitive; masks independently verify size, overlap, contact, and the
        # integer-centred core/halo construction.
        centroid = _read_centroid(component["centroid"], f"{context}.components[{index}].centroid")
        component_masks[component_id] = mask
        component_centroids[component_id] = centroid
        component_sizes[component_id] = size

    track_values = _expect_list(obj["tracks"], f"{context}.tracks", length=3)
    current_track_masks: dict[int, DecodedMask] = {}
    current_track_centroids: dict[int, tuple[float, float] | None] = {}
    track_component_ids: dict[int, int | None] = {}
    track_statuses: dict[int, str] = {}
    label_masks = {
        assignment[0]: named_masks["A"],
        assignment[1]: named_masks["B"],
        assignment[2]: named_masks["SENTINEL"],
    }
    for index, track_value in enumerate(track_values):
        track = _expect_object(
            track_value,
            {
                "tracker_id",
                "status",
                "component_id",
                "component_size",
                "centroid",
                "body_core_coverage",
                "body_mask",
                "core_mask",
                "halo_mask",
            },
            f"{context}.tracks[{index}]",
        )
        tracker_id = _expect_int(track["tracker_id"], f"{context}.tracks[{index}].tracker_id", minimum=0)
        if tracker_id != index:
            raise RawContractError(f"{context}.tracks:NONCANONICAL_TRACK_ORDER")
        status = _expect_token(track["status"], f"{context}.tracks[{index}].status")
        component_id = track["component_id"]
        if component_id is not None:
            component_id = _expect_int(component_id, f"{context}.tracks[{index}].component_id", minimum=0)
            if component_id not in component_masks:
                raise RawContractError(f"{context}.tracks[{index}]:UNKNOWN_COMPONENT")
        component_size = _expect_int(track["component_size"], f"{context}.tracks[{index}].component_size", minimum=0)
        track_statuses[tracker_id] = status
        track_component_ids[tracker_id] = component_id
        role_mask = label_masks[tracker_id]
        track_body_mask = decode_mask(track["body_mask"], f"{context}.tracks[{index}].body_mask")
        track_core_mask = decode_mask(track["core_mask"], f"{context}.tracks[{index}].core_mask")
        track_halo_mask = decode_mask(track["halo_mask"], f"{context}.tracks[{index}].halo_mask")
        if track_body_mask.packed != role_mask.packed:
            raise RawContractError(f"{context}.tracks[{index}]:BODY_MASK_ROLE_MISMATCH")
        current_track_masks[tracker_id] = role_mask
        if status == "ALIVE":
            if component_id is None or component_masks[component_id].packed != role_mask.packed:
                raise RawContractError(f"{context}.tracks[{index}]:SELECTED_MASK_MISMATCH")
            if component_size != role_mask.count:
                raise RawContractError(f"{context}.tracks[{index}]:COMPONENT_SIZE_MISMATCH")
            centroid = _read_centroid(track["centroid"], f"{context}.tracks[{index}].centroid")
            expected_component_centroid = component_centroids[component_id]
            if not (
                _close(centroid[0], expected_component_centroid[0])
                and _close(centroid[1], expected_component_centroid[1])
            ):
                raise RawContractError(f"{context}.tracks[{index}]:COMPONENT_CENTROID_MISMATCH")
            current_track_centroids[tracker_id] = centroid
            core = disk_cells(centroid, CORE_RADIUS)
            halo = disk_cells(centroid, HALO_RADIUS)
            if track_core_mask.cells != core or track_halo_mask.cells != halo:
                raise RawContractError(f"{context}.tracks[{index}]:CORE_OR_HALO_MASK_MISMATCH")
            expected_coverage = len(role_mask.cells & core) / max(1, role_mask.count)
            coverage = _expect_finite(track["body_core_coverage"], f"{context}.tracks[{index}].body_core_coverage")
            if not _close(coverage, expected_coverage):
                raise RawContractError(f"{context}.tracks[{index}]:BODY_CORE_COVERAGE_MISMATCH")
        else:
            if component_id is not None or track["centroid"] is not None or component_size != 0:
                raise RawContractError(f"{context}.tracks[{index}]:NONALIVE_TRACK_PAYLOAD")
            if track_body_mask.count or track_core_mask.count or track_halo_mask.count:
                raise RawContractError(f"{context}.tracks[{index}]:NONALIVE_MASK_NOT_EMPTY")
            if not _close(
                _expect_finite(track["body_core_coverage"], f"{context}.tracks[{index}].body_core_coverage"),
                0.0,
            ):
                raise RawContractError(f"{context}.tracks[{index}].body_core_coverage:NONZERO_FOR_NONALIVE")
            current_track_centroids[tracker_id] = None

    expected_largest = max(component_sizes.values(), default=0) / GRID_CELLS
    largest = _expect_finite(obj["largest_component_coverage"], f"{context}.largest_component_coverage")
    if not _close(largest, expected_largest):
        raise RawContractError(f"{context}:LARGEST_COMPONENT_COVERAGE_MISMATCH")

    a_tracker, b_tracker, sentinel_tracker = assignment
    a_alive = track_statuses[a_tracker] == "ALIVE"
    b_alive = track_statuses[b_tracker] == "ALIVE"
    sentinel_alive = track_statuses[sentinel_tracker] == "ALIVE"
    centroid_a = current_track_centroids[a_tracker] if a_alive else None
    centroid_b = current_track_centroids[b_tracker] if b_alive else None
    core_a = disk_cells(centroid_a, CORE_RADIUS) if centroid_a is not None else set()
    core_b = disk_cells(centroid_b, CORE_RADIUS) if centroid_b is not None else set()
    halo_a = disk_cells(centroid_a, HALO_RADIUS) if centroid_a is not None else set()
    halo_b = disk_cells(centroid_b, HALO_RADIUS) if centroid_b is not None else set()
    derived_masks = {
        "core_A": core_a,
        "core_B": core_b,
        "halo_A": halo_a,
        "halo_B": halo_b,
    }
    for name, expected_cells in derived_masks.items():
        if named_masks[name].cells != expected_cells:
            raise RawContractError(f"{context}.masks.{name}:DERIVED_MASK_MISMATCH")

    distance = toroidal_distance(centroid_a, centroid_b) if centroid_a is not None and centroid_b is not None else None
    core_overlap = len(core_a & core_b)
    halo_overlap = len(halo_a & halo_b)
    body_overlap = len(named_masks["A"].cells & named_masks["B"].cells)
    body_contact = masks_contact_four_neighbour(named_masks["A"], named_masks["B"])
    if distance is None:
        if obj["pair_geometry"] is not None:
            raise RawContractError(f"{context}.pair_geometry:MUST_BE_NULL_WHEN_PAIR_UNAVAILABLE")
    else:
        geometry = _expect_object(
            obj["pair_geometry"],
            {
                "centroid_A",
                "centroid_B",
                "distance",
                "core_overlap_cells",
                "halo_overlap_cells",
                "minimum_core_gap",
                "minimum_halo_gap",
                "body_contact",
                "body_overlap_cells",
            },
            f"{context}.pair_geometry",
        )
        _validate_centroid(geometry["centroid_A"], centroid_a, f"{context}.pair_geometry.centroid_A")
        _validate_centroid(geometry["centroid_B"], centroid_b, f"{context}.pair_geometry.centroid_B")
        numeric_geometry = {
            "distance": distance,
            "minimum_core_gap": distance - 2.0 * CORE_RADIUS,
            "minimum_halo_gap": distance - 2.0 * HALO_RADIUS,
        }
        for name, expected in numeric_geometry.items():
            actual = _expect_finite(geometry[name], f"{context}.pair_geometry.{name}")
            if not _close(actual, expected):
                raise RawContractError(f"{context}.pair_geometry.{name}:MISMATCH")
        integer_geometry = {
            "core_overlap_cells": core_overlap,
            "halo_overlap_cells": halo_overlap,
            "body_overlap_cells": body_overlap,
        }
        for name, expected in integer_geometry.items():
            actual = _expect_int(geometry[name], f"{context}.pair_geometry.{name}", minimum=0)
            if actual != expected:
                raise RawContractError(f"{context}.pair_geometry.{name}:MISMATCH")
        if _expect_bool(geometry["body_contact"], f"{context}.pair_geometry.body_contact") != body_contact:
            raise RawContractError(f"{context}.pair_geometry.body_contact:MISMATCH")

    events = obj["events"]
    if not isinstance(events, dict) or not set(events).issubset({"0", "1", "2"}):
        raise RawContractError(f"{context}.events:INVALID_KEYS")
    for tracker_id, event in events.items():
        _expect_token(event, f"{context}.events.{tracker_id}")

    edge_values = _expect_list(obj["association_edges"], f"{context}.association_edges")
    prior = dict(prior_track_masks or current_track_masks)
    prior_centroids = dict(prior_track_centroids or current_track_centroids)
    if set(prior) != {0, 1, 2}:
        raise RawContractError(f"{context}:PRIOR_TRACK_MASKS_INCOMPLETE")
    if set(prior_centroids) != {0, 1, 2}:
        raise RawContractError(f"{context}:PRIOR_TRACK_CENTROIDS_INCOMPLETE")
    active_prior_trackers = {tracker_id for tracker_id, mask in prior.items() if mask.count > 0}
    expected_edge_count = len(active_prior_trackers) * len(component_masks)
    if len(edge_values) != expected_edge_count:
        raise RawContractError(f"{context}.association_edges:INCOMPLETE_MATRIX")
    seen_edges: set[tuple[int, int]] = set()
    overlaps_by_track: dict[int, dict[int, float]] = {tracker_id: {} for tracker_id in active_prior_trackers}
    for tracker_id in sorted(active_prior_trackers):
        prior_mask = prior[tracker_id]
        prior_centroid = prior_centroids[tracker_id]
        if prior_centroid is None:
            raise RawContractError(f"{context}:ACTIVE_PRIOR_TRACK_MISSING_CENTROID")
        for component_id, component_mask in component_masks.items():
            overlap = len(prior_mask.cells & component_mask.cells) / max(1, prior_mask.count)
            overlaps_by_track[tracker_id][component_id] = overlap
    ranks_by_track = {
        tracker_id: {
            component_id: rank
            for rank, component_id in enumerate(
                sorted(component_masks, key=lambda item: (-overlaps[item], item))
            )
        }
        for tracker_id, overlaps in overlaps_by_track.items()
    }
    for index, edge_value in enumerate(edge_values):
        edge = _expect_object(
            edge_value,
            {
                "tracker_id",
                "component_id",
                "overlap",
                "centroid_distance",
                "size_ratio",
                "theta_gate",
                "split_gate",
                "compatible",
                "assignment_cost",
                "rank",
                "selected",
            },
            f"{context}.association_edges[{index}]",
        )
        tracker_id = _expect_int(edge["tracker_id"], f"{context}.association_edges[{index}].tracker_id", minimum=0)
        component_id = _expect_int(edge["component_id"], f"{context}.association_edges[{index}].component_id", minimum=0)
        identity = (tracker_id, component_id)
        if tracker_id not in active_prior_trackers or component_id not in component_masks or identity in seen_edges:
            raise RawContractError(f"{context}.association_edges[{index}]:INVALID_OR_DUPLICATE_ID")
        seen_edges.add(identity)
        prior_mask = prior[tracker_id]
        overlap = overlaps_by_track[tracker_id][component_id]
        expected_terms = {
            "overlap": overlap,
            "centroid_distance": toroidal_distance(prior_centroids[tracker_id], component_centroids[component_id]),
            "size_ratio": component_sizes[component_id] / max(1, prior_mask.count),
        }
        for name, expected in expected_terms.items():
            actual = _expect_finite(edge[name], f"{context}.association_edges[{index}].{name}")
            if not _close(actual, expected):
                raise RawContractError(f"{context}.association_edges[{index}].{name}:MISMATCH")
        if _expect_bool(edge["theta_gate"], f"{context}.association_edges[{index}].theta_gate") != (overlap >= TRACK_THETA):
            raise RawContractError(f"{context}.association_edges[{index}].theta_gate:MISMATCH")
        if _expect_bool(edge["split_gate"], f"{context}.association_edges[{index}].split_gate") != (overlap >= TRACK_SPLIT_FRAC):
            raise RawContractError(f"{context}.association_edges[{index}].split_gate:MISMATCH")
        if _expect_bool(edge["compatible"], f"{context}.association_edges[{index}].compatible") != (overlap >= TRACK_THETA):
            raise RawContractError(f"{context}.association_edges[{index}].compatible:MISMATCH")
        if not _close(
            _expect_finite(edge["assignment_cost"], f"{context}.association_edges[{index}].assignment_cost"),
            -overlap,
        ):
            raise RawContractError(f"{context}.association_edges[{index}].assignment_cost:MISMATCH")
        if _expect_int(edge["rank"], f"{context}.association_edges[{index}].rank", minimum=0) != ranks_by_track[tracker_id][component_id]:
            raise RawContractError(f"{context}.association_edges[{index}].rank:MISMATCH")
        selected = track_component_ids[tracker_id] == component_id and track_statuses[tracker_id] == "ALIVE"
        if _expect_bool(edge["selected"], f"{context}.association_edges[{index}].selected") != selected:
            raise RawContractError(f"{context}.association_edges[{index}].selected:MISMATCH")

    derived_component_switch = False
    if obj["stage"] not in ("PREWRITER", "PROBE_STANDARDIZE"):
        for tracker_id, component_id in track_component_ids.items():
            if component_id is None or tracker_id not in overlaps_by_track:
                continue
            own_overlap = overlaps_by_track[tracker_id][component_id]
            derived_component_switch |= any(
                other_id != tracker_id
                and component_id in other_overlaps
                and other_overlaps[component_id] > own_overlap
                for other_id, other_overlaps in overlaps_by_track.items()
            )

    collar_intrusion = 0
    collar = obj["collar"]
    if collar is None:
        if named_masks["collar"].count != 0:
            raise RawContractError(f"{context}.masks.collar:MUST_BE_EMPTY_WITHOUT_COLLAR_CONTEXT")
    else:
        collar_obj = _expect_object(
            collar,
            {
                "recipient",
                "recipient_body_intersection_cells",
                "partner_body_intersection_cells",
                "recipient_core_intersection_cells",
                "wrong_core_intersection_cells",
            },
            f"{context}.collar",
        )
        recipient = collar_obj["recipient"]
        if recipient not in ("A", "B"):
            raise RawContractError(f"{context}.collar.recipient:INVALID")
        recipient_tracker = a_tracker if recipient == "A" else b_tracker
        if fixed_collar_mask is not None:
            expected_collar = set(fixed_collar_mask.cells)
        else:
            collar_center = prior_centroids[recipient_tracker]
            if collar_center is None:
                collar_center = current_track_centroids[recipient_tracker]
            if collar_center is None:
                raise RawContractError(f"{context}.masks.collar:NO_RECIPIENT_CENTER_FOR_DERIVATION")
            expected_collar = disk_cells(collar_center, HALO_RADIUS) - disk_cells(collar_center, CORE_RADIUS)
        if named_masks["collar"].cells != expected_collar:
            raise RawContractError(f"{context}.masks.collar:DERIVED_MASK_MISMATCH")
        recipient_mask = named_masks[recipient]
        partner_mask = named_masks["B" if recipient == "A" else "A"]
        sentinel_mask = named_masks["SENTINEL"]
        sentinel_core = (
            disk_cells(current_track_centroids[sentinel_tracker], CORE_RADIUS)
            if sentinel_alive and current_track_centroids[sentinel_tracker] is not None
            else set()
        )
        expected_counts = {
            "recipient_body_intersection_cells": len(expected_collar & recipient_mask.cells),
            "partner_body_intersection_cells": len(expected_collar & partner_mask.cells),
            "recipient_core_intersection_cells": len(expected_collar & (core_a if recipient == "A" else core_b)),
            "wrong_core_intersection_cells": len(expected_collar & (core_b if recipient == "A" else core_a))
            + len(expected_collar & sentinel_core),
        }
        for name, expected in expected_counts.items():
            actual = _expect_int(collar_obj[name], f"{context}.collar.{name}", minimum=0)
            if actual != expected:
                raise RawContractError(f"{context}.collar.{name}:MISMATCH")
        collar_intrusion = sum(expected_counts.values())

    component_switch = _expect_bool(obj["component_switch"], f"{context}.component_switch")
    if component_switch != derived_component_switch:
        raise RawContractError(f"{context}.component_switch:DERIVED_MISMATCH")
    sentinel_valid = _expect_bool(obj["sentinel_valid"], f"{context}.sentinel_valid")
    expected_sentinel_valid = sentinel_alive and current_track_masks[sentinel_tracker].count >= MIN_COMPONENT_SIZE
    if sentinel_valid != expected_sentinel_valid:
        raise RawContractError(f"{context}.sentinel_valid:DERIVED_MISMATCH")
    state_finite = _expect_bool(obj["state_finite"], f"{context}.state_finite")
    logger_unchanged = _expect_bool(obj["logger_state_unchanged"], f"{context}.logger_state_unchanged")
    kill_reasons = _expect_list(obj["kill_reasons"], f"{context}.kill_reasons")
    if kill_reasons != sorted(set(kill_reasons)):
        raise RawContractError(f"{context}.kill_reasons:NOT_SORTED_UNIQUE")
    for index, reason in enumerate(kill_reasons):
        _expect_token(reason, f"{context}.kill_reasons[{index}]")
    expected_reasons: list[str] = []
    if not state_finite:
        expected_reasons.append("NONFINITE_STATE")
    if events:
        expected_reasons.extend(
            f"TRACKER_{status}_T{tracker_id}"
            for tracker_id, status in sorted((int(key), value) for key, value in events.items())
        )
    if any(status != "ALIVE" for status in track_statuses.values()):
        expected_reasons.append("TARGET_OR_SENTINEL_NOT_ALIVE")
    if any(current_track_masks[index].count < MIN_COMPONENT_SIZE for index in range(3)):
        expected_reasons.append("TARGET_OR_SENTINEL_BELOW_MIN_SIZE")
    if largest >= COVERAGE_CAP:
        expected_reasons.append("GIANT_COMPONENT_COVERAGE")
    if distance is None:
        expected_reasons.append("PAIR_GEOMETRY_UNAVAILABLE")
    else:
        if distance < MIN_SEPARATION:
            expected_reasons.append("PAIR_DISTANCE_BELOW_24")
        if halo_overlap > 0:
            expected_reasons.append("RADIUS12_HALO_OVERLAP")
        if body_contact:
            expected_reasons.append("PAIR_BODY_CONTACT")
    if component_switch:
        expected_reasons.append("PAIR_IDENTITY_SWITCH")
    if collar is not None:
        if collar["recipient_core_intersection_cells"] > 0:
            expected_reasons.append("CLAMP_COLLAR_RECIPIENT_CORE_INTERSECTION")
        if collar["recipient_body_intersection_cells"] > 0:
            expected_reasons.append("CLAMP_COLLAR_RECIPIENT_BODY_INTERSECTION")
        if collar["partner_body_intersection_cells"] > 0:
            expected_reasons.append("CLAMP_COLLAR_PARTNER_INTRUSION")
        if collar["wrong_core_intersection_cells"] > 0:
            expected_reasons.append("CLAMP_COLLAR_WRONG_CORE_INTERSECTION")
    if kill_reasons != sorted(set(expected_reasons)):
        raise RawContractError(f"{context}.kill_reasons:DERIVED_MISMATCH")
    if obj["stage"] == "TURNOVER":
        expected_material_gate = bool(
            not kill_reasons
            and material_retention is not None
            and all(item is not None and item <= 0.25 for item in material_retention)
        )
        if deep_material_gate != expected_material_gate:
            raise RawContractError(f"{context}.deep_material_gate:DERIVED_MISMATCH")
    target_gate = all(
        track_statuses[index] == "ALIVE" and current_track_masks[index].count >= MIN_COMPONENT_SIZE
        for index in range(3)
    )
    derived_gate = all(
        (
            state_finite,
            logger_unchanged,
            not events,
            target_gate,
            sentinel_valid,
            not component_switch,
            largest < COVERAGE_CAP,
            distance is not None and distance >= MIN_SEPARATION,
            core_overlap == 0,
            halo_overlap == 0,
            body_overlap == 0,
            not body_contact,
            collar_intrusion == 0,
            not kill_reasons,
        )
    )
    return StepSummary(
        gate_pass=derived_gate,
        distance=distance,
        halo_gap=None if distance is None else distance - 2.0 * HALO_RADIUS,
        core_overlap=core_overlap,
        halo_overlap=halo_overlap,
        body_overlap=body_overlap,
        body_contact=body_contact,
        largest_coverage=largest,
        kill_reason_count=len(kill_reasons),
        tracker_event_count=len(events),
        collar_intrusion_cells=collar_intrusion,
        association_edges_checked=len(edge_values),
        current_track_masks=current_track_masks,
        current_track_centroids=current_track_centroids,
        collar_mask=named_masks["collar"] if collar is not None else None,
    )


def _validate_schedule(value: Any, context: str) -> str:
    obj = _expect_object(
        value,
        {
            "schedule_id",
            "N_standardized_to",
            "settle_steps",
            "stimulus_amplitude",
            "stimulus_steps",
            "horizon_steps",
            "total_engine_steps",
            "schedule_digest",
        },
        context,
    )
    if obj["schedule_id"] != "CORRECTED_NONFUSING_PROBE_V1":
        raise RawContractError(f"{context}.schedule_id:MISMATCH")
    if not _close(_expect_finite(obj["N_standardized_to"], f"{context}.N_standardized_to"), 1.0):
        raise RawContractError(f"{context}.N_standardized_to:MISMATCH")
    constants = {
        "settle_steps": 40,
        "stimulus_steps": 5,
        "horizon_steps": 40,
        "total_engine_steps": 80,
    }
    for name, expected in constants.items():
        if _expect_int(obj[name], f"{context}.{name}", minimum=0) != expected:
            raise RawContractError(f"{context}.{name}:MISMATCH")
    if not _close(_expect_finite(obj["stimulus_amplitude"], f"{context}.stimulus_amplitude"), 0.25):
        raise RawContractError(f"{context}.stimulus_amplitude:MISMATCH")
    return str(_expect_sha256(obj["schedule_digest"], f"{context}.schedule_digest"))


def _validate_operation(value: Any, *, regime: str, schedule_digest: str, context: str) -> int:
    obj = _expect_object(
        value,
        {
            "clamp_active",
            "up_ref_zero",
            "recipient",
            "boundary_frames_sha256",
            "own_replay_exact",
            "unintended_write_cells",
            "isolation_exact",
            "schedule_digest",
        },
        context,
    )
    clamp_expected = regime not in ("ORDINARY", "UP_REF_ZERO")
    up_ref_expected = regime in (
        "UP_REF_ZERO",
        "REFERENCE_NOSWAP_A_UP_REF_ZERO",
        "REFERENCE_NOSWAP_B_UP_REF_ZERO",
    )
    if _expect_bool(obj["clamp_active"], f"{context}.clamp_active") != clamp_expected:
        raise RawContractError(f"{context}.clamp_active:MISMATCH")
    if _expect_bool(obj["up_ref_zero"], f"{context}.up_ref_zero") != up_ref_expected:
        raise RawContractError(f"{context}.up_ref_zero:MISMATCH")
    if obj["recipient"] != ACCESS_RECIPIENT[regime]:
        raise RawContractError(f"{context}.recipient:MISMATCH")
    boundary_expected = clamp_expected
    boundary_digest = _expect_sha256(
        obj["boundary_frames_sha256"],
        f"{context}.boundary_frames_sha256",
        nullable=True,
    )
    if (boundary_digest is not None) != boundary_expected:
        raise RawContractError(f"{context}.boundary_frames_sha256:PRESENCE_MISMATCH")
    if regime.startswith("OWN_REPLAY_SHAM_"):
        if type(obj["own_replay_exact"]) is not bool:
            raise RawContractError(f"{context}.own_replay_exact:EXPECTED_BOOLEAN")
    elif obj["own_replay_exact"] is not None:
        raise RawContractError(f"{context}.own_replay_exact:MUST_BE_NULL")
    if regime.startswith("REFERENCE_NOSWAP_") and regime.endswith("_UP_REF_ZERO"):
        if type(obj["isolation_exact"]) is not bool:
            raise RawContractError(f"{context}.isolation_exact:EXPECTED_BOOLEAN")
    elif obj["isolation_exact"] is not None:
        raise RawContractError(f"{context}.isolation_exact:MUST_BE_NULL")
    unintended = _expect_int(obj["unintended_write_cells"], f"{context}.unintended_write_cells", minimum=0)
    if _expect_sha256(obj["schedule_digest"], f"{context}.schedule_digest") != schedule_digest:
        raise RawContractError(f"{context}.schedule_digest:MISMATCH")
    return unintended


def _validate_isolation_failure(value: Any, context: str) -> dict[str, Any] | None:
    if value is None:
        return None
    obj = _expect_object(value, {"schedule_step", "reasons"}, context)
    schedule_step = _expect_int(obj["schedule_step"], f"{context}.schedule_step", minimum=0)
    if schedule_step > 80:
        raise RawContractError(f"{context}.schedule_step:INTEGER_ABOVE_MAXIMUM")
    reasons = _expect_list(obj["reasons"], f"{context}.reasons")
    if not reasons or reasons != sorted(set(reasons)):
        raise RawContractError(f"{context}.reasons:MUST_BE_NONEMPTY_SORTED_UNIQUE")
    for index, reason in enumerate(reasons):
        _expect_token(reason, f"{context}.reasons[{index}]")
    return obj


def _validate_isolation_evidence(value: Any, *, recipient: str, context: str) -> bool:
    obj = _expect_object(
        value,
        {
            "recipient",
            "barrier_width",
            "up_ref_zero",
            "environment_perturbation",
            "per_step",
            "maximum_core_abs_difference",
            "environment_c_max_difference_at_end",
            "outside_difference_nonzero",
            "own_replay_up_ref_zero_exact",
            "left_first_failure",
            "right_first_failure",
            "bit_exact_isolation",
        },
        context,
    )
    if obj["recipient"] != recipient:
        raise RawContractError(f"{context}.recipient:MISMATCH")
    if _expect_int(obj["barrier_width"], f"{context}.barrier_width") != 2:
        raise RawContractError(f"{context}.barrier_width:MISMATCH")
    if _expect_bool(obj["up_ref_zero"], f"{context}.up_ref_zero") is not True:
        raise RawContractError(f"{context}.up_ref_zero:MISMATCH")
    perturbation = _expect_object(
        obj["environment_perturbation"],
        {"fields", "amplitude"},
        f"{context}.environment_perturbation",
    )
    if perturbation["fields"] != ["c", "N"]:
        raise RawContractError(f"{context}.environment_perturbation.fields:MISMATCH")
    if not _close(
        _expect_finite(perturbation["amplitude"], f"{context}.environment_perturbation.amplitude"),
        0.05,
    ):
        raise RawContractError(f"{context}.environment_perturbation.amplitude:MISMATCH")
    rows = _expect_list(obj["per_step"], f"{context}.per_step")
    per_step_maxima: list[float] = []
    hashes_equal = True
    own_upref_pairs_equal = True
    for index, row_value in enumerate(rows):
        row = _expect_object(
            row_value,
            {
                "schedule_step",
                "max_core_abs",
                "left_core_sha256",
                "right_core_sha256",
                "left_state_sha256",
                "free_up_ref_state_sha256",
            },
            f"{context}.per_step[{index}]",
        )
        if _expect_int(row["schedule_step"], f"{context}.per_step[{index}].schedule_step", minimum=1) != index + 1:
            raise RawContractError(f"{context}.per_step[{index}].schedule_step:ORDER_MISMATCH")
        maximum = _expect_finite(row["max_core_abs"], f"{context}.per_step[{index}].max_core_abs")
        if maximum < 0.0:
            raise RawContractError(f"{context}.per_step[{index}].max_core_abs:NEGATIVE")
        left = _expect_sha256(row["left_core_sha256"], f"{context}.per_step[{index}].left_core_sha256")
        right = _expect_sha256(row["right_core_sha256"], f"{context}.per_step[{index}].right_core_sha256")
        left_state = _expect_sha256(
            row["left_state_sha256"],
            f"{context}.per_step[{index}].left_state_sha256",
        )
        free_state = _expect_sha256(
            row["free_up_ref_state_sha256"],
            f"{context}.per_step[{index}].free_up_ref_state_sha256",
            nullable=True,
        )
        per_step_maxima.append(maximum)
        hashes_equal &= left == right
        own_upref_pairs_equal &= free_state is not None and left_state == free_state
    terminal_max = _expect_finite(obj["maximum_core_abs_difference"], f"{context}.maximum_core_abs_difference")
    if not _close(terminal_max, max(per_step_maxima, default=0.0)):
        raise RawContractError(f"{context}.maximum_core_abs_difference:DERIVED_MISMATCH")
    environment_difference = _expect_finite(
        obj["environment_c_max_difference_at_end"],
        f"{context}.environment_c_max_difference_at_end",
    )
    outside_nonzero = _expect_bool(obj["outside_difference_nonzero"], f"{context}.outside_difference_nonzero")
    if outside_nonzero != (environment_difference > 0.0):
        raise RawContractError(f"{context}.outside_difference_nonzero:DERIVED_MISMATCH")
    left_failure = _validate_isolation_failure(obj["left_first_failure"], f"{context}.left_first_failure")
    right_failure = _validate_isolation_failure(obj["right_first_failure"], f"{context}.right_first_failure")
    own_upref_exact = bool(len(rows) == 80 and own_upref_pairs_equal)
    if _expect_bool(
        obj["own_replay_up_ref_zero_exact"],
        f"{context}.own_replay_up_ref_zero_exact",
    ) != own_upref_exact:
        raise RawContractError(f"{context}.own_replay_up_ref_zero_exact:DERIVED_MISMATCH")
    derived = bool(
        len(rows) == 80
        and hashes_equal
        and own_upref_exact
        and terminal_max == 0.0
        and outside_nonzero
        and left_failure is None
        and right_failure is None
    )
    if _expect_bool(obj["bit_exact_isolation"], f"{context}.bit_exact_isolation") != derived:
        raise RawContractError(f"{context}.bit_exact_isolation:DERIVED_MISMATCH")
    return derived


@dataclass
class WorldSummary:
    value: dict[str, Any]
    derived_complete: bool


def _validate_record_series(
    values: Any,
    *,
    world_id: int,
    context: str,
    initial_prior: Mapping[int, DecodedMask] | None = None,
    initial_prior_centroids: Mapping[int, tuple[float, float] | None] | None = None,
) -> tuple[
    list[StepSummary],
    bool,
    dict[int, DecodedMask] | None,
    dict[int, tuple[float, float] | None] | None,
]:
    records = _expect_list(values, context)
    summaries: list[StepSummary] = []
    prior: dict[int, DecodedMask] | None = dict(initial_prior) if initial_prior is not None else None
    prior_centroids: dict[int, tuple[float, float] | None] | None = (
        dict(initial_prior_centroids) if initial_prior_centroids is not None else None
    )
    fixed_collar: DecodedMask | None = None
    previous_engine_step: int | None = None
    for index, record in enumerate(records):
        record_prior = None if index == 0 and record.get("stage") in ("PREWRITER", "PROBE_STANDARDIZE") else prior
        summary = validate_step_record(
            record,
            world_id=world_id,
            context=f"{context}[{index}]",
            prior_track_masks=record_prior,
            prior_track_centroids=(
                None
                if index == 0 and record.get("stage") in ("PREWRITER", "PROBE_STANDARDIZE")
                else prior_centroids
            ),
            fixed_collar_mask=fixed_collar,
        )
        engine_step = record["engine_step"]
        if previous_engine_step is not None and engine_step != previous_engine_step + 1:
            raise RawContractError(f"{context}[{index}].engine_step:NOT_CONTIGUOUS")
        previous_engine_step = engine_step
        prior = summary.current_track_masks
        prior_centroids = summary.current_track_centroids
        if summary.collar_mask is not None:
            if fixed_collar is None:
                fixed_collar = summary.collar_mask
            elif summary.collar_mask.packed != fixed_collar.packed:
                raise RawContractError(f"{context}[{index}].masks.collar:CHANGED_WITHIN_SERIES")
        summaries.append(summary)
    return (
        summaries,
        bool(records) and all(summary.gate_pass for summary in summaries),
        prior,
        prior_centroids,
    )


def validate_world_shard(value: Any, *, expected_sequence: int) -> WorldSummary:
    root_keys = {
        "schema",
        "mission",
        "mode",
        "phase0_commit",
        "world_id",
        "sequence_index",
        "manifest_sha256",
        "plan_sha256",
        "previous_record_sha256",
        "contract_bindings",
        "assignment",
        "prewriter_state_sha256",
        "prewriter_clone_sha256",
        "writer",
        "common_deep_step",
        "history_arms",
        "world_complete",
        "first_failure",
    }
    obj = _expect_object(value, root_keys, f"shard[{expected_sequence}]")
    assert_outcome_free(obj)
    if obj["schema"] != RAW_SCHEMA or obj["mission"] != MISSION or obj["mode"] != MODE:
        raise RawContractError(f"shard[{expected_sequence}]:SCHEMA_MISSION_MODE_MISMATCH")
    if obj["phase0_commit"] != PHASE0_COMMIT:
        raise RawContractError(f"shard[{expected_sequence}]:PHASE0_COMMIT_MISMATCH")
    world_id = _expect_int(obj["world_id"], f"shard[{expected_sequence}].world_id")
    if expected_sequence >= len(WORLD_ORDER) or world_id != WORLD_ORDER[expected_sequence]:
        raise RawContractError(f"shard[{expected_sequence}]:WORLD_ORDER_MISMATCH")
    if _expect_int(obj["sequence_index"], f"shard[{expected_sequence}].sequence_index", minimum=0) != expected_sequence:
        raise RawContractError(f"shard[{expected_sequence}]:SEQUENCE_INDEX_MISMATCH")
    _expect_sha256(obj["manifest_sha256"], f"shard[{expected_sequence}].manifest_sha256")
    plan_sha256 = _expect_sha256(obj["plan_sha256"], f"shard[{expected_sequence}].plan_sha256")
    if plan_sha256 != EXPECTED_PLAN_SHA256:
        raise RawContractError(f"shard[{expected_sequence}].plan_sha256:FROZEN_PLAN_MISMATCH")
    _expect_sha256(obj["previous_record_sha256"], f"shard[{expected_sequence}].previous_record_sha256", nullable=True)
    _validate_contract_bindings(obj["contract_bindings"], f"shard[{expected_sequence}].contract_bindings")
    _validate_root_assignment(obj["assignment"], world_id, f"shard[{expected_sequence}].assignment")
    prewriter_state = str(
        _expect_sha256(obj["prewriter_state_sha256"], f"shard[{expected_sequence}].prewriter_state_sha256")
    )
    prewriter_clones = _expect_list(
        obj["prewriter_clone_sha256"],
        f"shard[{expected_sequence}].prewriter_clone_sha256",
        length=4,
    )
    for clone_index, clone_value in enumerate(prewriter_clones):
        clone_digest = _expect_sha256(
            clone_value,
            f"shard[{expected_sequence}].prewriter_clone_sha256[{clone_index}]",
        )
        if clone_digest != prewriter_state:
            raise RawContractError(f"shard[{expected_sequence}].prewriter_clone_sha256:CLONE_MISMATCH")

    writer = _expect_object(
        obj["writer"],
        {
            "writer_id",
            "stream_rule",
            "phase_steps",
            "phase_amplitudes",
            "amplitude_range",
            "target_patch_sha256",
            "operation_order",
            "operations_per_writer_step",
            "common_schedule_sha256",
        },
        f"shard[{expected_sequence}].writer",
    )
    if writer["writer_id"] != "FROZEN_03G_LOCAL_GAUSSIAN_WRITER":
        raise RawContractError("writer.writer_id:MISMATCH")
    if writer["stream_rule"] != "first amplitude pair from numpy default_rng(original_world_id)":
        raise RawContractError("writer.stream_rule:MISMATCH")
    if _expect_int(writer["phase_steps"], "writer.phase_steps", minimum=0) != 60:
        raise RawContractError("writer.phase_steps:MISMATCH")
    amplitudes = _expect_list(writer["phase_amplitudes"], "writer.phase_amplitudes", length=2)
    for index, amplitude in enumerate(amplitudes):
        numeric = _expect_finite(amplitude, f"writer.phase_amplitudes[{index}]")
        if not 0.005 <= numeric <= 0.035:
            raise RawContractError(f"writer.phase_amplitudes[{index}]:OUT_OF_FROZEN_RANGE")
    amplitude_range = _expect_list(writer["amplitude_range"], "writer.amplitude_range", length=2)
    if not (_close(_expect_finite(amplitude_range[0], "writer.amplitude_range[0]"), 0.005)
            and _close(_expect_finite(amplitude_range[1], "writer.amplitude_range[1]"), 0.035)):
        raise RawContractError("writer.amplitude_range:MISMATCH")
    patch_hashes = _expect_object(writer["target_patch_sha256"], {"A", "B"}, "writer.target_patch_sha256")
    _expect_sha256(patch_hashes["A"], "writer.target_patch_sha256.A")
    _expect_sha256(patch_hashes["B"], "writer.target_patch_sha256.B")
    if writer["operation_order"] != ["A", "B"]:
        raise RawContractError("writer.operation_order:MISMATCH")
    if _expect_int(writer["operations_per_writer_step"], "writer.operations_per_writer_step") != 2:
        raise RawContractError("writer.operations_per_writer_step:MISMATCH")
    _expect_sha256(writer["common_schedule_sha256"], "writer.common_schedule_sha256")

    arm_values = _expect_list(obj["history_arms"], f"shard[{expected_sequence}].history_arms", length=4)
    clone_hash: str | None = None
    root_common_deep = obj["common_deep_step"]
    if root_common_deep is not None:
        root_common_deep = _expect_int(root_common_deep, f"shard[{expected_sequence}].common_deep_step", minimum=1)
    common_deep_step: int | None = None
    all_step_summaries: list[StepSummary] = []
    all_arms_complete = True
    max_unintended = 0
    access_count = 0
    arm_failures: list[dict[str, Any] | None] = []
    for arm_index, arm_value in enumerate(arm_values):
        arm_context = f"shard[{expected_sequence}].history_arms[{arm_index}]"
        arm_obj = _expect_object(
            arm_value,
            {
                "arm",
                "bits",
                "clone_sha256",
                "writer",
                "writer_records",
                "common_deep_step",
                "deep_complete",
                "deep_joint",
                "turnover_records",
                "access_regimes",
                "arm_complete",
                "first_failure",
            },
            arm_context,
        )
        arm = arm_obj["arm"]
        if arm != ARM_ORDER[arm_index]:
            raise RawContractError(f"{arm_context}.arm:ORDER_MISMATCH")
        bits = _expect_list(arm_obj["bits"], f"{arm_context}.bits", length=2)
        if tuple(bits) != ARM_BITS[arm] or any(type(bit) is not int for bit in bits):
            raise RawContractError(f"{arm_context}.bits:MISMATCH")
        current_clone = str(_expect_sha256(arm_obj["clone_sha256"], f"{arm_context}.clone_sha256"))
        if current_clone != prewriter_clones[arm_index]:
            raise RawContractError(f"{arm_context}.clone_sha256:PREWRITER_BINDING_MISMATCH")
        if clone_hash is None:
            clone_hash = current_clone
        elif current_clone != clone_hash:
            raise RawContractError(f"{arm_context}.clone_sha256:CLONE_MISMATCH")
        arm_writer = _expect_object(
            arm_obj["writer"],
            {
                "operation_count",
                "expected_operation_count",
                "total_writer_engine_steps",
                "active_writer_steps",
                "settle_steps",
                "operation_digest",
                "postwriter_state_sha256",
                "sham_reference_exact",
            },
            f"{arm_context}.writer",
        )
        operation_count = _expect_int(
            arm_writer["operation_count"], f"{arm_context}.writer.operation_count", minimum=0
        )
        if _expect_int(
            arm_writer["expected_operation_count"],
            f"{arm_context}.writer.expected_operation_count",
            minimum=0,
        ) != 240:
            raise RawContractError(f"{arm_context}.writer.expected_operation_count:MISMATCH")
        total_writer_steps = _expect_int(
            arm_writer["total_writer_engine_steps"],
            f"{arm_context}.writer.total_writer_engine_steps",
            minimum=0,
        )
        active_writer_steps = _expect_int(
            arm_writer["active_writer_steps"],
            f"{arm_context}.writer.active_writer_steps",
            minimum=0,
        )
        writer_settle_steps = _expect_int(
            arm_writer["settle_steps"],
            f"{arm_context}.writer.settle_steps",
            minimum=0,
        )
        if operation_count != 2 * active_writer_steps or total_writer_steps != active_writer_steps + writer_settle_steps:
            raise RawContractError(f"{arm_context}.writer:COUNT_IDENTITY_MISMATCH")
        if active_writer_steps > 120 or writer_settle_steps > 120 or total_writer_steps > 240:
            raise RawContractError(f"{arm_context}.writer:COUNT_ABOVE_FROZEN_MAXIMUM")
        _expect_sha256(arm_writer["operation_digest"], f"{arm_context}.writer.operation_digest")
        _expect_sha256(arm_writer["postwriter_state_sha256"], f"{arm_context}.writer.postwriter_state_sha256")
        if arm == "H00":
            if type(arm_writer["sham_reference_exact"]) is not bool:
                raise RawContractError(f"{arm_context}.writer.sham_reference_exact:EXPECTED_BOOLEAN")
        elif arm_writer["sham_reference_exact"] is not None:
            raise RawContractError(f"{arm_context}.writer.sham_reference_exact:MUST_BE_NULL")
        arm_failure = _validate_failure(arm_obj["first_failure"], f"{arm_context}.first_failure")
        writer_summaries, writer_gates, writer_final_masks, writer_final_centroids = _validate_record_series(
            arm_obj["writer_records"],
            world_id=world_id,
            context=f"{arm_context}.writer_records",
        )
        all_step_summaries.extend(writer_summaries)
        if len(writer_summaries) != total_writer_steps + 1:
            raise RawContractError(f"{arm_context}.writer_records:COUNT_MISMATCH")
        writer_records = arm_obj["writer_records"]
        if writer_records[0]["stage"] != "PREWRITER" or writer_records[0]["stage_step"] != 0:
            raise RawContractError(f"{arm_context}.writer_records[0]:INVALID_SEED_SNAPSHOT")
        if writer_records[0]["state_sha256"] != current_clone:
            raise RawContractError(f"{arm_context}.writer_records[0].state_sha256:CLONE_MISMATCH")
        for local_index, record in enumerate(writer_records[1:], start=1):
            if local_index <= active_writer_steps:
                expected_stage, expected_stage_step = "WRITER", local_index
            else:
                expected_stage, expected_stage_step = "POSTWRITER_SETTLE", local_index - active_writer_steps
            if record["stage"] != expected_stage or record["stage_step"] != expected_stage_step:
                raise RawContractError(f"{arm_context}.writer_records[{local_index}]:STAGE_MISMATCH")
        if arm_writer["postwriter_state_sha256"] != writer_records[-1]["state_sha256"]:
            raise RawContractError(f"{arm_context}.writer.postwriter_state_sha256:TERMINAL_RECORD_MISMATCH")
        writer_complete = bool(
            len(writer_summaries) == 241
            and writer_gates
            and operation_count == 240
            and active_writer_steps == 120
            and writer_settle_steps == 120
            and (arm != "H00" or arm_writer["sham_reference_exact"] is True)
        )
        expected_arm_failure = _first_trace_failure(writer_records)
        if expected_arm_failure is None and not writer_complete:
            if arm == "H00" and arm_writer["sham_reference_exact"] is False:
                expected_arm_failure = _synthetic_failure(
                    writer_records[-1],
                    stage="WRITER",
                    stage_step=active_writer_steps,
                    reason="H00_SHAM_NOT_BYTE_IDENTICAL_TO_NO_WRITER_CONTINUATION",
                )
            else:
                expected_arm_failure = _synthetic_failure(
                    writer_records[-1],
                    stage="WRITER",
                    stage_step=active_writer_steps,
                    reason="WRITER_SCHEDULE_INCOMPLETE",
                )
        deep_step = arm_obj["common_deep_step"]
        if deep_step is not None:
            deep_step = _expect_int(deep_step, f"{arm_context}.common_deep_step", minimum=1)
        if arm_index == 0:
            common_deep_step = deep_step
        elif deep_step != common_deep_step:
            raise RawContractError(f"{arm_context}.common_deep_step:MISMATCH")
        deep_declared = _expect_bool(arm_obj["deep_complete"], f"{arm_context}.deep_complete")
        turnover_summaries, turnover_gates, _turnover_final_masks, _turnover_final_centroids = _validate_record_series(
            arm_obj["turnover_records"],
            world_id=world_id,
            context=f"{arm_context}.turnover_records",
            initial_prior=writer_final_masks,
            initial_prior_centroids=writer_final_centroids,
        )
        all_step_summaries.extend(turnover_summaries)
        turnover_records = arm_obj["turnover_records"]
        for local_index, record in enumerate(turnover_records, start=1):
            if record["stage"] != "TURNOVER" or record["stage_step"] != local_index:
                raise RawContractError(f"{arm_context}.turnover_records[{local_index - 1}]:STAGE_MISMATCH")
        if turnover_records and turnover_records[0]["engine_step"] != writer_records[-1]["engine_step"] + 1:
            raise RawContractError(f"{arm_context}.turnover_records[0].engine_step:WRITER_DISCONTINUITY")
        derived_deep = bool(
            writer_complete
            and common_deep_step is not None
            and len(turnover_summaries) == common_deep_step
            and turnover_gates
            and arm_obj["turnover_records"][-1]["deep_material_gate"] is True
        )
        deep_joint_values = arm_obj["deep_joint"]
        if deep_joint_values is None:
            if deep_declared:
                raise RawContractError(f"{arm_context}.deep_joint:MISSING_FOR_COMPLETE_DEEP")
            deep_joint_values = []
        else:
            deep_joint_values = _expect_list(deep_joint_values, f"{arm_context}.deep_joint", length=3)
        expected_labels = ("A", "B", "SENTINEL")
        for joint_index, joint_value in enumerate(deep_joint_values):
            joint_context = f"{arm_context}.deep_joint[{joint_index}]"
            joint = _expect_object(
                joint_value,
                {"target", "material_retention", "phenotype_descriptor"},
                joint_context,
            )
            if joint["target"] != expected_labels[joint_index]:
                raise RawContractError(f"{joint_context}.target:ORDER_MISMATCH")
            retention = (
                None
                if joint["material_retention"] is None
                else _expect_finite(joint["material_retention"], f"{joint_context}.material_retention")
            )
            if retention is not None and (retention < 0.0 or retention > 1.0):
                raise RawContractError(f"{joint_context}.material_retention:OUTSIDE_UNIT_INTERVAL")
            descriptor = _expect_object(
                joint["phenotype_descriptor"],
                {"component_size", "centroid", "body_core_coverage"},
                f"{joint_context}.phenotype_descriptor",
            )
            _expect_int(descriptor["component_size"], f"{joint_context}.phenotype_descriptor.component_size", minimum=0)
            _read_centroid(
                descriptor["centroid"],
                f"{joint_context}.phenotype_descriptor.centroid",
            )
            coverage = _expect_finite(
                descriptor["body_core_coverage"],
                f"{joint_context}.phenotype_descriptor.body_core_coverage",
            )
            if coverage < 0.0 or coverage > 1.0:
                raise RawContractError(f"{joint_context}.phenotype_descriptor.body_core_coverage:OUTSIDE_UNIT_INTERVAL")
        if turnover_summaries:
            last_turnover = arm_obj["turnover_records"][-1]
            last_retention = last_turnover["material_retention"]
            if last_retention is None:
                raise RawContractError(f"{arm_context}.deep_joint:NO_TERMINAL_MATERIAL_PRIMITIVE")
            for joint_index, joint in enumerate(deep_joint_values):
                tracker_id = WORLD_ASSIGNMENTS[world_id][joint_index]
                joint_retention = joint["material_retention"]
                record_retention = last_retention[tracker_id]
                if (joint_retention is None) != (record_retention is None) or (
                    joint_retention is not None
                    and not _close(float(joint_retention), float(record_retention))
                ):
                    raise RawContractError(f"{arm_context}.deep_joint[{joint_index}]:RETENTION_MISMATCH")
                track = last_turnover["tracks"][tracker_id]
                descriptor = joint["phenotype_descriptor"]
                if descriptor["component_size"] != track["component_size"]:
                    raise RawContractError(f"{arm_context}.deep_joint[{joint_index}]:SIZE_MISMATCH")
                expected_centroid = track["centroid"]
                if descriptor["centroid"] != expected_centroid:
                    # Canonical writer and logger should reuse the exact stored
                    # float values rather than independently rounding them.
                    raise RawContractError(f"{arm_context}.deep_joint[{joint_index}]:CENTROID_MISMATCH")
                if not _close(float(descriptor["body_core_coverage"]), float(track["body_core_coverage"])):
                    raise RawContractError(f"{arm_context}.deep_joint[{joint_index}]:COVERAGE_MISMATCH")
        if deep_declared != derived_deep:
            raise RawContractError(f"{arm_context}.deep_complete:DERIVED_MISMATCH")
        if expected_arm_failure is None and not derived_deep:
            trace_failure = _first_trace_failure(turnover_records)
            if trace_failure is not None:
                expected_arm_failure = trace_failure
            elif arm != "H00" and common_deep_step is None:
                expected_arm_failure = _synthetic_failure(
                    writer_records[-1],
                    stage="TURNOVER",
                    stage_step=0,
                    reason="H00_COMMON_DEEP_STEP_UNAVAILABLE",
                )
            elif turnover_records:
                expected_arm_failure = _synthetic_failure(
                    turnover_records[-1],
                    stage="TURNOVER",
                    stage_step=len(turnover_records),
                    reason=(
                        "H00_COMMON_DEEP_STEP_NOT_REACHED_BY_1500"
                        if arm == "H00"
                        else "COMMON_H00_DEEP_MATERIAL_GATE_FAILED"
                    ),
                )

        access_values = _expect_list(arm_obj["access_regimes"], f"{arm_context}.access_regimes")
        if len(access_values) not in (0, 8):
            raise RawContractError(f"{arm_context}.access_regimes:MUST_BE_EMPTY_OR_COMPLETE_SET")
        arm_access_complete = len(access_values) == 8
        schedule_digests: set[str] = set()
        access_by_name: dict[str, dict[str, Any]] = {}
        access_seed_signatures: list[tuple[str, dict[str, Any]]] = []
        access_failures: list[dict[str, Any] | None] = []
        for regime_index, regime_value in enumerate(access_values):
            regime_context = f"{arm_context}.access_regimes[{regime_index}]"
            regime_obj = _expect_object(
                regime_value,
                {
                    "regime",
                    "recipient",
                    "schedule",
                    "operation",
                    "records",
                    "complete",
                    "probe_schedule_viable",
                    "first_failure",
                    "isolation_evidence",
                },
                regime_context,
            )
            regime = regime_obj["regime"]
            if regime != ACCESS_ORDER[regime_index]:
                raise RawContractError(f"{regime_context}.regime:ORDER_MISMATCH")
            if regime_obj["recipient"] != ACCESS_RECIPIENT[regime]:
                raise RawContractError(f"{regime_context}.recipient:MISMATCH")
            schedule_digest = _validate_schedule(regime_obj["schedule"], f"{regime_context}.schedule")
            schedule_digests.add(schedule_digest)
            unintended = _validate_operation(
                regime_obj["operation"],
                regime=regime,
                schedule_digest=schedule_digest,
                context=f"{regime_context}.operation",
            )
            max_unintended = max(max_unintended, unintended)
            failure = _validate_failure(regime_obj["first_failure"], f"{regime_context}.first_failure")
            access_summaries, access_gates, _access_final_masks, _access_final_centroids = _validate_record_series(
                regime_obj["records"],
                world_id=world_id,
                context=f"{regime_context}.records",
            )
            all_step_summaries.extend(access_summaries)
            if access_summaries:
                records = regime_obj["records"]
                if records[0]["stage"] != "PROBE_STANDARDIZE" or records[0]["stage_step"] != 0:
                    raise RawContractError(f"{regime_context}.records[0]:MISSING_STANDARDIZE_SNAPSHOT")
                seed = records[0]
                access_seed_signatures.append(
                    (
                        regime,
                        {
                            "state_sha256": seed["state_sha256"],
                            "engine_step": seed["engine_step"],
                            "assignment": seed["assignment"],
                            "components": seed["components"],
                            "tracks": seed["tracks"],
                            "pair_geometry": seed["pair_geometry"],
                            "masks": {
                                name: seed["masks"][name]
                                for name in (
                                    "A",
                                    "B",
                                    "SENTINEL",
                                    "core_A",
                                    "core_B",
                                    "halo_A",
                                    "halo_B",
                                )
                            },
                        },
                    )
                )
                for local_index, record in enumerate(records[1:], start=1):
                    expected_stage = "PROBE_SETTLE" if local_index <= 40 else "PROBE_HORIZON"
                    expected_stage_step = local_index if local_index <= 40 else local_index - 40
                    if record["stage"] != expected_stage or record["stage_step"] != expected_stage_step:
                        raise RawContractError(f"{regime_context}.records[{local_index}]:SCHEDULE_STAGE_MISMATCH")
            isolation = regime_obj["isolation_evidence"]
            if regime.endswith("_UP_REF_ZERO") and regime.startswith("REFERENCE_NOSWAP_"):
                if isolation is None:
                    raise RawContractError(f"{regime_context}.isolation_evidence:MISSING")
                derived_isolation = _validate_isolation_evidence(
                    isolation,
                    recipient=str(regime_obj["recipient"]),
                    context=f"{regime_context}.isolation_evidence",
                )
                if regime_obj["operation"]["isolation_exact"] != derived_isolation:
                    raise RawContractError(f"{regime_context}.operation.isolation_exact:DERIVED_MISMATCH")
            elif isolation is not None:
                raise RawContractError(f"{regime_context}.isolation_evidence:MUST_BE_NULL")
            expected_regime_failure = _first_trace_failure(regime_obj["records"])
            terminal_access_record = regime_obj["records"][-1]
            if expected_regime_failure is None and unintended > 0:
                expected_regime_failure = _synthetic_failure(
                    terminal_access_record,
                    stage="CLAMP",
                    stage_step=len(access_summaries) - 1,
                    reason="CLAMP_UNINTENDED_WRITE_OUTSIDE_COLLAR",
                )
            if (
                expected_regime_failure is None
                and regime.startswith("OWN_REPLAY_SHAM_")
                and regime_obj["operation"]["own_replay_exact"] is False
            ):
                expected_regime_failure = _synthetic_failure(
                    terminal_access_record,
                    stage="CLAMP",
                    stage_step=len(access_summaries) - 1,
                    reason="OWN_REPLAY_NOT_BYTE_IDENTICAL",
                )
            if (
                expected_regime_failure is None
                and isolation is not None
                and regime_obj["operation"]["isolation_exact"] is False
            ):
                expected_regime_failure = _synthetic_failure(
                    terminal_access_record,
                    stage="EXACT_ISOLATION",
                    stage_step=80,
                    reason="PAIR_CONTEXT_EXACT_ISOLATION_FAILED",
                )
            if failure != expected_regime_failure:
                raise RawContractError(f"{regime_context}.first_failure:DERIVED_MISMATCH")
            access_failures.append(failure)
            # Complete scheduled continuation = standardized seed snapshot plus
            # exactly forty settle and forty horizon steps.
            derived_access = bool(
                len(access_summaries) == 81
                and access_gates
                and unintended == 0
                and failure is None
                and (
                    not (regime.endswith("_UP_REF_ZERO") and regime.startswith("REFERENCE_NOSWAP_"))
                    or regime_obj["operation"]["isolation_exact"] is True
                )
            )
            declared_access = _expect_bool(regime_obj["complete"], f"{regime_context}.complete")
            if declared_access != derived_access:
                raise RawContractError(f"{regime_context}.complete:DERIVED_MISMATCH")
            if _expect_bool(
                regime_obj["probe_schedule_viable"],
                f"{regime_context}.probe_schedule_viable",
            ) != declared_access:
                raise RawContractError(f"{regime_context}.probe_schedule_viable:MISMATCH")
            arm_access_complete &= derived_access
            access_count += 1
            access_by_name[regime] = regime_obj
        if access_values and len(schedule_digests) != 1:
            raise RawContractError(f"{arm_context}.access_regimes:SCHEDULE_DIGEST_MISMATCH")
        if access_values:
            if len(access_seed_signatures) != len(ACCESS_ORDER):
                raise RawContractError(
                    f"{arm_context}.access_regimes:STANDARDIZED_CLONE_SEED_MISSING"
                )
            reference_seed = access_seed_signatures[0][1]
            mismatched_seeds = [
                regime
                for regime, signature in access_seed_signatures[1:]
                if signature != reference_seed
            ]
            if mismatched_seeds:
                raise RawContractError(
                    f"{arm_context}.access_regimes:STANDARDIZED_CLONE_SEED_MISMATCH:"
                    f"{mismatched_seeds}"
                )
            ordinary_hashes = [record["state_sha256"] for record in access_by_name["ORDINARY"]["records"]]
            for own_name in ("OWN_REPLAY_SHAM_A", "OWN_REPLAY_SHAM_B"):
                own_hashes = [record["state_sha256"] for record in access_by_name[own_name]["records"]]
                derived_own_exact = len(own_hashes) == len(ordinary_hashes) and own_hashes == ordinary_hashes
                if access_by_name[own_name]["operation"]["own_replay_exact"] != derived_own_exact:
                    raise RawContractError(f"{arm_context}.{own_name}:OWN_REPLAY_HASH_MISMATCH")
        if derived_deep and len(access_values) != 8:
            raise RawContractError(f"{arm_context}.access_regimes:DEEP_COMPLETE_REQUIRES_EIGHT_REGIMES")
        if expected_arm_failure is None:
            expected_arm_failure = next((item for item in access_failures if item is not None), None)
        arm_declared = _expect_bool(arm_obj["arm_complete"], f"{arm_context}.arm_complete")
        derived_arm = bool(
            writer_complete
            and derived_deep
            and arm_access_complete
            and arm_failure is None
        )
        if arm_declared != derived_arm:
            raise RawContractError(f"{arm_context}.arm_complete:DERIVED_MISMATCH")
        if (arm_failure is None) != derived_arm:
            raise RawContractError(f"{arm_context}.first_failure:COMPLETION_UNION_MISMATCH")
        if arm_failure != expected_arm_failure:
            raise RawContractError(f"{arm_context}.first_failure:EARLIEST_FAILURE_MISMATCH")
        arm_failures.append(arm_failure)
        all_arms_complete &= derived_arm

    declared_world = _expect_bool(obj["world_complete"], f"shard[{expected_sequence}].world_complete")
    first_failure = _validate_failure(obj["first_failure"], f"shard[{expected_sequence}].first_failure")
    if root_common_deep != common_deep_step:
        raise RawContractError(f"shard[{expected_sequence}].common_deep_step:ARM_MISMATCH")
    derived_world = all_arms_complete and max_unintended == 0 and first_failure is None
    if declared_world != derived_world:
        raise RawContractError(f"shard[{expected_sequence}].world_complete:DERIVED_MISMATCH")
    if (first_failure is None) != derived_world:
        raise RawContractError(f"shard[{expected_sequence}].first_failure:COMPLETION_UNION_MISMATCH")
    expected_world_failure = next((item for item in arm_failures if item is not None), None)
    if first_failure != expected_world_failure:
        raise RawContractError(f"shard[{expected_sequence}].first_failure:EARLIEST_FAILURE_MISMATCH")
    if not all_step_summaries:
        minimum_distance = None
        minimum_halo_gap = None
        maximum_core_overlap = None
        maximum_halo_overlap = None
        maximum_body_overlap = None
        maximum_coverage = None
    else:
        available_distances = [summary.distance for summary in all_step_summaries if summary.distance is not None]
        available_halo_gaps = [summary.halo_gap for summary in all_step_summaries if summary.halo_gap is not None]
        minimum_distance = min(available_distances, default=None)
        minimum_halo_gap = min(available_halo_gaps, default=None)
        maximum_core_overlap = max(summary.core_overlap for summary in all_step_summaries)
        maximum_halo_overlap = max(summary.halo_overlap for summary in all_step_summaries)
        maximum_body_overlap = max(summary.body_overlap for summary in all_step_summaries)
        maximum_coverage = max(summary.largest_coverage for summary in all_step_summaries)
    summary_value = {
        "world_id": world_id,
        "sequence_index": expected_sequence,
        "assignment": {
            "A_target_index": WORLD_ASSIGNMENTS[world_id][0],
            "B_target_index": WORLD_ASSIGNMENTS[world_id][1],
            "sentinel_target_index": WORLD_ASSIGNMENTS[world_id][2],
        },
        "history_arm_count": len(arm_values),
        "access_regime_count": access_count,
        "step_records_checked": len(all_step_summaries),
        "association_edges_checked": sum(summary.association_edges_checked for summary in all_step_summaries),
        "minimum_pair_distance": minimum_distance,
        "minimum_radius12_halo_gap": minimum_halo_gap,
        "maximum_core_overlap_cells": maximum_core_overlap,
        "maximum_halo_overlap_cells": maximum_halo_overlap,
        "maximum_body_overlap_cells": maximum_body_overlap,
        "maximum_largest_component_coverage": maximum_coverage,
        "maximum_unintended_write_cells": max_unintended,
        "kill_reason_records": sum(summary.kill_reason_count > 0 for summary in all_step_summaries),
        "tracker_event_records": sum(summary.tracker_event_count > 0 for summary in all_step_summaries),
        "collar_intrusion_cells": sum(summary.collar_intrusion_cells for summary in all_step_summaries),
        "declared_world_complete": declared_world,
        "derived_world_complete": derived_world,
        "first_failure": first_failure,
    }
    return WorldSummary(value=summary_value, derived_complete=derived_world)


def _assert_schema_objects_closed(node: Any, context: str = "$") -> None:
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "object" and node.get("additionalProperties") is not False:
            raise RawContractError(f"SCHEMA_OBJECT_NOT_CLOSED:{context}")
        for key, child in node.items():
            _assert_schema_objects_closed(child, f"{context}/{key}")
    elif isinstance(node, list):
        for index, child in enumerate(node):
            _assert_schema_objects_closed(child, f"{context}/{index}")


def validate_schema_document(schema: Any) -> None:
    if not isinstance(schema, dict):
        raise RawContractError("SCHEMA_ROOT_NOT_OBJECT")
    if schema.get("$id") != FINAL_SCHEMA_ID:
        raise RawContractError("FINAL_SCHEMA_ID_MISMATCH")
    _assert_schema_objects_closed(schema)


def reproduce_shards(
    shards: Sequence[tuple[dict[str, Any], bytes]],
    *,
    schema_document: dict[str, Any],
) -> dict[str, Any]:
    validate_schema_document(schema_document)
    if len(shards) > len(WORLD_ORDER):
        raise RawContractError("TOO_MANY_WORLD_SHARDS")
    summaries: list[WorldSummary] = []
    sources: list[dict[str, Any]] = []
    manifest_sha: str | None = None
    plan_sha: str | None = None
    previous_canonical_sha: str | None = None
    for sequence, (value, canonical) in enumerate(shards):
        if value.get("previous_record_sha256") != previous_canonical_sha:
            raise RawContractError(f"shard[{sequence}]:PREDECESSOR_HASH_MISMATCH")
        current_manifest = value.get("manifest_sha256")
        current_plan = value.get("plan_sha256")
        if manifest_sha is None:
            manifest_sha = current_manifest
            plan_sha = current_plan
        elif current_manifest != manifest_sha or current_plan != plan_sha:
            raise RawContractError(f"shard[{sequence}]:BINDING_HASH_MISMATCH")
        summary = validate_world_shard(value, expected_sequence=sequence)
        record_sha = sha256_bytes(canonical)
        summaries.append(summary)
        sources.append(
            {
                "sequence_index": sequence,
                "world_id": value["world_id"],
                "record_sha256": record_sha,
                "declared_world_complete": value["world_complete"],
                "derived_world_complete": summary.derived_complete,
            }
        )
        previous_canonical_sha = record_sha
    prefix_complete = len(shards) == len(WORLD_ORDER)
    all_worlds_complete = prefix_complete and all(summary.derived_complete for summary in summaries)
    result = {
        "schema": REPRODUCTION_SCHEMA,
        "mission": MISSION,
        "mode": MODE,
        "source_schema": RAW_SCHEMA,
        "phase0_commit": PHASE0_COMMIT,
        "schema_sha256": sha256_bytes(canonical_json_bytes(schema_document)),
        "manifest_sha256": manifest_sha,
        "plan_sha256": plan_sha,
        "world_order": list(WORLD_ORDER),
        "source_records": sources,
        "worlds": [summary.value for summary in summaries],
        "ordered_prefix_complete": prefix_complete,
        "all_worlds_mechanically_complete": all_worlds_complete,
        "mechanical_firewall_pass": True,
        "reproduction_status": "COMPLETE_VALID" if all_worlds_complete else "INCOMPLETE_OR_FAILED",
    }
    assert_outcome_free(result)
    return result


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_schema(path: Path) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink():
        raise RawContractError("SYMLINK_SCHEMA_REFUSED")
    payload = path.read_bytes()
    value = strict_json_loads(payload)
    if not isinstance(value, dict):
        raise RawContractError("SCHEMA_ROOT_NOT_OBJECT")
    canonical = canonical_json_bytes(value)
    validate_schema_document(value)
    return value, canonical


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", required=True, type=Path, help="Exact final raw schema JSON")
    parser.add_argument(
        "--shard",
        required=True,
        action="append",
        type=Path,
        help="Explicit canonical shard in frozen world order; repeat for each shard",
    )
    parser.add_argument("--output", required=True, type=Path, help="Canonical reproduction JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    schema, _schema_bytes = _load_schema(args.schema)
    shards = [read_raw_shard(path) for path in args.shard]
    result = reproduce_shards(shards, schema_document=schema)
    payload = canonical_json_bytes(result)
    atomic_write(args.output, payload)
    print(sha256_bytes(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
