import csv
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from edlab.experiments import streaming as streaming_module
from edlab.experiments.analyze_streaming import (
    _candidate_direct_diagnostic,
    analyze_streaming_screen,
    qualify_run_candidate_rows,
)
from edlab.experiments.baseline import BaselineConfig, halton_point, run_baseline
from edlab.experiments.streaming import RAW_FILENAMES, run_streaming_screen


def test_halton_is_deterministic() -> None:
    assert (halton_point(32, 5) == halton_point(32, 5)).all()
    assert not (halton_point(32, 5) == halton_point(33, 5)).all()


def test_tiny_baseline_writes_reproducible_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "tiny"
    summary = run_baseline(
        output_dir=output,
        experiment_id="TEST-TINY",
        git_commit="fixture-sha",
        config=BaselineConfig(
            n_laws=1,
            seeds=(7,),
            n_particles=16,
            n_types=2,
            steps=30,
            snapshot_cadences=(10, 30),
            lag_indices=(1,),
        ),
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert summary["runs"] == 1
    assert manifest["git_commit"] == "fixture-sha"
    assert manifest["sampling"]["method"] == "Halton low-discrepancy sequence"
    assert manifest["sampling"]["probability_estimate"] is False
    for filename in (
        "laws.json",
        "measurements.csv",
        "lineage_events.csv",
        "association_edges.csv",
        "entity_observations.csv",
        "summary.json",
        "summary.md",
        "manifest.json",
    ):
        assert (output / filename).exists()


def test_streaming_shard_is_byte_equivalent_and_resumable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = BaselineConfig(
        n_laws=1,
        seeds=(7,),
        n_particles=64,
        n_types=2,
        steps=60,
        snapshot_cadences=(10, 30),
        lag_indices=(1,),
    )
    full_output = tmp_path / "full"
    stream_output = tmp_path / "stream"
    full_summary = run_baseline(
        output_dir=full_output,
        experiment_id="TEST-EQUIVALENCE-FULL",
        git_commit="fixture-sha",
        config=config,
    )
    stream_summary = run_streaming_screen(
        output_dir=stream_output,
        experiment_id="TEST-EQUIVALENCE-STREAM",
        git_commit="fixture-sha",
        config=config,
        reservoir_size=16,
    )
    shard = stream_output / "raw" / "runs" / "law-0000_seed-7"
    assert stream_summary["runs"] == full_summary["runs"] == 1
    assert stream_summary["measurement_rows"] == full_summary["measurement_rows"]
    assert stream_summary["measurement_rows"] > 0
    assert stream_summary["initial_probe"] == full_summary["initial_probe"]
    assert math.isclose(
        stream_summary["correlation_p_m_descriptive_only"],
        full_summary["correlation_p_m_descriptive_only"],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
    for filename in RAW_FILENAMES:
        assert (shard / filename).read_bytes() == (full_output / filename).read_bytes()

    raw_before = {
        filename: (shard / filename).read_bytes() for filename in RAW_FILENAMES
    }

    def fail_if_recomputed(**_kwargs: object) -> object:
        raise AssertionError("a complete verified shard must be resumed, not recomputed")

    monkeypatch.setattr(streaming_module, "_execute_one_run", fail_if_recomputed)
    resumed = run_streaming_screen(
        output_dir=stream_output,
        experiment_id="TEST-EQUIVALENCE-STREAM",
        git_commit="fixture-sha",
        config=config,
        reservoir_size=16,
    )
    assert resumed == stream_summary
    for filename in RAW_FILENAMES:
        assert (shard / filename).read_bytes() == raw_before[filename]


def test_streaming_rejects_plan_drift_and_corrupt_shards(tmp_path: Path) -> None:
    output = tmp_path / "stream"
    config = BaselineConfig(
        n_laws=1,
        seeds=(7,),
        n_particles=32,
        n_types=2,
        steps=30,
        snapshot_cadences=(10, 30),
        lag_indices=(1,),
    )
    run_streaming_screen(
        output_dir=output,
        experiment_id="TEST-INTEGRITY",
        git_commit="fixture-sha",
        config=config,
        reservoir_size=8,
    )
    with pytest.raises(RuntimeError, match="different experiment plan"):
        run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-INTEGRITY",
            git_commit="different-sha",
            config=config,
            reservoir_size=8,
        )
    with pytest.raises(RuntimeError, match="different experiment plan"):
        run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-INTEGRITY",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=9,
        )

    measurement_path = (
        output / "raw" / "runs" / "law-0000_seed-7" / "measurements.csv"
    )
    measurement_path.write_bytes(measurement_path.read_bytes() + b"corruption")
    with pytest.raises(RuntimeError, match="checksum failure"):
        run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-INTEGRITY",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=8,
        )


def test_streaming_final_manifest_is_last_and_crash_resume_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "stream"
    config = BaselineConfig(
        n_laws=1,
        seeds=(7,),
        n_particles=64,
        n_types=2,
        steps=60,
        snapshot_cadences=(10, 30),
        lag_indices=(1,),
    )

    def injected_finalizer_crash(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("INJECTED_FINALIZER_CRASH")

    with monkeypatch.context() as patcher:
        patcher.setattr(
            streaming_module, "_atomic_plot_sample", injected_finalizer_crash
        )
        with pytest.raises(RuntimeError, match="INJECTED_FINALIZER_CRASH"):
            run_streaming_screen(
                output_dir=output,
                experiment_id="TEST-CRASH-RESUME",
                git_commit="fixture-sha",
                config=config,
                reservoir_size=8,
            )

    shard = output / "raw" / "runs" / "law-0000_seed-7"
    assert (shard / "run_manifest.json").is_file()
    assert not (output / "manifest.json").exists()

    orphan = output / "raw" / "runs" / ".law-0000_seed-7-abrupt-process-exit"
    orphan.mkdir()
    (orphan / "unpublished.marker").write_text("not committed", encoding="utf-8")
    unlogged_quarantine = output / "raw" / "quarantine" / "prior-unlogged"
    unlogged_quarantine.mkdir(parents=True)
    (unlogged_quarantine / "prior.marker").write_text("preserve", encoding="utf-8")
    recovery_log_temp = output / "raw" / ".recovery_log.json-double-crash.tmp"
    recovery_log_temp.write_text("partial recovery log", encoding="utf-8")

    def fail_if_recomputed(**_kwargs: object) -> object:
        raise AssertionError("verified completed raw shard must not be recomputed")

    with monkeypatch.context() as patcher:
        patcher.setattr(streaming_module, "_execute_one_run", fail_if_recomputed)
        summary = run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-CRASH-RESUME",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=8,
        )

    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "COMPLETE"
    assert manifest["expected_runs"] == manifest["completed_runs"] == 1
    assert manifest["completion"] == {
        "all_planned_runs_present": True,
        "all_shards_verified": True,
        "derived_outputs_published_atomically": True,
        "manifest_published_last": True,
    }
    assert summary["raw_row_counts"] == manifest["raw_row_counts"]
    assert manifest["recovery"]["events_this_invocation"] == 3
    recovery_log = json.loads(
        (output / "raw" / "recovery_log.json").read_text(encoding="utf-8")
    )
    assert {event["kind"] for event in recovery_log} == {
        "UNPUBLISHED_TEMP_QUARANTINED",
        "QUARANTINE_INVENTORY_RECONCILED",
    }
    unpublished_event = next(
        event
        for event in recovery_log
        if event["source"]
        == "raw/runs/.law-0000_seed-7-abrupt-process-exit"
    )
    assert (
        output / unpublished_event["target"] / "unpublished.marker"
    ).read_text(encoding="utf-8") == "not committed"
    reconciled_event = next(
        event
        for event in recovery_log
        if event["kind"] == "QUARANTINE_INVENTORY_RECONCILED"
    )
    assert reconciled_event["target"] == "raw/quarantine/prior-unlogged"

    manifest_before = manifest_path.read_bytes()

    def fail_if_rewritten(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("verified COMPLETE experiment must not be rewritten")

    with monkeypatch.context() as patcher:
        patcher.setattr(streaming_module, "_execute_one_run", fail_if_recomputed)
        patcher.setattr(streaming_module, "_atomic_write_json", fail_if_rewritten)
        resumed = run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-CRASH-RESUME",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=8,
        )
    assert resumed == summary
    assert manifest_path.read_bytes() == manifest_before
    post_complete_temp = output / "raw" / ".recovery_log.json-post-complete.tmp"
    post_complete_temp.write_text("unexpected", encoding="utf-8")
    with pytest.raises(RuntimeError, match="orphan temporary work"):
        run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-CRASH-RESUME",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=8,
        )


def test_streaming_complete_manifest_rejects_derived_output_drift(tmp_path: Path) -> None:
    output = tmp_path / "stream"
    config = BaselineConfig(
        n_laws=1,
        seeds=(7,),
        n_particles=32,
        n_types=2,
        steps=30,
        snapshot_cadences=(10, 30),
        lag_indices=(1,),
    )
    run_streaming_screen(
        output_dir=output,
        experiment_id="TEST-DERIVED-INTEGRITY",
        git_commit="fixture-sha",
        config=config,
        reservoir_size=8,
    )
    summary_markdown = output / "summary.md"
    summary_markdown.write_text(
        summary_markdown.read_text(encoding="utf-8") + "\ncorruption\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="committed output verification failure"):
        run_streaming_screen(
            output_dir=output,
            experiment_id="TEST-DERIVED-INTEGRITY",
            git_commit="fixture-sha",
            config=config,
            reservoir_size=8,
        )


def test_streaming_recovers_after_real_process_exit_before_shard_publish(
    tmp_path: Path,
) -> None:
    output = tmp_path / "abrupt"
    child_code = r'''
import os
import sys
from pathlib import Path
from edlab.experiments.baseline import BaselineConfig
from edlab.experiments.streaming import run_streaming_screen

def crash_before_publish(_temp_dir: Path) -> None:
    os._exit(73)

run_streaming_screen(
    output_dir=Path(sys.argv[1]),
    experiment_id="TEST-REAL-PROCESS-EXIT",
    git_commit="fixture-sha",
    config=BaselineConfig(
        n_laws=1,
        seeds=(7,),
        n_particles=32,
        n_types=2,
        steps=30,
        snapshot_cadences=(10, 30),
        lag_indices=(1,),
    ),
    reservoir_size=8,
    _before_shard_publish=crash_before_publish,
)
'''
    child = subprocess.run(
        [sys.executable, "-c", child_code, str(output)],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert child.returncode == 73, child.stderr
    orphan_dirs = [
        path
        for path in (output / "raw" / "runs").iterdir()
        if path.name.startswith(".law-")
    ]
    assert len(orphan_dirs) == 1
    assert not (output / "manifest.json").exists()

    summary = run_streaming_screen(
        output_dir=output,
        experiment_id="TEST-REAL-PROCESS-EXIT",
        git_commit="fixture-sha",
        config=BaselineConfig(
            n_laws=1,
            seeds=(7,),
            n_particles=32,
            n_types=2,
            steps=30,
            snapshot_cadences=(10, 30),
            lag_indices=(1,),
        ),
        reservoir_size=8,
    )
    assert summary["runs"] == 1
    assert summary["recovery"]["events_this_invocation"] == 1
    assert json.loads((output / "manifest.json").read_text(encoding="utf-8"))[
        "status"
    ] == "COMPLETE"


def test_streaming_multi_run_index_and_raw_totals_are_consistent(tmp_path: Path) -> None:
    output = tmp_path / "multi"
    summary = run_streaming_screen(
        output_dir=output,
        experiment_id="TEST-MULTI-RUN-INDEX",
        git_commit="fixture-sha",
        config=BaselineConfig(
            n_laws=2,
            seeds=(7, 8),
            n_particles=32,
            n_types=2,
            steps=30,
            snapshot_cadences=(10, 30),
            lag_indices=(1,),
        ),
        reservoir_size=8,
    )
    raw_index = json.loads((output / "raw_index.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert summary["runs"] == manifest["expected_runs"] == 4
    assert manifest["completed_runs"] == 4
    assert {entry["run_key"] for entry in raw_index} == {
        "law-0000_seed-7",
        "law-0000_seed-8",
        "law-0001_seed-7",
        "law-0001_seed-8",
    }
    totals = {
        filename: sum(entry["row_counts"][filename] for entry in raw_index)
        for filename in RAW_FILENAMES
    }
    assert summary["raw_row_counts"] == manifest["raw_row_counts"] == totals
    aggregate_rows = list(
        csv.DictReader(
            (output / "measurement_aggregates.csv").open(
                newline="", encoding="utf-8"
            )
        )
    )
    assert all(int(row["lag_snapshots"]) == 1 for row in aggregate_rows)
    assert len(
        {
            (
                row["law_index"],
                row["seed"],
                row["snapshot_cadence"],
                row["lag_snapshots"],
            )
            for row in aggregate_rows
        }
    ) == len(aggregate_rows)


def test_candidate_gate_cleans_each_cadence_before_endpoint_join() -> None:
    def row(cadence: int, track_id: int, p_value: float = 0.9) -> dict[str, str]:
        return {
            "law_index": "5",
            "seed": "2001",
            "snapshot_cadence": str(cadence),
            "track_id": str(track_id),
            "start_step": "0",
            "end_step": "60",
            "phenotype_continuity": str(p_value),
            "material_retention": "0.4",
            "interval_has_ambiguity": "False",
            "interval_has_split_or_merge": "False",
        }

    rows = [row(10, 1), row(30, 2), row(60, 3, p_value=0.8)]
    observation_counts = {(10, 1): 8, (30, 2): 8, (60, 3): 8}
    rejected_rows, rejected_endpoints = qualify_run_candidate_rows(
        rows,
        observation_counts=observation_counts,
        complex_tracks={(30, 2)},
    )
    assert rejected_rows == []
    assert rejected_endpoints == set()

    accepted_rows, accepted_endpoints = qualify_run_candidate_rows(
        rows,
        observation_counts=observation_counts,
        complex_tracks=set(),
    )
    assert len(accepted_rows) == 2
    assert accepted_endpoints == {(5, 2001, 0, 60)}
    assert {row["snapshot_cadence"] for row in accepted_rows} == {"10", "30"}
    assert all(row["unresolved_sparse_alias_risk"] for row in accepted_rows)


def test_candidate_direct_diagnostic_recomputes_pm_and_periodic_motion() -> None:
    candidate = {
        "law_index": 5,
        "seed": 2001,
        "snapshot_cadence": 10,
        "track_id": 1,
        "start_step": 0,
        "end_step": 20,
        "phenotype_continuity": 1.0,
        "material_retention": 1.0 / 3.0,
    }
    observations = [
        {
            "snapshot_cadence": "10",
            "track_id": "1",
            "step": str(step),
            "centroid_json": json.dumps(centroid),
            "particle_ids_json": json.dumps(ids),
            "phenotype_vector_json": json.dumps([0.2, 0.4]),
        }
        for step, centroid, ids in (
            (0, [0.95, 0.05], [1, 2]),
            (10, [0.99, 0.05], [1, 2]),
            (20, [0.02, 0.05], [2, 3]),
        )
    ]
    edges = [
        {
            "snapshot_cadence": "10",
            "parent_track_id": "1",
            "snapshot_step": str(step),
            "selected": "True",
            "distance_gate_passed": "True",
            "size_gate_passed": "True",
            "centroid_distance": str(distance),
            "score": "0.9",
            "classification": "unique_candidate",
        }
        for step, distance in ((10, 0.04), (20, 0.03))
    ]
    result = _candidate_direct_diagnostic(
        candidate,
        observations=observations,
        association_edges=edges,
        box_size=1.0,
    )
    assert math.isclose(result["centroid_path_length"], 0.07, abs_tol=1e-12)
    assert math.isclose(result["centroid_net_displacement"], 0.07, abs_tol=1e-12)
    assert result["material_retention_absolute_error"] == 0.0
    assert result["phenotype_continuity_absolute_error"] == 0.0
    assert result["selected_edge_transitions"] == 2
    assert result["compatible_unselected_edges"] == 0
    assert result["static_occupancy_or_lookalike_alias_rejected"] is False


def test_chunk_aware_analysis_writes_auditable_outputs(tmp_path: Path) -> None:
    output = tmp_path / "analysis-fixture"
    screen_summary = run_streaming_screen(
        output_dir=output,
        experiment_id="TEST-ANALYSIS",
        git_commit="parent-fixture-sha",
        config=BaselineConfig(
            n_laws=1,
            seeds=(7,),
            n_particles=64,
            n_types=2,
            steps=60,
            snapshot_cadences=(10, 30),
            lag_indices=(1,),
        ),
        reservoir_size=8,
    )
    analysis = analyze_streaming_screen(
        output,
        analysis_git_commit="analysis-fixture-sha",
        analysis_git_scope_clean=True,
    )
    analysis_dir = output / "analysis"
    analysis_manifest = json.loads(
        (analysis_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )
    assert analysis["measurements"] == screen_summary["measurement_rows"]
    assert analysis["integrity"]["runs"] == 1
    assert analysis["integrity"]["non_finite_measurement_rows"] == 0
    assert analysis_manifest["status"] == "COMPLETE"
    assert analysis_manifest["parent_git_commit"] == "parent-fixture-sha"
    for filename in (
        "pm_joint_density.csv",
        "measurement_aggregates_corrected.csv",
        "pm_by_cadence_tau.csv",
        "pm_by_cadence_tau_flags.csv",
        "law_screening.csv",
        "lineage_summary.csv",
        "cross_cadence_candidate_rows.csv",
        "eligible_candidate_direct_diagnostics.csv",
        "eligible_candidate_direct_by_law.csv",
        "pareto_frontier.csv",
        "law_parameter_correlations.csv",
        "exp02_analysis_summary.json",
        "exp02_analysis_summary.md",
        "pm_joint_density.png",
        "probe_by_cadence_tau.png",
        "law_probe_fraction.png",
    ):
        assert (analysis_dir / filename).exists()
    all_headers = "\n".join(
        path.read_text(encoding="utf-8").splitlines()[0] if path.stat().st_size else ""
        for path in analysis_dir.glob("*.csv")
    )
    assert "theseus_score" not in all_headers
    assert "memory_score" not in all_headers
