"""Independently executed CORE V0 baseline and first technical kill-switch."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..entities.detection import detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import measure_tracks
from ..specs import DetectionSpec, LawSpec, PhenotypeSpec, RunSpec, TrackerSpec, WorldSpec
from ..substrates.particle_dynamics.engine import initialize_world, simulate
from ..validation.forces import validate_force_paths
from ..validation.nulls import (
    id_permutation_null,
    sparse_lookalike_alias_null,
    static_motif_material_flux_null,
    tracker_cadence_sensitivity_null,
)


@dataclass(frozen=True)
class BaselineConfig:
    n_laws: int = 12
    law_indices: tuple[int, ...] | None = None
    experiment_kind: str = "baseline"
    seeds: tuple[int, ...] = (101, 202, 303)
    n_particles: int = 64
    n_types: int = 3
    dt: float = 0.02
    steps: int = 600
    snapshot_cadences: tuple[int, ...] = (10, 30, 60)
    detection_radius: float = 0.11
    min_entity_size: int = 4
    tracker_distance: float = 0.16
    tracker_min_size_ratio: float = 0.25
    lag_indices: tuple[int, ...] = (1, 3, 6)

    def __post_init__(self) -> None:
        if self.n_laws < 1 or not self.seeds:
            raise ValueError("baseline requires at least one law and seed")
        if self.law_indices is not None and not self.law_indices:
            raise ValueError("law_indices must be non-empty when provided")
        if self.experiment_kind not in {"baseline", "holdout"}:
            raise ValueError("experiment_kind must be 'baseline' or 'holdout'")
        if not self.snapshot_cadences or min(self.snapshot_cadences) < 1:
            raise ValueError("snapshot cadences must be positive")
        base = min(self.snapshot_cadences)
        if any(cadence % base for cadence in self.snapshot_cadences):
            raise ValueError("snapshot cadences must be multiples of the minimum cadence")

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("seeds", "snapshot_cadences", "lag_indices", "law_indices"):
            if data[key] is None:
                continue
            data[key] = list(data[key])
        return data


_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67)
# NOTE: appended 59,61,67 (2026-07-10) so EXP03-C can request 19 Halton dims. Additive only:
# law_from_halton and EXP03-A/B use <=16 primes, so all prior law generation is byte-identical.


def _radical_inverse(index: int, base: int) -> float:
    inverse = 0.0
    factor = 1.0 / base
    while index:
        index, digit = divmod(index, base)
        inverse += digit * factor
        factor /= base
    return inverse


def halton_point(index: int, dimensions: int) -> np.ndarray:
    """Deterministic low-discrepancy point; index is one-based."""

    if dimensions > len(_PRIMES):
        raise ValueError("requested Halton dimension exceeds built-in prime table")
    return np.array(
        [_radical_inverse(index, base) for base in _PRIMES[:dimensions]],
        dtype=np.float64,
    )


def law_from_halton(law_index: int, n_types: int) -> LawSpec:
    dimensions = n_types * n_types + 4
    point = halton_point(law_index + 32, dimensions)
    matrix = 2.0 * point[: n_types * n_types].reshape(n_types, n_types) - 1.0
    tail = point[n_types * n_types :]
    return LawSpec(
        interaction=matrix,
        repulsion_strength=float(0.7 + 2.0 * tail[0]),
        short_range=float(0.022 + 0.023 * tail[1]),
        interaction_range=float(0.14 + 0.08 * tail[2]),
        damping=float(0.35 + 1.3 * tail[3]),
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plot_measurements(rows: list[dict[str, Any]], output: Path) -> None:
    p_values = np.array([row["phenotype_continuity"] for row in rows], dtype=float)
    m_values = np.array([row["material_retention"] for row in rows], dtype=float)
    fig, axes = plt.subplots(2, 2, figsize=(10, 9), constrained_layout=True)
    scatter = axes[0, 0]
    if len(rows) >= 200:
        scatter.hexbin(m_values, p_values, gridsize=35, mincnt=1, cmap="viridis")
    else:
        scatter.scatter(m_values, p_values, s=12, alpha=0.55)
    scatter.axhline(0.8, color="tab:red", linestyle="--", linewidth=1)
    scatter.axvline(0.5, color="tab:red", linestyle="--", linewidth=1)
    scatter.set(xlabel="Material retention M(tau)", ylabel="Phenotype continuity P(tau)")
    scatter.set_title("INITIAL EXPLORATORY PROBE — NOT AN IDENTITY DEFINITION")
    axes[0, 1].hist(p_values, bins=30, color="tab:blue", alpha=0.75)
    axes[0, 1].set(xlabel="P(tau)", ylabel="measurement rows", title="P marginal")
    axes[1, 0].hist(m_values, bins=30, color="tab:orange", alpha=0.75)
    axes[1, 0].set(xlabel="M(tau)", ylabel="measurement rows", title="M marginal")
    cadence_counts = Counter(int(row["snapshot_cadence"]) for row in rows)
    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.02,
        0.98,
        "Rows by cadence\n" + "\n".join(f"{key}: {value}" for key, value in sorted(cadence_counts.items())),
        va="top",
        family="monospace",
    )
    fig.savefig(output, dpi=160)
    plt.close(fig)


def run_baseline(
    *,
    output_dir: Path,
    experiment_id: str,
    git_commit: str,
    config: BaselineConfig,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=False)
    world = WorldSpec(
        n_particles=config.n_particles,
        n_types=config.n_types,
        initial_speed=0.04,
    )
    detection = DetectionSpec(config.detection_radius, config.min_entity_size)
    phenotype_spec = PhenotypeSpec(
        length_scale=config.detection_radius,
        speed_scale=0.25,
    )
    tracker_spec = TrackerSpec(
        max_centroid_distance=config.tracker_distance,
        min_size_ratio=config.tracker_min_size_ratio,
    )

    force_validation = validate_force_paths()
    null_results = [
        id_permutation_null(),
        static_motif_material_flux_null(),
        tracker_cadence_sensitivity_null(),
        sparse_lookalike_alias_null(),
    ]
    selected_indices = (
        tuple(range(config.n_laws))
        if config.law_indices is None
        else tuple(config.law_indices)
    )
    laws = [(index, law_from_halton(index, config.n_types)) for index in selected_indices]
    (output_dir / "laws.json").write_text(
        json.dumps(
            [
                {"law_index": law_index, "law_spec": law.as_dict()}
                for law_index, law in laws
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    measurement_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    association_rows: list[dict[str, Any]] = []
    cadence_track_counts: Counter[int] = Counter()
    cadence_measurement_counts: Counter[int] = Counter()
    base_cadence = min(config.snapshot_cadences)
    run_count = 0

    for law_index, law in laws:
        for seed in config.seeds:
            run_count += 1
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

            for cadence in config.snapshot_cadences:
                tracker = LineageTracker(tracker_spec, box_size=world.box_size)
                selected = [snapshot for snapshot in snapshots if snapshot.step % cadence == 0]
                for snapshot in selected:
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
                                "phenotype_vector_json": json.dumps(entity.phenotype.vector.tolist()),
                                "phenotype_raw_json": json.dumps(entity.phenotype.raw, sort_keys=True),
                            }
                        )
                measurements = measure_tracks(
                    tracker.tracks,
                    lag_indices=config.lag_indices,
                    events=tracker.events,
                )
                cadence_track_counts[cadence] += len(tracker.tracks)
                cadence_measurement_counts[cadence] += len(measurements)
                for measurement in measurements:
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

    _write_csv(output_dir / "measurements.csv", measurement_rows)
    _write_csv(output_dir / "lineage_events.csv", event_rows)
    _write_csv(output_dir / "entity_observations.csv", observation_rows)
    _write_csv(output_dir / "association_edges.csv", association_rows)

    p_values = np.array([row["phenotype_continuity"] for row in measurement_rows], dtype=float)
    m_values = np.array([row["material_retention"] for row in measurement_rows], dtype=float)
    if len(measurement_rows) > 1 and np.std(p_values) > 0 and np.std(m_values) > 0:
        correlation: float | None = float(np.corrcoef(p_values, m_values)[0, 1])
    else:
        correlation = None
    probe_count = int(np.sum((p_values > 0.8) & (m_values < 0.5))) if len(p_values) else 0
    resolved_probe_count = sum(
        1
        for row in measurement_rows
        if row["phenotype_continuity"] > 0.8
        and row["material_retention"] < 0.5
        and not row["interval_has_ambiguity"]
        and not row["interval_has_split_or_merge"]
    )
    p_range = float(np.ptp(p_values)) if len(p_values) else 0.0
    m_range = float(np.ptp(m_values)) if len(m_values) else 0.0
    event_counts = Counter(row["kind"] for row in event_rows)
    cadence_has_measurements = all(cadence_measurement_counts[cadence] > 0 for cadence in config.snapshot_cadences)
    null_by_name = {result.name: result for result in null_results}
    gates = {
        "second_force_path": force_validation.passed,
        "id_permutation_null": null_by_name["ID_PERMUTATION"].passed,
        "static_flux_false_positive_null": null_by_name[
            "STATIC_MOTIF_WITH_MATERIAL_FLUX"
        ].passed,
        "tracker_cadence_sensitivity_null": null_by_name[
            "TRACKER_CADENCE_SENSITIVITY"
        ].passed,
        "sparse_lookalike_alias_null_live": null_by_name[
            "SPARSE_LOOKALIKE_ALIAS"
        ].passed,
        "tracker_auditable": (
            len(event_rows) > 0
            and len(event_counts) > 0
            and len(association_rows) > 0
            and all("interval_has_ambiguity" in row for row in measurement_rows)
        ),
        "cadence_control_nonempty": cadence_has_measurements,
        "phenotype_continuity_varies": p_range > 1e-9,
        "material_retention_varies": m_range > 1e-9,
    }
    summary: dict[str, Any] = {
        "experiment_id": experiment_id,
        "git_commit": git_commit,
        "runs": run_count,
        "measurement_rows": len(measurement_rows),
        "correlation_p_m_descriptive_only": correlation,
        "initial_probe": {
            "definition": "P > 0.8 and M < 0.5",
            "raw_count": probe_count,
            "lineage_resolved_count": resolved_probe_count,
            "all_rows_retain_unresolved_sparse_alias_risk": True,
        },
        "p_min": float(p_values.min()) if len(p_values) else None,
        "p_max": float(p_values.max()) if len(p_values) else None,
        "m_min": float(m_values.min()) if len(m_values) else None,
        "m_max": float(m_values.max()) if len(m_values) else None,
        "lineage_event_counts": dict(sorted(event_counts.items())),
        "tracks_by_cadence": dict(sorted(cadence_track_counts.items())),
        "measurements_by_cadence": dict(sorted(cadence_measurement_counts.items())),
        "force_validation": asdict(force_validation),
        "null_models": [asdict(result) for result in null_results],
        "kill_switch_gates": gates,
        "kill_switch_all_green": all(gates.values()),
        "statistical_warning": (
            "Rows repeat tracks and lags and are not independent replicates; correlation is descriptive."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    study_title = (
        "Current Independently Executed Baseline"
        if config.experiment_kind == "baseline"
        else "Frozen Fresh-seed Hold-out"
    )
    summary_markdown = f"""# {experiment_id} — {study_title}

## HISTORICAL AGENT-REPORTED

- 7079 measurements; r(P,M)=0.68; 0/7079 for P>0.8 and M<0.5.
- These values were not used as reproduced data in this experiment.

## OBSERVED

- Executed runs: {run_count}.
- Measurement rows: {len(measurement_rows)} (repeated tracks/lags; not independent replicates).
- P range: {summary['p_min']} to {summary['p_max']}.
- M range: {summary['m_min']} to {summary['m_max']}.
- Descriptive r(P,M): {correlation}.
- Initial exploratory probe raw count P>0.8, M<0.5: {probe_count}.
- Probe rows without logged ambiguity/split/merge inside the interval: {resolved_probe_count}.
- Every probe row retains unresolved sparse look-alike/static-flux alias risk.
- Kill-switch gates: `{json.dumps(gates, sort_keys=True)}`.

## INFERRED

- The technical P/M pipeline is eligible for EXP02 only if every kill-switch gate above is true.
- The static-flux null remains a known false positive even when it enters the initial probe.

## HYPOTHESIS

- Any association between P and M may reflect physical coupling, tracker selection, or repeated-measure structure; this baseline alone does not distinguish them.

## WHAT WOULD FALSIFY THIS?

- Failure of ID permutation, independent force-path agreement, cadence sensitivity, or held-out reruns invalidates interpretation of rare candidates.
- A candidate that disappears under frozen tracker settings or fresh seeds is not robust evidence.
"""
    (output_dir / "summary.md").write_text(summary_markdown, encoding="utf-8")
    if measurement_rows:
        _plot_measurements(measurement_rows, output_dir / "p_m_audit.png")

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    manifest = {
        "experiment_id": experiment_id,
        "git_commit": git_commit,
        "code_version": "0.1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "substrate": "particle_dynamics",
        "core_mechanism_version": "CORE_V0",
        "sampling": {
            "method": (
                "Halton low-discrepancy sequence"
                if config.experiment_kind == "baseline"
                else "frozen candidate LawSpecs selected from the baseline"
            ),
            "skip": 32,
            "screening_only": config.experiment_kind == "baseline",
            "probability_estimate": False,
        },
        "config": config.as_dict(),
        "world_spec": world.as_dict(),
        "run_spec_template": {
            "dt": config.dt,
            "steps": config.steps,
            "simulated_time": config.steps * config.dt,
            "backend": "vectorized",
        },
        "detection_spec": detection.as_dict(),
        "phenotype_spec": phenotype_spec.as_dict(),
        "tracker_spec": tracker_spec.as_dict(),
        "law_specs_path": "laws.json",
        "seeds": list(config.seeds),
        "backend": "vectorized validated against scalar reference",
        "dependencies": {
            "python": platform.python_version(),
            "numpy": version("numpy"),
            "matplotlib": version("matplotlib"),
        },
        "output_paths": [path.name for path in output_paths],
        "output_sha256": {path.name: _hash_file(path) for path in output_paths},
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return summary
