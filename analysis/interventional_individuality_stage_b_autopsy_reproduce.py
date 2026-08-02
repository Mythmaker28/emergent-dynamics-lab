"""Independent engine-free Stage-B developmental autopsy reproducer.

No project module is imported.  Scientific reads are closed by the frozen
allowlist and accepted-parent Git blob identities before any NumPy array is
loaded.  ``--self-test`` uses only deterministic in-memory/temporary fixtures.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
from importlib import metadata as importlib_metadata
import io
import json
import math
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence
import warnings
import zipfile

import numpy as np


MISSION = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-RAW-ONLY-DEVELOPMENTAL-AUTOPSY"
ACCEPTED_PARENT = "c31bf27ea80a6a3dcc60d0ec5380f668358671ff"
PLAN_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-PLAN-v1"
PROTOCOL_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-RECONSTRUCTION-v1"
ALLOWLIST_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-SOURCE-ALLOWLIST-v1"
CLASSIFICATION_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-CLASSIFICATION-v1"
INTEGRITY_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-INTEGRITY-v1"
WORLD_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-WORLD-TRANSITIONS-v1"
OBS_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-TRACK-OBSERVATION-v1"
EVENT_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-EVENT-v1"
ATLAS_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-ATLAS-v1"
ANALYSIS_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-ANALYSIS-v1"
COMPLETE_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY-COMPLETE-v1"

PLAN_CONTROL_PATH = "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_ANALYSIS_PLAN.json"
ALLOWLIST_CONTROL_PATH = "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_SOURCE_ALLOWLIST.json"
PROTOCOL_CONTROL_PATH = "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_RECONSTRUCTION_PROTOCOL.json"

HORIZON = 160
SHAPE = (12, 12)
DT = 0.05
ATOL = 1e-12
RTOL = 1e-10

REGIMES = (
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
EVENT_TYPES = (
    "ASSOCIATION_DIAGNOSTICS",
    "APPEARANCE",
    "CONTINUATION",
    "DISSOLUTION",
    "MERGE",
    "SPLIT",
    "TEMPORARY_CONTACT",
    "TRACKING_UNRESOLVED",
)
PATHWAY_ORDER = (
    "ACTIVATION_FAILURE",
    "TURNOVER_FAILURE",
    "PERSISTENCE_FAILURE",
    "TRANSIENT_CANDIDATE_CROSSING",
    "STABLE_CANDIDATE_EPISODE",
)
PATHWAY_COUNT_KEYS = ("FORMATION_FAILURE", *PATHWAY_ORDER)
TERMINAL_COUNT_KEYS = (
    "EMPTY_OR_DISSOLVED", "FROZEN", "PERSISTENT_ACTIVE", "PERSISTENT_OTHER", "NONE",
)

LEDGER_ARRAYS = (
    "affinity",
    "matter_forward", "matter_reverse", "matter_natural", "matter_active", "matter_missing",
    "resource_permeability", "resource_natural", "resource_active", "resource_missing",
    "bond_cue", "bond_tension", "r_on", "r_off",
    "gross_formation", "gross_rupture", "gross_formation_work", "gross_rupture_release",
    "gross_weakening_release", "gross_dissolution_release", "maintenance_recycled_work",
    "formation_fuel", "rupture_heat", "weakening_heat", "dissolution_heat",
    "matter_missing_from_delta", "matter_missing_to_delta",
    "resource_missing_from_delta", "resource_missing_to_delta",
    "matter_scale", "resource_scale",
)
LEDGER_SCALARS = (
    "initial_matter", "final_matter", "matter_residual",
    "initial_stored_energy", "final_stored_energy", "total_rupture_heat",
    "total_maintenance_recycled_work", "energy_residual", "controller_onset_energy_jump",
)
EXPECTED_KEYS = (
    "state_step", "state_m", "state_n", "state_b",
    "vector_reference_max_error", "deterministic_replay_equal",
    *(f"ledger__{name}" for name in LEDGER_ARRAYS),
    *(f"ledger__{name}" for name in LEDGER_SCALARS),
)


class AuditError(RuntimeError):
    pass


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def reject_constant(value: str) -> None:
    raise AuditError(f"non-finite JSON constant {value!r}")


def normalize_float(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise AuditError("non-finite output float")
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: normalize_float(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_float(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_float(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    value = normalize_float(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def canonical_line(value: Any) -> bytes:
    return canonical_bytes(value)


def parse_json(raw: bytes, label: str, canonical: bool = False) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid JSON {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"{label} root is not an object")
    if canonical and raw != canonical_bytes(value):
        raise AuditError(f"{label} is not canonical finite JSON")
    return value


def exact_median(values: Sequence[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise AuditError("median received non-finite value")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def continuous_summary(values: Iterable[int | float | None]) -> dict[str, Any]:
    kept = [float(value) for value in values if value is not None]
    return {
        "n": len(kept),
        "median": exact_median(kept),
        "min": min(kept) if kept else None,
        "max": max(kept) if kept else None,
    }


def binary_summary(numerator: int, denominator: int) -> dict[str, Any]:
    return {"numerator": numerator, "denominator": denominator,
            "fraction": numerator / denominator if denominator else None}


def _is_reparse(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


class ReadGuard:
    def __init__(self, root: Path, allowed: Iterable[str]):
        self.root = root.resolve(strict=True)
        self.allowed: dict[str, str] = {}
        for raw in allowed:
            normalized = raw.replace("\\", "/")
            if Path(normalized).is_absolute() or ".." in Path(normalized).parts:
                raise AuditError(f"unsafe allowlist path {raw!r}")
            key = normalized.casefold()
            if key in self.allowed:
                raise AuditError(f"casefold duplicate allowlist path {raw!r}")
            self.allowed[key] = normalized

    def resolve(self, relative: str) -> Path:
        normalized = relative.replace("\\", "/")
        if Path(normalized).is_absolute() or ".." in Path(normalized).parts:
            raise AuditError(f"unsafe requested path {relative!r}")
        key = normalized.casefold()
        if key not in self.allowed:
            raise AuditError(f"path is not exact allowlist member: {relative!r}")
        canonical = self.allowed[key]
        probe = self.root
        for part in Path(canonical).parts:
            probe = probe / part
            if probe.is_symlink() or _is_reparse(probe):
                raise AuditError(f"symlink/reparse input forbidden: {canonical}")
        resolved = probe.resolve(strict=True)
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise AuditError(f"path escapes root: {normalized}") from exc
        return resolved

    def read(self, relative: str) -> bytes:
        return self.resolve(relative).read_bytes()


def exact_control_request(requested: str | Path, expected: str) -> None:
    literal = str(requested)
    if (literal != expected or Path(literal).is_absolute()
            or ".." in Path(literal).parts):
        raise AuditError(f"control path is not exact frozen literal: {literal}")


def expected_layout() -> dict[str, tuple[np.dtype[Any], tuple[int, ...]]]:
    layout: dict[str, tuple[np.dtype[Any], tuple[int, ...]]] = {
        "state_step": (np.dtype("int64"), (161,)),
        "state_m": (np.dtype("float64"), (161, 12, 12)),
        "state_n": (np.dtype("float64"), (161, 12, 12)),
        "state_b": (np.dtype("float64"), (161, 2, 12, 12)),
        "vector_reference_max_error": (np.dtype("float64"), (160,)),
        "deterministic_replay_equal": (np.dtype("uint8"), (160,)),
    }
    for name in LEDGER_ARRAYS:
        shape = (160, 12, 12) if name == "affinity" else (160, 2, 12, 12)
        layout[f"ledger__{name}"] = (np.dtype("float64"), shape)
    for name in LEDGER_SCALARS:
        layout[f"ledger__{name}"] = (np.dtype("float64"), (160,))
    return layout


def load_npz_bytes(raw: bytes, label: str) -> dict[str, np.ndarray]:
    layout = expected_layout()
    expected_members = {f"{name}.npy" for name in layout}
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise AuditError(f"{label}: duplicate ZIP member")
            for member in members:
                name = member.filename
                path = Path(name)
                if (member.is_dir() or "/" in name or "\\" in name or path.is_absolute()
                        or name in {".", ".."} or ".." in path.parts or name not in expected_members):
                    raise AuditError(f"{label}: unsafe/unexpected ZIP member {name!r}")
            if set(names) != expected_members:
                raise AuditError(f"{label}: ZIP member set mismatch")
        with np.load(io.BytesIO(raw), allow_pickle=False) as loaded:
            if set(loaded.files) != set(layout):
                raise AuditError(f"{label}: NumPy logical-key set mismatch")
            arrays = {name: np.array(loaded[name], copy=True) for name in loaded.files}
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise AuditError(f"{label}: malformed NPZ: {exc}") from exc
    for name, array in arrays.items():
        dtype, shape = layout[name]
        if (array.dtype.hasobject or array.dtype.fields is not None or array.dtype.subdtype is not None
                or not array.dtype.isnative or array.dtype != dtype or array.shape != shape):
            raise AuditError(f"{label}: invalid dtype/shape for {name}")
    return arrays


def divergence(face: np.ndarray) -> np.ndarray:
    term0 = face[0] - np.roll(face[0], 1, axis=0)
    term1 = face[1] - np.roll(face[1], 1, axis=1)
    return term0 + term1


def qualify_raw(arrays: Mapping[str, np.ndarray]) -> dict[str, bool]:
    if set(arrays) != set(EXPECTED_KEYS):
        raise AuditError("raw exact key inventory mismatch")
    for name, array in arrays.items():
        if name != "deterministic_replay_equal" and name != "state_step":
            if not np.all(np.isfinite(array)):
                raise AuditError(f"non-finite raw array {name}")
    if not np.array_equal(arrays["state_step"], np.arange(161, dtype=np.int64)):
        raise AuditError("state_step clock mismatch")
    for name in ("state_m", "state_n", "state_b"):
        if np.any(arrays[name] < 0.0):
            raise AuditError(f"negative state {name}")
    upper = 1.0 + ATOL + RTOL
    if any(np.any(arrays[name] > upper) for name in ("state_m", "state_n", "state_b")):
        raise AuditError("state upper bound exceeded")
    maximum_scale = 1.0
    scale_names = ["state_m", "state_n", "state_b"]
    scale_names.extend(f"ledger__{name}" for name in LEDGER_ARRAYS)
    scale_names.extend(f"ledger__{name}" for name in LEDGER_SCALARS)
    for name in scale_names:
        maximum_scale = max(maximum_scale, float(np.max(np.abs(arrays[name]))))
    errors = arrays["vector_reference_max_error"]
    if (not np.all(np.isfinite(errors)) or np.any(errors < 0.0)
            or np.any(errors > ATOL + RTOL * maximum_scale)):
        raise AuditError("vector-reference raw gate failed")
    for name in ("deterministic_replay_equal", "ledger__matter_scale", "ledger__resource_scale"):
        if not np.array_equal(arrays[name], np.ones_like(arrays[name])):
            raise AuditError(f"exact-one gate failed for {name}")
    for name in (
        "ledger__matter_missing", "ledger__resource_missing",
        "ledger__matter_missing_from_delta", "ledger__matter_missing_to_delta",
        "ledger__resource_missing_from_delta", "ledger__resource_missing_to_delta",
        "ledger__controller_onset_energy_jump",
    ):
        if not np.array_equal(arrays[name], np.zeros_like(arrays[name])):
            raise AuditError(f"exact-zero gate failed for {name}")
    for name in (
        "ledger__matter_forward", "ledger__matter_reverse", "ledger__gross_formation",
        "ledger__gross_rupture", "ledger__gross_formation_work", "ledger__gross_rupture_release",
    ):
        if np.any(arrays[name] < 0.0):
            raise AuditError(f"nonnegative ledger gate failed for {name}")
    for frame in range(HORIZON):
        net = arrays["ledger__matter_forward"][frame] - arrays["ledger__matter_reverse"][frame]
        expected_post = arrays["state_m"][frame] - DT * divergence(net)
        allowed = ATOL + RTOL * np.abs(expected_post)
        if np.any(np.abs(arrays["state_m"][frame + 1] - expected_post) > allowed):
            raise AuditError(f"matter transport identity failed at {frame}")
        initial = math.fsum(float(value) for value in arrays["state_m"][frame].flat)
        final = math.fsum(float(value) for value in arrays["state_m"][frame + 1].flat)
        for scalar, expected in (("initial_matter", initial), ("final_matter", final)):
            actual = float(arrays[f"ledger__{scalar}"][frame])
            if abs(actual - expected) > ATOL + RTOL * abs(expected):
                raise AuditError(f"{scalar} identity failed at {frame}")
        if abs(float(arrays["ledger__matter_residual"][frame])) > ATOL + RTOL * abs(final):
            raise AuditError(f"matter residual failed at {frame}")
        initial_energy = float(arrays["ledger__initial_stored_energy"][frame])
        if abs(float(arrays["ledger__energy_residual"][frame])) > ATOL + RTOL * abs(initial_energy):
            raise AuditError(f"energy residual failed at {frame}")
    return {
        "exact_inventory": True, "finite": True, "clock": True, "state_bounds": True,
        "reference_error": True, "replay": True, "neutral_arrays": True,
        "matter_transport": True, "matter_scalars": True, "energy_residual": True,
    }


@dataclass
class Component:
    frame: int
    index: int
    cells: tuple[tuple[int, int], ...]
    mask: np.ndarray
    mass: float
    centroid: tuple[float, float]
    radius: float
    wraps_y: bool
    wraps_x: bool

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def percolated(self) -> bool:
        return self.wraps_y or self.wraps_x

    @property
    def key(self) -> list[int]:
        return [self.frame, self.index]


def neighbours(y: int, x: int) -> Iterable[tuple[int, int, int, int]]:
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        yield (y + dy) % SHAPE[0], (x + dx) % SHAPE[1], dy, dx


def detect(matter: np.ndarray, frame: int) -> list[Component]:
    if matter.dtype != np.dtype("float64") or matter.shape != SHAPE or not np.all(np.isfinite(matter)):
        raise AuditError("detector received invalid matter")
    occupied = matter >= 0.5
    unseen = set(int(value) for value in np.flatnonzero(occupied.ravel(order="C")))
    raw: list[tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], tuple[int, int]], bool, bool]] = []
    while unseen:
        root_linear = min(unseen)
        root = divmod(root_linear, SHAPE[1])
        stack = [root]
        lifts: dict[tuple[int, int], tuple[int, int]] = {root: root}
        accepted: set[tuple[int, int]] = set()
        cells: list[tuple[int, int]] = []
        wraps_y = False
        wraps_x = False
        while stack:
            cell = stack.pop()
            if cell in accepted:
                continue
            accepted.add(cell)
            cells.append(cell)
            lift = lifts[cell]
            for ny, nx, dy, dx in neighbours(*cell):
                if not occupied[ny, nx]:
                    continue
                target = (ny, nx)
                proposed = (lift[0] + dy, lift[1] + dx)
                if target in lifts:
                    wraps_y = wraps_y or lifts[target][0] != proposed[0]
                    wraps_x = wraps_x or lifts[target][1] != proposed[1]
                else:
                    lifts[target] = proposed
                    stack.append(target)
        unseen.difference_update(y * SHAPE[1] + x for y, x in accepted)
        ordered = tuple(sorted(cells))
        if len(ordered) >= 3:
            raw.append((ordered, lifts, wraps_y, wraps_x))
    raw.sort(key=lambda item: item[0][0][0] * SHAPE[1] + item[0][0][1])
    result: list[Component] = []
    for index, (cells, lifts, wraps_y, wraps_x) in enumerate(raw):
        mask = np.zeros(SHAPE, dtype=np.bool_)
        ys, xs = zip(*cells)
        mask[np.asarray(ys), np.asarray(xs)] = True
        weights = np.asarray([matter[cell] for cell in cells], dtype=np.float64)
        mass = math.fsum(float(value) for value in weights)
        lifted = np.asarray([lifts[cell] for cell in cells], dtype=np.float64)
        if mass <= 0.0:
            raise AuditError("detected component has nonpositive mass")
        center_lift = np.sum(lifted * weights[:, None], axis=0) / mass
        squared = np.sum((lifted - center_lift) ** 2, axis=1)
        radius = math.sqrt(float(np.sum(weights * squared)) / mass)
        result.append(Component(
            frame=frame, index=index, cells=cells, mask=mask, mass=mass,
            centroid=(float(center_lift[0] % SHAPE[0]), float(center_lift[1] % SHAPE[1])),
            radius=radius, wraps_y=wraps_y, wraps_x=wraps_x,
        ))
    return result


def dilate(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    result = mask.copy()
    frontier = mask.copy()
    for _ in range(radius):
        frontier = (np.roll(frontier, 1, 0) | np.roll(frontier, -1, 0)
                    | np.roll(frontier, 1, 1) | np.roll(frontier, -1, 1))
        result |= frontier
    return result


def iou(first: np.ndarray, second: np.ndarray) -> float:
    intersection = int(np.count_nonzero(first & second))
    union = int(np.count_nonzero(first | second))
    return intersection / union if union else 0.0


def periodic_delta(first: float, second: float, period: int) -> float:
    raw = second - first
    return min((raw, raw - period, raw + period), key=lambda value: (abs(value), value))


@dataclass
class Edge:
    source: int
    target: int
    raw_iou: float
    dilated_iou: float
    distance: float
    area_ratio: float
    score: float
    qualified: bool
    reason: str
    selected: bool = False
    ambiguity: bool = False

    def row(self, source_frame: int, target_frame: int) -> dict[str, Any]:
        return {
            "source_key": [source_frame, self.source],
            "target_key": [target_frame, self.target],
            "raw_iou": self.raw_iou,
            "dilated_iou": self.dilated_iou,
            "centroid_distance": self.distance,
            "area_ratio": self.area_ratio,
            "score": self.score,
            "qualified": self.qualified,
            "qualification_reason": self.reason,
            "selected": self.selected,
            "ambiguity_bearing": self.ambiguity,
        }


def associate(sources: Sequence[Component], targets: Sequence[Component]) -> list[Edge]:
    source_d = {item.index: dilate(item.mask) for item in sources}
    target_d = {item.index: dilate(item.mask) for item in targets}
    edges: list[Edge] = []
    for source in sources:
        for target in targets:
            raw_overlap = iou(source.mask, target.mask)
            expanded = iou(source_d[source.index], target_d[target.index])
            dy = periodic_delta(source.centroid[0], target.centroid[0], SHAPE[0])
            dx = periodic_delta(source.centroid[1], target.centroid[1], SHAPE[1])
            distance = math.hypot(dy, dx)
            ratio = max(source.area, target.area) / min(source.area, target.area)
            score = (4.0 * raw_overlap + 2.0 * expanded + math.exp(-distance / 2.5)
                     + min(source.area, target.area) / max(source.area, target.area))
            if ratio > 3.0:
                qualified, reason = False, "AREA_RATIO"
            elif distance > 2.5:
                qualified, reason = False, "CENTROID_DISTANCE"
            elif raw_overlap == 0.0 and expanded == 0.0:
                qualified, reason = False, "NO_SUPPORT_OVERLAP"
            else:
                qualified, reason = True, "QUALIFIED"
            edges.append(Edge(source.index, target.index, raw_overlap, expanded, distance,
                              ratio, score, qualified, reason))
    for edge in edges:
        edge.selected = edge.qualified and edge.raw_iou > 0.0
    occupied_s = {edge.source for edge in edges if edge.selected}
    occupied_t = {edge.target for edge in edges if edge.selected}
    remaining = [edge for edge in edges if edge.qualified and not edge.selected
                 and edge.source not in occupied_s and edge.target not in occupied_t]
    by_s: dict[int, list[Edge]] = defaultdict(list)
    by_t: dict[int, list[Edge]] = defaultdict(list)
    for edge in remaining:
        by_s[edge.source].append(edge)
        by_t[edge.target].append(edge)
    for values in by_s.values():
        values.sort(key=lambda edge: (-edge.score, edge.target))
    for values in by_t.values():
        values.sort(key=lambda edge: (-edge.score, edge.source))

    def unique(values: Sequence[Edge]) -> Edge | None:
        if not values:
            return None
        return values[0] if len(values) == 1 or values[0].score - values[1].score > 1e-12 else None

    s_top = {key: unique(values) for key, values in by_s.items()}
    t_top = {key: unique(values) for key, values in by_t.items()}
    for edge in remaining:
        edge.selected = s_top.get(edge.source) is edge and t_top.get(edge.target) is edge
    selected_s = {edge.source for edge in edges if edge.selected}
    selected_t = {edge.target for edge in edges if edge.selected}
    for edge in remaining:
        edge.ambiguity = (not edge.selected and edge.source not in selected_s
                          and edge.target not in selected_t)
    return edges


def transition_groups(edges: Sequence[Edge]) -> list[tuple[list[int], list[int], list[Edge]]]:
    graph = [edge for edge in edges if edge.selected or edge.ambiguity]
    by_s: dict[int, list[Edge]] = defaultdict(list)
    by_t: dict[int, list[Edge]] = defaultdict(list)
    for edge in graph:
        by_s[edge.source].append(edge)
        by_t[edge.target].append(edge)
    visited_s: set[int] = set()
    visited_t: set[int] = set()
    groups = []
    for initial in sorted(by_s):
        if initial in visited_s:
            continue
        queue: deque[tuple[str, int]] = deque([("s", initial)])
        sources: set[int] = set()
        targets: set[int] = set()
        while queue:
            side, node = queue.popleft()
            if side == "s":
                if node in visited_s:
                    continue
                visited_s.add(node); sources.add(node)
                queue.extend(("t", edge.target) for edge in by_s[node])
            else:
                if node in visited_t:
                    continue
                visited_t.add(node); targets.add(node)
                queue.extend(("s", edge.source) for edge in by_t[node])
        group_edges = [edge for edge in graph if edge.source in sources and edge.target in targets]
        groups.append((sorted(sources), sorted(targets), group_edges))
    groups.sort(key=lambda group: (group[0][0], tuple(group[1])))
    return groups


@dataclass(frozen=True)
class Point:
    frame: int
    component_index: int


@dataclass
class Track:
    track_id: int
    points: list[Point]
    unresolved: bool = False
    parent_ids: tuple[int, ...] = ()
    fingerprint: str = ""


@dataclass
class Tracking:
    tracks: list[Track]
    events: list[dict[str, Any]]
    world_unresolved: bool


def fingerprint(component: Component) -> str:
    cell_ids = ",".join(str(y * SHAPE[1] + x) for y, x in component.cells)
    return f"{component.frame}:{cell_ids}"


def event_row(world_id: str, frame: int, event_type: str, source_ids: Sequence[int],
              target_ids: Sequence[int], source_keys: Sequence[Sequence[int]],
              target_keys: Sequence[Sequence[int]], resolved: bool,
              edges: Sequence[dict[str, Any]] = ()) -> dict[str, Any]:
    return {
        "schema": EVENT_SCHEMA, "world_id": world_id, "frame": frame,
        "event_type": event_type, "source_track_ids": list(source_ids),
        "target_track_ids": list(target_ids), "source_component_keys": [list(key) for key in source_keys],
        "target_component_keys": [list(key) for key in target_keys], "resolved": resolved,
        "association_edges": list(edges),
    }


def minimum_manhattan(first: Component, second: Component) -> int:
    best = sum(SHAPE)
    for y1, x1 in first.cells:
        for y2, x2 in second.cells:
            dy = abs(y1 - y2); dx = abs(x1 - x2)
            best = min(best, min(dy, SHAPE[0] - dy) + min(dx, SHAPE[1] - dx))
    return best


def track_sort_key(track: Track, component_lookup: Mapping[tuple[int, int], Component]) -> tuple[Any, ...]:
    onset = track.points[0]
    component = component_lookup[(onset.frame, onset.component_index)]
    return onset.frame, tuple(y * SHAPE[1] + x for y, x in component.cells)


def track_components(world_id: str, frames: Sequence[Sequence[Component]]) -> Tracking:
    if len(frames) != HORIZON:
        raise AuditError("tracking requires exactly 160 detector frames")
    transitions = [associate(frames[t - 1], frames[t]) for t in range(1, HORIZON)]
    collapse_nodes: set[tuple[int, int]] = set()
    for frame in range(1, HORIZON - 1):
        incoming = Counter(edge.target for edge in transitions[frame - 1] if edge.selected)
        outgoing = Counter(edge.source for edge in transitions[frame] if edge.selected)
        for component in frames[frame]:
            if incoming[component.index] >= 2 and outgoing[component.index] >= 2:
                collapse_nodes.add((frame, component.index))

    tracks: list[Track] = []
    events: list[dict[str, Any]] = []
    mapping: dict[tuple[int, int], int] = {}
    next_id = 0

    def create(component: Component, unresolved: bool = False,
               parents: Sequence[int] = ()) -> int:
        nonlocal next_id
        track = Track(next_id, [Point(component.frame, component.index)], unresolved,
                      tuple(sorted(parents)), fingerprint(component))
        tracks.append(track)
        mapping[(component.frame, component.index)] = next_id
        next_id += 1
        return track.track_id

    for component in frames[0]:
        target_id = create(component)
        events.append(event_row(world_id, 0, "APPEARANCE", (), (target_id,), (),
                                ((0, component.index),), True))

    world_unresolved = False
    for frame in range(1, HORIZON):
        sources = frames[frame - 1]
        targets = frames[frame]
        edges = transitions[frame - 1]
        groups = transition_groups(edges)
        graph_sources = {index for group in groups for index in group[0]}
        graph_targets = {index for group in groups for index in group[1]}

        for component in sources:
            if component.index not in graph_sources:
                source_id = mapping[(frame - 1, component.index)]
                events.append(event_row(world_id, frame, "DISSOLUTION", (source_id,), (),
                                        ((frame - 1, component.index),), (), True))

        for source_indices, target_indices, group_edges in groups:
            source_ids = [mapping[(frame - 1, index)] for index in source_indices]
            source_keys = [(frame - 1, index) for index in source_indices]
            target_keys = [(frame, index) for index in target_indices]
            has_ambiguity = any(edge.ambiguity for edge in group_edges)
            has_collapse = any(key in collapse_nodes for key in source_keys + target_keys)
            selected = [edge for edge in group_edges if edge.selected]
            selected_sources = {edge.source for edge in selected}
            selected_targets = {edge.target for edge in selected}
            complete = selected_sources == set(source_indices) and selected_targets == set(target_indices)
            unresolved = (has_ambiguity or has_collapse or not complete
                          or (len(source_indices) > 1 and len(target_indices) > 1))
            if unresolved:
                world_unresolved = True
                for source_id in source_ids:
                    tracks[source_id].unresolved = True
                target_ids = [create(targets[index], True, source_ids) for index in target_indices]
                events.append(event_row(world_id, frame, "TRACKING_UNRESOLVED", source_ids,
                                        target_ids, source_keys, target_keys, False))
            elif len(source_indices) == 1 and len(target_indices) == 1:
                source_id = source_ids[0]
                target = target_indices[0]
                mapping[(frame, target)] = source_id
                tracks[source_id].points.append(Point(frame, target))
                target_ids = [source_id]
                events.append(event_row(world_id, frame, "CONTINUATION", source_ids,
                                        target_ids, source_keys, target_keys, True))
            elif len(source_indices) == 1:
                target_ids = [create(targets[index], False, source_ids) for index in target_indices]
                events.append(event_row(world_id, frame, "SPLIT", source_ids, target_ids,
                                        source_keys, target_keys, True))
            elif len(target_indices) == 1:
                target_ids = [create(targets[target_indices[0]], False, source_ids)]
                events.append(event_row(world_id, frame, "MERGE", source_ids, target_ids,
                                        source_keys, target_keys, True))
            else:
                raise AuditError("empty or impossible transition group")

        for component in targets:
            if component.index not in graph_targets:
                target_id = create(component)
                events.append(event_row(world_id, frame, "APPEARANCE", (), (target_id,), (),
                                        ((frame, component.index),), True))

        target_ids_by_index = {
            component.index: mapping[(frame, component.index)] for component in targets
        }
        for left_position, left in enumerate(targets):
            for right in targets[left_position + 1:]:
                left_track = tracks[target_ids_by_index[left.index]]
                right_track = tracks[target_ids_by_index[right.index]]
                if (not left_track.unresolved and not right_track.unresolved
                        and minimum_manhattan(left, right) == 2):
                    events.append(event_row(
                        world_id, frame, "TEMPORARY_CONTACT", (),
                        (left_track.track_id, right_track.track_id), (),
                        ((frame, left.index), (frame, right.index)), True,
                    ))

        diagnostic_edges = [edge.row(frame - 1, frame) for edge in sorted(
            edges, key=lambda edge: (edge.source, edge.target))]
        diagnostic_resolved = not any(
            event["frame"] == frame and not event["resolved"] for event in events
        ) and not any(
            key in collapse_nodes for key in
            ([(frame - 1, component.index) for component in sources]
             + [(frame, component.index) for component in targets])
        )
        events.append(event_row(
            world_id, frame, "ASSOCIATION_DIAGNOSTICS",
            [mapping[(frame - 1, component.index)] for component in sources],
            [mapping[(frame, component.index)] for component in targets],
            [(frame - 1, component.index) for component in sources],
            [(frame, component.index) for component in targets], diagnostic_resolved,
            diagnostic_edges,
        ))

    component_lookup = {
        (component.frame, component.index): component
        for components in frames for component in components
    }
    canonical_tracks = sorted(tracks, key=lambda track: track_sort_key(track, component_lookup))
    canonical_rank = {track.track_id: rank for rank, track in enumerate(canonical_tracks)}
    event_rank = {name: index for index, name in enumerate(EVENT_TYPES)}
    events.sort(key=lambda row: (
        row["frame"], event_rank[row["event_type"]],
        tuple(tuple(key) for key in row["source_component_keys"]),
        tuple(tuple(key) for key in row["target_component_keys"]),
    ))
    # ID assignment remains mechanically frozen; canonical_rank is asserted to
    # be a permutation and used by the output row order, never association.
    if sorted(canonical_rank.values()) != list(range(len(tracks))):
        raise AuditError("invalid canonical track ordering")
    return Tracking(tracks, events, world_unresolved)


def _face_values(array: np.ndarray, support: np.ndarray, internal: bool) -> list[float]:
    values: list[float] = []
    for axis in (0, 1):
        target = np.roll(support, -1, axis=axis)
        mask = support & target if internal else support ^ target
        values.extend(float(value) for value in array[axis][mask].ravel(order="C"))
    return values


def support_cv(array: np.ndarray, cells: Sequence[tuple[int, int]]) -> float:
    values = [float(array[cell]) for cell in cells]
    mean = math.fsum(values) / len(values)
    if mean < 0.0:
        raise AuditError("negative support mean")
    if mean == 0.0:
        if any(value != 0.0 for value in values):
            raise AuditError("inconsistent zero support mean")
        return 0.0
    variance = math.fsum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def seam_metrics(component: Component) -> tuple[int, bool]:
    distance = min(min(y, SHAPE[0] - 1 - y, x, SHAPE[1] - 1 - x)
                   for y, x in component.cells)
    cells = set(component.cells)
    crossed = any(
        ((0, x) in cells and (SHAPE[0] - 1, x) in cells) for x in range(SHAPE[1])
    ) or any(
        ((y, 0) in cells and (y, SHAPE[1] - 1) in cells) for y in range(SHAPE[0])
    )
    return distance, crossed


def advance_cohort(q: np.ndarray, pre_m: np.ndarray, post_m: np.ndarray,
                   forward: np.ndarray, reverse: np.ndarray) -> np.ndarray:
    if any(array.dtype != np.dtype("float64") or array.shape[-2:] != SHAPE
           for array in (q, pre_m, post_m, forward, reverse)):
        raise AuditError("cohort arrays have invalid dtype or shape")
    scale = max(1.0, float(np.max(np.abs(pre_m))), float(np.max(np.abs(post_m))))
    tolerance = ATOL + RTOL * scale
    if (not all(np.all(np.isfinite(array)) for array in (q, pre_m, post_m, forward, reverse))
            or np.min(pre_m) < 0.0 or np.min(post_m) < 0.0
            or np.min(forward) < 0.0 or np.min(reverse) < 0.0
            or np.min(q) < -tolerance or np.max(q - pre_m) > tolerance):
        raise AuditError("cohort precondition failed")
    matter_net = forward - reverse
    expected = pre_m - DT * sum(
        matter_net[axis] - np.roll(matter_net[axis], 1, axis=axis) for axis in (0, 1)
    )
    if float(np.max(np.abs(post_m - expected))) > tolerance:
        raise AuditError("matter identity failed during cohort advance")
    fraction = np.divide(q, pre_m, out=np.zeros_like(q), where=pre_m > 0.0)
    directed = np.empty_like(forward)
    for axis in (0, 1):
        directed[axis] = (forward[axis] * fraction
                          - reverse[axis] * np.roll(fraction, -1, axis=axis))
    q_next = q - DT * sum(
        directed[axis] - np.roll(directed[axis], 1, axis=axis) for axis in (0, 1)
    )
    if abs(math.fsum(q_next.ravel(order="C")) - math.fsum(q.ravel(order="C"))) > tolerance * q.size:
        raise AuditError("cohort conservation failed")
    if np.min(q_next) < -tolerance or np.max(q_next - post_m) > tolerance:
        raise AuditError("cohort postcondition failed")
    return q_next


def track_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["frame"])
    if not ordered:
        raise AuditError("empty track summary")
    count = len(ordered)
    first_turn = next((row["frame"] for row in ordered if row["turnover_fraction"] >= 0.6), None)
    return {
        "observed_frames": count,
        "span_frames": ordered[-1]["frame"] - ordered[0]["frame"] + 1,
        "maximum_area_fraction": max(row["area_fraction"] for row in ordered),
        "bounded_fraction": math.fsum(
            1.0 for row in ordered if not row["percolated"] and row["area_fraction"] <= 0.25
        ) / count,
        "percolated_fraction": math.fsum(1.0 for row in ordered if row["percolated"]) / count,
        "mean_activity_per_mass": math.fsum(row["activity_per_mass"] for row in ordered) / count,
        "mean_energy_throughput_per_mass": math.fsum(
            row["energy_throughput_per_mass"] for row in ordered) / count,
        "maximum_turnover_fraction": max(row["turnover_fraction"] for row in ordered),
        "first_turnover_frame": first_turn,
        "post_turnover_frames": (sum(row["frame"] > first_turn for row in ordered)
                                 if first_turn is not None else 0),
        "persistent": (bool(ordered[0]["resolved"]) and count >= 80
                       and ordered[-1]["frame"] - ordered[0]["frame"] + 1 >= 80),
    }


def apply_prefix_flags(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows.sort(key=lambda row: row["frame"])
    final: dict[str, Any] | None = None
    for index, row in enumerate(rows):
        summary = track_summary(rows[:index + 1])
        active = (summary["mean_activity_per_mass"] >= 1e-4
                  and summary["mean_energy_throughput_per_mass"] >= 1e-5)
        candidate = (
            summary["persistent"] and summary["maximum_area_fraction"] <= 0.25
            and summary["bounded_fraction"] >= 0.95
            and summary["percolated_fraction"] == 0.0 and active
            and summary["maximum_turnover_fraction"] >= 0.6
            and summary["post_turnover_frames"] >= 32
        )
        row["instantaneous_bounded_active"] = (
            not row["percolated"] and row["area_fraction"] <= 0.25
            and row["activity_per_mass"] >= 1e-4
            and row["energy_throughput_per_mass"] >= 1e-5
        )
        row["prefix_persistent"] = summary["persistent"]
        row["prefix_active"] = active
        row["prefix_turnover"] = summary["maximum_turnover_fraction"] >= 0.6
        row["prefix_post_turnover_frames"] = summary["post_turnover_frames"]
        row["prefix_candidate"] = candidate
        final = summary | {"active": active, "candidate": candidate}
    assert final is not None
    return final


def observe_tracks(world_id: str, data: Mapping[str, np.ndarray], frames: Sequence[Sequence[Component]],
                   tracking: Tracking) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    components = {(component.frame, component.index): component
                  for frame in frames for component in frame}
    all_rows: list[dict[str, Any]] = []
    summaries: dict[int, dict[str, Any]] = {}
    for track in tracking.tracks:
        onset = track.points[0]
        onset_component = components[(onset.frame, onset.component_index)]
        q = np.zeros(SHAPE, dtype=np.float64)
        q[onset_component.mask] = data["state_m"][onset.frame][onset_component.mask]
        initial_mass = math.fsum(q.ravel(order="C"))
        if initial_mass <= 0.0:
            raise AuditError("nonpositive initial cohort mass")
        rows: list[dict[str, Any]] = []
        for point_position, point in enumerate(track.points):
            component = components[(point.frame, point.component_index)]
            support = component.mask
            frame = point.frame
            forward = data["ledger__matter_forward"][frame]
            reverse = data["ledger__matter_reverse"][frame]
            formation = data["ledger__gross_formation_work"][frame]
            rupture = data["ledger__gross_rupture_release"][frame]
            activity_values = _face_values(forward + reverse, support, True)
            energy_values = _face_values(formation + rupture, support, True)
            mass = component.mass
            matter_in_rates: list[float] = []
            matter_out_rates: list[float] = []
            resource_rates: list[float] = []
            resource = data["ledger__resource_natural"][frame]
            for axis in (0, 1):
                target_support = np.roll(support, -1, axis=axis)
                for y in range(SHAPE[0]):
                    for x in range(SHAPE[1]):
                        source_inside = bool(support[y, x])
                        target_inside = bool(target_support[y, x])
                        if source_inside == target_inside:
                            continue
                        fwd = float(forward[axis, y, x])
                        rev = float(reverse[axis, y, x])
                        if source_inside:
                            matter_out_rates.append(fwd); matter_in_rates.append(rev)
                        else:
                            matter_out_rates.append(rev); matter_in_rates.append(fwd)
                        resource_rates.append(abs(float(resource[axis, y, x])))
            matter_out = DT * math.fsum(matter_out_rates)
            matter_in = DT * math.fsum(matter_in_rates)
            internal_bonds = _face_values(data["state_b"][frame], support, True)
            retained = math.fsum(float(value) for value in q[support].ravel(order="C"))
            raw_turnover = 1.0 - retained / initial_mass
            range_tolerance = ATOL + RTOL * initial_mass
            if raw_turnover < -range_tolerance or raw_turnover > 1.0 + range_tolerance:
                raise AuditError("turnover outside tolerated range")
            seam_distance, seam_crossed = seam_metrics(component)
            row = {
                "schema": OBS_SCHEMA, "world_id": world_id, "track_id": track.track_id,
                "track_fingerprint": track.fingerprint, "frame": frame,
                "component_index": point.component_index, "resolved": not track.unresolved,
                "mass": mass, "area_fraction": component.area / (SHAPE[0] * SHAPE[1]),
                "percolated": component.percolated,
                "activity_per_mass": math.fsum(activity_values) / mass,
                "energy_throughput_per_mass": math.fsum(energy_values) / (DT * mass),
                "turnover_fraction": min(1.0, max(0.0, raw_turnover)),
                "matter_in": matter_in, "matter_out": matter_out,
                "matter_exchange_per_mass": (matter_in + matter_out) / mass,
                "net_matter_loss_per_mass": (matter_out - matter_in) / mass,
                "resource_natural_exchange_per_mass": DT * math.fsum(resource_rates) / mass,
                "mean_internal_bond": (math.fsum(internal_bonds) / len(internal_bonds)
                                       if internal_bonds else 0.0),
                "internal_bond_saturation_fraction": (
                    sum(value >= 0.9 for value in internal_bonds) / len(internal_bonds)
                    if internal_bonds else 0.0),
                "matter_cv": support_cv(data["state_m"][frame], component.cells),
                "resource_cv": support_cv(data["state_n"][frame], component.cells),
                "coordinate_seam_distance": seam_distance,
                "coordinate_seam_crossed": seam_crossed,
                "wraps_y": component.wraps_y, "wraps_x": component.wraps_x,
                "radius_gyration_fraction": component.radius / min(SHAPE),
            }
            rows.append(row)
            if point_position + 1 < len(track.points):
                next_point = track.points[point_position + 1]
                if next_point.frame != frame + 1:
                    raise AuditError("nonconsecutive points within track")
                q = advance_cohort(q, data["state_m"][frame], data["state_m"][frame + 1],
                                   forward, reverse)
        summaries[track.track_id] = apply_prefix_flags(rows)
        all_rows.extend(rows)
    all_rows.sort(key=lambda row: (
        track_sort_key(tracking.tracks[row["track_id"]], components), row["frame"]
    ))
    if len(all_rows) != sum(len(track.points) for track in tracking.tracks):
        raise AuditError("observation assembly cardinality mismatch")
    return all_rows, summaries


def classify_world(frames: Sequence[Sequence[Component]], tracking: Tracking,
                   summaries: Mapping[int, Mapping[str, Any]]) -> tuple[str, list[int]]:
    if tracking.world_unresolved or any(track.unresolved for track in tracking.tracks):
        regime = "TRACKING_UNRESOLVED"
    elif any(summary["percolated_fraction"] > 0.0 and summary["active"]
             for summary in summaries.values()):
        regime = "ACTIVE_UNBOUNDED"
    elif any(component.percolated for frame in frames for component in frame):
        regime = "PERCOLATED"
    elif not any(frames):
        regime = "EMPTY_OR_GAS"
    elif not frames[-1]:
        regime = "DISSOLVED"
    elif any(summary["candidate"] for summary in summaries.values()):
        regime = "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    else:
        persistent = [summary for summary in summaries.values() if summary["persistent"]]
        if any(summary["active"] for summary in persistent) and not any(
                summary["maximum_turnover_fraction"] >= 0.6 for summary in persistent):
            regime = "PERSISTENT_NO_TURNOVER"
        elif persistent:
            regime = "STATIC_CRYSTAL_OR_SHELL"
        elif any(summary["maximum_turnover_fraction"] >= 0.6 for summary in summaries.values()):
            regime = "TURNOVER_WITHOUT_PERSISTENCE"
        else:
            regime = "DISSOLVED"
    candidate_ids = (sorted(track_id for track_id, summary in summaries.items()
                            if summary["candidate"])
                     if regime == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" else [])
    return regime, candidate_ids


def consecutive_runs(rows: Sequence[Mapping[str, Any]], key: str) -> list[tuple[int, int, int]]:
    frames = [int(row["frame"]) for row in rows if row[key]]
    runs: list[tuple[int, int, int]] = []
    if not frames:
        return runs
    onset = previous = frames[0]
    for frame in frames[1:]:
        if frame != previous + 1:
            runs.append((onset, previous, previous - onset + 1))
            onset = frame
        previous = frame
    runs.append((onset, previous, previous - onset + 1))
    return runs


def track_milestones(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["frame"])
    t_active = next((row["frame"] for row in ordered
                     if row["instantaneous_bounded_active"]), None)
    t_persistence = next((row["frame"] for row in ordered if row["prefix_persistent"]), None)
    t_turn = (next((row["frame"] for row in ordered
                    if row["frame"] >= t_active and row["turnover_fraction"] >= 0.6), None)
              if t_active is not None else None)
    t_candidate = (next((row["frame"] for row in ordered
                         if row["frame"] >= t_turn and row["prefix_candidate"]), None)
                   if t_turn is not None else None)
    runs = consecutive_runs(ordered, "prefix_candidate")
    longest = max((run[2] for run in runs), default=0)
    terminal = any(run[2] == longest and run[1] == ordered[-1]["frame"] for run in runs)
    stable = t_candidate is not None and longest >= 32 and terminal
    if t_active is None:
        pathway = "ACTIVATION_FAILURE"
    elif t_turn is None:
        pathway = "TURNOVER_FAILURE"
    elif t_candidate is None:
        pathway = "PERSISTENCE_FAILURE"
    elif stable:
        pathway = "STABLE_CANDIDATE_EPISODE"
    else:
        pathway = "TRANSIENT_CANDIDATE_CROSSING"
    return {
        "formation": ordered[0]["frame"], "bounded_active": t_active,
        "persistence": t_persistence, "turnover": t_turn,
        "prefix_candidate": t_candidate, "candidate_runs": runs,
        "stable_candidate": stable, "pathway": pathway,
    }


def _milestone_min(track_rows: Mapping[int, Sequence[Mapping[str, Any]]],
                   milestones: Mapping[int, Mapping[str, Any]], key: str,
                   tracks: Mapping[int, Track]) -> tuple[int | None, str | None]:
    available = [(values[key], tracks[track_id].fingerprint)
                 for track_id, values in milestones.items() if values[key] is not None]
    if not available:
        return None, None
    value = min(item[0] for item in available)
    return int(value), min(item[1] for item in available if item[0] == value)


def _terminal_state(track: Track, rows: Sequence[Mapping[str, Any]],
                    events: Sequence[Mapping[str, Any]]) -> tuple[str, int | None, bool]:
    ordered = sorted(rows, key=lambda row: row["frame"])
    dissolutions = [event["frame"] for event in events
                    if event["event_type"] == "DISSOLUTION"
                    and event["source_track_ids"] == [track.track_id]]
    if dissolutions:
        return "EMPTY_OR_DISSOLVED", None, False
    if ordered[-1]["frame"] != HORIZON - 1:
        raise AuditError("representative track ended before horizon without dissolution")
    suffix: list[Mapping[str, Any]] = []
    expected = HORIZON - 1
    for row in reversed(ordered):
        if row["frame"] != expected:
            break
        suffix.append(row)
        expected -= 1
    frozen_suffix = []
    for row in suffix:
        if row["activity_per_mass"] < 1e-4 and row["energy_throughput_per_mass"] < 1e-5:
            frozen_suffix.append(row)
        else:
            break
    if len(frozen_suffix) >= 32:
        return "FROZEN", int(frozen_suffix[-1]["frame"]), True
    last_32 = list(reversed(suffix[:32]))
    if (len(last_32) == 32
            and math.fsum(row["activity_per_mass"] for row in last_32) / 32 >= 1e-4
            and math.fsum(row["energy_throughput_per_mass"] for row in last_32) / 32 >= 1e-5):
        return "PERSISTENT_ACTIVE", None, True
    return "PERSISTENT_OTHER", None, True


def _formation_bin(frame: int | None) -> str:
    if frame is None:
        return "none"
    if frame <= 39:
        return "early"
    if frame <= 119:
        return "middle"
    return "late"


def develop_world(metadata: Mapping[str, Any], committed_regime: str,
                  committed_candidate_ids: Sequence[int], reconstructed_regime: str,
                  reconstructed_candidate_ids: Sequence[int], frames: Sequence[Sequence[Component]],
                  tracking: Tracking, observations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    world_id = str(metadata["world_id"])
    tracks = {track.track_id: track for track in tracking.tracks}
    by_track: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in observations:
        by_track[int(row["track_id"])].append(row)
    milestones = {track_id: track_milestones(rows) for track_id, rows in by_track.items()}

    if not tracks:
        pathway = "FORMATION_FAILURE"
        co_primary: list[Track] = []
        representative: Track | None = None
    else:
        highest = max(PATHWAY_ORDER.index(values["pathway"]) for values in milestones.values())
        pathway = PATHWAY_ORDER[highest]
        co_primary = [tracks[track_id] for track_id, values in milestones.items()
                      if PATHWAY_ORDER.index(values["pathway"]) == highest]
        co_primary.sort(key=lambda track: (track.points[0].frame, track.fingerprint))
        representative = co_primary[0]

    if committed_regime == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE":
        episode_options: list[tuple[int, int, tuple[Any, ...], Track]] = []
        for track_id in reconstructed_candidate_ids:
            track = tracks[track_id]
            for onset, _end, length in milestones[track_id]["candidate_runs"]:
                episode_options.append((-length, onset,
                                        (track.points[0].frame, track.fingerprint), track))
        if not episode_options:
            raise AuditError("committed candidate world lacks reconstructed candidate episode")
        representative = min(episode_options)[3]

    first_component = min((component.frame for frame in frames for component in frame), default=None)
    first_active, active_fp = _milestone_min(by_track, milestones, "bounded_active", tracks)
    first_persistence, persistence_fp = _milestone_min(by_track, milestones, "persistence", tracks)
    first_turn, turn_fp = _milestone_min(by_track, milestones, "turnover", tracks)
    first_candidate, candidate_fp = _milestone_min(by_track, milestones, "prefix_candidate", tracks)
    formation_fp = (min((track.fingerprint for track in tracks.values()
                         if track.points[0].frame == first_component), default=None)
                    if first_component is not None else None)

    representative_rows = by_track[representative.track_id] if representative is not None else []
    representative_runs = (milestones[representative.track_id]["candidate_runs"]
                           if representative is not None else [])
    status_frames = sum(bool(row["prefix_candidate"]) for row in representative_rows)
    episode_count = len(representative_runs)
    longest_episode = max((run[2] for run in representative_runs), default=0)
    selected_run = (min((run for run in representative_runs if run[2] == longest_episode),
                        key=lambda run: run[0]) if representative_runs else None)
    candidate_terminal = bool(
        selected_run is not None and selected_run[1] == representative_rows[-1]["frame"]
    )

    detected_frames = [frame for frame, components in enumerate(frames) if components]
    last_detected = max(detected_frames, default=None)
    terminal_empty_start = None if frames[-1] else (last_detected + 1 if last_detected is not None else 0)
    right_censored = any(
        not tracks[int(row["track_id"])].unresolved for row in observations
        if row["frame"] == HORIZON - 1
    )
    if representative is None:
        terminal_state, freeze_onset, terminal_alive = None, None, False
    else:
        terminal_state, freeze_onset, terminal_alive = _terminal_state(
            representative, representative_rows, tracking.events)

    def delta(value: int | None) -> int | None:
        return value - first_component if value is not None and first_component is not None else None

    representative_dissolution = None
    if representative is not None:
        representative_dissolution = next((event["frame"] for event in tracking.events
            if event["event_type"] == "DISSOLUTION"
            and event["source_track_ids"] == [representative.track_id]), None)
    split_count = sum(event["event_type"] == "SPLIT" for event in tracking.events)
    merge_count = sum(event["event_type"] == "MERGE" for event in tracking.events)
    appearance_count = sum(event["event_type"] == "APPEARANCE" for event in tracking.events)
    dissolution_count = sum(event["event_type"] == "DISSOLUTION" for event in tracking.events)
    seam_crossed = any(bool(row["coordinate_seam_crossed"]) for row in observations)
    ever_wound = any(bool(row["wraps_y"] or row["wraps_x"]) for row in observations)
    trajectory_class = None
    if representative is not None:
        trajectory_class = (
            f"{pathway}|{terminal_state or 'NONE'}|{_formation_bin(representative.points[0].frame)}"
            f"|SPLIT_MERGE={'1' if split_count or merge_count else '0'}"
            f"|CENSORED={'1' if right_censored else '0'}"
        )
    row = {
        "world_id": world_id, "law_id": str(metadata["law_id"]), "ic_id": str(metadata["ic_id"]),
        "replicate": int(metadata["replicate"]), "committed_regime": committed_regime,
        "reconstructed_regime": reconstructed_regime,
        "first_component_frame": first_component, "first_bounded_active_frame": first_active,
        "first_persistence_qualification_frame": first_persistence,
        "first_turnover_frame": first_turn, "first_prefix_candidate_frame": first_candidate,
        "candidate_status_frames": status_frames, "candidate_episode_count": episode_count,
        "longest_candidate_episode_frames": longest_episode,
        "candidate_episode_terminal": candidate_terminal, "last_detected_frame": last_detected,
        "terminal_empty_run_start": terminal_empty_start, "terminal_freeze_onset": freeze_onset,
        "terminal_track_alive": terminal_alive,
        "frames_formation_to_bounded_active": delta(first_active),
        "frames_formation_to_persistence": delta(first_persistence),
        "frames_formation_to_turnover": delta(first_turn),
        "frames_formation_to_candidate": delta(first_candidate),
        "frames_formation_to_terminal_loss": delta(representative_dissolution),
        "right_censored": right_censored, "coordinate_seam_crossed": seam_crossed,
        "ever_wound": ever_wound, "split_count": split_count, "merge_count": merge_count,
        "appearance_count": appearance_count, "dissolution_count": dissolution_count,
        "primary_developmental_pathway": pathway, "terminal_state": terminal_state,
        "formation_opportunity": True, "maintenance_opportunity": bool(tracks),
        "persistence_horizon_opportunity": any(track.points[0].frame <= 80 for track in tracks.values()),
        "post_turnover_horizon_opportunity": any(
            values["turnover"] is not None and values["turnover"] <= 127
            for values in milestones.values()),
        "milestone_track_fingerprints": {
            "formation": formation_fp, "bounded_active": active_fp,
            "persistence": persistence_fp, "turnover": turn_fp,
            "prefix_candidate": candidate_fp,
        },
        "representative_track_fingerprint": representative.fingerprint if representative else None,
        "co_primary_track_fingerprints": sorted(track.fingerprint for track in co_primary),
        "trajectory_class": trajectory_class,
    }
    if set(reconstructed_candidate_ids) != set(committed_candidate_ids):
        # The caller records the audit gate; world construction stays available
        # for an AUDIT_INVALID report without changing classifications.
        pass
    return row


CONTINUOUS_METRICS = (
    "first_component_frame", "first_bounded_active_frame",
    "first_persistence_qualification_frame", "first_turnover_frame",
    "first_prefix_candidate_frame", "candidate_status_frames",
    "longest_candidate_episode_frames",
)
MAINTENANCE_STAGES = (
    "formed", "bounded_active", "persistent", "turnover", "prefix_candidate",
    "stable_candidate", "terminal_persistence",
)


def world_stage(row: Mapping[str, Any], stage: str) -> bool:
    checks = {
        "formed": row["first_component_frame"] is not None,
        "bounded_active": row["first_bounded_active_frame"] is not None,
        "persistent": row["first_persistence_qualification_frame"] is not None,
        "turnover": row["first_turnover_frame"] is not None,
        "prefix_candidate": row["first_prefix_candidate_frame"] is not None,
        "stable_candidate": row["primary_developmental_pathway"] == "STABLE_CANDIDATE_EPISODE",
        "terminal_persistence": bool(row["terminal_track_alive"]),
    }
    return checks[stage]


def group_summary(group: Mapping[str, str], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    denominator = len(rows)
    regime_counter = Counter(row["reconstructed_regime"] for row in rows)
    pathway_counter = Counter(row["primary_developmental_pathway"] for row in rows)
    terminal_counter = Counter(row["terminal_state"] or "NONE" for row in rows)
    return {
        "group": dict(group), "denominator": denominator,
        "regime_counts": {key: regime_counter[key] for key in REGIMES},
        "pathway_counts": {key: pathway_counter[key] for key in PATHWAY_COUNT_KEYS},
        "terminal_counts": {key: terminal_counter[key] for key in TERMINAL_COUNT_KEYS},
        "formed": binary_summary(sum(world_stage(row, "formed") for row in rows), denominator),
        "bounded_active": binary_summary(sum(world_stage(row, "bounded_active") for row in rows), denominator),
        "persistent": binary_summary(sum(world_stage(row, "persistent") for row in rows), denominator),
        "turnover": binary_summary(sum(world_stage(row, "turnover") for row in rows), denominator),
        "prefix_candidate": binary_summary(sum(world_stage(row, "prefix_candidate") for row in rows), denominator),
        "stable_candidate": binary_summary(sum(world_stage(row, "stable_candidate") for row in rows), denominator),
        "right_censored": binary_summary(sum(bool(row["right_censored"]) for row in rows), denominator),
        "continuous_summaries": {
            metric: continuous_summary(row[metric] for row in rows) for metric in CONTINUOUS_METRICS
        },
    }


def formation_group(group: Mapping[str, str], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    numerator = sum(world_stage(row, "formed") for row in rows)
    return {"group": dict(group), **binary_summary(numerator, len(rows))}


def maintenance_group(group: Mapping[str, str], rows: Sequence[Mapping[str, Any]],
                      unit: str) -> dict[str, Any]:
    eligible = [row for row in rows if world_stage(row, "formed")]
    stage_rows = []
    for stage in MAINTENANCE_STAGES:
        numerator = sum(world_stage(row, stage) for row in eligible)
        stage_rows.append({"stage": stage, **binary_summary(numerator, len(eligible))})
    return {"group": dict(group), "denominator": len(eligible), "stage_rows": stage_rows}


def _track_funnel_group(group: Mapping[str, str], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "group": dict(group), "denominator": len(rows),
        "stage_rows": [{"stage": stage, **binary_summary(
            sum(bool(row[stage]) for row in rows), len(rows))} for stage in MAINTENANCE_STAGES],
    }


def formation_maintenance(worlds: Sequence[Mapping[str, Any]], laws: Sequence[str],
                          observations: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    by_ic = [formation_group({"ic_id": ic}, [row for row in worlds if row["ic_id"] == ic])
             for ic in ("soup", "compact")]
    by_law_ic = [formation_group(
        {"law_id": law, "ic_id": ic},
        [row for row in worlds if row["law_id"] == law and row["ic_id"] == ic])
        for law in laws for ic in ("soup", "compact")]
    cumulative = []
    for frame in range(HORIZON):
        cumulative.append({
            "frame": frame,
            "all_formed": sum(row["first_component_frame"] is not None
                              and row["first_component_frame"] <= frame for row in worlds),
            "soup_formed": sum(row["ic_id"] == "soup"
                               and row["first_component_frame"] is not None
                               and row["first_component_frame"] <= frame for row in worlds),
            "compact_formed": sum(row["ic_id"] == "compact"
                                  and row["first_component_frame"] is not None
                                  and row["first_component_frame"] <= frame for row in worlds),
            "all_denominator": len(worlds), "per_ic_denominator": len(worlds) // 2,
        })
    formation = {
        "all": formation_group({}, worlds), "by_ic": by_ic, "by_law_ic": by_law_ic,
        "cumulative_by_frame": cumulative,
    }
    maintenance = {
        "all": maintenance_group({}, worlds, "world"),
        "by_ic": [maintenance_group(
            {"ic_id": ic}, [row for row in worlds if row["ic_id"] == ic], "world")
            for ic in ("soup", "compact")],
        "by_law_ic": [maintenance_group(
            {"law_id": law, "ic_id": ic},
            [row for row in worlds if row["law_id"] == law and row["ic_id"] == ic], "world")
            for law in laws for ic in ("soup", "compact")],
        "stages": list(MAINTENANCE_STAGES), "unit": "original_world",
        "precision_warning": "Four worlds per law/IC are descriptive and not a precise probability estimate.",
    }
    world_lookup = {row["world_id"]: row for row in worlds}
    observation_groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in observations:
        observation_groups[(row["world_id"], row["track_fingerprint"])].append(row)
    track_rows = []
    for (world_id, fingerprint_value), rows in sorted(observation_groups.items()):
        milestone = track_milestones(rows)
        track_rows.append({
            "world_id": world_id, "law_id": world_lookup[world_id]["law_id"],
            "ic_id": world_lookup[world_id]["ic_id"], "track_fingerprint": fingerprint_value,
            "formed": True,
            "bounded_active": milestone["bounded_active"] is not None,
            "persistent": milestone["persistence"] is not None,
            "turnover": milestone["turnover"] is not None,
            "prefix_candidate": milestone["prefix_candidate"] is not None,
            "stable_candidate": milestone["stable_candidate"],
            "terminal_persistence": rows[-1]["frame"] == HORIZON - 1 and bool(rows[-1]["resolved"]),
        })
    track_maintenance = {
        "all": _track_funnel_group({}, track_rows),
        "by_ic": [_track_funnel_group(
            {"ic_id": ic}, [row for row in track_rows if row["ic_id"] == ic])
            for ic in ("soup", "compact")],
        "by_law_ic": [_track_funnel_group(
            {"law_id": law, "ic_id": ic},
            [row for row in track_rows if row["law_id"] == law and row["ic_id"] == ic])
            for law in laws for ic in ("soup", "compact")],
        "stages": list(MAINTENANCE_STAGES), "unit": "diagnostic_track",
        "precision_warning": "Track rows are nested diagnostics and never replace the original-world denominator.",
    }
    return {
        "A_formation": formation,
        "B_conditional_maintenance_world": maintenance,
        "B_conditional_maintenance_track": track_maintenance,
        "gate_conflation_note": (
            "Stage B's unconditional region gate combined formation probability from a neutral IC "
            "with maintenance and turnover conditional on formation; this decomposition cannot "
            "reclassify or rescue Stage B."
        ),
    }


def build_atlas(worlds: Sequence[Mapping[str, Any]], laws: Sequence[str],
                candidate_ids: Mapping[str, Sequence[int]]) -> dict[str, Any]:
    ic_rows = [group_summary({"ic_id": ic}, [row for row in worlds if row["ic_id"] == ic])
               for ic in ("soup", "compact")]
    law_ic_rows = [group_summary(
        {"law_id": law, "ic_id": ic},
        [row for row in worlds if row["law_id"] == law and row["ic_id"] == ic])
        for law in laws for ic in ("soup", "compact")]
    nominal = []
    for law in laws:
        for replicate in range(4):
            soup = next(row for row in worlds if row["law_id"] == law
                        and row["ic_id"] == "soup" and row["replicate"] == replicate)
            compact = next(row for row in worlds if row["law_id"] == law
                           and row["ic_id"] == "compact" and row["replicate"] == replicate)
            differences = {}
            for metric in CONTINUOUS_METRICS:
                first, second = soup[metric], compact[metric]
                differences[metric] = first - second if first is not None and second is not None else None
            nominal.append({
                "law_id": law, "replicate": replicate, "soup_world_id": soup["world_id"],
                "compact_world_id": compact["world_id"], "statistically_matched": False,
                "differences": differences,
            })
    candidate_worlds = [{
        "world_id": row["world_id"], "law_id": row["law_id"], "ic_id": row["ic_id"],
        "candidate_track_count": len(candidate_ids[row["world_id"]]),
        "primary_developmental_pathway": row["primary_developmental_pathway"],
        "terminal_state": row["terminal_state"],
        "first_prefix_candidate_frame": row["first_prefix_candidate_frame"],
        "candidate_status_frames": row["candidate_status_frames"],
        "candidate_episode_count": row["candidate_episode_count"],
        "longest_candidate_episode_frames": row["longest_candidate_episode_frames"],
        "candidate_episode_terminal": row["candidate_episode_terminal"],
        "right_censored": row["right_censored"], "trajectory_class": row["trajectory_class"],
    } for row in worlds if row["committed_regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"]
    estimands = formation_maintenance(worlds, laws)
    return {
        "schema": ATLAS_SCHEMA, "world_count": len(worlds), "ic_class": ic_rows,
        "law_ic": law_ic_rows, "nominal_index_alignment": nominal,
        "candidate_worlds": candidate_worlds,
        "formation_funnel": {
            "all_worlds": binary_summary(
                sum(world_stage(row, "formed") for row in worlds), len(worlds)),
            "by_ic": estimands["A_formation"]["by_ic"],
            "by_law_ic": estimands["A_formation"]["by_law_ic"],
        },
        "maintenance_funnel": {
            "all_worlds": estimands["B_conditional_maintenance_world"]["all"],
            "by_ic": estimands["B_conditional_maintenance_world"]["by_ic"],
            "by_law_ic": estimands["B_conditional_maintenance_world"]["by_law_ic"],
        },
    }


def choose_outcome(audit_valid: bool, duration_available: bool, coherence_available: bool,
                   transient_or_heterogeneous: bool, mechanism_available: bool,
                   actionable: bool) -> tuple[str, dict[str, bool]]:
    if not audit_valid:
        selected = "AUDIT_INVALID"
    elif not duration_available or not coherence_available:
        selected = "RAW_INSUFFICIENT"
    elif transient_or_heterogeneous:
        selected = "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES"
    elif not mechanism_available:
        selected = "RAW_INSUFFICIENT"
    elif actionable:
        selected = "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS"
    else:
        selected = "RAW_INSUFFICIENT"
    truth = {name: name == selected for name in (
        "AUDIT_INVALID", "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES",
        "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS", "RAW_INSUFFICIENT",
    )}
    truth["selected"] = selected  # type: ignore[assignment]
    return selected, truth


def _rows_for_fingerprint(observations: Sequence[Mapping[str, Any]], world_id: str,
                          fingerprint_value: str | None) -> list[Mapping[str, Any]]:
    return sorted((row for row in observations if row["world_id"] == world_id
                   and row["track_fingerprint"] == fingerprint_value), key=lambda row: row["frame"])


def _representative_episode(row: Mapping[str, Any], observations: Sequence[Mapping[str, Any]]) -> tuple[int, int] | None:
    rows = _rows_for_fingerprint(observations, row["world_id"], row["representative_track_fingerprint"])
    runs = consecutive_runs(rows, "prefix_candidate")
    if not runs:
        return None
    longest = max(run[2] for run in runs)
    return min((run for run in runs if run[2] == longest), key=lambda run: run[0])[:2]


def _signature_row(qualified: bool, available: bool, world_ids: Sequence[str],
                   law_ids: Sequence[str], numerator: int, denominator: int,
                   details: Mapping[str, Any], name: str) -> dict[str, Any]:
    return {
        "qualified": qualified, "available": available,
        "world_ids": sorted(world_ids), "law_ids": sorted(set(law_ids)),
        "numerator": numerator, "denominator": denominator, "details": dict(details),
        "interpretation": (
            f"OBSERVATIONAL_SIGNATURE_ONLY:{name}; never causal and never changes DEV_FEASIBILITY_FAIL"
        ),
    }


def exact_frame_window(rows: Sequence[Mapping[str, Any]], start: int, length: int) -> bool:
    return [int(row["frame"]) for row in rows] == list(range(start, start + length))


def compact_precursor_windows(rows: Sequence[Mapping[str, Any]],
                              freeze_onset: int) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["frame"])
    pre = [row for row in ordered if row["frame"] < freeze_onset]
    if not ordered:
        return {"pre": [], "baseline": [], "final_pre": [],
                "bond_available": False, "heterogeneity_available": False,
                "exchange_available": False}
    full_pre = exact_frame_window(pre, int(ordered[0]["frame"]),
                                  freeze_onset - int(ordered[0]["frame"]))
    baseline = ordered[:16]
    baseline_complete = (len(baseline) == 16
                         and exact_frame_window(baseline, int(ordered[0]["frame"]), 16))
    final_pre = [row for row in pre if freeze_onset - 8 <= row["frame"] < freeze_onset]
    final_complete = len(final_pre) == 8 and exact_frame_window(final_pre, freeze_onset - 8, 8)
    return {
        "pre": pre, "baseline": baseline, "final_pre": final_pre,
        "bond_available": full_pre and len(pre) >= 8,
        "heterogeneity_available": full_pre and len(pre) >= 8,
        "exchange_available": full_pre and baseline_complete and final_complete,
    }


def destructive_support_sets(dissolution_ids: Sequence[str],
                             high_exchange_ids: Sequence[str]) -> dict[str, Any]:
    dissolution = sorted(set(dissolution_ids))
    high_exchange = sorted(set(high_exchange_ids))
    overlap = sorted(set(dissolution) & set(high_exchange))
    dissolution_qualified = len(dissolution) >= 9
    high_exchange_qualified = len(high_exchange) >= 9
    if dissolution_qualified and high_exchange_qualified:
        support = overlap if len(overlap) >= 9 else []
    elif dissolution_qualified:
        support = dissolution
    elif high_exchange_qualified:
        support = high_exchange
    else:
        support = []
    return {
        "dissolution": dissolution, "high_exchange": high_exchange, "overlap": overlap,
        "dissolution_qualified": dissolution_qualified,
        "high_exchange_qualified": high_exchange_qualified,
        "same_nine_or_single_subtype": bool(support), "support": support,
    }


def analyze(worlds: Sequence[Mapping[str, Any]], observations: Sequence[Mapping[str, Any]],
            events: Sequence[Mapping[str, Any]], laws: Sequence[str], audit_gates: Mapping[str, bool]) -> dict[str, Any]:
    candidates = [row for row in worlds
                  if row["committed_regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"]
    class_counts = Counter(row["trajectory_class"] for row in candidates)
    dominant_class, dominant_count = (min(class_counts.items(), key=lambda item: (-item[1], item[0]))
                                      if class_counts else (None, 0))
    coherent = len(candidates) == 11 and dominant_count >= 9
    transient_ids = sorted(row["world_id"] for row in candidates
                           if row["longest_candidate_episode_frames"] < 32
                           or not row["candidate_episode_terminal"])
    transient_majority = len(transient_ids) >= 6
    coherence = {
        "candidate_world_count": len(candidates),
        "trajectory_class_counts": {str(key): value for key, value in sorted(class_counts.items())},
        "dominant_class": dominant_class, "dominant_count": dominant_count,
        "coherent": coherent, "transient_count": len(transient_ids),
        "transient_majority": transient_majority,
    }
    duration = {
        "worlds": [{
            "world_id": row["world_id"],
            "candidate_status_frames": row["candidate_status_frames"],
            "candidate_episode_count": row["candidate_episode_count"],
            "longest_candidate_episode_frames": row["longest_candidate_episode_frames"],
            "candidate_episode_terminal": row["candidate_episode_terminal"],
        } for row in candidates],
        "status_frames_summary": continuous_summary(row["candidate_status_frames"] for row in candidates),
        "episode_count_summary": continuous_summary(row["candidate_episode_count"] for row in candidates),
        "longest_episode_summary": continuous_summary(
            row["longest_candidate_episode_frames"] for row in candidates),
        "terminal_episode_count": sum(row["candidate_episode_terminal"] for row in candidates),
    }
    touches = []
    for row in candidates:
        track_rows = _rows_for_fingerprint(observations, row["world_id"],
                                           row["representative_track_fingerprint"])
        if any(item["frame"] == HORIZON - 1 and item["prefix_candidate"] for item in track_rows):
            touches.append(row["world_id"])
    censoring = {
        "right_censored_worlds": sum(row["right_censored"] for row in worlds),
        "candidate_right_censored": sum(row["right_censored"] for row in candidates),
        "candidate_status_touches_159": len(touches),
        "coordinate_seam_crossers": sum(row["coordinate_seam_crossed"] for row in worlds),
        "winding_worlds": sum(row["ever_wound"] for row in worlds),
    }

    formation_laws = []
    soup_formed = sum(row["ic_id"] == "soup" and world_stage(row, "formed") for row in worlds)
    compact_formed = sum(row["ic_id"] == "compact" and world_stage(row, "formed") for row in worlds)
    aggregate_difference = soup_formed / 32 - compact_formed / 32
    direction_sign = 1 if aggregate_difference > 0 else -1 if aggregate_difference < 0 else 0
    direction = ("SOUP_GT_COMPACT" if direction_sign > 0 else
                 "COMPACT_GT_SOUP" if direction_sign < 0 else "EQUAL")
    for law in laws:
        soup = sum(row["law_id"] == law and row["ic_id"] == "soup"
                   and world_stage(row, "formed") for row in worlds)
        compact = sum(row["law_id"] == law and row["ic_id"] == "compact"
                      and world_stage(row, "formed") for row in worlds)
        difference = soup / 4 - compact / 4
        qualifies = direction_sign != 0 and difference * direction_sign >= 0.25
        formation_laws.append({
            "law_id": law, "soup_formed": soup, "compact_formed": compact,
            "per_ic_denominator": 4, "difference": difference,
            "same_direction_qualifies": qualifies,
        })
    formation_qualified = abs(aggregate_difference) >= 0.25 and sum(
        row["same_direction_qualifies"] for row in formation_laws) >= 6
    signatures: dict[str, dict[str, Any]] = {}
    signatures["IC_FORMATION_DEPENDENCE"] = _signature_row(
        formation_qualified, True,
        [row["world_id"] for row in worlds if world_stage(row, "formed")],
        [row["law_id"] for row in formation_laws if row["same_direction_qualifies"]],
        sum(row["same_direction_qualifies"] for row in formation_laws), 8,
        {"soup_formed": soup_formed, "compact_formed": compact_formed,
         "per_ic_denominator": 32, "aggregate_difference": aggregate_difference,
         "direction": direction, "law_rows": formation_laws,
         "qualifying_law_count": sum(row["same_direction_qualifies"] for row in formation_laws)},
        "IC_FORMATION_DEPENDENCE")

    frozen = [row for row in worlds if row["terminal_state"] == "FROZEN"]
    compact_frozen = [row for row in frozen if row["ic_id"] == "compact"]
    soup_frozen = [row for row in frozen if row["ic_id"] == "soup"]
    freeze_laws = []
    for law in laws:
        compact_count = sum(row["law_id"] == law for row in compact_frozen)
        soup_count = sum(row["law_id"] == law for row in soup_frozen)
        difference = compact_count / 4 - soup_count / 4
        freeze_laws.append({
            "law_id": law, "compact_frozen": compact_count, "soup_frozen": soup_count,
            "per_ic_denominator": 4, "difference": difference, "qualifies": difference >= 0.25,
        })
    freeze_gate = (len(compact_frozen) / 32 - len(soup_frozen) / 32 >= 0.25
                   and sum(row["qualifies"] for row in freeze_laws) >= 6)
    precursor_ids: dict[str, list[str]] = {name: [] for name in (
        "BOND_SATURATION", "LOW_INTERNAL_HETEROGENEITY", "REDUCED_MATERIAL_EXCHANGE")}
    precursor_unavailable: dict[str, list[str]] = {name: [] for name in precursor_ids}
    for world in compact_frozen:
        rows = _rows_for_fingerprint(observations, world["world_id"],
                                     world["representative_track_fingerprint"])
        freeze_onset = world["terminal_freeze_onset"]
        if freeze_onset is None:
            raise AuditError("frozen world lacks freeze onset")
        windows = compact_precursor_windows(rows, freeze_onset)
        saturation = next((row["frame"] for row in rows
                           if row["internal_bond_saturation_fraction"] >= 0.5), None)
        if windows["bond_available"] and saturation is not None and saturation <= freeze_onset - 8:
            precursor_ids["BOND_SATURATION"].append(world["world_id"])
        if not windows["bond_available"]:
            precursor_unavailable["BOND_SATURATION"].append(world["world_id"])
        pre = windows["pre"]
        hetero_runs = []
        current = 0; previous = None
        for row in pre:
            if (row["matter_cv"] < 0.05 and row["resource_cv"] < 0.05
                    and (previous is None or row["frame"] == previous + 1)):
                current += 1
            elif row["matter_cv"] < 0.05 and row["resource_cv"] < 0.05:
                current = 1
            else:
                current = 0
            hetero_runs.append(current); previous = row["frame"]
        if windows["heterogeneity_available"] and max(hetero_runs, default=0) >= 8:
            precursor_ids["LOW_INTERNAL_HETEROGENEITY"].append(world["world_id"])
        if not windows["heterogeneity_available"]:
            precursor_unavailable["LOW_INTERNAL_HETEROGENEITY"].append(world["world_id"])
        baseline = windows["baseline"]
        final_pre = windows["final_pre"]
        baseline_median = exact_median([row["matter_exchange_per_mass"] for row in baseline])
        pre_median = exact_median([row["matter_exchange_per_mass"] for row in final_pre])
        if (not windows["exchange_available"] or baseline_median is None
                or baseline_median <= 0.0):
            precursor_unavailable["REDUCED_MATERIAL_EXCHANGE"].append(world["world_id"])
        elif pre_median is not None and pre_median <= 0.25 * baseline_median:
            precursor_ids["REDUCED_MATERIAL_EXCHANGE"].append(world["world_id"])
    required = math.ceil(0.75 * len(compact_frozen))
    precursors = {}
    for name in precursor_ids:
        available = not precursor_unavailable[name]
        qualified = bool(compact_frozen) and available and len(precursor_ids[name]) >= required
        precursors[name] = {
            "numerator": len(precursor_ids[name]), "denominator": len(compact_frozen),
            "required": required, "available": available, "qualified": qualified,
            "world_ids": sorted(precursor_ids[name]),
        }
    qualified_precursors = [name for name, item in precursors.items() if item["qualified"]]
    compact_available = all(item["available"] for item in precursors.values())
    compact_qualified = freeze_gate and compact_available and len(qualified_precursors) == 1
    signatures["COMPACT_PREMATURE_FREEZE"] = _signature_row(
        compact_qualified, compact_available,
        [row["world_id"] for row in compact_frozen],
        [row["law_id"] for row in freeze_laws if row["qualifies"]],
        sum(row["qualifies"] for row in freeze_laws), 8,
        {"compact_frozen": len(compact_frozen), "soup_frozen": len(soup_frozen),
         "per_ic_denominator": 32, "law_rows": freeze_laws,
         "qualifying_law_count": sum(row["qualifies"] for row in freeze_laws),
         "N_compact_frozen": len(compact_frozen), "precursors": precursors,
         "unique_precursor": qualified_precursors[0] if len(qualified_precursors) == 1 else None},
        "COMPACT_PREMATURE_FREEZE")

    dissolution_ids: list[str] = []
    high_exchange_ids: list[str] = []
    destructive_unavailable: list[str] = []
    for world in candidates:
        episode = _representative_episode(world, observations)
        rows = _rows_for_fingerprint(observations, world["world_id"],
                                     world["representative_track_fingerprint"])
        if episode is None:
            destructive_unavailable.append(world["world_id"]); continue
        onset, end = episode
        representative_track_ids = {row["track_id"] for row in rows}
        later_dissolutions = [event["frame"] for event in events
                              if event["world_id"] == world["world_id"]
                              and event["event_type"] == "DISSOLUTION"
                              and set(event["source_track_ids"]) == representative_track_ids
                              and end < event["frame"] < HORIZON - 1]
        if later_dissolutions and min(later_dissolutions) - end <= 32:
            dissolution_ids.append(world["world_id"])
        baseline_values = [row["matter_exchange_per_mass"] for row in rows if row["frame"] < onset]
        episode_values = [row["matter_exchange_per_mass"] for row in rows
                          if onset <= row["frame"] <= end]
        baseline_median = exact_median(baseline_values)
        episode_median = exact_median(episode_values)
        if baseline_median is None or baseline_median <= 0.0 or episode_median is None:
            destructive_unavailable.append(world["world_id"])
        elif episode_median >= 2.0 * baseline_median:
            high_exchange_ids.append(world["world_id"])
    destructive_sets = destructive_support_sets(dissolution_ids, high_exchange_ids)
    dissolution_q = destructive_sets["dissolution_qualified"]
    high_exchange_q = destructive_sets["high_exchange_qualified"]
    overlap = destructive_sets["overlap"]
    same_nine = destructive_sets["same_nine_or_single_subtype"]
    destructive_support = destructive_sets["support"]
    destructive_support_laws = sorted({
        row["law_id"] for row in candidates if row["world_id"] in destructive_support})
    destructive_available = not destructive_unavailable
    destructive_qualified = (destructive_available and same_nine
                             and len(destructive_support_laws) >= 4)
    signatures["DESTRUCTIVE_TRANSITION_PROXIMITY"] = _signature_row(
        destructive_qualified, destructive_available, destructive_support,
        destructive_support_laws,
        len(destructive_support), 11,
        {"dissolution_subtype_world_ids": sorted(dissolution_ids),
         "high_exchange_subtype_world_ids": sorted(high_exchange_ids),
         "overlap_world_ids": overlap, "unavailable_world_ids": sorted(set(destructive_unavailable)),
         "dissolution_subtype_qualified": dissolution_q,
         "high_exchange_subtype_qualified": high_exchange_q,
         "same_nine_or_single_subtype": same_nine},
        "DESTRUCTIVE_TRANSITION_PROXIMITY")

    finite_support = sorted(set(touches) & {row["world_id"] for row in candidates if row["right_censored"]})
    finite_laws = sorted({row["law_id"] for row in candidates if row["world_id"] in finite_support})
    finite_q = len(finite_support) >= 9 and len(finite_laws) >= 4
    signatures["FINITE_HORIZON_CENSORING"] = _signature_row(
        finite_q, True, finite_support, finite_laws, len(finite_support), 11,
        {"candidate_right_censored": sum(row["right_censored"] for row in candidates),
         "candidate_status_touches_159": len(touches),
         "supporting_law_count": len(finite_laws), "supporting_world_ids": finite_support},
        "FINITE_HORIZON_CENSORING")
    brief_ids = sorted(row["world_id"] for row in candidates
                       if row["longest_candidate_episode_frames"] < 32)
    nonterminal_ids = sorted(row["world_id"] for row in candidates
                             if not row["candidate_episode_terminal"])
    signatures["TRANSIENT_THRESHOLD_CROSSING"] = _signature_row(
        transient_majority, True, transient_ids,
        [row["law_id"] for row in candidates if row["world_id"] in transient_ids],
        len(transient_ids), 11,
        {"brief_world_ids": brief_ids, "nonterminal_world_ids": nonterminal_ids,
         "union_world_ids": transient_ids, "transient_count": len(transient_ids)},
        "TRANSIENT_THRESHOLD_CROSSING")

    unavailable_reasons = []
    if not signatures["COMPACT_PREMATURE_FREEZE"]["available"]:
        unavailable_reasons.append("COMPACT_PREMATURE_FREEZE precursor window unavailable")
    if not signatures["DESTRUCTIVE_TRANSITION_PROXIMITY"]["available"]:
        unavailable_reasons.append(
            "DESTRUCTIVE_TRANSITION_PROXIMITY same-track baseline unavailable")
    availability = {name: signatures[name]["available"] for name in signatures}
    availability["unavailable_reasons"] = unavailable_reasons
    eligible = [name for name in (
        "IC_FORMATION_DEPENDENCE", "COMPACT_PREMATURE_FREEZE",
        "DESTRUCTIVE_TRANSITION_PROXIMITY", "FINITE_HORIZON_CENSORING",
    ) if signatures[name]["qualified"] and len(signatures[name]["law_ids"]) >= 4]
    audit_valid = all(audit_gates.values())
    mechanism_available = all(signatures[name]["available"] for name in (
        "IC_FORMATION_DEPENDENCE", "COMPACT_PREMATURE_FREEZE",
        "DESTRUCTIVE_TRANSITION_PROXIMITY", "FINITE_HORIZON_CENSORING",
    ))
    outcome, truth = choose_outcome(
        audit_valid, len(candidates) == 11, len(candidates) == 11,
        transient_majority or not coherent, mechanism_available, len(eligible) == 1,
    )
    compact_static = {
        "compact_frozen_count": len(compact_frozen), "soup_frozen_count": len(soup_frozen),
        "bond_saturation_precursor": precursors["BOND_SATURATION"],
        "low_internal_heterogeneity_precursor": precursors["LOW_INTERNAL_HETEROGENEITY"],
        "reduced_material_exchange_precursor": precursors["REDUCED_MATERIAL_EXCHANGE"],
        "low_throughput_definition_only": True,
        "common_precursor_count": len(qualified_precursors),
    }
    recommendations = {
        "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS": (
            "Human review may consider a fresh, separately preregistered developmental design "
            "testing the single observational signature."
        ),
        "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES": (
            "Do not select or promote candidate worlds; any future work requires a fresh pre-data "
            "design aimed at formation and stability separately."
        ),
        "RAW_INSUFFICIENT": (
            "Persisted Stage-B variables do not select a unique developmental account; stop unless "
            "a fresh measurement design is authorized."
        ),
        "AUDIT_INVALID": "Audit invalid; stop and preserve the failed evidence package for human review.",
    }
    return {
        "schema": ANALYSIS_SCHEMA, "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
        "autopsy_outcome": outcome, "audit_gates": dict(audit_gates) | {"valid": audit_valid},
        "candidate_coherence": coherence, "candidate_duration": duration,
        "censoring": censoring, "compact_static_audit": compact_static,
        "observational_signatures_consistent_with": signatures,
        "signature_availability": availability,
        "formation_maintenance_estimands": formation_maintenance(worlds, laws, observations),
        "outcome_truth_table": truth,
        "bounded_roadmap": {
            "recommendation": recommendations[outcome],
            "allowed_next_action": "human review of this raw-only developmental autopsy",
            "forbidden_actions": [
                "Stage C", "candidate promotion or subset selection",
                "threshold or two-of-four revision", "family extension, retry or new seed",
                "causal, memory, ownership or individuality claim",
            ],
        },
    }


def reconstruct_classification(manifest_sha256: str, classified: Sequence[Mapping[str, Any]],
                               laws: Sequence[str]) -> dict[str, Any]:
    world_rows = [{
        "candidate_track_ids": list(row["candidate_track_ids"]),
        "ic_id": row["ic_id"], "law_id": row["law_id"], "regime": row["regime"],
        "replicate": row["replicate"], "status": "COMPLETE", "world_id": row["world_id"],
    } for row in sorted(classified, key=lambda row: row["world_id"])]
    atlas = []
    candidate_laws: list[str] = []
    for law in laws:
        per_ic = []
        candidate_counts: dict[str, int] = {}
        for ic in ("soup", "compact"):
            rows = [row for row in world_rows if row["law_id"] == law and row["ic_id"] == ic]
            counts = {regime: sum(row["regime"] == regime for row in rows) for regime in REGIMES}
            complete = len(rows) == 4 and all(row["status"] == "COMPLETE" for row in rows)
            per_ic.append({"complete": complete, "counts": counts,
                           "denominator": len(rows), "ic_id": ic})
            candidate_counts[ic] = counts["BOUNDED_ACTIVE_TURNOVER_CANDIDATE"]
        reproducible = (all(row["complete"] for row in per_ic)
                        and candidate_counts["soup"] >= 2 and candidate_counts["compact"] >= 2)
        atlas.append({"law_id": law, "per_ic": per_ic, "region_id": law,
                      "reproducible_candidate": reproducible})
        if reproducible:
            candidate_laws.append(law)
    if any(row["status"] != "COMPLETE" for row in world_rows):
        disposition = "REVISE_INSTRUMENTATION"
    else:
        disposition = "DEV_REGIME_CANDIDATE" if candidate_laws else "DEV_FEASIBILITY_FAIL"
    return {
        "atlas": atlas, "candidate_regions": candidate_laws, "disposition": disposition,
        "manifest_sha256": manifest_sha256, "schema": CLASSIFICATION_SCHEMA, "worlds": world_rows,
    }


def accepted_parent_blobs(repo: Path, paths: Sequence[str]) -> dict[str, str]:
    command = ["git", "ls-tree", "-r", ACCEPTED_PARENT, "--", *paths]
    completed = subprocess.run(command, cwd=repo, check=False, capture_output=True, text=True,
                               encoding="utf-8", errors="strict")
    if completed.returncode != 0:
        raise AuditError(f"accepted-parent git metadata query failed: {completed.stderr.strip()}")
    blobs: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        prefix, path = line.split("\t", 1)
        mode, kind, oid = prefix.split(" ")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise AuditError(f"accepted-parent path is not a regular blob: {path}")
        blobs[path] = oid
    if set(blobs) != set(paths):
        raise AuditError("accepted-parent tree does not contain exact input path inventory")
    return blobs


def authenticated_npz(guard: ReadGuard, path: str, expected_size: int,
                      expected_sha256: str, expected_git_oid: str,
                      label: str) -> tuple[bytes, dict[str, np.ndarray]]:
    """Parse only the exact byte string that passed the second authentication."""
    raw = guard.read(path)
    if (len(raw) != expected_size or sha256_bytes(raw) != expected_sha256
            or git_blob_oid(raw) != expected_git_oid):
        raise AuditError(f"physics changed after authentication: {path}")
    return raw, load_npz_bytes(raw, label)


def exact_independent_output_root(repo: Path, requested: Path,
                                  planned_relative: str) -> Path:
    normalized_plan = planned_relative.replace("\\", "/")
    normalized_request = str(requested).replace("\\", "/")
    plan_parts = Path(normalized_plan).parts
    if (Path(normalized_plan).is_absolute() or ".." in plan_parts
            or normalized_request != normalized_plan):
        raise AuditError("output root is not the exact planned independent root")
    candidate = repo.joinpath(*plan_parts)
    try:
        candidate.resolve(strict=False).relative_to(repo)
    except ValueError as exc:
        raise AuditError("output root escapes repository") from exc
    probe = repo
    for part in plan_parts[:-1]:
        probe = probe / part
        if not probe.exists():
            raise AuditError("planned output parent must already exist")
        if not probe.is_dir() or probe.is_symlink() or _is_reparse(probe):
            raise AuditError("planned output parent is not a regular directory")
    return candidate


def runtime_gate() -> dict[str, Any]:
    interpreter = "C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe"
    actual = {
        "interpreter": interpreter, "python": platform.python_version(),
        "numpy": np.__version__, "pytest": importlib_metadata.version("pytest"),
        "byteorder": sys.byteorder,
    }
    expected_executable = Path("C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe").resolve()
    if (actual["python"] != "3.12.10" or actual["numpy"] != "2.5.1"
            or actual["pytest"] != "8.4.2" or actual["byteorder"] != "little"
            or Path(sys.executable).resolve() != expected_executable):
        raise AuditError(f"runtime mismatch: {actual}")
    return actual


def write_exclusive(path: Path, raw: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def publish(output_root: Path, payloads: Mapping[str, bytes], complete_base: Mapping[str, Any],
            counts: Mapping[str, int]) -> None:
    partial = output_root.with_name(output_root.name + ".partial")
    if output_root.exists() or partial.exists():
        raise AuditError("final or partial output root already exists")
    partial.parent.mkdir(parents=True, exist_ok=True)
    partial.mkdir()
    expected = {
        "integrity.json", "recomputed_classification.json", "world_transitions.json",
        "track_observations.jsonl", "events.jsonl", "trajectory_atlas.json", "analysis.json",
    }
    if set(payloads) != expected:
        raise AuditError("closed publication inventory mismatch")
    for name in sorted(payloads):
        write_exclusive(partial / name, payloads[name])
    file_rows = [{"path": name, "bytes": len(payloads[name]), "sha256": sha256_bytes(payloads[name])}
                 for name in sorted(payloads)]
    complete = dict(complete_base) | {"files": file_rows, "counts": dict(counts)}
    write_exclusive(partial / "COMPLETE.json", canonical_bytes(complete))
    try:
        directory_fd = os.open(partial, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError:
        if os.name != "nt":
            raise
    os.replace(partial, output_root)


def _manifest_world_ids(manifest: Mapping[str, Any]) -> list[str]:
    try:
        values = manifest["execution"]["world_ids"]
    except (KeyError, TypeError) as exc:
        raise AuditError("manifest lacks execution.world_ids") from exc
    if (not isinstance(values, list) or len(values) != 64
            or len(set(values)) != 64 or not all(isinstance(value, str) for value in values)):
        raise AuditError("manifest world inventory mismatch")
    return list(values)


def validate_root_manifest(root_manifest: Mapping[str, Any], semantic_gate: Mapping[str, Any],
                           world_ids: Sequence[str],
                           manifest_sha256: str, classification_sha256: str,
                           classification_bytes: int) -> None:
    expected_top = set(semantic_gate["top_keys"])
    if set(root_manifest) != expected_top:
        raise AuditError("root manifest exact top-level schema mismatch")
    if (root_manifest["schema"] != semantic_gate["schema"]
            or root_manifest["world_count"] != semantic_gate["world_count"]
            or root_manifest["disposition"] != semantic_gate["disposition"]
            or root_manifest["manifest_sha256"] != manifest_sha256
            or root_manifest["classification_sha256"] != classification_sha256
            or root_manifest["classification_bytes"] != classification_bytes):
        raise AuditError("root manifest population/disposition/input binding mismatch")
    for key in ("enrollment_sha256", "raw_schema_sha256"):
        value = root_manifest[key]
        if (not isinstance(value, str) or len(value) != 64
                or any(character not in "0123456789abcdef" for character in value)):
            raise AuditError(f"root manifest invalid {key}")
    if (not isinstance(root_manifest["enrollment_bytes"], int)
            or isinstance(root_manifest["enrollment_bytes"], bool)
            or root_manifest["enrollment_bytes"] <= 0):
        raise AuditError("root manifest invalid enrollment_bytes")
    shards = root_manifest["shards"]
    if not isinstance(shards, list) or len(shards) != semantic_gate["world_count"]:
        raise AuditError("root manifest shard enrollment count mismatch")
    expected_shard = set(semantic_gate["shard_row_keys"])
    enrolled_worlds: list[str] = []
    for row in shards:
        if not isinstance(row, dict) or set(row) != expected_shard:
            raise AuditError("root manifest exact shard-row schema mismatch")
        if row["status"] != semantic_gate["shard_status"] or not isinstance(row["world_id"], str):
            raise AuditError("root manifest contains non-COMPLETE/invalid shard")
        if (not isinstance(row["shard_manifest_bytes"], int)
                or isinstance(row["shard_manifest_bytes"], bool)
                or row["shard_manifest_bytes"] <= 0):
            raise AuditError("root manifest invalid shard byte count")
        digest = row["shard_manifest_sha256"]
        if (not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)):
            raise AuditError("root manifest invalid shard SHA-256")
        enrolled_worlds.append(row["world_id"])
    if (len(set(enrolled_worlds)) != semantic_gate["world_count"]
            or set(enrolled_worlds) != set(world_ids)):
        raise AuditError("root manifest shard world set mismatch")


def _world_metadata(world_id: str) -> dict[str, Any]:
    parts = world_id.split("__")
    if (len(parts) != 3 or not parts[0].startswith("L")
            or parts[1] not in {"soup", "compact"} or not parts[2].startswith("r")):
        raise AuditError(f"invalid frozen world identifier {world_id!r}")
    return {"world_id": world_id, "law_id": parts[0], "ic_id": parts[1],
            "replicate": int(parts[2][1:])}


def run_raw(plan_path: str, allowlist_path: str, output_root: Path) -> None:
    runtime = runtime_gate()
    repo = Path.cwd().resolve()
    exact_control_request(plan_path, PLAN_CONTROL_PATH)
    exact_control_request(allowlist_path, ALLOWLIST_CONTROL_PATH)
    control_guard = ReadGuard(repo, (
        PLAN_CONTROL_PATH, ALLOWLIST_CONTROL_PATH, PROTOCOL_CONTROL_PATH))
    plan_raw = control_guard.read(PLAN_CONTROL_PATH)
    allowlist_raw = control_guard.read(ALLOWLIST_CONTROL_PATH)
    plan_hash = sha256_bytes(plan_raw)
    allowlist_hash = sha256_bytes(allowlist_raw)
    plan = parse_json(plan_raw, "plan")
    allowlist = parse_json(allowlist_raw, "allowlist")
    if (plan.get("schema") != PLAN_SCHEMA or plan.get("mission") != MISSION
            or plan.get("accepted_parent") != ACCEPTED_PARENT):
        raise AuditError("plan identity mismatch")
    if (allowlist.get("schema") != ALLOWLIST_SCHEMA or allowlist.get("mission") != MISSION
            or allowlist.get("accepted_parent") != ACCEPTED_PARENT):
        raise AuditError("allowlist identity mismatch")
    independent_output = exact_independent_output_root(
        repo, output_root, plan["planned_outputs"]["independent_root"])
    bindings = plan["input_bindings"]
    if bindings["source_allowlist"]["path"] != ALLOWLIST_CONTROL_PATH:
        raise AuditError("allowlist control binding path is not exact frozen literal")
    if allowlist_hash != bindings["source_allowlist"]["sha256"]:
        raise AuditError("allowlist hash mismatch")
    if bindings["reconstruction_protocol"]["path"] != PROTOCOL_CONTROL_PATH:
        raise AuditError("protocol control path is not exact frozen literal")
    protocol_raw = control_guard.read(PROTOCOL_CONTROL_PATH)
    protocol_hash = sha256_bytes(protocol_raw)
    protocol = parse_json(protocol_raw, "protocol")
    if (protocol_hash != bindings["reconstruction_protocol"]["sha256"]
            or protocol.get("schema") != PROTOCOL_SCHEMA):
        raise AuditError("protocol binding mismatch")

    scientific = allowlist["scientific_inputs"]
    metadata_paths = list(scientific["metadata"])
    physics_paths = list(scientific["physics_shards"])
    if len(metadata_paths) != 3 or len(physics_paths) != 64:
        raise AuditError("scientific allowlist cardinality mismatch")
    guard = ReadGuard(repo, metadata_paths + physics_paths)
    all_paths = metadata_paths + physics_paths
    tree_blobs = accepted_parent_blobs(repo, all_paths)
    record = "".join(f"{path}\t{tree_blobs[path]}\n" for path in sorted(physics_paths)).encode("utf-8")
    if sha256_bytes(record) != bindings["accepted_parent_physics_git_tree"]["aggregate_sha256"]:
        raise AuditError("accepted-parent physics tree aggregate mismatch")

    input_rows = []
    metadata_raw: dict[str, bytes] = {}
    for path in metadata_paths:
        raw = guard.read(path)
        expected_hash = next(item["sha256"] for item in bindings.values()
                             if isinstance(item, dict) and item.get("path") == path)
        if sha256_bytes(raw) != expected_hash:
            raise AuditError(f"metadata hash mismatch: {path}")
        oid = git_blob_oid(raw)
        if oid != tree_blobs[path]:
            raise AuditError(f"metadata Git blob mismatch: {path}")
        metadata_raw[path] = raw
        input_rows.append({"path": path, "bytes": len(raw), "sha256": sha256_bytes(raw),
                           "accepted_parent_git_blob_oid": tree_blobs[path], "git_blob_match": True})
    manifest_path = bindings["manifest"]["path"]
    root_manifest_path = bindings["root_manifest"]["path"]
    classification_path = bindings["committed_classification"]["path"]
    manifest = parse_json(metadata_raw[manifest_path], "manifest")
    root_manifest = parse_json(metadata_raw[root_manifest_path], "root manifest")
    committed = parse_json(metadata_raw[classification_path], "classification", canonical=True)
    world_ids = _manifest_world_ids(manifest)
    validate_root_manifest(
        root_manifest, bindings["root_manifest"]["semantic_gate"], world_ids,
        sha256_bytes(metadata_raw[manifest_path]),
        sha256_bytes(metadata_raw[classification_path]), len(metadata_raw[classification_path]))
    expected_physics = [f"results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV/{world}/physics.npz"
                        for world in world_ids]
    if physics_paths != expected_physics:
        raise AuditError("allowlist physics order/path rule mismatch")
    committed_by_world = {row["world_id"]: row for row in committed["worlds"]}
    if set(committed_by_world) != set(world_ids):
        raise AuditError("committed classification world set mismatch")

    physics_preflight: dict[str, tuple[int, str]] = {}
    for path in physics_paths:
        raw = guard.read(path)
        oid = git_blob_oid(raw)
        if oid != tree_blobs[path]:
            raise AuditError(f"physics Git blob mismatch: {path}")
        digest = sha256_bytes(raw)
        physics_preflight[path] = (len(raw), digest)
        input_rows.append({"path": path, "bytes": len(raw), "sha256": digest,
                           "accepted_parent_git_blob_oid": tree_blobs[path], "git_blob_match": True})

    classified_rows = []
    world_rows = []
    observation_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    candidate_ids: dict[str, list[int]] = {}
    maximum_reference_error = 0.0
    maximum_transport_error = 0.0
    maximum_matter_residual = 0.0
    maximum_energy_residual = 0.0
    for world_id, path in zip(world_ids, physics_paths, strict=True):
        # This is the first NumPy touch of the shard.  The single in-memory byte
        # string returned here is authenticated and then passed to the loader;
        # no path is reopened between authentication and parsing.
        raw, arrays = authenticated_npz(
            guard, path, physics_preflight[path][0], physics_preflight[path][1],
            tree_blobs[path], world_id)
        qualify_raw(arrays)
        maximum_reference_error = max(
            maximum_reference_error, float(np.max(arrays["vector_reference_max_error"])))
        maximum_matter_residual = max(
            maximum_matter_residual, float(np.max(np.abs(arrays["ledger__matter_residual"]))))
        maximum_energy_residual = max(
            maximum_energy_residual, float(np.max(np.abs(arrays["ledger__energy_residual"]))))
        for frame in range(HORIZON):
            net = arrays["ledger__matter_forward"][frame] - arrays["ledger__matter_reverse"][frame]
            expected_post = arrays["state_m"][frame] - DT * divergence(net)
            maximum_transport_error = max(
                maximum_transport_error,
                float(np.max(np.abs(arrays["state_m"][frame + 1] - expected_post))),
            )
        frames = [detect(arrays["state_m"][frame], frame) for frame in range(HORIZON)]
        tracking = track_components(world_id, frames)
        observations, summaries = observe_tracks(world_id, arrays, frames, tracking)
        regime, ids = classify_world(frames, tracking, summaries)
        committed_row = committed_by_world[world_id]
        metadata = _world_metadata(world_id)
        classified_rows.append({
            "world_id": world_id, "law_id": metadata["law_id"],
            "ic_id": metadata["ic_id"], "replicate": metadata["replicate"],
            "regime": regime, "candidate_track_ids": ids,
        })
        candidate_ids[world_id] = ids
        world_rows.append(develop_world(
            metadata, committed_row["regime"], committed_row["candidate_track_ids"],
            regime, ids, frames, tracking, observations,
        ))
        observation_rows.extend(observations)
        event_rows.extend(tracking.events)

    laws = list(dict.fromkeys(_world_metadata(world_id)["law_id"] for world_id in world_ids))
    recomputed = reconstruct_classification(sha256_bytes(metadata_raw[manifest_path]),
                                            classified_rows, laws)
    recomputed_raw = canonical_bytes(recomputed)
    classification_identity = recomputed_raw == metadata_raw[classification_path]
    candidate_identity = all(
        row["candidate_track_ids"] == committed_by_world[row["world_id"]]["candidate_track_ids"]
        for row in classified_rows)
    audit_gates = {
        "input_bindings": True, "git_blob_identity": True, "raw_layout": True,
        "numerical_qualification": True, "classification_byte_identity": classification_identity,
        "candidate_set_identity": candidate_identity, "world_count": len(world_rows) == 64,
    }
    if not classification_identity or not candidate_identity or len(world_rows) != 64:
        raise AuditError("post-reconstruction audit gate failed")
    atlas = build_atlas(world_rows, laws, candidate_ids)
    analysis = analyze(world_rows, observation_rows, event_rows, laws, audit_gates)
    integrity = {
        "schema": INTEGRITY_SCHEMA, "accepted_parent": ACCEPTED_PARENT,
        "plan_sha256": plan_hash, "protocol_sha256": protocol_hash,
        "allowlist_sha256": allowlist_hash, "runtime": runtime,
        "input_files": input_rows,
        "git_tree_binding": {
            "blob_count": len(physics_paths), "aggregate_sha256": sha256_bytes(record),
            "all_match": True,
        },
        "raw_inventory": {"key_count": len(EXPECTED_KEYS), "keys": sorted(EXPECTED_KEYS)},
        "qualification_gates": {
            "world_count": len(world_rows), "all_layout_valid": True,
            "all_numerically_valid": True, "maximum_reference_error": maximum_reference_error,
            "maximum_transport_error": maximum_transport_error,
            "maximum_matter_residual": maximum_matter_residual,
            "maximum_energy_residual": maximum_energy_residual,
        },
        "audit_valid": True,
    }
    payloads = {
        "integrity.json": canonical_bytes(integrity),
        "recomputed_classification.json": recomputed_raw,
        "world_transitions.json": canonical_bytes({
            "schema": WORLD_SCHEMA, "world_count": len(world_rows), "worlds": world_rows}),
        "track_observations.jsonl": b"".join(canonical_line(row) for row in observation_rows),
        "events.jsonl": b"".join(canonical_line(row) for row in event_rows),
        "trajectory_atlas.json": canonical_bytes(atlas), "analysis.json": canonical_bytes(analysis),
    }
    complete_base = {
        "schema": COMPLETE_SCHEMA, "status": "COMPLETE", "accepted_parent": ACCEPTED_PARENT,
        "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
        "autopsy_outcome": analysis["autopsy_outcome"], "plan_sha256": plan_hash,
        "protocol_sha256": protocol_hash, "allowlist_sha256": allowlist_hash,
    }
    publish(independent_output, payloads, complete_base, {
        "worlds": len(world_rows), "tracks": len({
            (row["world_id"], row["track_id"]) for row in observation_rows}),
        "track_observations": len(observation_rows), "events": len(event_rows),
        "candidate_worlds": sum(row["committed_regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
                                for row in world_rows),
    })


def _component_rows(count: int, turnover_at: int | None = None,
                    candidate_from: int | None = None, resolved: bool = True) -> list[dict[str, Any]]:
    rows = []
    for frame in range(count):
        turnover = 0.7 if turnover_at is not None and frame >= turnover_at else 0.0
        rows.append({
            "frame": frame, "resolved": resolved, "area_fraction": 3 / 144,
            "percolated": False, "activity_per_mass": 2e-4,
            "energy_throughput_per_mass": 2e-5, "turnover_fraction": turnover,
            "prefix_candidate": candidate_from is not None and frame >= candidate_from,
        })
    return rows


def _tiny_npz(layout: Mapping[str, tuple[np.dtype[Any], tuple[int, ...]]],
              override: Mapping[str, np.ndarray] | None = None) -> bytes:
    arrays = {name: np.zeros(shape, dtype=dtype) for name, (dtype, shape) in layout.items()}
    if override:
        arrays.update(override)
    stream = io.BytesIO()
    np.savez(stream, **arrays)
    return stream.getvalue()


def _replace_zip_member(raw: bytes, member_name: str, member_raw: bytes,
                        duplicate: bool = False) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw), "r") as source, zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_STORED) as target:
        for member in source.infolist():
            if member.filename != member_name:
                target.writestr(member.filename, source.read(member.filename))
            elif duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    target.writestr(member.filename, source.read(member.filename))
                    target.writestr(member.filename, source.read(member.filename))
            else:
                target.writestr(member.filename, member_raw)
    return output.getvalue()


def _npy_bytes(array: np.ndarray) -> bytes:
    stream = io.BytesIO()
    np.save(stream, array, allow_pickle=True)
    return stream.getvalue()


def self_test() -> dict[str, Any]:
    passed: list[str] = []

    matter = np.zeros(SHAPE, dtype=np.float64)
    matter[0, 11] = matter[0, 0] = matter[0, 1] = 1.0
    components = detect(matter, 0)
    assert len(components) == 1 and components[0].cells == ((0, 0), (0, 1), (0, 11))
    assert fingerprint(components[0]) == "0:0,1,11"
    passed.append("detector_periodic_lift_and_fingerprint")

    stable_matter = np.zeros(SHAPE, dtype=np.float64)
    stable_matter[2, 2:5] = 1.0
    frames = [detect(stable_matter, frame) for frame in range(HORIZON)]
    tracking = track_components("SYNTH", frames)
    assert len(tracking.tracks) == 1 and len(tracking.tracks[0].points) == HORIZON
    assert sum(event["event_type"] == "ASSOCIATION_DIAGNOSTICS" for event in tracking.events) == 159
    assert sum(event["event_type"] == "CONTINUATION" for event in tracking.events) == 159
    passed.append("tracker_continuation_and_diagnostics")

    split_source = np.zeros(SHAPE, dtype=np.float64); split_source[3, 1:8] = 1.0
    split_target = np.zeros(SHAPE, dtype=np.float64)
    split_target[3, 1:4] = 1.0; split_target[3, 5:8] = 1.0
    split_frames = [detect(split_source, 0), detect(split_target, 1)] + [[] for _ in range(158)]
    split_tracking = track_components("SPLIT_SYNTH", split_frames)
    assert sum(event["event_type"] == "SPLIT" for event in split_tracking.events) == 1
    assert sorted(track.track_id for track in split_tracking.tracks) == [0, 1, 2]
    passed.append("tracker_split_id_allocation")

    merge_frames = [detect(split_target, 0), detect(split_source, 1)] + [[] for _ in range(158)]
    merge_tracking = track_components("MERGE_SYNTH", merge_frames)
    assert sum(event["event_type"] == "MERGE" for event in merge_tracking.events) == 1
    merge_event = next(event for event in merge_tracking.events if event["event_type"] == "MERGE")
    assert merge_event["source_track_ids"] == [0, 1] and merge_event["target_track_ids"] == [2]
    passed.append("tracker_merge_id_allocation")

    tie_matter = np.zeros(SHAPE, dtype=np.float64)
    tie_matter[1, 7:10] = 1.0; tie_matter[8, 1:4] = 1.0
    tie_components = detect(tie_matter, 0)
    tie_lookup = {(component.frame, component.index): component for component in tie_components}
    later_id_first = Track(9, [Point(0, 1)], fingerprint=fingerprint(tie_components[1]))
    earlier_support = Track(10, [Point(0, 0)], fingerprint=fingerprint(tie_components[0]))
    assert min((later_id_first, earlier_support), key=lambda track: track_sort_key(track, tie_lookup)) is earlier_support
    passed.append("co_primary_onset_support_tie_break")

    q = np.zeros(SHAPE, dtype=np.float64); q[4, 4:7] = 0.5
    zero_faces = np.zeros((2, *SHAPE), dtype=np.float64)
    q_next = advance_cohort(q, q.copy(), q.copy(), zero_faces, zero_faces)
    assert np.array_equal(q, q_next)
    passed.append("passive_cohort_identity")

    prefix_rows = _component_rows(112, turnover_at=79)
    summary = apply_prefix_flags(prefix_rows)
    assert summary["candidate"] and prefix_rows[110]["prefix_post_turnover_frames"] == 31
    assert not prefix_rows[110]["prefix_candidate"] and prefix_rows[111]["prefix_candidate"]
    passed.append("prefix_duration_exactness")

    active_only = _component_rows(100)
    turn_only = _component_rows(40, turnover_at=0)
    for row in turn_only:
        row["activity_per_mass"] = 0.0; row["energy_throughput_per_mass"] = 0.0
        row.update({"instantaneous_bounded_active": False, "prefix_persistent": False,
                    "prefix_active": False, "prefix_turnover": True,
                    "prefix_post_turnover_frames": row["frame"], "prefix_candidate": False})
    apply_prefix_flags(active_only)
    assert track_milestones(active_only)["pathway"] == "TURNOVER_FAILURE"
    assert track_milestones(turn_only)["pathway"] == "ACTIVATION_FAILURE"
    assert not any(track_milestones(rows)["pathway"] == "STABLE_CANDIDATE_EPISODE"
                   for rows in (active_only, turn_only))
    passed.append("multi_track_anti_stitching")

    no_episode = _component_rows(90, turnover_at=79)
    apply_prefix_flags(no_episode)
    assert consecutive_runs(no_episode, "prefix_candidate") == []
    assert track_milestones(no_episode)["pathway"] == "PERSISTENCE_FAILURE"
    passed.append("no_episode_null")

    terminal_rows = []
    for frame in range(128, 160):
        terminal_rows.append({"frame": frame, "activity_per_mass": 0.0,
                              "energy_throughput_per_mass": 0.0})
    terminal_track = Track(0, [Point(frame, 0) for frame in range(128, 160)], fingerprint="128:0,1,2")
    assert _terminal_state(terminal_track, terminal_rows, [])[0:2] == ("FROZEN", 128)
    gap_rows = terminal_rows[:15] + terminal_rows[16:]
    assert _terminal_state(terminal_track, gap_rows, [])[0] != "FROZEN"
    passed.append("freeze_terminal_gap_and_censoring")

    assert binary_summary(0, 0)["fraction"] is None
    assert continuous_summary([]) == {"n": 0, "median": None, "min": None, "max": None}
    assert exact_median([0.0]) == 0.0
    passed.append("zero_denominator_and_baseline")

    outcome_cases = [
        ((False, True, True, False, True, False), "AUDIT_INVALID"),
        ((True, True, True, True, True, False), "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES"),
        ((True, True, True, False, True, True), "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS"),
        ((True, False, True, False, True, False), "RAW_INSUFFICIENT"),
        ((True, True, True, False, True, False), "RAW_INSUFFICIENT"),
    ]
    for arguments, expected in outcome_cases:
        selected, truth = choose_outcome(*arguments)
        assert selected == expected and truth["selected"] == expected
        assert sum(value is True for key, value in truth.items() if key != "selected") == 1
    passed.append("all_outcome_truth_table_branches")

    empty_frames = [[] for _ in range(HORIZON)]
    assert classify_world(empty_frames, Tracking([], [], False), {}) == ("EMPTY_OR_GAS", [])
    unresolved_track = Track(0, [Point(0, 0)], True)
    regime, _ = classify_world(frames, Tracking([unresolved_track], [], True), {
        0: {"percolated_fraction": 1.0, "active": True, "candidate": True,
            "persistent": True, "maximum_turnover_fraction": 1.0}})
    assert regime == "TRACKING_UNRESOLVED"
    passed.append("taxonomy_precedence")

    fake_worlds = []
    for law_index in range(8):
        for ic in ("soup", "compact"):
            for replicate in range(4):
                fake_worlds.append({
                    "world_id": f"L{law_index:03d}__{ic}__r{replicate:02d}",
                    "law_id": f"L{law_index:03d}", "ic_id": ic, "replicate": replicate,
                    "first_component_frame": 0, "first_bounded_active_frame": None,
                    "first_persistence_qualification_frame": None, "first_turnover_frame": None,
                    "first_prefix_candidate_frame": None, "candidate_status_frames": 0,
                    "longest_candidate_episode_frames": 0,
                    "primary_developmental_pathway": "ACTIVATION_FAILURE",
                    "terminal_track_alive": False,
                })
    estimands = formation_maintenance(fake_worlds, [f"L{i:03d}" for i in range(8)])
    assert estimands["A_formation"]["all"]["denominator"] == 64
    assert all(row["denominator"] == 4 for row in estimands["A_formation"]["by_law_ic"])
    passed.append("aggregation_denominators")

    classified_fixture = []
    for row in fake_worlds:
        is_candidate = (row["law_id"] == "L000" and row["replicate"] < 2)
        classified_fixture.append({
            "world_id": row["world_id"], "law_id": row["law_id"], "ic_id": row["ic_id"],
            "replicate": row["replicate"],
            "regime": ("BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if is_candidate else "EMPTY_OR_GAS"),
            "candidate_track_ids": [0] if is_candidate else [],
        })
    reconstructed_fixture = reconstruct_classification(
        "f" * 64, classified_fixture, [f"L{i:03d}" for i in range(8)])
    assert set(reconstructed_fixture) == {
        "atlas", "candidate_regions", "disposition", "manifest_sha256", "schema", "worlds"}
    assert reconstructed_fixture["candidate_regions"] == ["L000"]
    assert reconstructed_fixture["disposition"] == "DEV_REGIME_CANDIDATE"
    assert len(reconstructed_fixture["atlas"]) == 8
    assert all(set(per_ic["counts"]) == set(REGIMES)
               for atlas_row in reconstructed_fixture["atlas"] for per_ic in atlas_row["per_ic"])
    assert all(per_ic["denominator"] == 4 and per_ic["complete"]
               for atlas_row in reconstructed_fixture["atlas"] for per_ic in atlas_row["per_ic"])
    passed.append("full_independent_classification_aggregation")

    group_fixture = {
        "reconstructed_regime": "EMPTY_OR_GAS", "primary_developmental_pathway": "FORMATION_FAILURE",
        "terminal_state": None, "first_component_frame": None,
        "first_bounded_active_frame": None, "first_persistence_qualification_frame": None,
        "first_turnover_frame": None, "first_prefix_candidate_frame": None,
        "candidate_status_frames": 0, "longest_candidate_episode_frames": 0,
        "terminal_track_alive": False, "right_censored": False,
    }
    complete_counts = group_summary({}, [group_fixture])
    assert (tuple(complete_counts["regime_counts"]) == REGIMES
            and tuple(complete_counts["pathway_counts"]) == PATHWAY_COUNT_KEYS
            and tuple(complete_counts["terminal_counts"]) == TERMINAL_COUNT_KEYS)
    assert complete_counts["regime_counts"]["EMPTY_OR_GAS"] == 1
    assert complete_counts["regime_counts"]["PERCOLATED"] == 0
    passed.append("trajectory_atlas_complete_zero_count_vocabularies")

    empty_development = develop_world(
        {"world_id": "L000__soup__r00", "law_id": "L000", "ic_id": "soup", "replicate": 0},
        "EMPTY_OR_GAS", (), "EMPTY_OR_GAS", (), [[] for _ in range(HORIZON)],
        Tracking([], [], False), [])
    assert (empty_development["primary_developmental_pathway"] == "FORMATION_FAILURE"
            and empty_development["representative_track_fingerprint"] is None
            and empty_development["trajectory_class"] is None)
    passed.append("empty_world_null_trajectory_class")

    complete_window_rows = [{"frame": frame} for frame in range(41)]
    complete_windows = compact_precursor_windows(complete_window_rows, 40)
    assert (complete_windows["bond_available"]
            and complete_windows["heterogeneity_available"]
            and complete_windows["exchange_available"])
    first_window_gap = [row for row in complete_window_rows if row["frame"] != 10]
    gap_windows = compact_precursor_windows(first_window_gap, 40)
    assert (not gap_windows["bond_available"]
            and not gap_windows["heterogeneity_available"]
            and not gap_windows["exchange_available"])
    terminal_window_gap = [row for row in complete_window_rows if row["frame"] != 35]
    assert not compact_precursor_windows(terminal_window_gap, 40)["exchange_available"]
    sparse_rows = [{"frame": frame} for frame in range(0, 40, 2)]
    assert not compact_precursor_windows(sparse_rows, 40)["heterogeneity_available"]
    passed.append("compact_precursor_incomplete_and_gapped_windows")

    dissolution_support = [f"D{index:02d}" for index in range(9)]
    unqualified_high_support = ["H00", "H01"]
    destructive_sets = destructive_support_sets(dissolution_support, unqualified_high_support)
    support_laws = {world: f"L{index % 3:03d}" for index, world in enumerate(dissolution_support)}
    support_laws.update({"H00": "L003", "H01": "L004"})
    assert destructive_sets["support"] == dissolution_support
    assert len({support_laws[world] for world in destructive_sets["support"]}) == 3
    assert len({support_laws[world] for world in destructive_sets["support"]}) < 4
    both_sets = destructive_support_sets(dissolution_support,
                                         dissolution_support + ["H00", "H01"])
    assert both_sets["support"] == dissolution_support and len(both_sets["overlap"]) == 9
    passed.append("destructive_qualifying_subtype_law_span")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "safe.bin").write_bytes(b"safe")
        guard = ReadGuard(root, ["safe.bin"])
        assert guard.read("safe.bin") == b"safe"
        assert guard.read("SAFE.BIN") == b"safe"
        for forbidden in ("../safe.bin", str((root / "safe.bin").resolve())):
            try:
                guard.read(forbidden)
            except AuditError:
                pass
            else:
                raise AssertionError(f"forbidden path accepted: {forbidden}")
        link_tested = False
        link = root / "link.bin"
        try:
            os.symlink(root / "safe.bin", link)
            link_tested = True
            link_guard = ReadGuard(root, ["link.bin"])
            try:
                link_guard.read("link.bin")
            except AuditError:
                pass
            else:
                raise AssertionError("symlink/reparse path accepted")
        except OSError:
            # On Windows without symlink privilege, the code path remains the
            # same FILE_ATTRIBUTE_REPARSE_POINT check exercised in production.
            assert os.name == "nt"
        passed.append("path_casefold_dotdot_absolute_and_symlink" +
                      ("" if link_tested else "_platform_no_symlink_privilege"))

    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary).resolve()
        for relative in (PLAN_CONTROL_PATH, ALLOWLIST_CONTROL_PATH, PROTOCOL_CONTROL_PATH):
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(relative.encode("ascii"))
        control_guard = ReadGuard(repo, (
            PLAN_CONTROL_PATH, ALLOWLIST_CONTROL_PATH, PROTOCOL_CONTROL_PATH))
        exact_control_request(PLAN_CONTROL_PATH, PLAN_CONTROL_PATH)
        exact_control_request(ALLOWLIST_CONTROL_PATH, ALLOWLIST_CONTROL_PATH)
        assert control_guard.read(PROTOCOL_CONTROL_PATH) == PROTOCOL_CONTROL_PATH.encode("ascii")
        for requested in (
            PLAN_CONTROL_PATH.upper(), "../" + PLAN_CONTROL_PATH,
            str(repo / PLAN_CONTROL_PATH), "./" + PLAN_CONTROL_PATH,
            PLAN_CONTROL_PATH.replace("/", "\\"),
        ):
            try:
                exact_control_request(requested, PLAN_CONTROL_PATH)
            except AuditError:
                pass
            else:
                raise AssertionError(f"nonliteral control path accepted: {requested}")
    passed.append("exact_guarded_captured_control_paths")

    synthetic_world_ids = [f"L{index // 8:03d}__{'soup' if (index % 8) < 4 else 'compact'}__r{index % 4:02d}"
                           for index in range(64)]
    semantic_gate = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ROOT-v1",
        "top_keys": ["classification_bytes", "classification_sha256", "disposition",
                     "enrollment_bytes", "enrollment_sha256", "manifest_sha256",
                     "raw_schema_sha256", "schema", "shards", "world_count"],
        "shard_row_keys": ["shard_manifest_bytes", "shard_manifest_sha256", "status", "world_id"],
        "world_count": 64, "disposition": "DEV_FEASIBILITY_FAIL", "shard_status": "COMPLETE",
    }
    manifest_digest = "a" * 64; classification_digest = "b" * 64
    synthetic_root = {
        "classification_bytes": 1234, "classification_sha256": classification_digest,
        "disposition": "DEV_FEASIBILITY_FAIL", "enrollment_bytes": 5678,
        "enrollment_sha256": "c" * 64, "manifest_sha256": manifest_digest,
        "raw_schema_sha256": "d" * 64,
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ROOT-v1",
        "shards": [{"shard_manifest_bytes": 100 + index,
                    "shard_manifest_sha256": f"{index:064x}", "status": "COMPLETE",
                    "world_id": world_id}
                   for index, world_id in enumerate(synthetic_world_ids)],
        "world_count": 64,
    }
    validate_root_manifest(synthetic_root, semantic_gate, synthetic_world_ids,
                           manifest_digest, classification_digest, 1234)
    invalid_roots = []
    for path, value in (
        (("world_count",), 63), (("disposition",), "DEV_REGIME_CANDIDATE"),
        (("manifest_sha256",), "e" * 64), (("classification_bytes",), 1235),
        (("shards", 0, "status"), "FAILED"),
        (("shards", 0, "world_id"), "UNENROLLED"),
    ):
        candidate = json.loads(json.dumps(synthetic_root))
        if len(path) == 1:
            candidate[path[0]] = value
        else:
            candidate[path[0]][path[1]][path[2]] = value
        invalid_roots.append(candidate)
    extra_key_root = json.loads(json.dumps(synthetic_root)); extra_key_root["extra"] = True
    invalid_roots.append(extra_key_root)
    for candidate in invalid_roots:
        try:
            validate_root_manifest(candidate, semantic_gate, synthetic_world_ids,
                                   manifest_digest, classification_digest, 1234)
        except AuditError:
            pass
        else:
            raise AssertionError("invalid synthetic root manifest accepted")
    passed.append("root_manifest_semantic_gate_before_physics")

    original_layout = expected_layout
    tiny_layout = {"safe": (np.dtype("float64"), (2,))}
    globals()["expected_layout"] = lambda: tiny_layout
    try:
        safe_npz = _tiny_npz(tiny_layout)
        loaded = load_npz_bytes(safe_npz, "safe")
        assert np.array_equal(loaded["safe"], np.zeros(2, dtype=np.float64))
        malicious: list[tuple[str, bytes]] = []
        malicious.append(("duplicate", _replace_zip_member(safe_npz, "safe.npy", b"", True)))
        for label, name in (("nested", "nested/safe.npy"), ("traversal", "../safe.npy"),
                            ("extra", "extra.npy")):
            output = io.BytesIO()
            with zipfile.ZipFile(io.BytesIO(safe_npz), "r") as source, zipfile.ZipFile(output, "w") as target:
                for member in source.infolist():
                    target.writestr(member.filename, source.read(member.filename))
                target.writestr(name, _npy_bytes(np.zeros(1, dtype=np.float64)))
            malicious.append((label, output.getvalue()))
        malicious.append(("object", _replace_zip_member(
            safe_npz, "safe.npy", _npy_bytes(np.asarray([object(), object()], dtype=object)))))
        malicious.append(("structured", _replace_zip_member(
            safe_npz, "safe.npy", _npy_bytes(np.zeros(2, dtype=[("x", "f8")])))))
        for label, raw in malicious:
            try:
                load_npz_bytes(raw, label)
            except AuditError:
                pass
            else:
                raise AssertionError(f"malicious NPZ accepted: {label}")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shard = root / "shard.npz"
            shard.write_bytes(safe_npz)
            shard_guard = ReadGuard(root, ["shard.npz"])
            expected_size = len(safe_npz)
            expected_digest = sha256_bytes(safe_npz)
            expected_oid = git_blob_oid(safe_npz)
            authenticated_raw, authenticated_arrays = authenticated_npz(
                shard_guard, "shard.npz", expected_size, expected_digest, expected_oid, "safe")
            assert authenticated_raw == safe_npz and set(authenticated_arrays) == {"safe"}
            shard.write_bytes(b"substituted-after-preflight")
            original_loader = load_npz_bytes
            loader_calls: list[str] = []
            globals()["load_npz_bytes"] = lambda raw, label: loader_calls.append(label) or {}
            try:
                try:
                    authenticated_npz(shard_guard, "shard.npz", expected_size,
                                      expected_digest, expected_oid, "substituted")
                except AuditError:
                    pass
                else:
                    raise AssertionError("substituted shard reached loader")
                assert loader_calls == []
            finally:
                globals()["load_npz_bytes"] = original_loader
    finally:
        globals()["expected_layout"] = original_layout
    passed.append("safe_malicious_and_authenticated_byte_npz_gates")

    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary).resolve()
        planned = "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY/independent"
        (repo / "results" / "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY").mkdir(parents=True)
        accepted_root = exact_independent_output_root(repo, Path(planned), planned)
        assert accepted_root == repo / Path(planned)
        for rejected in (
            Path("results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-AUTOPSY/primary"),
            Path("results/interventional-individuality-00-stage-b-autopsy/independent"),
            accepted_root,
        ):
            try:
                exact_independent_output_root(repo, rejected, planned)
            except AuditError:
                pass
            else:
                raise AssertionError(f"unauthorized output root accepted: {rejected}")
        payloads = {name: canonical_bytes({"file": name}) for name in (
            "integrity.json", "recomputed_classification.json", "world_transitions.json",
            "track_observations.jsonl", "events.jsonl", "trajectory_atlas.json", "analysis.json",
        )}
        captured_plan = "1" * 64; captured_protocol = "2" * 64; captured_allowlist = "3" * 64
        publish(accepted_root, payloads, {
            "schema": COMPLETE_SCHEMA, "status": "COMPLETE", "accepted_parent": ACCEPTED_PARENT,
            "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
            "autopsy_outcome": "RAW_INSUFFICIENT", "plan_sha256": captured_plan,
            "protocol_sha256": captured_protocol, "allowlist_sha256": captured_allowlist,
        }, {"worlds": 0, "tracks": 0, "track_observations": 0,
            "events": 0, "candidate_worlds": 0})
        sealed = parse_json((accepted_root / "COMPLETE.json").read_bytes(), "synthetic COMPLETE",
                            canonical=True)
        assert (sealed["plan_sha256"], sealed["protocol_sha256"], sealed["allowlist_sha256"]) == (
            captured_plan, captured_protocol, captured_allowlist)
        try:
            publish(accepted_root, payloads, sealed, sealed["counts"])
        except AuditError:
            pass
        else:
            raise AssertionError("publication overwrote existing exact root")
    passed.append("exact_independent_root_captured_hash_and_no_overwrite_publication")

    assert runtime_gate()["pytest"] == "8.4.2"
    passed.append("runtime_pytest_verified")

    encoded = canonical_bytes({"z": -0.0, "a": 1})
    assert encoded == b'{"a":1,"z":0.0}\n'
    assert canonical_bytes(parse_json(encoded, "serialization", canonical=True)) == encoded
    signature = _signature_row(False, True, (), (), 0, 1, {}, "FINITE_HORIZON_CENSORING")
    assert signature["interpretation"] == (
        "OBSERVATIONAL_SIGNATURE_ONLY:FINITE_HORIZON_CENSORING; never causal and never changes "
        "DEV_FEASIBILITY_FAIL")
    passed.append("canonical_serialization")
    return {"status": "SELF_TESTS_PASSED", "count": len(passed), "tests": passed}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan")
    parser.add_argument("--allowlist")
    parser.add_argument("--output-root", type=Path)
    arguments = parser.parse_args(argv)
    try:
        if arguments.self_test:
            print(canonical_bytes(self_test()).decode("utf-8"), end="")
            return 0
        if arguments.plan is None or arguments.allowlist is None or arguments.output_root is None:
            parser.error("raw mode requires --plan, --allowlist and --output-root")
        run_raw(arguments.plan, arguments.allowlist, arguments.output_root)
        return 0
    except (AuditError, AssertionError) as exc:
        print(f"AUDIT_INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
