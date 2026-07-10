import json
from pathlib import Path

from edlab.experiments.baseline import BaselineConfig, halton_point, run_baseline


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
    for filename in (
        "laws.json",
        "measurements.csv",
        "lineage_events.csv",
        "entity_observations.csv",
        "summary.json",
        "summary.md",
        "manifest.json",
    ):
        assert (output / filename).exists()
