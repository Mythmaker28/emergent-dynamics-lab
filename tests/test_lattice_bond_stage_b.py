"""Code-only qualification of the frozen Stage-B runner utilities."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import LatticeBondEngine, LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond.stage_b import (
    InstrumentationInvalid,
    ManifestError,
    NumericalInvalid,
    REGIMES,
    SCHEMA,
    _durable_replace,
    _expected_physics_layout,
    _npz_inventory,
    _reference_error,
    _verify_partial_root,
    _write_json,
    canonical_json_bytes,
    classify_family,
    enumerate_worlds,
    hash_uniform,
    load_and_validate_manifest,
    sha256_file,
    validate_manifest_structure,
)


def _manifest():
    return {
        "law_family": {"laws": [{"law_id": "L00"}, {"law_id": "L01"}]},
        "initial_conditions": [{"ic_id": "soup"}, {"ic_id": "compact"}],
        "execution": {"replicates_per_law_ic": 3},
        "region_rule": {"minimum_candidate_worlds_per_ic": 2},
        "runtime_manifest_sha256": "synthetic",
    }


def _structural_manifest():
    spec = asdict(LatticeBondSpec())
    fixed_spec = dict(spec)
    fixed_spec.pop("kappa_m")
    manifest = {
        "schema": SCHEMA,
        "accepted_parent": "b0dbab7674816ebdf3f3f911694b2744ca4bfc76",
        "b0_commit": "93f4a42d8972d2d4b9f8da6f1dc3c8161dc3c045",
        "namespace": "results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV",
        "extension_policy": "NO_EXTENSION_NO_REPLACEMENT_NO_RETRY",
        "law_family": {
            "sampling_rule": "full_cartesian_discrete_grid_in_declared_factor_order",
            "factors": [{"name": "kappa_m", "levels": [spec["kappa_m"]], "closed_range": [spec["kappa_m"], spec["kappa_m"]]}],
            "fixed_spec": fixed_spec,
            "laws": [{"law_id": "L000", "spec": spec}],
        },
        "initial_conditions": [
            {
                "ic_id": "soup",
                "kind": "bounded_hash_soup",
                "m_low": 0.2,
                "m_high": 0.6,
                "n_low": 0.6,
                "n_high": 0.9,
            },
            {
                "ic_id": "compact",
                "kind": "generic_compact_fluctuations",
                "blob_count": 3,
                "m_base_low": 0.1,
                "m_base_high": 0.2,
                "n_low": 0.6,
                "n_high": 0.9,
                "sigma_low": 1.0,
                "sigma_high": 2.0,
                "amplitude_low": 0.3,
                "amplitude_high": 0.5,
                "m_cap": 0.9,
            },
        ],
        "execution": {
            "sample_cadence": 1,
            "horizon_steps": 10,
            "shape": [4, 4],
            "replicates_per_law_ic": 3,
            "backend": "vectorized_with_every_step_reference_audit",
            "world_count": 6,
        },
        "detector": {"matter_threshold": 0.5, "min_cells": 1},
        "tracker": {
            "max_centroid_displacement": 3.0,
            "max_area_ratio": 3.0,
            "dilation_radius": 1,
            "unique_score_margin": 1e-12,
        },
        "classifier": {
            "classes": list(REGIMES),
            "thresholds": {
                "min_persistence_frames": 5,
                "max_area_fraction": 0.25,
                "min_bounded_fraction": 0.9,
                "min_activity_per_mass": 1e-6,
                "min_energy_throughput_per_mass": 1e-7,
                "min_turnover_fraction": 0.5,
                "min_post_turnover_frames": 2,
            },
        },
        "region_rule": {"minimum_candidate_worlds_per_ic": 2},
        "initializer": {
            "algorithm": "sha256_first_u64_big_endian_div_2pow64",
            "namespace": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-FRESH-DEV-v1",
        },
    }
    manifest["execution"]["world_ids"] = [world["world_id"] for world in enumerate_worlds(manifest)]
    return manifest


def test_hash_uniform_is_stateless_bounded_and_coordinate_sensitive():
    values = [hash_uniform("fixture", "m", y, x) for y in range(4) for x in range(4)]
    assert values == [hash_uniform("fixture", "m", y, x) for y in range(4) for x in range(4)]
    assert all(0.0 <= value < 1.0 for value in values)
    assert len(set(values)) == len(values)


def test_canonical_json_is_sorted_finite_and_terminal_newline():
    assert canonical_json_bytes({"b": 1, "a": 2}) == b'{"a":2,"b":1}\n'
    with pytest.raises(ValueError):
        canonical_json_bytes({"bad": float("nan")})


def test_world_enrollment_is_complete_unique_and_ordered():
    worlds = enumerate_worlds(_manifest())
    assert len(worlds) == 12
    assert len({world["world_id"] for world in worlds}) == 12
    assert worlds[0]["world_id"] == "L00__soup__r00"
    assert worlds[-1]["world_id"] == "L01__compact__r02"


def test_region_rule_requires_replication_in_both_ic_classes():
    manifest = _manifest()
    rows = []
    for world in enumerate_worlds(manifest):
        candidate = world["law_id"] == "L00" and world["replicate"] < 2
        rows.append(
            {
                **world,
                "status": "COMPLETE",
                "regime": "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if candidate else "DISSOLVED",
                "candidate_track_ids": [0] if candidate else [],
            }
        )
    result = classify_family(rows, manifest)
    assert result["candidate_regions"] == ["L00"]
    assert result["disposition"] == "DEV_REGIME_CANDIDATE"
    assert all(set(item["counts"]) == set(REGIMES) for region in result["atlas"] for item in region["per_ic"])


def test_single_world_or_single_ic_cannot_make_candidate_region():
    manifest = _manifest()
    rows = []
    for world in enumerate_worlds(manifest):
        candidate = world["law_id"] == "L00" and world["ic_id"] == "soup"
        rows.append(
            {
                **world,
                "status": "COMPLETE",
                "regime": "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if candidate else "DISSOLVED",
                "candidate_track_ids": [0] if candidate else [],
            }
        )
    result = classify_family(rows, manifest)
    assert result["candidate_regions"] == []
    assert result["disposition"] == "DEV_FEASIBILITY_FAIL"


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("NUMERICAL_INVALID", "MANIPULATION_OR_NUMERICAL_INVALID"),
        ("INSTRUMENTATION_INVALID", "REVISE_INSTRUMENTATION"),
    ],
)
def test_family_failure_escalation_is_frozen(status, expected):
    manifest = _manifest()
    rows = []
    for index, world in enumerate(enumerate_worlds(manifest)):
        rows.append(
            {
                **world,
                "status": status if index == 0 else "COMPLETE",
                "regime": "TRACKING_UNRESOLVED" if index == 0 else "DISSOLVED",
                "candidate_track_ids": [],
            }
        )
    assert classify_family(rows, manifest)["disposition"] == expected


def test_raw_schema_is_valid_json_and_forbids_online_input_to_reproducer():
    schema = json.loads(
        open("docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json", encoding="utf-8").read()
    )
    assert schema["world_files"]["online.json"]["independent_reproducer_access"] == "FORBIDDEN"
    assert "engine.py" in schema["independent_reproduction_forbidden_inputs"]


def test_manifest_structure_is_closed_and_numeric_fields_fail_closed():
    manifest = _structural_manifest()
    validate_manifest_structure(manifest)
    for mutation in (
        lambda value: value["execution"].__setitem__("horizon_steps", 0),
        lambda value: value["execution"].__setitem__("replicates_per_law_ic", 2.5),
        lambda value: value["region_rule"].__setitem__("minimum_candidate_worlds_per_ic", 4),
        lambda value: value["classifier"]["thresholds"].__setitem__("min_activity_per_mass", float("nan")),
        lambda value: value["initial_conditions"][0].__setitem__("m_high", 1.1),
        lambda value: value.pop("initializer"),
    ):
        candidate = json.loads(json.dumps(manifest))
        mutation(candidate)
        with pytest.raises((ManifestError, ValueError)):
            validate_manifest_structure(candidate)
    inadmissible = json.loads(json.dumps(manifest))
    inadmissible["law_family"]["fixed_spec"]["m_max"] = 0.3
    inadmissible["law_family"]["laws"][0]["spec"]["m_max"] = 0.3
    with pytest.raises(ManifestError, match="initial matter"):
        validate_manifest_structure(inadmissible)


def test_manifest_missing_seal_and_noncanonical_file_fail_before_source_access(tmp_path):
    manifest = _structural_manifest()
    missing = tmp_path / "missing.json"
    missing.write_bytes(canonical_json_bytes(manifest))
    with pytest.raises(ManifestError, match="seal"):
        load_and_validate_manifest(missing)
    manifest["manifest_sha256_excluding_field"] = "0" * 64
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with pytest.raises(ManifestError, match="canonical"):
        load_and_validate_manifest(pretty)


def test_reference_audit_rejects_nonfinite_ledger_values():
    spec = LatticeBondSpec()
    state = LatticeBondState(
        np.full((2, 2), 0.4, dtype=np.float64),
        np.full((2, 2), 0.8, dtype=np.float64),
        np.zeros((2, 2, 2), dtype=np.float64),
    )
    result = LatticeBondEngine(spec).step(state)
    bad = replace(result, ledger=replace(result.ledger, matter_residual=float("nan")))
    with pytest.raises(NumericalInvalid, match="nonfinite"):
        _reference_error(bad, result)
    wrong_clock = replace(result, state=replace(result.state, step=result.state.step + 7))
    with pytest.raises(NumericalInvalid, match="clock"):
        _reference_error(wrong_clock, result)


def test_classification_rejects_duplicate_missing_extra_unknown_and_relabelled_rows():
    manifest = _manifest()
    valid = [
        {**world, "status": "COMPLETE", "regime": "DISSOLVED", "candidate_track_ids": []}
        for world in enumerate_worlds(manifest)
    ]
    for invalid in (
        valid[:-1],
        valid + [dict(valid[0])],
        [{**row, "regime": "UNKNOWN"} if index == 0 else row for index, row in enumerate(valid)],
        [{**row, "candidate_track_ids": [0]} if index == 0 else row for index, row in enumerate(valid)],
        [{**row, "status": "NUMERICAL_INVALID"} if index == 0 else row for index, row in enumerate(valid)],
    ):
        with pytest.raises(InstrumentationInvalid):
            classify_family(invalid, manifest)


def test_atomic_replace_refuses_existing_target(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    with pytest.raises(FileExistsError):
        _durable_replace(source, target)
    assert source.is_dir() and target.is_dir()


def test_partial_root_verifier_binds_exact_terminal_shard_inventory(tmp_path):
    spec = asdict(LatticeBondSpec())
    manifest = {
        "law_family": {"laws": [{"law_id": "L00", "spec": spec}]},
        "initial_conditions": [{"ic_id": "soup"}],
        "execution": {"replicates_per_law_ic": 1, "horizon_steps": 1, "shape": [2, 2]},
    }
    world = enumerate_worlds(manifest)[0]
    shard = tmp_path / world["world_id"]
    shard.mkdir()
    layout = _expected_physics_layout(manifest)
    physics = {
        name: np.zeros(shape, dtype=dtype)
        for name, (shape, dtype) in layout.items()
    }
    physics["state_step"] = np.arange(2, dtype=np.int64)
    physics["deterministic_replay_equal"][:] = 1
    physics["ledger__matter_scale"][:] = 1.0
    physics["ledger__resource_scale"][:] = 1.0
    np.savez_compressed(shard / "physics.npz", **physics)
    online = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-ONLINE-v1",
        "world": world,
        "components": [[]],
        "association_edges": [],
        "events": [],
        "assignments": [],
        "component_diagnostics": [],
        "track_observations": [],
        "tracer_rows": [],
        "world_metrics": {},
        "regime": "EMPTY_OR_GAS",
        "candidate_track_ids": [],
    }
    _write_json(shard / "online.json", online)
    record = {
        "schema": "INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B1-SHARD-v1",
        "world": world,
        "status": "COMPLETE",
        "files": {
            name: {"sha256": sha256_file(shard / name), "bytes": (shard / name).stat().st_size}
            for name in ("physics.npz", "online.json")
        },
        "physics_inventory": _npz_inventory(shard / "physics.npz"),
        "row_counts": {
            "state_rows": 2,
            "ledger_rows": 1,
            "component_rows": 0,
            "association_edge_rows": 0,
            "event_rows": 0,
            "track_observation_rows": 0,
            "tracer_rows": 0,
        },
    }
    _write_json(shard / "shard_manifest.json", record)
    assert _verify_partial_root(tmp_path, manifest)[0]["status"] == "COMPLETE"
    physics["vector_reference_max_error"][:] = 1.0
    np.savez_compressed(shard / "physics.npz", **physics)
    record["files"]["physics.npz"] = {
        "sha256": sha256_file(shard / "physics.npz"),
        "bytes": (shard / "physics.npz").stat().st_size,
    }
    record["physics_inventory"] = _npz_inventory(shard / "physics.npz")
    _write_json(shard / "shard_manifest.json", record)
    with pytest.raises(InstrumentationInvalid, match="reference error"):
        _verify_partial_root(tmp_path, manifest)
    physics["vector_reference_max_error"][:] = 0.0
    (shard / "physics.npz").write_bytes(b"not-an-npz")
    record["files"]["physics.npz"] = {
        "sha256": sha256_file(shard / "physics.npz"),
        "bytes": (shard / "physics.npz").stat().st_size,
    }
    _write_json(shard / "shard_manifest.json", record)
    with pytest.raises(InstrumentationInvalid, match="physics"):
        _verify_partial_root(tmp_path, manifest)
    np.savez_compressed(shard / "physics.npz", **physics)
    record["files"]["physics.npz"] = {
        "sha256": sha256_file(shard / "physics.npz"),
        "bytes": (shard / "physics.npz").stat().st_size,
    }
    record["physics_inventory"] = _npz_inventory(shard / "physics.npz")
    _write_json(shard / "shard_manifest.json", record)
    (shard / "extra.bin").write_bytes(b"unbound")
    with pytest.raises(InstrumentationInvalid, match="inventory"):
        _verify_partial_root(tmp_path, manifest)
