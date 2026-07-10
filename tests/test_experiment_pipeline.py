import json
import math
from pathlib import Path

import pytest

from edlab.experiments import streaming as streaming_module
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
