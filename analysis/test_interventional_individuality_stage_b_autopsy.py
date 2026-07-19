"""Code-only synthetic qualification for the Stage-B raw autopsy.

Every fixture is deterministic and hand-built.  This suite never opens a
Stage-B physics archive, result manifest, world, checkpoint, or engine.
"""

from __future__ import annotations

import io
import inspect
import json
import math
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pytest

import analysis.interventional_individuality_stage_b_autopsy as autopsy
import analysis.interventional_individuality_stage_b_autopsy_reproduce as independent


def _tiny_protocol() -> dict:
    """A closed 46-key layout small enough for hostile-archive fixtures."""

    state = {
        "state_step": {"dtype": "int64", "shape": [1]},
        "state_m": {"dtype": "float64", "shape": [1]},
        "state_n": {"dtype": "float64", "shape": [1]},
        "state_b": {"dtype": "float64", "shape": [1]},
        "vector_reference_max_error": {"dtype": "float64", "shape": [1]},
        "deterministic_replay_equal": {"dtype": "uint8", "shape": [1]},
    }
    return {
        "exact_raw_inventory": {
            "state_and_validation": state,
            "cell_ledger": {"ledger__affinity": {"dtype": "float64", "shape": [1]}},
            "face_ledger_float64_shape_160_2_12_12": [f"face_{index:02d}" for index in range(30)],
            "scalar_ledger_float64_shape_160": [f"scalar_{index:02d}" for index in range(9)],
        }
    }


def _tiny_arrays(protocol: dict) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    for key, (dtype, shape) in autopsy.expected_inventory(protocol).items():
        arrays[key] = np.zeros(shape, dtype=dtype)
    return arrays


def _npy_bytes(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.lib.format.write_array(buffer, array, allow_pickle=True)
    return buffer.getvalue()


def _write_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    np.savez(path, **arrays)


def _component(
    frame: int,
    index: int,
    cells: tuple[int, ...] | list[int],
    *,
    centroid: tuple[float, float] | None = None,
    wraps_y: bool = False,
    wraps_x: bool = False,
) -> autopsy.Component:
    ordered = tuple(sorted(cells))
    mask = np.zeros((12, 12), dtype=np.bool_)
    for cell in ordered:
        mask[divmod(cell, 12)] = True
    if centroid is None:
        ys = [divmod(cell, 12)[0] for cell in ordered]
        xs = [divmod(cell, 12)[1] for cell in ordered]
        centroid = (math.fsum(ys) / len(ys), math.fsum(xs) / len(xs))
    return autopsy.Component(
        frame=frame,
        index=index,
        cells=ordered,
        lifts=tuple((cell, *divmod(cell, 12)) for cell in ordered),
        area=len(ordered),
        mass=float(len(ordered)),
        lifted_centroid=centroid,
        centroid=centroid,
        radius_gyration=0.0,
        wraps_y=wraps_y,
        wraps_x=wraps_x,
        mask=mask,
    )


def _observation(
    frame: int,
    *,
    area_fraction: float = 3.0 / 144.0,
    percolated: bool = False,
    activity: float = 2e-4,
    energy: float = 2e-5,
    turnover: float = 0.0,
) -> dict:
    return {
        "frame": frame,
        "area_fraction": area_fraction,
        "percolated": percolated,
        "activity_per_mass": activity,
        "energy_throughput_per_mass": energy,
        "turnover_fraction": turnover,
    }


def _summary(**updates) -> dict:
    result = {
        "resolved": True,
        "percolated_fraction": 0.0,
        "active": False,
        "candidate": False,
        "persistent": False,
        "maximum_turnover_fraction": 0.0,
    }
    result.update(updates)
    return result


def _frames() -> list[list[autopsy.Component]]:
    return [[] for _ in range(160)]


def _developmental_observation(
    frame: int,
    fingerprint: str,
    *,
    active: bool = False,
    persistent: bool = False,
    turnover: float = 0.0,
    candidate: bool = False,
    activity: float = 2e-4,
    energy: float = 2e-5,
    seam_crossed: bool = False,
) -> dict:
    """Minimal exact row consumed by developmental_world_summary."""

    return {
        "frame": frame,
        "track_fingerprint": fingerprint,
        "instantaneous_bounded_active": active,
        "prefix_persistent": persistent,
        "turnover_fraction": turnover,
        "prefix_candidate": candidate,
        "activity_per_mass": activity,
        "energy_throughput_per_mass": energy,
        "coordinate_seam_crossed": seam_crossed,
    }


def _track(track_id: int, frames: list[int] | range, *, resolved: bool = True) -> autopsy.Track:
    return autopsy.Track(
        track_id=track_id,
        points=[(int(frame), track_id) for frame in frames],
        resolved=resolved,
    )


def _ordinary_components(track_count: int = 1) -> list[list[autopsy.Component]]:
    frames = _frames()
    supports = ([13, 14, 25], [52, 53, 64], [91, 92, 103])
    for frame in range(160):
        frames[frame] = [
            _component(frame, index, supports[index]) for index in range(track_count)
        ]
    return frames


def _candidate_analysis_world(index: int) -> dict:
    law_id = f"L{index % 8:02d}"
    world_id = f"{law_id}__compact__r{index}"
    return {
        "world_id": world_id,
        "law_id": law_id,
        "ic_id": "compact",
        "committed_regime": "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
        "reconstructed_regime": "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
        "trajectory_class": "STABLE_CANDIDATE_EPISODE|FROZEN|early|SPLIT_MERGE=0|CENSORED=0",
        "longest_candidate_episode_frames": 40,
        "candidate_episode_count": 1,
        "candidate_status_frames": 40,
        "candidate_episode_terminal": True,
        "right_censored": False,
        "coordinate_seam_crossed": False,
        "ever_wound": False,
        "representative_track_fingerprint": "0:13,14,25",
        "first_component_frame": 0,
        "first_bounded_active_frame": 0,
        "first_persistence_qualification_frame": 79,
        "first_turnover_frame": 80,
        "first_prefix_candidate_frame": 120,
        "primary_developmental_pathway": "STABLE_CANDIDATE_EPISODE",
        "terminal_state": "FROZEN",
        "terminal_freeze_onset": 128,
        "terminal_track_alive": True,
        "maintenance_opportunity": True,
        "_representative_track_development": {"selected_run": (120, 159, 40)},
        "_representative_dissolution_frame": None,
    }


def _frozen_protocol() -> dict:
    return json.loads(
        Path(
            "docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_RECONSTRUCTION_PROTOCOL.json"
        ).read_text(encoding="utf-8")
    )


def _valid_raw_arrays() -> dict[str, np.ndarray]:
    arrays = {
        key: np.zeros(shape, dtype=dtype)
        for key, (dtype, shape) in autopsy.expected_inventory(_frozen_protocol()).items()
    }
    arrays["state_step"] = np.arange(161, dtype=np.int64)
    arrays["deterministic_replay_equal"].fill(1)
    arrays["ledger__matter_scale"].fill(1.0)
    arrays["ledger__resource_scale"].fill(1.0)
    return arrays


def _npz_payload(arrays: dict[str, np.ndarray]) -> bytes:
    buffer = io.BytesIO()
    np.savez(buffer, **arrays)
    return buffer.getvalue()


def _package_payloads() -> dict[str, bytes]:
    hashes = _synthetic_control_hashes()
    return {
        "analysis.json": autopsy.canonical_json_bytes(
            {
                "immutable_stage_b_disposition": "DEV_FEASIBILITY_FAIL",
                "autopsy_outcome": "RAW_INSUFFICIENT",
            }
        ),
        "events.jsonl": b"",
        "integrity.json": autopsy.canonical_json_bytes(
            {
                "audit_valid": True,
                "plan_sha256": hashes["plan_sha256"],
                "protocol_sha256": hashes["protocol_sha256"],
                "allowlist_sha256": hashes["allowlist_sha256"],
            }
        ),
        "recomputed_classification.json": autopsy.canonical_json_bytes(
            {"disposition": "DEV_FEASIBILITY_FAIL", "candidate_regions": []}
        ),
        "track_observations.jsonl": b"",
        "trajectory_atlas.json": autopsy.canonical_json_bytes({"world_count": 64}),
        "world_transitions.json": autopsy.canonical_json_bytes({"world_count": 64}),
    }


def _synthetic_controls() -> dict[str, bytes]:
    return {
        autopsy.PLAN_RELATIVE: b"synthetic-plan",
        autopsy.ALLOWLIST_RELATIVE: b"synthetic-allowlist",
        "protocol.json": b"synthetic-protocol",
    }


def _synthetic_control_hashes() -> dict[str, str]:
    controls = _synthetic_controls()
    return {
        "plan_sha256": autopsy.sha256_bytes(controls[autopsy.PLAN_RELATIVE]),
        "protocol_sha256": autopsy.sha256_bytes(controls["protocol.json"]),
        "allowlist_sha256": autopsy.sha256_bytes(controls[autopsy.ALLOWLIST_RELATIVE]),
    }


def _package_counts() -> dict[str, int]:
    return {
        "worlds": 64,
        "tracks": 0,
        "track_observations": 0,
        "events": 0,
        "candidate_worlds": 11,
    }


def _write_synthetic_package(root: Path) -> None:
    hashes = _synthetic_control_hashes()
    autopsy.write_package(
        root,
        _package_payloads(),
        _package_counts(),
        "RAW_INSUFFICIENT",
        hashes["plan_sha256"],
        hashes["protocol_sha256"],
        hashes["allowlist_sha256"],
    )


def _synthetic_planned_output_contract(
    primary: str = "primary",
    independent: str = "independent",
    qualification: str = "QUALIFICATION.json",
) -> dict:
    return {
        "input_bindings": {"reconstruction_protocol": {"path": "protocol.json"}},
        "planned_outputs": {
            "primary_root": primary,
            "independent_root": independent,
            "comparison_file": qualification,
            "files": [
                "integrity.json",
                "recomputed_classification.json",
                "world_transitions.json",
                "track_observations.jsonl",
                "events.jsonl",
                "trajectory_atlas.json",
                "analysis.json",
                "COMPLETE.json",
            ],
        },
    }


def _fabricated_complete_population() -> tuple[
    list[dict], list[dict], dict[str, list[dict]], list[dict], dict[str, list[int]]
]:
    """A complete 8 x 2 x 4 population with 11 fabricated candidate worlds."""

    laws = [f"L{index:03d}" for index in range(8)]
    soup_ids = [
        f"{law_id}__soup__r{replicate:02d}"
        for law_id in laws
        for replicate in range(4)
    ]
    candidate_set = set(soup_ids[:11])
    worlds: list[dict] = []
    track_rows: list[dict] = []
    observations_by_world: dict[str, list[dict]] = {}
    candidate_ids: dict[str, list[int]] = {}
    for law_id in laws:
        for ic_id in ("soup", "compact"):
            for replicate in range(4):
                world_id = f"{law_id}__{ic_id}__r{replicate:02d}"
                candidate = world_id in candidate_set
                fingerprint = "0:13,14,25" if candidate else None
                world = {
                    "world_id": world_id,
                    "law_id": law_id,
                    "ic_id": ic_id,
                    "replicate": replicate,
                    "committed_regime": (
                        "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if candidate else "EMPTY_OR_GAS"
                    ),
                    "reconstructed_regime": (
                        "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if candidate else "EMPTY_OR_GAS"
                    ),
                    "first_component_frame": 0 if candidate else None,
                    "first_bounded_active_frame": 0 if candidate else None,
                    "first_persistence_qualification_frame": 79 if candidate else None,
                    "first_turnover_frame": 80 if candidate else None,
                    "first_prefix_candidate_frame": 120 if candidate else None,
                    "candidate_status_frames": 40 if candidate else 0,
                    "candidate_episode_count": 1 if candidate else 0,
                    "longest_candidate_episode_frames": 40 if candidate else 0,
                    "candidate_episode_terminal": candidate,
                    "last_detected_frame": 159 if candidate else None,
                    "terminal_empty_run_start": None if candidate else 0,
                    "terminal_freeze_onset": None,
                    "terminal_track_alive": candidate,
                    "frames_formation_to_bounded_active": 0 if candidate else None,
                    "frames_formation_to_persistence": 79 if candidate else None,
                    "frames_formation_to_turnover": 80 if candidate else None,
                    "frames_formation_to_candidate": 120 if candidate else None,
                    "frames_formation_to_terminal_loss": None,
                    "right_censored": candidate,
                    "coordinate_seam_crossed": False,
                    "ever_wound": False,
                    "split_count": 0,
                    "merge_count": 0,
                    "appearance_count": 1 if candidate else 0,
                    "dissolution_count": 0,
                    "primary_developmental_pathway": (
                        "STABLE_CANDIDATE_EPISODE" if candidate else "FORMATION_FAILURE"
                    ),
                    "terminal_state": "PERSISTENT_ACTIVE" if candidate else None,
                    "formation_opportunity": True,
                    "maintenance_opportunity": candidate,
                    "persistence_horizon_opportunity": candidate,
                    "post_turnover_horizon_opportunity": candidate,
                    "milestone_track_fingerprints": {
                        "formation": fingerprint,
                        "bounded_active": fingerprint,
                        "persistence": fingerprint,
                        "turnover": fingerprint,
                        "prefix_candidate": fingerprint,
                    },
                    "representative_track_fingerprint": fingerprint,
                    "co_primary_track_fingerprints": [fingerprint] if candidate else [],
                    "trajectory_class": (
                        "STABLE_CANDIDATE_EPISODE|PERSISTENT_ACTIVE|early|SPLIT_MERGE=0|CENSORED=1"
                        if candidate
                        else None
                    ),
                    "_candidate_track_count": 1 if candidate else 0,
                    "_representative_track_development": {
                        "selected_run": (120, 159, 40)
                    }
                    if candidate
                    else None,
                    "_representative_dissolution_frame": None,
                }
                worlds.append(world)
                candidate_ids[world_id] = [0] if candidate else []
                if not candidate:
                    observations_by_world[world_id] = []
                    continue
                rows = [
                    {
                        "world_id": world_id,
                        "track_id": 0,
                        "track_fingerprint": fingerprint,
                        "frame": frame,
                        "resolved": True,
                        "instantaneous_bounded_active": True,
                        "prefix_persistent": frame >= 79,
                        "turnover_fraction": 0.6 if frame >= 80 else 0.0,
                        "prefix_candidate": frame >= 120,
                        "matter_exchange_per_mass": 1.0,
                        "internal_bond_saturation_fraction": 0.0,
                        "matter_cv": 0.1,
                        "resource_cv": 0.1,
                    }
                    for frame in range(160)
                ]
                observations_by_world[world_id] = rows
                track_rows.append(
                    {
                        "world_id": world_id,
                        "law_id": law_id,
                        "ic_id": ic_id,
                        "replicate": replicate,
                        "track_id": 0,
                        "track_fingerprint": fingerprint,
                        "t_active": 0,
                        "t_persistence": 79,
                        "t_turn": 80,
                        "t_prefix": 120,
                        "stable": True,
                        "terminal_persistence": True,
                    }
                )
    observations = [row for world_id in sorted(observations_by_world) for row in observations_by_world[world_id]]
    return worlds, track_rows, observations_by_world, observations, candidate_ids


def _synthetic_reconstruction_arrays(kind: str) -> dict[str, np.ndarray]:
    arrays = _valid_raw_arrays()
    if kind == "empty":
        return arrays
    if kind != "persistent":
        raise AssertionError(kind)
    arrays["state_m"][:, 4:7, 4:7] = 1.0
    arrays["ledger__initial_matter"].fill(9.0)
    arrays["ledger__final_matter"].fill(9.0)
    return arrays


def _primary_synthetic_reconstruction(
    arrays: dict[str, np.ndarray], world_id: str, committed_regime: str
) -> dict[str, object]:
    components = [autopsy.detect_components(arrays["state_m"][frame], frame) for frame in range(160)]
    tracks, events = autopsy.track_components(components)
    for event in events:
        event["world_id"] = world_id
    observations_by_track, summaries = autopsy.build_track_observations(
        world_id, arrays, components, tracks
    )
    regime, candidate_ids = autopsy.classify_world(summaries, components, tracks)
    transition = autopsy.developmental_world_summary(
        world_id,
        committed_regime,
        regime,
        components,
        tracks,
        observations_by_track,
        summaries,
        events,
        candidate_ids,
    )
    ordered_tracks = sorted(
        tracks,
        key=lambda track_id: (
            tracks[track_id].points[0][0],
            components[tracks[track_id].points[0][0]][tracks[track_id].points[0][1]].cells,
        ),
    )
    observations = [
        row for track_id in ordered_tracks for row in observations_by_track[track_id]
    ]
    return {
        "classification": {"regime": regime, "candidate_track_ids": candidate_ids},
        "world_transition": autopsy._strip_internal_world(transition),
        "track_observations": observations,
        "events": events,
    }


def _independent_synthetic_reconstruction(
    arrays: dict[str, np.ndarray], world_id: str, committed_regime: str
) -> dict[str, object]:
    frames = [independent.detect(arrays["state_m"][frame], frame) for frame in range(160)]
    tracking = independent.track_components(world_id, frames)
    observations, summaries = independent.observe_tracks(world_id, arrays, frames, tracking)
    regime, candidate_ids = independent.classify_world(frames, tracking, summaries)
    transition = independent.develop_world(
        independent._world_metadata(world_id),
        committed_regime,
        [],
        regime,
        candidate_ids,
        frames,
        tracking,
        observations,
    )
    return {
        "classification": {"regime": regime, "candidate_track_ids": candidate_ids},
        "world_transition": transition,
        "track_observations": observations,
        "events": tracking.events,
    }


def test_safe_load_npz_accepts_exact_closed_layout(tmp_path: Path):
    protocol = _tiny_protocol()
    arrays = _tiny_arrays(protocol)
    path = tmp_path / "synthetic.npz"
    _write_npz(path, arrays)
    loaded = autopsy.safe_load_npz(path, protocol)
    assert tuple(loaded) == tuple(autopsy.expected_inventory(protocol))
    assert all(np.array_equal(loaded[key], value) for key, value in arrays.items())
    assert all(loaded[key] is not value for key, value in arrays.items())


@pytest.mark.parametrize("unsafe_name", ["../state_m.npy", "nested/state_m.npy", r"nested\state_m.npy"])
def test_safe_load_npz_rejects_traversal_and_nested_members(tmp_path: Path, unsafe_name: str):
    path = tmp_path / "unsafe.npz"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(unsafe_name, _npy_bytes(np.zeros(1, dtype=np.float64)))
    with pytest.raises(autopsy.AuditError, match="unsafe ZIP member"):
        autopsy.safe_load_npz(path, _tiny_protocol())


def test_safe_load_npz_rejects_duplicate_members_before_numpy(tmp_path: Path):
    path = tmp_path / "duplicate.npz"
    payload = _npy_bytes(np.zeros(1, dtype=np.float64))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("state_m.npy", payload)
            archive.writestr("state_m.npy", payload)
    with pytest.raises(autopsy.AuditError, match="duplicate ZIP member"):
        autopsy.safe_load_npz(path, _tiny_protocol())


def test_safe_load_npz_rejects_missing_and_extra_members(tmp_path: Path):
    protocol = _tiny_protocol()
    arrays = _tiny_arrays(protocol)
    arrays["unexpected"] = np.zeros(1, dtype=np.float64)
    path = tmp_path / "extra.npz"
    _write_npz(path, arrays)
    with pytest.raises(autopsy.AuditError, match="inventory mismatch"):
        autopsy.safe_load_npz(path, protocol)


@pytest.mark.parametrize(
    "replacement",
    [
        np.array([object()], dtype=object),
        np.array([(1.0,)], dtype=np.dtype([("value", "<f8")])),
        np.zeros(1, dtype=">f8"),
    ],
    ids=("object", "structured", "nonnative"),
)
def test_safe_load_npz_rejects_unsafe_or_nonnative_dtypes(
    tmp_path: Path, replacement: np.ndarray
):
    protocol = _tiny_protocol()
    arrays = _tiny_arrays(protocol)
    arrays["state_m"] = replacement
    path = tmp_path / "dtype.npz"
    _write_npz(path, arrays)
    with pytest.raises(autopsy.AuditError):
        autopsy.safe_load_npz(path, protocol)


def test_detector_connects_coordinate_seam_without_false_winding():
    matter = np.zeros((12, 12), dtype=np.float64)
    matter[0, 0] = matter[0, 11] = matter[1, 0] = 1.0
    components = autopsy.detect_components(matter, frame=7)
    assert len(components) == 1
    component = components[0]
    assert component.cells == (0, 11, 12)
    assert component.key == (7, 0)
    assert not component.percolates
    assert not component.wraps_y and not component.wraps_x


def test_detector_marks_true_periodic_winding_and_discards_small_sets_before_indexing():
    matter = np.zeros((12, 12), dtype=np.float64)
    matter[3, :] = 1.0
    matter[0, 0:2] = 1.0  # discarded two-cell set has the first row-major root
    matter[8, 8:11] = 1.0
    components = autopsy.detect_components(matter, frame=2)
    assert [component.index for component in components] == [0, 1]
    assert components[0].wraps_x and components[0].percolates
    assert not components[1].percolates
    assert components[0].cells[0] == 36
    assert components[1].cells[0] == 104


def test_association_exact_tie_remains_ambiguity_bearing():
    source = _component(0, 0, [65, 66, 67], centroid=(5.0, 6.0))
    upper = _component(1, 0, [53, 54, 55], centroid=(4.0, 6.0))
    lower = _component(1, 1, [77, 78, 79], centroid=(6.0, 6.0))
    result = autopsy.associate_components([source], [upper, lower])
    assert result["selected"] == set()
    assert result["ambiguity"] == {(0, 0), (0, 1)}
    assert all(edge["qualified"] for edge in result["edges"])
    assert all(edge["ambiguity_bearing"] for edge in result["edges"])
    assert result["edges"][0]["score"] == result["edges"][1]["score"]


def test_tracker_allocates_group_children_before_lower_index_appearance():
    source = _component(0, 0, [64, 65, 66])
    appearance = _component(1, 0, [0, 1, 12])
    child_a = _component(1, 1, [52, 64, 65])
    child_b = _component(1, 2, [54, 66, 78])
    frames = _frames()
    frames[0] = [source]
    frames[1] = [appearance, child_a, child_b]
    tracks, events = autopsy.track_components(frames)
    split = next(row for row in events if row["frame"] == 1 and row["event_type"] == "SPLIT")
    appeared = next(row for row in events if row["frame"] == 1 and row["event_type"] == "APPEARANCE")
    assert split["source_track_ids"] == [0]
    assert split["target_track_ids"] == [1, 2]
    assert appeared["target_component_keys"] == [[1, 0]]
    assert appeared["target_track_ids"] == [3]
    assert tracks[1].parent_ids == (0,) and tracks[2].parent_ids == (0,)


def test_tracker_marks_merge_split_collapse_and_many_to_many_unresolved():
    left0 = _component(0, 0, [61, 62, 63])
    right0 = _component(0, 1, [65, 66, 67])
    middle = _component(1, 0, list(range(61, 68)))
    left2 = _component(2, 0, [61, 62, 63])
    right2 = _component(2, 1, [65, 66, 67])
    frames = _frames()
    frames[0] = [left0, right0]
    frames[1] = [middle]
    frames[2] = [left2, right2]
    tracks, events = autopsy.track_components(frames)
    unresolved = [row for row in events if row["event_type"] == "TRACKING_UNRESOLVED"]
    assert [row["frame"] for row in unresolved] == [1, 2]
    assert unresolved[0]["source_track_ids"] == [0, 1]
    assert unresolved[0]["target_track_ids"] == [2]
    assert unresolved[1]["source_track_ids"] == [2]
    assert unresolved[1]["target_track_ids"] == [3, 4]
    assert all(not tracks[index].resolved for index in range(5))
    assert not any(row["event_type"] in {"MERGE", "SPLIT"} for row in events)


def test_advance_cohort_identity_when_cohort_equals_all_matter():
    pre = np.zeros((12, 12), dtype=np.float64)
    pre[5, 5] = 0.8
    pre[5, 6] = 0.2
    forward = np.zeros((2, 12, 12), dtype=np.float64)
    reverse = np.zeros_like(forward)
    forward[1, 5, 5] = 0.1
    net = forward - reverse
    post = pre - 0.05 * (
        (net[0] - np.roll(net[0], 1, axis=0))
        + (net[1] - np.roll(net[1], 1, axis=1))
    )
    advanced = autopsy.advance_cohort(pre.copy(), pre, post, forward, reverse)
    assert np.array_equal(advanced, post)
    assert math.fsum(advanced.flat) == math.fsum(pre.flat)


def test_advance_cohort_never_clips_a_tolerance_admissible_value():
    pre = np.zeros((12, 12), dtype=np.float64)
    post = pre.copy()
    q = pre.copy()
    q[0, 0] = -5e-13
    q[0, 1] = 5e-13
    flows = np.zeros((2, 12, 12), dtype=np.float64)
    advanced = autopsy.advance_cohort(q, pre, post, flows, flows)
    assert advanced[0, 0] == -5e-13
    assert advanced[0, 1] == 5e-13


def test_advance_cohort_rejects_matter_identity_and_cohort_bound_failures():
    zero = np.zeros((12, 12), dtype=np.float64)
    flows = np.zeros((2, 12, 12), dtype=np.float64)
    bad_post = zero.copy()
    bad_post[0, 0] = 1e-3
    with pytest.raises(autopsy.AuditError, match="matter identity"):
        autopsy.advance_cohort(zero, zero, bad_post, flows, flows)
    bad_q = zero.copy()
    bad_q[0, 0] = 1e-3
    with pytest.raises(autopsy.AuditError, match="pre-cohort bounds"):
        autopsy.advance_cohort(bad_q, zero, zero, flows, flows)


def test_track_summary_candidate_boundary_and_gap_sensitive_post_turnover_count():
    observations = [
        _observation(frame, turnover=0.6 if frame >= 79 else 0.0)
        for frame in range(112)
    ]
    summary = autopsy.summarize_track(observations)
    assert summary["persistent"] and summary["active"] and summary["candidate"]
    assert summary["first_turnover_frame"] == 79
    assert summary["post_turnover_frames"] == 32

    missing_one_post = [row for row in observations if row["frame"] != 80]
    gap_summary = autopsy.summarize_track(missing_one_post)
    assert gap_summary["persistent"]
    assert gap_summary["post_turnover_frames"] == 31
    assert not gap_summary["candidate"]
    assert not autopsy.summarize_track(observations, resolved=False)["persistent"]


@pytest.mark.parametrize(
    ("summaries", "configure", "expected"),
    [
        ({0: _summary(resolved=False)}, "terminal", "TRACKING_UNRESOLVED"),
        ({0: _summary(percolated_fraction=0.1, active=True)}, "wound", "ACTIVE_UNBOUNDED"),
        ({0: _summary()}, "wound", "PERCOLATED"),
        ({}, "empty", "EMPTY_OR_GAS"),
        ({0: _summary()}, "dissolved", "DISSOLVED"),
        ({4: _summary(candidate=True)}, "terminal", "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"),
        ({0: _summary(persistent=True, active=True)}, "terminal", "PERSISTENT_NO_TURNOVER"),
        ({0: _summary(persistent=True)}, "terminal", "STATIC_CRYSTAL_OR_SHELL"),
        ({0: _summary(maximum_turnover_fraction=0.6)}, "terminal", "TURNOVER_WITHOUT_PERSISTENCE"),
        ({0: _summary()}, "terminal", "DISSOLVED"),
    ],
)
def test_world_classifier_exhausts_frozen_precedence(summaries: dict, configure: str, expected: str):
    frames = _frames()
    ordinary = _component(159, 0, [65, 66, 77])
    if configure == "terminal":
        frames[159] = [ordinary]
    elif configure == "wound":
        frames[10] = [_component(10, 0, list(range(12)), wraps_x=True)]
        frames[159] = [ordinary]
    elif configure == "dissolved":
        frames[0] = [_component(0, 0, [65, 66, 77])]
    elif configure != "empty":
        raise AssertionError(configure)
    regime, candidate_ids = autopsy.classify_world(summaries, frames)
    assert regime == expected
    assert candidate_ids == ([4] if expected == "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" else [])


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        ((False, True, False, True, True, ["ONE"]), "AUDIT_INVALID"),
        ((True, False, False, True, True, ["ONE"]), "RAW_INSUFFICIENT"),
        ((True, True, True, True, True, ["ONE"]), "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES"),
        ((True, True, False, False, True, ["ONE"]), "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES"),
        ((True, True, False, True, False, ["ONE"]), "RAW_INSUFFICIENT"),
        ((True, True, False, True, True, []), "RAW_INSUFFICIENT"),
        ((True, True, False, True, True, ["ONE", "TWO"]), "RAW_INSUFFICIENT"),
        ((True, True, False, True, True, ["ONE"]), "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS"),
    ],
)
def test_autopsy_outcome_total_truth_table(arguments: tuple, expected: str):
    assert autopsy.decide_autopsy_outcome(*arguments) == expected


def test_canonical_json_bytes_is_sorted_finite_utf8_and_normalizes_negative_zero():
    value = {"z": np.float64(-0.0), "a": [np.int64(2), "é"], "b": np.bool_(True)}
    assert autopsy.canonical_json_bytes(value) == b'{"a":[2,"\xc3\xa9"],"b":true,"z":0.0}\n'
    for invalid in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(autopsy.AuditError, match="nonfinite"):
            autopsy.canonical_json_bytes({"value": invalid})


def test_required_developmental_world_summary_api_exists():
    assert callable(getattr(autopsy, "developmental_world_summary", None))


def test_developmental_summary_never_stitches_milestones_across_tracks():
    components = _ordinary_components(track_count=2)
    tracks = {0: _track(0, range(160)), 1: _track(1, range(160))}
    first = [
        _developmental_observation(
            frame,
            "0:13,14,25",
            active=frame == 0,
            persistent=frame >= 79,
        )
        for frame in range(160)
    ]
    second = [
        _developmental_observation(
            frame,
            "0:52,53,64",
            turnover=0.6,
            candidate=frame >= 100,
        )
        for frame in range(160)
    ]
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "DISSOLVED",
        "DISSOLVED",
        components,
        tracks,
        {0: first, 1: second},
        {},
        [],
        [],
    )
    assert result["primary_developmental_pathway"] == "TURNOVER_FAILURE"
    assert result["first_bounded_active_frame"] == 0
    assert result["first_turnover_frame"] is None
    assert result["first_prefix_candidate_frame"] is None
    assert result["representative_track_fingerprint"] == "0:13,14,25"


def test_non_candidate_co_primary_tie_uses_numeric_onset_support_order():
    components = _ordinary_components(track_count=2)
    tracks = {0: _track(0, range(160)), 1: _track(1, range(160))}
    observations = {
        0: [
            _developmental_observation(frame, "0:100,101,102")
            for frame in range(160)
        ],
        1: [
            _developmental_observation(frame, "0:20,21,22")
            for frame in range(160)
        ],
    }
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "DISSOLVED",
        "DISSOLVED",
        components,
        tracks,
        observations,
        {},
        [],
        [],
    )
    assert result["co_primary_track_fingerprints"] == [
        "0:20,21,22",
        "0:100,101,102",
    ]
    assert result["representative_track_fingerprint"] == "0:20,21,22"


def test_candidate_representative_is_one_track_and_uses_frozen_episode_ties():
    components = _ordinary_components(track_count=2)
    tracks = {0: _track(0, range(160)), 1: _track(1, range(160))}
    observations: dict[int, list[dict]] = {}
    for track_id, (fingerprint, start, end) in enumerate(
        (("0:13,14,25", 100, 139), ("0:52,53,64", 120, 159))
    ):
        observations[track_id] = [
            _developmental_observation(
                frame,
                fingerprint,
                active=True,
                persistent=frame >= 79,
                turnover=0.6 if frame >= 80 else 0.0,
                candidate=start <= frame <= end,
            )
            for frame in range(160)
        ]
    result = autopsy.developmental_world_summary(
        "L00__compact__r3",
        "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
        "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
        components,
        tracks,
        observations,
        {},
        [],
        [0, 1],
    )
    # Both episodes are 40 frames; the earlier onset wins even though the
    # other track's episode touches the administrative horizon.
    assert result["representative_track_fingerprint"] == "0:13,14,25"
    assert result["candidate_status_frames"] == 40
    assert result["candidate_episode_count"] == 1
    assert result["longest_candidate_episode_frames"] == 40
    assert not result["candidate_episode_terminal"]
    assert result["primary_developmental_pathway"] == "STABLE_CANDIDATE_EPISODE"


def test_terminal_freeze_run_is_broken_by_a_missing_frame():
    components = _ordinary_components()
    frames = [frame for frame in range(160) if frame != 144]
    track = _track(0, frames)
    observations = [
        _developmental_observation(
            frame,
            "0:13,14,25",
            active=True,
            activity=0.0 if frame >= 127 else 2e-4,
            energy=0.0 if frame >= 127 else 2e-5,
        )
        for frame in frames
    ]
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "PERSISTENT_NO_TURNOVER",
        "PERSISTENT_NO_TURNOVER",
        components,
        {0: track},
        {0: observations},
        {},
        [],
        [],
    )
    assert result["terminal_track_alive"]
    assert result["terminal_freeze_onset"] is None
    assert result["terminal_state"] == "PERSISTENT_OTHER"


def test_terminal_dissolution_and_empty_suffix_are_explicit_not_censoring():
    components = _ordinary_components()
    for frame in range(100, 160):
        components[frame] = []
    observations = [
        _developmental_observation(frame, "0:13,14,25", active=True)
        for frame in range(100)
    ]
    event = {
        "frame": 100,
        "event_type": "DISSOLUTION",
        "source_track_ids": [0],
        "target_track_ids": [],
    }
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "DISSOLVED",
        "DISSOLVED",
        components,
        {0: _track(0, range(100))},
        {0: observations},
        {},
        [event],
        [],
    )
    assert result["terminal_state"] == "EMPTY_OR_DISSOLVED"
    assert result["terminal_empty_run_start"] == 100
    assert result["frames_formation_to_terminal_loss"] == 100
    assert not result["terminal_track_alive"]
    assert not result["right_censored"]


@pytest.mark.parametrize(
    ("activity", "energy", "expected_state", "expected_onset"),
    [
        (0.0, 0.0, "FROZEN", 128),
        (1e-4, 1e-5, "PERSISTENT_ACTIVE", None),
        (1e-4, 0.0, "PERSISTENT_OTHER", None),
    ],
)
def test_terminal_last_32_window_uses_strict_freeze_and_inclusive_active_thresholds(
    activity: float,
    energy: float,
    expected_state: str,
    expected_onset: int | None,
):
    components = _ordinary_components()
    observations = [
        _developmental_observation(
            frame,
            "0:13,14,25",
            active=True,
            activity=activity if frame >= 128 else 2e-4,
            energy=energy if frame >= 128 else 2e-5,
        )
        for frame in range(160)
    ]
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "PERSISTENT_NO_TURNOVER",
        "PERSISTENT_NO_TURNOVER",
        components,
        {0: _track(0, range(160))},
        {0: observations},
        {},
        [],
        [],
    )
    assert result["terminal_state"] == expected_state
    assert result["terminal_freeze_onset"] == expected_onset


def test_developmental_formation_failure_has_null_milestones_and_zero_episode_counts():
    result = autopsy.developmental_world_summary(
        "L00__soup__r0",
        "EMPTY_OR_GAS",
        "EMPTY_OR_GAS",
        _frames(),
        {},
        {},
        {},
        [],
        [],
    )
    assert result["primary_developmental_pathway"] == "FORMATION_FAILURE"
    assert result["first_component_frame"] is None
    assert result["first_bounded_active_frame"] is None
    assert result["first_persistence_qualification_frame"] is None
    assert result["first_turnover_frame"] is None
    assert result["first_prefix_candidate_frame"] is None
    assert result["candidate_status_frames"] == 0
    assert result["candidate_episode_count"] == 0
    assert result["longest_candidate_episode_frames"] == 0
    assert not result["candidate_episode_terminal"]
    assert result["representative_track_fingerprint"] is None
    assert result["co_primary_track_fingerprints"] == []
    assert result["trajectory_class"] is None


def test_prehorizon_track_end_without_dissolution_is_audit_failure():
    components = _ordinary_components()
    observations = [
        _developmental_observation(frame, "0:13,14,25", active=True)
        for frame in range(100)
    ]
    with pytest.raises(autopsy.AuditError, match="ends without dissolution"):
        autopsy.developmental_world_summary(
            "L00__soup__r0",
            "DISSOLVED",
            "DISSOLVED",
            components,
            {0: _track(0, range(100))},
            {0: observations},
            {},
            [],
            [],
        )


def test_zero_initial_cohort_denominator_fails_closed():
    components = _frames()
    components[0] = [_component(0, 0, [13, 14, 25])]
    arrays = {
        "state_m": np.zeros((161, 12, 12), dtype=np.float64),
    }
    with pytest.raises(autopsy.AuditError, match="nonpositive initial cohort"):
        autopsy.build_track_observations(
            "L00__soup__r0",
            arrays,
            components,
            {0: _track(0, [0])},
        )


def test_zero_measurement_baselines_are_unavailable_and_route_raw_insufficient():
    worlds = [_candidate_analysis_world(index) for index in range(11)]
    observations: dict[str, list[dict]] = {}
    for world in worlds:
        observations[world["world_id"]] = [
            {
                "frame": frame,
                "track_fingerprint": world["representative_track_fingerprint"],
                "prefix_candidate": frame >= 120,
                "matter_exchange_per_mass": 0.0,
                "internal_bond_saturation_fraction": 0.0,
                "matter_cv": 0.1,
                "resource_cv": 0.1,
            }
            for frame in range(160)
        ]
    result = autopsy.build_analysis(
        worlds,
        [],
        observations,
        [f"L{index:02d}" for index in range(8)],
    )
    signatures = result["observational_signatures_consistent_with"]
    assert not signatures["COMPACT_PREMATURE_FREEZE"]["available"]
    assert not signatures["DESTRUCTIVE_TRANSITION_PROXIMITY"]["available"]
    assert not result["signature_availability"]["COMPACT_PREMATURE_FREEZE"]
    assert not result["signature_availability"]["DESTRUCTIVE_TRANSITION_PROXIMITY"]
    assert result["autopsy_outcome"] == "RAW_INSUFFICIENT"
    assert result["outcome_truth_table"] == {
        "AUDIT_INVALID": False,
        "TRANSIENT_OR_HETEROGENEOUS_CANDIDATES": False,
        "ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS": False,
        "RAW_INSUFFICIENT": True,
        "selected": "RAW_INSUFFICIENT",
    }


def test_destructive_signature_law_span_uses_only_the_qualifying_subtype_support():
    worlds: list[dict] = []
    observations: dict[str, list[dict]] = {}
    law_assignments = ["L00", "L01", "L02"] * 3 + ["L03", "L04"]
    for index, law_id in enumerate(law_assignments):
        world = _candidate_analysis_world(index)
        world_id = f"{law_id}__soup__r{index:02d}"
        world.update(
            {
                "world_id": world_id,
                "law_id": law_id,
                "ic_id": "soup",
                "trajectory_class": "STABLE_CANDIDATE_EPISODE|PERSISTENT_ACTIVE|early|SPLIT_MERGE=0|CENSORED=0",
                "terminal_state": "PERSISTENT_ACTIVE",
                "terminal_freeze_onset": None,
                "candidate_status_frames": 32,
                "longest_candidate_episode_frames": 32,
                "_representative_track_development": {"selected_run": (100, 131, 32)},
                # Nine dissolution-support worlds span only three laws.
                "_representative_dissolution_frame": 150 if index < 9 else None,
            }
        )
        worlds.append(world)
        observations[world_id] = [
            {
                "frame": frame,
                "track_fingerprint": world["representative_track_fingerprint"],
                "prefix_candidate": 100 <= frame <= 131,
                "matter_exchange_per_mass": (
                    2.0 if index >= 9 and 100 <= frame <= 131 else 1.0
                ),
                "internal_bond_saturation_fraction": 0.0,
                "matter_cv": 0.1,
                "resource_cv": 0.1,
            }
            for frame in range(160)
        ]
    result = autopsy.build_analysis(
        worlds,
        [],
        observations,
        [f"L{index:02d}" for index in range(8)],
    )
    signature = result["observational_signatures_consistent_with"][
        "DESTRUCTIVE_TRANSITION_PROXIMITY"
    ]
    assert signature["details"]["dissolution_subtype_qualified"]
    assert not signature["details"]["high_exchange_subtype_qualified"]
    assert signature["law_ids"] == ["L00", "L01", "L02"]
    assert not signature["qualified"]
    assert result["autopsy_outcome"] == "RAW_INSUFFICIENT"


def test_process_world_has_no_second_path_read_after_byte_authentication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    protocol = _frozen_protocol()
    original = _npz_payload(_valid_raw_arrays())
    replacement_arrays = _valid_raw_arrays()
    replacement_arrays["state_n"][0, 0, 0] = 0.5
    replacement = _npz_payload(replacement_arrays)
    shard = tmp_path / "physics.npz"
    shard.write_bytes(original)
    authenticated = shard.read_bytes()
    shard.write_bytes(replacement)

    observed_loader_inputs: list[Path | bytes] = []
    real_loader = autopsy.safe_load_npz

    def recording_loader(source: Path | bytes, candidate_protocol: dict):
        observed_loader_inputs.append(source)
        return real_loader(source, candidate_protocol)

    monkeypatch.setattr(autopsy, "safe_load_npz", recording_loader)
    parameters = inspect.signature(autopsy.process_world).parameters
    if "authenticated_row" in parameters:
        authenticated_row = {
            "bytes": len(authenticated),
            "sha256": autopsy.sha256_bytes(authenticated),
            "accepted_parent_git_blob_oid": autopsy.git_blob_oid_bytes(authenticated),
        }
        with pytest.raises(autopsy.AuditError, match="changed after authentication"):
            autopsy.process_world(
                tmp_path,
                "physics.npz",
                "L000__soup__r00",
                protocol,
                {"regime": "EMPTY_OR_GAS"},
                {autopsy.normalize_allowlist_path("physics.npz")},
                authenticated_row,
            )
        assert observed_loader_inputs == []
    elif "authenticated_bytes" in parameters:
        result = autopsy.process_world(
            tmp_path,
            "physics.npz",
            "L000__soup__r00",
            protocol,
            {"regime": "EMPTY_OR_GAS"},
            authenticated_bytes=authenticated,
        )
        assert result["regime"] == "EMPTY_OR_GAS"
        assert observed_loader_inputs == [authenticated]
    elif "expected_sha256" in parameters:
        with pytest.raises(autopsy.AuditError, match="hash|SHA|authenticated|substitution"):
            autopsy.process_world(
                tmp_path,
                "physics.npz",
                "L000__soup__r00",
                protocol,
                {"regime": "EMPTY_OR_GAS"},
                expected_sha256=autopsy.sha256_bytes(authenticated),
            )
    else:
        pytest.fail(
            "process_world exposes neither an authenticated row/bytes nor an expected-hash gate"
        )


@pytest.mark.parametrize(
    "relative",
    [
        "../secret.json",
        "safe/../secret.json",
        "safe/./file.json",
        "safe//file.json",
        "/absolute/file.json",
        "C:/absolute/file.json",
    ],
)
def test_allowlist_normalization_rejects_dotdot_empty_and_absolute_paths(relative: str):
    with pytest.raises(autopsy.AuditError):
        autopsy.normalize_allowlist_path(relative)


def test_allowlist_normalization_casefolds_and_normalizes_windows_separators():
    assert autopsy.normalize_allowlist_path(r"Docs\Safe\FILE.Json") == "docs/safe/file.json"


def test_read_allowed_bytes_rejects_unauthorized_casefolded_path(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "safe").mkdir(parents=True)
    (repo / "safe" / "other.json").write_bytes(b"{}")
    allowed = {autopsy.normalize_allowlist_path("safe/allowed.json")}
    with pytest.raises(autopsy.AuditError, match="source firewall"):
        autopsy.read_allowed_bytes(repo, "SAFE/OTHER.JSON", allowed)


def test_read_allowed_bytes_rejects_symlink_or_reparse_component(tmp_path: Path):
    repo = tmp_path / "repo"
    target = repo / "real" / "allowed.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"{}")
    link = repo / "allowed.json"
    try:
        link.symlink_to(target)
    except OSError:
        # Optional real-link coverage on Windows accounts with Developer Mode
        # or SeCreateSymbolicLinkPrivilege.  The deterministic reparse fixture
        # below remains binding on every platform.
        return
    allowed = {autopsy.normalize_allowlist_path("allowed.json")}
    with pytest.raises(autopsy.AuditError, match="reparse|symlink"):
        autopsy.read_allowed_bytes(repo, "allowed.json", allowed)


def test_primary_reparse_detection_honors_windows_file_attribute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "allowed.json"
    target.write_bytes(b"{}")
    real_lstat = autopsy.os.lstat

    class MockReparseStat:
        st_file_attributes = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT

    def mocked_lstat(path):
        return MockReparseStat() if Path(path) == target else real_lstat(path)

    monkeypatch.setattr(autopsy.os, "lstat", mocked_lstat)
    monkeypatch.setattr(autopsy.os.path, "islink", lambda _path: False)
    assert autopsy._has_reparse_or_symlink(repo, target)
    allowed = {autopsy.normalize_allowlist_path("allowed.json")}
    with pytest.raises(autopsy.AuditError, match="reparse|symlink"):
        autopsy.read_allowed_bytes(repo, "allowed.json", allowed)


def test_validate_raw_arrays_accepts_the_exact_synthetic_neutral_fixture():
    result = autopsy.validate_raw_arrays(_valid_raw_arrays())
    assert result == {
        "maximum_scale": 1.0,
        "maximum_reference_error": 0.0,
        "maximum_transport_error": 0.0,
        "maximum_matter_residual": 0.0,
        "maximum_energy_residual": 0.0,
    }


@pytest.mark.parametrize(
    ("fault", "message"),
    [
        ("nonfinite", "nonfinite"),
        ("replay", "deterministic replay"),
        ("scale", "neutral scale"),
        ("exact_zero", "exact-zero"),
        ("reference", "vector/reference"),
        ("transport", "matter transport identity"),
        ("matter_residual", "matter residual"),
        ("energy_residual", "energy residual"),
    ],
)
def test_validate_raw_arrays_fails_each_numerical_qualification_gate(
    fault: str, message: str
):
    arrays = _valid_raw_arrays()
    if fault == "nonfinite":
        arrays["state_n"][0, 0, 0] = np.nan
    elif fault == "replay":
        arrays["deterministic_replay_equal"][0] = 0
    elif fault == "scale":
        arrays["ledger__matter_scale"][0, 0, 0, 0] = 0.999
    elif fault == "exact_zero":
        arrays["ledger__controller_onset_energy_jump"][0] = 1e-15
    elif fault == "reference":
        arrays["vector_reference_max_error"][0] = 2e-10
    elif fault == "transport":
        arrays["state_m"][1, 0, 0] = 1e-4
    elif fault == "matter_residual":
        arrays["ledger__matter_residual"][0] = 1e-9
    elif fault == "energy_residual":
        arrays["ledger__energy_residual"][0] = 1e-9
    else:
        raise AssertionError(fault)
    with pytest.raises(autopsy.AuditError, match=message):
        autopsy.validate_raw_arrays(arrays)


def test_write_package_publishes_exact_closed_inventory_and_never_overwrites(tmp_path: Path):
    root = tmp_path / "package"
    _write_synthetic_package(root)
    assert sorted(path.name for path in root.iterdir()) == sorted(autopsy.PACKAGE_NAMES)
    complete = json.loads((root / "COMPLETE.json").read_text(encoding="utf-8"))
    assert complete["status"] == "COMPLETE"
    assert [row["path"] for row in complete["files"]] == sorted(_package_payloads())
    for row in complete["files"]:
        data = (root / row["path"]).read_bytes()
        assert row["bytes"] == len(data)
        assert row["sha256"] == autopsy.sha256_bytes(data)
    before = {path.name: path.read_bytes() for path in root.iterdir()}
    with pytest.raises(autopsy.AuditError, match="no-overwrite"):
        _write_synthetic_package(root)
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before
    blocked = tmp_path / "blocked"
    Path(str(blocked) + ".partial").mkdir()
    with pytest.raises(autopsy.AuditError, match="no-overwrite"):
        _write_synthetic_package(blocked)


@pytest.mark.parametrize("fault", ["missing", "extra"])
def test_write_package_rejects_nonexact_payload_inventory(tmp_path: Path, fault: str):
    files = _package_payloads()
    if fault == "missing":
        del files["events.jsonl"]
    else:
        files["unexpected.json"] = b"{}\n"
    root = tmp_path / fault
    with pytest.raises(autopsy.AuditError, match="inventory"):
        autopsy.write_package(
            root,
            files,
            _package_counts(),
            "RAW_INSUFFICIENT",
            "1" * 64,
            "2" * 64,
            "3" * 64,
        )
    assert not root.exists() and not Path(str(root) + ".partial").exists()


def test_compare_packages_rejects_complete_hash_inventory_lie(tmp_path: Path):
    primary = tmp_path / "primary"
    _write_synthetic_package(primary)
    complete = json.loads((primary / "COMPLETE.json").read_text(encoding="utf-8"))
    complete["files"][0]["sha256"] = "0" * 64
    (primary / "COMPLETE.json").write_bytes(autopsy.canonical_json_bytes(complete))
    with pytest.raises(autopsy.AuditError, match="COMPLETE|hash|inventory"):
        autopsy._validated_package_bytes(
            tmp_path,
            "primary",
            "primary",
            _synthetic_control_hashes(),
        )


def test_compare_packages_rejects_extra_or_missing_members(tmp_path: Path):
    for fault in ("extra", "missing"):
        repo = tmp_path / fault
        repo.mkdir()
        primary = repo / "primary"
        _write_synthetic_package(primary)
        if fault == "extra":
            (primary / "unexpected.txt").write_text("x", encoding="utf-8")
        else:
            (primary / "analysis.json").unlink()
        with pytest.raises(autopsy.AuditError, match="inventory|missing|package"):
            autopsy._validated_package_bytes(
                repo,
                "primary",
                "primary",
                _synthetic_control_hashes(),
            )


def test_compare_packages_never_overwrites_qualification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    qualification = tmp_path / "QUALIFICATION.json"
    qualification.write_bytes(b"sentinel")
    monkeypatch.setattr(autopsy, "PRIMARY_ROOT_RELATIVE", "primary")
    monkeypatch.setattr(autopsy, "INDEPENDENT_ROOT_RELATIVE", "independent")
    monkeypatch.setattr(autopsy, "QUALIFICATION_RELATIVE", "QUALIFICATION.json")
    plan = _synthetic_planned_output_contract()
    with pytest.raises(autopsy.AuditError, match="already exists"):
        autopsy.compare_packages(
            tmp_path,
            "primary",
            "independent",
            "QUALIFICATION.json",
            plan,
            _synthetic_controls(),
        )
    assert qualification.read_bytes() == b"sentinel"


def test_main_rejects_arbitrary_output_root_before_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    called = False

    def forbidden_build(*_args, **_kwargs):
        nonlocal called
        called = True
        return {}, {}, "RAW_INSUFFICIENT"

    monkeypatch.setattr(autopsy, "build_package", forbidden_build)
    result = autopsy.main(
        [
            "--plan",
            "plan.json",
            "--allowlist",
            "allowlist.json",
            "--output-root",
            str(tmp_path / "arbitrary"),
        ]
    )
    assert result == 2
    assert not called


def test_main_rejects_arbitrary_compare_and_qualification_roots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    called = False

    def forbidden_compare(*_args, **_kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(autopsy, "compare_packages", forbidden_compare)
    result = autopsy.main(
        [
            "--compare-only",
            "--primary-root",
            str(tmp_path / "primary"),
            "--independent-root",
            str(tmp_path / "independent"),
            "--qualification",
            str(tmp_path / "QUALIFICATION.json"),
        ]
    )
    assert result == 2
    assert not called


def test_runtime_gate_rejects_a_pytest_version_mismatch(monkeypatch: pytest.MonkeyPatch):
    world_ids = [f"L000__soup__r{index:02d}" for index in range(64)]
    committed_worlds = [
        {
            "world_id": world_id,
            "regime": (
                "BOUNDED_ACTIVE_TURNOVER_CANDIDATE" if index < 11 else "EMPTY_OR_GAS"
            ),
        }
        for index, world_id in enumerate(world_ids)
    ]
    plan = {
        "accepted_parent": "c31bf27ea80a6a3dcc60d0ec5380f668358671ff",
        "input_bindings": {
            "manifest": {"sha256": "a" * 64},
            "committed_classification": {"path": "classification.json"},
            "reconstruction_protocol": {"path": "protocol.json"},
            "accepted_parent_physics_git_tree": {"aggregate_sha256": "b" * 64},
        },
        "planned_outputs": {
            "primary_root": autopsy.PRIMARY_ROOT_RELATIVE,
            "independent_root": autopsy.INDEPENDENT_ROOT_RELATIVE,
            "comparison_file": autopsy.QUALIFICATION_RELATIVE,
            "files": [
                "integrity.json",
                "recomputed_classification.json",
                "world_transitions.json",
                "track_observations.jsonl",
                "events.jsonl",
                "trajectory_atlas.json",
                "analysis.json",
                "COMPLETE.json",
            ],
        },
    }
    physics_paths = [f"synthetic/{world_id}/physics.npz" for world_id in world_ids]
    allowlist = {"scientific_inputs": {"physics_shards": physics_paths}}
    manifest = {
        "execution": {"world_ids": world_ids},
        "law_family": {"laws": [{"law_id": "L000"}]},
    }
    committed = {"worlds": committed_worlds}
    recomputed = {
        "disposition": "DEV_FEASIBILITY_FAIL",
        "candidate_regions": [],
        "worlds": [],
    }
    controls = {
        "plan.json": b"plan",
        "allowlist.json": b"allowlist",
        "protocol.json": b"protocol",
    }
    monkeypatch.setattr(
        autopsy,
        "load_controls",
        lambda *_args: (plan, allowlist, {}, set(), controls),
    )
    monkeypatch.setattr(
        autopsy,
        "verify_inputs_before_arrays",
        lambda *_args: (
            manifest,
            {},
            committed,
            {"committed_classification": autopsy.canonical_json_bytes(recomputed)},
            [
                {
                    "path": path,
                    "bytes": 0,
                    "sha256": autopsy.sha256_bytes(b""),
                    "accepted_parent_git_blob_oid": autopsy.git_blob_oid_bytes(b""),
                }
                for path in physics_paths
            ],
            {},
        ),
    )

    def fake_world(
        _repo,
        _relative,
        world_id,
        _protocol,
        committed_world,
        _allowed,
        _authenticated_row,
    ):
        return {
            "world_id": world_id,
            "law_id": "L000",
            "ic_id": "soup",
            "replicate": 0,
            "regime": committed_world["regime"],
            "candidate_track_ids": [],
            "qualification": {
                "maximum_reference_error": 0.0,
                "maximum_transport_error": 0.0,
                "maximum_matter_residual": 0.0,
                "maximum_energy_residual": 0.0,
            },
            "transition": {},
            "observations": [],
            "events": [],
            "track_stage_rows": [],
            "track_count": 0,
        }

    monkeypatch.setattr(autopsy, "process_world", fake_world)
    monkeypatch.setattr(autopsy, "build_recomputed_classification", lambda *_args: recomputed)
    monkeypatch.setattr(autopsy, "build_trajectory_atlas", lambda *_args: {})
    monkeypatch.setattr(
        autopsy,
        "build_analysis",
        lambda *_args: {"autopsy_outcome": "RAW_INSUFFICIENT"},
    )
    monkeypatch.setattr(autopsy.sys, "version_info", (3, 12, 10))
    monkeypatch.setattr(autopsy.np, "__version__", "2.5.1")
    monkeypatch.setattr(autopsy.sys, "byteorder", "little")
    monkeypatch.setattr(
        autopsy.sys,
        "executable",
        "C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe",
    )
    monkeypatch.setattr(autopsy.pytest, "__version__", "0.0.0")
    with pytest.raises(autopsy.AuditError, match="runtime|pytest"):
        autopsy.build_package(Path.cwd(), "plan.json", "allowlist.json")


def test_precursor_availability_requires_a_consecutive_pre_freeze_opportunity_window():
    world = _candidate_analysis_world(0)
    world.update(
        {
            "committed_regime": "STATIC_CRYSTAL_OR_SHELL",
            "reconstructed_regime": "STATIC_CRYSTAL_OR_SHELL",
            "terminal_freeze_onset": 128,
        }
    )
    pre_frames = [116, 117, 118, 119, 121, 122, 123, 124]
    observations = [
        {
            "frame": frame,
            "track_fingerprint": world["representative_track_fingerprint"],
            "prefix_candidate": False,
            "matter_exchange_per_mass": 1.0,
            "internal_bond_saturation_fraction": 0.6,
            "matter_cv": 0.1,
            "resource_cv": 0.1,
        }
        for frame in pre_frames + list(range(128, 160))
    ]
    result = autopsy.build_analysis(
        [world],
        [],
        {world["world_id"]: observations},
        ["L00"],
    )
    precursors = result["observational_signatures_consistent_with"][
        "COMPACT_PREMATURE_FREEZE"
    ]["details"]["precursors"]
    assert not precursors["BOND_SATURATION"]["available"]
    assert not precursors["LOW_INTERNAL_HETEROGENEITY"]["available"]
    assert not precursors["REDUCED_MATERIAL_EXCHANGE"]["available"]


def test_precursor_windows_are_available_but_false_with_complete_nonqualifying_history():
    world = _candidate_analysis_world(0)
    world.update(
        {
            "committed_regime": "STATIC_CRYSTAL_OR_SHELL",
            "reconstructed_regime": "STATIC_CRYSTAL_OR_SHELL",
            "terminal_freeze_onset": 128,
        }
    )
    observations = [
        {
            "frame": frame,
            "track_fingerprint": world["representative_track_fingerprint"],
            "prefix_candidate": False,
            "matter_exchange_per_mass": 1.0,
            "internal_bond_saturation_fraction": 0.0,
            "matter_cv": 0.1,
            "resource_cv": 0.1,
        }
        for frame in range(160)
    ]
    result = autopsy.build_analysis(
        [world],
        [],
        {world["world_id"]: observations},
        ["L00"],
    )
    precursors = result["observational_signatures_consistent_with"][
        "COMPACT_PREMATURE_FREEZE"
    ]["details"]["precursors"]
    assert all(row["available"] for row in precursors.values())
    assert not any(row["qualified"] for row in precursors.values())


def test_primary_and_independent_atlas_have_canonical_synthetic_parity():
    worlds, track_rows, observations_by_world, observations, candidate_ids = (
        _fabricated_complete_population()
    )
    laws = [f"L{index:03d}" for index in range(8)]
    primary_atlas = autopsy.build_trajectory_atlas(worlds, track_rows, laws)
    independent_atlas = independent.build_atlas(worlds, laws, candidate_ids)
    assert autopsy.canonical_json_bytes(primary_atlas) == independent.canonical_bytes(
        independent_atlas
    )


def test_primary_and_independent_analysis_have_canonical_synthetic_parity():
    worlds, track_rows, observations_by_world, observations, _candidate_ids = (
        _fabricated_complete_population()
    )
    laws = [f"L{index:03d}" for index in range(8)]
    primary_analysis = autopsy.build_analysis(
        worlds,
        track_rows,
        observations_by_world,
        laws,
    )
    audit_gates = {
        "input_bindings": True,
        "git_blob_identity": True,
        "raw_layout": True,
        "numerical_qualification": True,
        "classification_byte_identity": True,
        "candidate_set_identity": True,
        "world_count": True,
    }
    independent_analysis = independent.analyze(
        worlds,
        observations,
        [],
        laws,
        audit_gates,
    )
    assert autopsy.canonical_json_bytes(primary_analysis) == independent.canonical_bytes(
        independent_analysis
    )


def test_independent_signature_interpretation_matches_the_frozen_exact_literal():
    names = (
        "IC_FORMATION_DEPENDENCE",
        "COMPACT_PREMATURE_FREEZE",
        "DESTRUCTIVE_TRANSITION_PROXIMITY",
        "FINITE_HORIZON_CENSORING",
        "TRANSIENT_THRESHOLD_CROSSING",
    )
    for name in names:
        row = independent._signature_row(False, True, [], [], 0, 1, {}, name)
        assert row["interpretation"] == (
            f"OBSERVATIONAL_SIGNATURE_ONLY:{name}; never causal and never changes "
            "DEV_FEASIBILITY_FAIL"
        )


@pytest.mark.parametrize(
    ("kind", "committed_regime", "expected_trajectory_class"),
    [
        ("empty", "EMPTY_OR_GAS", None),
        (
            "persistent",
            "STATIC_CRYSTAL_OR_SHELL",
            "ACTIVATION_FAILURE|FROZEN|early|SPLIT_MERGE=0|CENSORED=1",
        ),
    ],
)
def test_primary_and_independent_end_to_end_synthetic_reconstruction_parity(
    kind: str,
    committed_regime: str,
    expected_trajectory_class: str | None,
):
    arrays = _synthetic_reconstruction_arrays(kind)
    # This is a complete code-only numerical fixture before either independent
    # reconstruction path sees it.
    autopsy.validate_raw_arrays(arrays)
    world_id = "L000__soup__r00"
    primary = _primary_synthetic_reconstruction(arrays, world_id, committed_regime)
    reproduced = _independent_synthetic_reconstruction(arrays, world_id, committed_regime)
    assert autopsy.canonical_json_bytes(primary) == independent.canonical_bytes(reproduced)
    assert primary["world_transition"]["trajectory_class"] == expected_trajectory_class
