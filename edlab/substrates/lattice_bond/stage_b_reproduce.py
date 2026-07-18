"""Independent raw-only Stage-B reproduction.

This module intentionally imports no project code.  Its runtime inputs are the
sealed B1 manifest, enrolled shard identity/integrity manifests, and physics
NPZ files.  Outcome-bearing online files are rejected by path and never read.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
from typing import Any, Iterable, Mapping, Sequence
import zipfile

import numpy as np


RAW_SCHEMA_SHA256 = "ffa9be82bd4c3285e75e1ac46b63a0a794598e2169afcb6a2890c3834749fe01"
REPRODUCTION_SPEC_SHA256 = "9031a954881aba12dddf081e57850af9c1df92eded5a177b731b245246c6c7c2"
RAW_SCHEMA_ID = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-RAW-v1"
REPRODUCTION_SPEC_ID = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-REPRODUCTION-SPEC-v4"
MANIFEST_SCHEMA_ID = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-MANIFEST-v1"
SHARD_SCHEMA_ID = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-SHARD-v1"
OUTPUT_SCHEMA_ID = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-CLASSIFICATION-v1"
RESULT_NAMESPACE = "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV"
ATOL = 1e-12
RTOL = 1e-10

REGIMES = (
    "TRACKING_UNRESOLVED",
    "ACTIVE_UNBOUNDED",
    "PERCOLATED",
    "EMPTY_OR_GAS",
    "DISSOLVED",
    "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
    "PERSISTENT_NO_TURNOVER",
    "STATIC_CRYSTAL_OR_SHELL",
    "TURNOVER_WITHOUT_PERSISTENCE",
)

TERMINAL_STATUSES = {
    "COMPLETE",
    "NUMERICAL_INVALID",
    "INSTRUMENTATION_INVALID",
}

FORBIDDEN_BASENAMES = {
    "online.json",
    "classification.json",
    "root_manifest.json",
    "engine.py",
    "instrumentation.py",
    "stage_b.py",
}

REQUIRED_LEDGER_ARRAY_FIELDS = (
    "affinity",
    "matter_forward",
    "matter_reverse",
    "matter_natural",
    "matter_active",
    "matter_missing",
    "resource_permeability",
    "resource_natural",
    "resource_active",
    "resource_missing",
    "bond_cue",
    "bond_tension",
    "r_on",
    "r_off",
    "gross_formation",
    "gross_rupture",
    "gross_formation_work",
    "gross_rupture_release",
    "gross_weakening_release",
    "gross_dissolution_release",
    "maintenance_recycled_work",
    "formation_fuel",
    "rupture_heat",
    "weakening_heat",
    "dissolution_heat",
    "matter_missing_from_delta",
    "matter_missing_to_delta",
    "resource_missing_from_delta",
    "resource_missing_to_delta",
    "matter_scale",
    "resource_scale",
)

REQUIRED_LEDGER_SCALAR_FIELDS = (
    "initial_matter",
    "final_matter",
    "matter_residual",
    "initial_stored_energy",
    "final_stored_energy",
    "total_rupture_heat",
    "total_maintenance_recycled_work",
    "energy_residual",
    "controller_onset_energy_jump",
)


class ReproductionError(RuntimeError):
    """A binding firewall, integrity, numerical, or protocol failure."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:
        raise ReproductionError(f"output is not canonical-JSON serializable: {exc}") from exc
    return (text + "\n").encode("utf-8")


def _reject_json_constant(value: str) -> None:
    raise ReproductionError(f"non-finite JSON constant {value!r}")


def _read_json(path: Path, *, require_canonical: bool = True) -> dict[str, Any]:
    _assert_not_forbidden(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ReproductionError(f"cannot read {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"), parse_constant=_reject_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReproductionError(f"invalid UTF-8 JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReproductionError(f"JSON root must be an object: {path}")
    if require_canonical and raw != _canonical_bytes(value):
        raise ReproductionError(f"JSON file is not strict finite canonical JSON: {path}")
    return value


def _assert_not_forbidden(path: Path) -> None:
    lowered = {part.lower() for part in path.parts}
    if path.name.lower() in FORBIDDEN_BASENAMES:
        raise ReproductionError(f"forbidden input path: {path}")
    if "selected-world" in str(path).lower() or "picked-world" in str(path).lower():
        raise ReproductionError(f"selected-world input is forbidden: {path}")
    if "reports" in lowered or "report" in lowered or "atlas" in lowered:
        raise ReproductionError(f"report/atlas input is forbidden: {path}")


def _resolved_child(root: Path, relative: str, expected_name: str | None = None) -> Path:
    candidate_relative = Path(relative)
    if candidate_relative.is_absolute() or ".." in candidate_relative.parts:
        raise ReproductionError(f"unsafe relative path: {relative!r}")
    root_resolved = root.resolve(strict=True)
    unresolved_candidate = root_resolved / candidate_relative
    probe = root_resolved
    for part in candidate_relative.parts:
        probe = probe / part
        if probe.is_symlink():
            raise ReproductionError(f"symlinked input is forbidden: {probe}")
    candidate = unresolved_candidate.resolve(strict=True)
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ReproductionError(f"path escapes result root: {relative!r}") from exc
    if expected_name is not None and candidate.name != expected_name:
        raise ReproductionError(
            f"expected {expected_name!r}, got {candidate.name!r} at {relative!r}"
        )
    _assert_not_forbidden(candidate)
    return candidate


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReproductionError(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise ReproductionError(f"{label} must be an array")
    return value


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReproductionError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ReproductionError(f"{label} must be finite")
    return result


def _integer(value: Any, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReproductionError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ReproductionError(f"{label} must be >= {minimum}")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReproductionError(f"{label} must be a nonempty string")
    return value


def _hash_text(value: Any, label: str) -> str:
    result = _string(value, label)
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise ReproductionError(f"{label} must be lowercase SHA-256")
    return result


def _one_present(mapping: Mapping[str, Any], keys: Sequence[str], label: str) -> Any:
    present = [key for key in keys if key in mapping]
    if len(present) != 1:
        raise ReproductionError(
            f"{label} requires exactly one of {tuple(keys)!r}; found {present!r}"
        )
    return mapping[present[0]]


@dataclass(frozen=True)
class DetectorConfig:
    matter_threshold: float
    min_cells: int


@dataclass(frozen=True)
class TrackerConfig:
    dilation_radius: int
    max_centroid_displacement: float
    max_area_ratio: float
    unique_score_margin: float


@dataclass(frozen=True)
class Thresholds:
    min_persistence_frames: int
    max_area_fraction: float
    min_bounded_fraction: float
    min_activity_per_mass: float
    min_energy_throughput_per_mass: float
    min_turnover_fraction: float
    min_post_turnover_frames: int


@dataclass(frozen=True)
class WorldEnrollment:
    world_id: str
    law_id: str
    ic_id: str
    replicate: int


@dataclass(frozen=True)
class LawContract:
    law_id: str
    spec: Mapping[str, Any]
    dt: float


@dataclass(frozen=True)
class ManifestContract:
    source: Mapping[str, Any]
    sha256: str
    laws: tuple[LawContract, ...]
    horizon_steps: int
    shape: tuple[int, int]
    replicates_per_law_ic: int
    detector: DetectorConfig
    tracker: TrackerConfig
    thresholds: Thresholds
    regimes: tuple[str, ...]
    ic_order: tuple[str, ...]
    worlds: tuple[WorldEnrollment, ...]
    minimum_candidate_worlds_per_ic: int

    @property
    def law_order(self) -> tuple[str, ...]:
        return tuple(law.law_id for law in self.laws)

    def law(self, law_id: str) -> LawContract:
        for law in self.laws:
            if law.law_id == law_id:
                return law
        raise ReproductionError(f"undeclared law_id {law_id!r}")


def _extract_named_order(value: Any, label: str, id_keys: Sequence[str]) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        if "order" in value:
            value = value["order"]
        elif "laws" in value:
            value = value["laws"]
        elif "classes" in value:
            value = value["classes"]
    items = _sequence(value, label)
    result: list[str] = []
    for index, item in enumerate(items):
        if isinstance(item, str):
            name = _string(item, f"{label}[{index}]")
        else:
            entry = _mapping(item, f"{label}[{index}]")
            name = _string(_one_present(entry, id_keys, f"{label}[{index}] identifier"), label)
        if name in result:
            raise ReproductionError(f"duplicate identifier {name!r} in {label}")
        result.append(name)
    if not result:
        raise ReproductionError(f"{label} must not be empty")
    return tuple(result)


def load_manifest(path: Path, expected_sha256: str) -> ManifestContract:
    actual_hash = _sha256(path)
    if actual_hash != expected_sha256.lower():
        raise ReproductionError(
            f"sealed manifest SHA-256 mismatch: expected {expected_sha256.lower()}, got {actual_hash}"
        )
    raw = _read_json(path)
    if raw.get("schema") != MANIFEST_SCHEMA_ID:
        raise ReproductionError("unexpected Stage-B1 manifest schema")
    if raw.get("namespace") != RESULT_NAMESPACE:
        raise ReproductionError("unexpected Stage-B1 result namespace")
    seal = _string(
        raw.get("manifest_sha256_excluding_field"),
        "manifest.manifest_sha256_excluding_field",
    ).lower()
    if len(seal) != 64 or any(character not in "0123456789abcdef" for character in seal):
        raise ReproductionError("manifest internal seal is not lowercase SHA-256")
    seal_object = dict(raw)
    del seal_object["manifest_sha256_excluding_field"]
    computed_seal = hashlib.sha256(_canonical_bytes(seal_object)).hexdigest()
    if seal != computed_seal:
        raise ReproductionError("manifest internal excluding-field seal mismatch")

    source_hashes = _mapping(raw.get("source_sha256"), "manifest.source_sha256")
    raw_schema_hash = _string(
        source_hashes.get(
            "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json"
        ),
        "manifest source raw-schema hash",
    )
    reproduction_hash = _string(
        source_hashes.get(
            "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json"
        ),
        "manifest source reproduction-spec hash",
    )
    reproducer_hash = _hash_text(
        source_hashes.get("edlab/substrates/lattice_bond/stage_b_reproduce.py"),
        "manifest source independent-reproducer hash",
    )
    if raw_schema_hash != RAW_SCHEMA_SHA256:
        raise ReproductionError("manifest binds an unexpected raw-schema hash")
    if reproduction_hash != REPRODUCTION_SPEC_SHA256:
        raise ReproductionError("manifest binds an unexpected reproduction-spec hash")
    runtime_source = Path(__file__).resolve(strict=True)
    actual_reproducer_hash = _sha256(runtime_source)
    if reproducer_hash != actual_reproducer_hash:
        raise ReproductionError(
            "manifest independent-reproducer hash differs from the executable source bytes"
        )
    environment = _mapping(raw.get("environment"), "manifest.environment")
    expected_environment = {
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "byteorder": sys.byteorder,
    }
    if set(environment) != set(expected_environment) or dict(environment) != expected_environment:
        raise ReproductionError(
            "manifest environment differs from the executing Python/NumPy/platform/byteorder"
        )

    law_family = _mapping(raw.get("law_family"), "manifest.law_family")
    law_entries = _sequence(law_family.get("laws"), "manifest.law_family.laws")
    laws: list[LawContract] = []
    for index, item in enumerate(law_entries):
        law_entry = _mapping(item, f"manifest.law_family.laws[{index}]")
        if set(law_entry) != {"law_id", "spec"}:
            raise ReproductionError(f"law[{index}] must contain exactly law_id and spec")
        law_id = _string(law_entry.get("law_id"), f"law[{index}].law_id")
        spec = _mapping(law_entry.get("spec"), f"law[{index}].spec")
        if any(law.law_id == law_id for law in laws):
            raise ReproductionError(f"duplicate law_id {law_id!r}")
        dt = _finite_float(spec.get("dt"), f"law[{index}].spec.dt")
        if dt <= 0.0:
            raise ReproductionError(f"law {law_id!r} dt must be positive")
        laws.append(LawContract(law_id=law_id, spec=spec, dt=dt))
    if not laws:
        raise ReproductionError("manifest law family must not be empty")

    ic_entries = _sequence(raw.get("initial_conditions"), "manifest.initial_conditions")
    ic_ids: list[str] = []
    for index, item in enumerate(ic_entries):
        entry = _mapping(item, f"manifest.initial_conditions[{index}]")
        ic_id = _string(entry.get("ic_id"), f"initial_conditions[{index}].ic_id")
        if ic_id in ic_ids:
            raise ReproductionError(f"duplicate ic_id {ic_id!r}")
        ic_ids.append(ic_id)
    if not ic_ids:
        raise ReproductionError("manifest initial_conditions must not be empty")

    execution = _mapping(raw.get("execution"), "manifest.execution")
    shape_values = _sequence(execution.get("shape"), "manifest.execution.shape")
    if len(shape_values) != 2:
        raise ReproductionError("manifest.execution.shape must be [Y,X]")
    shape = (
        _integer(shape_values[0], "manifest.execution.shape[0]", 1),
        _integer(shape_values[1], "manifest.execution.shape[1]", 1),
    )
    horizon = _integer(
        execution.get("horizon_steps"), "manifest.execution.horizon_steps", 1
    )
    replicates = _integer(
        execution.get("replicates_per_law_ic"),
        "manifest.execution.replicates_per_law_ic",
        1,
    )
    expected_world_ids = [
        f"{law.law_id}__{ic_id}__r{replicate:02d}"
        for law in laws
        for ic_id in ic_ids
        for replicate in range(replicates)
    ]
    world_count = _integer(execution.get("world_count"), "manifest.execution.world_count", 1)
    if world_count != len(expected_world_ids):
        raise ReproductionError("manifest execution.world_count is inconsistent")
    world_ids = [
        _string(value, f"manifest.execution.world_ids[{index}]")
        for index, value in enumerate(
            _sequence(execution.get("world_ids"), "manifest.execution.world_ids")
        )
    ]
    if world_ids != expected_world_ids:
        raise ReproductionError("manifest world_ids are not exact law/IC/replicate enrollment order")
    worlds = tuple(
        WorldEnrollment(
            world_id=f"{law.law_id}__{ic_id}__r{replicate:02d}",
            law_id=law.law_id,
            ic_id=ic_id,
            replicate=replicate,
        )
        for law in laws
        for ic_id in ic_ids
        for replicate in range(replicates)
    )

    detector_raw = _mapping(raw.get("detector"), "manifest.detector")
    detector = DetectorConfig(
        matter_threshold=_finite_float(
            detector_raw.get("matter_threshold"), "manifest.detector.matter_threshold"
        ),
        min_cells=_integer(detector_raw.get("min_cells"), "manifest.detector.min_cells", 1),
    )

    tracker_raw = _mapping(raw.get("tracker"), "manifest.tracker")
    tracker = TrackerConfig(
        dilation_radius=_integer(
            tracker_raw.get("dilation_radius"), "manifest.tracker.dilation_radius", 0
        ),
        max_centroid_displacement=_finite_float(
            tracker_raw.get("max_centroid_displacement"),
            "manifest.tracker.max_centroid_displacement",
        ),
        max_area_ratio=_finite_float(
            tracker_raw.get("max_area_ratio"), "manifest.tracker.max_area_ratio"
        ),
        unique_score_margin=_finite_float(
            tracker_raw.get("unique_score_margin"), "manifest.tracker.unique_score_margin"
        ),
    )
    if tracker.max_centroid_displacement <= 0 or tracker.max_area_ratio < 1:
        raise ReproductionError("manifest tracker bounds are invalid")
    if tracker.unique_score_margin < 0:
        raise ReproductionError("manifest tracker margin must be nonnegative")

    classifier = _mapping(raw.get("classifier"), "manifest.classifier")
    classes = tuple(
        _string(value, f"manifest.classifier.classes[{index}]")
        for index, value in enumerate(
            _sequence(classifier.get("classes"), "manifest.classifier.classes")
        )
    )
    if len(classes) != 9 or set(classes) != set(REGIMES):
        raise ReproductionError("manifest classifier classes differ from frozen nine-class vocabulary")
    threshold_raw = _mapping(classifier.get("thresholds"), "manifest.classifier.thresholds")
    if set(threshold_raw) != {
        "min_persistence_frames",
        "max_area_fraction",
        "min_bounded_fraction",
        "min_activity_per_mass",
        "min_energy_throughput_per_mass",
        "min_turnover_fraction",
        "min_post_turnover_frames",
    }:
        raise ReproductionError("manifest classifier must contain exactly seven frozen thresholds")
    thresholds = Thresholds(
        min_persistence_frames=_integer(
            threshold_raw.get("min_persistence_frames"), "min_persistence_frames", 1
        ),
        max_area_fraction=_finite_float(
            threshold_raw.get("max_area_fraction"), "max_area_fraction"
        ),
        min_bounded_fraction=_finite_float(
            threshold_raw.get("min_bounded_fraction"), "min_bounded_fraction"
        ),
        min_activity_per_mass=_finite_float(
            threshold_raw.get("min_activity_per_mass"), "min_activity_per_mass"
        ),
        min_energy_throughput_per_mass=_finite_float(
            threshold_raw.get("min_energy_throughput_per_mass"),
            "min_energy_throughput_per_mass",
        ),
        min_turnover_fraction=_finite_float(
            threshold_raw.get("min_turnover_fraction"), "min_turnover_fraction"
        ),
        min_post_turnover_frames=_integer(
            threshold_raw.get("min_post_turnover_frames"), "min_post_turnover_frames", 0
        ),
    )
    for label, value in (
        ("max_area_fraction", thresholds.max_area_fraction),
        ("min_bounded_fraction", thresholds.min_bounded_fraction),
        ("min_turnover_fraction", thresholds.min_turnover_fraction),
    ):
        if not 0.0 <= value <= 1.0:
            raise ReproductionError(f"{label} must lie in [0,1]")

    region_rule = _mapping(raw.get("region_rule"), "manifest.region_rule")
    minimum_candidates = _integer(
        region_rule.get("minimum_candidate_worlds_per_ic"),
        "manifest.region_rule.minimum_candidate_worlds_per_ic",
        1,
    )
    return ManifestContract(
        source=raw,
        sha256=actual_hash,
        laws=tuple(laws),
        horizon_steps=horizon,
        shape=shape,
        replicates_per_law_ic=replicates,
        detector=detector,
        tracker=tracker,
        thresholds=thresholds,
        regimes=classes,
        ic_order=tuple(ic_ids),
        worlds=worlds,
        minimum_candidate_worlds_per_ic=minimum_candidates,
    )


@dataclass
class Component:
    index: int
    cells: tuple[tuple[int, int], ...]
    mask: np.ndarray
    area: int
    mass: float
    centroid: tuple[float, float]
    radius_gyration: float
    wraps_y: bool
    wraps_x: bool

    @property
    def percolates(self) -> bool:
        return self.wraps_y or self.wraps_x


def _neighbours(y: int, x: int, shape: tuple[int, int]) -> Iterable[tuple[int, int, int, int]]:
    height, width = shape
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        yield (y + dy) % height, (x + dx) % width, dy, dx


def detect_components(matter: np.ndarray, config: DetectorConfig) -> list[Component]:
    if matter.ndim != 2 or matter.dtype != np.dtype("float64"):
        raise ReproductionError("detector matter must be a float64 [Y,X] array")
    if not np.all(np.isfinite(matter)) or np.any(matter < 0.0):
        raise ReproductionError("detector matter must be finite and nonnegative")
    shape = (int(matter.shape[0]), int(matter.shape[1]))
    occupied = matter >= config.matter_threshold
    raw: list[tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], tuple[int, int]], bool, bool]] = []

    unseen = set(int(value) for value in np.flatnonzero(occupied.ravel(order="C")))
    while unseen:
        linear_index = min(unseen)
        root = divmod(linear_index, shape[1])
        stack: list[tuple[int, int]] = [root]
        lifts: dict[tuple[int, int], tuple[int, int]] = {root: root}
        cells: list[tuple[int, int]] = []
        cell_set: set[tuple[int, int]] = set()
        wraps_y = False
        wraps_x = False
        while stack:
            cell = stack.pop()
            if cell in cell_set:
                continue
            cell_set.add(cell)
            cells.append(cell)
            lift_y, lift_x = lifts[cell]
            for ny, nx, dy, dx in _neighbours(cell[0], cell[1], shape):
                if not occupied[ny, nx]:
                    continue
                proposed = (lift_y + dy, lift_x + dx)
                neighbour = (ny, nx)
                if neighbour in lifts:
                    prior = lifts[neighbour]
                    wraps_y = wraps_y or prior[0] != proposed[0]
                    wraps_x = wraps_x or prior[1] != proposed[1]
                    continue
                lifts[neighbour] = proposed
                stack.append(neighbour)
        unseen.difference_update(cell[0] * shape[1] + cell[1] for cell in cell_set)
        ordered_cells = tuple(sorted(cells))
        if len(ordered_cells) >= config.min_cells:
            raw.append((ordered_cells, lifts, wraps_y, wraps_x))

    raw.sort(key=lambda item: item[0][0][0] * shape[1] + item[0][0][1])
    components: list[Component] = []
    for index, (cells, lifts, wraps_y, wraps_x) in enumerate(raw):
        mask = np.zeros(shape, dtype=np.bool_)
        mask[tuple(zip(*cells))] = True
        masses = [float(matter[cell]) for cell in cells]
        mass = math.fsum(masses)
        lifted = [lifts[cell] for cell in cells]
        weights = np.asarray(masses, dtype=np.float64)
        lift_values = np.asarray(lifted, dtype=np.float64)
        if mass > 0.0:
            centroid_lift = np.sum(lift_values * weights[:, None], axis=0) / mass
            centroid_lift_y = float(centroid_lift[0])
            centroid_lift_x = float(centroid_lift[1])
            squared = np.sum((lift_values - centroid_lift) ** 2, axis=1)
            rg_squared = float(np.sum(weights * squared)) / mass
        else:
            centroid_lift = np.sum(lift_values, axis=0) / len(lifted)
            centroid_lift_y = float(centroid_lift[0])
            centroid_lift_x = float(centroid_lift[1])
            squared = np.sum((lift_values - centroid_lift) ** 2, axis=1)
            rg_squared = float(np.sum(squared)) / len(lifted)
        components.append(
            Component(
                index=index,
                cells=cells,
                mask=mask,
                area=len(cells),
                mass=mass,
                centroid=(centroid_lift_y % shape[0], centroid_lift_x % shape[1]),
                radius_gyration=math.sqrt(max(0.0, rg_squared)),
                wraps_y=wraps_y,
                wraps_x=wraps_x,
            )
        )
    return components


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    result = mask.copy()
    frontier = mask.copy()
    for _ in range(radius):
        frontier = (
            np.roll(frontier, 1, axis=0)
            | np.roll(frontier, -1, axis=0)
            | np.roll(frontier, 1, axis=1)
            | np.roll(frontier, -1, axis=1)
        )
        result |= frontier
    return result


def _iou(first: np.ndarray, second: np.ndarray) -> float:
    intersection = int(np.count_nonzero(first & second))
    union = int(np.count_nonzero(first | second))
    return 0.0 if union == 0 else intersection / union


def _minimum_periodic_delta(first: float, second: float, period: int) -> float:
    raw = second - first
    candidates = (raw, raw - period, raw + period)
    return min(candidates, key=lambda value: (abs(value), value))


@dataclass
class AssociationEdge:
    source: int
    target: int
    raw_iou: float
    dilated_iou: float
    centroid_distance: float
    area_ratio: float
    score: float
    qualified: bool
    qualification_reason: str
    selected: bool = False
    ambiguity_bearing: bool = False


def associate(
    sources: Sequence[Component],
    targets: Sequence[Component],
    shape: tuple[int, int],
    config: TrackerConfig,
) -> list[AssociationEdge]:
    edges: list[AssociationEdge] = []
    source_dilations = {source.index: _dilate(source.mask, config.dilation_radius) for source in sources}
    target_dilations = {target.index: _dilate(target.mask, config.dilation_radius) for target in targets}
    for source in sources:
        for target in targets:
            raw_iou = _iou(source.mask, target.mask)
            dilated_iou = _iou(source_dilations[source.index], target_dilations[target.index])
            dy = _minimum_periodic_delta(source.centroid[0], target.centroid[0], shape[0])
            dx = _minimum_periodic_delta(source.centroid[1], target.centroid[1], shape[1])
            distance = math.hypot(dy, dx)
            area_ratio = max(source.area, target.area) / min(source.area, target.area)
            score = (
                4.0 * raw_iou
                + 2.0 * dilated_iou
                + math.exp(-distance / config.max_centroid_displacement)
                + min(source.area, target.area) / max(source.area, target.area)
            )
            if area_ratio > config.max_area_ratio:
                qualified = False
                reason = "REJECT_AREA_RATIO"
            elif distance > config.max_centroid_displacement:
                qualified = False
                reason = "REJECT_CENTROID_DISTANCE"
            elif raw_iou == 0.0 and dilated_iou == 0.0:
                qualified = False
                reason = "REJECT_NO_GEOMETRIC_SUPPORT"
            else:
                qualified = True
                reason = "QUALIFIED_RAW_OVERLAP" if raw_iou > 0 else "QUALIFIED_DILATED_GEOMETRY"
            edges.append(
                AssociationEdge(
                    source=source.index,
                    target=target.index,
                    raw_iou=raw_iou,
                    dilated_iou=dilated_iou,
                    centroid_distance=distance,
                    area_ratio=area_ratio,
                    score=score,
                    qualified=qualified,
                    qualification_reason=reason,
                )
            )

    for edge in edges:
        if edge.qualified and edge.raw_iou > 0.0:
            edge.selected = True
    occupied_sources = {edge.source for edge in edges if edge.selected}
    occupied_targets = {edge.target for edge in edges if edge.selected}
    remaining = [
        edge
        for edge in edges
        if edge.qualified
        and not edge.selected
        and edge.source not in occupied_sources
        and edge.target not in occupied_targets
    ]

    by_source: dict[int, list[AssociationEdge]] = defaultdict(list)
    by_target: dict[int, list[AssociationEdge]] = defaultdict(list)
    for edge in remaining:
        by_source[edge.source].append(edge)
        by_target[edge.target].append(edge)
    for candidates in by_source.values():
        candidates.sort(key=lambda edge: (-edge.score, edge.target))
    for candidates in by_target.values():
        candidates.sort(key=lambda edge: (-edge.score, edge.source))

    def unique_top(candidates: Sequence[AssociationEdge]) -> AssociationEdge | None:
        if not candidates:
            return None
        if len(candidates) == 1 or candidates[0].score - candidates[1].score > config.unique_score_margin:
            return candidates[0]
        return None

    source_top = {key: unique_top(value) for key, value in by_source.items()}
    target_top = {key: unique_top(value) for key, value in by_target.items()}
    for edge in remaining:
        if source_top.get(edge.source) is edge and target_top.get(edge.target) is edge:
            edge.selected = True

    finally_selected_sources = {edge.source for edge in edges if edge.selected}
    finally_selected_targets = {edge.target for edge in edges if edge.selected}
    for edge in remaining:
        if (
            not edge.selected
            and edge.source not in finally_selected_sources
            and edge.target not in finally_selected_targets
        ):
            edge.ambiguity_bearing = True
    return edges


@dataclass(frozen=True)
class TrackPoint:
    frame: int
    component_index: int


@dataclass
class Track:
    track_id: int
    points: list[TrackPoint]
    unresolved: bool = False
    parent_ids: tuple[int, ...] = ()


@dataclass
class Tracking:
    tracks: list[Track]
    unresolved: bool
    events: list[dict[str, Any]]


def _transition_groups(
    edges: Sequence[AssociationEdge],
) -> list[tuple[list[int], list[int], list[AssociationEdge]]]:
    graph_edges = [edge for edge in edges if edge.selected or edge.ambiguity_bearing]
    source_nodes = sorted({edge.source for edge in graph_edges})
    source_to_edges: dict[int, list[AssociationEdge]] = defaultdict(list)
    target_to_edges: dict[int, list[AssociationEdge]] = defaultdict(list)
    for edge in graph_edges:
        source_to_edges[edge.source].append(edge)
        target_to_edges[edge.target].append(edge)
    visited_sources: set[int] = set()
    visited_targets: set[int] = set()
    groups: list[tuple[list[int], list[int], list[AssociationEdge]]] = []
    for initial_source in source_nodes:
        if initial_source in visited_sources:
            continue
        queue: deque[tuple[str, int]] = deque([("s", initial_source)])
        group_sources: set[int] = set()
        group_targets: set[int] = set()
        while queue:
            side, node = queue.popleft()
            if side == "s":
                if node in visited_sources:
                    continue
                visited_sources.add(node)
                group_sources.add(node)
                for edge in source_to_edges[node]:
                    queue.append(("t", edge.target))
            else:
                if node in visited_targets:
                    continue
                visited_targets.add(node)
                group_targets.add(node)
                for edge in target_to_edges[node]:
                    queue.append(("s", edge.source))
        selected_edges = [
            edge
            for edge in graph_edges
            if edge.source in group_sources and edge.target in group_targets
        ]
        groups.append((sorted(group_sources), sorted(group_targets), selected_edges))
    groups.sort(key=lambda group: (group[0][0] if group[0] else math.inf, tuple(group[1])))
    return groups


def _minimum_cell_manhattan(first: Component, second: Component, shape: tuple[int, int]) -> int:
    height, width = shape
    best = height + width
    for y1, x1 in first.cells:
        for y2, x2 in second.cells:
            dy_raw = abs(y1 - y2)
            dx_raw = abs(x1 - x2)
            best = min(best, min(dy_raw, height - dy_raw) + min(dx_raw, width - dx_raw))
    return best


def track_components(
    frames: Sequence[Sequence[Component]],
    shape: tuple[int, int],
    config: TrackerConfig,
) -> Tracking:
    if not frames:
        return Tracking(tracks=[], unresolved=False, events=[])
    transitions = [
        associate(frames[index], frames[index + 1], shape, config)
        for index in range(len(frames) - 1)
    ]
    collapse_nodes: set[tuple[int, int]] = set()
    for frame in range(1, len(frames) - 1):
        incoming = transitions[frame - 1]
        outgoing = transitions[frame]
        for component in frames[frame]:
            incoming_count = sum(
                edge.selected and edge.target == component.index for edge in incoming
            )
            outgoing_count = sum(
                edge.selected and edge.source == component.index for edge in outgoing
            )
            if incoming_count >= 2 and outgoing_count >= 2:
                collapse_nodes.add((frame, component.index))

    tracks: list[Track] = []
    assignment: dict[int, int] = {}
    next_track_id = 0
    for component in frames[0]:
        tracks.append(Track(track_id=next_track_id, points=[TrackPoint(0, component.index)]))
        assignment[component.index] = next_track_id
        next_track_id += 1
    events: list[dict[str, Any]] = []
    world_unresolved = False

    for transition_index, edges in enumerate(transitions):
        target_frame = transition_index + 1
        next_assignment: dict[int, int] = {}
        groups = _transition_groups(edges)
        graph_sources = {source for group in groups for source in group[0]}
        graph_targets = {target for group in groups for target in group[1]}
        for source, track_id in sorted(assignment.items()):
            if source not in graph_sources:
                events.append(
                    {"event": "DISSOLVE", "frame": target_frame, "track_ids": [track_id]}
                )
        for sources, targets, group_edges in groups:
            source_tracks = sorted(
                assignment[source] for source in sources if source in assignment
            )
            ambiguous = any(edge.ambiguity_bearing for edge in group_edges)
            ambiguous = ambiguous or any((transition_index, source) in collapse_nodes for source in sources)
            ambiguous = ambiguous or any((target_frame, target) in collapse_nodes for target in targets)
            if len(source_tracks) != len(sources):
                ambiguous = True

            if not ambiguous and len(sources) == 1 and len(targets) == 1:
                track_id = source_tracks[0]
                tracks[track_id].points.append(TrackPoint(target_frame, targets[0]))
                next_assignment[targets[0]] = track_id
            elif not ambiguous and len(sources) == 1 and len(targets) > 1:
                parent_id = source_tracks[0]
                child_ids: list[int] = []
                for target in targets:
                    child_id = next_track_id
                    next_track_id += 1
                    tracks.append(
                        Track(
                            track_id=child_id,
                            points=[TrackPoint(target_frame, target)],
                            parent_ids=(parent_id,),
                        )
                    )
                    next_assignment[target] = child_id
                    child_ids.append(child_id)
                events.append(
                    {
                        "event": "SPLIT",
                        "frame": target_frame,
                        "parent_track_ids": [parent_id],
                        "child_track_ids": child_ids,
                    }
                )
            elif not ambiguous and len(sources) > 1 and len(targets) == 1:
                merged_id = next_track_id
                next_track_id += 1
                tracks.append(
                    Track(
                        track_id=merged_id,
                        points=[TrackPoint(target_frame, targets[0])],
                        parent_ids=tuple(source_tracks),
                    )
                )
                next_assignment[targets[0]] = merged_id
                events.append(
                    {
                        "event": "MERGE",
                        "frame": target_frame,
                        "parent_track_ids": source_tracks,
                        "child_track_ids": [merged_id],
                    }
                )
            else:
                world_unresolved = True
                for track_id in source_tracks:
                    tracks[track_id].unresolved = True
                unresolved_ids: list[int] = []
                for target in targets:
                    track_id = next_track_id
                    next_track_id += 1
                    tracks.append(
                        Track(
                            track_id=track_id,
                            points=[TrackPoint(target_frame, target)],
                            unresolved=True,
                            parent_ids=tuple(source_tracks),
                        )
                    )
                    next_assignment[target] = track_id
                    unresolved_ids.append(track_id)
                events.append(
                    {
                        "event": "TRACKING_UNRESOLVED",
                        "frame": target_frame,
                        "source_track_ids": source_tracks,
                        "target_track_ids": unresolved_ids,
                    }
                )

        for target in sorted(component.index for component in frames[target_frame]):
            if target not in graph_targets:
                track_id = next_track_id
                next_track_id += 1
                tracks.append(Track(track_id=track_id, points=[TrackPoint(target_frame, target)]))
                next_assignment[target] = track_id
                events.append(
                    {"event": "APPEAR", "frame": target_frame, "track_ids": [track_id]}
                )

        resolved_targets = [
            target
            for target, track_id in sorted(next_assignment.items())
            if not tracks[track_id].unresolved
        ]
        target_components = {component.index: component for component in frames[target_frame]}
        for left_index, left_target in enumerate(resolved_targets):
            for right_target in resolved_targets[left_index + 1 :]:
                if _minimum_cell_manhattan(
                    target_components[left_target], target_components[right_target], shape
                ) == 2:
                    events.append(
                        {
                            "event": "TEMPORARY_CONTACT",
                            "frame": target_frame,
                            "track_ids": sorted(
                                [next_assignment[left_target], next_assignment[right_target]]
                            ),
                        }
                    )
        assignment = next_assignment

    tracks.sort(key=lambda track: track.track_id)
    return Tracking(tracks=tracks, unresolved=world_unresolved, events=events)


@dataclass
class Physics:
    arrays: dict[str, np.ndarray]
    shape: tuple[int, int]
    horizon: int


def _extract_physics_integrity(shard: Mapping[str, Any]) -> Mapping[str, Any]:
    files = _mapping(shard.get("files"), "shard_manifest.files")
    physics = files.get("physics.npz")
    if physics is None:
        raise ReproductionError("shard manifest does not bind physics.npz")
    return _mapping(physics, "shard_manifest.files.physics.npz")


def _verify_array_inventory(
    arrays: Mapping[str, np.ndarray], inventory_value: Any
) -> None:
    expected = _mapping(inventory_value, "shard_manifest.physics_inventory")
    if set(expected) != set(arrays):
        raise ReproductionError(
            f"NPZ array inventory mismatch: missing={sorted(set(expected)-set(arrays))}, "
            f"extra={sorted(set(arrays)-set(expected))}"
        )
    for name, array in arrays.items():
        entry = _mapping(expected[name], f"physics_inventory.{name}")
        if set(entry) != {"shape", "dtype"}:
            raise ReproductionError(f"physics inventory entry {name!r} has extra/missing keys")
        shape = tuple(_integer(value, f"{name}.shape", 0) for value in _sequence(entry.get("shape"), f"{name}.shape"))
        dtype = _string(entry.get("dtype"), f"{name}.dtype")
        if array.shape != shape or array.dtype.str != dtype and array.dtype.name != dtype:
            raise ReproductionError(
                f"array metadata mismatch for {name}: got shape={array.shape}, dtype={array.dtype.str}; "
                f"expected shape={shape}, dtype={dtype}"
            )


def load_physics(
    path: Path,
    integrity: Mapping[str, Any],
    inventory: Mapping[str, Any],
    manifest: ManifestContract,
    law: LawContract,
) -> Physics:
    if set(integrity) != {"sha256", "bytes"}:
        raise ReproductionError("physics.npz file entry must contain exactly sha256 and bytes")
    expected_hash = _hash_text(integrity.get("sha256"), "physics.npz.sha256")
    expected_bytes = _integer(integrity.get("bytes"), "physics.npz.bytes", 1)
    if path.stat().st_size != expected_bytes:
        raise ReproductionError(f"physics.npz byte-count mismatch at {path}")
    actual_hash = _sha256(path)
    if actual_hash != expected_hash:
        raise ReproductionError(f"physics.npz SHA-256 mismatch at {path}")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.namelist()
            if len(members) != len(set(members)):
                raise ReproductionError(f"duplicate ZIP member in {path}")
            for member in members:
                member_path = Path(member)
                if member_path.is_absolute() or ".." in member_path.parts or member_path.suffix != ".npy":
                    raise ReproductionError(f"unsafe NPZ member {member!r} in {path}")
        with np.load(path, allow_pickle=False) as loaded:
            arrays = {name: np.array(loaded[name], copy=True) for name in loaded.files}
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise ReproductionError(f"invalid physics NPZ {path}: {exc}") from exc
    _verify_array_inventory(arrays, inventory)

    required = {
        "state_step",
        "state_m",
        "state_n",
        "state_b",
        "vector_reference_max_error",
        "deterministic_replay_equal",
    }
    required.update(f"ledger__{name}" for name in REQUIRED_LEDGER_ARRAY_FIELDS)
    required.update(f"ledger__{name}" for name in REQUIRED_LEDGER_SCALAR_FIELDS)
    missing = required - set(arrays)
    if missing:
        raise ReproductionError(f"physics NPZ missing required arrays: {sorted(missing)}")
    if set(arrays) != required:
        raise ReproductionError(f"physics NPZ has unexpected arrays: {sorted(set(arrays)-required)}")

    horizon = manifest.horizon_steps
    state_m = arrays["state_m"]
    state_n = arrays["state_n"]
    state_b = arrays["state_b"]
    state_step = arrays["state_step"]
    if state_m.dtype != np.dtype("float64") or state_m.ndim != 3:
        raise ReproductionError("state_m must be float64 [H+1,Y,X]")
    shape = (int(state_m.shape[1]), int(state_m.shape[2]))
    if shape != manifest.shape:
        raise ReproductionError("physics lattice shape differs from manifest execution.shape")
    if state_m.shape != (horizon + 1, *shape):
        raise ReproductionError("state_m horizon mismatch")
    if state_n.dtype != np.dtype("float64") or state_n.shape != state_m.shape:
        raise ReproductionError("state_n must match state_m as float64")
    if state_b.dtype != np.dtype("float64") or state_b.shape != (horizon + 1, 2, *shape):
        raise ReproductionError("state_b must be float64 [H+1,2,Y,X]")
    if state_step.dtype != np.dtype("int64") or state_step.shape != (horizon + 1,):
        raise ReproductionError("state_step must be int64 [H+1]")
    if not np.array_equal(state_step, np.arange(horizon + 1, dtype=np.int64)):
        raise ReproductionError("state_step must be exactly 0..H")
    for name in ("state_m", "state_n", "state_b"):
        if not np.all(np.isfinite(arrays[name])) or np.any(arrays[name] < 0.0):
            raise ReproductionError(f"{name} must be finite and nonnegative")
    matter_bound = _finite_float(law.spec.get("m_max"), f"law {law.law_id}.m_max")
    resource_bound = _finite_float(law.spec.get("n_max"), f"law {law.law_id}.n_max")
    if np.any(state_m > matter_bound + (ATOL + RTOL * max(1.0, matter_bound))):
        raise ReproductionError("state_m exceeds law matter bound")
    if np.any(state_n > resource_bound + (ATOL + RTOL * max(1.0, resource_bound))):
        raise ReproductionError("state_n exceeds law resource bound")
    if np.any(state_b > 1.0 + ATOL + RTOL):
        raise ReproductionError("state_b exceeds unit bond bound")

    face_shape = (horizon, 2, *shape)
    scalar_shape = (horizon,)
    for name in REQUIRED_LEDGER_ARRAY_FIELDS:
        array = arrays[f"ledger__{name}"]
        expected_shape = (horizon, *shape) if name == "affinity" else face_shape
        if array.dtype != np.dtype("float64") or array.shape != expected_shape:
            raise ReproductionError(f"ledger__{name} must be float64 {expected_shape}")
        if not np.all(np.isfinite(array)):
            raise ReproductionError(f"ledger__{name} contains non-finite values")
    for name in (
        "matter_forward",
        "matter_reverse",
        "gross_formation_work",
        "gross_rupture_release",
    ):
        if arrays[f"ledger__{name}"].shape != face_shape:
            raise ReproductionError(f"ledger__{name} must have face shape {face_shape}")
    for name in REQUIRED_LEDGER_SCALAR_FIELDS:
        array = arrays[f"ledger__{name}"]
        if array.dtype != np.dtype("float64") or array.shape != scalar_shape:
            raise ReproductionError(f"ledger__{name} must be float64 {scalar_shape}")
        if not np.all(np.isfinite(array)):
            raise ReproductionError(f"ledger__{name} contains non-finite values")
    if arrays["vector_reference_max_error"].dtype != np.dtype("float64") or arrays[
        "vector_reference_max_error"
    ].shape != scalar_shape:
        raise ReproductionError("vector_reference_max_error must be float64 [H]")
    if arrays["deterministic_replay_equal"].dtype != np.dtype("uint8") or arrays[
        "deterministic_replay_equal"
    ].shape != scalar_shape:
        raise ReproductionError("deterministic_replay_equal must be uint8 [H]")

    _validate_physics_identities(arrays, manifest, law)
    return Physics(arrays=arrays, shape=shape, horizon=horizon)


def _tolerance(reference: np.ndarray | float) -> np.ndarray | float:
    return ATOL + RTOL * np.abs(reference)


def _assert_close(
    actual: np.ndarray,
    expected: np.ndarray,
    label: str,
) -> None:
    if actual.shape != expected.shape:
        raise ReproductionError(f"{label} shape mismatch")
    error = np.abs(actual - expected)
    allowed = _tolerance(expected)
    if not bool(np.all(error <= allowed)):
        maximum = float(np.max(error - allowed))
        raise ReproductionError(f"{label} exceeds frozen operation tolerance by {maximum:.17g}")


def _divergence(face_flux: np.ndarray) -> np.ndarray:
    term0 = face_flux[0] - np.roll(face_flux[0], 1, axis=0)
    term1 = face_flux[1] - np.roll(face_flux[1], 1, axis=1)
    return term0 + term1


def _validate_physics_identities(
    arrays: Mapping[str, np.ndarray], manifest: ManifestContract, law: LawContract
) -> None:
    if not np.all(arrays["deterministic_replay_equal"] == np.uint8(1)):
        raise ReproductionError("deterministic replay identity failed")
    reference_error = arrays["vector_reference_max_error"]
    raw_scale = 1.0
    scale_names = ["state_m", "state_n", "state_b"]
    scale_names.extend(f"ledger__{name}" for name in REQUIRED_LEDGER_ARRAY_FIELDS)
    scale_names.extend(f"ledger__{name}" for name in REQUIRED_LEDGER_SCALAR_FIELDS)
    for name in scale_names:
        raw_scale = max(raw_scale, float(np.max(np.abs(arrays[name]))))
    reference_limit = ATOL + RTOL * raw_scale
    if not np.all(np.isfinite(reference_error)) or np.any(reference_error < 0.0):
        raise ReproductionError("vector-reference errors must be finite and nonnegative")
    if np.any(reference_error > reference_limit):
        raise ReproductionError("vector-reference error exceeds manifest frozen limit")

    for flow_name in (
        "matter_forward",
        "matter_reverse",
        "gross_formation",
        "gross_rupture",
        "gross_formation_work",
        "gross_rupture_release",
    ):
        if np.any(arrays[f"ledger__{flow_name}"] < 0.0):
            raise ReproductionError(f"ledger__{flow_name} must be nonnegative")

    matter_forward = arrays["ledger__matter_forward"]
    matter_reverse = arrays["ledger__matter_reverse"]
    for field_name in (
        "matter_missing",
        "resource_missing",
        "matter_missing_from_delta",
        "matter_missing_to_delta",
        "resource_missing_from_delta",
        "resource_missing_to_delta",
    ):
        if not np.array_equal(arrays[f"ledger__{field_name}"], np.zeros_like(arrays[f"ledger__{field_name}"])):
            raise ReproductionError(f"ledger__{field_name} is non-neutral")
    for field_name in ("matter_scale", "resource_scale"):
        if not np.array_equal(arrays[f"ledger__{field_name}"], np.ones_like(arrays[f"ledger__{field_name}"])):
            raise ReproductionError(f"ledger__{field_name} is non-neutral")
    if not np.array_equal(
        arrays["ledger__controller_onset_energy_jump"],
        np.zeros_like(arrays["ledger__controller_onset_energy_jump"]),
    ):
        raise ReproductionError("controller_onset_energy_jump is nonzero")
    for frame in range(manifest.horizon_steps):
        expected_matter = arrays["state_m"][frame] - law.dt * _divergence(
            matter_forward[frame] - matter_reverse[frame]
        )
        _assert_close(
            arrays["state_m"][frame + 1],
            expected_matter,
            f"matter face-balance at frame {frame}",
        )
        initial_matter = math.fsum(float(value) for value in arrays["state_m"][frame].flat)
        final_matter = math.fsum(float(value) for value in arrays["state_m"][frame + 1].flat)
        for field_name, expected_scalar in (
            ("initial_matter", initial_matter),
            ("final_matter", final_matter),
        ):
            actual = float(arrays[f"ledger__{field_name}"][frame])
            if abs(actual - expected_scalar) > float(_tolerance(expected_scalar)):
                raise ReproductionError(f"ledger {field_name} mismatch at frame {frame}")
        residual = float(arrays["ledger__matter_residual"][frame])
        if abs(residual) > float(_tolerance(final_matter)):
            raise ReproductionError(f"matter residual exceeds tolerance at frame {frame}")
        energy_residual = float(arrays["ledger__energy_residual"][frame])
        energy_reference = float(arrays["ledger__initial_stored_energy"][frame])
        if abs(energy_residual) > float(_tolerance(energy_reference)):
            raise ReproductionError(f"energy residual exceeds tolerance at frame {frame}")


@dataclass(frozen=True)
class Observation:
    track_id: int
    frame: int
    component_index: int
    area_fraction: float
    percolated: bool
    activity_per_mass: float
    energy_throughput_per_mass: float
    turnover_fraction: float


@dataclass
class TrackMetric:
    track_id: int
    unresolved: bool
    observed_frames: int
    span_frames: int
    maximum_area_fraction: float
    bounded_fraction: float
    percolated_fraction: float
    mean_activity_per_mass: float
    mean_energy_throughput_per_mass: float
    maximum_turnover_fraction: float
    post_turnover_frames: int


def _advance_cohort(
    cohort: np.ndarray,
    matter: np.ndarray,
    next_matter: np.ndarray,
    forward: np.ndarray,
    reverse: np.ndarray,
    dt: float,
    frame: int,
) -> np.ndarray:
    if not math.isfinite(dt) or dt <= 0.0:
        raise ReproductionError(f"cohort dt must be finite and positive at frame {frame}")
    if cohort.shape != matter.shape or next_matter.shape != matter.shape:
        raise ReproductionError(f"cohort/matter shape mismatch at frame {frame}")
    if matter.ndim != 2 or forward.shape != (2, *matter.shape) or reverse.shape != forward.shape:
        raise ReproductionError(f"cohort face-flow shape mismatch at frame {frame}")
    for label, array in (("cohort", cohort), ("matter", matter), ("next_matter", next_matter)):
        if array.dtype != np.dtype("float64") or not np.all(np.isfinite(array)):
            raise ReproductionError(f"{label} invalid during cohort update at frame {frame}")
    if forward.dtype != np.dtype("float64") or reverse.dtype != np.dtype("float64"):
        raise ReproductionError("gross cohort flows must be float64")
    if not np.all(np.isfinite(forward)) or not np.all(np.isfinite(reverse)):
        raise ReproductionError("gross cohort flows must be finite")
    if np.any(forward < 0.0) or np.any(reverse < 0.0):
        raise ReproductionError("gross cohort flows must be nonnegative")
    if np.any(matter < 0.0) or np.any(next_matter < 0.0):
        raise ReproductionError("cohort matter states must be nonnegative")
    tolerance = ATOL + RTOL * max(
        1.0,
        float(np.max(np.abs(matter))),
        float(np.max(np.abs(next_matter))),
    )
    if float(np.min(cohort)) < -tolerance or float(np.max(cohort - matter)) > tolerance:
        raise ReproductionError(f"cohort leaves [0,m] before frame {frame}")
    expected_matter = matter - dt * _divergence(forward - reverse)
    if float(np.max(np.abs(next_matter - expected_matter))) > tolerance:
        raise ReproductionError(f"cohort matter identity failed at frame {frame}")
    fraction = np.divide(cohort, matter, out=np.zeros_like(cohort), where=matter > 0.0)
    flux = np.empty_like(forward)
    flux[0] = forward[0] * fraction - reverse[0] * np.roll(fraction, -1, axis=0)
    flux[1] = forward[1] * fraction - reverse[1] * np.roll(fraction, -1, axis=1)
    updated = cohort - dt * _divergence(flux)
    initial_total = math.fsum(float(value) for value in cohort.flat)
    final_total = math.fsum(float(value) for value in updated.flat)
    if abs(final_total - initial_total) > tolerance * cohort.size:
        raise ReproductionError(f"cohort global conservation failed at frame {frame}")
    if float(np.min(updated)) < -tolerance or float(np.max(updated - next_matter)) > tolerance:
        raise ReproductionError(f"cohort leaves [0,m] after frame {frame}")
    return updated


def observe_tracks(
    physics: Physics,
    components: Sequence[Sequence[Component]],
    tracking: Tracking,
    manifest: ManifestContract,
    law: LawContract,
) -> tuple[list[Observation], list[TrackMetric]]:
    arrays = physics.arrays
    component_lookup = {
        (frame, component.index): component
        for frame, frame_components in enumerate(components)
        for component in frame_components
    }
    observations: list[Observation] = []
    metrics: list[TrackMetric] = []
    for track in tracking.tracks:
        if not track.points:
            raise ReproductionError(f"track {track.track_id} has no points")
        points = sorted(track.points, key=lambda point: point.frame)
        if len({point.frame for point in points}) != len(points):
            raise ReproductionError(f"track {track.track_id} has duplicate frame observations")
        first_point = points[0]
        first_component = component_lookup.get((first_point.frame, first_point.component_index))
        if first_component is None:
            raise ReproductionError(f"track {track.track_id} has orphan first point")
        cohort = np.zeros(physics.shape, dtype=np.float64)
        cohort[first_component.mask] = arrays["state_m"][first_point.frame][first_component.mask]
        initial_cohort_mass = math.fsum(float(value) for value in cohort.flat)
        if initial_cohort_mass <= 0.0:
            raise ReproductionError(f"track {track.track_id} cohort mass is not positive")
        point_by_frame = {point.frame: point for point in points}
        track_observations: list[Observation] = []
        last_frame = points[-1].frame
        for frame in range(first_point.frame, last_frame + 1):
            point = point_by_frame.get(frame)
            if point is not None:
                component = component_lookup.get((frame, point.component_index))
                if component is None:
                    raise ReproductionError(f"track {track.track_id} has orphan component")
                retained = math.fsum(float(value) for value in cohort[component.mask])
                turnover = 1.0 - retained / initial_cohort_mass
                tolerance_fraction = ATOL + RTOL * initial_cohort_mass
                if turnover < -tolerance_fraction or turnover > 1.0 + tolerance_fraction:
                    raise ReproductionError(f"turnover outside [0,1] for track {track.track_id}")
                turnover = min(1.0, max(0.0, turnover))
                internal_faces = np.stack(
                    (
                        component.mask & np.roll(component.mask, -1, axis=0),
                        component.mask & np.roll(component.mask, -1, axis=1),
                    )
                )
                gross_flow = (
                    arrays["ledger__matter_forward"][frame]
                    + arrays["ledger__matter_reverse"][frame]
                )
                activity_sum = math.fsum(float(value) for value in gross_flow[internal_faces])
                activity_numerator = law.dt * activity_sum
                work = (
                    arrays["ledger__gross_formation_work"][frame]
                    + arrays["ledger__gross_rupture_release"][frame]
                )
                energy_numerator = math.fsum(float(value) for value in work[internal_faces])
                observation = Observation(
                    track_id=track.track_id,
                    frame=frame,
                    component_index=component.index,
                    area_fraction=component.area / (physics.shape[0] * physics.shape[1]),
                    percolated=component.percolates,
                    activity_per_mass=activity_numerator / (law.dt * component.mass),
                    energy_throughput_per_mass=(energy_numerator / law.dt) / component.mass,
                    turnover_fraction=turnover,
                )
                if not all(
                    math.isfinite(value)
                    for value in (
                        observation.area_fraction,
                        observation.activity_per_mass,
                        observation.energy_throughput_per_mass,
                        observation.turnover_fraction,
                    )
                ):
                    raise ReproductionError(f"non-finite observation for track {track.track_id}")
                observations.append(observation)
                track_observations.append(observation)
            if frame < last_frame:
                cohort = _advance_cohort(
                    cohort,
                    arrays["state_m"][frame],
                    arrays["state_m"][frame + 1],
                    arrays["ledger__matter_forward"][frame],
                    arrays["ledger__matter_reverse"][frame],
                    law.dt,
                    frame,
                )

        if len(track_observations) != len(points):
            raise ReproductionError(f"missing observation for track {track.track_id}")
        observed_frames = len(track_observations)
        span_frames = points[-1].frame - points[0].frame + 1
        first_turnover_frame = next(
            (
                observation.frame
                for observation in track_observations
                if observation.turnover_fraction >= manifest.thresholds.min_turnover_fraction
            ),
            None,
        )
        metrics.append(
            TrackMetric(
                track_id=track.track_id,
                unresolved=track.unresolved,
                observed_frames=observed_frames,
                span_frames=span_frames,
                maximum_area_fraction=max(obs.area_fraction for obs in track_observations),
                bounded_fraction=math.fsum(
                    1.0
                    for obs in track_observations
                    if not obs.percolated
                    and obs.area_fraction <= manifest.thresholds.max_area_fraction
                )
                / observed_frames,
                percolated_fraction=math.fsum(
                    1.0 for obs in track_observations if obs.percolated
                )
                / observed_frames,
                mean_activity_per_mass=math.fsum(
                    obs.activity_per_mass for obs in track_observations
                )
                / observed_frames,
                mean_energy_throughput_per_mass=math.fsum(
                    obs.energy_throughput_per_mass for obs in track_observations
                )
                / observed_frames,
                maximum_turnover_fraction=max(
                    obs.turnover_fraction for obs in track_observations
                ),
                post_turnover_frames=(
                    0
                    if first_turnover_frame is None
                    else sum(obs.frame > first_turnover_frame for obs in track_observations)
                ),
            )
        )
    if len(observations) != sum(len(track.points) for track in tracking.tracks):
        raise ReproductionError("world observation/track-point integrity failed")
    return observations, metrics


def _persistent(metric: TrackMetric, thresholds: Thresholds) -> bool:
    return (
        not metric.unresolved
        and metric.observed_frames >= thresholds.min_persistence_frames
        and metric.span_frames >= thresholds.min_persistence_frames
    )


def _active(metric: TrackMetric, thresholds: Thresholds) -> bool:
    return (
        metric.mean_activity_per_mass >= thresholds.min_activity_per_mass
        and metric.mean_energy_throughput_per_mass >= thresholds.min_energy_throughput_per_mass
    )


def _candidate(metric: TrackMetric, thresholds: Thresholds) -> bool:
    return (
        _persistent(metric, thresholds)
        and metric.maximum_area_fraction <= thresholds.max_area_fraction
        and metric.bounded_fraction >= thresholds.min_bounded_fraction
        and metric.percolated_fraction == 0.0
        and _active(metric, thresholds)
        and metric.maximum_turnover_fraction >= thresholds.min_turnover_fraction
        and metric.post_turnover_frames >= thresholds.min_post_turnover_frames
    )


def classify_world(
    components: Sequence[Sequence[Component]],
    tracking: Tracking,
    metrics: Sequence[TrackMetric],
    thresholds: Thresholds,
) -> str:
    if tracking.unresolved or any(metric.unresolved for metric in metrics):
        return "TRACKING_UNRESOLVED"
    if any(metric.percolated_fraction > 0.0 and _active(metric, thresholds) for metric in metrics):
        return "ACTIVE_UNBOUNDED"
    if any(component.percolates for frame in components for component in frame):
        return "PERCOLATED"
    if not any(components):
        return "EMPTY_OR_GAS"
    if len(components[-1]) == 0:
        return "DISSOLVED"
    if any(_candidate(metric, thresholds) for metric in metrics):
        return "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    persistent = [metric for metric in metrics if _persistent(metric, thresholds)]
    if (
        any(_active(metric, thresholds) for metric in persistent)
        and not any(
            metric.maximum_turnover_fraction >= thresholds.min_turnover_fraction
            for metric in persistent
        )
    ):
        return "PERSISTENT_NO_TURNOVER"
    if persistent:
        return "STATIC_CRYSTAL_OR_SHELL"
    if any(
        not _persistent(metric, thresholds)
        and metric.maximum_turnover_fraction >= thresholds.min_turnover_fraction
        for metric in metrics
    ):
        return "TURNOVER_WITHOUT_PERSISTENCE"
    return "DISSOLVED"


def _component_payload(component: Component) -> dict[str, Any]:
    return {
        "area": component.area,
        "centroid": [component.centroid[0], component.centroid[1]],
        "component_index": component.index,
        "mass": component.mass,
        "percolates": component.percolates,
        "radius_gyration": component.radius_gyration,
        "wraps_x": component.wraps_x,
        "wraps_y": component.wraps_y,
    }


def _track_metric_payload(metric: TrackMetric) -> dict[str, Any]:
    return {
        "bounded_fraction": metric.bounded_fraction,
        "maximum_area_fraction": metric.maximum_area_fraction,
        "maximum_turnover_fraction": metric.maximum_turnover_fraction,
        "mean_activity_per_mass": metric.mean_activity_per_mass,
        "mean_energy_throughput_per_mass": metric.mean_energy_throughput_per_mass,
        "observed_frames": metric.observed_frames,
        "percolated_fraction": metric.percolated_fraction,
        "post_turnover_frames": metric.post_turnover_frames,
        "span_frames": metric.span_frames,
        "track_id": metric.track_id,
        "unresolved": metric.unresolved,
    }


def reproduce_complete_world(
    physics: Physics,
    manifest: ManifestContract,
    law: LawContract,
) -> dict[str, Any]:
    components = [
        detect_components(physics.arrays["state_m"][frame], manifest.detector)
        for frame in range(manifest.horizon_steps)
    ]
    tracking = track_components(components, physics.shape, manifest.tracker)
    _observations, metrics = observe_tracks(physics, components, tracking, manifest, law)
    regime = classify_world(components, tracking, metrics, manifest.thresholds)
    if regime not in REGIMES:
        raise ReproductionError(f"classifier emitted unknown regime {regime!r}")
    candidate_track_ids = sorted(
        metric.track_id for metric in metrics if _candidate(metric, manifest.thresholds)
    )
    if regime != "BOUNDED_ACTIVE_TURNOVER_CANDIDATE":
        candidate_track_ids = []
    return {"candidate_track_ids": candidate_track_ids, "regime": regime}


def _verify_shard_identity(
    shard: Mapping[str, Any], enrollment: WorldEnrollment
) -> str:
    if shard.get("schema") != SHARD_SCHEMA_ID:
        raise ReproductionError(f"unexpected shard schema for {enrollment.world_id!r}")
    world = _mapping(shard.get("world"), "shard_manifest.world")
    if set(world) != {"world_id", "law_id", "ic_id", "replicate"}:
        raise ReproductionError(f"shard world identity keys mismatch for {enrollment.world_id!r}")
    world_id = _string(world.get("world_id"), "shard_manifest.world.world_id")
    law_id = _string(world.get("law_id"), "shard_manifest.world.law_id")
    ic_id = _string(world.get("ic_id"), "shard_manifest.world.ic_id")
    replicate = _integer(world.get("replicate"), "shard_manifest.world.replicate", 0)
    status = _string(shard.get("status"), "shard_manifest.status")
    if (
        world_id != enrollment.world_id
        or law_id != enrollment.law_id
        or ic_id != enrollment.ic_id
        or replicate != enrollment.replicate
    ):
        raise ReproductionError(f"shard identity mismatch for {enrollment.world_id!r}")
    if status not in TERMINAL_STATUSES:
        raise ReproductionError(f"invalid shard status {status!r} for {world_id!r}")
    return status


def _find_physics_path(shard_dir: Path, integrity: Mapping[str, Any]) -> Path:
    return _resolved_child(shard_dir, "physics.npz", expected_name="physics.npz")


def _verify_result_root_entries(result_root: Path, world_ids: Sequence[str]) -> None:
    actual_dirs: list[str] = []
    actual_files: list[str] = []
    for entry in result_root.iterdir():
        if entry.is_symlink():
            raise ReproductionError(f"symlinked result-root entry is forbidden: {entry}")
        if entry.is_dir():
            actual_dirs.append(entry.name)
        elif entry.is_file():
            actual_files.append(entry.name)
        else:
            raise ReproductionError(f"unsupported result-root entry: {entry}")
    if sorted(actual_dirs) != sorted(world_ids):
        raise ReproductionError(
            f"result-root shard directory set mismatch: got={sorted(actual_dirs)!r}"
        )
    expected_root_files = {"enrollment.json", "classification.json", "root_manifest.json"}
    if set(actual_files) != expected_root_files:
        raise ReproductionError(
            f"result-root file set mismatch: got={sorted(actual_files)!r}"
        )


def _verify_shard_file_set(shard_dir: Path, expected: set[str]) -> None:
    entries = set()
    for entry in shard_dir.iterdir():
        if entry.is_symlink() or not entry.is_file():
            raise ReproductionError(f"invalid shard directory entry: {entry}")
        entries.add(entry.name)
    if entries != expected:
        raise ReproductionError(
            f"shard file set mismatch at {shard_dir}: got={sorted(entries)!r}, expected={sorted(expected)!r}"
        )


def _validate_row_counts(row_counts: Any, manifest: ManifestContract) -> None:
    required = {
        "state_rows",
        "ledger_rows",
        "component_rows",
        "association_edge_rows",
        "event_rows",
        "track_observation_rows",
        "tracer_rows",
    }
    rows = _mapping(row_counts, "shard_manifest.row_counts")
    if set(rows) != required:
        raise ReproductionError("shard row_counts keyset mismatch")
    parsed = {key: _integer(value, f"row_counts.{key}", 0) for key, value in rows.items()}
    if parsed["state_rows"] != manifest.horizon_steps + 1:
        raise ReproductionError("shard state_rows mismatch")
    if parsed["ledger_rows"] != manifest.horizon_steps:
        raise ReproductionError("shard ledger_rows mismatch")


def build_classification(
    manifest: ManifestContract, world_results: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    exact_world_keys = {
        "world_id",
        "law_id",
        "ic_id",
        "replicate",
        "status",
        "regime",
        "candidate_track_ids",
    }
    normalized_worlds = [dict(world) for world in world_results]
    if len(normalized_worlds) != len(manifest.worlds):
        raise ReproductionError("classification world count differs from enrollment")
    expected_ids = sorted(world.world_id for world in manifest.worlds)
    actual_ids = [world.get("world_id") for world in normalized_worlds]
    if actual_ids != expected_ids:
        raise ReproductionError("classification worlds are not complete lexicographic enrollment")
    for world in normalized_worlds:
        if set(world) != exact_world_keys:
            raise ReproductionError(f"world classification keyset mismatch for {world.get('world_id')!r}")
        if world["status"] not in TERMINAL_STATUSES or world["regime"] not in REGIMES:
            raise ReproductionError(f"invalid world status/regime for {world['world_id']!r}")
        candidate_ids = world["candidate_track_ids"]
        if world["regime"] != "BOUNDED_ACTIVE_TURNOVER_CANDIDATE":
            candidate_ids = []
            world["candidate_track_ids"] = candidate_ids
        if (
            not isinstance(candidate_ids, list)
            or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in candidate_ids)
            or candidate_ids != sorted(set(candidate_ids))
        ):
            raise ReproductionError(f"candidate_track_ids invalid for {world['world_id']!r}")
        if world["regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" and not candidate_ids:
            raise ReproductionError(f"candidate world lacks candidate track for {world['world_id']!r}")
        if world["status"] != "COMPLETE" and (
            world["regime"] != "TRACKING_UNRESOLVED" or candidate_ids
        ):
            raise ReproductionError(f"failed-world classification mismatch for {world['world_id']!r}")

    atlas: list[dict[str, Any]] = []
    for law_id in manifest.law_order:
        per_ic: list[dict[str, Any]] = []
        for ic_id in manifest.ic_order:
            enrolled = [
                world
                for world in normalized_worlds
                if world["law_id"] == law_id and world["ic_id"] == ic_id
            ]
            counts = {regime: 0 for regime in manifest.regimes}
            complete_count = 0
            for world in enrolled:
                if world["status"] == "COMPLETE":
                    complete_count += 1
                    counts[world["regime"]] += 1
            per_ic.append(
                {
                    "complete": (
                        len(enrolled) == manifest.replicates_per_law_ic
                        and all(world["status"] == "COMPLETE" for world in enrolled)
                    ),
                    "counts": counts,
                    "denominator": len(enrolled),
                    "ic_id": ic_id,
                }
            )
        reproducible = (
            len(per_ic) == len(manifest.ic_order)
            and all(row["complete"] for row in per_ic)
            and all(
                row["counts"]["BOUNDED_ACTIVE_TURNOVER_CANDIDATE"]
                >= manifest.minimum_candidate_worlds_per_ic
                for row in per_ic
            )
        )
        atlas.append(
            {
                "law_id": law_id,
                "per_ic": per_ic,
                "region_id": law_id,
                "reproducible_candidate": reproducible,
            }
        )

    candidate_regions = [row["law_id"] for row in atlas if row["reproducible_candidate"]]
    statuses = [world["status"] for world in normalized_worlds]
    if "NUMERICAL_INVALID" in statuses:
        disposition = "MANIPULATION_OR_NUMERICAL_INVALID"
    elif any(status != "COMPLETE" for status in statuses):
        disposition = "REVISE_INSTRUMENTATION"
    elif candidate_regions:
        disposition = "DEV_REGIME_CANDIDATE"
    else:
        disposition = "DEV_FEASIBILITY_FAIL"
    return {
        "atlas": atlas,
        "candidate_regions": candidate_regions,
        "disposition": disposition,
        "manifest_sha256": manifest.sha256,
        "schema": OUTPUT_SCHEMA_ID,
        "worlds": normalized_worlds,
    }


def reproduce_family(
    manifest: ManifestContract,
    result_root: Path,
) -> dict[str, Any]:
    result_root = result_root.resolve(strict=True)
    if not result_root.is_dir() or result_root.is_symlink():
        raise ReproductionError("result root must be a real directory")
    if result_root.name != Path(RESULT_NAMESPACE).name:
        raise ReproductionError("result root does not match frozen namespace")
    _verify_result_root_entries(result_root, [world.world_id for world in manifest.worlds])

    world_results: list[dict[str, Any]] = []
    for enrollment in sorted(manifest.worlds, key=lambda world: world.world_id):
        shard_dir = _resolved_child(result_root, enrollment.world_id)
        if not shard_dir.is_dir():
            raise ReproductionError(f"shard path is not a directory for {enrollment.world_id}")
        shard_manifest_path = _resolved_child(
            shard_dir, "shard_manifest.json", expected_name="shard_manifest.json"
        )
        shard = _read_json(shard_manifest_path)
        status = _verify_shard_identity(shard, enrollment)
        entry: dict[str, Any] = {
            "candidate_track_ids": [],
            "ic_id": enrollment.ic_id,
            "law_id": enrollment.law_id,
            "regime": "TRACKING_UNRESOLVED",
            "replicate": enrollment.replicate,
            "status": status,
            "world_id": enrollment.world_id,
        }
        if status == "COMPLETE":
            if set(shard) != {"schema", "world", "status", "files", "physics_inventory", "row_counts"}:
                raise ReproductionError(f"complete shard top-level keyset mismatch for {enrollment.world_id}")
            files = _mapping(shard.get("files"), "shard_manifest.files")
            if set(files) != {"physics.npz", "online.json"}:
                raise ReproductionError(f"complete shard file manifest mismatch for {enrollment.world_id}")
            for filename in ("physics.npz", "online.json"):
                file_entry = _mapping(files[filename], f"shard_manifest.files.{filename}")
                if set(file_entry) != {"sha256", "bytes"}:
                    raise ReproductionError(f"invalid {filename} integrity entry")
                _hash_text(file_entry.get("sha256"), f"{filename}.sha256")
                declared_bytes = _integer(file_entry.get("bytes"), f"{filename}.bytes", 1)
                if filename == "online.json" and (shard_dir / filename).stat().st_size != declared_bytes:
                    raise ReproductionError("online.json byte count differs from shard manifest")
            _verify_shard_file_set(shard_dir, {"shard_manifest.json", "physics.npz", "online.json"})
            _validate_row_counts(shard.get("row_counts"), manifest)
            integrity = _extract_physics_integrity(shard)
            inventory = _mapping(shard.get("physics_inventory"), "shard_manifest.physics_inventory")
            physics_path = _find_physics_path(shard_dir, integrity)
            law = manifest.law(enrollment.law_id)
            physics = load_physics(physics_path, integrity, inventory, manifest, law)
            entry.update(reproduce_complete_world(physics, manifest, law))
        else:
            if set(shard) != {"schema", "world", "status", "files"}:
                raise ReproductionError(f"failed shard top-level keyset mismatch for {enrollment.world_id}")
            files = _mapping(shard.get("files"), "shard_manifest.files")
            allowed_failed_files = {"failure.json", "physics.npz", "online.json"}
            if "failure.json" not in files or not set(files).issubset(allowed_failed_files):
                raise ReproductionError(
                    f"failed shard file inventory invalid for {enrollment.world_id}"
                )
            _verify_shard_file_set(shard_dir, {"shard_manifest.json", *files.keys()})
            for filename, raw_file_entry in files.items():
                file_entry = _mapping(
                    raw_file_entry, f"shard_manifest.files.{filename}"
                )
                if set(file_entry) != {"sha256", "bytes"}:
                    raise ReproductionError(f"invalid failed-shard {filename} integrity entry")
                declared_hash = _hash_text(file_entry.get("sha256"), f"{filename}.sha256")
                declared_bytes = _integer(file_entry.get("bytes"), f"{filename}.bytes", 1)
                file_path = shard_dir / filename
                if file_path.stat().st_size != declared_bytes:
                    raise ReproductionError(
                        f"{filename} byte count differs from failed shard manifest"
                    )
                if filename == "physics.npz" and _sha256(file_path) != declared_hash:
                    raise ReproductionError("preserved failed-shard physics.npz hash mismatch")
        world_results.append(entry)

    return build_classification(manifest, world_results)


def _write_exclusive(path: Path, payload: bytes) -> None:
    if path.exists():
        raise ReproductionError(f"refusing to overwrite output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise ReproductionError(f"cannot write output {path}: {exc}") from exc


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--manifest-sha256",
        required=True,
        help="externally supplied SHA-256 of the committed sealed manifest",
    )
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        _assert_not_forbidden(args.manifest)
        _assert_not_forbidden(args.output)
        if len(args.manifest_sha256) != 64 or any(
            character not in "0123456789abcdefABCDEF" for character in args.manifest_sha256
        ):
            raise ReproductionError("--manifest-sha256 must be 64 hexadecimal characters")
        manifest = load_manifest(args.manifest.resolve(strict=True), args.manifest_sha256.lower())
        result = reproduce_family(manifest, args.result_root)
        output_bytes = _canonical_bytes(result)
        _write_exclusive(args.output, output_bytes)
        summary = {
            "bytes": len(output_bytes),
            "output": str(args.output),
            "sha256": hashlib.sha256(output_bytes).hexdigest(),
        }
        sys.stdout.buffer.write(_canonical_bytes(summary))
        return 0
    except (OSError, ReproductionError) as exc:
        sys.stderr.write(f"REPRODUCTION_ERROR: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
