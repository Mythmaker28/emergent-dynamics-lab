"""Code-only qualification of the frozen Stage-B runner utilities."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import platform
from pathlib import Path
import sys

import numpy as np
import pytest

from edlab.substrates.lattice_bond import LatticeBondEngine, LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond import stage_b_reproduce as raw_reproduce
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    RegimeThresholds,
    TrackMetrics,
    TrackerSpec,
    WorldMetrics,
    advance_passive_tracer,
    classify_regime,
    detect_components,
    track_components,
)
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


def _parity_state(mask: np.ndarray, frame: int, *, weights: np.ndarray | None = None) -> LatticeBondState:
    matter = np.where(mask, 0.8, 0.1).astype(np.float64) if weights is None else weights.astype(np.float64)
    return LatticeBondState(
        matter,
        np.full(mask.shape, 0.7, dtype=np.float64),
        np.zeros((2, *mask.shape), dtype=np.float64),
        frame,
    )


def _parity_frames(masks: list[np.ndarray], tracker: TrackerSpec):
    detector = DetectorSpec(matter_threshold=0.5, min_cells=1)
    raw_detector = raw_reproduce.DetectorConfig(matter_threshold=0.5, min_cells=1)
    production = [
        detect_components(_parity_state(mask, frame), detector, frame=frame)
        for frame, mask in enumerate(masks)
    ]
    independent = [
        raw_reproduce.detect_components(_parity_state(mask, frame).m, raw_detector)
        for frame, mask in enumerate(masks)
    ]
    raw_tracker = raw_reproduce.TrackerConfig(
        dilation_radius=tracker.dilation_radius,
        max_centroid_displacement=tracker.max_centroid_displacement,
        max_area_ratio=tracker.max_area_ratio,
        unique_score_margin=tracker.unique_score_margin,
    )
    return production, independent, raw_tracker


def _raw_manifest_contract(manifest: dict) -> raw_reproduce.ManifestContract:
    worlds = tuple(
        raw_reproduce.WorldEnrollment(**world)
        for world in enumerate_worlds(manifest)
    )
    thresholds = raw_reproduce.Thresholds(3, 0.25, 0.9, 0.1, 0.1, 0.6, 1)
    return raw_reproduce.ManifestContract(
        source=manifest,
        sha256=manifest["runtime_manifest_sha256"],
        laws=tuple(
            raw_reproduce.LawContract(law["law_id"], {"dt": 0.05}, 0.05)
            for law in manifest["law_family"]["laws"]
        ),
        horizon_steps=4,
        shape=(4, 4),
        replicates_per_law_ic=manifest["execution"]["replicates_per_law_ic"],
        detector=raw_reproduce.DetectorConfig(0.5, 1),
        tracker=raw_reproduce.TrackerConfig(1, 3.0, 3.0, 1e-12),
        thresholds=thresholds,
        regimes=tuple(REGIMES),
        ic_order=tuple(item["ic_id"] for item in manifest["initial_conditions"]),
        worlds=worlds,
        minimum_candidate_worlds_per_ic=manifest["region_rule"]["minimum_candidate_worlds_per_ic"],
    )


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


def test_independent_detector_matches_weighted_periodic_geometry_exactly():
    shape = (5, 7)
    weights = np.full(shape, 0.1, dtype=np.float64)
    occupied = {(2, x) for x in range(shape[1])} | {(4, 6), (4, 0), (4, 1)}
    for index, (y, x) in enumerate(sorted(occupied)):
        weights[y, x] = 0.55 + 0.01 * index
    mask = weights >= 0.5
    production = detect_components(
        _parity_state(mask, 7, weights=weights),
        DetectorSpec(0.5, 1),
        frame=7,
    )
    independent = raw_reproduce.detect_components(
        weights,
        raw_reproduce.DetectorConfig(0.5, 1),
    )
    assert len(production) == len(independent)
    for left, right in zip(production, independent, strict=True):
        assert tuple(divmod(cell, shape[1]) for cell in left.cells) == right.cells
        assert np.array_equal(left.mask(), right.mask)
        assert (
            left.index,
            left.area,
            left.mass,
            left.centroid_y,
            left.centroid_x,
            left.radius_gyration,
            left.wraps_y,
            left.wraps_x,
        ) == (
            right.index,
            right.area,
            right.mass,
            right.centroid[0],
            right.centroid[1],
            right.radius_gyration,
            right.wraps_y,
            right.wraps_x,
        )


@pytest.mark.parametrize("scenario", ["split", "merge", "tie", "collapse"])
def test_independent_tracker_matches_split_merge_tie_and_collapse(scenario):
    shape = (10, 12)

    def mask(cells):
        value = np.zeros(shape, dtype=bool)
        for y, x in cells:
            value[y % shape[0], x % shape[1]] = True
        return value

    joined = mask({(4, x) for x in range(3, 8)})
    separated = mask({(4, 3), (4, 4), (4, 6), (4, 7)})
    tracker = TrackerSpec(3.0, 4.0, 1, 1e-12)
    if scenario == "split":
        masks = [joined, separated]
    elif scenario == "merge":
        masks = [separated, joined]
    elif scenario == "tie":
        masks = [mask({(4, 3), (4, 7)}), mask({(3, 5), (5, 5)})]
        tracker = TrackerSpec(5.0, 3.0, 3, 1e-12)
    else:
        wide_separation = mask(
            {(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)}
        )
        collapsed = wide_separation.copy()
        collapsed[4, 4:7] = True
        masks = [wide_separation, collapsed, wide_separation]

    frames, raw_frames, raw_tracker = _parity_frames(masks, tracker)
    production = track_components(frames, tracker)
    independent = raw_reproduce.track_components(raw_frames, shape, raw_tracker)

    production_tracks = [
        (
            track.track_id,
            tuple((point.frame, point.component_index) for point in track.points),
            track.parent_track_ids,
            track.unresolved,
        )
        for track in production.tracks
    ]
    independent_tracks = [
        (
            track.track_id,
            tuple((point.frame, point.component_index) for point in track.points),
            track.parent_ids,
            track.unresolved,
        )
        for track in independent.tracks
    ]
    assert independent_tracks == production_tracks
    production_unresolved = any(
        track.unresolved for track in production.tracks
    ) or any(event.kind == "TRACKING_UNRESOLVED" for event in production.events)
    assert independent.unresolved == production_unresolved
    event_name = {
        "split": "SPLIT",
        "merge": "MERGE",
        "tie": "TRACKING_UNRESOLVED",
        "collapse": "TRACKING_UNRESOLVED",
    }[scenario]
    assert any(event.kind == event_name for event in production.events)
    assert any(event["event"] == event_name for event in independent.events)


def test_independent_cohort_update_is_operation_exact_with_production():
    spec = LatticeBondSpec(dt=0.05)
    matter = np.array(
        [[0.21, 0.74, 0.43, 0.68], [0.59, 0.32, 0.81, 0.27], [0.48, 0.66, 0.37, 0.72]],
        dtype=np.float64,
    )
    state = LatticeBondState(
        matter,
        np.array(
            [[0.92, 0.61, 0.73, 0.84], [0.67, 0.88, 0.56, 0.79], [0.63, 0.75, 0.91, 0.58]],
            dtype=np.float64,
        ),
        np.linspace(0.05, 0.9, 24, dtype=np.float64).reshape(2, 3, 4),
    )
    step = LatticeBondEngine(spec).step(state)
    cohort = np.where(matter >= 0.4, 0.37 * matter, 0.0).astype(np.float64)
    production = advance_passive_tracer(
        cohort,
        matter,
        step.ledger.matter_forward,
        step.ledger.matter_reverse,
        step.state.m,
        spec.dt,
    )
    independent = raw_reproduce._advance_cohort(
        cohort,
        matter,
        step.state.m,
        step.ledger.matter_forward,
        step.ledger.matter_reverse,
        spec.dt,
        0,
    )
    assert np.array_equal(independent, production)


@pytest.mark.parametrize("expected", list(REGIMES))
def test_independent_classifier_matches_all_nine_precedence_paths(expected):
    production_thresholds = RegimeThresholds(3, 0.25, 0.9, 0.1, 0.1, 0.6, 1)
    raw_thresholds = raw_reproduce.Thresholds(3, 0.25, 0.9, 0.1, 0.1, 0.6, 1)
    bounded_mask = np.zeros((4, 4), dtype=bool)
    bounded_mask[0, 0] = True
    bounded = raw_reproduce.Component(0, ((0, 0),), bounded_mask, 1, 0.8, (0.0, 0.0), 0.0, False, False)
    winding = raw_reproduce.Component(0, ((0, 0),), bounded_mask, 1, 0.8, (0.0, 0.0), 0.0, False, True)

    metric_values = {
        "track_id": 0,
        "observed_frames": 3,
        "span_frames": 3,
        "maximum_area_fraction": 0.1,
        "bounded_fraction": 1.0,
        "percolated_fraction": 0.0,
        "mean_activity_per_mass": 0.2,
        "mean_energy_throughput_per_mass": 0.2,
        "maximum_turnover_fraction": 0.7,
        "post_turnover_frames": 1,
        "unresolved": False,
    }
    frames = [[bounded]]
    tracking_unresolved = expected == "TRACKING_UNRESOLVED"
    any_active_unbounded = expected == "ACTIVE_UNBOUNDED"
    any_turnover_without_persistence = expected == "TURNOVER_WITHOUT_PERSISTENCE"
    if expected in {"ACTIVE_UNBOUNDED", "PERCOLATED"}:
        frames = [[winding]]
        metric_values["percolated_fraction"] = 1.0
        metric_values["bounded_fraction"] = 0.0
        if expected == "PERCOLATED":
            metric_values["mean_activity_per_mass"] = 0.0
            metric_values["mean_energy_throughput_per_mass"] = 0.0
    elif expected == "EMPTY_OR_GAS":
        frames = [[]]
        metric_values = None
    elif expected == "DISSOLVED":
        frames = [[bounded], []]
        metric_values["observed_frames"] = 1
        metric_values["span_frames"] = 1
        metric_values["maximum_turnover_fraction"] = 0.0
        metric_values["post_turnover_frames"] = 0
    elif expected == "PERSISTENT_NO_TURNOVER":
        metric_values["maximum_turnover_fraction"] = 0.1
        metric_values["post_turnover_frames"] = 0
    elif expected == "STATIC_CRYSTAL_OR_SHELL":
        metric_values["mean_activity_per_mass"] = 0.0
        metric_values["mean_energy_throughput_per_mass"] = 0.0
        metric_values["maximum_turnover_fraction"] = 0.1
        metric_values["post_turnover_frames"] = 0
    elif expected == "TURNOVER_WITHOUT_PERSISTENCE":
        metric_values["observed_frames"] = 2
        metric_values["span_frames"] = 2
    elif expected == "TRACKING_UNRESOLVED":
        metric_values["unresolved"] = True

    production_metrics = () if metric_values is None else (TrackMetrics(**metric_values),)
    raw_metrics = [] if metric_values is None else [raw_reproduce.TrackMetric(**metric_values)]
    production_world = WorldMetrics(
        ever_detected=any(bool(frame) for frame in frames),
        final_component_count=len(frames[-1]),
        any_percolated=any(component.percolates for frame in frames for component in frame),
        any_active_unbounded=any_active_unbounded,
        any_turnover_without_persistence=any_turnover_without_persistence,
        tracking_unresolved=tracking_unresolved,
        tracks=production_metrics,
    )
    raw_tracking = raw_reproduce.Tracking([], tracking_unresolved, [])
    assert classify_regime(production_world, production_thresholds) == expected
    assert raw_reproduce.classify_world(frames, raw_tracking, raw_metrics, raw_thresholds) == expected


def test_independent_family_classification_is_canonical_byte_identical():
    manifest = _manifest()
    contract = _raw_manifest_contract(manifest)
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
    rows.sort(key=lambda row: row["world_id"])
    production = classify_family(rows, manifest)
    independent = raw_reproduce.build_classification(contract, rows)
    assert raw_reproduce._canonical_bytes(independent) == canonical_json_bytes(production)
    assert all(
        isinstance(row["complete"], bool)
        for region in independent["atlas"]
        for row in region["per_ic"]
    )

    malformed_non_candidate = [dict(row) for row in rows]
    index = next(index for index, row in enumerate(malformed_non_candidate) if row["regime"] == "DISSOLVED")
    malformed_non_candidate[index] = {**malformed_non_candidate[index], "candidate_track_ids": [99]}
    cleared = raw_reproduce.build_classification(contract, malformed_non_candidate)
    assert cleared["worlds"][index]["candidate_track_ids"] == []
    with pytest.raises(InstrumentationInvalid, match="candidate IDs"):
        classify_family(malformed_non_candidate, manifest)


def test_independent_manifest_parser_binds_nested_layout_environment_and_self_source(tmp_path):
    manifest = _structural_manifest()
    manifest["environment"] = {
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "byteorder": sys.byteorder,
    }
    manifest["source_sha256"] = {
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json": raw_reproduce.RAW_SCHEMA_SHA256,
        "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json": raw_reproduce.REPRODUCTION_SPEC_SHA256,
        "edlab/substrates/lattice_bond/stage_b_reproduce.py": sha256_file(Path(raw_reproduce.__file__)),
    }
    manifest["manifest_sha256_excluding_field"] = hashlib.sha256(
        raw_reproduce._canonical_bytes(manifest)
    ).hexdigest()
    payload = raw_reproduce._canonical_bytes(manifest)
    path = tmp_path / "manifest.json"
    path.write_bytes(payload)
    manifest_hash = hashlib.sha256(payload).hexdigest()
    contract = raw_reproduce.load_manifest(path, manifest_hash)
    assert contract.shape == (4, 4)
    assert contract.worlds[0].world_id == "L000__soup__r00"

    with pytest.raises(raw_reproduce.ReproductionError, match="SHA-256 mismatch"):
        raw_reproduce.load_manifest(path, "0" * 64)

    wrong_source = json.loads(payload)
    wrong_source["source_sha256"]["edlab/substrates/lattice_bond/stage_b_reproduce.py"] = "0" * 64
    wrong_source.pop("manifest_sha256_excluding_field")
    wrong_source["manifest_sha256_excluding_field"] = hashlib.sha256(
        raw_reproduce._canonical_bytes(wrong_source)
    ).hexdigest()
    wrong_source_payload = raw_reproduce._canonical_bytes(wrong_source)
    wrong_source_path = tmp_path / "manifest-wrong-source.json"
    wrong_source_path.write_bytes(wrong_source_payload)
    with pytest.raises(raw_reproduce.ReproductionError, match="executable source"):
        raw_reproduce.load_manifest(
            wrong_source_path,
            hashlib.sha256(wrong_source_payload).hexdigest(),
        )

    wrong_environment = json.loads(payload)
    wrong_environment["environment"]["byteorder"] = "invalid"
    wrong_environment.pop("manifest_sha256_excluding_field")
    wrong_environment["manifest_sha256_excluding_field"] = hashlib.sha256(
        raw_reproduce._canonical_bytes(wrong_environment)
    ).hexdigest()
    wrong_environment_payload = raw_reproduce._canonical_bytes(wrong_environment)
    wrong_environment_path = tmp_path / "manifest-wrong-environment.json"
    wrong_environment_path.write_bytes(wrong_environment_payload)
    with pytest.raises(raw_reproduce.ReproductionError, match="environment"):
        raw_reproduce.load_manifest(
            wrong_environment_path,
            hashlib.sha256(wrong_environment_payload).hexdigest(),
        )


def test_independent_failed_shard_inventory_and_identity_fail_closed(tmp_path):
    enrollment = raw_reproduce.WorldEnrollment("L000__soup__r00", "L000", "soup", 0)
    shard = {
        "schema": raw_reproduce.SHARD_SCHEMA_ID,
        "world": asdict(enrollment),
        "status": "INSTRUMENTATION_INVALID",
        "files": {"failure.json": {"sha256": "0" * 64, "bytes": 1}},
    }
    assert raw_reproduce._verify_shard_identity(shard, enrollment) == "INSTRUMENTATION_INVALID"
    wrong = json.loads(json.dumps(shard))
    wrong["world"]["replicate"] = 1
    with pytest.raises(raw_reproduce.ReproductionError, match="identity mismatch"):
        raw_reproduce._verify_shard_identity(wrong, enrollment)

    (tmp_path / "shard_manifest.json").write_bytes(b"{}\n")
    (tmp_path / "failure.json").write_bytes(b"x")
    raw_reproduce._verify_shard_file_set(tmp_path, {"shard_manifest.json", "failure.json"})
    (tmp_path / "unbound.bin").write_bytes(b"x")
    with pytest.raises(raw_reproduce.ReproductionError, match="file set mismatch"):
        raw_reproduce._verify_shard_file_set(tmp_path, {"shard_manifest.json", "failure.json"})
