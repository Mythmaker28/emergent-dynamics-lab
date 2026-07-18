"""Synthetic, outcome-blind contract tests for DIRECTED-CAUSAL-PAIR-00 Phase 0.5.

These tests never construct a development world.  They exercise only passive
mechanical primitives, the standard-library preflight, and temporary synthetic
files.  No prospective namespace, scientific endpoint, reader, decoder, or
analyzer is imported.
"""

from __future__ import annotations

import ast
import base64
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest import mock

import numpy as np
import pytest

from edlab.experiments.sc_iom.engine import IOMState
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import directed_causal_pair_phase05_mechanics as mech
from experiments.individuation import directed_causal_pair_phase05_reproduce as repro
from experiments.individuation import directed_causal_pair_phase05_runner as runner


N = mech.GRID_SIZE


def _point(row: int, column: int) -> np.ndarray:
    mask = np.zeros((N, N), dtype=bool)
    mask[row % N, column % N] = True
    return mask


def _disk(row: int, column: int, radius: int = 4) -> np.ndarray:
    rows, columns = np.indices((N, N))
    dr = np.minimum(np.abs(rows - row), N - np.abs(rows - row))
    dc = np.minimum(np.abs(columns - column), N - np.abs(columns - column))
    return dr * dr + dc * dc <= radius * radius


def _synthetic_state(step: int = 19) -> IOMState:
    rows, columns = np.indices((N, N))
    rho = 0.20 + 0.0003 * rows + 0.0002 * columns
    U = rho * (0.70 + 0.0001 * rows)
    V = rho * (0.40 + 0.0001 * columns)
    c = 0.30 + 0.0002 * rows + 0.0001 * columns
    nutrient = 0.50 + 0.0001 * rows + 0.0002 * columns
    cohorts = np.stack((0.45 * rho, 0.55 * rho))
    uptake = 0.01 + 0.00001 * rows + 0.00002 * columns
    memory = np.stack((rho * (0.10 + 0.0001 * rows), rho * (0.20 + 0.0001 * columns)))
    return IOMState(rho, U, V, c, nutrient, cohorts, uptake, memory, step)


def _pair_masks() -> list[np.ndarray]:
    # A/B are 32 cells apart and each mask has 49 cells, above the frozen 45.
    return [_disk(10, 8), _disk(10, 40), _disk(44, 24)]


def _assignment() -> mech.PairAssignment:
    return mech.PairAssignment(target_A=0, target_B=1, sentinel=2)


def _mechanics_manifest() -> dict[str, object]:
    return {
        "schema": "DIRECTED-CAUSAL-PAIR-00-PHASE05-DEV-MANIFEST-v1",
        "mission": mech.MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "phase0_commit": mech.PHASE0_COMMIT,
        "allowed_seed_namespace": list(mech.OPEN_DEV_NAMESPACE),
        "worlds": list(mech.FROZEN_PAIR_WORLDS),
        "pair_assignments": {
            str(world): dict(values) for world, values in mech.FROZEN_ASSIGNMENTS.items()
        },
        "prospective_namespace": None,
    }


def _runner_manifest() -> dict[str, object]:
    return {
        "schema": runner.MANIFEST_SCHEMA,
        "mission": runner.MISSION,
        "mode": "DEV_ONLY_MECHANICAL",
        "phase0_commit": runner.PHASE0_COMMIT,
        "code_commit": "0" * 40,
        "allowed_seed_namespace": list(runner.OPEN_DEV_NAMESPACE),
        "worlds": list(runner.PLAN),
        "pair_assignments": copy.deepcopy(runner.ASSIGNMENTS),
        "prospective_namespace": None,
        "output_directory": runner.EXPECTED_OUTPUT.as_posix(),
        # Invalid-manifest tests fail before either placeholder can be opened.
        "input_files": {
            "synthetic-input.bin": {"sha256": "0" * 64, "git_blob": "0" * 40}
        },
        "code_files": {
            "synthetic-code.py": {"sha256": "0" * 64, "git_blob": "0" * 40}
        },
    }


def _prefix_row(root: Path, sequence: int, world_id: int, payload: bytes) -> dict[str, object]:
    name = f"{sequence:03d}_{world_id}.json.gz"
    path = root / name
    path.write_bytes(payload)
    return {
        "sequence_index": sequence,
        "world_id": world_id,
        "path": name,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
    }


def _write_canonical_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    path.write_bytes(payload)


def _runner_manifest_path(repo: Path) -> Path:
    return repo / runner.EXPECTED_MANIFEST


def test_periodic_wrap_geometry_uses_short_toroidal_displacement() -> None:
    geometry = mech.pair_geometry(_point(10, 63), _point(10, 1))
    assert geometry["distance"] == pytest.approx(2.0)
    assert geometry["centroid_A"] == pytest.approx([10.0, 63.0])
    assert geometry["centroid_B"] == pytest.approx([10.0, 1.0])


def test_exact_24_and_below_24_are_distinct_from_the_halo_gate() -> None:
    exact = mech.pair_geometry(_point(8, 3), _point(8, 27))
    below = mech.pair_geometry(_point(8, 3), _point(8, 26))
    assert exact["distance"] == pytest.approx(mech.MIN_SEPARATION)
    assert exact["minimum_halo_gap"] == pytest.approx(0.0)
    # Inclusive radius-12 lattice disks touch at exact continuous distance 24.
    assert exact["halo_overlap_cells"] > 0
    assert below["distance"] < mech.MIN_SEPARATION
    assert below["minimum_halo_gap"] < 0.0


def test_halo_overlap_and_four_neighbour_contact_fail_independently() -> None:
    halo_only = mech.pair_geometry(_point(12, 5), _point(12, 29))
    assert halo_only["halo_overlap_cells"] > 0
    assert not halo_only["body_contact"]
    assert halo_only["body_overlap_cells"] == 0

    # Contact also wraps across the periodic boundary.
    assert mech.masks_contact_four_neighbour(_point(12, 0), _point(12, 63))
    contact = mech.pair_geometry(_point(12, 0), _point(12, 63))
    assert contact["body_contact"]
    assert contact["body_overlap_cells"] == 0


def test_exact_24_observer_passes_distance_but_fails_closed_on_halo_touch() -> None:
    masks = [_disk(10, 4), _disk(10, 28), _disk(44, 48)]
    state = _synthetic_state()
    # Keep this a literal geometric boundary fixture under the observer's
    # rho-weighted centroid convention.
    state.rho = np.ones_like(state.rho)
    record = mech.PassivePairObserver(masks, _assignment()).seed_snapshot(state, masks)
    assert record["pair_geometry"]["distance"] == pytest.approx(24.0)
    assert "PAIR_DISTANCE_BELOW_24" not in record["kill_reasons"]
    assert "RADIUS12_HALO_OVERLAP" in record["kill_reasons"]


def test_production_observer_round_trips_weighted_prior_edge_centroids() -> None:
    masks = _pair_masks()
    observer = mech.PassivePairObserver(masks, _assignment())
    seed_state = _synthetic_state(step=100)
    seed = observer.seed_snapshot(seed_state, masks)
    seed_summary = repro.validate_step_record(
        seed,
        world_id=50004,
        context="weighted-observer-seed",
    )

    next_state = _synthetic_state(step=101)
    current = observer.advance(next_state, masks, step=1, stage="WRITER")
    summary = repro.validate_step_record(
        current,
        world_id=50004,
        context="weighted-observer-current",
        prior_track_masks=seed_summary.current_track_masks,
        prior_track_centroids=seed_summary.current_track_centroids,
    )
    assert summary.association_edges_checked == 9


def test_synthetic_crossing_without_fusion_fails_closed_on_separation() -> None:
    masks = [_disk(10, 8), _disk(20, 40), _disk(48, 24)]
    observer = mech.PassivePairObserver(masks, _assignment())
    state = _synthetic_state()
    records = [observer.seed_snapshot(state, masks)]
    for step in range(1, 13):
        next_masks = [
            _disk(10, 8 + 2 * step),
            _disk(20, 40 - 2 * step),
            masks[2],
        ]
        # Component enumeration is deliberately unrelated to tracker identity.
        components = next_masks if step % 2 else [next_masks[2], next_masks[1], next_masks[0]]
        records.append(
            observer.advance(state, components, step=step, stage="SYNTHETIC_CROSSING")
        )

    assert any("PAIR_DISTANCE_BELOW_24" in row["kill_reasons"] for row in records)
    assert all(not row["events"] for row in records)
    assert all(not row["component_switch"] for row in records)
    assert all(track.status == "ALIVE" for track in observer.tracker.tracks)


def test_synthetic_tracker_switch_is_explicitly_fail_closed() -> None:
    masks = [_disk(14, 8), _disk(14, 34), _disk(48, 50)]
    observer = mech.PassivePairObserver(masks, _assignment())
    state = _synthetic_state()
    observer.seed_snapshot(state, masks)

    def forced_swap(component_masks: list[np.ndarray], _step: int) -> dict[int, str]:
        observer.tracker.tracks[0].mask = component_masks[1].copy()
        observer.tracker.tracks[1].mask = component_masks[0].copy()
        observer.tracker.tracks[2].mask = component_masks[2].copy()
        return {}

    observer.tracker.update = forced_swap  # type: ignore[method-assign]
    record = observer.advance(state, masks, step=1, stage="SYNTHETIC_SWITCH")
    assert record["component_switch"]
    assert "PAIR_IDENTITY_SWITCH" in record["kill_reasons"]


def test_synthetic_A_sentinel_switch_is_explicitly_fail_closed() -> None:
    masks = [_disk(14, 8), _disk(14, 34), _disk(48, 50)]
    observer = mech.PassivePairObserver(masks, _assignment())
    state = _synthetic_state()
    observer.seed_snapshot(state, masks)

    def forced_swap(component_masks: list[np.ndarray], _step: int) -> dict[int, str]:
        observer.tracker.tracks[0].mask = component_masks[2].copy()
        observer.tracker.tracks[1].mask = component_masks[1].copy()
        observer.tracker.tracks[2].mask = component_masks[0].copy()
        return {}

    observer.tracker.update = forced_swap  # type: ignore[method-assign]
    record = observer.advance(state, masks, step=1, stage="SYNTHETIC_SENTINEL_SWITCH")
    assert record["component_switch"]
    assert "PAIR_IDENTITY_SWITCH" in record["kill_reasons"]


def test_tracker_lifecycle_uses_monotonic_engine_step_across_stage_resets() -> None:
    masks = _pair_masks()
    observer = mech.PassivePairObserver(masks, _assignment())
    state = _synthetic_state(step=100)
    observer.seed_snapshot(state, masks)

    state.step = 101
    writer = observer.advance(state, masks, step=60, stage="WRITER")
    state.step = 102
    settle = observer.advance(state, masks, step=1, stage="WRITER_SETTLE")
    state.step = 103
    probe = observer.advance(state, masks[:2], step=1, stage="PROBE")

    assert [row["stage_step"] for row in (writer, settle, probe)] == [60, 1, 1]
    assert [row["engine_step"] for row in (writer, settle, probe)] == [101, 102, 103]
    assert observer.tracker.tracks[2].died == 103
    assert probe["events"] == {"2": "LOST"}
    for track in observer.tracker.tracks:
        lifecycle_steps = [int(step) for step, _assignment_label in track.assign_history]
        assert lifecycle_steps == sorted(lifecycle_steps)
        assert lifecycle_steps[-3:] == [101, 102, 103]


def test_synthetic_fusion_censors_both_pair_tracks() -> None:
    masks = [_disk(16, 10), _disk(16, 36), _disk(48, 50)]
    observer = mech.PassivePairObserver(masks, _assignment())
    state = _synthetic_state()
    observer.seed_snapshot(state, masks)
    fused = masks[0] | masks[1]
    fused[16, 10:37] = True
    record = observer.advance(
        state,
        [fused, masks[2]],
        step=1,
        stage="SYNTHETIC_FUSION",
    )
    assert record["events"] == {"0": "MERGED", "1": "MERGED"}
    assert "TRACKER_MERGED_T0" in record["kill_reasons"]
    assert "TRACKER_MERGED_T1" in record["kill_reasons"]
    assert "PAIR_GEOMETRY_UNAVAILABLE" in record["kill_reasons"]


def test_passive_logger_matches_an_unlogged_synthetic_continuation() -> None:
    masks = _pair_masks()
    logged = _synthetic_state()
    unlogged = ops.deserialize_state(ops.serialize_state(logged))
    observer = mech.PassivePairObserver(masks, _assignment())
    before = ops.state_sha256(logged)
    seed_record = observer.seed_snapshot(logged, masks)
    assert seed_record["logger_state_unchanged"]
    assert ops.state_sha256(logged) == before == ops.state_sha256(unlogged)

    for step in range(1, 4):
        logged.N = logged.N + 0.001 * step
        unlogged.N = unlogged.N + 0.001 * step
        logged.step += 1
        unlogged.step += 1
        record = observer.advance(logged, masks, step=step, stage="SYNTHETIC_STEP")
        assert record["logger_state_unchanged"]
        assert ops.state_sha256(logged) == ops.state_sha256(unlogged)


def test_tracker_id_relabel_does_not_change_pair_geometry() -> None:
    masks = _pair_masks()
    state = _synthetic_state()
    observer = mech.PassivePairObserver(masks, _assignment())
    before = observer.seed_snapshot(state, masks)["pair_geometry"]
    for index, track in enumerate(observer.tracker.tracks):
        track.id = 700 + index
    after = observer.seed_snapshot(state, masks)["pair_geometry"]
    assert after == before


def test_packed_masks_and_gzip_are_byte_deterministic() -> None:
    mask = _disk(3, 63)
    first = mech.packed_mask(mask)
    second = mech.packed_mask(mask.copy())
    assert first == second
    packed = base64.b64decode(first["data_base64"], validate=True)
    assert hashlib.sha256(packed).hexdigest() == first["sha256"]
    decoded = np.unpackbits(np.frombuffer(packed, dtype=np.uint8), bitorder="little")
    assert np.array_equal(decoded[: N * N].astype(bool).reshape((N, N)), mask)

    payload = mech.canonical_json_bytes({"mechanical_status": "SYNTHETIC"})
    compressed_a = mech.deterministic_gzip(payload)
    compressed_b = mech.deterministic_gzip(payload)
    assert compressed_a == compressed_b
    assert gzip.decompress(compressed_a) == payload
    assert mech.decode_gzip_json(compressed_a) == {"mechanical_status": "SYNTHETIC"}


@pytest.mark.parametrize(
    "forbidden_key",
    ["Y", "y_A", "C_AB", "I_B", "feeding_endpoint", "OutcomeValue", "contrast_pair"],
)
def test_recursive_outcome_firewall_rejects_nested_keys(forbidden_key: str) -> None:
    nested = {"safe": [{"deeper": {forbidden_key: 1.0}}]}
    with pytest.raises(ValueError, match="OUTCOME FIREWALL"):
        mech.assert_outcome_free(nested)


def test_recursive_outcome_firewall_allows_physical_and_mechanical_names() -> None:
    mech.assert_outcome_free(
        {
            "physical": {"c": 0.2, "state_sha256": "a" * 64},
            "mechanical": [{"history_arm": "H10", "component_identity": 0}],
        }
    )


def test_exact_manifest_accepts_only_the_frozen_assignments() -> None:
    valid = _mechanics_manifest()
    assert mech.validate_dev_manifest(valid) is valid
    changed = copy.deepcopy(valid)
    changed["pair_assignments"]["50005"]["target_A"] = 0  # type: ignore[index]
    with pytest.raises(ValueError, match="pair assignments"):
        mech.validate_dev_manifest(changed)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("worlds", [50002, 50004, 50005, True]),
        ("worlds", [50002, 50004, 50005, "50007"]),
        ("worlds", [50002, 50004, 50005, 50005]),
        ("worlds", [50004, 50002, 50005, 50007]),
        ("allowed_seed_namespace", [True, *range(50002, 50011)]),
    ],
)
def test_manifest_rejects_type_duplicate_and_order_changes(
    field: str, replacement: list[object]
) -> None:
    manifest = _mechanics_manifest()
    manifest[field] = replacement
    with pytest.raises(ValueError):
        mech.validate_dev_manifest(manifest)


def test_runner_preflight_module_has_standard_library_imports_only() -> None:
    source_path = Path(runner.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {
        "__future__",
        "argparse",
        "contextlib",
        "hashlib",
        "importlib",
        "json",
        "pathlib",
        "re",
        "subprocess",
        "sys",
        "tempfile",
        "typing",
    }
    assert "experiments" not in imports
    assert "edlab" not in imports
    assert "numpy" not in imports


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["worlds"].__setitem__(3, 50008),
        lambda value: value.__setitem__("unexpected", True),
        lambda value: value["pair_assignments"]["50002"].__setitem__("target_B", 1),
    ],
)
def test_invalid_preflight_never_imports_executor_or_creates_output(
    tmp_path: Path, mutation
) -> None:
    manifest = _runner_manifest()
    mutation(manifest)
    manifest_path = _runner_manifest_path(tmp_path)
    _write_canonical_json(manifest_path, manifest)
    output = tmp_path / runner.EXPECTED_OUTPUT
    executor_name = "experiments.individuation.directed_causal_pair_phase05_executor"
    loaded_before = executor_name in sys.modules
    with mock.patch.object(runner.importlib, "import_module") as importer:
        with pytest.raises(ValueError):
            runner.validate_preflight(tmp_path, manifest_path)
    importer.assert_not_called()
    assert (executor_name in sys.modules) is loaded_before
    assert not output.exists()


@pytest.mark.parametrize("section", ["input_files", "code_files"])
def test_preflight_requires_exact_frozen_binding_paths(tmp_path: Path, section: str) -> None:
    manifest = _runner_manifest()
    expected = (
        runner.EXPECTED_INPUT_PATHS
        if section == "input_files"
        else runner.EXPECTED_CODE_PATHS
    )
    binding = {"sha256": "0" * 64, "git_blob": "0" * 40}
    manifest[section] = {path: dict(binding) for path in sorted(expected)}
    manifest[section]["unexpected-extra-path"] = dict(binding)  # type: ignore[index]
    other = "code_files" if section == "input_files" else "input_files"
    other_expected = (
        runner.EXPECTED_CODE_PATHS
        if other == "code_files"
        else runner.EXPECTED_INPUT_PATHS
    )
    manifest[other] = {path: dict(binding) for path in sorted(other_expected)}
    manifest_path = _runner_manifest_path(tmp_path)
    _write_canonical_json(manifest_path, manifest)
    with (
        mock.patch.object(runner, "_require_ancestor"),
        mock.patch.object(runner, "_require_exact_clean_code_checkout"),
        mock.patch.object(
            runner,
            "_resolve_repo_file",
            side_effect=lambda repo, raw, **_kwargs: repo / Path(raw),
        ),
        mock.patch.object(runner, "_sha256", return_value="0" * 64),
        mock.patch.object(runner, "_git_blob_id", return_value="0" * 40),
    ):
        with pytest.raises(ValueError, match="exact frozen binding set"):
            runner.validate_preflight(tmp_path, manifest_path)


def test_preflight_refuses_in_repo_symlink_before_open(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "linked.json"
    try:
        link.symlink_to(target)
    except OSError:  # Windows without developer-mode symlink permission.
        link.write_text("{}", encoding="utf-8")
        with mock.patch.object(
            runner,
            "_is_link_or_junction",
            side_effect=lambda path: path.name == link.name,
        ):
            with pytest.raises(ValueError, match="symlink|junction"):
                runner._resolve_repo_file(tmp_path, link.name)
            with mock.patch.object(
                Path, "read_bytes", side_effect=AssertionError("link was opened")
            ) as reader:
                with pytest.raises(ValueError, match="symlink|junction"):
                    runner.validate_preflight(tmp_path, link)
            reader.assert_not_called()
        return

    with pytest.raises(ValueError, match="symlink|junction"):
        runner._resolve_repo_file(tmp_path, link.name)
    with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("symlink was opened")) as reader:
        with pytest.raises(ValueError, match="symlink|junction"):
            runner.validate_preflight(tmp_path, link)
    reader.assert_not_called()


def test_preflight_refuses_noncanonical_manifest_path_before_read(tmp_path: Path) -> None:
    manifest_path = tmp_path / "wrong-location.json"
    manifest_path.write_text("{}", encoding="utf-8")
    with mock.patch.object(
        Path, "read_bytes", side_effect=AssertionError("wrong-path manifest was read")
    ) as reader:
        with pytest.raises(ValueError, match="fixed Phase-0.5 path"):
            runner.validate_preflight(tmp_path, manifest_path)
    reader.assert_not_called()


def test_exact_code_checkout_rejects_other_head_and_tracked_dirt(tmp_path: Path) -> None:
    clean = mock.Mock(returncode=0, stdout="", stderr="")
    wrong_head = mock.Mock(returncode=0, stdout="1" * 40 + "\n", stderr="")
    with mock.patch.object(runner.subprocess, "run", side_effect=[wrong_head]):
        with pytest.raises(ValueError, match="exact checked-out HEAD"):
            runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)

    right_head = mock.Mock(returncode=0, stdout="2" * 40 + "\n", stderr="")
    dirty = mock.Mock(returncode=0, stdout=" M tracked.py\n", stderr="")
    with mock.patch.object(runner.subprocess, "run", side_effect=[right_head, dirty]):
        with pytest.raises(ValueError, match="tracked worktree/index"):
            runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)

    with mock.patch.object(runner.subprocess, "run", side_effect=[right_head, clean]):
        runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)


def test_exact_code_checkout_refuses_unbound_namespace_initializer(tmp_path: Path) -> None:
    shadow = tmp_path / "experiments/individuation/__init__.py"
    shadow.parent.mkdir(parents=True)
    shadow.write_text("raise AssertionError('unbound import shadow executed')\n", encoding="utf-8")
    right_head = mock.Mock(returncode=0, stdout="2" * 40 + "\n", stderr="")
    clean = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch.object(runner.subprocess, "run", side_effect=[right_head, clean]):
        with pytest.raises(ValueError, match="unbound import-shadow"):
            runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)


def test_exact_code_checkout_refuses_abi_extension_shadow(tmp_path: Path) -> None:
    suffix = runner.machinery.EXTENSION_SUFFIXES[0]
    relative = Path(
        "experiments/individuation/directed_causal_pair_phase05_executor.py"
    ).with_suffix(suffix).as_posix()
    assert relative in runner.FORBIDDEN_IMPORT_SHADOW_PATHS
    assert "edlab.py" in runner.FORBIDDEN_IMPORT_SHADOW_PATHS
    shadow = tmp_path / relative
    shadow.parent.mkdir(parents=True)
    shadow.write_bytes(b"unbound extension shadow")
    right_head = mock.Mock(returncode=0, stdout="2" * 40 + "\n", stderr="")
    clean = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch.object(runner.subprocess, "run", side_effect=[right_head, clean]):
        with pytest.raises(ValueError, match="unbound import-shadow"):
            runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)


def test_exact_code_checkout_refuses_package_form_module_shadow(tmp_path: Path) -> None:
    relative = (
        "experiments/individuation/"
        "directed_causal_pair_phase05_executor/__init__.py"
    )
    assert relative in runner.FORBIDDEN_IMPORT_SHADOW_PATHS
    shadow = tmp_path / relative
    shadow.parent.mkdir(parents=True)
    shadow.write_text("raise AssertionError('package shadow executed')\n", encoding="utf-8")
    right_head = mock.Mock(returncode=0, stdout="2" * 40 + "\n", stderr="")
    clean = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch.object(runner.subprocess, "run", side_effect=[right_head, clean]):
        with pytest.raises(ValueError, match="unbound import-shadow"):
            runner._require_exact_clean_code_checkout(tmp_path, "2" * 40)


def test_executor_import_uses_fresh_external_bytecode_cache() -> None:
    previous_prefix = sys.pycache_prefix
    previous_dont_write = sys.dont_write_bytecode
    with runner._isolated_import_cache():
        cache = Path(str(sys.pycache_prefix))
        assert cache.is_dir()
        assert not cache.is_relative_to(Path(runner.__file__).resolve().parents[2])
        assert sys.dont_write_bytecode is True
        assert list(cache.iterdir()) == []
    assert sys.pycache_prefix == previous_prefix
    assert sys.dont_write_bytecode is previous_dont_write


def test_verified_repo_root_is_available_only_inside_executor_import_context() -> None:
    repo = Path(runner.__file__).resolve().parents[2]
    previous = list(sys.path)
    try:
        sys.path[:] = [entry for entry in sys.path if Path(entry or ".").resolve() != repo]
        without_repo = list(sys.path)
        with runner._bound_repo_import_path(repo):
            assert Path(sys.path[0]).resolve() == repo
        assert sys.path == without_repo
    finally:
        sys.path[:] = previous


@pytest.mark.parametrize(
    "wrong_output",
    [
        r"docs\individuation\DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW",
        "docs/individuation/./DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW",
    ],
)
def test_preflight_requires_exact_output_path_string(
    tmp_path: Path, wrong_output: str
) -> None:
    manifest = _runner_manifest()
    manifest["output_directory"] = wrong_output
    manifest_path = _runner_manifest_path(tmp_path)
    _write_canonical_json(manifest_path, manifest)
    with (
        mock.patch.object(runner, "_require_ancestor"),
        mock.patch.object(runner, "_require_exact_clean_code_checkout"),
    ):
        with pytest.raises(ValueError, match="fixed Phase-0.5 raw directory"):
            runner.validate_preflight(tmp_path, manifest_path)


def test_executor_local_import_closure_is_hash_bound() -> None:
    repo = Path(runner.__file__).resolve().parents[2]
    probe = r'''
import importlib
import json
from pathlib import Path
import sys

repo = Path.cwd().resolve()
importlib.import_module("experiments.individuation.directed_causal_pair_phase05_executor")
loaded = set()
for module_name, module in tuple(sys.modules.items()):
    if not (
        module_name == "edlab"
        or module_name.startswith("edlab.")
        or module_name.startswith("experiments.individuation.")
    ):
        continue
    source = getattr(module, "__file__", None)
    if source is None:
        continue
    resolved = Path(source).resolve()
    if resolved.suffix == ".py" and resolved.is_relative_to(repo):
        loaded.add(resolved.relative_to(repo).as_posix())
print(json.dumps(sorted(loaded)))
'''
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    loaded_local_sources = set(json.loads(completed.stdout))
    assert loaded_local_sources <= runner.EXPECTED_CODE_PATHS


def test_forbidden_namespace_decoy_path_is_rejected_before_read(tmp_path: Path) -> None:
    decoy = tmp_path / "synthetic-58001-decoy.json"
    with mock.patch.object(Path, "read_text", side_effect=AssertionError("decoy was read")) as reader:
        with pytest.raises(PermissionError, match="58xxx"):
            mech.safe_read_json(decoy, [decoy])
    reader.assert_not_called()
    assert not decoy.exists()


def test_namespace_guard_does_not_parse_opaque_crypto_identities() -> None:
    digest = "a58001" + "b" * 58
    assert len(digest) == 64
    assert not runner._contains_58(digest)
    assert not mech._contains_58_namespace(digest)
    assert runner._contains_58("seed-58001.json")
    assert mech._contains_58_namespace("seed-58001.json")


def test_ordered_prefix_accepts_valid_prefix_and_rejects_hole(tmp_path: Path) -> None:
    index = mech.new_ordered_prefix_index("a" * 64)
    index["completed"] = [
        _prefix_row(tmp_path, 0, 50002, b"first"),
        _prefix_row(tmp_path, 1, 50004, b"second"),
    ]
    mech.validate_ordered_prefix(index, mech.FROZEN_PAIR_WORLDS, tmp_path)

    hole = copy.deepcopy(index)
    hole["completed"][1]["world_id"] = 50005
    with pytest.raises(ValueError, match="ordered prefix"):
        mech.validate_ordered_prefix(hole, mech.FROZEN_PAIR_WORLDS, tmp_path)


def test_ordered_prefix_rejects_shard_tamper(tmp_path: Path) -> None:
    index = mech.new_ordered_prefix_index("b" * 64)
    row = _prefix_row(tmp_path, 0, 50002, b"alpha")
    index["completed"] = [row]
    mech.validate_ordered_prefix(index, mech.FROZEN_PAIR_WORLDS, tmp_path)
    (tmp_path / row["path"]).write_bytes(b"omega")
    with pytest.raises(ValueError, match="hash mismatch"):
        mech.validate_ordered_prefix(index, mech.FROZEN_PAIR_WORLDS, tmp_path)


def test_ordered_prefix_rejects_tampered_declared_plan(tmp_path: Path) -> None:
    index = mech.new_ordered_prefix_index("c" * 64)
    index["completed"] = [_prefix_row(tmp_path, 0, 50002, b"first")]
    index["plan"] = [50002, 50005, 50004, 50007]
    with pytest.raises(ValueError, match="plan"):
        mech.validate_ordered_prefix(index, mech.FROZEN_PAIR_WORLDS, tmp_path)


def test_ordered_prefix_rejects_path_escape(tmp_path: Path) -> None:
    root = tmp_path / "raw"
    root.mkdir()
    outside = tmp_path / "outside.gz"
    outside.write_bytes(b"outside")
    index = mech.new_ordered_prefix_index("d" * 64)
    index["completed"] = [
        {
            "sequence_index": 0,
            "world_id": 50002,
            "path": "../outside.gz",
            "sha256": hashlib.sha256(b"outside").hexdigest(),
            "size_bytes": len(b"outside"),
        }
    ]
    with pytest.raises(ValueError, match="path"):
        mech.validate_ordered_prefix(index, mech.FROZEN_PAIR_WORLDS, root)


def test_exact_isolation_uses_the_rho_weighted_collar_core() -> None:
    from experiments.individuation import access_structure_noswap_operators as ns
    from experiments.individuation import directed_causal_pair_phase05_executor as executor

    state = _synthetic_state()
    masks = _pair_masks()
    state.rho.fill(0.20)
    for mask in masks:
        ys, xs = np.nonzero(mask)
        state.rho[ys, xs] = np.linspace(0.31, 1.0, len(ys))

    weighted_center = mech.periodic_centroid(masks[0], state.rho)
    _partition, expected_core, collar = ns.core_and_collar(
        state.rho.shape,
        weighted_center,
    )
    unweighted_core = mech.disk_mask(
        state.rho.shape,
        mech.periodic_centroid(masks[0]),
        ns.CORE_RADIUS,
    )
    assert not np.array_equal(unweighted_core, expected_core)

    core, outside = executor._isolation_supports(
        state=state,
        masks=masks,
        recipient_index=0,
        collar=collar,
    )
    assert np.array_equal(core, expected_core)
    for mask in masks[1:]:
        protected = mech.disk_mask(
            state.rho.shape,
            mech.periodic_centroid(mask, state.rho),
            mech.HALO_RADIUS,
        )
        assert not np.any(outside & protected)
