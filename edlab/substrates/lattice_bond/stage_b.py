"""Frozen Stage-B DEV regime-map runner for the lattice-bond substrate.

This module executes only a fully bound manifest.  It contains no adaptive
search, cut, intervention, fitness, genome, visual selection, or memory
writer.  Every physical world is the statistical unit and every enrolled
world is retained.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, fields, is_dataclass
import hashlib
import itertools
import json
import math
import os
import platform
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .engine import AdmissibilityError, LatticeBondEngine, LatticeBondSpec, LatticeBondState, StepLedger
from .instrumentation import (
    DetectorSpec,
    RegimeThresholds,
    TrackObservation,
    TrackerSpec,
    advance_passive_tracer,
    assemble_world_metrics,
    classify_regime,
    component_diagnostics,
    detect_components,
    track_components,
)


SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-MANIFEST-v1"
CLASSIFICATION_SCHEMA = "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-CLASSIFICATION-v1"
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
REPO_ROOT = Path(__file__).resolve().parents[3]
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_HASH_PATHS = frozenset(
    {
        "edlab/substrates/lattice_bond/engine.py",
        "edlab/substrates/lattice_bond/instrumentation.py",
        "edlab/substrates/lattice_bond/stage_b.py",
        "edlab/substrates/lattice_bond/stage_b_reproduce.py",
        "tests/test_lattice_bond.py",
        "tests/test_lattice_bond_instrumentation.py",
        "tests/test_lattice_bond_stage_b.py",
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_SOURCE_ALLOWLIST.json",
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B0_QUALIFICATION.json",
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json",
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json",
    }
)
TERMINAL_STATUSES = frozenset({"COMPLETE", "NUMERICAL_INVALID", "INSTRUMENTATION_INVALID"})
LEDGER_SCALAR_FIELDS = (
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
LEDGER_ARRAY_FIELDS = tuple(field.name for field in fields(StepLedger) if field.name not in LEDGER_SCALAR_FIELDS)


class ManifestError(ValueError):
    """The B1 freeze is incomplete or does not match the local source."""


class NumericalInvalid(RuntimeError):
    """A frozen Stage-A mechanical identity failed during a DEV world."""


class InstrumentationInvalid(RuntimeError):
    """The qualified passive measurement path failed closed."""


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant {value}")


def strict_json_loads(raw: bytes) -> Any:
    return json.loads(raw, parse_constant=_reject_json_constant)


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite value cannot enter canonical JSON")
    return value


def _write_json(path: Path, value: Any) -> None:
    with path.open("wb") as handle:
        handle.write(canonical_json_bytes(_jsonable(value)))
        handle.flush()
        os.fsync(handle.fileno())


def _fsync_file(path: Path) -> None:
    with path.open("rb+") as handle:
        os.fsync(handle.fileno())


def _durable_replace(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"atomic target already exists: {target}")
    os.replace(source, target)
    if os.name != "nt":
        descriptor = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def hash_uniform(namespace: str, *coordinates: object) -> float:
    """Stateless deterministic U[0,1) draw; no mutable RNG or replacement."""

    payload = "|".join((namespace, *(str(item) for item in coordinates))).encode("utf-8")
    integer = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)
    return integer / 18446744073709551616.0


def enumerate_worlds(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    worlds: list[dict[str, Any]] = []
    for law in manifest["law_family"]["laws"]:
        for initial_condition in manifest["initial_conditions"]:
            for replicate in range(manifest["execution"]["replicates_per_law_ic"]):
                worlds.append(
                    {
                        "world_id": f"{law['law_id']}__{initial_condition['ic_id']}__r{replicate:02d}",
                        "law_id": law["law_id"],
                        "ic_id": initial_condition["ic_id"],
                        "replicate": replicate,
                    }
                )
    return tuple(worlds)


def _exact_positive_int(value: Any, name: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ManifestError(f"{name} must be an integer >= {minimum}")
    return value


def validate_manifest_structure(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema") != SCHEMA:
        raise ManifestError("unexpected manifest schema")
    if manifest.get("accepted_parent") != "b0dbab7674816ebdf3f3f911694b2744ca4bfc76":
        raise ManifestError("accepted parent mismatch")
    if manifest.get("b0_commit") != "93f4a42d8972d2d4b9f8da6f1dc3c8161dc3c045":
        raise ManifestError("B0 checkpoint mismatch")
    if manifest.get("namespace") != "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV":
        raise ManifestError("namespace mismatch")
    if manifest.get("extension_policy") != "NO_EXTENSION_NO_REPLACEMENT_NO_RETRY":
        raise ManifestError("extension policy is not closed")
    if manifest.get("execution", {}).get("sample_cadence") != 1:
        raise ManifestError("only the frozen every-step cadence is admissible")
    _exact_positive_int(manifest.get("execution", {}).get("horizon_steps"), "horizon_steps", minimum=2)
    shape = manifest.get("execution", {}).get("shape", [])
    if len(shape) != 2 or any(isinstance(value, bool) or not isinstance(value, int) or value < 2 for value in shape):
        raise ManifestError("lattice shape must contain two integers >=2")
    replicates = _exact_positive_int(
        manifest.get("execution", {}).get("replicates_per_law_ic"), "replicates_per_law_ic"
    )
    if manifest.get("execution", {}).get("backend") != "vectorized_with_every_step_reference_audit":
        raise ManifestError("backend audit binding missing")
    if tuple(manifest["classifier"]["classes"]) != REGIMES:
        raise ManifestError("regime vocabulary or order mismatch")
    DetectorSpec(**manifest["detector"])
    TrackerSpec(**manifest["tracker"])
    thresholds = RegimeThresholds(**manifest["classifier"]["thresholds"])
    if any(
        isinstance(value, bool) or not isinstance(value, int)
        for value in (thresholds.min_persistence_frames, thresholds.min_post_turnover_frames)
    ):
        raise ManifestError("classifier frame thresholds must be integers")
    law_family = manifest["law_family"]
    if law_family.get("sampling_rule") != "full_cartesian_discrete_grid_in_declared_factor_order":
        raise ManifestError("law-family sampling rule is not the frozen Cartesian grid")
    factors = law_family.get("factors")
    if not isinstance(factors, list) or not factors:
        raise ManifestError("law-family factors must be a nonempty ordered list")
    factor_names = [factor.get("name") for factor in factors]
    spec_field_names = {field.name for field in fields(LatticeBondSpec)}
    if len(factor_names) != len(set(factor_names)) or any(name not in spec_field_names for name in factor_names):
        raise ManifestError("law-family factor names are duplicate or unknown")
    for factor in factors:
        levels = factor.get("levels")
        if (
            not isinstance(levels, list)
            or not levels
            or len(levels) != len(set(levels))
            or any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in levels)
            or factor.get("closed_range") != [min(levels), max(levels)]
        ):
            raise ManifestError("law-family levels/range metadata are invalid")
    fixed_spec = law_family.get("fixed_spec")
    if not isinstance(fixed_spec, dict) or set(fixed_spec) != spec_field_names - set(factor_names):
        raise ManifestError("law-family fixed spec keyset is not exact")
    laws = law_family["laws"]
    if not isinstance(laws, list) or not laws or len({item["law_id"] for item in laws}) != len(laws):
        raise ManifestError("law family must be a nonempty unique explicit list")
    combinations = list(itertools.product(*(factor["levels"] for factor in factors)))
    if len(laws) != len(combinations):
        raise ManifestError("law list does not saturate the frozen Cartesian grid")
    for index, (law, combination) in enumerate(zip(laws, combinations, strict=True)):
        if law["law_id"] != f"L{index:03d}":
            raise ManifestError("law IDs/order differ from the frozen factor order")
        expected_spec = dict(fixed_spec)
        expected_spec.update({name: value for name, value in zip(factor_names, combination, strict=True)})
        if law.get("spec") != expected_spec:
            raise ManifestError("enumerated law differs from frozen factors/fixed spec")
        LatticeBondSpec(**expected_spec)
    initial_conditions = manifest["initial_conditions"]
    if [item.get("kind") for item in initial_conditions] != [
        "bounded_hash_soup",
        "generic_compact_fluctuations",
    ]:
        raise ManifestError("exactly the two frozen neutral IC classes are required")
    if len({item["ic_id"] for item in initial_conditions}) != 2:
        raise ManifestError("initial-condition identifiers must be unique")
    soup, compact = initial_conditions
    for low, high, name in (
        (soup["m_low"], soup["m_high"], "soup matter"),
        (soup["n_low"], soup["n_high"], "soup resource"),
        (compact["m_base_low"], compact["m_base_high"], "compact matter base"),
        (compact["n_low"], compact["n_high"], "compact resource"),
        (compact["sigma_low"], compact["sigma_high"], "compact sigma"),
        (compact["amplitude_low"], compact["amplitude_high"], "compact amplitude"),
    ):
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in (low, high)):
            raise ManifestError(f"{name} bounds must be finite numbers")
        if low < 0.0 or high < low:
            raise ManifestError(f"{name} bounds are invalid")
    for key in ("m_low", "m_high", "n_low", "n_high"):
        if soup[key] > 1.0:
            raise ManifestError("soup field ranges must lie in [0,1]")
    for key in ("m_base_low", "m_base_high", "n_low", "n_high", "amplitude_low", "amplitude_high", "m_cap"):
        if compact[key] > 1.0:
            raise ManifestError("compact field ranges must lie in [0,1]")
    _exact_positive_int(compact["blob_count"], "blob_count")
    if compact["sigma_low"] <= 0.0 or compact["m_cap"] < compact["m_base_high"]:
        raise ManifestError("compact fluctuation scale/cap is invalid")
    initializer = manifest.get("initializer")
    if initializer != {
        "algorithm": "sha256_first_u64_big_endian_div_2pow64",
        "namespace": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-FRESH-DEV-v1",
    }:
        raise ManifestError("fresh initializer identity is missing or altered")
    for law in laws:
        spec = law["spec"]
        if soup["m_high"] > spec["m_max"] or compact["m_cap"] > spec["m_max"]:
            raise ManifestError("initial matter range exceeds a law m_max")
        if soup["n_high"] > spec["n_max"] or compact["n_high"] > spec["n_max"]:
            raise ManifestError("initial resource range exceeds a law n_max")
    minimum = _exact_positive_int(
        manifest["region_rule"].get("minimum_candidate_worlds_per_ic"),
        "minimum_candidate_worlds_per_ic",
        minimum=2,
    )
    if minimum > replicates:
        raise ManifestError("region minimum exceeds enrolled replicates")
    expected_count = (
        len(laws)
        * len(initial_conditions)
        * replicates
    )
    worlds = enumerate_worlds(manifest)
    world_count = _exact_positive_int(manifest["execution"].get("world_count"), "world_count")
    if len(worlds) != expected_count or expected_count != world_count:
        raise ManifestError("world count is not exactly frozen")
    if len({world["world_id"] for world in worlds}) != len(worlds):
        raise ManifestError("world identifiers are not unique")
    if manifest["execution"].get("world_ids") != [world["world_id"] for world in worlds]:
        raise ManifestError("explicit enrollment list mismatch")


def load_and_validate_manifest(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    manifest = strict_json_loads(raw)
    if raw != canonical_json_bytes(manifest):
        raise ManifestError("manifest file is not canonical JSON")
    seal = manifest.get("manifest_sha256_excluding_field")
    if not isinstance(seal, str) or LOWER_SHA256.fullmatch(seal) is None:
        raise ManifestError("manifest content seal is missing or malformed")
    copy = dict(manifest)
    copy.pop("manifest_sha256_excluding_field")
    if sha256_bytes(canonical_json_bytes(copy)) != seal:
        raise ManifestError("manifest content seal mismatch")
    validate_manifest_structure(manifest)
    expected_environment = {
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "byteorder": sys.byteorder,
    }
    if manifest.get("environment") != expected_environment:
        raise ManifestError("runtime environment differs from the exact frozen environment")
    source_hashes = manifest.get("source_sha256")
    if not isinstance(source_hashes, dict) or set(source_hashes) != SOURCE_HASH_PATHS:
        raise ManifestError("source hash keyset is not exact and closed")
    repo = REPO_ROOT.resolve()
    for relative, expected in source_hashes.items():
        if not isinstance(expected, str) or LOWER_SHA256.fullmatch(expected) is None:
            raise ManifestError(f"malformed source hash for {relative}")
        relative_path = Path(relative)
        resolved = (repo / relative_path).resolve()
        if relative_path.is_absolute() or not resolved.is_relative_to(repo):
            raise ManifestError(f"source path escapes repository: {relative}")
        actual = sha256_file(resolved)
        if actual != expected:
            raise ManifestError(f"source hash mismatch for {relative}: {actual}")
    return manifest


def _law(manifest: Mapping[str, Any], law_id: str) -> Mapping[str, Any]:
    return next(item for item in manifest["law_family"]["laws"] if item["law_id"] == law_id)


def _ic(manifest: Mapping[str, Any], ic_id: str) -> Mapping[str, Any]:
    return next(item for item in manifest["initial_conditions"] if item["ic_id"] == ic_id)


def build_initial_state(world: Mapping[str, Any], manifest: Mapping[str, Any]) -> LatticeBondState:
    """Create one neutral fresh state from the frozen coordinate hash."""

    shape = tuple(int(value) for value in manifest["execution"]["shape"])
    h, w = shape
    ic = _ic(manifest, str(world["ic_id"]))
    namespace = f"{manifest['initializer']['namespace']}|{world['world_id']}"
    m = np.empty(shape, dtype=np.float64)
    n = np.empty(shape, dtype=np.float64)
    if ic["kind"] == "bounded_hash_soup":
        for y in range(h):
            for x in range(w):
                m[y, x] = ic["m_low"] + (ic["m_high"] - ic["m_low"]) * hash_uniform(namespace, "m", y, x)
                n[y, x] = ic["n_low"] + (ic["n_high"] - ic["n_low"]) * hash_uniform(namespace, "n", y, x)
    elif ic["kind"] == "generic_compact_fluctuations":
        blobs = []
        for index in range(ic["blob_count"]):
            blobs.append(
                (
                    h * hash_uniform(namespace, "blob-y", index),
                    w * hash_uniform(namespace, "blob-x", index),
                    ic["sigma_low"]
                    + (ic["sigma_high"] - ic["sigma_low"]) * hash_uniform(namespace, "blob-sigma", index),
                    ic["amplitude_low"]
                    + (ic["amplitude_high"] - ic["amplitude_low"]) * hash_uniform(namespace, "blob-amplitude", index),
                )
            )
        for y in range(h):
            for x in range(w):
                base = ic["m_base_low"] + (ic["m_base_high"] - ic["m_base_low"]) * hash_uniform(
                    namespace, "m-base", y, x
                )
                fluctuation = 0.0
                for cy, cx, sigma, amplitude in blobs:
                    dy = min(abs(y - cy), h - abs(y - cy))
                    dx = min(abs(x - cx), w - abs(x - cx))
                    fluctuation = max(fluctuation, amplitude * math.exp(-(dy * dy + dx * dx) / (2.0 * sigma * sigma)))
                m[y, x] = min(ic["m_cap"], base + fluctuation)
                n[y, x] = ic["n_low"] + (ic["n_high"] - ic["n_low"]) * hash_uniform(namespace, "n", y, x)
    else:
        raise ManifestError(f"unknown initial-condition kind {ic['kind']!r}")
    b = np.zeros((2, h, w), dtype=np.float64)
    state = LatticeBondState(m, n, b, 0)
    state.validate(LatticeBondSpec(**_law(manifest, str(world["law_id"]))["spec"]))
    return state


def _array_tolerance(reference: np.ndarray | float) -> np.ndarray | float:
    return 1e-12 + 1e-10 * np.abs(reference)


def _reference_error(vector: Any, reference: Any) -> float:
    maximum = 0.0
    if vector.state.step != reference.state.step:
        raise NumericalInvalid("vectorized state clock differs from scalar reference")
    for vector_array, reference_array in (
        (vector.state.m, reference.state.m),
        (vector.state.n, reference.state.n),
        (vector.state.b, reference.state.b),
    ):
        if not np.isfinite(vector_array).all() or not np.isfinite(reference_array).all():
            raise NumericalInvalid("nonfinite vector/reference state")
        error = np.abs(vector_array - reference_array)
        if np.any(error > _array_tolerance(reference_array)):
            raise NumericalInvalid("vectorized state differs from scalar reference")
        maximum = max(maximum, float(np.max(error)))
    for field in fields(StepLedger):
        left = getattr(vector.ledger, field.name)
        right = getattr(reference.ledger, field.name)
        if isinstance(left, np.ndarray):
            if not np.isfinite(left).all() or not np.isfinite(right).all():
                raise NumericalInvalid(f"nonfinite ledger array {field.name}")
            error = np.abs(left - right)
            if np.any(error > _array_tolerance(right)):
                raise NumericalInvalid(f"ledger field {field.name} differs from scalar reference")
            maximum = max(maximum, float(np.max(error)))
        else:
            if not math.isfinite(float(left)) or not math.isfinite(float(right)):
                raise NumericalInvalid(f"nonfinite ledger scalar {field.name}")
            error = abs(float(left) - float(right))
            if error > 1e-12 + 1e-10 * abs(float(right)):
                raise NumericalInvalid(f"ledger scalar {field.name} differs from scalar reference")
            maximum = max(maximum, error)
    return maximum


def _check_stage_a_invariants(result: Any, spec: LatticeBondSpec) -> None:
    ledger = result.ledger
    for field in fields(StepLedger):
        value = getattr(ledger, field.name)
        if isinstance(value, np.ndarray):
            if not np.isfinite(value).all():
                raise NumericalInvalid(f"nonfinite ledger array {field.name}")
        elif not math.isfinite(float(value)):
            raise NumericalInvalid(f"nonfinite ledger scalar {field.name}")
    for name, residual, reference in (
        ("matter", ledger.matter_residual, ledger.initial_matter),
        ("energy", ledger.energy_residual, ledger.initial_stored_energy),
        ("controller-onset", ledger.controller_onset_energy_jump, ledger.initial_stored_energy),
    ):
        if abs(residual) > 1e-12 + 1e-10 * abs(reference):
            raise NumericalInvalid(f"{name} residual exceeds frozen tolerance")
    for name in ("matter_scale", "resource_scale"):
        if not np.array_equal(getattr(ledger, name), np.ones_like(getattr(ledger, name))):
            raise NumericalInvalid("non-neutral intervention scale present in Stage B")
    for name in (
        "matter_missing",
        "resource_missing",
        "matter_missing_from_delta",
        "matter_missing_to_delta",
        "resource_missing_from_delta",
        "resource_missing_to_delta",
    ):
        if not np.array_equal(getattr(ledger, name), np.zeros_like(getattr(ledger, name))):
            raise NumericalInvalid(f"unexpected intervention accounting in {name}")
    try:
        result.state.validate(spec)
    except (AdmissibilityError, ValueError, ArithmeticError, FloatingPointError) as error:
        raise NumericalInvalid("physical state left the frozen admissible domain") from error


def _physics_payload(states: Sequence[LatticeBondState], ledgers: Sequence[StepLedger], errors: Sequence[float]) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {
        "state_step": np.asarray([state.step for state in states], dtype=np.int64),
        "state_m": np.stack([state.m for state in states]),
        "state_n": np.stack([state.n for state in states]),
        "state_b": np.stack([state.b for state in states]),
        "vector_reference_max_error": np.asarray(errors, dtype=np.float64),
        "deterministic_replay_equal": np.ones(len(ledgers), dtype=np.uint8),
    }
    for field in fields(StepLedger):
        values = [getattr(ledger, field.name) for ledger in ledgers]
        payload[f"ledger__{field.name}"] = np.stack(values) if isinstance(values[0], np.ndarray) else np.asarray(values, dtype=np.float64)
    return payload


def _internal_bond_rate(component: Any, ledger: StepLedger, dt: float) -> float:
    mask = component.mask()
    internal = np.zeros_like(ledger.gross_formation_work, dtype=bool)
    for axis in (0, 1):
        internal[axis] = mask & np.roll(mask, -1, axis=axis)
    total = math.fsum(
        float(value)
        for value in (ledger.gross_formation_work[internal] + ledger.gross_rupture_release[internal])
    )
    return total / dt


def _measurement_payload(
    states: Sequence[LatticeBondState],
    ledgers: Sequence[StepLedger],
    manifest: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    detector = DetectorSpec(**manifest["detector"])
    tracker_spec = TrackerSpec(**manifest["tracker"])
    thresholds = RegimeThresholds(**manifest["classifier"]["thresholds"])
    horizon = int(manifest["execution"]["horizon_steps"])
    frames = tuple(detect_components(states[frame], detector, frame=frame) for frame in range(horizon))
    tracking = track_components(frames, tracker_spec)
    component_lookup = {component.key: component for frame in frames for component in frame}
    diagnostics: dict[tuple[int, int], Any] = {}
    internal_energy_rate: dict[tuple[int, int], float] = {}
    for frame, components in enumerate(frames):
        for component in components:
            diagnostics[component.key] = component_diagnostics(component, states[frame], ledgers[frame], LatticeBondSpec(**manifest["active_law_spec"]))
            internal_energy_rate[component.key] = _internal_bond_rate(component, ledgers[frame], manifest["active_law_spec"]["dt"])

    observations: list[TrackObservation] = []
    tracer_rows: list[dict[str, Any]] = []
    for track in tracking.tracks:
        if not track.points:
            continue
        point_by_frame = {point.frame: point for point in track.points}
        first = min(point_by_frame)
        last = max(point_by_frame)
        first_component = component_lookup[(first, point_by_frame[first].component_index)]
        tracer = np.where(first_component.mask(), states[first].m, 0.0).astype(np.float64)
        initial_cohort = math.fsum(float(value) for value in tracer.ravel(order="C"))
        if initial_cohort <= 0.0:
            raise InstrumentationInvalid("detected track has no enrollable cohort mass")
        for frame in range(first, last + 1):
            point = point_by_frame.get(frame)
            if point is not None:
                component = component_lookup[(frame, point.component_index)]
                live_inside = math.fsum(float(value) for value in tracer[component.mask()].ravel(order="C"))
                turnover = 1.0 - live_inside / initial_cohort
                tolerance = 1e-12 + 1e-10 * initial_cohort
                if turnover < -tolerance or turnover > 1.0 + tolerance:
                    raise InstrumentationInvalid("cohort turnover left [0,1]")
                turnover = min(1.0, max(0.0, turnover))
                diag = diagnostics[component.key]
                mass = component.mass
                activity_rate = diag.matter_internal_gross / (manifest["active_law_spec"]["dt"] * mass)
                energy_rate = internal_energy_rate[component.key] / mass
                observations.append(
                    TrackObservation(
                        track.track_id,
                        frame,
                        component.index,
                        component.area / (component.shape[0] * component.shape[1]),
                        component.percolates,
                        activity_rate,
                        energy_rate,
                        turnover,
                    )
                )
                tracer_rows.append(
                    {
                        "track_id": track.track_id,
                        "frame": frame,
                        "initial_cohort_mass": initial_cohort,
                        "live_cohort_in_support": live_inside,
                        "global_cohort_mass": math.fsum(float(value) for value in tracer.ravel(order="C")),
                        "turnover_fraction": turnover,
                    }
                )
            if frame < last:
                tracer = advance_passive_tracer(
                    tracer,
                    states[frame].m,
                    ledgers[frame].matter_forward,
                    ledgers[frame].matter_reverse,
                    states[frame + 1].m,
                    manifest["active_law_spec"]["dt"],
                )

    world_metrics = assemble_world_metrics(frames, tracking, observations, thresholds)
    regime = classify_regime(world_metrics, thresholds)
    candidate_tracks = [
        track.track_id
        for track in world_metrics.tracks
        if track.maximum_area_fraction <= thresholds.max_area_fraction
        and track.bounded_fraction >= thresholds.min_bounded_fraction
        and track.percolated_fraction == 0.0
        and track.observed_frames >= thresholds.min_persistence_frames
        and track.span_frames >= thresholds.min_persistence_frames
        and track.mean_activity_per_mass >= thresholds.min_activity_per_mass
        and track.mean_energy_throughput_per_mass >= thresholds.min_energy_throughput_per_mass
        and track.maximum_turnover_fraction >= thresholds.min_turnover_fraction
        and track.post_turnover_frames >= thresholds.min_post_turnover_frames
        and not track.unresolved
    ]
    if regime != "BOUNDED_ACTIVE_TURNOVER_CANDIDATE":
        candidate_tracks = []
    online = {
        "components": [[_jsonable(component) for component in frame] for frame in frames],
        "association_edges": [_jsonable(edge) for edge in tracking.edges],
        "events": [_jsonable(event) for event in tracking.events],
        "assignments": _jsonable(tracking.assignments),
        "component_diagnostics": [
            {
                **_jsonable(diagnostics[key]),
                "internal_bond_energy_rate": internal_energy_rate[key],
            }
            for key in sorted(diagnostics)
        ],
        "track_observations": [_jsonable(observation) for observation in observations],
        "tracer_rows": tracer_rows,
        "world_metrics": _jsonable(world_metrics),
        "regime": regime,
        "candidate_track_ids": sorted(candidate_tracks),
    }
    summary = {"regime": regime, "candidate_track_ids": sorted(candidate_tracks)}
    return online, summary


def _npz_inventory(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as archive:
        return {
            name: {"shape": list(archive[name].shape), "dtype": str(archive[name].dtype)}
            for name in sorted(archive.files)
        }


def _write_complete_shard(
    root: Path,
    world: Mapping[str, Any],
    physics: Mapping[str, np.ndarray],
    online: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> None:
    final = root / str(world["world_id"])
    partial = root / f"{world['world_id']}.partial"
    if final.exists() or partial.exists():
        raise FileExistsError(f"world shard already exists: {world['world_id']}")
    partial.mkdir()
    physics_path = partial / "physics.npz"
    np.savez_compressed(physics_path, **physics)
    _fsync_file(physics_path)
    online_path = partial / "online.json"
    _write_json(online_path, online)
    shard_manifest = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-SHARD-v1",
        "world": dict(world),
        "status": "COMPLETE",
        "files": {
            "physics.npz": {"sha256": sha256_file(physics_path), "bytes": physics_path.stat().st_size},
            "online.json": {"sha256": sha256_file(online_path), "bytes": online_path.stat().st_size},
        },
        "physics_inventory": _npz_inventory(physics_path),
        "row_counts": {
            "state_rows": int(physics["state_step"].shape[0]),
            "ledger_rows": int(physics["vector_reference_max_error"].shape[0]),
            "component_rows": sum(len(frame) for frame in online["components"]),
            "association_edge_rows": len(online["association_edges"]),
            "event_rows": len(online["events"]),
            "track_observation_rows": len(online["track_observations"]),
            "tracer_rows": len(online["tracer_rows"]),
        },
    }
    _write_json(partial / "shard_manifest.json", shard_manifest)
    _verify_physics(physics_path, shard_manifest, world, manifest)
    _verify_online(online_path, shard_manifest, world, manifest)
    _durable_replace(partial, final)


def _write_failed_shard(root: Path, world: Mapping[str, Any], status: str, error: BaseException) -> None:
    final = root / str(world["world_id"])
    partial = root / f"{world['world_id']}.partial"
    if final.exists():
        raise FileExistsError(f"completed world shard already exists: {world['world_id']}")
    partial.mkdir(exist_ok=True)
    failure = {
        "world": dict(world),
        "status": status,
        "error_type": type(error).__name__,
        "message": str(error),
    }
    _write_json(partial / "failure.json", failure)
    files = {}
    for path in sorted(item for item in partial.iterdir() if item.is_file() and item.name != "shard_manifest.json"):
        files[path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    _write_json(
        partial / "shard_manifest.json",
        {
            "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-SHARD-v1",
            "world": dict(world),
            "status": status,
            "files": files,
        },
    )
    _durable_replace(partial, final)


def run_world(world: Mapping[str, Any], manifest: Mapping[str, Any], root: Path) -> dict[str, Any]:
    law = _law(manifest, str(world["law_id"]))
    spec = LatticeBondSpec(**law["spec"])
    engine = LatticeBondEngine(spec)
    active_manifest = dict(manifest)
    active_manifest["active_law_spec"] = law["spec"]
    try:
        state = build_initial_state(world, manifest)
    except (AdmissibilityError, ArithmeticError, FloatingPointError) as error:
        raise NumericalInvalid("fresh initial state left the frozen physical domain") from error
    states = [state]
    ledgers: list[StepLedger] = []
    reference_errors: list[float] = []
    for _ in range(manifest["execution"]["horizon_steps"]):
        try:
            result = engine.step(state, backend="vectorized")
            replay = engine.step(state, backend="vectorized")
            reference = engine.step(state, backend="reference")
        except (AdmissibilityError, ArithmeticError, FloatingPointError) as error:
            raise NumericalInvalid("Stage-A update rejected a frozen DEV state") from error
        if result.canonical_bytes() != replay.canonical_bytes():
            raise NumericalInvalid("same-state deterministic replay differs")
        reference_errors.append(_reference_error(result, reference))
        _check_stage_a_invariants(result, spec)
        ledgers.append(result.ledger)
        state = result.state
        states.append(state)
    physics = _physics_payload(states, ledgers, reference_errors)
    online, summary = _measurement_payload(states, ledgers, active_manifest)
    online = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ONLINE-v1",
        "world": dict(world),
        **online,
    }
    _write_complete_shard(root, world, physics, online, manifest)
    return {**dict(world), "status": "COMPLETE", **summary}


def classify_family(world_rows: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]) -> dict[str, Any]:
    _validate_world_rows(world_rows, manifest)
    atlas: list[dict[str, Any]] = []
    candidate_regions: list[str] = []
    minimum = int(manifest["region_rule"]["minimum_candidate_worlds_per_ic"])
    for law in manifest["law_family"]["laws"]:
        law_rows = [row for row in world_rows if row["law_id"] == law["law_id"]]
        per_ic = []
        reproducible = True
        for ic in manifest["initial_conditions"]:
            rows = [row for row in law_rows if row["ic_id"] == ic["ic_id"]]
            counts = Counter(row["regime"] for row in rows if row["status"] == "COMPLETE")
            candidate_count = counts["BOUNDED_ACTIVE_TURNOVER_CANDIDATE"]
            complete = len(rows) == manifest["execution"]["replicates_per_law_ic"] and all(
                row["status"] == "COMPLETE" for row in rows
            )
            reproducible = reproducible and complete and candidate_count >= minimum
            per_ic.append(
                {
                    "ic_id": ic["ic_id"],
                    "denominator": len(rows),
                    "complete": complete,
                    "counts": {regime: counts[regime] for regime in REGIMES},
                }
            )
        atlas.append({"region_id": law["law_id"], "law_id": law["law_id"], "per_ic": per_ic, "reproducible_candidate": reproducible})
        if reproducible:
            candidate_regions.append(law["law_id"])
    statuses = {row["status"] for row in world_rows}
    if "NUMERICAL_INVALID" in statuses:
        disposition = "MANIPULATION_OR_NUMERICAL_INVALID"
    elif statuses != {"COMPLETE"}:
        disposition = "REVISE_INSTRUMENTATION"
    elif candidate_regions:
        disposition = "DEV_REGIME_CANDIDATE"
    else:
        disposition = "DEV_FEASIBILITY_FAIL"
    return {
        "schema": CLASSIFICATION_SCHEMA,
        "manifest_sha256": manifest["runtime_manifest_sha256"],
        "worlds": [dict(row) for row in sorted(world_rows, key=lambda item: item["world_id"])],
        "atlas": atlas,
        "candidate_regions": candidate_regions,
        "disposition": disposition,
    }


def _validate_world_rows(world_rows: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]) -> None:
    expected = {world["world_id"]: world for world in enumerate_worlds(manifest)}
    identifiers = [row.get("world_id") for row in world_rows]
    if len(identifiers) != len(set(identifiers)):
        raise InstrumentationInvalid("duplicate world row")
    if set(identifiers) != set(expected) or len(world_rows) != len(expected):
        raise InstrumentationInvalid("world rows do not exactly match frozen enrollment")
    for row in world_rows:
        identity = expected[row["world_id"]]
        if any(row.get(key) != identity[key] for key in ("law_id", "ic_id", "replicate")):
            raise InstrumentationInvalid("world coordinates differ from frozen enrollment")
        if row.get("status") not in TERMINAL_STATUSES:
            raise InstrumentationInvalid("unknown terminal world status")
        if row.get("regime") not in REGIMES:
            raise InstrumentationInvalid("unknown regime")
        candidate_ids = row.get("candidate_track_ids")
        if (
            not isinstance(candidate_ids, list)
            or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in candidate_ids)
            or len(candidate_ids) != len(set(candidate_ids))
        ):
            raise InstrumentationInvalid("candidate track IDs are malformed")
        is_candidate = row["regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
        if bool(candidate_ids) != is_candidate:
            raise InstrumentationInvalid("candidate IDs and regime disagree")
        if row["status"] != "COMPLETE" and (row["regime"] != "TRACKING_UNRESOLVED" or candidate_ids):
            raise InstrumentationInvalid("failed world has been reclassified")


def _expected_physics_layout(manifest: Mapping[str, Any]) -> dict[str, tuple[tuple[int, ...], str]]:
    horizon = manifest["execution"]["horizon_steps"]
    y, x = manifest["execution"]["shape"]
    layout: dict[str, tuple[tuple[int, ...], str]] = {
        "state_step": ((horizon + 1,), "int64"),
        "state_m": ((horizon + 1, y, x), "float64"),
        "state_n": ((horizon + 1, y, x), "float64"),
        "state_b": ((horizon + 1, 2, y, x), "float64"),
        "vector_reference_max_error": ((horizon,), "float64"),
        "deterministic_replay_equal": ((horizon,), "uint8"),
    }
    for name in LEDGER_ARRAY_FIELDS:
        layout[f"ledger__{name}"] = ((horizon, y, x), "float64") if name == "affinity" else (
            (horizon, 2, y, x),
            "float64",
        )
    for name in LEDGER_SCALAR_FIELDS:
        layout[f"ledger__{name}"] = ((horizon,), "float64")
    return layout


def _verify_physics(path: Path, shard: Mapping[str, Any], world: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    layout = _expected_physics_layout(manifest)
    try:
        with np.load(path, allow_pickle=False) as archive:
            if set(archive.files) != set(layout):
                raise InstrumentationInvalid("physics array keyset is not exact")
            actual_inventory = {}
            maximum_scale = 1.0
            for name, (shape, dtype) in layout.items():
                value = archive[name]
                actual_inventory[name] = {"shape": list(value.shape), "dtype": str(value.dtype)}
                if value.shape != shape or str(value.dtype) != dtype:
                    raise InstrumentationInvalid(f"physics shape/dtype mismatch for {name}")
                if not np.isfinite(value).all():
                    raise InstrumentationInvalid(f"nonfinite physics array {name}")
                if np.issubdtype(value.dtype, np.floating):
                    maximum_scale = max(maximum_scale, float(np.max(np.abs(value))))
            if shard.get("physics_inventory") != actual_inventory:
                raise InstrumentationInvalid("physics inventory differs from NPZ content")
            horizon = manifest["execution"]["horizon_steps"]
            if not np.array_equal(archive["state_step"], np.arange(horizon + 1, dtype=np.int64)):
                raise InstrumentationInvalid("state clock rows are not exact")
            if not np.array_equal(archive["deterministic_replay_equal"], np.ones(horizon, dtype=np.uint8)):
                raise InstrumentationInvalid("deterministic replay evidence is not all true")
            errors = archive["vector_reference_max_error"]
            if float(np.min(errors)) < 0.0 or float(np.max(errors)) > 1e-12 + 1e-10 * maximum_scale:
                raise InstrumentationInvalid("reference error evidence exceeds the frozen criterion")
            law = _law(manifest, str(world["law_id"]))["spec"]
            tolerance = 1e-12 + 1e-10 * max(law["m_max"], law["n_max"], 1.0)
            for name, lower, upper in (
                ("state_m", 0.0, law["m_max"]),
                ("state_n", 0.0, law["n_max"]),
                ("state_b", 0.0, 1.0),
            ):
                if float(np.min(archive[name])) < lower - tolerance or float(np.max(archive[name])) > upper + tolerance:
                    raise InstrumentationInvalid(f"raw physical domain violation in {name}")
            for name in ("matter_scale", "resource_scale"):
                value = archive[f"ledger__{name}"]
                if not np.array_equal(value, np.ones_like(value)):
                    raise InstrumentationInvalid("raw intervention scale is non-neutral")
            for name in (
                "matter_missing",
                "resource_missing",
                "matter_missing_from_delta",
                "matter_missing_to_delta",
                "resource_missing_from_delta",
                "resource_missing_to_delta",
            ):
                value = archive[f"ledger__{name}"]
                if not np.array_equal(value, np.zeros_like(value)):
                    raise InstrumentationInvalid("raw missing-flux field is nonzero")
            for residual_name, reference_name in (
                ("matter_residual", "initial_matter"),
                ("energy_residual", "initial_stored_energy"),
                ("controller_onset_energy_jump", "initial_stored_energy"),
            ):
                residual = archive[f"ledger__{residual_name}"]
                reference = archive[f"ledger__{reference_name}"]
                if np.any(np.abs(residual) > 1e-12 + 1e-10 * np.abs(reference)):
                    raise InstrumentationInvalid(f"raw {residual_name} exceeds frozen tolerance")
    except InstrumentationInvalid:
        raise
    except Exception as error:
        raise InstrumentationInvalid("physics.npz cannot be parsed and verified") from error


def _verify_online(path: Path, shard: Mapping[str, Any], world: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    raw = path.read_bytes()
    try:
        online = strict_json_loads(raw)
    except Exception as error:
        raise InstrumentationInvalid("online JSON is malformed or nonfinite") from error
    if raw != canonical_json_bytes(online):
        raise InstrumentationInvalid("online JSON is not canonical")
    if online.get("schema") != "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ONLINE-v1" or online.get("world") != world:
        raise InstrumentationInvalid("online schema or world identity mismatch")
    horizon = manifest["execution"]["horizon_steps"]
    list_fields = (
        "components",
        "association_edges",
        "events",
        "assignments",
        "component_diagnostics",
        "track_observations",
        "tracer_rows",
        "candidate_track_ids",
    )
    if any(not isinstance(online.get(name), list) for name in list_fields) or len(online["components"]) != horizon:
        raise InstrumentationInvalid("online row collections are malformed")
    if not isinstance(online.get("world_metrics"), dict) or online.get("regime") not in REGIMES:
        raise InstrumentationInvalid("online metrics or regime are malformed")
    expected_rows = {
        "state_rows": horizon + 1,
        "ledger_rows": horizon,
        "component_rows": sum(len(frame) for frame in online["components"]),
        "association_edge_rows": len(online["association_edges"]),
        "event_rows": len(online["events"]),
        "track_observation_rows": len(online["track_observations"]),
        "tracer_rows": len(online["tracer_rows"]),
    }
    if shard.get("row_counts") != expected_rows:
        raise InstrumentationInvalid("shard row counts differ from raw online rows")
    candidate_ids = online["candidate_track_ids"]
    if bool(candidate_ids) != (online["regime"] == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"):
        raise InstrumentationInvalid("online candidate IDs and regime disagree")


def _verify_partial_root(root: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    expected = {world["world_id"]: world for world in enumerate_worlds(manifest)}
    shard_directories = sorted(path for path in root.iterdir() if path.is_dir())
    if {path.name for path in shard_directories} != set(expected):
        raise InstrumentationInvalid("published shard directories do not match enrollment")
    inventory: list[dict[str, Any]] = []
    for directory in shard_directories:
        manifest_path = directory / "shard_manifest.json"
        raw = manifest_path.read_bytes()
        try:
            shard = strict_json_loads(raw)
        except Exception as error:
            raise InstrumentationInvalid("shard manifest is malformed or nonfinite") from error
        if raw != canonical_json_bytes(shard):
            raise InstrumentationInvalid("shard manifest is not canonical")
        if shard.get("schema") != "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-SHARD-v1":
            raise InstrumentationInvalid("shard schema mismatch")
        if shard.get("world") != expected[directory.name]:
            raise InstrumentationInvalid("shard identity differs from enrollment")
        if shard.get("status") not in TERMINAL_STATUSES:
            raise InstrumentationInvalid("shard has unknown terminal status")
        actual_files = {path.name for path in directory.iterdir() if path.is_file() and path.name != "shard_manifest.json"}
        if actual_files != set(shard.get("files", {})):
            raise InstrumentationInvalid("shard file inventory is not exact")
        for name, record in shard.get("files", {}).items():
            file_path = directory / name
            if not file_path.is_file():
                raise InstrumentationInvalid("shard file is missing")
            if file_path.stat().st_size != record.get("bytes") or sha256_file(file_path) != record.get("sha256"):
                raise InstrumentationInvalid("shard file integrity mismatch")
        if shard["status"] == "COMPLETE":
            if set(shard["files"]) != {"physics.npz", "online.json"} or "row_counts" not in shard:
                raise InstrumentationInvalid("complete shard lacks required files or row counts")
            _verify_physics(directory / "physics.npz", shard, expected[directory.name], manifest)
            _verify_online(directory / "online.json", shard, expected[directory.name], manifest)
        else:
            if "failure.json" not in shard["files"]:
                raise InstrumentationInvalid("failed shard lacks failure record")
            failure_path = directory / "failure.json"
            failure_raw = failure_path.read_bytes()
            try:
                failure = strict_json_loads(failure_raw)
            except Exception as error:
                raise InstrumentationInvalid("failure record is malformed or nonfinite") from error
            if failure_raw != canonical_json_bytes(failure):
                raise InstrumentationInvalid("failure record is not canonical")
            if failure.get("world") != expected[directory.name] or failure.get("status") != shard["status"]:
                raise InstrumentationInvalid("failure record identity/status mismatch")
        inventory.append(
            {
                "world_id": directory.name,
                "status": shard["status"],
                "shard_manifest_sha256": sha256_file(manifest_path),
                "shard_manifest_bytes": manifest_path.stat().st_size,
            }
        )
    return inventory


def run_family(manifest_path: Path) -> dict[str, Any]:
    manifest = load_and_validate_manifest(manifest_path)
    manifest["runtime_manifest_sha256"] = sha256_file(manifest_path)
    final_root = REPO_ROOT / manifest["namespace"]
    partial_root = final_root.with_name(final_root.name + ".partial")
    if final_root.exists() or partial_root.exists():
        raise FileExistsError("Stage-B result root or partial root already exists; retries/replacements are forbidden")
    partial_root.parent.mkdir(parents=True, exist_ok=True)
    partial_root.mkdir()
    _write_json(partial_root / "enrollment.json", {"worlds": list(enumerate_worlds(manifest))})
    rows: list[dict[str, Any]] = []
    for world in enumerate_worlds(manifest):
        try:
            rows.append(run_world(world, manifest, partial_root))
        except NumericalInvalid as error:
            _write_failed_shard(partial_root, world, "NUMERICAL_INVALID", error)
            rows.append({**world, "status": "NUMERICAL_INVALID", "regime": "TRACKING_UNRESOLVED", "candidate_track_ids": []})
        except Exception as error:  # failure is preserved; never replaced
            _write_failed_shard(partial_root, world, "INSTRUMENTATION_INVALID", error)
            rows.append({**world, "status": "INSTRUMENTATION_INVALID", "regime": "TRACKING_UNRESOLVED", "candidate_track_ids": []})
    classification = classify_family(rows, manifest)
    _write_json(partial_root / "classification.json", classification)
    shard_inventory = _verify_partial_root(partial_root, manifest)
    root_manifest = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ROOT-v1",
        "manifest_sha256": manifest["runtime_manifest_sha256"],
        "world_count": len(rows),
        "raw_schema_sha256": manifest["source_sha256"]["docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json"],
        "enrollment_sha256": sha256_file(partial_root / "enrollment.json"),
        "enrollment_bytes": (partial_root / "enrollment.json").stat().st_size,
        "classification_sha256": sha256_file(partial_root / "classification.json"),
        "classification_bytes": (partial_root / "classification.json").stat().st_size,
        "shards": shard_inventory,
        "disposition": classification["disposition"],
    }
    _write_json(partial_root / "root_manifest.json", root_manifest)
    if {path.name for path in partial_root.iterdir() if path.is_file()} != {
        "enrollment.json",
        "classification.json",
        "root_manifest.json",
    }:
        raise InstrumentationInvalid("root file inventory is not exact")
    _durable_replace(partial_root, final_root)
    return classification


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_family(args.manifest.resolve())
    print(result["disposition"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
