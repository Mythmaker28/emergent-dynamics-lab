"""Resumable per-run shard writer for large regime screens such as EXP02."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import shutil
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable, Iterable

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..entities.detection import detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import measure_tracks
from ..specs import DetectionSpec, PhenotypeSpec, RunSpec, TrackerSpec, WorldSpec
from ..substrates.particle_dynamics.engine import initialize_world, simulate
from ..validation.forces import validate_force_paths
from ..validation.nulls import (
    id_permutation_null,
    sparse_lookalike_alias_null,
    static_motif_material_flux_null,
    tracker_cadence_sensitivity_null,
)
from .baseline import BaselineConfig, _hash_file, _write_csv, law_from_halton


RAW_FILENAMES = (
    "measurements.csv",
    "lineage_events.csv",
    "entity_observations.csv",
    "association_edges.csv",
)
RAW_SCHEMA_VERSION = 1
DISK_BYTES_PER_REMAINING_RUN = 4 * 1024 * 1024
FINALIZATION_HEADROOM_BYTES = 512 * 1024 * 1024


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


def _atomic_write_json(path: Path, value: Any) -> None:
    _atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True))


def _atomic_write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        _write_csv(temp_path, rows)
        with temp_path.open("r+b") as handle:
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def _csv_data_row_count(path: Path) -> int:
    if path.stat().st_size == 0:
        return 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _row in reader)


def _disk_preflight(output_dir: Path, remaining_runs: int) -> dict[str, int]:
    free_bytes = shutil.disk_usage(output_dir).free
    required_free_bytes = (
        FINALIZATION_HEADROOM_BYTES
        + remaining_runs * DISK_BYTES_PER_REMAINING_RUN
    )
    if free_bytes < required_free_bytes:
        raise RuntimeError(
            "insufficient disk headroom for streaming screen: "
            f"free={free_bytes}, required={required_free_bytes}, "
            f"remaining_runs={remaining_runs}"
        )
    return {
        "free_bytes_at_preflight": free_bytes,
        "required_free_bytes": required_free_bytes,
        "remaining_runs_at_preflight": remaining_runs,
        "assumed_bytes_per_remaining_run": DISK_BYTES_PER_REMAINING_RUN,
        "finalization_headroom_bytes": FINALIZATION_HEADROOM_BYTES,
    }


def _orphan_work_paths(output_dir: Path, raw_root: Path) -> list[Path]:
    top_level = [
        path
        for path in output_dir.iterdir()
        if path.name.startswith(".") and path.name.endswith(".tmp")
    ]
    raw_temps = (
        [path for path in raw_root.iterdir() if path.name.startswith(".law-")]
        if raw_root.exists()
        else []
    )
    raw_dir = output_dir / "raw"
    raw_atomic_temps = (
        [
            path
            for path in raw_dir.iterdir()
            if path.name.startswith(".") and path.name.endswith(".tmp")
        ]
        if raw_dir.exists()
        else []
    )
    return sorted(top_level + raw_temps + raw_atomic_temps, key=lambda path: str(path))


def _quarantine_orphan_work(output_dir: Path, raw_root: Path) -> dict[str, Any]:
    orphan_paths = _orphan_work_paths(output_dir, raw_root)
    log_path = output_dir / "raw" / "recovery_log.json"
    history: list[dict[str, Any]] = []
    if log_path.exists():
        history = json.loads(log_path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            raise RuntimeError("invalid raw recovery log")
    quarantine_root = output_dir / "raw" / "quarantine"
    new_events: list[dict[str, Any]] = []
    for source in orphan_paths:
        quarantine_root.mkdir(parents=True, exist_ok=True)
        target = quarantine_root / source.name.lstrip(".")
        suffix = 1
        while target.exists():
            target = quarantine_root / f"{source.name.lstrip('.')}-{suffix}"
            suffix += 1
        os.replace(source, target)
        event = {
            "kind": "UNPUBLISHED_TEMP_QUARANTINED",
            "source": str(source.relative_to(output_dir)).replace("\\", "/"),
            "target": str(target.relative_to(output_dir)).replace("\\", "/"),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        history.append(event)
        new_events.append(event)
    logged_targets = {
        event.get("target") for event in history if isinstance(event, dict)
    }
    if quarantine_root.exists():
        for target in sorted(quarantine_root.iterdir(), key=lambda path: path.name):
            relative_target = str(target.relative_to(output_dir)).replace("\\", "/")
            if relative_target in logged_targets:
                continue
            event = {
                "kind": "QUARANTINE_INVENTORY_RECONCILED",
                "source": None,
                "target": relative_target,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
            history.append(event)
            new_events.append(event)
    if new_events:
        _atomic_write_json(log_path, history)
    return {
        "events_total": len(history),
        "events_this_invocation": len(new_events),
        "log_relative_path": (
            str(log_path.relative_to(output_dir)).replace("\\", "/")
            if log_path.exists()
            else None
        ),
        "log_sha256": _hash_file(log_path) if log_path.exists() else None,
        "log_size": log_path.stat().st_size if log_path.exists() else 0,
    }


@dataclass
class _OnlineCovariance:
    count: int = 0
    mean_x: float = 0.0
    mean_y: float = 0.0
    sum_square_x: float = 0.0
    sum_square_y: float = 0.0
    sum_cross: float = 0.0

    def update(self, x_value: float, y_value: float) -> None:
        self.count += 1
        delta_x = x_value - self.mean_x
        self.mean_x += delta_x / self.count
        delta_y = y_value - self.mean_y
        self.mean_y += delta_y / self.count
        self.sum_square_x += delta_x * (x_value - self.mean_x)
        self.sum_square_y += delta_y * (y_value - self.mean_y)
        self.sum_cross += delta_x * (y_value - self.mean_y)

    def correlation(self) -> float | None:
        denominator = self.sum_square_x * self.sum_square_y
        if self.count < 2 or denominator <= 0.0:
            return None
        return self.sum_cross / math.sqrt(denominator)


def _run_key(law_index: int, seed: int) -> str:
    return f"law-{law_index:04d}_seed-{seed}"


def _planned_law_indices(config: BaselineConfig) -> tuple[int, ...]:
    return (
        tuple(range(config.n_laws))
        if config.law_indices is None
        else tuple(config.law_indices)
    )


def _execute_one_run(
    *,
    law_index: int,
    seed: int,
    config: BaselineConfig,
    world: WorldSpec,
    detection: DetectionSpec,
    phenotype_spec: PhenotypeSpec,
    tracker_spec: TrackerSpec,
) -> dict[str, list[dict[str, Any]]]:
    law = law_from_halton(law_index, config.n_types)
    base_cadence = min(config.snapshot_cadences)
    run = RunSpec(
        seed=seed,
        dt=config.dt,
        steps=config.steps,
        snapshot_interval=base_cadence,
        backend="vectorized",
    )
    initial = initialize_world(world, seed + 100_000 * law_index)
    snapshots = simulate(initial, law, world, run)
    entities_by_step = {
        snapshot.step: detect_entities(
            snapshot.state,
            snapshot_step=snapshot.step,
            time=snapshot.time,
            world=world,
            detection=detection,
            phenotype_spec=phenotype_spec,
        )
        for snapshot in snapshots
    }

    measurement_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    association_rows: list[dict[str, Any]] = []
    for cadence in config.snapshot_cadences:
        tracker = LineageTracker(tracker_spec, box_size=world.box_size)
        for snapshot in snapshots:
            if snapshot.step % cadence:
                continue
            tracked = tracker.update(
                entities_by_step[snapshot.step],
                snapshot_step=snapshot.step,
                time=snapshot.time,
            )
            for item in tracked:
                entity = item.entity
                observation_rows.append(
                    {
                        "law_index": law_index,
                        "seed": seed,
                        "snapshot_cadence": cadence,
                        "track_id": item.track_id,
                        "local_index": entity.local_index,
                        "step": entity.snapshot_step,
                        "time": entity.time,
                        "centroid_json": json.dumps(entity.centroid.tolist()),
                        "particle_ids_json": json.dumps(sorted(entity.particle_ids)),
                        "phenotype_vector_json": json.dumps(
                            entity.phenotype.vector.tolist()
                        ),
                        "phenotype_raw_json": json.dumps(
                            entity.phenotype.raw, sort_keys=True
                        ),
                    }
                )
        for measurement in measure_tracks(
            tracker.tracks,
            lag_indices=config.lag_indices,
            events=tracker.events,
        ):
            row = asdict(measurement)
            row.update(
                {
                    "law_index": law_index,
                    "seed": seed,
                    "snapshot_cadence": cadence,
                }
            )
            measurement_rows.append(row)
        for event in tracker.events:
            event_rows.append(
                {
                    "law_index": law_index,
                    "seed": seed,
                    "snapshot_cadence": cadence,
                    "kind": event.kind,
                    "snapshot_step": event.snapshot_step,
                    "time": event.time,
                    "parent_track_ids_json": json.dumps(event.parent_track_ids),
                    "child_track_ids_json": json.dumps(event.child_track_ids),
                    "detail": event.detail,
                }
            )
        for edge in tracker.association_edges:
            association_rows.append(
                {
                    "law_index": law_index,
                    "seed": seed,
                    "snapshot_cadence": cadence,
                    **asdict(edge),
                }
            )
    return {
        "measurements.csv": measurement_rows,
        "lineage_events.csv": event_rows,
        "entity_observations.csv": observation_rows,
        "association_edges.csv": association_rows,
    }


def _write_shard_atomic(
    *,
    run_root: Path,
    run_key: str,
    rows_by_file: dict[str, list[dict[str, Any]]],
    law_index: int,
    seed: int,
    input_sha256: str,
    before_publish: Callable[[Path], None] | None = None,
) -> Path:
    final_dir = run_root / run_key
    if final_dir.exists():
        manifest_path = final_dir / "run_manifest.json"
        if manifest_path.exists():
            return final_dir
        raise RuntimeError(f"incomplete existing shard requires audit: {final_dir}")
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_key}-", dir=run_root))
    try:
        row_counts: dict[str, int] = {}
        hashes: dict[str, str] = {}
        sizes: dict[str, int] = {}
        for filename in RAW_FILENAMES:
            path = temp_dir / filename
            rows = rows_by_file[filename]
            _write_csv(path, rows)
            with path.open("r+b") as handle:
                handle.flush()
                os.fsync(handle.fileno())
            row_counts[filename] = len(rows)
            hashes[filename] = _hash_file(path)
            sizes[filename] = path.stat().st_size
        _atomic_write_json(
            temp_dir / "run_manifest.json",
            {
                "law_index": law_index,
                "seed": seed,
                "raw_schema_version": RAW_SCHEMA_VERSION,
                "input_sha256": input_sha256,
                "row_counts": row_counts,
                "sha256": hashes,
                "sizes": sizes,
                "complete": True,
            },
        )
        if before_publish is not None:
            before_publish(temp_dir)
        os.replace(temp_dir, final_dir)
    except BaseException:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    return final_dir


def _verify_shard(
    shard: Path,
    *,
    law_index: int,
    seed: int,
    input_sha256: str,
) -> dict[str, Any]:
    manifest_path = shard / "run_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"incomplete existing shard requires audit: {shard}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_identity = {
        "law_index": law_index,
        "seed": seed,
        "raw_schema_version": RAW_SCHEMA_VERSION,
        "input_sha256": input_sha256,
        "complete": True,
    }
    for key, expected in expected_identity.items():
        if manifest.get(key) != expected:
            raise RuntimeError(
                f"shard identity mismatch for {shard}: {key}={manifest.get(key)!r}, "
                f"expected {expected!r}"
            )
    for filename in RAW_FILENAMES:
        path = shard / filename
        if not path.is_file():
            raise RuntimeError(f"missing raw shard file: {path}")
        expected_size = manifest.get("sizes", {}).get(filename)
        expected_hash = manifest.get("sha256", {}).get(filename)
        expected_rows = manifest.get("row_counts", {}).get(filename)
        if (
            path.stat().st_size != expected_size
            or _hash_file(path) != expected_hash
            or _csv_data_row_count(path) != expected_rows
        ):
            raise RuntimeError(f"raw shard checksum failure: {path}")
    return manifest


def _iter_csv(path: Path) -> Iterable[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return ()
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def _plot_sample(
    sample: list[tuple[float, float]],
    *,
    p_hist: np.ndarray,
    m_hist: np.ndarray,
    output: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 9), constrained_layout=True)
    if sample:
        points = np.asarray(sample)
        axes[0, 0].scatter(points[:, 1], points[:, 0], s=5, alpha=0.25)
    axes[0, 0].axhline(0.8, color="tab:red", linestyle="--", linewidth=1)
    axes[0, 0].axvline(0.5, color="tab:red", linestyle="--", linewidth=1)
    axes[0, 0].set(
        xlabel="Material retention M(tau)",
        ylabel="Phenotype continuity P(tau)",
        title="RESERVOIR SAMPLE — INITIAL PROBE IS NOT AN IDENTITY DEFINITION",
    )
    centers = np.linspace(0.0, 1.0, len(p_hist), endpoint=False) + 0.5 / len(p_hist)
    axes[0, 1].bar(centers, p_hist, width=1.0 / len(p_hist), color="tab:blue")
    axes[0, 1].set(title="P marginal (all rows)", xlabel="P")
    axes[1, 0].bar(centers, m_hist, width=1.0 / len(m_hist), color="tab:orange")
    axes[1, 0].set(title="M marginal (all rows)", xlabel="M")
    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.02,
        0.98,
        f"Scatter reservoir rows: {len(sample)}\nMarginals use every row",
        va="top",
        family="monospace",
    )
    fig.savefig(output, dpi=160, format="png")
    plt.close(fig)


def _atomic_plot_sample(
    sample: list[tuple[float, float]],
    *,
    p_hist: np.ndarray,
    m_hist: np.ndarray,
    output: Path,
) -> None:
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{output.stem}-", suffix=".png.tmp", dir=output.parent
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        _plot_sample(sample, p_hist=p_hist, m_hist=m_hist, output=temp_path)
        with temp_path.open("r+b") as handle:
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, output)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def _run_input_sha256(plan_sha256: str, law_index: int, seed: int) -> str:
    return _canonical_sha256(
        {
            "plan_sha256": plan_sha256,
            "law_index": law_index,
            "seed": seed,
        }
    )


def _reproduction_command(
    output_dir: Path,
    experiment_id: str,
    config: BaselineConfig,
    reservoir_size: int,
) -> str:
    seeds = " ".join(str(seed) for seed in config.seeds)
    cadences = " ".join(str(cadence) for cadence in config.snapshot_cadences)
    return (
        ".\\.venv\\Scripts\\python.exe -m edlab.cli stream-screen "
        f'--output "{output_dir}" --experiment-id {experiment_id} '
        f"--laws {config.n_laws} --seeds {seeds} --particles {config.n_particles} "
        f"--steps {config.steps} --cadences {cadences} --reservoir-size {reservoir_size}"
    )


def _verify_complete_manifest(
    *,
    output_dir: Path,
    plan: dict[str, Any],
    config: BaselineConfig,
    law_indices: tuple[int, ...],
) -> dict[str, Any]:
    manifest_path = output_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("invalid final manifest") from exc
    expected_runs = len(law_indices) * len(config.seeds)
    required = {
        "status": "COMPLETE",
        "experiment_id": plan["experiment_id"],
        "git_commit": plan["git_commit"],
        "plan_sha256": plan["plan_sha256"],
        "expected_runs": expected_runs,
        "completed_runs": expected_runs,
    }
    for key, expected in required.items():
        if manifest.get(key) != expected:
            raise RuntimeError(
                f"invalid COMPLETE manifest: {key}={manifest.get(key)!r}, "
                f"expected {expected!r}"
            )
    output_paths = manifest.get("output_paths")
    output_hashes = manifest.get("output_sha256")
    output_sizes = manifest.get("output_sizes")
    if not isinstance(output_paths, list) or not isinstance(output_hashes, dict):
        raise RuntimeError("invalid COMPLETE manifest output index")
    if not isinstance(output_sizes, dict) or "manifest.json" in output_paths:
        raise RuntimeError("invalid COMPLETE manifest size index")
    for relative_path in output_paths:
        path = output_dir / relative_path
        if (
            not path.is_file()
            or path.stat().st_size != output_sizes.get(relative_path)
            or _hash_file(path) != output_hashes.get(relative_path)
        ):
            raise RuntimeError(f"committed output verification failure: {path}")

    raw_index_path = output_dir / "raw_index.json"
    if manifest.get("raw_index_sha256") != _hash_file(raw_index_path):
        raise RuntimeError("raw index hash mismatch")
    raw_index = json.loads(raw_index_path.read_text(encoding="utf-8"))
    if not isinstance(raw_index, list) or len(raw_index) != expected_runs:
        raise RuntimeError("raw index run count mismatch")
    entries = {entry.get("run_key"): entry for entry in raw_index}
    if len(entries) != expected_runs:
        raise RuntimeError("raw index contains duplicate run keys")
    raw_totals: Counter[str] = Counter()
    for law_index in law_indices:
        for seed in config.seeds:
            run_key = _run_key(law_index, seed)
            entry = entries.get(run_key)
            if entry is None:
                raise RuntimeError(f"raw index missing run: {run_key}")
            shard = output_dir / str(entry.get("relative_path"))
            run_manifest = _verify_shard(
                shard,
                law_index=law_index,
                seed=seed,
                input_sha256=_run_input_sha256(
                    plan["plan_sha256"], law_index, seed
                ),
            )
            for key, value in run_manifest.items():
                if entry.get(key) != value:
                    raise RuntimeError(
                        f"raw index metadata mismatch for {run_key}: {key}"
                    )
            for filename, rows in run_manifest["row_counts"].items():
                raw_totals[filename] += int(rows)
    raw_totals_dict = dict(sorted(raw_totals.items()))
    if manifest.get("raw_row_counts") != raw_totals_dict:
        raise RuntimeError("manifest/raw-index row-count inconsistency")
    recovery = manifest.get("recovery", {})
    recovery_log_relative = recovery.get("log_relative_path")
    if recovery_log_relative is not None:
        recovery_log_path = output_dir / recovery_log_relative
        if (
            not recovery_log_path.is_file()
            or recovery_log_path.stat().st_size != recovery.get("log_size")
            or _hash_file(recovery_log_path) != recovery.get("log_sha256")
        ):
            raise RuntimeError("recovery log verification failure")
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    if (
        summary.get("runs") != expected_runs
        or summary.get("raw_row_counts") != raw_totals_dict
        or summary.get("measurement_rows") != raw_totals_dict.get("measurements.csv", 0)
    ):
        raise RuntimeError("summary/raw-index consistency failure")
    return summary


def run_streaming_screen(
    *,
    output_dir: Path,
    experiment_id: str,
    git_commit: str,
    config: BaselineConfig,
    reservoir_size: int = 100_000,
    git_scope_clean: bool = False,
    _before_shard_publish: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    if reservoir_size < 0:
        raise ValueError("reservoir_size must be non-negative")
    output_dir.mkdir(parents=True, exist_ok=True)
    law_indices = _planned_law_indices(config)
    expected_runs = len(law_indices) * len(config.seeds)
    plan = {
        "raw_schema_version": RAW_SCHEMA_VERSION,
        "experiment_id": experiment_id,
        "git_commit": git_commit,
        "git_scope_clean": git_scope_clean,
        "config": config.as_dict(),
        "law_indices": list(law_indices),
        "reservoir_size": reservoir_size,
    }
    plan["plan_sha256"] = _canonical_sha256(plan)
    plan_path = output_dir / "stream_plan.json"
    if plan_path.exists():
        existing_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if existing_plan != plan:
            raise RuntimeError(
                "streaming output directory belongs to a different experiment plan"
            )
    elif (output_dir / "raw").exists():
        raise RuntimeError("raw shards exist without a stream_plan.json audit anchor")
    else:
        _atomic_write_json(plan_path, plan)
    raw_root = output_dir / "raw" / "runs"
    raw_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        orphan_paths = _orphan_work_paths(output_dir, raw_root)
        if orphan_paths:
            raise RuntimeError(
                "orphan temporary work exists beside a COMPLETE manifest; audit required"
            )
        return _verify_complete_manifest(
            output_dir=output_dir,
            plan=plan,
            config=config,
            law_indices=law_indices,
        )
    recovery = _quarantine_orphan_work(output_dir, raw_root)
    completed_before = sum(
        1
        for law_index in law_indices
        for seed in config.seeds
        if (raw_root / _run_key(law_index, seed) / "run_manifest.json").is_file()
    )
    disk_preflight = _disk_preflight(output_dir, expected_runs - completed_before)
    world = WorldSpec(
        n_particles=config.n_particles,
        n_types=config.n_types,
        initial_speed=0.04,
    )
    detection = DetectionSpec(config.detection_radius, config.min_entity_size)
    phenotype_spec = PhenotypeSpec(config.detection_radius, 0.25)
    tracker_spec = TrackerSpec(
        config.tracker_distance,
        config.tracker_min_size_ratio,
    )
    laws = [(index, law_from_halton(index, config.n_types)) for index in law_indices]
    _atomic_write_text(
        output_dir / "laws.json",
        json.dumps(
            [
                {"law_index": law_index, "law_spec": law.as_dict()}
                for law_index, law in laws
            ],
            indent=2,
        ),
    )

    shard_paths: list[Path] = []
    for law_index, _law in laws:
        for seed in config.seeds:
            run_key = _run_key(law_index, seed)
            run_input_sha256 = _run_input_sha256(
                plan["plan_sha256"], law_index, seed
            )
            final_dir = raw_root / run_key
            if final_dir.exists() and not (final_dir / "run_manifest.json").is_file():
                raise RuntimeError(
                    f"incomplete existing shard requires audit: {final_dir}"
                )
            if not (final_dir / "run_manifest.json").exists():
                rows = _execute_one_run(
                    law_index=law_index,
                    seed=seed,
                    config=config,
                    world=world,
                    detection=detection,
                    phenotype_spec=phenotype_spec,
                    tracker_spec=tracker_spec,
                )
                final_dir = _write_shard_atomic(
                    run_root=raw_root,
                    run_key=run_key,
                    rows_by_file=rows,
                    law_index=law_index,
                    seed=seed,
                    input_sha256=run_input_sha256,
                    before_publish=_before_shard_publish,
                )
            _verify_shard(
                final_dir,
                law_index=law_index,
                seed=seed,
                input_sha256=run_input_sha256,
            )
            shard_paths.append(final_dir)

    moments = _OnlineCovariance()
    p_min = m_min = math.inf
    p_max = m_max = -math.inf
    probe_count = resolved_probe_count = 0
    cadence_counts: Counter[int] = Counter()
    event_counts: Counter[str] = Counter()
    aggregate: dict[
        tuple[int, int, int, int, str], dict[str, float | int]
    ] = defaultdict(
        lambda: {
            "rows": 0,
            "probe_rows": 0,
            "resolved_probe_rows": 0,
            "sum_p": 0.0,
            "sum_m": 0.0,
            "p_min": math.inf,
            "p_max": -math.inf,
            "m_min": math.inf,
            "m_max": -math.inf,
        }
    )
    p_hist = np.zeros(50, dtype=np.int64)
    m_hist = np.zeros(50, dtype=np.int64)
    reservoir: list[tuple[float, float]] = []
    reservoir_rng = np.random.default_rng(20260710)
    raw_index: list[dict[str, Any]] = []
    raw_totals: Counter[str] = Counter()

    for shard in sorted(shard_paths):
        run_manifest = json.loads((shard / "run_manifest.json").read_text(encoding="utf-8"))
        for filename, rows in run_manifest["row_counts"].items():
            raw_totals[filename] += int(rows)
        raw_index.append(
            {
                "run_key": shard.name,
                "relative_path": str(shard.relative_to(output_dir)).replace("\\", "/"),
                **run_manifest,
            }
        )
        for row in _iter_csv(shard / "measurements.csv"):
            p_value = float(row["phenotype_continuity"])
            m_value = float(row["material_retention"])
            if not math.isfinite(p_value) or not math.isfinite(m_value):
                raise RuntimeError(f"non-finite P/M value in {shard / 'measurements.csv'}")
            moments.update(p_value, m_value)
            count = moments.count
            p_min = min(p_min, p_value)
            p_max = max(p_max, p_value)
            m_min = min(m_min, m_value)
            m_max = max(m_max, m_value)
            cadence = int(row["snapshot_cadence"])
            cadence_counts[cadence] += 1
            is_probe = p_value > 0.8 and m_value < 0.5
            is_resolved = (
                is_probe
                and row["interval_has_ambiguity"] == "False"
                and row["interval_has_split_or_merge"] == "False"
            )
            probe_count += int(is_probe)
            resolved_probe_count += int(is_resolved)
            p_hist[max(0, min(49, int(p_value * 50)))] += 1
            m_hist[max(0, min(49, int(m_value * 50)))] += 1
            if len(reservoir) < reservoir_size:
                reservoir.append((p_value, m_value))
            else:
                replace = int(reservoir_rng.integers(0, count))
                if replace < reservoir_size:
                    reservoir[replace] = (p_value, m_value)
            step_delta = int(row["end_step"]) - int(row["start_step"])
            if step_delta <= 0 or step_delta % cadence:
                raise RuntimeError(
                    f"invalid measurement step delta in {shard / 'measurements.csv'}"
                )
            lag_snapshots = step_delta // cadence
            normalized_tau = f"{step_delta * config.dt:.12g}"
            key = (
                int(row["law_index"]),
                int(row["seed"]),
                cadence,
                lag_snapshots,
                normalized_tau,
            )
            stats = aggregate[key]
            stats["rows"] += 1
            stats["probe_rows"] += int(is_probe)
            stats["resolved_probe_rows"] += int(is_resolved)
            stats["sum_p"] += p_value
            stats["sum_m"] += m_value
            stats["p_min"] = min(float(stats["p_min"]), p_value)
            stats["p_max"] = max(float(stats["p_max"]), p_value)
            stats["m_min"] = min(float(stats["m_min"]), m_value)
            stats["m_max"] = max(float(stats["m_max"]), m_value)
        for row in _iter_csv(shard / "lineage_events.csv"):
            event_counts[row["kind"]] += 1

    aggregate_rows: list[dict[str, Any]] = []
    for (law_index, seed, cadence, lag_snapshots, tau), stats in sorted(
        aggregate.items()
    ):
        rows = int(stats["rows"])
        aggregate_rows.append(
            {
                "law_index": law_index,
                "seed": seed,
                "snapshot_cadence": cadence,
                "lag_snapshots": lag_snapshots,
                "tau": tau,
                **stats,
                "mean_p": float(stats["sum_p"]) / rows,
                "mean_m": float(stats["sum_m"]) / rows,
            }
        )
    if len(shard_paths) != expected_runs:
        raise RuntimeError(
            f"cannot finalize incomplete screen: {len(shard_paths)}/{expected_runs} runs"
        )
    _atomic_write_csv(output_dir / "measurement_aggregates.csv", aggregate_rows)
    _atomic_write_json(output_dir / "raw_index.json", raw_index)

    count = moments.count
    correlation = moments.correlation()
    force_validation = validate_force_paths()
    null_results = [
        id_permutation_null(),
        static_motif_material_flux_null(),
        tracker_cadence_sensitivity_null(),
        sparse_lookalike_alias_null(),
    ]
    summary = {
        "experiment_id": experiment_id,
        "git_commit": git_commit,
        "runs": len(shard_paths),
        "measurement_rows": count,
        "reservoir_size": reservoir_size,
        "raw_row_counts": dict(sorted(raw_totals.items())),
        "correlation_p_m_descriptive_only": correlation,
        "p_min": None if count == 0 else p_min,
        "p_max": None if count == 0 else p_max,
        "m_min": None if count == 0 else m_min,
        "m_max": None if count == 0 else m_max,
        "initial_probe": {
            "definition": "P > 0.8 and M < 0.5",
            "raw_count": probe_count,
            "lineage_resolved_count": resolved_probe_count,
            "all_rows_retain_unresolved_sparse_alias_risk": True,
        },
        "measurements_by_cadence": dict(sorted(cadence_counts.items())),
        "lineage_event_counts": dict(sorted(event_counts.items())),
        "force_validation": asdict(force_validation),
        "null_models": [asdict(result) for result in null_results],
        "raw_storage": "local ignored per-run shards; committed checksums/index",
        "recovery": recovery,
        "disk_preflight": disk_preflight,
        "statistical_warning": "Rows are repeated windows, not independent replicates.",
    }
    _atomic_write_json(output_dir / "summary.json", summary)
    _atomic_write_text(
        output_dir / "summary.md",
        f"""# {experiment_id} — Streaming CORE V0 Screen

## OBSERVED

- Runs: {len(shard_paths)}.
- Measurement rows: {count} (not independent replicates).
- P range: {summary['p_min']} to {summary['p_max']}.
- M range: {summary['m_min']} to {summary['m_max']}.
- Descriptive r(P,M): {correlation}.
- Raw initial-probe rows: {probe_count}; interval-lineage-resolved rows: {resolved_probe_count}.

## INFERRED

- None of these counts alone establishes individuality; every probe row retains sparse-alias/static-flux risk.

## HYPOTHESIS

- Eligible laws, if any, require the preregistered clean cross-cadence rule and fresh seeds.

## WHAT WOULD FALSIFY THIS?

- Raw shard checksum failure, non-equivalence to the validated full runner, null failure, or fresh-seed failure invalidates promotion.
""",
    )
    _atomic_plot_sample(
        reservoir,
        p_hist=p_hist,
        m_hist=m_hist,
        output=output_dir / "p_m_audit.png",
    )
    committed_outputs = [
        output_dir / "stream_plan.json",
        output_dir / "laws.json",
        output_dir / "measurement_aggregates.csv",
        output_dir / "raw_index.json",
        output_dir / "summary.json",
        output_dir / "summary.md",
        output_dir / "p_m_audit.png",
    ]
    manifest = {
        "status": "COMPLETE",
        "experiment_id": experiment_id,
        "git_commit": git_commit,
        "git_scope_clean": git_scope_clean,
        "plan_sha256": plan["plan_sha256"],
        "expected_runs": expected_runs,
        "completed_runs": len(shard_paths),
        "code_version": "0.1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "substrate": "particle_dynamics",
        "core_mechanism_version": "CORE_V0",
        "sampling": {
            "method": "Halton low-discrepancy sequence",
            "law_indices": list(law_indices),
            "seeds": list(config.seeds),
            "screening_only": True,
            "probability_estimate": False,
        },
        "config": config.as_dict(),
        "world_spec": world.as_dict(),
        "detection_spec": detection.as_dict(),
        "phenotype_spec": phenotype_spec.as_dict(),
        "tracker_spec": tracker_spec.as_dict(),
        "backend": "vectorized; exact-SHA force and one-step validation required",
        "dependencies": {
            "python": platform.python_version(),
            "numpy": version("numpy"),
            "matplotlib": version("matplotlib"),
        },
        "raw_policy": {
            "git_tracked": False,
            "index": "raw_index.json",
            "shard_root": "raw/runs",
            "resume_unit": "complete per-run shard",
        },
        "raw_row_counts": dict(sorted(raw_totals.items())),
        "raw_index_sha256": _hash_file(output_dir / "raw_index.json"),
        "analysis_parameters": {
            "reservoir_size": reservoir_size,
            "histogram_bins_per_axis": 50,
        },
        "recovery": recovery,
        "disk_preflight": disk_preflight,
        "reproduction_command": _reproduction_command(
            output_dir, experiment_id, config, reservoir_size
        ),
        "completion": {
            "all_planned_runs_present": len(shard_paths) == expected_runs,
            "all_shards_verified": True,
            "derived_outputs_published_atomically": True,
            "manifest_published_last": True,
        },
        "output_paths": [path.name for path in committed_outputs],
        "output_sha256": {path.name: _hash_file(path) for path in committed_outputs},
        "output_sizes": {path.name: path.stat().st_size for path in committed_outputs},
    }
    _atomic_write_json(output_dir / "manifest.json", manifest)
    return _verify_complete_manifest(
        output_dir=output_dir,
        plan=plan,
        config=config,
        law_indices=law_indices,
    )
