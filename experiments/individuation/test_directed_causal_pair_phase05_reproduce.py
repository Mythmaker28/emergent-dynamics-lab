"""Engine-free synthetic tests for the Phase-0.5 mechanical raw reproducer.

No development world, scientific endpoint, engine, reader, decoder, or analyzer
is imported here.  The fixtures are standard-library constructions of the
strict mechanical raw contract, including both a complete synthetic pass and a
legitimate fail-closed shard.
"""

from __future__ import annotations

import ast
import base64
import copy
from functools import lru_cache
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping

import pytest

from experiments.individuation import directed_causal_pair_phase05_reproduce as repro


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json"
RUNNER_PATH = ROOT / "experiments/individuation/directed_causal_pair_phase05_runner.py"
CENTERS = ((8.0, 8.0), (8.0, 40.0), (40.0, 40.0))
RETENTIONS = (0.11, 0.22, 0.05)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _blob(label: str) -> str:
    return hashlib.sha1(label.encode("utf-8")).hexdigest()


def _body(center: tuple[float, float]) -> frozenset[int]:
    row, column = (int(center[0]), int(center[1]))
    return frozenset(
        ((row + dr) % 64) * 64 + ((column + dc) % 64)
        for dr in range(-3, 4)
        for dc in range(-3, 4)
    )


def _packed(cells: frozenset[int] | set[int]) -> dict[str, Any]:
    payload = bytearray(repro.PACKED_BYTES)
    for flat in cells:
        payload[flat // 8] |= 1 << (flat % 8)
    packed = bytes(payload)
    return {
        "encoding": "PACKED_BITS_BASE64_V1",
        "shape": [64, 64],
        "bitorder": "little",
        "data_base64": base64.b64encode(packed).decode("ascii"),
        "sha256": hashlib.sha256(packed).hexdigest(),
    }


def _bindings() -> list[dict[str, str]]:
    return [
        {"kind": kind, "path": path, "sha256": _sha(f"sha:{path}"), "git_blob": _blob(f"blob:{path}")}
        for kind, paths in (
            ("INPUT", sorted(repro.EXPECTED_INPUT_PATHS)),
            ("CODE", sorted(repro.EXPECTED_CODE_PATHS)),
        )
        for path in paths
    ]


def _association_edges(
    prior_masks: Mapping[int, repro.DecodedMask],
    prior_centroids: Mapping[int, tuple[float, float]],
    component_masks: Mapping[int, repro.DecodedMask],
    component_centroids: Mapping[int, tuple[float, float]],
    selected_components: Mapping[int, int],
) -> list[dict[str, Any]]:
    overlaps = {
        tracker_id: {
            component_id: len(prior.cells & component.cells) / max(1, prior.count)
            for component_id, component in component_masks.items()
        }
        for tracker_id, prior in prior_masks.items()
    }
    ranks = {
        tracker_id: {
            component_id: rank
            for rank, component_id in enumerate(
                sorted(component_masks, key=lambda item: (-tracker_overlaps[item], item))
            )
        }
        for tracker_id, tracker_overlaps in overlaps.items()
    }
    rows: list[dict[str, Any]] = []
    for tracker_id in sorted(prior_masks):
        for component_id in sorted(component_masks):
            overlap = overlaps[tracker_id][component_id]
            rows.append(
                {
                    "tracker_id": tracker_id,
                    "component_id": component_id,
                    "overlap": overlap,
                    "centroid_distance": repro.toroidal_distance(
                        prior_centroids[tracker_id], component_centroids[component_id]
                    ),
                    "size_ratio": component_masks[component_id].count / max(1, prior_masks[tracker_id].count),
                    "theta_gate": overlap >= repro.TRACK_THETA,
                    "split_gate": overlap >= repro.TRACK_SPLIT_FRAC,
                    "compatible": overlap >= repro.TRACK_THETA,
                    "assignment_cost": -overlap,
                    "rank": ranks[tracker_id][component_id],
                    "selected": selected_components[tracker_id] == component_id,
                }
            )
    return rows


@lru_cache(maxsize=None)
def _bundle(world_id: int, collar_recipient: str | None) -> dict[str, Any]:
    assignment = repro.WORLD_ASSIGNMENTS[world_id]
    body_values = {index: _packed(_body(CENTERS[index])) for index in range(3)}
    body_masks = {index: repro.decode_mask(value) for index, value in body_values.items()}
    centroids = {index: CENTERS[index] for index in range(3)}
    core_cells = {index: repro.disk_cells(centroids[index], repro.CORE_RADIUS) for index in range(3)}
    halo_cells = {index: repro.disk_cells(centroids[index], repro.HALO_RADIUS) for index in range(3)}
    core_values = {index: _packed(core_cells[index]) for index in range(3)}
    halo_values = {index: _packed(halo_cells[index]) for index in range(3)}

    components = [
        {
            "component_id": index,
            "size": body_masks[index].count,
            "centroid": list(centroids[index]),
            "mask": body_values[index],
        }
        for index in range(3)
    ]
    tracks = [
        {
            "tracker_id": index,
            "status": "ALIVE",
            "component_id": index,
            "component_size": body_masks[index].count,
            "centroid": list(centroids[index]),
            "body_core_coverage": len(body_masks[index].cells & core_cells[index]) / body_masks[index].count,
            "body_mask": body_values[index],
            "core_mask": core_values[index],
            "halo_mask": halo_values[index],
        }
        for index in range(3)
    ]

    a_tracker, b_tracker, sentinel_tracker = assignment
    collar_cells: frozenset[int] | set[int]
    collar: dict[str, Any] | None
    if collar_recipient is None:
        collar_cells = frozenset()
        collar = None
    else:
        recipient_tracker = a_tracker if collar_recipient == "A" else b_tracker
        partner_tracker = b_tracker if collar_recipient == "A" else a_tracker
        collar_cells = halo_cells[recipient_tracker] - core_cells[recipient_tracker]
        wrong_trackers = [index for index in range(3) if index != recipient_tracker]
        collar = {
            "recipient": collar_recipient,
            "recipient_body_intersection_cells": len(collar_cells & body_masks[recipient_tracker].cells),
            "partner_body_intersection_cells": len(collar_cells & body_masks[partner_tracker].cells),
            "recipient_core_intersection_cells": len(collar_cells & core_cells[recipient_tracker]),
            "wrong_core_intersection_cells": sum(
                len(collar_cells & core_cells[index]) for index in wrong_trackers
            ),
        }

    named_masks = {
        "A": body_values[a_tracker],
        "B": body_values[b_tracker],
        "SENTINEL": body_values[sentinel_tracker],
        "core_A": core_values[a_tracker],
        "core_B": core_values[b_tracker],
        "halo_A": halo_values[a_tracker],
        "halo_B": halo_values[b_tracker],
        "collar": _packed(collar_cells),
    }
    distance = repro.toroidal_distance(centroids[a_tracker], centroids[b_tracker])
    pair_geometry = {
        "centroid_A": list(centroids[a_tracker]),
        "centroid_B": list(centroids[b_tracker]),
        "distance": distance,
        "core_overlap_cells": len(core_cells[a_tracker] & core_cells[b_tracker]),
        "halo_overlap_cells": len(halo_cells[a_tracker] & halo_cells[b_tracker]),
        "minimum_core_gap": distance - 2.0 * repro.CORE_RADIUS,
        "minimum_halo_gap": distance - 2.0 * repro.HALO_RADIUS,
        "body_contact": repro.masks_contact_four_neighbour(body_masks[a_tracker], body_masks[b_tracker]),
        "body_overlap_cells": len(body_masks[a_tracker].cells & body_masks[b_tracker].cells),
    }
    return {
        "assignment": {
            "A_target_index": a_tracker,
            "B_target_index": b_tracker,
            "sentinel_target_index": sentinel_tracker,
            "pair_order": ["A", "B"],
        },
        "components": components,
        "association_edges": _association_edges(
            body_masks,
            centroids,
            body_masks,
            centroids,
            {index: index for index in range(3)},
        ),
        "tracks": tracks,
        "pair_geometry": pair_geometry,
        "collar": collar,
        "masks": named_masks,
        "body_masks": body_masks,
        "centroids": centroids,
        "largest_component_coverage": max(mask.count for mask in body_masks.values()) / repro.GRID_CELLS,
    }


def _step_record(
    world_id: int,
    *,
    stage: str,
    stage_step: int,
    engine_step: int,
    state_sha256: str | None = None,
    collar_recipient: str | None = None,
    material_retention: tuple[float, float, float] | None = None,
    state_finite: bool = True,
    component_switch: bool = False,
) -> dict[str, Any]:
    bundle = _bundle(world_id, collar_recipient)
    reasons: list[str] = []
    if not state_finite:
        reasons.append("NONFINITE_STATE")
    if component_switch:
        reasons.append("PAIR_IDENTITY_SWITCH")
    reasons.sort()
    if stage == "TURNOVER":
        retention = list(material_retention or RETENTIONS)
        deep_material_gate: bool | None = not reasons and all(value <= 0.25 for value in retention)
    else:
        retention = None
        deep_material_gate = None
    return {
        "stage": stage,
        "stage_step": stage_step,
        "engine_step": engine_step,
        "state_sha256": state_sha256 or _sha(f"state:{stage}:{engine_step}"),
        "assignment": bundle["assignment"],
        "components": bundle["components"],
        "association_edges": bundle["association_edges"],
        "tracks": bundle["tracks"],
        "events": {},
        "pair_geometry": bundle["pair_geometry"],
        "component_switch": component_switch,
        "largest_component_coverage": bundle["largest_component_coverage"],
        "collar": bundle["collar"],
        "sentinel_valid": True,
        "state_finite": state_finite,
        "logger_state_unchanged": True,
        "kill_reasons": reasons,
        "masks": bundle["masks"],
        "material_retention": retention,
        "deep_material_gate": deep_material_gate,
    }


def _root_writer() -> dict[str, Any]:
    return {
        "writer_id": "FROZEN_03G_LOCAL_GAUSSIAN_WRITER",
        "stream_rule": "first amplitude pair from numpy default_rng(original_world_id)",
        "phase_steps": 60,
        "phase_amplitudes": [0.01, 0.02],
        "amplitude_range": [0.005, 0.035],
        "target_patch_sha256": {"A": _sha("patch:A"), "B": _sha("patch:B")},
        "operation_order": ["A", "B"],
        "operations_per_writer_step": 2,
        "common_schedule_sha256": _sha("writer:schedule"),
    }


def _schedule() -> dict[str, Any]:
    return {
        "schedule_id": "CORRECTED_NONFUSING_PROBE_V1",
        "N_standardized_to": 1.0,
        "settle_steps": 40,
        "stimulus_amplitude": 0.25,
        "stimulus_steps": 5,
        "horizon_steps": 40,
        "total_engine_steps": 80,
        "schedule_digest": _sha("probe:schedule"),
    }


def _writer_records(world_id: int, clone_sha256: str) -> list[dict[str, Any]]:
    rows = [
        _step_record(
            world_id,
            stage="PREWRITER",
            stage_step=0,
            engine_step=0,
            state_sha256=clone_sha256,
        )
    ]
    rows.extend(
        _step_record(
            world_id,
            stage="WRITER",
            stage_step=step,
            engine_step=step,
            state_sha256=_sha(f"writer:{step}"),
        )
        for step in range(1, 121)
    )
    rows.extend(
        _step_record(
            world_id,
            stage="POSTWRITER_SETTLE",
            stage_step=step,
            engine_step=120 + step,
            state_sha256=_sha(f"writer:{120 + step}"),
        )
        for step in range(1, 121)
    )
    return rows


@lru_cache(maxsize=None)
def _access_records(world_id: int, recipient: str | None) -> tuple[dict[str, Any], ...]:
    rows = [
        _step_record(
            world_id,
            stage="PROBE_STANDARDIZE",
            stage_step=0,
            engine_step=300,
            state_sha256=_sha("probe:0"),
            collar_recipient=recipient,
        )
    ]
    rows.extend(
        _step_record(
            world_id,
            stage="PROBE_SETTLE",
            stage_step=step,
            engine_step=300 + step,
            state_sha256=_sha(f"probe:{step}"),
            collar_recipient=recipient,
        )
        for step in range(1, 41)
    )
    rows.extend(
        _step_record(
            world_id,
            stage="PROBE_HORIZON",
            stage_step=step,
            engine_step=340 + step,
            state_sha256=_sha(f"probe:{40 + step}"),
            collar_recipient=recipient,
        )
        for step in range(1, 41)
    )
    return tuple(rows)


def _isolation(recipient: str) -> dict[str, Any]:
    rows = [
        {
            "schedule_step": step,
            "max_core_abs": 0.0,
            "left_core_sha256": _sha(f"core:{recipient}:{step}"),
            "right_core_sha256": _sha(f"core:{recipient}:{step}"),
            "left_state_sha256": _sha(f"probe:{step}"),
            "free_up_ref_state_sha256": _sha(f"probe:{step}"),
        }
        for step in range(1, 81)
    ]
    return {
        "recipient": recipient,
        "barrier_width": 2,
        "up_ref_zero": True,
        "environment_perturbation": {"fields": ["c", "N"], "amplitude": 0.05},
        "per_step": rows,
        "maximum_core_abs_difference": 0.0,
        "environment_c_max_difference_at_end": 0.05,
        "outside_difference_nonzero": True,
        "own_replay_up_ref_zero_exact": True,
        "left_first_failure": None,
        "right_first_failure": None,
        "bit_exact_isolation": True,
    }


def _access_set(world_id: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    schedule = _schedule()
    for regime in repro.ACCESS_ORDER:
        recipient = repro.ACCESS_RECIPIENT[regime]
        clamp_active = regime not in ("ORDINARY", "UP_REF_ZERO")
        combined = regime.startswith("REFERENCE_NOSWAP_") and regime.endswith("_UP_REF_ZERO")
        own_replay = regime.startswith("OWN_REPLAY_SHAM_")
        rows.append(
            {
                "regime": regime,
                "recipient": recipient,
                "schedule": schedule,
                "operation": {
                    "clamp_active": clamp_active,
                    "up_ref_zero": regime
                    in (
                        "UP_REF_ZERO",
                        "REFERENCE_NOSWAP_A_UP_REF_ZERO",
                        "REFERENCE_NOSWAP_B_UP_REF_ZERO",
                    ),
                    "recipient": recipient,
                    "boundary_frames_sha256": _sha(f"boundary:{regime}") if clamp_active else None,
                    "own_replay_exact": True if own_replay else None,
                    "unintended_write_cells": 0,
                    "isolation_exact": True if combined else None,
                    "schedule_digest": schedule["schedule_digest"],
                },
                "records": list(_access_records(world_id, recipient if clamp_active else None)),
                "complete": True,
                "probe_schedule_viable": True,
                "first_failure": None,
                "isolation_evidence": _isolation(str(recipient)) if combined else None,
            }
        )
    return rows


def _deep_joint(world_id: int, turnover_record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "target": label,
            "material_retention": turnover_record["material_retention"][tracker_id],
            "phenotype_descriptor": {
                "component_size": turnover_record["tracks"][tracker_id]["component_size"],
                "centroid": turnover_record["tracks"][tracker_id]["centroid"],
                "body_core_coverage": turnover_record["tracks"][tracker_id]["body_core_coverage"],
            },
        }
        for label, tracker_id in zip(("A", "B", "SENTINEL"), repro.WORLD_ASSIGNMENTS[world_id])
    ]


@lru_cache(maxsize=None)
def _pass_shard(world_id: int = 50002) -> dict[str, Any]:
    sequence = repro.WORLD_ORDER.index(world_id)
    clone = _sha(f"prewriter:{world_id}")
    writer_records = _writer_records(world_id, clone)
    turnover_record = _step_record(
        world_id,
        stage="TURNOVER",
        stage_step=1,
        engine_step=241,
        state_sha256=_sha("turnover:1"),
        material_retention=RETENTIONS,
    )
    access_regimes = _access_set(world_id)
    arms: list[dict[str, Any]] = []
    for arm in repro.ARM_ORDER:
        arms.append(
            {
                "arm": arm,
                "bits": list(repro.ARM_BITS[arm]),
                "clone_sha256": clone,
                "writer": {
                    "operation_count": 240,
                    "expected_operation_count": 240,
                    "total_writer_engine_steps": 240,
                    "active_writer_steps": 120,
                    "settle_steps": 120,
                    "operation_digest": _sha(f"operation:{arm}"),
                    "postwriter_state_sha256": writer_records[-1]["state_sha256"],
                    "sham_reference_exact": True if arm == "H00" else None,
                },
                "writer_records": writer_records,
                "common_deep_step": 1,
                "deep_complete": True,
                "deep_joint": _deep_joint(world_id, turnover_record),
                "turnover_records": [turnover_record],
                "access_regimes": access_regimes,
                "arm_complete": True,
                "first_failure": None,
            }
        )
    a, b, sentinel = repro.WORLD_ASSIGNMENTS[world_id]
    return {
        "schema": repro.RAW_SCHEMA,
        "mission": repro.MISSION,
        "mode": repro.MODE,
        "phase0_commit": repro.PHASE0_COMMIT,
        "world_id": world_id,
        "sequence_index": sequence,
        "manifest_sha256": _sha("manifest"),
        "plan_sha256": repro.EXPECTED_PLAN_SHA256,
        "previous_record_sha256": None,
        "contract_bindings": _bindings(),
        "assignment": {"target_A": a, "target_B": b, "sentinel": sentinel},
        "prewriter_state_sha256": clone,
        "prewriter_clone_sha256": [clone] * 4,
        "writer": _root_writer(),
        "common_deep_step": 1,
        "history_arms": arms,
        "world_complete": True,
        "first_failure": None,
    }


def _failure_shard(
    *,
    sequence: int = 0,
    previous_record_sha256: str | None = None,
) -> dict[str, Any]:
    world_id = repro.WORLD_ORDER[sequence]
    clone = _sha(f"prewriter:{world_id}")
    failure = {
        "stage": "WRITER",
        "stage_step": 0,
        "engine_step": 0,
        "reasons": ["WRITER_SCHEDULE_INCOMPLETE"],
    }
    arms = []
    for arm in repro.ARM_ORDER:
        prewriter = _step_record(
            world_id,
            stage="PREWRITER",
            stage_step=0,
            engine_step=0,
            state_sha256=clone,
        )
        arms.append(
            {
                "arm": arm,
                "bits": list(repro.ARM_BITS[arm]),
                "clone_sha256": clone,
                "writer": {
                    "operation_count": 0,
                    "expected_operation_count": 240,
                    "total_writer_engine_steps": 0,
                    "active_writer_steps": 0,
                    "settle_steps": 0,
                    "operation_digest": _sha(f"empty-operation:{arm}"),
                    "postwriter_state_sha256": clone,
                    "sham_reference_exact": True if arm == "H00" else None,
                },
                "writer_records": [prewriter],
                "common_deep_step": None,
                "deep_complete": False,
                "deep_joint": None,
                "turnover_records": [],
                "access_regimes": [],
                "arm_complete": False,
                "first_failure": failure,
            }
        )
    a, b, sentinel = repro.WORLD_ASSIGNMENTS[world_id]
    return {
        "schema": repro.RAW_SCHEMA,
        "mission": repro.MISSION,
        "mode": repro.MODE,
        "phase0_commit": repro.PHASE0_COMMIT,
        "world_id": world_id,
        "sequence_index": sequence,
        "manifest_sha256": _sha("manifest"),
        "plan_sha256": repro.EXPECTED_PLAN_SHA256,
        "previous_record_sha256": previous_record_sha256,
        "contract_bindings": _bindings(),
        "assignment": {"target_A": a, "target_B": b, "sentinel": sentinel},
        "prewriter_state_sha256": clone,
        "prewriter_clone_sha256": [clone] * 4,
        "writer": _root_writer(),
        "common_deep_step": None,
        "history_arms": arms,
        "world_complete": False,
        "first_failure": failure,
    }


@pytest.fixture(scope="module")
def schema_document() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _cache_exact_disk_calculations(monkeypatch: pytest.MonkeyPatch) -> None:
    original = repro.disk_cells
    cache: dict[tuple[tuple[float, ...], float, tuple[int, int]], frozenset[int]] = {}

    def cached(
        center: tuple[float, float] | list[float],
        radius: float,
        shape: tuple[int, int] = repro.GRID_SHAPE,
    ) -> frozenset[int]:
        key = (tuple(float(value) for value in center), float(radius), tuple(shape))
        if key not in cache:
            cache[key] = original(center, radius, shape)
        return cache[key]

    monkeypatch.setattr(repro, "disk_cells", cached)


def _declared_frozenset(path: Path, name: str) -> frozenset[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        assert isinstance(node.value, ast.Call) and len(node.value.args) == 1
        return frozenset(ast.literal_eval(node.value.args[0]))
    raise AssertionError(f"missing {name}")


def test_reproducer_import_closure_is_standard_library_only() -> None:
    source_path = Path(repro.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "__import__"
    assert imported_roots <= set(sys.stdlib_module_names) | {"__future__"}


def test_frozen_binding_sets_match_runner_without_importing_it() -> None:
    assert repro.EXPECTED_INPUT_PATHS == _declared_frozenset(RUNNER_PATH, "EXPECTED_INPUT_PATHS")
    assert repro.EXPECTED_CODE_PATHS == _declared_frozenset(RUNNER_PATH, "EXPECTED_CODE_PATHS")
    assert len(repro.EXPECTED_INPUT_PATHS) == 7
    assert len(repro.EXPECTED_CODE_PATHS) == 51


def test_final_schema_is_closed_and_freezes_exact_binding_cardinality(
    schema_document: dict[str, Any],
) -> None:
    repro.validate_schema_document(schema_document)
    bindings = schema_document["properties"]["contract_bindings"]
    assert bindings["minItems"] == bindings["maxItems"] == 58
    assert bindings["uniqueItems"] is True
    for coordinate in schema_document["$defs"]["centroid"]["prefixItems"]:
        assert coordinate["minimum"] == 0.0
        assert coordinate["exclusiveMaximum"] == 64.0
    isolation_step = schema_document["$defs"]["isolation_failure"]["properties"][
        "schedule_step"
    ]
    assert isolation_step == {"type": "integer", "minimum": 0, "maximum": 80}
    opened = copy.deepcopy(schema_document)
    opened["$defs"]["step_record"]["additionalProperties"] = True
    with pytest.raises(repro.RawContractError, match="SCHEMA_OBJECT_NOT_CLOSED"):
        repro.validate_schema_document(opened)


def test_complete_synthetic_world_passes_and_respects_assignment_order() -> None:
    shard = _pass_shard()
    turnover = shard["history_arms"][0]["turnover_records"][-1]
    deep = shard["history_arms"][0]["deep_joint"]
    assert deep[1]["target"] == "B"
    assert deep[1]["material_retention"] == turnover["material_retention"][2]
    assert deep[1]["material_retention"] != turnover["material_retention"][1]
    summary = repro.validate_world_shard(shard, expected_sequence=0)
    assert summary.derived_complete is True
    assert summary.value["access_regime_count"] == 32
    assert summary.value["step_records_checked"] == 3560
    assert summary.value["first_failure"] is None


def test_access_regimes_require_one_exact_standardized_clone_seed() -> None:
    shard = copy.deepcopy(_pass_shard())
    regime = shard["history_arms"][0]["access_regimes"][3]
    regime["records"][0]["state_sha256"] = _sha("different-standardized-seed")
    with pytest.raises(repro.RawContractError, match="STANDARDIZED_CLONE_SEED_MISMATCH"):
        repro.validate_world_shard(shard, expected_sequence=0)


def test_exact_isolation_accepts_fail_closed_schedule_zero_seed_gate() -> None:
    evidence = _isolation("A")
    evidence["left_first_failure"] = {
        "schedule_step": 0,
        "reasons": ["CLAMP_COLLAR_PARTNER_INTRUSION"],
    }
    evidence["bit_exact_isolation"] = False
    assert repro._validate_isolation_evidence(
        evidence,
        recipient="A",
        context="schedule-zero-isolation",
    ) is False


@pytest.mark.parametrize("centroid", [(-0.01, 0.0), (64.0, 0.0), (0.0, 64.0)])
def test_centroid_primitive_requires_canonical_grid_range(
    centroid: tuple[float, float],
) -> None:
    with pytest.raises(repro.RawContractError, match="CENTROID_OUT_OF_CANONICAL_RANGE"):
        repro._read_centroid(list(centroid), "centroid")


def test_rho_weighted_centroid_is_accepted_as_a_raw_primitive() -> None:
    row = copy.deepcopy(
        _step_record(50002, stage="PREWRITER", stage_step=0, engine_step=0)
    )
    physical = {index: tuple(track["centroid"]) for index, track in enumerate(row["tracks"])}
    physical[0] = (8.25, 8.0)
    row["components"][0]["centroid"] = list(physical[0])
    row["tracks"][0]["centroid"] = list(physical[0])
    component_masks = {
        item["component_id"]: repro.decode_mask(item["mask"]) for item in row["components"]
    }
    prior_masks = {
        item["tracker_id"]: repro.decode_mask(item["body_mask"]) for item in row["tracks"]
    }
    row["association_edges"] = _association_edges(
        prior_masks,
        physical,
        component_masks,
        physical,
        {index: index for index in range(3)},
    )
    a_tracker, b_tracker, _sentinel = repro.WORLD_ASSIGNMENTS[50002]
    distance = repro.toroidal_distance(physical[a_tracker], physical[b_tracker])
    row["pair_geometry"].update(
        {
            "centroid_A": list(physical[a_tracker]),
            "centroid_B": list(physical[b_tracker]),
            "distance": distance,
            "minimum_core_gap": distance - 2.0 * repro.CORE_RADIUS,
            "minimum_halo_gap": distance - 2.0 * repro.HALO_RADIUS,
        }
    )
    binary_centroid = repro.periodic_centroid(prior_masks[0])
    assert binary_centroid != pytest.approx(physical[0])
    summary = repro.validate_step_record(row, world_id=50002, context="weighted")
    assert summary.gate_pass is True


def test_sentinel_switch_sets_kill_reason_and_forces_deep_gate_false() -> None:
    row = copy.deepcopy(
        _step_record(
            50002,
            stage="TURNOVER",
            stage_step=1,
            engine_step=1,
            material_retention=RETENTIONS,
            component_switch=True,
        )
    )
    current_masks = {
        item["tracker_id"]: repro.decode_mask(item["body_mask"]) for item in row["tracks"]
    }
    current_centroids = {
        item["tracker_id"]: tuple(item["centroid"]) for item in row["tracks"]
    }
    # World 50002 has A=0, B=2, sentinel=1.  The sentinel's prior mask fits
    # A's selected component better than A's own prior mask; A/B-only logic
    # would miss this switch.
    prior_masks = {0: current_masks[1], 1: current_masks[0], 2: current_masks[2]}
    prior_centroids = {0: current_centroids[1], 1: current_centroids[0], 2: current_centroids[2]}
    component_masks = {
        item["component_id"]: repro.decode_mask(item["mask"]) for item in row["components"]
    }
    component_centroids = {
        item["component_id"]: tuple(item["centroid"]) for item in row["components"]
    }
    row["association_edges"] = _association_edges(
        prior_masks,
        prior_centroids,
        component_masks,
        component_centroids,
        {index: index for index in range(3)},
    )
    assert row["kill_reasons"] == ["PAIR_IDENTITY_SWITCH"]
    assert row["deep_material_gate"] is False
    summary = repro.validate_step_record(
        row,
        world_id=50002,
        context="sentinel-switch",
        prior_track_masks=prior_masks,
        prior_track_centroids=prior_centroids,
    )
    assert summary.gate_pass is False
    tampered = copy.deepcopy(row)
    tampered["deep_material_gate"] = True
    with pytest.raises(repro.RawContractError, match="deep_material_gate:DERIVED_MISMATCH"):
        repro.validate_step_record(
            tampered,
            world_id=50002,
            context="sentinel-switch-tampered",
            prior_track_masks=prior_masks,
            prior_track_centroids=prior_centroids,
        )


def test_legitimate_failure_shard_reproduces_without_inventing_zeros(
    schema_document: dict[str, Any],
) -> None:
    shard = _failure_shard()
    summary = repro.validate_world_shard(shard, expected_sequence=0)
    assert summary.derived_complete is False
    assert summary.value["step_records_checked"] == 4
    assert summary.value["first_failure"]["reasons"] == ["WRITER_SCHEDULE_INCOMPLETE"]
    canonical = repro.canonical_json_bytes(shard)
    first = repro.reproduce_shards([(shard, canonical)], schema_document=schema_document)
    second = repro.reproduce_shards([(shard, canonical)], schema_document=schema_document)
    assert repro.canonical_json_bytes(first) == repro.canonical_json_bytes(second)
    assert first["reproduction_status"] == "INCOMPLETE_OR_FAILED"
    assert first["ordered_prefix_complete"] is False
    assert first["all_worlds_mechanically_complete"] is False
    assert first["source_records"][0]["derived_world_complete"] is False


@pytest.mark.parametrize("tamper", ["plan", "binding", "geometry"])
def test_reproducer_rejects_binding_and_mechanical_tamper(tamper: str) -> None:
    shard = copy.deepcopy(_failure_shard())
    if tamper == "plan":
        shard["plan_sha256"] = _sha("different-plan")
        match = "FROZEN_PLAN_MISMATCH"
    elif tamper == "binding":
        shard["contract_bindings"].pop()
        match = "FROZEN_SET_MISMATCH"
    else:
        shard["history_arms"][0]["writer_records"][0]["pair_geometry"]["distance"] += 0.5
        match = "pair_geometry.distance:MISMATCH"
    with pytest.raises(repro.RawContractError, match=match):
        repro.validate_world_shard(shard, expected_sequence=0)


def test_assignment_order_retention_tamper_is_rejected() -> None:
    shard = copy.deepcopy(_pass_shard())
    arm = shard["history_arms"][0]
    arm["deep_joint"][1]["material_retention"] = arm["turnover_records"][-1]["material_retention"][1]
    with pytest.raises(repro.RawContractError, match=r"deep_joint\[1\]:RETENTION_MISMATCH"):
        repro.validate_world_shard(shard, expected_sequence=0)


def test_deep_joint_centroid_uses_the_canonical_grid_range() -> None:
    shard = copy.deepcopy(_pass_shard())
    shard["history_arms"][0]["deep_joint"][0]["phenotype_descriptor"][
        "centroid"
    ][0] = 64.0
    with pytest.raises(repro.RawContractError, match="CENTROID_OUT_OF_CANONICAL_RANGE"):
        repro.validate_world_shard(shard, expected_sequence=0)


@pytest.mark.parametrize(
    "forbidden",
    ["Y_A", "c_ab", "FeEdInG_Result", "OutcomeSummary", "scientific_response"],
)
def test_recursive_outcome_firewall_rejects_every_depth_and_case(forbidden: str) -> None:
    with pytest.raises(repro.RawContractError, match="OUTCOME_FIREWALL_FORBIDDEN_KEYS"):
        repro.assert_outcome_free({"mechanics": [{"nested": {forbidden: 1}}]})
    repro.assert_outcome_free(
        {"physical_c_field": 1, "component_switch": False, "identity_label": "A", "pair_geometry": {}}
    )


def test_strict_loader_rejects_duplicate_keys_and_noncanonical_bytes(tmp_path: Path) -> None:
    with pytest.raises(repro.RawContractError, match="DUPLICATE_JSON_KEY"):
        repro.strict_json_loads(b'{"schema":1,"schema":2}\n')
    shard = _failure_shard()
    pretty = json.dumps(shard, indent=2, sort_keys=True).encode("utf-8")
    path = tmp_path / "000_50002.json"
    path.write_bytes(pretty)
    with pytest.raises(repro.RawContractError, match="RAW_SHARD_NOT_CANONICAL_JSON"):
        repro.read_raw_shard(path)


def test_deterministic_gzip_and_hash_chain_tamper(
    tmp_path: Path,
    schema_document: dict[str, Any],
) -> None:
    first = _failure_shard()
    first_canonical = repro.canonical_json_bytes(first)
    compressed_a = gzip.compress(first_canonical, compresslevel=9, mtime=0)
    compressed_b = gzip.compress(first_canonical, compresslevel=9, mtime=0)
    assert compressed_a == compressed_b
    path = tmp_path / "000_50002.json.gz"
    path.write_bytes(compressed_a)
    loaded, canonical = repro.read_raw_shard(path)
    assert loaded == first
    assert canonical == first_canonical

    second = _failure_shard(
        sequence=1,
        previous_record_sha256=repro.sha256_bytes(first_canonical),
    )
    second_canonical = repro.canonical_json_bytes(second)
    result = repro.reproduce_shards(
        [(first, first_canonical), (second, second_canonical)],
        schema_document=schema_document,
    )
    assert len(result["source_records"]) == 2
    broken = copy.deepcopy(second)
    broken["previous_record_sha256"] = _sha("wrong-predecessor")
    with pytest.raises(repro.RawContractError, match="PREDECESSOR_HASH_MISMATCH"):
        repro.reproduce_shards(
            [(first, first_canonical), (broken, repro.canonical_json_bytes(broken))],
            schema_document=schema_document,
        )


def test_cli_reproduces_byte_identically_without_repository_on_pythonpath(tmp_path: Path) -> None:
    script = tmp_path / "reproduce.py"
    schema = tmp_path / "schema.json"
    shard_path = tmp_path / "000_50002.json.gz"
    shutil.copyfile(Path(repro.__file__), script)
    shutil.copyfile(SCHEMA_PATH, schema)
    canonical = repro.canonical_json_bytes(_failure_shard())
    shard_path.write_bytes(gzip.compress(canonical, compresslevel=9, mtime=0))
    outputs = [tmp_path / "first.json", tmp_path / "second.json"]
    stdout: list[str] = []
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path / "forbidden-pythonpath")
    for output in outputs:
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(script),
                "--schema",
                str(schema),
                "--shard",
                str(shard_path),
                "--output",
                str(output),
            ],
            cwd=tmp_path,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        assert completed.stderr == ""
        stdout.append(completed.stdout.strip())
    assert outputs[0].read_bytes() == outputs[1].read_bytes()
    expected_hash = hashlib.sha256(outputs[0].read_bytes()).hexdigest()
    assert stdout == [expected_hash, expected_hash]
    result = repro.strict_json_loads(outputs[0].read_bytes())
    assert result["reproduction_status"] == "INCOMPLETE_OR_FAILED"
    repro.assert_outcome_free(result)
