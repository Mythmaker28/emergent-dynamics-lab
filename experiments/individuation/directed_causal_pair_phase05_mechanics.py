"""Outcome-blind mechanical primitives for DIRECTED-CAUSAL-PAIR-00 Phase 0.5.

This module contains passive geometry/tracker instrumentation, manifest guards,
mechanical-output firewall checks, deterministic encoding, and atomic shard
helpers.  It does not build a world, apply a scientific analyzer, or calculate a
feeding endpoint or directed causal contrast.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid
from typing import Any, Iterable, Sequence

import numpy as np

from experiments.individuation import access_structure_operators as ops
from experiments.individuation import bijective_tracker as bt


MISSION = "DIRECTED-CAUSAL-PAIR-00"
PHASE = "PHASE05"
SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-MECHANICAL-v1"
RAW_SHARD_SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-MECHANICAL-SHARD-v1"
INDEX_SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-ORDERED-PREFIX-v1"
PHASE0_COMMIT = "4bcb551092291b7383c4168f653818d4bade14f6"
OPEN_DEV_NAMESPACE = tuple(range(50001, 50011))
FROZEN_PAIR_WORLDS = (50002, 50004, 50005, 50007)
FROZEN_ASSIGNMENTS = {
    50002: {"target_A": 0, "target_B": 2, "sentinel": 1},
    50004: {"target_A": 0, "target_B": 1, "sentinel": 2},
    50005: {"target_A": 1, "target_B": 0, "sentinel": 2},
    50007: {"target_A": 1, "target_B": 0, "sentinel": 2},
}
ARM_ORDER = ("H00", "H10", "H01", "H11")
ARM_BITS = {
    "H00": (0, 0),
    "H10": (1, 0),
    "H01": (0, 1),
    "H11": (1, 1),
}
MIN_SEPARATION = 24.0
CORE_RADIUS = 10
HALO_RADIUS = 12
MIN_COMPONENT_SIZE = 45
COVERAGE_CAP = 0.15
GRID_SIZE = 64

# Exact outcome names forbidden in persisted mechanical objects.  Physical
# simulator field ``c`` is intentionally not forbidden.
FORBIDDEN_OUTCOME_KEYS = frozenset(
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
        "feeding_endpoint",
        "feeding_contrast",
        "uptake",
        "pair_feeding_outcome",
        "integrated_tracked_uptake",
        "integrated_fixed_mask_uptake",
        "scientific_effect",
        "scientific_contrast",
    }
)
FORBIDDEN_ANALYZER_MODULES = (
    "directed_causal_pair_analy",
    "causal_analyze",
    "causal_certificate",
    "nonmerging_confirm",
    "turnover_dev_runner",
    "turnover_analyzer_03g",
    "turnover_statistics_03g",
)
FORBIDDEN_OUTCOME_PREFIXES = (
    "y_",
    "feeding",
    "outcome",
    "contrast",
    "effect",
    "estimand",
    "directed_matrix",
    "analyzer",
)
SEED_58_RE = re.compile(r"(?<!\d)58\d{3}(?!\d)")


def canonical_json_bytes(value: Any) -> bytes:
    """Stable LF-terminated JSON bytes for hashes and exact reproduction."""
    assert_outcome_free(value)
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _walk_items(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, str(key), child
            yield from _walk_items(child, path + (str(key),))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _walk_items(child, path + (str(index),))


def assert_outcome_free(value: Any) -> None:
    violations = []
    for path, key, _child in _walk_items(value):
        folded = key.casefold()
        if (
            folded in FORBIDDEN_OUTCOME_KEYS
            or folded in {"y", "i"}
            or any(folded.startswith(prefix) for prefix in FORBIDDEN_OUTCOME_PREFIXES)
        ):
            violations.append("/".join(path + (key,)))
    if violations:
        raise ValueError(f"OUTCOME FIREWALL: forbidden mechanical keys: {violations}")


def assert_no_forbidden_analyzer_imports() -> None:
    loaded = sorted(
        name for name in sys.modules
        if any(fragment in name.casefold() for fragment in FORBIDDEN_ANALYZER_MODULES)
    )
    if loaded:
        raise RuntimeError(f"OUTCOME FIREWALL: scientific analyzer modules loaded: {loaded}")


def _contains_58_namespace(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, int):
        return 58000 <= value <= 58999
    if isinstance(value, str):
        return bool(SEED_58_RE.search(value))
    if isinstance(value, dict):
        return any(_contains_58_namespace(key) or _contains_58_namespace(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_58_namespace(child) for child in value)
    return False


def validate_dev_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Fail closed unless a manifest names only the already-open four DEV worlds."""
    if _contains_58_namespace(manifest):
        raise ValueError("OUTCOME FIREWALL: 58xxx namespace reference refused")
    if manifest.get("schema") != "DIRECTED-CAUSAL-PAIR-00-PHASE05-DEV-MANIFEST-v1":
        raise ValueError("unsupported Phase-0.5 DEV manifest schema")
    if manifest.get("mission") != MISSION or manifest.get("mode") != "DEV_ONLY_MECHANICAL":
        raise ValueError("manifest mission/mode mismatch")
    if manifest.get("phase0_commit") != PHASE0_COMMIT:
        raise ValueError("manifest is not bound to the accepted Phase-0 commit")
    allowed_raw = manifest.get("allowed_seed_namespace", ())
    requested_raw = manifest.get("worlds", ())
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in allowed_raw):
        raise ValueError("manifest allowed namespace must contain JSON integers only")
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in requested_raw):
        raise ValueError("manifest worlds must contain JSON integers only")
    allowed = tuple(allowed_raw)
    requested = tuple(requested_raw)
    if allowed != OPEN_DEV_NAMESPACE:
        raise ValueError("manifest allowed namespace must be exactly 50001-50010")
    if requested != FROZEN_PAIR_WORLDS:
        raise ValueError("manifest worlds must be exactly the frozen ordered pair-world tuple")
    if len(requested) != len(set(requested)):
        raise ValueError("duplicate DEV worlds are forbidden")
    if manifest.get("prospective_namespace") is not None:
        raise ValueError("prospective namespace must remain null in Phase 0.5")
    assignments = manifest.get("pair_assignments")
    expected_assignments = {
        str(world): dict(values) for world, values in FROZEN_ASSIGNMENTS.items()
    }
    if assignments != expected_assignments:
        raise ValueError("manifest pair assignments do not match the frozen Phase-0 choices")
    assert_outcome_free(manifest)
    return manifest


def safe_read_json(path: Path, allowed_paths: Iterable[Path]) -> Any:
    resolved = path.resolve()
    allowed = {candidate.resolve() for candidate in allowed_paths}
    if resolved not in allowed:
        raise PermissionError(f"read refused outside explicit Phase-0.5 inputs: {resolved}")
    if _contains_58_namespace(str(resolved)):
        raise PermissionError("58xxx path refused")
    return json.loads(resolved.read_text(encoding="utf-8"))


def periodic_centroid(mask: np.ndarray) -> tuple[float, float]:
    """Centroid of a compact mask on a periodic 2-D grid via circular means."""
    if mask.ndim != 2 or mask.dtype != np.bool_ or not mask.any():
        raise ValueError("periodic_centroid requires a nonempty 2-D boolean mask")
    coords = np.where(mask)
    result = []
    for axis, values in enumerate(coords):
        size = mask.shape[axis]
        angles = 2.0 * np.pi * values.astype(float) / float(size)
        z = np.exp(1j * angles).mean()
        if abs(z) <= 1e-12:
            raise ValueError("periodic centroid undefined for a non-compact circular support")
        angle = math.atan2(float(z.imag), float(z.real)) % (2.0 * math.pi)
        result.append(float(angle * size / (2.0 * math.pi)))
    return (result[0], result[1])


def toroidal_distance(a: Sequence[float], b: Sequence[float], shape: Sequence[int] = (GRID_SIZE, GRID_SIZE)) -> float:
    delta = []
    for left, right, size in zip(a, b, shape):
        raw = abs(float(left) - float(right))
        delta.append(min(raw, float(size) - raw))
    return float(math.hypot(*delta))


def disk_mask(shape: tuple[int, int], center: Sequence[float], radius: float) -> np.ndarray:
    return ops.periodic_distance(shape, center) <= float(radius)


def masks_contact_four_neighbour(left: np.ndarray, right: np.ndarray) -> bool:
    if (left & right).any():
        return True
    expanded = left.copy()
    for axis in (0, 1):
        expanded |= np.roll(left, 1, axis=axis)
        expanded |= np.roll(left, -1, axis=axis)
    return bool((expanded & right).any())


def pair_geometry(mask_a: np.ndarray, mask_b: np.ndarray) -> dict[str, Any]:
    if mask_a.shape != mask_b.shape:
        raise ValueError("pair masks must share a grid")
    centroid_a = periodic_centroid(mask_a)
    centroid_b = periodic_centroid(mask_b)
    distance = toroidal_distance(centroid_a, centroid_b, mask_a.shape)
    core_a = disk_mask(mask_a.shape, centroid_a, CORE_RADIUS)
    core_b = disk_mask(mask_b.shape, centroid_b, CORE_RADIUS)
    halo_a = disk_mask(mask_a.shape, centroid_a, HALO_RADIUS)
    halo_b = disk_mask(mask_b.shape, centroid_b, HALO_RADIUS)
    core_overlap = int(np.count_nonzero(core_a & core_b))
    halo_overlap = int(np.count_nonzero(halo_a & halo_b))
    return {
        "centroid_A": [float(value) for value in centroid_a],
        "centroid_B": [float(value) for value in centroid_b],
        "distance": float(distance),
        "core_overlap_cells": core_overlap,
        "halo_overlap_cells": halo_overlap,
        "minimum_core_gap": float(distance - 2.0 * CORE_RADIUS),
        "minimum_halo_gap": float(distance - 2.0 * HALO_RADIUS),
        "body_contact": masks_contact_four_neighbour(mask_a, mask_b),
        "body_overlap_cells": int(np.count_nonzero(mask_a & mask_b)),
    }


def _mask_overlap(source: np.ndarray, candidate: np.ndarray) -> float:
    denominator = int(np.count_nonzero(source))
    return float(np.count_nonzero(source & candidate) / denominator) if denominator else 0.0


def _state_is_finite(state) -> bool:
    return all(bool(np.isfinite(getattr(state, field)).all()) for field in ops.STATE_FIELDS)


def _component_id_for_mask(mask: np.ndarray, components: list[np.ndarray]) -> int | None:
    for index, component in enumerate(components):
        if np.array_equal(mask, component):
            return int(index)
    return None


def packed_mask(mask: np.ndarray) -> dict[str, Any]:
    """Canonical row-major little-bitorder encoding for engine-free checking."""
    if mask.ndim != 2 or mask.dtype != np.bool_:
        raise ValueError("packed masks must be two-dimensional boolean arrays")
    payload = np.packbits(np.ascontiguousarray(mask).reshape(-1), bitorder="little").tobytes()
    return {
        "encoding": "PACKED_BITS_BASE64_V1",
        "shape": [int(mask.shape[0]), int(mask.shape[1])],
        "bitorder": "little",
        "data_base64": base64.b64encode(payload).decode("ascii"),
        "sha256": sha256_bytes(payload),
    }


@dataclass(frozen=True)
class PairAssignment:
    target_A: int
    target_B: int
    sentinel: int

    def validate(self) -> None:
        values = (int(self.target_A), int(self.target_B), int(self.sentinel))
        if sorted(values) != [0, 1, 2]:
            raise ValueError("A, B, and sentinel must be a permutation of target indices 0,1,2")


class PassivePairObserver:
    """External observer that never mutates the simulator state.

    The tracker is external measurement state.  Every candidate association edge
    and its individual terms are emitted before the frozen tracker update.
    """

    def __init__(self, seed_masks: list[np.ndarray], assignment: PairAssignment, *, theta: float = 0.10,
                 split_frac: float = 0.30, ambiguity_margin: float = 0.05):
        if len(seed_masks) != 3:
            raise ValueError("exactly three frozen targets are required")
        assignment.validate()
        self.assignment = assignment
        self.tracker = bt.BijectiveTracker(theta=theta, split_frac=split_frac, ambiguity_margin=ambiguity_margin)
        self.tracker.seed([mask.copy() for mask in seed_masks], 0)
        self.initial_mask_hashes = [sha256_bytes(np.ascontiguousarray(mask).tobytes()) for mask in seed_masks]
        self._last_component_ids = {index: None for index in range(3)}

    def _snapshot(self, state, component_masks: list[np.ndarray], *, step: int, stage: str,
                  advance_tracker: bool, collar: np.ndarray | None = None,
                  clamp_recipient: str | None = None) -> dict[str, Any]:
        state_before = ops.state_sha256(state)
        prior_masks = [track.mask.copy() for track in self.tracker.tracks]
        prior_statuses = [track.status for track in self.tracker.tracks]
        component_centroids = [periodic_centroid(mask) for mask in component_masks]
        component_sizes = [int(np.count_nonzero(mask)) for mask in component_masks]

        edges = []
        edge_lookup: dict[tuple[int, int], dict[str, Any]] = {}
        for track_id, (prior, status) in enumerate(zip(prior_masks, prior_statuses)):
            if status != bt.ALIVE:
                continue
            prior_centroid = periodic_centroid(prior)
            prior_size = max(1, int(np.count_nonzero(prior)))
            overlaps = [_mask_overlap(prior, component) for component in component_masks]
            ranked = sorted(range(len(component_masks)), key=lambda index: (-overlaps[index], index))
            ranks = {component_id: rank for rank, component_id in enumerate(ranked)}
            for component_id, component in enumerate(component_masks):
                overlap = overlaps[component_id]
                row = {
                    "tracker_id": int(track_id),
                    "component_id": int(component_id),
                    "overlap": float(overlap),
                    "centroid_distance": toroidal_distance(prior_centroid, component_centroids[component_id], prior.shape),
                    "size_ratio": float(component_sizes[component_id] / prior_size),
                    "theta_gate": bool(overlap >= self.tracker.theta),
                    "split_gate": bool(overlap >= self.tracker.split_frac),
                    "compatible": bool(overlap >= self.tracker.theta),
                    "assignment_cost": float(-overlap),
                    "rank": int(ranks[component_id]),
                    "selected": False,
                }
                edges.append(row)
                edge_lookup[(track_id, component_id)] = row

        events = self.tracker.update(component_masks, step) if advance_tracker else {}
        assigned_component_ids = []
        for track_id, track in enumerate(self.tracker.tracks):
            component_id = _component_id_for_mask(track.mask, component_masks) if track.status == bt.ALIVE else None
            assigned_component_ids.append(component_id)
            if component_id is not None and (track_id, component_id) in edge_lookup:
                edge_lookup[(track_id, component_id)]["selected"] = True

        track_rows = []
        for track_id, track in enumerate(self.tracker.tracks):
            component_id = assigned_component_ids[track_id]
            mask = track.mask
            if track.status == bt.ALIVE and component_id is not None:
                centroid = periodic_centroid(mask)
                core = disk_mask(mask.shape, centroid, CORE_RADIUS)
                halo = disk_mask(mask.shape, centroid, HALO_RADIUS)
                body_cells = int(np.count_nonzero(mask))
                inside = int(np.count_nonzero(mask & core))
                body_core_coverage = float(inside / body_cells) if body_cells else 0.0
            else:
                centroid = None
                body_cells = 0
                body_core_coverage = 0.0
                core = np.zeros(state.rho.shape, dtype=bool)
                halo = np.zeros(state.rho.shape, dtype=bool)
            track_rows.append(
                {
                    "tracker_id": int(track_id),
                    "status": str(track.status),
                    "component_id": component_id,
                    "component_size": body_cells,
                    "centroid": ([float(value) for value in centroid] if centroid is not None else None),
                    "body_core_coverage": body_core_coverage,
                    "body_mask": packed_mask(mask if track.status == bt.ALIVE else np.zeros(state.rho.shape, dtype=bool)),
                    "core_mask": packed_mask(core),
                    "halo_mask": packed_mask(halo),
                }
            )

        a = self.assignment.target_A
        b = self.assignment.target_B
        s = self.assignment.sentinel
        mask_a = self.tracker.tracks[a].mask if self.tracker.tracks[a].status == bt.ALIVE else None
        mask_b = self.tracker.tracks[b].mask if self.tracker.tracks[b].status == bt.ALIVE else None
        geometry = pair_geometry(mask_a, mask_b) if mask_a is not None and mask_b is not None else None

        component_switch = False
        if advance_tracker and mask_a is not None and mask_b is not None:
            cid_a = assigned_component_ids[a]
            cid_b = assigned_component_ids[b]
            if cid_a is not None:
                component_switch |= _mask_overlap(prior_masks[b], component_masks[cid_a]) > _mask_overlap(prior_masks[a], component_masks[cid_a])
            if cid_b is not None:
                component_switch |= _mask_overlap(prior_masks[a], component_masks[cid_b]) > _mask_overlap(prior_masks[b], component_masks[cid_b])

        collar_diagnostics = None
        if collar is not None:
            if clamp_recipient not in ("A", "B"):
                raise ValueError("collar context requires clamp_recipient A or B")
            recipient_index = a if clamp_recipient == "A" else b
            partner_index = b if clamp_recipient == "A" else a
            recipient_mask = self.tracker.tracks[recipient_index].mask if self.tracker.tracks[recipient_index].status == bt.ALIVE else None
            partner_mask = self.tracker.tracks[partner_index].mask if self.tracker.tracks[partner_index].status == bt.ALIVE else None
            wrong_masks = [
                self.tracker.tracks[index].mask
                for index in range(3)
                if index != recipient_index and self.tracker.tracks[index].status == bt.ALIVE
            ]
            wrong_core_overlap = 0
            for wrong_mask in wrong_masks:
                wrong_center = periodic_centroid(wrong_mask)
                wrong_core_overlap += int(np.count_nonzero(collar & disk_mask(collar.shape, wrong_center, CORE_RADIUS)))
            recipient_core_overlap = 0
            if recipient_mask is not None:
                recipient_center = periodic_centroid(recipient_mask)
                recipient_core_overlap = int(
                    np.count_nonzero(collar & disk_mask(collar.shape, recipient_center, CORE_RADIUS))
                )
            collar_diagnostics = {
                "recipient": clamp_recipient,
                "recipient_body_intersection_cells": int(np.count_nonzero(collar & recipient_mask)) if recipient_mask is not None else 0,
                "partner_body_intersection_cells": int(np.count_nonzero(collar & partner_mask)) if partner_mask is not None else 0,
                "recipient_core_intersection_cells": recipient_core_overlap,
                "wrong_core_intersection_cells": int(wrong_core_overlap),
            }

        largest_coverage = float(max(component_sizes, default=0) / state.rho.size)
        reasons: list[str] = []
        if not _state_is_finite(state):
            reasons.append("NONFINITE_STATE")
        if events:
            reasons.extend(f"TRACKER_{status}_T{track_id}" for track_id, status in sorted(events.items()))
        if any(track.status != bt.ALIVE for track in self.tracker.tracks):
            reasons.append("TARGET_OR_SENTINEL_NOT_ALIVE")
        if any(row["component_size"] < MIN_COMPONENT_SIZE for row in track_rows):
            reasons.append("TARGET_OR_SENTINEL_BELOW_MIN_SIZE")
        if largest_coverage >= COVERAGE_CAP:
            reasons.append("GIANT_COMPONENT_COVERAGE")
        if geometry is None:
            reasons.append("PAIR_GEOMETRY_UNAVAILABLE")
        else:
            if geometry["distance"] < MIN_SEPARATION:
                reasons.append("PAIR_DISTANCE_BELOW_24")
            if geometry["halo_overlap_cells"] > 0:
                reasons.append("RADIUS12_HALO_OVERLAP")
            if geometry["body_contact"]:
                reasons.append("PAIR_BODY_CONTACT")
        if component_switch:
            reasons.append("PAIR_IDENTITY_SWITCH")
        if collar_diagnostics is not None:
            if collar_diagnostics["recipient_core_intersection_cells"] > 0:
                reasons.append("CLAMP_COLLAR_RECIPIENT_CORE_INTERSECTION")
            if collar_diagnostics["recipient_body_intersection_cells"] > 0:
                reasons.append("CLAMP_COLLAR_RECIPIENT_BODY_INTERSECTION")
            if collar_diagnostics["partner_body_intersection_cells"] > 0:
                reasons.append("CLAMP_COLLAR_PARTNER_INTRUSION")
            if collar_diagnostics["wrong_core_intersection_cells"] > 0:
                reasons.append("CLAMP_COLLAR_WRONG_CORE_INTERSECTION")

        state_after = ops.state_sha256(state)
        if state_before != state_after:
            raise AssertionError("passive logger mutated simulator state")
        record = {
            "stage": str(stage),
            "stage_step": int(step),
            "engine_step": int(state.step),
            "assignment": {
                "A_target_index": int(a),
                "B_target_index": int(b),
                "sentinel_target_index": int(s),
                "pair_order": ["A", "B"],
            },
            "components": [
                {"component_id": int(index), "size": component_sizes[index],
                 "centroid": [float(value) for value in component_centroids[index]],
                 "mask": packed_mask(component_masks[index])}
                for index in range(len(component_masks))
            ],
            "association_edges": edges,
            "tracks": track_rows,
            "events": {str(key): str(value) for key, value in sorted(events.items())},
            "pair_geometry": geometry,
            "component_switch": bool(component_switch),
            "largest_component_coverage": largest_coverage,
            "collar": collar_diagnostics,
            "sentinel_valid": bool(track_rows[s]["status"] == bt.ALIVE and track_rows[s]["component_size"] >= MIN_COMPONENT_SIZE),
            "state_finite": bool(_state_is_finite(state)),
            "logger_state_unchanged": bool(state_before == state_after),
            "state_sha256": state_before,
            "material_retention": None,
            "deep_material_gate": None,
            "masks": {
                "A": packed_mask(mask_a if mask_a is not None else np.zeros(state.rho.shape, dtype=bool)),
                "B": packed_mask(mask_b if mask_b is not None else np.zeros(state.rho.shape, dtype=bool)),
                "SENTINEL": packed_mask(
                    self.tracker.tracks[s].mask
                    if self.tracker.tracks[s].status == bt.ALIVE
                    else np.zeros(state.rho.shape, dtype=bool)
                ),
                "core_A": packed_mask(
                    disk_mask(mask_a.shape, periodic_centroid(mask_a), CORE_RADIUS)
                    if mask_a is not None else np.zeros(state.rho.shape, dtype=bool)
                ),
                "core_B": packed_mask(
                    disk_mask(mask_b.shape, periodic_centroid(mask_b), CORE_RADIUS)
                    if mask_b is not None else np.zeros(state.rho.shape, dtype=bool)
                ),
                "halo_A": packed_mask(
                    disk_mask(mask_a.shape, periodic_centroid(mask_a), HALO_RADIUS)
                    if mask_a is not None else np.zeros(state.rho.shape, dtype=bool)
                ),
                "halo_B": packed_mask(
                    disk_mask(mask_b.shape, periodic_centroid(mask_b), HALO_RADIUS)
                    if mask_b is not None else np.zeros(state.rho.shape, dtype=bool)
                ),
                "collar": packed_mask(collar if collar is not None else np.zeros(state.rho.shape, dtype=bool)),
            },
            "kill_reasons": sorted(set(reasons)),
        }
        assert_outcome_free(record)
        return record

    def seed_snapshot(self, state, component_masks: list[np.ndarray], *, stage: str = "PREWRITER") -> dict[str, Any]:
        return self._snapshot(state, component_masks, step=0, stage=stage, advance_tracker=False)

    def advance(self, state, component_masks: list[np.ndarray], *, step: int, stage: str,
                collar: np.ndarray | None = None, clamp_recipient: str | None = None) -> dict[str, Any]:
        return self._snapshot(
            state,
            component_masks,
            step=step,
            stage=stage,
            advance_tracker=True,
            collar=collar,
            clamp_recipient=clamp_recipient,
        )


def mechanical_trace_sha256(records: list[dict[str, Any]]) -> str:
    return sha256_bytes(canonical_json_bytes(records))


def deterministic_gzip(payload: bytes) -> bytes:
    return gzip.compress(payload, compresslevel=9, mtime=0)


def decode_gzip_json(payload: bytes) -> Any:
    return json.loads(gzip.decompress(payload).decode("utf-8"))


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Publish one explicit file atomically; no directory scanning or broad deletion."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value))


def validate_ordered_prefix(index: dict[str, Any], plan: Sequence[int], root: Path) -> None:
    if index.get("schema") != INDEX_SCHEMA:
        raise ValueError("ordered-prefix index schema mismatch")
    frozen_plan = list(plan)
    if index.get("plan") != frozen_plan:
        raise ValueError("ordered-prefix index declared plan mismatch")
    completed = index.get("completed", [])
    if not isinstance(completed, list) or len(completed) > len(frozen_plan):
        raise ValueError("ordered-prefix completed rows are malformed")
    completed_worlds = []
    resolved_root = root.resolve(strict=True)
    seen_paths: set[Path] = set()
    for sequence_index, row in enumerate(completed):
        if not isinstance(row, dict):
            raise ValueError("ordered-prefix row must be an object")
        world = row.get("world_id")
        if isinstance(world, bool) or not isinstance(world, int):
            raise ValueError("ordered-prefix world identity must be an integer")
        if row.get("sequence_index") != sequence_index:
            raise ValueError("ordered-prefix sequence index mismatch")
        completed_worlds.append(world)
    if completed_worlds != frozen_plan[:len(completed_worlds)]:
        raise ValueError("completed mechanical shards are not an exact ordered prefix")
    for row in completed:
        relative = row.get("path")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError("completed shard path must be a nonempty relative string")
        path = (resolved_root / relative).resolve(strict=False)
        try:
            path.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(f"completed shard path escapes the raw root: {relative}") from exc
        if path in seen_paths:
            raise ValueError("duplicate completed shard path")
        seen_paths.add(path)
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing completed shard: {path}")
        if path.stat().st_size != int(row["size_bytes"]):
            raise ValueError(f"completed shard size mismatch: {path}")
        if sha256_file(path) != row["sha256"]:
            raise ValueError(f"completed shard hash mismatch: {path}")


def new_ordered_prefix_index(manifest_sha256: str) -> dict[str, Any]:
    return {
        "schema": INDEX_SCHEMA,
        "mission": MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "manifest_sha256": manifest_sha256,
        "plan": list(FROZEN_PAIR_WORLDS),
        "completed": [],
        "complete": False,
    }
