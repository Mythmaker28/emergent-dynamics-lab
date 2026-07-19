"""Raw-only Stage-B developmental autopsy.

This module is intentionally engine-free.  Its only scientific inputs are the
three frozen JSON records and the 64 allowlisted physics NPZ archives declared
by the committed analysis plan.  Importing this file performs no I/O.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pytest


CLASSES = (
    "EMPTY_OR_GAS",
    "STATIC_CRYSTAL_OR_SHELL",
    "PERCOLATED",
    "DISSOLVED",
    "ACTIVE_UNBOUNDED",
    "PERSISTENT_NO_TURNOVER",
    "TURNOVER_WITHOUT_PERSISTENCE",
    "TRACKING_UNRESOLVED",
    "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
)
EVENT_ORDER = {
    name: index
    for index, name in enumerate(
        (
            "ASSOCIATION_DIAGNOSTICS",
            "APPEARANCE",
            "CONTINUATION",
            "DISSOLUTION",
            "MERGE",
            "SPLIT",
            "TEMPORARY_CONTACT",
            "TRACKING_UNRESOLVED",
        )
    )
}
PATHWAY_ORDER = {
    "ACTIVATION_FAILURE": 0,
    "TURNOVER_FAILURE": 1,
    "PERSISTENCE_FAILURE": 2,
    "TRANSIENT_CANDIDATE_CROSSING": 3,
    "STABLE_CANDIDATE_EPISODE": 4,
}
AUTOPSY_OUTCOMES = (
    "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS",
    "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES",
    "RAW_INSUFFICIENT",
    "AUDIT_INVALID",
)

PLAN_RELATIVE = "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_ANALYSIS_PLAN.json"
ALLOWLIST_RELATIVE = "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_SOURCE_ALLOWLIST.json"
PRIMARY_ROOT_RELATIVE = "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY/primary"
INDEPENDENT_ROOT_RELATIVE = "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY/independent"
QUALIFICATION_RELATIVE = "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY/QUALIFICATION.json"


class AuditError(RuntimeError):
    """A binding, layout, numerical, or reconstruction audit failure."""


def _normalize_floats(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _normalize_floats(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_floats(v) for v in value]
    if isinstance(value, np.generic):
        return _normalize_floats(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            raise AuditError("nonfinite value cannot be serialized")
        return 0.0 if value == 0.0 else value
    return value


def canonical_json_bytes(value: Any) -> bytes:
    normalized = _normalize_floats(value)
    text = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(dict(row)) for row in rows)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_oid_bytes(data: bytes) -> str:
    digest = hashlib.sha1()
    digest.update(f"blob {len(data)}\0".encode("ascii"))
    digest.update(data)
    return digest.hexdigest()


def _repo_relative(repo: Path, path: Path) -> str:
    try:
        rel = path.resolve(strict=True).relative_to(repo.resolve(strict=True))
    except (ValueError, FileNotFoundError) as exc:
        raise AuditError(f"path escapes repository: {path}") from exc
    return rel.as_posix()


def _has_reparse_or_symlink(repo: Path, path: Path) -> bool:
    current = path
    root = repo.resolve(strict=True)
    while True:
        stat = os.lstat(current)
        if os.path.islink(current):
            return True
        if getattr(stat, "st_file_attributes", 0) & 0x400:
            return True
        if current.resolve(strict=False) == root:
            return False
        if current.parent == current:
            return True
        current = current.parent


def normalize_allowlist_path(path: str) -> str:
    candidate = path.replace("\\", "/")
    if candidate.startswith("/") or ":" in candidate:
        raise AuditError(f"absolute allowlist path: {path}")
    parts = candidate.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise AuditError(f"unsafe allowlist path: {path}")
    return "/".join(parts).casefold()


def read_allowed_bytes(repo: Path, relative: str, allowed: set[str]) -> bytes:
    normalized = normalize_allowlist_path(relative)
    if normalized not in allowed:
        raise AuditError(f"source firewall rejected {relative}")
    path = repo / relative
    if _has_reparse_or_symlink(repo, path):
        raise AuditError(f"reparse/symlink rejected {relative}")
    if _repo_relative(repo, path).casefold() != normalized:
        raise AuditError(f"resolved path mismatch {relative}")
    return path.read_bytes()


def read_allowed_json(repo: Path, relative: str, allowed: set[str]) -> Any:
    try:
        return json.loads(read_allowed_bytes(repo, relative, allowed).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid JSON {relative}") from exc


def expected_inventory(protocol: Mapping[str, Any]) -> dict[str, tuple[np.dtype[Any], tuple[int, ...]]]:
    raw = protocol["exact_raw_inventory"]
    inventory: dict[str, tuple[np.dtype[Any], tuple[int, ...]]] = {}
    for key, spec in raw["state_and_validation"].items():
        inventory[key] = (np.dtype(spec["dtype"]), tuple(spec["shape"]))
    for key, spec in raw["cell_ledger"].items():
        inventory[key] = (np.dtype(spec["dtype"]), tuple(spec["shape"]))
    for key in raw["face_ledger_float64_shape_160_2_12_12"]:
        inventory[key] = (np.dtype("float64"), (160, 2, 12, 12))
    for key in raw["scalar_ledger_float64_shape_160"]:
        inventory[key] = (np.dtype("float64"), (160,))
    if len(inventory) != 46:
        raise AuditError(f"protocol inventory has {len(inventory)} keys")
    return inventory


def safe_load_npz(path: Path | bytes, protocol: Mapping[str, Any]) -> dict[str, np.ndarray[Any, Any]]:
    inventory = expected_inventory(protocol)
    expected_members = {f"{key}.npy" for key in inventory}
    data = path if isinstance(path, bytes) else path.read_bytes()
    label = "<authenticated-bytes>" if isinstance(path, bytes) else str(path)
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        names = [info.filename for info in archive.infolist()]
        if len(names) != len(set(names)):
            raise AuditError(f"duplicate ZIP member in {label}")
        for name in names:
            if (
                name.endswith("/")
                or "/" in name
                or "\\" in name
                or ":" in name
                or name.startswith(("/", "\\"))
                or Path(name).is_absolute()
                or any(part in ("", ".", "..") for part in name.replace("\\", "/").split("/"))
            ):
                raise AuditError(f"unsafe ZIP member {name!r}")
        if set(names) != expected_members or len(names) != len(expected_members):
            raise AuditError(f"NPZ member inventory mismatch {label}")
    arrays: dict[str, np.ndarray[Any, Any]] = {}
    with np.load(io.BytesIO(data), allow_pickle=False) as loaded:
        if set(loaded.files) != set(inventory) or len(loaded.files) != len(inventory):
            raise AuditError(f"NumPy inventory mismatch {label}")
        for key, (dtype, shape) in inventory.items():
            try:
                array = loaded[key]
            except ValueError as exc:
                raise AuditError(f"unsafe NumPy payload for {key}") from exc
            if array.dtype.fields is not None or array.dtype.subdtype is not None or array.dtype.hasobject:
                raise AuditError(f"unsafe dtype for {key}")
            if not array.dtype.isnative or array.dtype != dtype or array.shape != shape:
                raise AuditError(f"layout mismatch for {key}: {array.dtype} {array.shape}")
            arrays[key] = np.array(array, copy=True)
    return arrays


def validate_raw_arrays(arrays: Mapping[str, np.ndarray[Any, Any]], dt: float = 0.05) -> dict[str, float]:
    for key, array in arrays.items():
        if key == "deterministic_replay_equal":
            continue
        if not np.all(np.isfinite(array)):
            raise AuditError(f"nonfinite {key}")
    if not np.array_equal(arrays["state_step"], np.arange(161, dtype=np.int64)):
        raise AuditError("state_step mismatch")
    bound = 1.0 + 1e-12 + 1e-10
    for key in ("state_m", "state_n", "state_b"):
        value = arrays[key]
        if np.any(value < 0.0) or np.any(value > bound):
            raise AuditError(f"state bounds failed {key}")
    if not np.array_equal(arrays["deterministic_replay_equal"], np.ones(160, dtype=np.uint8)):
        raise AuditError("deterministic replay mismatch")
    for key in ("ledger__matter_scale", "ledger__resource_scale"):
        if not np.array_equal(arrays[key], np.ones_like(arrays[key])):
            raise AuditError(f"neutral scale mismatch {key}")
    for key in (
        "ledger__matter_missing",
        "ledger__resource_missing",
        "ledger__matter_missing_from_delta",
        "ledger__matter_missing_to_delta",
        "ledger__resource_missing_from_delta",
        "ledger__resource_missing_to_delta",
        "ledger__controller_onset_energy_jump",
    ):
        if not np.array_equal(arrays[key], np.zeros_like(arrays[key])):
            raise AuditError(f"exact-zero mismatch {key}")
    for key in (
        "ledger__matter_forward",
        "ledger__matter_reverse",
        "ledger__gross_formation",
        "ledger__gross_rupture",
        "ledger__gross_formation_work",
        "ledger__gross_rupture_release",
    ):
        if np.any(arrays[key] < 0.0):
            raise AuditError(f"negative gross ledger {key}")
    maximum_scale = 1.0
    for key in ("state_m", "state_n", "state_b"):
        maximum_scale = max(maximum_scale, float(np.max(np.abs(arrays[key]))))
    for key in sorted(k for k in arrays if k.startswith("ledger__")):
        maximum_scale = max(maximum_scale, float(np.max(np.abs(arrays[key]))))
    errors = arrays["vector_reference_max_error"]
    if np.any(errors < 0.0) or np.any(errors > 1e-12 + 1e-10 * maximum_scale):
        raise AuditError("vector/reference gate failed")
    m = arrays["state_m"]
    forward = arrays["ledger__matter_forward"]
    reverse = arrays["ledger__matter_reverse"]
    max_transport_error = 0.0
    max_matter_residual = 0.0
    max_energy_residual = 0.0
    for step in range(160):
        net = forward[step] - reverse[step]
        divergence = (net[0] - np.roll(net[0], 1, axis=0)) + (net[1] - np.roll(net[1], 1, axis=1))
        expected = m[step] - dt * divergence
        difference = np.abs(m[step + 1] - expected)
        if np.any(difference > 1e-12 + 1e-10 * np.abs(expected)):
            raise AuditError(f"matter transport identity failed at {step}")
        max_transport_error = max(max_transport_error, float(np.max(difference)))
        expected_initial = math.fsum(float(x) for x in m[step].flat)
        expected_final = math.fsum(float(x) for x in m[step + 1].flat)
        for key, expected_scalar in (
            ("ledger__initial_matter", expected_initial),
            ("ledger__final_matter", expected_final),
        ):
            stored = float(arrays[key][step])
            if abs(stored - expected_scalar) > 1e-12 + 1e-10 * abs(expected_scalar):
                raise AuditError(f"{key} mismatch at {step}")
        matter_residual = abs(float(arrays["ledger__matter_residual"][step]))
        if matter_residual > 1e-12 + 1e-10 * abs(expected_final):
            raise AuditError(f"matter residual failed at {step}")
        max_matter_residual = max(max_matter_residual, matter_residual)
        initial_energy = float(arrays["ledger__initial_stored_energy"][step])
        energy_residual = abs(float(arrays["ledger__energy_residual"][step]))
        if energy_residual > 1e-12 + 1e-10 * abs(initial_energy):
            raise AuditError(f"energy residual failed at {step}")
        max_energy_residual = max(max_energy_residual, energy_residual)
    return {
        "maximum_scale": maximum_scale,
        "maximum_reference_error": float(np.max(errors)),
        "maximum_transport_error": max_transport_error,
        "maximum_matter_residual": max_matter_residual,
        "maximum_energy_residual": max_energy_residual,
    }


@dataclass(frozen=True)
class Component:
    frame: int
    index: int
    cells: tuple[int, ...]
    lifts: tuple[tuple[int, int, int], ...]
    area: int
    mass: float
    lifted_centroid: tuple[float, float]
    centroid: tuple[float, float]
    radius_gyration: float
    wraps_y: bool
    wraps_x: bool
    mask: np.ndarray[Any, Any] = field(compare=False, repr=False)

    @property
    def percolates(self) -> bool:
        return self.wraps_y or self.wraps_x

    @property
    def key(self) -> tuple[int, int]:
        return (self.frame, self.index)


def detect_components(
    matter: np.ndarray[Any, Any],
    frame: int = 0,
    threshold: float = 0.5,
    min_cells: int = 3,
) -> list[Component]:
    if matter.shape != (12, 12) or matter.dtype != np.float64 or not np.all(np.isfinite(matter)):
        raise AuditError("invalid detector matter")
    occupied = matter >= threshold
    unseen = {int(i) for i in np.flatnonzero(occupied.ravel(order="C"))}
    raw: list[tuple[tuple[int, ...], dict[int, tuple[int, int]], bool, bool]] = []
    neighbours = ((-1, 0), (1, 0), (0, -1), (0, 1))
    while unseen:
        root = min(unseen)
        root_y, root_x = divmod(root, 12)
        lifts: dict[int, tuple[int, int]] = {root: (root_y, root_x)}
        stack = [root]
        accepted: set[int] = set()
        wraps_y = False
        wraps_x = False
        while stack:
            cell = stack.pop()
            if cell in accepted:
                continue
            accepted.add(cell)
            y, x = divmod(cell, 12)
            ly, lx = lifts[cell]
            for dy, dx in neighbours:
                ny, nx = (y + dy) % 12, (x + dx) % 12
                neighbour = ny * 12 + nx
                if not occupied[ny, nx]:
                    continue
                proposed = (ly + dy, lx + dx)
                if neighbour in lifts:
                    stored = lifts[neighbour]
                    wraps_y = wraps_y or proposed[0] != stored[0]
                    wraps_x = wraps_x or proposed[1] != stored[1]
                else:
                    lifts[neighbour] = proposed
                    stack.append(neighbour)
        unseen.difference_update(accepted)
        if len(accepted) >= min_cells:
            raw.append((tuple(sorted(accepted)), lifts, wraps_y, wraps_x))
    raw.sort(key=lambda row: row[0][0])
    components: list[Component] = []
    for index, (cells, lifts, wraps_y, wraps_x) in enumerate(raw):
        weights = np.asarray([matter[divmod(cell, 12)] for cell in cells], dtype=np.float64)
        lifted = np.asarray([lifts[cell] for cell in cells], dtype=np.float64)
        mass = math.fsum(float(value) for value in weights)
        lifted_centroid_array = np.sum(lifted * weights[:, None], axis=0) / mass
        deviations = lifted - lifted_centroid_array
        squared = np.sum(deviations * deviations, axis=1)
        radius = math.sqrt(float(np.sum(squared * weights)) / mass)
        mask = np.zeros((12, 12), dtype=np.bool_)
        for cell in cells:
            mask[divmod(cell, 12)] = True
        components.append(
            Component(
                frame=frame,
                index=index,
                cells=cells,
                lifts=tuple((cell, lifts[cell][0], lifts[cell][1]) for cell in cells),
                area=len(cells),
                mass=mass,
                lifted_centroid=(float(lifted_centroid_array[0]), float(lifted_centroid_array[1])),
                centroid=(float(lifted_centroid_array[0] % 12), float(lifted_centroid_array[1] % 12)),
                radius_gyration=radius,
                wraps_y=wraps_y,
                wraps_x=wraps_x,
                mask=mask,
            )
        )
    return components


def _iou(left: np.ndarray[Any, Any], right: np.ndarray[Any, Any]) -> float:
    intersection = int(np.count_nonzero(left & right))
    union = int(np.count_nonzero(left | right))
    return float(intersection / union) if union else 0.0


def _dilate(mask: np.ndarray[Any, Any], radius: int) -> np.ndarray[Any, Any]:
    result = np.array(mask, copy=True)
    frontier = np.array(mask, copy=True)
    for _ in range(radius):
        frontier = (
            np.roll(frontier, 1, axis=0)
            | np.roll(frontier, -1, axis=0)
            | np.roll(frontier, 1, axis=1)
            | np.roll(frontier, -1, axis=1)
        )
        result |= frontier
    return result


def _periodic_distance(left: Sequence[float], right: Sequence[float]) -> float:
    differences: list[float] = []
    for a, b in zip(left, right, strict=True):
        raw = float(b - a)
        differences.append(min(abs(raw), abs(raw - 12.0), abs(raw + 12.0)))
    return math.hypot(differences[0], differences[1])


def associate_components(
    sources: Sequence[Component],
    targets: Sequence[Component],
    dilation_radius: int = 1,
    max_centroid_displacement: float = 2.5,
    max_area_ratio: float = 3.0,
    unique_score_margin: float = 1e-12,
) -> dict[str, Any]:
    edges: list[dict[str, Any]] = []
    for source in sources:
        for target in targets:
            raw_iou = _iou(source.mask, target.mask)
            dilated_iou = _iou(_dilate(source.mask, dilation_radius), _dilate(target.mask, dilation_radius))
            distance = _periodic_distance(source.centroid, target.centroid)
            area_ratio = max(source.area, target.area) / min(source.area, target.area)
            score = (
                4.0 * raw_iou
                + 2.0 * dilated_iou
                + math.exp(-distance / max_centroid_displacement)
                + min(source.area, target.area) / max(source.area, target.area)
            )
            if area_ratio > max_area_ratio:
                qualified, reason = False, "AREA_RATIO"
            elif distance > max_centroid_displacement:
                qualified, reason = False, "CENTROID_DISTANCE"
            elif raw_iou == 0.0 and dilated_iou == 0.0:
                qualified, reason = False, "NO_SUPPORT_OVERLAP"
            else:
                qualified, reason = True, "QUALIFIED"
            edges.append(
                {
                    "source_key": [source.frame, source.index],
                    "target_key": [target.frame, target.index],
                    "raw_iou": raw_iou,
                    "dilated_iou": dilated_iou,
                    "centroid_distance": distance,
                    "area_ratio": area_ratio,
                    "score": score,
                    "qualified": qualified,
                    "qualification_reason": reason,
                    "selected": False,
                    "ambiguity_bearing": False,
                }
            )
    raw_selected = {
        (edge["source_key"][1], edge["target_key"][1])
        for edge in edges
        if edge["qualified"] and edge["raw_iou"] > 0.0
    }
    selected = set(raw_selected)
    touched_sources = {source for source, _ in raw_selected}
    touched_targets = {target for _, target in raw_selected}
    remaining = [
        edge
        for edge in edges
        if edge["qualified"]
        and (edge["source_key"][1], edge["target_key"][1]) not in selected
        and edge["source_key"][1] not in touched_sources
        and edge["target_key"][1] not in touched_targets
    ]
    by_source: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_target: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for edge in remaining:
        by_source[edge["source_key"][1]].append(edge)
        by_target[edge["target_key"][1]].append(edge)
    unique_source: dict[int, tuple[int, int]] = {}
    for source, candidates in by_source.items():
        candidates.sort(key=lambda edge: (-edge["score"], edge["target_key"][1]))
        if len(candidates) == 1 or candidates[0]["score"] - candidates[1]["score"] > unique_score_margin:
            unique_source[source] = (source, candidates[0]["target_key"][1])
    unique_target: dict[int, tuple[int, int]] = {}
    for target, candidates in by_target.items():
        candidates.sort(key=lambda edge: (-edge["score"], edge["source_key"][1]))
        if len(candidates) == 1 or candidates[0]["score"] - candidates[1]["score"] > unique_score_margin:
            unique_target[target] = (candidates[0]["source_key"][1], target)
    for pair in unique_source.values():
        if unique_target.get(pair[1]) == pair:
            selected.add(pair)
    selected_sources = {source for source, _ in selected}
    selected_targets = {target for _, target in selected}
    ambiguity = {
        (edge["source_key"][1], edge["target_key"][1])
        for edge in remaining
        if (edge["source_key"][1], edge["target_key"][1]) not in selected
        and edge["source_key"][1] not in selected_sources
        and edge["target_key"][1] not in selected_targets
    }
    for edge in edges:
        pair = (edge["source_key"][1], edge["target_key"][1])
        edge["selected"] = pair in selected
        edge["ambiguity_bearing"] = pair in ambiguity
    return {"edges": edges, "selected": selected, "ambiguity": ambiguity}


@dataclass
class Track:
    track_id: int
    points: list[tuple[int, int]]
    resolved: bool = True
    parent_ids: tuple[int, ...] = ()

    def fingerprint(self, components: Sequence[Sequence[Component]]) -> str:
        frame, index = self.points[0]
        cells = components[frame][index].cells
        return f"{frame}:" + ",".join(str(cell) for cell in cells)


def _connected_groups(edges: set[tuple[int, int]]) -> list[tuple[list[int], list[int]]]:
    source_to_target: dict[int, set[int]] = defaultdict(set)
    target_to_source: dict[int, set[int]] = defaultdict(set)
    for source, target in edges:
        source_to_target[source].add(target)
        target_to_source[target].add(source)
    unvisited = {("s", source) for source in source_to_target} | {("t", target) for target in target_to_source}
    groups: list[tuple[list[int], list[int]]] = []
    while unvisited:
        root = min(unvisited, key=lambda item: (item[0], item[1]))
        queue = deque([root])
        sources: set[int] = set()
        targets: set[int] = set()
        while queue:
            side, value = queue.popleft()
            node = (side, value)
            if node not in unvisited:
                continue
            unvisited.remove(node)
            if side == "s":
                sources.add(value)
                queue.extend(("t", target) for target in source_to_target[value])
            else:
                targets.add(value)
                queue.extend(("s", source) for source in target_to_source[value])
        groups.append((sorted(sources), sorted(targets)))
    groups.sort(key=lambda group: (group[0][0], tuple(group[1])))
    return groups


def _minimum_periodic_manhattan(left: Component, right: Component) -> int:
    best = 24
    for left_cell in left.cells:
        ly, lx = divmod(left_cell, 12)
        for right_cell in right.cells:
            ry, rx = divmod(right_cell, 12)
            dy = min(abs(ly - ry), 12 - abs(ly - ry))
            dx = min(abs(lx - rx), 12 - abs(lx - rx))
            best = min(best, dy + dx)
    return best


def track_components(components: Sequence[Sequence[Component]]) -> tuple[dict[int, Track], list[dict[str, Any]]]:
    if len(components) != 160:
        raise AuditError("tracker requires 160 detector frames")
    associations = [None]
    for frame in range(1, 160):
        associations.append(associate_components(components[frame - 1], components[frame]))
    collapse_nodes: set[tuple[int, int]] = set()
    for frame in range(1, 159):
        incoming = Counter(target for _, target in associations[frame]["selected"])
        outgoing = Counter(source for source, _ in associations[frame + 1]["selected"])
        for index in range(len(components[frame])):
            if incoming[index] >= 2 and outgoing[index] >= 2:
                collapse_nodes.add((frame, index))
    tracks: dict[int, Track] = {}
    next_id = 0
    mapping: dict[int, int] = {}
    events: list[dict[str, Any]] = []

    def make_event(
        frame: int,
        kind: str,
        source_ids: Sequence[int],
        target_ids: Sequence[int],
        source_keys: Sequence[Sequence[int]],
        target_keys: Sequence[Sequence[int]],
        resolved: bool,
        association_edges: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        return {
            "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-EVENT-v1",
            "world_id": None,
            "frame": frame,
            "event_type": kind,
            "source_track_ids": list(source_ids),
            "target_track_ids": list(target_ids),
            "source_component_keys": [list(key) for key in source_keys],
            "target_component_keys": [list(key) for key in target_keys],
            "resolved": resolved,
            "association_edges": [dict(edge) for edge in association_edges],
        }

    for component in components[0]:
        track = Track(next_id, [(0, component.index)])
        tracks[next_id] = track
        mapping[component.index] = next_id
        events.append(make_event(0, "APPEARANCE", [], [next_id], [], [component.key], True))
        next_id += 1
    for frame in range(1, 160):
        previous_mapping = dict(mapping)
        result = associations[frame]
        graph_edges = set(result["selected"]) | set(result["ambiguity"])
        groups = _connected_groups(graph_edges)
        supported_sources = {source for source, _ in graph_edges}
        supported_targets = {target for _, target in graph_edges}
        target_mapping: dict[int, int] = {}
        transition_unresolved = False
        for source_index in sorted(set(range(len(components[frame - 1]))) - supported_sources):
            source_id = previous_mapping[source_index]
            events.append(
                make_event(frame, "DISSOLUTION", [source_id], [], [components[frame - 1][source_index].key], [], True)
            )
        for source_indices, target_indices in groups:
            source_ids = [previous_mapping[index] for index in source_indices if index in previous_mapping]
            incomplete = len(source_ids) != len(source_indices)
            ambiguous = any(
                pair in result["ambiguity"]
                for pair in ((source, target) for source in source_indices for target in target_indices)
            )
            collapse = any((frame - 1, source) in collapse_nodes for source in source_indices) or any(
                (frame, target) in collapse_nodes for target in target_indices
            )
            unresolved = incomplete or ambiguous or collapse or (len(source_indices) > 1 and len(target_indices) > 1)
            source_keys = [components[frame - 1][index].key for index in source_indices]
            target_keys = [components[frame][index].key for index in target_indices]
            if unresolved:
                transition_unresolved = True
                for source_id in source_ids:
                    tracks[source_id].resolved = False
                target_ids: list[int] = []
                for target_index in target_indices:
                    tracks[next_id] = Track(next_id, [(frame, target_index)], resolved=False, parent_ids=tuple(sorted(source_ids)))
                    target_mapping[target_index] = next_id
                    target_ids.append(next_id)
                    next_id += 1
                events.append(make_event(frame, "TRACKING_UNRESOLVED", source_ids, target_ids, source_keys, target_keys, False))
            elif len(source_indices) == 1 and len(target_indices) == 1:
                source_id = source_ids[0]
                target_index = target_indices[0]
                tracks[source_id].points.append((frame, target_index))
                target_mapping[target_index] = source_id
                events.append(make_event(frame, "CONTINUATION", [source_id], [source_id], source_keys, target_keys, True))
            elif len(source_indices) == 1:
                parent_id = source_ids[0]
                target_ids = []
                for target_index in target_indices:
                    tracks[next_id] = Track(next_id, [(frame, target_index)], parent_ids=(parent_id,))
                    target_mapping[target_index] = next_id
                    target_ids.append(next_id)
                    next_id += 1
                events.append(make_event(frame, "SPLIT", [parent_id], target_ids, source_keys, target_keys, True))
            elif len(target_indices) == 1:
                target_index = target_indices[0]
                parent_ids = tuple(sorted(source_ids))
                tracks[next_id] = Track(next_id, [(frame, target_index)], parent_ids=parent_ids)
                target_mapping[target_index] = next_id
                events.append(make_event(frame, "MERGE", source_ids, [next_id], source_keys, target_keys, True))
                next_id += 1
            else:
                raise AuditError("unexpected empty association group")
        for target_index in sorted(set(range(len(components[frame]))) - supported_targets):
            tracks[next_id] = Track(next_id, [(frame, target_index)])
            target_mapping[target_index] = next_id
            events.append(make_event(frame, "APPEARANCE", [], [next_id], [], [components[frame][target_index].key], True))
            next_id += 1
        for left in range(len(components[frame])):
            for right in range(left + 1, len(components[frame])):
                left_id = target_mapping[left]
                right_id = target_mapping[right]
                if tracks[left_id].resolved and tracks[right_id].resolved and _minimum_periodic_manhattan(
                    components[frame][left], components[frame][right]
                ) == 2:
                    events.append(
                        make_event(
                            frame,
                            "TEMPORARY_CONTACT",
                            [],
                            [left_id, right_id],
                            [],
                            [components[frame][left].key, components[frame][right].key],
                            True,
                        )
                    )
        diagnostic_edges = sorted(
            result["edges"], key=lambda edge: (edge["source_key"][1], edge["target_key"][1])
        )
        events.append(
            make_event(
                frame,
                "ASSOCIATION_DIAGNOSTICS",
                [previous_mapping[index] for index in range(len(components[frame - 1]))],
                [target_mapping[index] for index in range(len(components[frame]))],
                [component.key for component in components[frame - 1]],
                [component.key for component in components[frame]],
                not transition_unresolved,
                diagnostic_edges,
            )
        )
        mapping = target_mapping
    events.sort(
        key=lambda row: (
            row["frame"],
            EVENT_ORDER[row["event_type"]],
            row["source_component_keys"],
            row["target_component_keys"],
        )
    )
    return tracks, events


def advance_cohort(
    q: np.ndarray[Any, Any],
    pre_matter: np.ndarray[Any, Any],
    post_matter: np.ndarray[Any, Any],
    forward: np.ndarray[Any, Any],
    reverse: np.ndarray[Any, Any],
    dt: float = 0.05,
) -> np.ndarray[Any, Any]:
    arrays = (q, pre_matter, post_matter, forward, reverse)
    if q.shape != (12, 12) or pre_matter.shape != q.shape or post_matter.shape != q.shape:
        raise AuditError("cohort cell shape mismatch")
    if forward.shape != (2, 12, 12) or reverse.shape != forward.shape:
        raise AuditError("cohort face shape mismatch")
    if any(array.dtype != np.float64 or not np.all(np.isfinite(array)) for array in arrays):
        raise AuditError("cohort dtype/nonfinite")
    if np.any(pre_matter < 0.0) or np.any(post_matter < 0.0) or np.any(forward < 0.0) or np.any(reverse < 0.0):
        raise AuditError("negative cohort input")
    tolerance = 1e-12 + 1e-10 * max(
        1.0, float(np.max(np.abs(pre_matter))), float(np.max(np.abs(post_matter)))
    )
    if float(np.min(q)) < -tolerance or float(np.max(q - pre_matter)) > tolerance:
        raise AuditError("invalid pre-cohort bounds")
    net = forward - reverse
    expected_post = pre_matter - dt * (
        (net[0] - np.roll(net[0], 1, axis=0)) + (net[1] - np.roll(net[1], 1, axis=1))
    )
    if float(np.max(np.abs(post_matter - expected_post))) > tolerance:
        raise AuditError("cohort matter identity")
    fraction = np.divide(q, pre_matter, out=np.zeros_like(q), where=pre_matter > 0.0)
    j0 = forward[0] * fraction - reverse[0] * np.roll(fraction, -1, axis=0)
    j1 = forward[1] * fraction - reverse[1] * np.roll(fraction, -1, axis=1)
    q_next = q - dt * ((j0 - np.roll(j0, 1, axis=0)) + (j1 - np.roll(j1, 1, axis=1)))
    if abs(math.fsum(float(v) for v in q_next.flat) - math.fsum(float(v) for v in q.flat)) > tolerance * q.size:
        raise AuditError("cohort conservation")
    if float(np.min(q_next)) < -tolerance or float(np.max(q_next - post_matter)) > tolerance:
        raise AuditError("invalid post-cohort bounds")
    return q_next


def _median(values: Sequence[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def summarize_track(observations: Sequence[Mapping[str, Any]], resolved: bool = True) -> dict[str, Any]:
    if not observations:
        raise AuditError("empty track summary")
    ordered = sorted(observations, key=lambda row: row["frame"])
    frames = [int(row["frame"]) for row in ordered]
    first_turnover = next((frame for frame, row in zip(frames, ordered, strict=True) if row["turnover_fraction"] >= 0.6), None)
    observed = len(ordered)
    summary = {
        "observed_frames": observed,
        "span_frames": frames[-1] - frames[0] + 1,
        "maximum_area_fraction": max(float(row["area_fraction"]) for row in ordered),
        "bounded_fraction": sum(
            1 for row in ordered if not row["percolated"] and row["area_fraction"] <= 0.25
        )
        / observed,
        "percolated_fraction": sum(1 for row in ordered if row["percolated"]) / observed,
        "mean_activity_per_mass": math.fsum(float(row["activity_per_mass"]) for row in ordered) / observed,
        "mean_energy_throughput_per_mass": math.fsum(
            float(row["energy_throughput_per_mass"]) for row in ordered
        )
        / observed,
        "maximum_turnover_fraction": max(float(row["turnover_fraction"]) for row in ordered),
        "first_turnover_frame": first_turnover,
        "post_turnover_frames": 0 if first_turnover is None else sum(frame > first_turnover for frame in frames),
        "resolved": bool(resolved),
    }
    summary["persistent"] = bool(resolved and observed >= 80 and summary["span_frames"] >= 80)
    summary["active"] = bool(
        summary["mean_activity_per_mass"] >= 1e-4
        and summary["mean_energy_throughput_per_mass"] >= 1e-5
    )
    summary["candidate"] = bool(
        summary["persistent"]
        and summary["maximum_area_fraction"] <= 0.25
        and summary["bounded_fraction"] >= 0.95
        and summary["percolated_fraction"] == 0.0
        and summary["active"]
        and summary["maximum_turnover_fraction"] >= 0.6
        and summary["post_turnover_frames"] >= 32
    )
    return summary


def classify_world(
    track_summaries: Mapping[int, Mapping[str, Any]],
    components: Sequence[Sequence[Component]],
    tracks: Mapping[int, Track] | None = None,
) -> tuple[str, list[int]]:
    unresolved = any(not summary.get("resolved", True) for summary in track_summaries.values())
    if tracks is not None:
        unresolved = unresolved or any(not track.resolved for track in tracks.values())
    if unresolved:
        regime = "TRACKING_UNRESOLVED"
    elif any(
        summary["percolated_fraction"] > 0.0 and summary["active"] for summary in track_summaries.values()
    ):
        regime = "ACTIVE_UNBOUNDED"
    elif any(component.percolates for frame in components for component in frame):
        regime = "PERCOLATED"
    elif not any(components):
        regime = "EMPTY_OR_GAS"
    elif not components[159]:
        regime = "DISSOLVED"
    elif any(summary["candidate"] for summary in track_summaries.values()):
        regime = "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    else:
        persistent = [summary for summary in track_summaries.values() if summary["persistent"]]
        if any(summary["active"] for summary in persistent) and not any(
            summary["maximum_turnover_fraction"] >= 0.6 for summary in persistent
        ):
            regime = "PERSISTENT_NO_TURNOVER"
        elif persistent:
            regime = "STATIC_CRYSTAL_OR_SHELL"
        elif any(
            not summary["persistent"] and summary["maximum_turnover_fraction"] >= 0.6
            for summary in track_summaries.values()
        ):
            regime = "TURNOVER_WITHOUT_PERSISTENCE"
        else:
            regime = "DISSOLVED"
    candidate_ids = sorted(track_id for track_id, summary in track_summaries.items() if summary["candidate"])
    if regime != "BOUNDED_ACTIVE_TURNOVER_CANDIDATE":
        candidate_ids = []
    return regime, candidate_ids


def decide_autopsy_outcome(
    audit_valid: bool,
    candidate_diagnostics_available: bool,
    transient_majority: bool,
    coherent: bool,
    mechanism_diagnostics_available: bool,
    qualified_mechanisms: Sequence[str],
) -> str:
    if not audit_valid:
        return "AUDIT_INVALID"
    if not candidate_diagnostics_available:
        return "RAW_INSUFFICIENT"
    if transient_majority or not coherent:
        return "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES"
    if not mechanism_diagnostics_available:
        return "RAW_INSUFFICIENT"
    if len(qualified_mechanisms) == 1:
        return "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS"
    return "RAW_INSUFFICIENT"


def _component_observation_metrics(
    frame: int,
    component: Component,
    arrays: Mapping[str, np.ndarray[Any, Any]],
    q: np.ndarray[Any, Any],
    initial_cohort_mass: float,
) -> dict[str, Any]:
    support = component.mask
    gross = arrays["ledger__matter_forward"][frame] + arrays["ledger__matter_reverse"][frame]
    work = arrays["ledger__gross_formation_work"][frame] + arrays["ledger__gross_rupture_release"][frame]
    internal_masks = [support & np.roll(support, -1, axis=axis) for axis in range(2)]

    def face_sum(values: np.ndarray[Any, Any], masks: Sequence[np.ndarray[Any, Any]]) -> float:
        return math.fsum(
            float(values[axis, y, x])
            for axis in range(2)
            for y in range(12)
            for x in range(12)
            if masks[axis][y, x]
        )

    activity = face_sum(gross, internal_masks) / component.mass
    energy = face_sum(work, internal_masks) / (0.05 * component.mass)
    matter_in_rates: list[float] = []
    matter_out_rates: list[float] = []
    resource_natural_rates: list[float] = []
    forward = arrays["ledger__matter_forward"][frame]
    reverse = arrays["ledger__matter_reverse"][frame]
    resource_natural = arrays["ledger__resource_natural"][frame]
    bond_values: list[float] = []
    for axis in range(2):
        target_support = np.roll(support, -1, axis=axis)
        for y in range(12):
            for x in range(12):
                source_inside = bool(support[y, x])
                target_inside = bool(target_support[y, x])
                if source_inside and target_inside:
                    bond_values.append(float(arrays["state_b"][frame, axis, y, x]))
                elif source_inside != target_inside:
                    fwd = float(forward[axis, y, x])
                    rev = float(reverse[axis, y, x])
                    if source_inside:
                        matter_out_rates.append(fwd)
                        matter_in_rates.append(rev)
                    else:
                        matter_in_rates.append(fwd)
                        matter_out_rates.append(rev)
                    resource_natural_rates.append(abs(float(resource_natural[axis, y, x])))
    matter_in = 0.05 * math.fsum(matter_in_rates)
    matter_out = 0.05 * math.fsum(matter_out_rates)
    resource_natural_exchange = 0.05 * math.fsum(resource_natural_rates)
    retained = math.fsum(float(q[y, x]) for y in range(12) for x in range(12) if support[y, x])
    turnover_raw = 1.0 - retained / initial_cohort_mass
    turnover_tolerance = 1e-12 + 1e-10 * initial_cohort_mass
    if turnover_raw < -turnover_tolerance or turnover_raw > 1.0 + turnover_tolerance:
        raise AuditError("turnover range")
    turnover = min(1.0, max(0.0, turnover_raw))
    cells = component.cells
    matter_values = [float(arrays["state_m"][frame][divmod(cell, 12)]) for cell in cells]
    resource_values = [float(arrays["state_n"][frame][divmod(cell, 12)]) for cell in cells]

    def cv(values: Sequence[float]) -> float:
        mean = math.fsum(values) / len(values)
        if mean == 0.0:
            if any(value != 0.0 for value in values):
                raise AuditError("inconsistent zero mean")
            return 0.0
        if mean < 0.0:
            raise AuditError("negative support mean")
        variance = math.fsum((value - mean) ** 2 for value in values) / len(values)
        return math.sqrt(variance) / mean

    seam_distance = min(min(y, 11 - y, x, 11 - x) for y, x in (divmod(cell, 12) for cell in cells))
    seam_crossed = False
    for axis in range(2):
        if axis == 0:
            seam_crossed = seam_crossed or any(support[0, x] and support[11, x] for x in range(12))
        else:
            seam_crossed = seam_crossed or any(support[y, 0] and support[y, 11] for y in range(12))
    return {
        "mass": component.mass,
        "area_fraction": component.area / 144.0,
        "percolated": component.percolates,
        "activity_per_mass": activity,
        "energy_throughput_per_mass": energy,
        "turnover_fraction": turnover,
        "matter_in": matter_in,
        "matter_out": matter_out,
        "matter_exchange_per_mass": (matter_in + matter_out) / component.mass,
        "net_matter_loss_per_mass": (matter_out - matter_in) / component.mass,
        "resource_natural_exchange_per_mass": resource_natural_exchange / component.mass,
        "mean_internal_bond": math.fsum(bond_values) / len(bond_values) if bond_values else 0.0,
        "internal_bond_saturation_fraction": (
            sum(value >= 0.9 for value in bond_values) / len(bond_values) if bond_values else 0.0
        ),
        "matter_cv": cv(matter_values),
        "resource_cv": cv(resource_values),
        "coordinate_seam_distance": int(seam_distance),
        "coordinate_seam_crossed": bool(seam_crossed),
        "wraps_y": component.wraps_y,
        "wraps_x": component.wraps_x,
        "radius_gyration_fraction": component.radius_gyration / 12.0,
        "instantaneous_bounded_active": bool(
            not component.percolates
            and component.area / 144.0 <= 0.25
            and activity >= 1e-4
            and energy >= 1e-5
        ),
    }


def build_track_observations(
    world_id: str,
    arrays: Mapping[str, np.ndarray[Any, Any]],
    components: Sequence[Sequence[Component]],
    tracks: Mapping[int, Track],
) -> tuple[dict[int, list[dict[str, Any]]], dict[int, dict[str, Any]]]:
    observations_by_track: dict[int, list[dict[str, Any]]] = {}
    summaries: dict[int, dict[str, Any]] = {}
    for track_id in sorted(tracks):
        track = tracks[track_id]
        first_frame, first_component_index = track.points[0]
        first_component = components[first_frame][first_component_index]
        q = np.zeros((12, 12), dtype=np.float64)
        q[first_component.mask] = arrays["state_m"][first_frame][first_component.mask]
        initial_cohort_mass = math.fsum(float(value) for value in q.flat)
        if initial_cohort_mass <= 0.0:
            raise AuditError("nonpositive initial cohort")
        fingerprint = track.fingerprint(components)
        rows: list[dict[str, Any]] = []
        for point_index, (frame, component_index) in enumerate(track.points):
            component = components[frame][component_index]
            metrics = _component_observation_metrics(frame, component, arrays, q, initial_cohort_mass)
            row: dict[str, Any] = {
                "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-TRACK-OBSERVATION-v1",
                "world_id": world_id,
                "track_id": track_id,
                "track_fingerprint": fingerprint,
                "frame": frame,
                "component_index": component_index,
                "resolved": track.resolved,
                **metrics,
            }
            rows.append(row)
            if point_index + 1 < len(track.points):
                next_frame, _ = track.points[point_index + 1]
                if next_frame != frame + 1:
                    raise AuditError("nonconsecutive track")
                q = advance_cohort(
                    q,
                    arrays["state_m"][frame],
                    arrays["state_m"][frame + 1],
                    arrays["ledger__matter_forward"][frame],
                    arrays["ledger__matter_reverse"][frame],
                )
        for index, row in enumerate(rows):
            prefix = summarize_track(rows[: index + 1], resolved=track.resolved)
            row["prefix_persistent"] = prefix["persistent"]
            row["prefix_active"] = prefix["active"]
            row["prefix_turnover"] = prefix["maximum_turnover_fraction"] >= 0.6
            row["prefix_post_turnover_frames"] = prefix["post_turnover_frames"]
            row["prefix_candidate"] = prefix["candidate"]
        observations_by_track[track_id] = rows
        summaries[track_id] = summarize_track(rows, resolved=track.resolved)
    return observations_by_track, summaries


def _runs(frames: Sequence[int]) -> list[tuple[int, int, int]]:
    if not frames:
        return []
    ordered = sorted(set(frames))
    runs: list[tuple[int, int, int]] = []
    start = previous = ordered[0]
    for frame in ordered[1:]:
        if frame != previous + 1:
            runs.append((start, previous, previous - start + 1))
            start = frame
        previous = frame
    runs.append((start, previous, previous - start + 1))
    return runs


def _formation_bin(frame: int | None) -> str:
    if frame is None:
        return "none"
    if frame <= 39:
        return "early"
    if frame <= 119:
        return "middle"
    return "late"


def _fingerprint_sort_key(value: str) -> tuple[int, tuple[int, ...]]:
    try:
        frame_text, cells_text = value.split(":", 1)
        cells = tuple(int(token) for token in cells_text.split(",") if token != "")
        return int(frame_text), cells
    except (ValueError, TypeError) as exc:
        raise AuditError(f"invalid track fingerprint {value!r}") from exc


def developmental_world_summary(
    world_id: str,
    committed_regime: str,
    reconstructed_regime: str,
    components: Sequence[Sequence[Component]],
    tracks: Mapping[int, Track],
    observations_by_track: Mapping[int, Sequence[Mapping[str, Any]]],
    summaries: Mapping[int, Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    candidate_track_ids: Sequence[int],
) -> dict[str, Any]:
    law_id, ic_id, replicate_token = world_id.split("__")
    replicate = int(replicate_token[1:])
    track_development: dict[int, dict[str, Any]] = {}
    for track_id, rows_value in observations_by_track.items():
        rows = list(rows_value)
        t_active = next((int(row["frame"]) for row in rows if row["instantaneous_bounded_active"]), None)
        t_persistence = next((int(row["frame"]) for row in rows if row["prefix_persistent"]), None)
        t_turn = None
        if t_active is not None:
            t_turn = next(
                (int(row["frame"]) for row in rows if row["frame"] >= t_active and row["turnover_fraction"] >= 0.6),
                None,
            )
        t_prefix = None
        if t_turn is not None:
            t_prefix = next(
                (int(row["frame"]) for row in rows if row["frame"] >= t_turn and row["prefix_candidate"]),
                None,
            )
        candidate_runs = _runs([int(row["frame"]) for row in rows if row["prefix_candidate"]])
        longest = max((run[2] for run in candidate_runs), default=0)
        selected_run = min(
            (run for run in candidate_runs if run[2] == longest),
            key=lambda run: run[0],
            default=None,
        )
        terminal_episode = bool(selected_run is not None and selected_run[1] == int(rows[-1]["frame"]))
        stable = bool(longest >= 32 and terminal_episode)
        if t_active is None:
            pathway = "ACTIVATION_FAILURE"
        elif t_turn is None:
            pathway = "TURNOVER_FAILURE"
        elif t_prefix is None:
            pathway = "PERSISTENCE_FAILURE"
        elif stable:
            pathway = "STABLE_CANDIDATE_EPISODE"
        else:
            pathway = "TRANSIENT_CANDIDATE_CROSSING"
        track_development[track_id] = {
            "t_formation": int(rows[0]["frame"]),
            "t_active": t_active,
            "t_persistence": t_persistence,
            "t_turn": t_turn,
            "t_prefix": t_prefix,
            "runs": candidate_runs,
            "selected_run": selected_run,
            "longest": longest,
            "terminal_episode": terminal_episode,
            "stable": stable,
            "pathway": pathway,
            "fingerprint": str(rows[0]["track_fingerprint"]),
            "fingerprint_key": _fingerprint_sort_key(str(rows[0]["track_fingerprint"])),
        }
    if not tracks:
        pathway = "FORMATION_FAILURE"
        co_primary: list[int] = []
        representative: int | None = None
    else:
        maximum_rank = max(PATHWAY_ORDER[value["pathway"]] for value in track_development.values())
        co_primary = sorted(
            (track_id for track_id, value in track_development.items() if PATHWAY_ORDER[value["pathway"]] == maximum_rank),
            key=lambda track_id: track_development[track_id]["fingerprint_key"],
        )
        pathway = track_development[co_primary[0]]["pathway"]
        if candidate_track_ids:
            representative = min(
                candidate_track_ids,
                key=lambda track_id: (
                    -track_development[track_id]["longest"],
                    track_development[track_id]["selected_run"][0]
                    if track_development[track_id]["selected_run"] is not None
                    else 10**9,
                    track_development[track_id]["fingerprint_key"],
                ),
            )
        else:
            representative = co_primary[0]
    milestone_specs = {
        "formation": "t_formation",
        "bounded_active": "t_active",
        "persistence": "t_persistence",
        "turnover": "t_turn",
        "prefix_candidate": "t_prefix",
    }
    milestone_frames: dict[str, int | None] = {}
    milestone_fingerprints: dict[str, str | None] = {}
    for name, key in milestone_specs.items():
        eligible = [
            (int(value[key]), value["fingerprint_key"], value["fingerprint"])
            for value in track_development.values()
            if value[key] is not None
        ]
        if eligible:
            frame, _, fingerprint = min(eligible, key=lambda item: (item[0], item[1]))
            milestone_frames[name] = frame
            milestone_fingerprints[name] = fingerprint
        else:
            milestone_frames[name] = None
            milestone_fingerprints[name] = None
    last_detected = max((frame for frame, frame_components in enumerate(components) if frame_components), default=None)
    terminal_empty_run_start = None
    if not components[159]:
        terminal_empty_run_start = 159
        while terminal_empty_run_start > 0 and not components[terminal_empty_run_start - 1]:
            terminal_empty_run_start -= 1
    representative_rows = [] if representative is None else list(observations_by_track[representative])
    terminal_freeze_onset = None
    terminal_state = None
    terminal_alive = bool(representative_rows and representative_rows[-1]["frame"] == 159)
    dissolution_frame = None
    if representative is not None:
        dissolution_frame = next(
            (
                int(event["frame"])
                for event in events
                if event["event_type"] == "DISSOLUTION" and representative in event["source_track_ids"]
            ),
            None,
        )
        if dissolution_frame is not None and dissolution_frame < 159:
            terminal_state = "EMPTY_OR_DISSOLVED"
        elif terminal_alive:
            suffix: list[Mapping[str, Any]] = []
            expected_frame = int(representative_rows[-1]["frame"])
            for row in reversed(representative_rows):
                if (
                    int(row["frame"]) == expected_frame
                    and row["activity_per_mass"] < 1e-4
                    and row["energy_throughput_per_mass"] < 1e-5
                ):
                    suffix.append(row)
                    expected_frame -= 1
                else:
                    break
            if len(suffix) >= 32:
                terminal_freeze_onset = int(suffix[-1]["frame"])
                terminal_state = "FROZEN"
            elif len(representative_rows) >= 32 and all(
                int(right["frame"]) == int(left["frame"]) + 1
                for left, right in zip(representative_rows[-32:-1], representative_rows[-31:], strict=True)
            ):
                last32 = representative_rows[-32:]
                mean_activity = math.fsum(float(row["activity_per_mass"]) for row in last32) / 32
                mean_energy = math.fsum(float(row["energy_throughput_per_mass"]) for row in last32) / 32
                terminal_state = (
                    "PERSISTENT_ACTIVE" if mean_activity >= 1e-4 and mean_energy >= 1e-5 else "PERSISTENT_OTHER"
                )
            else:
                terminal_state = "PERSISTENT_OTHER"
        elif representative_rows:
            raise AuditError(f"track {representative} ends without dissolution")
    right_censored = any(track.resolved and track.points[-1][0] == 159 for track in tracks.values())
    event_counts = Counter(event["event_type"] for event in events)
    any_split_merge = event_counts["SPLIT"] > 0 or event_counts["MERGE"] > 0
    representative_fp = None if representative is None else track_development[representative]["fingerprint"]
    trajectory_class = None
    if representative is not None:
        trajectory_class = (
            f"{pathway}|{terminal_state or 'NONE'}|{_formation_bin(track_development[representative]['t_formation'])}"
            f"|SPLIT_MERGE={'1' if any_split_merge else '0'}|CENSORED={'1' if right_censored else '0'}"
        )
    rep_development = None if representative is None else track_development[representative]
    first_component = milestone_frames["formation"]

    def elapsed(target: int | None) -> int | None:
        return None if first_component is None or target is None else target - first_component

    return {
        "world_id": world_id,
        "law_id": law_id,
        "ic_id": ic_id,
        "replicate": replicate,
        "committed_regime": committed_regime,
        "reconstructed_regime": reconstructed_regime,
        "first_component_frame": milestone_frames["formation"],
        "first_bounded_active_frame": milestone_frames["bounded_active"],
        "first_persistence_qualification_frame": milestone_frames["persistence"],
        "first_turnover_frame": milestone_frames["turnover"],
        "first_prefix_candidate_frame": milestone_frames["prefix_candidate"],
        "candidate_status_frames": 0
        if representative is None
        else sum(bool(row["prefix_candidate"]) for row in representative_rows),
        "candidate_episode_count": 0 if rep_development is None else len(rep_development["runs"]),
        "longest_candidate_episode_frames": 0 if rep_development is None else rep_development["longest"],
        "candidate_episode_terminal": False if rep_development is None else rep_development["terminal_episode"],
        "last_detected_frame": last_detected,
        "terminal_empty_run_start": terminal_empty_run_start,
        "terminal_freeze_onset": terminal_freeze_onset,
        "terminal_track_alive": terminal_alive,
        "frames_formation_to_bounded_active": elapsed(milestone_frames["bounded_active"]),
        "frames_formation_to_persistence": elapsed(milestone_frames["persistence"]),
        "frames_formation_to_turnover": elapsed(milestone_frames["turnover"]),
        "frames_formation_to_candidate": elapsed(milestone_frames["prefix_candidate"]),
        "frames_formation_to_terminal_loss": elapsed(dissolution_frame),
        "right_censored": right_censored,
        "coordinate_seam_crossed": any(
            bool(row["coordinate_seam_crossed"]) for rows in observations_by_track.values() for row in rows
        ),
        "ever_wound": any(component.percolates for frame_components in components for component in frame_components),
        "split_count": event_counts["SPLIT"],
        "merge_count": event_counts["MERGE"],
        "appearance_count": event_counts["APPEARANCE"],
        "dissolution_count": event_counts["DISSOLUTION"],
        "primary_developmental_pathway": pathway,
        "terminal_state": terminal_state,
        "formation_opportunity": True,
        "maintenance_opportunity": first_component is not None,
        "persistence_horizon_opportunity": any(track.points[0][0] <= 80 for track in tracks.values()),
        "post_turnover_horizon_opportunity": any(
            value["t_turn"] is not None and value["t_turn"] <= 127 for value in track_development.values()
        ),
        "milestone_track_fingerprints": milestone_fingerprints,
        "representative_track_fingerprint": representative_fp,
        "co_primary_track_fingerprints": [track_development[track_id]["fingerprint"] for track_id in co_primary],
        "trajectory_class": trajectory_class,
        "_representative_track_id": representative,
        "_representative_track_development": None if representative is None else track_development[representative],
        "_representative_dissolution_frame": dissolution_frame,
        "_candidate_track_count": len(candidate_track_ids),
        "_track_development": track_development,
    }


def _binary_summary(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "numerator": int(numerator),
        "denominator": int(denominator),
        "fraction": None if denominator == 0 else numerator / denominator,
    }


def _continuous_summary(values: Iterable[int | float | None]) -> dict[str, Any]:
    finite = [float(value) for value in values if value is not None]
    return {
        "n": len(finite),
        "median": _median(finite),
        "min": None if not finite else min(finite),
        "max": None if not finite else max(finite),
    }


def _group_summary(rows: Sequence[Mapping[str, Any]], group: Mapping[str, str]) -> dict[str, Any]:
    denominator = len(rows)
    binary = {
        "formed": lambda row: row["first_component_frame"] is not None,
        "bounded_active": lambda row: row["first_bounded_active_frame"] is not None,
        "persistent": lambda row: row["first_persistence_qualification_frame"] is not None,
        "turnover": lambda row: row["first_turnover_frame"] is not None,
        "prefix_candidate": lambda row: row["first_prefix_candidate_frame"] is not None,
        "stable_candidate": lambda row: row["primary_developmental_pathway"] == "STABLE_CANDIDATE_EPISODE",
        "right_censored": lambda row: bool(row["right_censored"]),
    }
    metrics = (
        "first_component_frame",
        "first_bounded_active_frame",
        "first_persistence_qualification_frame",
        "first_turnover_frame",
        "first_prefix_candidate_frame",
        "candidate_status_frames",
        "longest_candidate_episode_frames",
    )
    pathway_names = ("FORMATION_FAILURE",) + tuple(PATHWAY_ORDER)
    terminal_names = ("EMPTY_OR_DISSOLVED", "FROZEN", "PERSISTENT_ACTIVE", "PERSISTENT_OTHER", "NONE")
    result: dict[str, Any] = {
        "group": dict(group),
        "denominator": denominator,
        "regime_counts": {name: sum(row["reconstructed_regime"] == name for row in rows) for name in CLASSES},
        "pathway_counts": {name: sum(row["primary_developmental_pathway"] == name for row in rows) for name in pathway_names},
        "terminal_counts": {
            name: sum((row["terminal_state"] or "NONE") == name for row in rows) for name in terminal_names
        },
        "continuous_summaries": {name: _continuous_summary(row[name] for row in rows) for name in metrics},
    }
    for name, predicate in binary.items():
        result[name] = _binary_summary(sum(predicate(row) for row in rows), denominator)
    return result


def build_recomputed_classification(
    manifest: Mapping[str, Any],
    manifest_sha256: str,
    world_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    worlds = sorted(
        (
            {
                "candidate_track_ids": list(result["candidate_track_ids"]),
                "ic_id": result["ic_id"],
                "law_id": result["law_id"],
                "regime": result["regime"],
                "replicate": result["replicate"],
                "status": "COMPLETE",
                "world_id": result["world_id"],
            }
            for result in world_results
        ),
        key=lambda row: row["world_id"],
    )
    law_ids = [law["law_id"] for law in manifest["law_family"]["laws"]]
    atlas: list[dict[str, Any]] = []
    candidate_regions: list[str] = []
    for law_id in law_ids:
        per_ic: list[dict[str, Any]] = []
        ic_candidate_counts: list[int] = []
        for ic_id in ("soup", "compact"):
            selected = [row for row in worlds if row["law_id"] == law_id and row["ic_id"] == ic_id]
            counts = {name: sum(row["regime"] == name for row in selected) for name in CLASSES}
            complete = len(selected) == 4 and all(row["status"] == "COMPLETE" for row in selected)
            per_ic.append(
                {
                    "complete": complete,
                    "counts": counts,
                    "denominator": 4,
                    "ic_id": ic_id,
                }
            )
            ic_candidate_counts.append(counts["BOUNDED_ACTIVE_TURNOVER_CANDIDATE"])
        reproducible = all(row["complete"] for row in per_ic) and all(count >= 2 for count in ic_candidate_counts)
        if reproducible:
            candidate_regions.append(law_id)
        atlas.append(
            {
                "law_id": law_id,
                "per_ic": per_ic,
                "region_id": law_id,
                "reproducible_candidate": reproducible,
            }
        )
    disposition = "DEV_REGIME_CANDIDATE" if candidate_regions else "DEV_FEASIBILITY_FAIL"
    return {
        "atlas": atlas,
        "candidate_regions": candidate_regions,
        "disposition": disposition,
        "manifest_sha256": manifest_sha256,
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-CLASSIFICATION-v1",
        "worlds": worlds,
    }


def _stage_row(stage: str, numerator: int, denominator: int) -> dict[str, Any]:
    return {"stage": stage, **_binary_summary(numerator, denominator)}


def _world_maintenance_group(rows: Sequence[Mapping[str, Any]], group: Mapping[str, str]) -> dict[str, Any]:
    formed = [row for row in rows if row["maintenance_opportunity"]]
    predicates = {
        "formed": lambda row: True,
        "bounded_active": lambda row: row["first_bounded_active_frame"] is not None,
        "persistent": lambda row: row["first_persistence_qualification_frame"] is not None,
        "turnover": lambda row: row["first_turnover_frame"] is not None,
        "prefix_candidate": lambda row: row["first_prefix_candidate_frame"] is not None,
        "stable_candidate": lambda row: row["primary_developmental_pathway"] == "STABLE_CANDIDATE_EPISODE",
        "terminal_persistence": lambda row: bool(row["terminal_track_alive"]),
    }
    denominator = len(formed)
    return {
        "group": dict(group),
        "denominator": denominator,
        "stage_rows": [_stage_row(name, sum(predicate(row) for row in formed), denominator) for name, predicate in predicates.items()],
    }


def _track_maintenance_group(rows: Sequence[Mapping[str, Any]], group: Mapping[str, str]) -> dict[str, Any]:
    predicates = {
        "formed": lambda row: True,
        "bounded_active": lambda row: row["t_active"] is not None,
        "persistent": lambda row: row["t_persistence"] is not None,
        "turnover": lambda row: row["t_turn"] is not None,
        "prefix_candidate": lambda row: row["t_prefix"] is not None,
        "stable_candidate": lambda row: bool(row["stable"]),
        "terminal_persistence": lambda row: bool(row["terminal_persistence"]),
    }
    denominator = len(rows)
    return {
        "group": dict(group),
        "denominator": denominator,
        "stage_rows": [_stage_row(name, sum(predicate(row) for row in rows), denominator) for name, predicate in predicates.items()],
    }


def build_trajectory_atlas(
    world_rows: Sequence[Mapping[str, Any]],
    track_rows: Sequence[Mapping[str, Any]],
    law_ids: Sequence[str],
) -> dict[str, Any]:
    ic_class = [
        _group_summary([row for row in world_rows if row["ic_id"] == ic_id], {"ic_id": ic_id})
        for ic_id in ("soup", "compact")
    ]
    law_ic = [
        _group_summary(
            [row for row in world_rows if row["law_id"] == law_id and row["ic_id"] == ic_id],
            {"law_id": law_id, "ic_id": ic_id},
        )
        for law_id in law_ids
        for ic_id in ("soup", "compact")
    ]
    difference_metrics = (
        "first_component_frame",
        "first_bounded_active_frame",
        "first_persistence_qualification_frame",
        "first_turnover_frame",
        "first_prefix_candidate_frame",
        "candidate_status_frames",
        "longest_candidate_episode_frames",
    )
    by_id = {row["world_id"]: row for row in world_rows}
    nominal: list[dict[str, Any]] = []
    for law_id in law_ids:
        for replicate in range(4):
            soup = by_id[f"{law_id}__soup__r{replicate:02d}"]
            compact = by_id[f"{law_id}__compact__r{replicate:02d}"]
            differences = {
                name: None
                if soup[name] is None or compact[name] is None
                else soup[name] - compact[name]
                for name in difference_metrics
            }
            nominal.append(
                {
                    "law_id": law_id,
                    "replicate": replicate,
                    "soup_world_id": soup["world_id"],
                    "compact_world_id": compact["world_id"],
                    "statistically_matched": False,
                    "differences": differences,
                }
            )
    candidate_worlds = [
        {
            "world_id": row["world_id"],
            "law_id": row["law_id"],
            "ic_id": row["ic_id"],
            "candidate_track_count": row["_candidate_track_count"],
            "primary_developmental_pathway": row["primary_developmental_pathway"],
            "terminal_state": row["terminal_state"],
            "first_prefix_candidate_frame": row["first_prefix_candidate_frame"],
            "candidate_status_frames": row["candidate_status_frames"],
            "candidate_episode_count": row["candidate_episode_count"],
            "longest_candidate_episode_frames": row["longest_candidate_episode_frames"],
            "candidate_episode_terminal": row["candidate_episode_terminal"],
            "right_censored": row["right_censored"],
            "trajectory_class": row["trajectory_class"],
        }
        for row in world_rows
        if row["committed_regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    ]
    formation_all = _binary_summary(sum(row["first_component_frame"] is not None for row in world_rows), len(world_rows))
    formation_by_ic = [
        {"group": {"ic_id": ic_id}, **_binary_summary(sum(row["first_component_frame"] is not None for row in world_rows if row["ic_id"] == ic_id), sum(row["ic_id"] == ic_id for row in world_rows))}
        for ic_id in ("soup", "compact")
    ]
    formation_by_law_ic = [
        {
            "group": {"law_id": law_id, "ic_id": ic_id},
            **_binary_summary(
                sum(row["first_component_frame"] is not None for row in world_rows if row["law_id"] == law_id and row["ic_id"] == ic_id),
                sum(row["law_id"] == law_id and row["ic_id"] == ic_id for row in world_rows),
            ),
        }
        for law_id in law_ids
        for ic_id in ("soup", "compact")
    ]
    formation_funnel = {"all_worlds": formation_all, "by_ic": formation_by_ic, "by_law_ic": formation_by_law_ic}
    maintenance_funnel = {
        "all_worlds": _world_maintenance_group(world_rows, {}),
        "by_ic": [
            _world_maintenance_group([row for row in world_rows if row["ic_id"] == ic_id], {"ic_id": ic_id})
            for ic_id in ("soup", "compact")
        ],
        "by_law_ic": [
            _world_maintenance_group(
                [row for row in world_rows if row["law_id"] == law_id and row["ic_id"] == ic_id],
                {"law_id": law_id, "ic_id": ic_id},
            )
            for law_id in law_ids
            for ic_id in ("soup", "compact")
        ],
    }
    return {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-ATLAS-v1",
        "world_count": len(world_rows),
        "ic_class": ic_class,
        "law_ic": law_ic,
        "nominal_index_alignment": nominal,
        "candidate_worlds": candidate_worlds,
        "formation_funnel": formation_funnel,
        "maintenance_funnel": maintenance_funnel,
    }


def _precursor_row(
    supporting: Sequence[str], denominator: int, available: bool,
) -> dict[str, Any]:
    required = math.ceil(0.75 * denominator)
    return {
        "numerator": len(supporting),
        "denominator": denominator,
        "required": required,
        "available": available,
        "qualified": bool(denominator > 0 and available and len(supporting) >= required),
        "world_ids": sorted(supporting),
    }


def build_analysis(
    world_rows: Sequence[Mapping[str, Any]],
    track_stage_rows: Sequence[Mapping[str, Any]],
    observations_by_world: Mapping[str, Sequence[Mapping[str, Any]]],
    law_ids: Sequence[str],
) -> dict[str, Any]:
    candidate_rows = [
        row for row in world_rows if row["committed_regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    ]
    class_counts = Counter(str(row["trajectory_class"]) for row in candidate_rows)
    dominant_class, dominant_count = (None, 0)
    if class_counts:
        dominant_class, dominant_count = min(class_counts.items(), key=lambda item: (-item[1], item[0]))
    transient_worlds = sorted(
        row["world_id"]
        for row in candidate_rows
        if row["longest_candidate_episode_frames"] < 32 or not row["candidate_episode_terminal"]
    )
    coherent = dominant_count >= 9
    transient_majority = len(transient_worlds) >= 6
    candidate_coherence = {
        "candidate_world_count": len(candidate_rows),
        "trajectory_class_counts": dict(sorted(class_counts.items())),
        "dominant_class": dominant_class,
        "dominant_count": dominant_count,
        "coherent": coherent,
        "transient_count": len(transient_worlds),
        "transient_majority": transient_majority,
    }
    candidate_duration = {
        "worlds": [
            {
                "world_id": row["world_id"],
                "candidate_status_frames": row["candidate_status_frames"],
                "candidate_episode_count": row["candidate_episode_count"],
                "longest_candidate_episode_frames": row["longest_candidate_episode_frames"],
                "candidate_episode_terminal": row["candidate_episode_terminal"],
            }
            for row in candidate_rows
        ],
        "status_frames_summary": _continuous_summary(row["candidate_status_frames"] for row in candidate_rows),
        "episode_count_summary": _continuous_summary(row["candidate_episode_count"] for row in candidate_rows),
        "longest_episode_summary": _continuous_summary(
            row["longest_candidate_episode_frames"] for row in candidate_rows
        ),
        "terminal_episode_count": sum(row["candidate_episode_terminal"] for row in candidate_rows),
    }
    censoring = {
        "right_censored_worlds": sum(row["right_censored"] for row in world_rows),
        "candidate_right_censored": sum(row["right_censored"] for row in candidate_rows),
        "candidate_status_touches_159": 0,
        "coordinate_seam_crossers": sum(row["coordinate_seam_crossed"] for row in world_rows),
        "winding_worlds": sum(row["ever_wound"] for row in world_rows),
    }
    candidate_touches: list[str] = []
    for row in candidate_rows:
        representative = row["representative_track_fingerprint"]
        rows = [obs for obs in observations_by_world[row["world_id"]] if obs["track_fingerprint"] == representative]
        if any(obs["frame"] == 159 and obs["prefix_candidate"] for obs in rows):
            candidate_touches.append(row["world_id"])
    censoring["candidate_status_touches_159"] = len(candidate_touches)

    # IC formation signature.
    soup_formed = sum(row["first_component_frame"] is not None for row in world_rows if row["ic_id"] == "soup")
    compact_formed = sum(
        row["first_component_frame"] is not None for row in world_rows if row["ic_id"] == "compact"
    )
    aggregate_difference = soup_formed / 32 - compact_formed / 32
    direction = "SOUP_GT_COMPACT" if aggregate_difference > 0 else "COMPACT_GT_SOUP" if aggregate_difference < 0 else "EQUAL"
    formation_law_rows: list[dict[str, Any]] = []
    for law_id in law_ids:
        soup = sum(
            row["first_component_frame"] is not None
            for row in world_rows
            if row["law_id"] == law_id and row["ic_id"] == "soup"
        )
        compact = sum(
            row["first_component_frame"] is not None
            for row in world_rows
            if row["law_id"] == law_id and row["ic_id"] == "compact"
        )
        difference = soup / 4 - compact / 4
        same = abs(difference) >= 0.25 and difference != 0 and difference * aggregate_difference > 0
        formation_law_rows.append(
            {
                "law_id": law_id,
                "soup_formed": soup,
                "compact_formed": compact,
                "per_ic_denominator": 4,
                "difference": difference,
                "same_direction_qualifies": same,
            }
        )
    formation_qualifying_laws = [row["law_id"] for row in formation_law_rows if row["same_direction_qualifies"]]
    ic_qualified = abs(aggregate_difference) >= 0.25 and len(formation_qualifying_laws) >= 6

    # Compact freeze and precursors.
    compact_frozen_rows = [row for row in world_rows if row["ic_id"] == "compact" and row["terminal_state"] == "FROZEN"]
    soup_frozen_rows = [row for row in world_rows if row["ic_id"] == "soup" and row["terminal_state"] == "FROZEN"]
    freeze_law_rows: list[dict[str, Any]] = []
    for law_id in law_ids:
        compact = sum(row["law_id"] == law_id for row in compact_frozen_rows)
        soup = sum(row["law_id"] == law_id for row in soup_frozen_rows)
        difference = compact / 4 - soup / 4
        freeze_law_rows.append(
            {
                "law_id": law_id,
                "compact_frozen": compact,
                "soup_frozen": soup,
                "per_ic_denominator": 4,
                "difference": difference,
                "qualifies": difference >= 0.25,
            }
        )
    freeze_qualifying_laws = [row["law_id"] for row in freeze_law_rows if row["qualifies"]]
    aggregate_freeze_difference = len(compact_frozen_rows) / 32 - len(soup_frozen_rows) / 32
    freeze_gate = aggregate_freeze_difference >= 0.25 and len(freeze_qualifying_laws) >= 6
    bond_support: list[str] = []
    heterogeneity_support: list[str] = []
    exchange_support: list[str] = []
    bond_available = True
    heterogeneity_available = True
    exchange_available = True
    for world in compact_frozen_rows:
        representative = world["representative_track_fingerprint"]
        observations = sorted(
            (row for row in observations_by_world[world["world_id"]] if row["track_fingerprint"] == representative),
            key=lambda row: row["frame"],
        )
        freeze_onset = world["terminal_freeze_onset"]
        if freeze_onset is None:
            raise AuditError("frozen world without onset")
        observation_frames = [row["frame"] for row in observations]
        pre = [row for row in observations if row["frame"] < freeze_onset]
        prefreeze_frames = [row["frame"] for row in pre]
        contiguous_prefreeze = bool(prefreeze_frames) and prefreeze_frames == list(
            range(observation_frames[0], freeze_onset)
        )
        bond_window_available = contiguous_prefreeze and prefreeze_frames[0] <= freeze_onset - 8
        heterogeneity_window_available = contiguous_prefreeze and len(prefreeze_frames) >= 8
        first16_frames = observation_frames[:16]
        exchange_window_available = (
            contiguous_prefreeze
            and len(first16_frames) == 16
            and first16_frames == list(range(observation_frames[0], observation_frames[0] + 16))
            and prefreeze_frames[-8:] == list(range(freeze_onset - 8, freeze_onset))
        )
        if not bond_window_available:
            bond_available = False
        saturation_frames = [
            row["frame"] for row in observations if row["internal_bond_saturation_fraction"] >= 0.5
        ]
        if bond_window_available and saturation_frames and min(saturation_frames) <= freeze_onset - 8:
            bond_support.append(world["world_id"])
        heterogeneity_runs = _runs(
            [row["frame"] for row in pre if row["matter_cv"] < 0.05 and row["resource_cv"] < 0.05]
        )
        if not heterogeneity_window_available:
            heterogeneity_available = False
        elif any(run[2] >= 8 for run in heterogeneity_runs):
            heterogeneity_support.append(world["world_id"])
        first16 = observations[:16]
        final8 = [row for row in observations if freeze_onset - 8 <= row["frame"] < freeze_onset]
        if not exchange_window_available or len(final8) != 8:
            exchange_available = False
        else:
            baseline = _median([row["matter_exchange_per_mass"] for row in first16])
            prefreeze = _median([row["matter_exchange_per_mass"] for row in final8])
            if baseline is None or baseline <= 0.0:
                exchange_available = False
            elif prefreeze is not None and prefreeze <= 0.25 * baseline:
                exchange_support.append(world["world_id"])
    n_compact_frozen = len(compact_frozen_rows)
    precursor_rows = {
        "BOND_SATURATION": _precursor_row(bond_support, n_compact_frozen, bond_available),
        "LOW_INTERNAL_HETEROGENEITY": _precursor_row(
            heterogeneity_support, n_compact_frozen, heterogeneity_available
        ),
        "REDUCED_MATERIAL_EXCHANGE": _precursor_row(exchange_support, n_compact_frozen, exchange_available),
    }
    true_precursors = [name for name, value in precursor_rows.items() if value["qualified"]]
    compact_available = all(value["available"] for value in precursor_rows.values())
    compact_qualified = freeze_gate and compact_available and len(true_precursors) == 1

    # Candidate destructive-transition signature.
    dissolution_support: list[str] = []
    high_exchange_support: list[str] = []
    destructive_unavailable: list[str] = []
    for world in candidate_rows:
        development = world["_representative_track_development"]
        selected_run = development["selected_run"]
        representative = world["representative_track_fingerprint"]
        observations = sorted(
            (row for row in observations_by_world[world["world_id"]] if row["track_fingerprint"] == representative),
            key=lambda row: row["frame"],
        )
        if selected_run is None:
            destructive_unavailable.append(world["world_id"])
            continue
        loss = world["_representative_dissolution_frame"]
        if loss is not None and loss < 159 and 0 <= loss - selected_run[1] <= 32:
            dissolution_support.append(world["world_id"])
        baseline_rows = [row for row in observations if row["frame"] < selected_run[0]]
        episode_rows = [row for row in observations if selected_run[0] <= row["frame"] <= selected_run[1]]
        baseline = _median([row["matter_exchange_per_mass"] for row in baseline_rows])
        episode = _median([row["matter_exchange_per_mass"] for row in episode_rows])
        if baseline is None or baseline <= 0.0 or episode is None:
            destructive_unavailable.append(world["world_id"])
        elif episode >= 2.0 * baseline:
            high_exchange_support.append(world["world_id"])
    destructive_available = not destructive_unavailable
    dissolution_qualified = len(dissolution_support) >= 9
    exchange_qualified = len(high_exchange_support) >= 9
    overlap = sorted(set(dissolution_support) & set(high_exchange_support))
    same_nine_or_single = (dissolution_qualified != exchange_qualified) or (
        dissolution_qualified and exchange_qualified and len(overlap) >= 9
    )
    if dissolution_qualified and not exchange_qualified:
        destructive_worlds = sorted(dissolution_support)
    elif exchange_qualified and not dissolution_qualified:
        destructive_worlds = sorted(high_exchange_support)
    elif dissolution_qualified and exchange_qualified and len(overlap) >= 9:
        destructive_worlds = overlap
    else:
        destructive_worlds = []
    destructive_laws = sorted({row["law_id"] for row in candidate_rows if row["world_id"] in destructive_worlds})
    destructive_qualified = (
        destructive_available
        and same_nine_or_single
        and len(destructive_worlds) >= 9
        and len(destructive_laws) >= 4
    )

    finite_support = sorted(
        row["world_id"] for row in candidate_rows if row["right_censored"] and row["world_id"] in candidate_touches
    )
    finite_laws = sorted({row["law_id"] for row in candidate_rows if row["world_id"] in finite_support})
    finite_qualified = len(finite_support) >= 9 and len(finite_laws) >= 4
    transient_brief = sorted(
        row["world_id"] for row in candidate_rows if row["longest_candidate_episode_frames"] < 32
    )
    transient_nonterminal = sorted(
        row["world_id"] for row in candidate_rows if not row["candidate_episode_terminal"]
    )

    signatures = {
        "IC_FORMATION_DEPENDENCE": {
            "qualified": ic_qualified,
            "available": True,
            "world_ids": sorted(row["world_id"] for row in world_rows if row["first_component_frame"] is not None),
            "law_ids": sorted(formation_qualifying_laws),
            "numerator": len(formation_qualifying_laws),
            "denominator": 8,
            "details": {
                "soup_formed": soup_formed,
                "compact_formed": compact_formed,
                "per_ic_denominator": 32,
                "aggregate_difference": aggregate_difference,
                "direction": direction,
                "law_rows": formation_law_rows,
                "qualifying_law_count": len(formation_qualifying_laws),
            },
            "interpretation": "OBSERVATIONAL_SIGNATURE_ONLY:IC_FORMATION_DEPENDENCE; never causal and never changes DEV_FEASIBILITY_FAIL",
        },
        "COMPACT_PREMATURE_FREEZE": {
            "qualified": compact_qualified,
            "available": compact_available,
            "world_ids": sorted(row["world_id"] for row in compact_frozen_rows),
            "law_ids": sorted(freeze_qualifying_laws),
            "numerator": len(freeze_qualifying_laws),
            "denominator": 8,
            "details": {
                "compact_frozen": len(compact_frozen_rows),
                "soup_frozen": len(soup_frozen_rows),
                "per_ic_denominator": 32,
                "law_rows": freeze_law_rows,
                "qualifying_law_count": len(freeze_qualifying_laws),
                "N_compact_frozen": n_compact_frozen,
                "precursors": precursor_rows,
                "unique_precursor": true_precursors[0] if len(true_precursors) == 1 else None,
            },
            "interpretation": "OBSERVATIONAL_SIGNATURE_ONLY:COMPACT_PREMATURE_FREEZE; never causal and never changes DEV_FEASIBILITY_FAIL",
        },
        "DESTRUCTIVE_TRANSITION_PROXIMITY": {
            "qualified": destructive_qualified,
            "available": destructive_available,
            "world_ids": destructive_worlds,
            "law_ids": destructive_laws,
            "numerator": len(destructive_worlds),
            "denominator": 11,
            "details": {
                "dissolution_subtype_world_ids": sorted(dissolution_support),
                "high_exchange_subtype_world_ids": sorted(high_exchange_support),
                "overlap_world_ids": overlap,
                "unavailable_world_ids": sorted(set(destructive_unavailable)),
                "dissolution_subtype_qualified": dissolution_qualified,
                "high_exchange_subtype_qualified": exchange_qualified,
                "same_nine_or_single_subtype": same_nine_or_single,
            },
            "interpretation": "OBSERVATIONAL_SIGNATURE_ONLY:DESTRUCTIVE_TRANSITION_PROXIMITY; never causal and never changes DEV_FEASIBILITY_FAIL",
        },
        "FINITE_HORIZON_CENSORING": {
            "qualified": finite_qualified,
            "available": True,
            "world_ids": finite_support,
            "law_ids": finite_laws,
            "numerator": len(finite_support),
            "denominator": 11,
            "details": {
                "candidate_right_censored": sum(row["right_censored"] for row in candidate_rows),
                "candidate_status_touches_159": len(candidate_touches),
                "supporting_law_count": len(finite_laws),
                "supporting_world_ids": finite_support,
            },
            "interpretation": "OBSERVATIONAL_SIGNATURE_ONLY:FINITE_HORIZON_CENSORING; never causal and never changes DEV_FEASIBILITY_FAIL",
        },
        "TRANSIENT_THRESHOLD_CROSSING": {
            "qualified": transient_majority,
            "available": True,
            "world_ids": transient_worlds,
            "law_ids": sorted({row["law_id"] for row in candidate_rows if row["world_id"] in transient_worlds}),
            "numerator": len(transient_worlds),
            "denominator": 11,
            "details": {
                "brief_world_ids": transient_brief,
                "nonterminal_world_ids": transient_nonterminal,
                "union_world_ids": transient_worlds,
                "transient_count": len(transient_worlds),
            },
            "interpretation": "OBSERVATIONAL_SIGNATURE_ONLY:TRANSIENT_THRESHOLD_CROSSING; never causal and never changes DEV_FEASIBILITY_FAIL",
        },
    }
    availability = {name: bool(value["available"]) for name, value in signatures.items()}
    unavailable_reasons: list[str] = []
    if not compact_available:
        unavailable_reasons.append("COMPACT_PREMATURE_FREEZE precursor window unavailable")
    if not destructive_available:
        unavailable_reasons.append("DESTRUCTIVE_TRANSITION_PROXIMITY same-track baseline unavailable")
    availability["unavailable_reasons"] = unavailable_reasons
    qualified_mechanisms = [
        name
        for name in (
            "IC_FORMATION_DEPENDENCE",
            "COMPACT_PREMATURE_FREEZE",
            "DESTRUCTIVE_TRANSITION_PROXIMITY",
            "FINITE_HORIZON_CENSORING",
        )
        if signatures[name]["qualified"]
    ]
    mechanism_available = all(signatures[name]["available"] for name in signatures if name != "TRANSIENT_THRESHOLD_CROSSING")
    outcome = decide_autopsy_outcome(
        True,
        len(candidate_rows) == 11,
        transient_majority,
        coherent,
        mechanism_available,
        qualified_mechanisms,
    )
    truth = {
        "AUDIT_INVALID": False,
        "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES": outcome == "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES",
        "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS": outcome == "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS",
        "RAW_INSUFFICIENT": outcome == "RAW_INSUFFICIENT",
        "selected": outcome,
    }
    # Formation and maintenance estimands.
    cumulative = [
        {
            "frame": frame,
            "all_formed": sum(
                row["first_component_frame"] is not None and row["first_component_frame"] <= frame for row in world_rows
            ),
            "soup_formed": sum(
                row["ic_id"] == "soup"
                and row["first_component_frame"] is not None
                and row["first_component_frame"] <= frame
                for row in world_rows
            ),
            "compact_formed": sum(
                row["ic_id"] == "compact"
                and row["first_component_frame"] is not None
                and row["first_component_frame"] <= frame
                for row in world_rows
            ),
            "all_denominator": 64,
            "per_ic_denominator": 32,
        }
        for frame in range(160)
    ]
    a_formation = {
        "all": {"group": {}, **_binary_summary(soup_formed + compact_formed, 64)},
        "by_ic": [
            {"group": {"ic_id": "soup"}, **_binary_summary(soup_formed, 32)},
            {"group": {"ic_id": "compact"}, **_binary_summary(compact_formed, 32)},
        ],
        "by_law_ic": [
            {
                "group": {"law_id": law_id, "ic_id": ic_id},
                **_binary_summary(
                    sum(
                        row["first_component_frame"] is not None
                        for row in world_rows
                        if row["law_id"] == law_id and row["ic_id"] == ic_id
                    ),
                    4,
                ),
            }
            for law_id in law_ids
            for ic_id in ("soup", "compact")
        ],
        "cumulative_by_frame": cumulative,
    }
    b_world = {
        "all": _world_maintenance_group(world_rows, {}),
        "by_ic": [
            _world_maintenance_group([row for row in world_rows if row["ic_id"] == ic_id], {"ic_id": ic_id})
            for ic_id in ("soup", "compact")
        ],
        "by_law_ic": [
            _world_maintenance_group(
                [row for row in world_rows if row["law_id"] == law_id and row["ic_id"] == ic_id],
                {"law_id": law_id, "ic_id": ic_id},
            )
            for law_id in law_ids
            for ic_id in ("soup", "compact")
        ],
        "stages": ["formed", "bounded_active", "persistent", "turnover", "prefix_candidate", "stable_candidate", "terminal_persistence"],
        "unit": "original_world",
        "precision_warning": "Four worlds per law/IC are descriptive and not a precise probability estimate.",
    }
    b_track = {
        "all": _track_maintenance_group(track_stage_rows, {}),
        "by_ic": [
            _track_maintenance_group([row for row in track_stage_rows if row["ic_id"] == ic_id], {"ic_id": ic_id})
            for ic_id in ("soup", "compact")
        ],
        "by_law_ic": [
            _track_maintenance_group(
                [row for row in track_stage_rows if row["law_id"] == law_id and row["ic_id"] == ic_id],
                {"law_id": law_id, "ic_id": ic_id},
            )
            for law_id in law_ids
            for ic_id in ("soup", "compact")
        ],
        "stages": ["formed", "bounded_active", "persistent", "turnover", "prefix_candidate", "stable_candidate", "terminal_persistence"],
        "unit": "diagnostic_track",
        "precision_warning": "Track rows are nested diagnostics and never replace the original-world denominator.",
    }
    estimands = {
        "A_formation": a_formation,
        "B_conditional_maintenance_world": b_world,
        "B_conditional_maintenance_track": b_track,
        "gate_conflation_note": "Stage B's unconditional region gate combined formation probability from a neutral IC with maintenance and turnover conditional on formation; this decomposition cannot reclassify or rescue Stage B.",
    }
    compact_static = {
        "compact_frozen_count": len(compact_frozen_rows),
        "soup_frozen_count": len(soup_frozen_rows),
        "bond_saturation_precursor": precursor_rows["BOND_SATURATION"],
        "low_internal_heterogeneity_precursor": precursor_rows["LOW_INTERNAL_HETEROGENEITY"],
        "reduced_material_exchange_precursor": precursor_rows["REDUCED_MATERIAL_EXCHANGE"],
        "low_throughput_definition_only": True,
        "common_precursor_count": len(true_precursors),
    }
    roadmap_text = {
        "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS": "Human review may consider a fresh, separately preregistered developmental design testing the single observational signature.",
        "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES": "Do not select or promote candidate worlds; any future work requires a fresh pre-data design aimed at formation and stability separately.",
        "RAW_INSUFFICIENT": "Persisted Stage-B variables do not select a unique developmental account; stop unless a fresh measurement design is authorized.",
    }[outcome]
    return {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-ANALYSIS-v1",
        "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
        "autopsy_outcome": outcome,
        "audit_gates": {
            "input_bindings": True,
            "git_blob_identity": True,
            "raw_layout": True,
            "numerical_qualification": True,
            "classification_byte_identity": True,
            "candidate_set_identity": len(candidate_rows) == 11,
            "world_count": len(world_rows) == 64,
            "valid": True,
        },
        "candidate_coherence": candidate_coherence,
        "candidate_duration": candidate_duration,
        "censoring": censoring,
        "compact_static_audit": compact_static,
        "observational_signatures_consistent_with": signatures,
        "signature_availability": availability,
        "formation_maintenance_estimands": estimands,
        "outcome_truth_table": truth,
        "bounded_roadmap": {
            "recommendation": roadmap_text,
            "allowed_next_action": "human review of this raw-only developmental autopsy",
            "forbidden_actions": [
                "Stage C",
                "candidate promotion or subset selection",
                "threshold or two-of-four revision",
                "family extension, retry or new seed",
                "causal, memory, ownership or individuality claim",
            ],
        },
    }


def _bootstrap_json(repo: Path, relative: str) -> tuple[dict[str, Any], bytes]:
    path = repo / relative
    if _has_reparse_or_symlink(repo, path):
        raise AuditError(f"bootstrap reparse/symlink rejected {relative}")
    if _repo_relative(repo, path) != relative.replace("\\", "/"):
        raise AuditError(f"bootstrap path mismatch {relative}")
    data = path.read_bytes()
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid bootstrap JSON {relative}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"bootstrap JSON is not object {relative}")
    return value, data


def load_controls(
    repo: Path, plan_relative: str, allowlist_relative: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], set[str], dict[str, bytes]]:
    plan, plan_bytes = _bootstrap_json(repo, plan_relative)
    allowlist, allowlist_bytes = _bootstrap_json(repo, allowlist_relative)
    if plan["accepted_parent"] != "c31bf27ea80a6a3dcc60d0ec5380f668358671ff":
        raise AuditError("accepted parent drift")
    binding = plan["input_bindings"]["source_allowlist"]
    if binding["path"] != allowlist_relative or sha256_bytes(allowlist_bytes) != binding["sha256"]:
        raise AuditError("source allowlist binding mismatch")
    allowed_relatives = set(allowlist["scientific_inputs"]["metadata"])
    allowed_relatives.update(allowlist["scientific_inputs"]["physics_shards"])
    allowed_relatives.update(
        path
        for path in allowlist["authorized_new_paths"]
        if not path.endswith("/") and (repo / path).exists()
    )
    allowed_relatives.update((plan_relative, allowlist_relative))
    allowed = {normalize_allowlist_path(path) for path in allowed_relatives}
    protocol_binding = plan["input_bindings"]["reconstruction_protocol"]
    protocol_bytes = read_allowed_bytes(repo, protocol_binding["path"], allowed)
    if sha256_bytes(protocol_bytes) != protocol_binding["sha256"]:
        raise AuditError("reconstruction protocol binding mismatch")
    try:
        protocol = json.loads(protocol_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError("invalid reconstruction protocol") from exc
    controls = {
        plan_relative: plan_bytes,
        allowlist_relative: allowlist_bytes,
        protocol_binding["path"]: protocol_bytes,
    }
    return plan, allowlist, protocol, allowed, controls


def _git_tree_physics(repo: Path, commit: str, root: str) -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", commit, "--", root],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    blobs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        metadata, path = line.split("\t", 1)
        mode, kind, oid = metadata.split(" ")
        if kind == "blob" and path.endswith("/physics.npz"):
            if mode != "100644" or path in blobs:
                raise AuditError("unexpected physics tree entry")
            blobs[path] = oid
    return blobs


def _git_blob_at(repo: Path, commit: str, relative: str) -> str:
    result = subprocess.run(
        ["git", "ls-tree", commit, "--", relative],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise AuditError(f"accepted-parent metadata path missing {relative}")
    metadata, returned = lines[0].split("\t", 1)
    mode, kind, oid = metadata.split(" ")
    if returned != relative or mode != "100644" or kind != "blob":
        raise AuditError(f"unexpected accepted-parent metadata entry {relative}")
    return oid


def verify_inputs_before_arrays(
    repo: Path,
    plan: Mapping[str, Any],
    allowlist: Mapping[str, Any],
    allowed: set[str],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, bytes],
    list[dict[str, Any]],
    dict[str, str],
]:
    bindings = plan["input_bindings"]
    metadata_rows: list[dict[str, Any]] = []
    metadata_values: dict[str, dict[str, Any]] = {}
    metadata_bytes: dict[str, bytes] = {}
    commit = bindings["accepted_parent_physics_git_tree"]["commit"]
    for name in ("manifest", "root_manifest", "committed_classification"):
        binding = bindings[name]
        data = read_allowed_bytes(repo, binding["path"], allowed)
        if sha256_bytes(data) != binding["sha256"]:
            raise AuditError(f"{name} SHA-256 mismatch")
        try:
            value = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AuditError(f"invalid {name}") from exc
        metadata_values[name] = value
        metadata_bytes[name] = data
        expected_oid = _git_blob_at(repo, commit, binding["path"])
        actual_oid = git_blob_oid_bytes(data)
        if actual_oid != expected_oid:
            raise AuditError(f"accepted-parent blob mismatch {binding['path']}")
        metadata_rows.append(
            {
                "path": binding["path"],
                "bytes": len(data),
                "sha256": sha256_bytes(data),
                "accepted_parent_git_blob_oid": expected_oid,
                "git_blob_match": True,
            }
        )
    manifest = metadata_values["manifest"]
    root_manifest = metadata_values["root_manifest"]
    committed_classification = metadata_values["committed_classification"]
    if manifest["execution"]["world_count"] != 64 or len(manifest["execution"]["world_ids"]) != 64:
        raise AuditError("manifest population mismatch")
    root_gate = bindings["root_manifest"]["semantic_gate"]
    if (
        set(root_manifest) != set(root_gate["top_keys"])
        or root_manifest.get("schema") != root_gate["schema"]
        or root_manifest.get("world_count") != root_gate["world_count"]
        or root_manifest.get("disposition") != root_gate["disposition"]
    ):
        raise AuditError("root manifest disposition/population mismatch")
    if root_manifest["manifest_sha256"] != bindings["manifest"]["sha256"]:
        raise AuditError("root manifest parent mismatch")
    if root_manifest["classification_sha256"] != bindings["committed_classification"]["sha256"]:
        raise AuditError("root classification parent mismatch")
    root_shards = root_manifest.get("shards", [])
    if (
        len(root_shards) != 64
        or any(set(row) != set(root_gate["shard_row_keys"]) for row in root_shards)
        or any(row.get("status") != root_gate["shard_status"] for row in root_shards)
        or {row.get("world_id") for row in root_shards} != set(manifest["execution"]["world_ids"])
    ):
        raise AuditError("root shard enrollment/status mismatch")
    if root_manifest.get("classification_bytes") != len(metadata_bytes["committed_classification"]):
        raise AuditError("root classification byte-count mismatch")
    expected_paths = [
        f"results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV/{world_id}/physics.npz"
        for world_id in manifest["execution"]["world_ids"]
    ]
    actual_paths = list(allowlist["scientific_inputs"]["physics_shards"])
    if actual_paths != expected_paths or len(set(actual_paths)) != 64:
        raise AuditError("physics allowlist sequence mismatch")
    tree = _git_tree_physics(repo, commit, "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV")
    if set(tree) != set(expected_paths) or len(tree) != 64:
        raise AuditError("accepted-parent physics tree mismatch")
    records = "".join(f"{path}\t{tree[path]}\n" for path in sorted(tree))
    if sha256_bytes(records.encode("utf-8")) != bindings["accepted_parent_physics_git_tree"]["aggregate_sha256"]:
        raise AuditError("physics tree aggregate mismatch")
    physics_rows: list[dict[str, Any]] = []
    for relative in expected_paths:
        normalized = normalize_allowlist_path(relative)
        if normalized not in allowed:
            raise AuditError(f"physics path not authorized {relative}")
        data = read_allowed_bytes(repo, relative, allowed)
        actual_oid = git_blob_oid_bytes(data)
        if actual_oid != tree[relative]:
            raise AuditError(f"physics blob mismatch {relative}")
        physics_rows.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
                "accepted_parent_git_blob_oid": tree[relative],
                "git_blob_match": True,
            }
        )
    return (
        manifest,
        root_manifest,
        committed_classification,
        metadata_bytes,
        metadata_rows + physics_rows,
        tree,
    )


def _world_identity(world_id: str) -> tuple[str, str, int]:
    law_id, ic_id, replicate = world_id.split("__")
    return law_id, ic_id, int(replicate[1:])


def process_world(
    repo: Path,
    relative: str,
    world_id: str,
    protocol: Mapping[str, Any],
    committed_world: Mapping[str, Any],
    allowed: set[str],
    authenticated_row: Mapping[str, Any],
) -> dict[str, Any]:
    data = read_allowed_bytes(repo, relative, allowed)
    if (
        len(data) != authenticated_row["bytes"]
        or sha256_bytes(data) != authenticated_row["sha256"]
        or git_blob_oid_bytes(data) != authenticated_row["accepted_parent_git_blob_oid"]
    ):
        raise AuditError(f"physics bytes changed after authentication {relative}")
    arrays = safe_load_npz(data, protocol)
    qualification = validate_raw_arrays(arrays)
    components = [detect_components(arrays["state_m"][frame], frame=frame) for frame in range(160)]
    tracks, events = track_components(components)
    for event in events:
        event["world_id"] = world_id
    observations_by_track, summaries = build_track_observations(world_id, arrays, components, tracks)
    regime, candidate_track_ids = classify_world(summaries, components, tracks)
    transition = developmental_world_summary(
        world_id,
        committed_world["regime"],
        regime,
        components,
        tracks,
        observations_by_track,
        summaries,
        events,
        candidate_track_ids,
    )
    law_id, ic_id, replicate = _world_identity(world_id)
    canonical_track_ids = sorted(
        tracks,
        key=lambda track_id: (
            tracks[track_id].points[0][0],
            components[tracks[track_id].points[0][0]][tracks[track_id].points[0][1]].cells,
        ),
    )
    flattened_observations = [row for track_id in canonical_track_ids for row in observations_by_track[track_id]]
    track_stage_rows: list[dict[str, Any]] = []
    for track_id in canonical_track_ids:
        development = transition["_track_development"][track_id]
        track_stage_rows.append(
            {
                "world_id": world_id,
                "law_id": law_id,
                "ic_id": ic_id,
                "replicate": replicate,
                "track_id": track_id,
                "track_fingerprint": development["fingerprint"],
                "t_active": development["t_active"],
                "t_persistence": development["t_persistence"],
                "t_turn": development["t_turn"],
                "t_prefix": development["t_prefix"],
                "stable": development["stable"],
                "terminal_persistence": tracks[track_id].points[-1][0] == 159,
            }
        )
    return {
        "world_id": world_id,
        "law_id": law_id,
        "ic_id": ic_id,
        "replicate": replicate,
        "regime": regime,
        "candidate_track_ids": candidate_track_ids,
        "qualification": qualification,
        "transition": transition,
        "observations": flattened_observations,
        "events": events,
        "track_stage_rows": track_stage_rows,
        "track_count": len(tracks),
    }


def _strip_internal_world(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def build_package(
    repo: Path,
    plan_relative: str,
    allowlist_relative: str,
) -> tuple[dict[str, bytes], dict[str, int], str, dict[str, str]]:
    plan, allowlist, protocol, allowed, controls = load_controls(repo, plan_relative, allowlist_relative)
    _validate_planned_paths(plan)
    (
        manifest,
        root_manifest,
        committed_classification,
        metadata_bytes,
        input_rows,
        tree,
    ) = verify_inputs_before_arrays(repo, plan, allowlist, allowed)
    authenticated_by_path = {row["path"]: row for row in input_rows}
    committed_by_id = {row["world_id"]: row for row in committed_classification["worlds"]}
    world_results: list[dict[str, Any]] = []
    for world_id, relative in zip(
        manifest["execution"]["world_ids"], allowlist["scientific_inputs"]["physics_shards"], strict=True
    ):
        world_results.append(
            process_world(
                repo,
                relative,
                world_id,
                protocol,
                committed_by_id[world_id],
                allowed,
                authenticated_by_path[relative],
            )
        )
    recomputed = build_recomputed_classification(
        manifest, plan["input_bindings"]["manifest"]["sha256"], world_results
    )
    recomputed_bytes = canonical_json_bytes(recomputed)
    committed_bytes = metadata_bytes["committed_classification"]
    if recomputed_bytes != committed_bytes:
        raise AuditError(
            "classification byte identity failed: "
            f"recomputed={sha256_bytes(recomputed_bytes)} committed={sha256_bytes(committed_bytes)}"
        )
    if recomputed["disposition"] != "DEV_FEASIBILITY_FAIL" or recomputed["candidate_regions"]:
        raise AuditError("immutable Stage-B disposition drift")
    world_rows_internal = [result["transition"] for result in world_results]
    world_rows = [_strip_internal_world(row) for row in world_rows_internal]
    observations = [row for result in world_results for row in result["observations"]]
    events = [row for result in world_results for row in result["events"]]
    track_stage_rows = [row for result in world_results for row in result["track_stage_rows"]]
    observations_by_world = {
        result["world_id"]: result["observations"] for result in world_results
    }
    law_ids = [law["law_id"] for law in manifest["law_family"]["laws"]]
    atlas = build_trajectory_atlas(world_rows_internal, track_stage_rows, law_ids)
    analysis = build_analysis(world_rows_internal, track_stage_rows, observations_by_world, law_ids)
    candidate_world_ids = sorted(
        row["world_id"]
        for row in committed_classification["worlds"]
        if row["regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    )
    if len(candidate_world_ids) != 11:
        raise AuditError("committed candidate count drift")
    runtime = {
        "interpreter": "C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe",
        "python": "3.12.10",
        "numpy": "2.5.1",
        "pytest": "8.4.2",
        "byteorder": "little",
    }
    if (
        sys.version_info[:3] != (3, 12, 10)
        or np.__version__ != "2.5.1"
        or pytest.__version__ != "8.4.2"
        or sys.byteorder != "little"
        or Path(sys.executable).resolve() != Path("C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe").resolve()
    ):
        raise AuditError("runtime binding mismatch")
    integrity = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-INTEGRITY-v1",
        "accepted_parent": plan["accepted_parent"],
        "plan_sha256": sha256_bytes(controls[plan_relative]),
        "protocol_sha256": sha256_bytes(controls[plan["input_bindings"]["reconstruction_protocol"]["path"]]),
        "allowlist_sha256": sha256_bytes(controls[allowlist_relative]),
        "runtime": runtime,
        "input_files": input_rows,
        "git_tree_binding": {
            "blob_count": len(tree),
            "aggregate_sha256": plan["input_bindings"]["accepted_parent_physics_git_tree"]["aggregate_sha256"],
            "all_match": True,
        },
        "raw_inventory": {"key_count": 46, "keys": sorted(expected_inventory(protocol))},
        "qualification_gates": {
            "world_count": 64,
            "all_layout_valid": True,
            "all_numerically_valid": True,
            "maximum_reference_error": max(result["qualification"]["maximum_reference_error"] for result in world_results),
            "maximum_transport_error": max(result["qualification"]["maximum_transport_error"] for result in world_results),
            "maximum_matter_residual": max(result["qualification"]["maximum_matter_residual"] for result in world_results),
            "maximum_energy_residual": max(result["qualification"]["maximum_energy_residual"] for result in world_results),
        },
        "audit_valid": True,
    }
    world_transitions = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-WORLD-TRANSITIONS-v1",
        "world_count": len(world_rows),
        "worlds": world_rows,
    }
    files = {
        "integrity.json": canonical_json_bytes(integrity),
        "recomputed_classification.json": recomputed_bytes,
        "world_transitions.json": canonical_json_bytes(world_transitions),
        "track_observations.jsonl": canonical_jsonl_bytes(observations),
        "events.jsonl": canonical_jsonl_bytes(events),
        "trajectory_atlas.json": canonical_json_bytes(atlas),
        "analysis.json": canonical_json_bytes(analysis),
    }
    counts = {
        "worlds": 64,
        "tracks": sum(result["track_count"] for result in world_results),
        "track_observations": len(observations),
        "events": len(events),
        "candidate_worlds": 11,
    }
    control_hashes = {
        "plan_sha256": sha256_bytes(controls[plan_relative]),
        "protocol_sha256": sha256_bytes(
            controls[plan["input_bindings"]["reconstruction_protocol"]["path"]]
        ),
        "allowlist_sha256": sha256_bytes(controls[allowlist_relative]),
    }
    return files, counts, analysis["autopsy_outcome"], control_hashes


def write_package(
    output_root: Path,
    files: Mapping[str, bytes],
    counts: Mapping[str, int],
    outcome: str,
    plan_sha256: str,
    protocol_sha256: str,
    allowlist_sha256: str,
) -> None:
    expected_payloads = {
        "integrity.json",
        "recomputed_classification.json",
        "world_transitions.json",
        "track_observations.jsonl",
        "events.jsonl",
        "trajectory_atlas.json",
        "analysis.json",
    }
    if set(files) != expected_payloads:
        raise AuditError("closed publication payload inventory mismatch")
    partial = Path(str(output_root) + ".partial")
    if os.path.lexists(output_root) or os.path.lexists(partial):
        raise AuditError(f"no-overwrite output root exists: {output_root} or {partial}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    partial.mkdir()
    file_rows: list[dict[str, Any]] = []
    for name in sorted(files):
        data = files[name]
        path = partial / name
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        file_rows.append({"path": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    complete = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-COMPLETE-v1",
        "status": "COMPLETE",
        "accepted_parent": "c31bf27ea80a6a3dcc60d0ec5380f668358671ff",
        "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
        "autopsy_outcome": outcome,
        "plan_sha256": plan_sha256,
        "protocol_sha256": protocol_sha256,
        "allowlist_sha256": allowlist_sha256,
        "files": file_rows,
        "counts": dict(counts),
    }
    complete_bytes = canonical_json_bytes(complete)
    with (partial / "COMPLETE.json").open("xb") as handle:
        handle.write(complete_bytes)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, output_root)


PACKAGE_NAMES = (
    "COMPLETE.json",
    "analysis.json",
    "events.jsonl",
    "integrity.json",
    "recomputed_classification.json",
    "track_observations.jsonl",
    "trajectory_atlas.json",
    "world_transitions.json",
)


def _validate_scoped_path(
    repo: Path,
    literal: str,
    expected: str,
    *,
    must_exist: bool,
) -> Path:
    if literal != expected:
        raise AuditError(f"path is not the frozen target: {literal}")
    normalized = normalize_allowlist_path(literal)
    path = repo / literal
    current = path
    if must_exist and not os.path.lexists(path):
        raise AuditError(f"required path absent: {literal}")
    while not os.path.lexists(current):
        if current.parent == current:
            raise AuditError(f"no existing path ancestor: {literal}")
        current = current.parent
    if _has_reparse_or_symlink(repo, current):
        raise AuditError(f"reparse/symlink rejected: {literal}")
    try:
        resolved = path.resolve(strict=must_exist)
        relative = resolved.relative_to(repo.resolve(strict=True)).as_posix().casefold()
    except (FileNotFoundError, ValueError) as exc:
        raise AuditError(f"path escapes repository: {literal}") from exc
    if relative != normalized:
        raise AuditError(f"resolved path mismatch: {literal}")
    return path


def _validate_planned_paths(plan: Mapping[str, Any]) -> None:
    planned = plan.get("planned_outputs", {})
    if (
        planned.get("primary_root") != PRIMARY_ROOT_RELATIVE
        or planned.get("independent_root") != INDEPENDENT_ROOT_RELATIVE
        or planned.get("comparison_file") != QUALIFICATION_RELATIVE
        or planned.get("files") != [
            "integrity.json",
            "recomputed_classification.json",
            "world_transitions.json",
            "track_observations.jsonl",
            "events.jsonl",
            "trajectory_atlas.json",
            "analysis.json",
            "COMPLETE.json",
        ]
    ):
        raise AuditError("frozen planned-output contract mismatch")


def _require_absent_publication_root(path: Path) -> None:
    partial = Path(str(path) + ".partial")
    if os.path.lexists(path) or os.path.lexists(partial):
        raise AuditError(f"no-overwrite output root exists: {path} or {partial}")


def _decode_json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid JSON in {label}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"JSON object required in {label}")
    return value


def _validated_package_bytes(
    repo: Path,
    root_relative: str,
    expected_root: str,
    control_hashes: Mapping[str, str],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = _validate_scoped_path(repo, root_relative, expected_root, must_exist=True)
    if not root.is_dir() or os.path.lexists(Path(str(root) + ".partial")):
        raise AuditError(f"package root is not a closed directory: {root_relative}")
    entries = list(root.iterdir())
    if sorted(entry.name for entry in entries) != sorted(PACKAGE_NAMES):
        raise AuditError(f"closed package inventory mismatch: {root_relative}")
    for entry in entries:
        if _has_reparse_or_symlink(repo, entry) or not entry.is_file():
            raise AuditError(f"unsafe package entry: {entry}")
    captured = {name: (root / name).read_bytes() for name in PACKAGE_NAMES}
    complete = _decode_json_object(captured["COMPLETE.json"], f"{root_relative}/COMPLETE.json")
    if set(complete) != {
        "schema",
        "status",
        "accepted_parent",
        "immutable_stage_b_disposition",
        "autopsy_outcome",
        "plan_sha256",
        "protocol_sha256",
        "allowlist_sha256",
        "files",
        "counts",
    }:
        raise AuditError(f"COMPLETE schema mismatch: {root_relative}")
    if (
        complete["schema"] != "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-COMPLETE-v1"
        or complete["status"] != "COMPLETE"
        or complete["accepted_parent"] != "c31bf27ea80a6a3dcc60d0ec5380f668358671ff"
        or complete["immutable_stage_b_disposition"] != "DEV_FEASIBILITY_FAIL"
        or complete["autopsy_outcome"] not in AUTOPSY_OUTCOMES[:-1]
        or complete["plan_sha256"] != control_hashes["plan_sha256"]
        or complete["protocol_sha256"] != control_hashes["protocol_sha256"]
        or complete["allowlist_sha256"] != control_hashes["allowlist_sha256"]
    ):
        raise AuditError(f"COMPLETE binding mismatch: {root_relative}")
    expected_data_names = sorted(name for name in PACKAGE_NAMES if name != "COMPLETE.json")
    file_rows = complete.get("files")
    if not isinstance(file_rows, list) or [row.get("path") for row in file_rows] != expected_data_names:
        raise AuditError(f"COMPLETE file-row order/inventory mismatch: {root_relative}")
    for row in file_rows:
        if set(row) != {"path", "bytes", "sha256"}:
            raise AuditError(f"COMPLETE file-row schema mismatch: {root_relative}")
        data = captured[row["path"]]
        if row["bytes"] != len(data) or row["sha256"] != sha256_bytes(data):
            raise AuditError(f"COMPLETE file hash mismatch: {root_relative}/{row['path']}")
    if set(complete.get("counts", {})) != {
        "worlds",
        "tracks",
        "track_observations",
        "events",
        "candidate_worlds",
    }:
        raise AuditError(f"COMPLETE counts schema mismatch: {root_relative}")
    analysis = _decode_json_object(captured["analysis.json"], f"{root_relative}/analysis.json")
    integrity = _decode_json_object(captured["integrity.json"], f"{root_relative}/integrity.json")
    classification = _decode_json_object(
        captured["recomputed_classification.json"], f"{root_relative}/recomputed_classification.json"
    )
    if (
        analysis.get("immutable_stage_b_disposition") != "DEV_FEASIBILITY_FAIL"
        or analysis.get("autopsy_outcome") != complete["autopsy_outcome"]
        or classification.get("disposition") != "DEV_FEASIBILITY_FAIL"
        or classification.get("candidate_regions") != []
        or integrity.get("audit_valid") is not True
        or integrity.get("plan_sha256") != control_hashes["plan_sha256"]
        or integrity.get("protocol_sha256") != control_hashes["protocol_sha256"]
        or integrity.get("allowlist_sha256") != control_hashes["allowlist_sha256"]
    ):
        raise AuditError(f"package semantic binding mismatch: {root_relative}")
    return captured, complete


def compare_packages(
    repo: Path,
    primary_relative: str,
    independent_relative: str,
    qualification_relative: str,
    plan: Mapping[str, Any],
    controls: Mapping[str, bytes],
) -> None:
    _validate_planned_paths(plan)
    qualification = _validate_scoped_path(
        repo, qualification_relative, QUALIFICATION_RELATIVE, must_exist=False
    )
    if os.path.lexists(qualification):
        raise AuditError(f"qualification already exists: {qualification_relative}")
    control_hashes = {
        "plan_sha256": sha256_bytes(controls[PLAN_RELATIVE]),
        "protocol_sha256": sha256_bytes(
            controls[plan["input_bindings"]["reconstruction_protocol"]["path"]]
        ),
        "allowlist_sha256": sha256_bytes(controls[ALLOWLIST_RELATIVE]),
    }
    primary_data, primary_complete = _validated_package_bytes(
        repo, primary_relative, PRIMARY_ROOT_RELATIVE, control_hashes
    )
    independent_data, independent_complete = _validated_package_bytes(
        repo, independent_relative, INDEPENDENT_ROOT_RELATIVE, control_hashes
    )
    rows: list[dict[str, Any]] = []
    for name in PACKAGE_NAMES:
        primary_file = primary_data[name]
        independent_file = independent_data[name]
        equal = primary_file == independent_file
        rows.append(
            {
                "path": name,
                "primary_bytes": len(primary_file),
                "primary_sha256": sha256_bytes(primary_file),
                "independent_bytes": len(independent_file),
                "independent_sha256": sha256_bytes(independent_file),
                "byte_identical": equal,
            }
        )
    if not all(row["byte_identical"] for row in rows):
        mismatches = [row["path"] for row in rows if not row["byte_identical"]]
        raise AuditError(f"independent package mismatch: {mismatches}")
    if primary_complete != independent_complete:
        raise AuditError("COMPLETE semantic mismatch")
    qualification_object = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-QUALIFICATION-v1",
        "status": "QUALIFIED",
        "accepted_parent": "c31bf27ea80a6a3dcc60d0ec5380f668358671ff",
        "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
        "autopsy_outcome": primary_complete["autopsy_outcome"],
        "primary_complete_sha256": sha256_bytes(primary_data["COMPLETE.json"]),
        "independent_complete_sha256": sha256_bytes(independent_data["COMPLETE.json"]),
        "compared_files": rows,
        "byte_identical": True,
        "review_required": True,
    }
    data = canonical_json_bytes(qualification_object)
    qualification.parent.mkdir(parents=True, exist_ok=True)
    with qualification.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan")
    parser.add_argument("--allowlist")
    parser.add_argument("--output-root")
    parser.add_argument("--compare-only", action="store_true")
    parser.add_argument("--primary-root")
    parser.add_argument("--independent-root")
    parser.add_argument("--qualification")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    repo = Path.cwd()
    try:
        if args.compare_only:
            if not args.primary_root or not args.independent_root or not args.qualification:
                raise AuditError("compare-only paths required")
            if any((args.plan, args.allowlist, args.output_root)):
                raise AuditError("normal-run arguments forbidden in compare-only mode")
            if (
                args.primary_root != PRIMARY_ROOT_RELATIVE
                or args.independent_root != INDEPENDENT_ROOT_RELATIVE
                or args.qualification != QUALIFICATION_RELATIVE
            ):
                raise AuditError("compare-only mode requires the frozen publication paths")
            plan, _allowlist, _protocol, _allowed, controls = load_controls(
                repo, PLAN_RELATIVE, ALLOWLIST_RELATIVE
            )
            compare_packages(
                repo,
                args.primary_root,
                args.independent_root,
                args.qualification,
                plan,
                controls,
            )
            print("INDEPENDENT_BYTE_IDENTITY_QUALIFIED")
            return 0
        if not args.plan or not args.allowlist or not args.output_root:
            raise AuditError("plan, allowlist and output-root required")
        if any((args.primary_root, args.independent_root, args.qualification)):
            raise AuditError("compare-only arguments forbidden in normal mode")
        if args.plan != PLAN_RELATIVE or args.allowlist != ALLOWLIST_RELATIVE:
            raise AuditError("normal run requires the frozen control paths")
        preflight_output = _validate_scoped_path(
            repo, args.output_root, PRIMARY_ROOT_RELATIVE, must_exist=False
        )
        _require_absent_publication_root(preflight_output)
        files, counts, outcome, control_hashes = build_package(repo, args.plan, args.allowlist)
        output_root = _validate_scoped_path(
            repo, args.output_root, PRIMARY_ROOT_RELATIVE, must_exist=False
        )
        _require_absent_publication_root(output_root)
        write_package(
            output_root,
            files,
            counts,
            outcome,
            control_hashes["plan_sha256"],
            control_hashes["protocol_sha256"],
            control_hashes["allowlist_sha256"],
        )
        print(outcome)
        return 0
    except (
        AuditError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
        subprocess.CalledProcessError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"AUDIT_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
