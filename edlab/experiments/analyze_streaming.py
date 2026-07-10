"""Chunk-aware analysis for a completed streaming CORE V0 screen."""

from __future__ import annotations

import bisect
import csv
import json
import math
import os
import tempfile
from array import array
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from .baseline import _hash_file
from .streaming import (
    RAW_FILENAMES,
    _atomic_write_csv,
    _atomic_write_json,
    _atomic_write_text,
    _csv_data_row_count,
    _iter_csv,
)


COMPLEX_EVENTS = {"split", "merge", "ambiguous_association"}
HISTOGRAM_BINS = 50


@dataclass
class Aggregate:
    rows: int = 0
    probe_rows: int = 0
    sum_p: float = 0.0
    sum_m: float = 0.0
    p_min: float = math.inf
    p_max: float = -math.inf
    m_min: float = math.inf
    m_max: float = -math.inf

    def update(self, p_value: float, m_value: float) -> None:
        self.rows += 1
        self.probe_rows += int(p_value > 0.8 and m_value < 0.5)
        self.sum_p += p_value
        self.sum_m += m_value
        self.p_min = min(self.p_min, p_value)
        self.p_max = max(self.p_max, p_value)
        self.m_min = min(self.m_min, m_value)
        self.m_max = max(self.m_max, m_value)

    def as_fields(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "probe_rows": self.probe_rows,
            "probe_fraction": self.probe_rows / self.rows if self.rows else None,
            "mean_p": self.sum_p / self.rows if self.rows else None,
            "mean_m": self.sum_m / self.rows if self.rows else None,
            "p_min": None if not self.rows else self.p_min,
            "p_max": None if not self.rows else self.p_max,
            "m_min": None if not self.rows else self.m_min,
            "m_max": None if not self.rows else self.m_max,
        }


def _as_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise RuntimeError(f"invalid serialized boolean: {value!r}")


def qualify_run_candidate_rows(
    measurement_rows: Iterable[dict[str, str]],
    *,
    observation_counts: Mapping[tuple[int, int], int],
    complex_tracks: set[tuple[int, int]],
) -> tuple[list[dict[str, Any]], set[tuple[int, int, int, int]]]:
    """Apply the frozen per-cadence cleanliness rule before endpoint grouping."""

    clean_by_endpoint: dict[
        tuple[int, int, int, int], list[dict[str, Any]]
    ] = defaultdict(list)
    for row in measurement_rows:
        p_value = float(row["phenotype_continuity"])
        m_value = float(row["material_retention"])
        if not (p_value > 0.8 and m_value < 0.5):
            continue
        cadence = int(row["snapshot_cadence"])
        track_id = int(row["track_id"])
        track_key = (cadence, track_id)
        if observation_counts.get(track_key, 0) < 8 or track_key in complex_tracks:
            continue
        endpoint = (
            int(row["law_index"]),
            int(row["seed"]),
            int(row["start_step"]),
            int(row["end_step"]),
        )
        enriched: dict[str, Any] = dict(row)
        enriched.update(
            {
                "phenotype_continuity": p_value,
                "material_retention": m_value,
                "track_observations": observation_counts[track_key],
                "track_ever_complex": False,
                "unresolved_sparse_alias_risk": True,
            }
        )
        clean_by_endpoint[endpoint].append(enriched)

    qualified_endpoints: set[tuple[int, int, int, int]] = set()
    qualified_rows: list[dict[str, Any]] = []
    for endpoint, rows in clean_by_endpoint.items():
        cadence_count = len({int(row["snapshot_cadence"]) for row in rows})
        if cadence_count < 2:
            continue
        qualified_endpoints.add(endpoint)
        for row in rows:
            row["clean_probe_cadence_count_same_endpoint"] = cadence_count
            qualified_rows.append(row)
    return qualified_rows, qualified_endpoints


def _update_pareto(
    frontier_m: list[float],
    frontier: list[dict[str, Any]],
    record: dict[str, Any],
) -> None:
    m_value = float(record["material_retention"])
    p_value = float(record["phenotype_continuity"])
    predecessor = bisect.bisect_right(frontier_m, m_value) - 1
    if predecessor >= 0 and float(frontier[predecessor]["phenotype_continuity"]) >= p_value:
        return
    insert_at = bisect.bisect_left(frontier_m, m_value)
    while (
        insert_at < len(frontier)
        and float(frontier[insert_at]["phenotype_continuity"]) <= p_value
    ):
        del frontier_m[insert_at]
        del frontier[insert_at]
    frontier_m.insert(insert_at, m_value)
    frontier.insert(insert_at, record)


def _law_features(law_spec: dict[str, Any]) -> dict[str, float]:
    interaction = np.asarray(law_spec["interaction"], dtype=np.float64)
    return {
        "interaction_mean": float(np.mean(interaction)),
        "interaction_abs_mean": float(np.mean(np.abs(interaction))),
        "interaction_positive_fraction": float(np.mean(interaction > 0.0)),
        "interaction_diagonal_mean": float(np.mean(np.diag(interaction))),
        "interaction_asymmetry_rms": float(
            np.sqrt(np.mean(np.square(interaction - interaction.T)))
        ),
        "repulsion_strength": float(law_spec["repulsion_strength"]),
        "short_range": float(law_spec["short_range"]),
        "interaction_range": float(law_spec["interaction_range"]),
        "damping": float(law_spec["damping"]),
    }


def _atomic_save_figure(path: Path, figure: plt.Figure) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.stem}-", suffix=".png.tmp", dir=path.parent
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        figure.savefig(temp_path, dpi=170, bbox_inches="tight", format="png")
        plt.close(figure)
        with temp_path.open("r+b") as handle:
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        plt.close(figure)
        temp_path.unlink(missing_ok=True)
        raise


def _plot_joint_density(
    joint_histogram: np.ndarray,
    pareto_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 7.2))
    image = axis.imshow(
        np.log1p(joint_histogram),
        origin="lower",
        extent=(0.0, 1.0, 0.0, 1.0),
        aspect="auto",
        cmap="cividis",
    )
    if pareto_rows:
        axis.plot(
            [float(row["material_retention"]) for row in pareto_rows],
            [float(row["phenotype_continuity"]) for row in pareto_rows],
            color="#D55E00",
            marker="o",
            markersize=3,
            linewidth=1.2,
            label="Exact observed Pareto frontier",
        )
    axis.axhline(0.8, color="white", linestyle="--", linewidth=1, label="Initial probe")
    axis.axvline(0.5, color="white", linestyle="--", linewidth=1)
    axis.set(
        xlabel="Material retention M(tau)",
        ylabel="Phenotype continuity P(tau)",
        title="EXP02 joint P/M density (log1p count; repeated rows)",
    )
    axis.legend(loc="lower right", frameon=True)
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("log(1 + measurement rows)")
    _atomic_save_figure(output, figure)


def _plot_probe_by_cadence_tau(
    cadence_tau: Mapping[tuple[int, int, str], Aggregate], output: Path
) -> None:
    figure, axis = plt.subplots(figsize=(9.2, 5.8))
    colors = {10: "#0072B2", 30: "#E69F00", 60: "#009E73"}
    for cadence in sorted({key[0] for key in cadence_tau}):
        points = sorted(
            (
                float(tau),
                aggregate.probe_rows / aggregate.rows if aggregate.rows else 0.0,
            )
            for (item_cadence, _lag, tau), aggregate in cadence_tau.items()
            if item_cadence == cadence
        )
        axis.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            marker="o",
            linewidth=1.8,
            color=colors.get(cadence),
            label=f"cadence {cadence}",
        )
    axis.set(
        xlabel="Normalized lag tau (from integer step delta)",
        ylabel="Initial-probe row fraction",
        title="Probe occupancy depends on cadence and lag",
    )
    axis.set_ylim(bottom=0.0)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    _atomic_save_figure(output, figure)


def _plot_law_probe_fraction(law_rows: list[dict[str, Any]], output: Path) -> None:
    top = sorted(law_rows, key=lambda row: float(row["probe_fraction"]), reverse=True)[:30]
    top.reverse()
    colors = ["#D55E00" if row["eligible_law"] else "#0072B2" for row in top]
    figure, axis = plt.subplots(figsize=(9.5, 8.0))
    positions = np.arange(len(top))
    axis.barh(positions, [row["probe_fraction"] for row in top], color=colors)
    axis.set_yticks(
        positions,
        [
            f"{row['law_index']}*" if row["eligible_law"] else str(row["law_index"])
            for row in top
        ],
    )
    axis.set(
        xlabel="Initial-probe row fraction (descriptive only)",
        ylabel="Law index",
        title="Top probe occupancy laws; orange passed the frozen seed gate",
    )
    axis.grid(axis="x", alpha=0.25)
    axis.legend(
        handles=[
            Patch(color="#D55E00", label="Passed frozen 2/3-seed gate (*)"),
            Patch(color="#0072B2", label="Did not pass that gate"),
        ],
        loc="lower right",
        frameon=False,
    )
    _atomic_save_figure(output, figure)


def analyze_streaming_screen(
    result_dir: Path,
    *,
    analysis_git_commit: str,
    analysis_git_scope_clean: bool,
) -> dict[str, Any]:
    parent_manifest_path = result_dir / "manifest.json"
    parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
    if parent_manifest.get("status") != "COMPLETE":
        raise RuntimeError("streaming parent experiment is not COMPLETE")
    raw_index = json.loads((result_dir / "raw_index.json").read_text(encoding="utf-8"))
    if len(raw_index) != parent_manifest["expected_runs"]:
        raise RuntimeError("analysis raw-index run count mismatch")
    config = parent_manifest["config"]
    dt = float(config["dt"])
    expected_seeds = {int(seed) for seed in config["seeds"]}
    law_specs = {
        int(item["law_index"]): item["law_spec"]
        for item in json.loads((result_dir / "laws.json").read_text(encoding="utf-8"))
    }

    p_values = array("d")
    m_values = array("d")
    joint_histogram = np.zeros((HISTOGRAM_BINS, HISTOGRAM_BINS), dtype=np.int64)
    cadence_tau: dict[tuple[int, int, str], Aggregate] = defaultdict(Aggregate)
    cadence_tau_flags: dict[tuple[int, int, str, bool, bool], Aggregate] = defaultdict(
        Aggregate
    )
    run_cadence_lag: dict[tuple[int, int, int, int, str], Aggregate] = defaultdict(
        Aggregate
    )
    run_aggregates: dict[tuple[int, int], Aggregate] = defaultdict(Aggregate)
    law_aggregates: dict[int, Aggregate] = defaultdict(Aggregate)
    event_counts: Counter[str] = Counter()
    raw_totals: Counter[str] = Counter()
    non_finite_rows = 0
    probe_rows = 0
    interval_flag_clean_probe_rows = 0
    clean_long_probe_rows = 0
    cross_cadence_rows: list[dict[str, Any]] = []
    cross_endpoints: set[tuple[int, int, int, int]] = set()
    cross_endpoints_by_law_seed: Counter[tuple[int, int]] = Counter()
    candidate_seeds_by_law: dict[int, set[int]] = defaultdict(set)
    lineage_rows: list[dict[str, Any]] = []
    frontier_m: list[float] = []
    pareto_rows: list[dict[str, Any]] = []
    total_tracks = 0
    horizon_tracks = 0
    simulations_with_final_entity = 0
    horizon_measurement_windows = 0
    horizon_probe_rows = 0
    track_spans = array("d")
    horizon_track_spans = array("d")

    for entry in sorted(raw_index, key=lambda item: (item["law_index"], item["seed"])):
        law_index = int(entry["law_index"])
        seed = int(entry["seed"])
        shard = result_dir / entry["relative_path"]
        for filename in RAW_FILENAMES:
            path = shard / filename
            if (
                path.stat().st_size != entry["sizes"][filename]
                or _hash_file(path) != entry["sha256"][filename]
                or _csv_data_row_count(path) != entry["row_counts"][filename]
            ):
                raise RuntimeError(f"analysis source verification failure: {path}")
            raw_totals[filename] += int(entry["row_counts"][filename])

        observation_stats: dict[tuple[int, int], list[int]] = {}
        for row in _iter_csv(shard / "entity_observations.csv"):
            key = (int(row["snapshot_cadence"]), int(row["track_id"]))
            step = int(row["step"])
            stats = observation_stats.setdefault(key, [0, step, step])
            stats[0] += 1
            stats[1] = min(stats[1], step)
            stats[2] = max(stats[2], step)
        observation_counts = {key: stats[0] for key, stats in observation_stats.items()}

        complex_tracks: set[tuple[int, int]] = set()
        events_by_cadence: Counter[tuple[int, str]] = Counter()
        for row in _iter_csv(shard / "lineage_events.csv"):
            cadence = int(row["snapshot_cadence"])
            kind = row["kind"]
            event_counts[kind] += 1
            events_by_cadence[(cadence, kind)] += 1
            if kind not in COMPLEX_EVENTS:
                continue
            track_ids = set(json.loads(row["parent_track_ids_json"]))
            track_ids.update(json.loads(row["child_track_ids_json"]))
            complex_tracks.update((cadence, int(track_id)) for track_id in track_ids)

        measurement_rows = list(_iter_csv(shard / "measurements.csv"))
        qualified_rows, qualified_endpoints = qualify_run_candidate_rows(
            measurement_rows,
            observation_counts=observation_counts,
            complex_tracks=complex_tracks,
        )
        clean_long_probe_rows += sum(
            1
            for row in measurement_rows
            if float(row["phenotype_continuity"]) > 0.8
            and float(row["material_retention"]) < 0.5
            and observation_counts.get(
                (int(row["snapshot_cadence"]), int(row["track_id"])), 0
            )
            >= 8
            and (int(row["snapshot_cadence"]), int(row["track_id"]))
            not in complex_tracks
        )
        if qualified_endpoints:
            candidate_seeds_by_law[law_index].add(seed)
        for endpoint in qualified_endpoints:
            cross_endpoints.add(endpoint)
            cross_endpoints_by_law_seed[(law_index, seed)] += 1
        cross_cadence_rows.extend(qualified_rows)

        for row in measurement_rows:
            p_value = float(row["phenotype_continuity"])
            m_value = float(row["material_retention"])
            if not math.isfinite(p_value) or not math.isfinite(m_value):
                non_finite_rows += 1
                continue
            if not (0.0 <= p_value <= 1.0 and 0.0 <= m_value <= 1.0):
                raise RuntimeError("P/M value outside frozen [0,1] domain")
            p_values.append(p_value)
            m_values.append(m_value)
            is_probe = p_value > 0.8 and m_value < 0.5
            probe_rows += int(is_probe)
            interval_flag_clean_probe_rows += int(
                is_probe
                and not _as_bool(row["interval_has_ambiguity"])
                and not _as_bool(row["interval_has_split_or_merge"])
            )
            p_bin = max(0, min(HISTOGRAM_BINS - 1, int(p_value * HISTOGRAM_BINS)))
            m_bin = max(0, min(HISTOGRAM_BINS - 1, int(m_value * HISTOGRAM_BINS)))
            joint_histogram[p_bin, m_bin] += 1
            cadence = int(row["snapshot_cadence"])
            step_delta = int(row["end_step"]) - int(row["start_step"])
            if step_delta <= 0 or step_delta % cadence:
                raise RuntimeError("measurement has invalid integer lag geometry")
            lag_snapshots = step_delta // cadence
            normalized_tau = f"{step_delta * dt:.12g}"
            ambiguity = _as_bool(row["interval_has_ambiguity"])
            split_merge = _as_bool(row["interval_has_split_or_merge"])
            cadence_tau[(cadence, lag_snapshots, normalized_tau)].update(
                p_value, m_value
            )
            cadence_tau_flags[
                (cadence, lag_snapshots, normalized_tau, ambiguity, split_merge)
            ].update(p_value, m_value)
            run_cadence_lag[
                (law_index, seed, cadence, lag_snapshots, normalized_tau)
            ].update(p_value, m_value)
            run_aggregates[(law_index, seed)].update(p_value, m_value)
            law_aggregates[law_index].update(p_value, m_value)
            if int(row["end_step"]) == int(config["steps"]):
                horizon_measurement_windows += 1
                horizon_probe_rows += int(is_probe)
            _update_pareto(
                frontier_m,
                pareto_rows,
                {
                    "law_index": law_index,
                    "seed": seed,
                    "snapshot_cadence": cadence,
                    "track_id": int(row["track_id"]),
                    "start_step": int(row["start_step"]),
                    "end_step": int(row["end_step"]),
                    "lag_snapshots": lag_snapshots,
                    "tau": normalized_tau,
                    "phenotype_continuity": p_value,
                    "material_retention": m_value,
                    "unresolved_sparse_alias_risk": True,
                },
            )

        run_has_final_entity = False
        cadences = sorted({key[0] for key in observation_stats} | {key[0] for key in events_by_cadence})
        for cadence in cadences:
            tracks = {
                key: stats for key, stats in observation_stats.items() if key[0] == cadence
            }
            observation_lengths = [stats[0] for stats in tracks.values()]
            lifetime_steps = [stats[2] - stats[1] for stats in tracks.values()]
            total_tracks += len(tracks)
            for stats in tracks.values():
                span = (stats[2] - stats[1]) * dt
                track_spans.append(span)
                if stats[2] == int(config["steps"]):
                    horizon_tracks += 1
                    horizon_track_spans.append(span)
                    run_has_final_entity = True
            lineage_rows.append(
                {
                    "law_index": law_index,
                    "seed": seed,
                    "snapshot_cadence": cadence,
                    "tracks": len(tracks),
                    "mean_track_observations": (
                        float(np.mean(observation_lengths)) if observation_lengths else None
                    ),
                    "median_track_observations": (
                        float(np.median(observation_lengths)) if observation_lengths else None
                    ),
                    "mean_lifetime_steps": (
                        float(np.mean(lifetime_steps)) if lifetime_steps else None
                    ),
                    "median_lifetime_steps": (
                        float(np.median(lifetime_steps)) if lifetime_steps else None
                    ),
                    "complex_tracks": sum(key in complex_tracks for key in tracks),
                    "birth_events": events_by_cadence[(cadence, "birth")],
                    "disappearance_events": events_by_cadence[(cadence, "disappearance")],
                    "continuity_events": events_by_cadence[(cadence, "continuity")],
                    "split_events": events_by_cadence[(cadence, "split")],
                    "merge_events": events_by_cadence[(cadence, "merge")],
                    "ambiguity_events": events_by_cadence[
                        (cadence, "ambiguous_association")
                    ],
                }
            )
        simulations_with_final_entity += int(run_has_final_entity)

    if non_finite_rows:
        raise RuntimeError(f"analysis found {non_finite_rows} non-finite rows")
    raw_totals_dict = dict(sorted(raw_totals.items()))
    if raw_totals_dict != parent_manifest["raw_row_counts"]:
        raise RuntimeError("analysis raw totals disagree with parent manifest")
    if len(p_values) != raw_totals_dict["measurements.csv"]:
        raise RuntimeError("analysis measurement count mismatch")

    parent_aggregate_rows = list(_iter_csv(result_dir / "measurement_aggregates.csv"))
    parent_logical_groups: Counter[tuple[int, int, int, int]] = Counter()
    for row in parent_aggregate_rows:
        cadence = int(row["snapshot_cadence"])
        lag_snapshots = int(round(float(row["tau"]) / (dt * cadence)))
        parent_logical_groups[
            (
                int(row["law_index"]),
                int(row["seed"]),
                cadence,
                lag_snapshots,
            )
        ] += 1
    fragmented_parent_groups = sum(
        fragments > 1 for fragments in parent_logical_groups.values()
    )

    p_array = np.frombuffer(p_values, dtype=np.float64)
    m_array = np.frombuffer(m_values, dtype=np.float64)
    correlation = float(np.corrcoef(p_array, m_array)[0, 1])
    quantile_levels = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
    p_quantiles = np.quantile(p_array, quantile_levels)
    m_quantiles = np.quantile(m_array, quantile_levels)
    run_row_counts = np.array(
        [aggregate.rows for aggregate in run_aggregates.values()], dtype=np.float64
    )
    run_probe_fractions = np.array(
        [aggregate.probe_rows / aggregate.rows for aggregate in run_aggregates.values()],
        dtype=np.float64,
    )
    run_size_probe_correlation = (
        float(np.corrcoef(run_row_counts, run_probe_fractions)[0, 1])
        if len(run_row_counts) > 1
        and np.std(run_row_counts) > 0.0
        and np.std(run_probe_fractions) > 0.0
        else None
    )

    eligible_laws = sorted(
        law for law, seeds in candidate_seeds_by_law.items() if len(seeds) >= 2
    )
    cross_endpoint_rows: list[dict[str, Any]] = []
    for row in cross_cadence_rows:
        law_index = int(row["law_index"])
        row["eligible_seed_count_for_law"] = len(candidate_seeds_by_law[law_index])
        row["eligible_law"] = law_index in eligible_laws
        cross_endpoint_rows.append(row)

    law_rows: list[dict[str, Any]] = []
    for law_index in sorted(law_specs):
        aggregate = law_aggregates[law_index]
        seeds = sorted(candidate_seeds_by_law.get(law_index, set()))
        law_rows.append(
            {
                "law_index": law_index,
                **_law_features(law_specs[law_index]),
                **aggregate.as_fields(),
                "cross_cadence_endpoint_count": sum(
                    count
                    for (law, _seed), count in cross_endpoints_by_law_seed.items()
                    if law == law_index
                ),
                "qualifying_seeds_json": json.dumps(seeds),
                "eligible_seed_count": len(seeds),
                "eligible_law": law_index in eligible_laws,
                "all_candidates_retain_unresolved_alias_risk": True,
            }
        )

    correlation_rows: list[dict[str, Any]] = []
    feature_names = list(_law_features(next(iter(law_specs.values()))))
    outcomes = ("probe_fraction", "mean_p", "mean_m", "eligible_seed_count")
    for feature in feature_names:
        x_values = np.array([float(row[feature]) for row in law_rows])
        for outcome in outcomes:
            y_values = np.array([float(row[outcome]) for row in law_rows])
            value = (
                float(np.corrcoef(x_values, y_values)[0, 1])
                if np.std(x_values) > 0.0 and np.std(y_values) > 0.0
                else None
            )
            correlation_rows.append(
                {
                    "law_parameter": feature,
                    "outcome": outcome,
                    "pearson_descriptive": value,
                    "laws": len(law_rows),
                    "warning": "screening association; no causal or probability claim",
                }
            )

    cadence_tau_rows = [
        {
            "snapshot_cadence": cadence,
            "lag_snapshots": lag_snapshots,
            "tau": tau,
            **aggregate.as_fields(),
        }
        for (cadence, lag_snapshots, tau), aggregate in sorted(cadence_tau.items())
    ]
    corrected_measurement_aggregate_rows = [
        {
            "law_index": law_index,
            "seed": seed,
            "snapshot_cadence": cadence,
            "lag_snapshots": lag_snapshots,
            "tau": tau,
            **aggregate.as_fields(),
        }
        for (
            law_index,
            seed,
            cadence,
            lag_snapshots,
            tau,
        ), aggregate in sorted(run_cadence_lag.items())
    ]
    cadence_tau_flag_rows = [
        {
            "snapshot_cadence": cadence,
            "lag_snapshots": lag_snapshots,
            "tau": tau,
            "interval_has_ambiguity": ambiguity,
            "interval_has_split_or_merge": split_merge,
            **aggregate.as_fields(),
        }
        for (
            cadence,
            lag_snapshots,
            tau,
            ambiguity,
            split_merge,
        ), aggregate in sorted(cadence_tau_flags.items())
    ]
    joint_rows = [
        {
            "p_bin": p_bin,
            "p_lower": p_bin / HISTOGRAM_BINS,
            "p_upper": (p_bin + 1) / HISTOGRAM_BINS,
            "m_bin": m_bin,
            "m_lower": m_bin / HISTOGRAM_BINS,
            "m_upper": (m_bin + 1) / HISTOGRAM_BINS,
            "rows": int(joint_histogram[p_bin, m_bin]),
            "fraction": int(joint_histogram[p_bin, m_bin]) / len(p_values),
        }
        for p_bin in range(HISTOGRAM_BINS)
        for m_bin in range(HISTOGRAM_BINS)
    ]

    summary = {
        "parent_experiment_id": parent_manifest["experiment_id"],
        "parent_git_commit": parent_manifest["git_commit"],
        "analysis_git_commit": analysis_git_commit,
        "analysis_git_scope_clean": analysis_git_scope_clean,
        "integrity": {
            "parent_status": parent_manifest["status"],
            "runs": len(raw_index),
            "raw_row_counts": raw_totals_dict,
            "non_finite_measurement_rows": non_finite_rows,
            "parent_aggregate_tau_fragmentation_detected": fragmented_parent_groups > 0,
            "parent_aggregate_rows": len(parent_aggregate_rows),
            "canonical_nonempty_run_cadence_lag_groups": len(run_cadence_lag),
            "fragmented_parent_logical_groups": fragmented_parent_groups,
            "corrected_grouping": "integer step_delta and lag_snapshots",
        },
        "measurements": len(p_values),
        "correlation_p_m_descriptive_only": correlation,
        "p_mean": float(np.mean(p_array)),
        "m_mean": float(np.mean(m_array)),
        "m_equal_one_fraction": float(np.mean(m_array == 1.0)),
        "m_equal_zero_fraction": float(np.mean(m_array == 0.0)),
        "p_quantiles": {
            f"q{int(level * 100):02d}": float(value)
            for level, value in zip(quantile_levels, p_quantiles, strict=True)
        },
        "m_quantiles": {
            f"q{int(level * 100):02d}": float(value)
            for level, value in zip(quantile_levels, m_quantiles, strict=True)
        },
        "initial_probe": {
            "definition": "P > 0.8 and M < 0.5; not an identity definition",
            "raw_rows": probe_rows,
            "interval_flag_clean_rows": interval_flag_clean_probe_rows,
            "clean_long_rows": clean_long_probe_rows,
            "cross_cadence_rows": len(cross_endpoint_rows),
            "cross_cadence_endpoints": len(cross_endpoints),
            "law_seed_pairs": len(cross_endpoints_by_law_seed),
            "laws_with_any_qualifying_seed": len(candidate_seeds_by_law),
            "eligible_laws_min_two_of_three_seeds": eligible_laws,
            "eligible_law_count": len(eligible_laws),
            "all_rows_retain_unresolved_sparse_alias_risk": True,
        },
        "expected_screening_seeds": sorted(expected_seeds),
        "lineage_event_counts": dict(sorted(event_counts.items())),
        "lifecycle_accounting": {
            "tracks": total_tracks,
            "births_minus_disappearances": (
                event_counts["birth"] - event_counts["disappearance"]
            ),
            "horizon_tracks": horizon_tracks,
            "identity_closes": (
                event_counts["birth"] - event_counts["disappearance"]
                == horizon_tracks
            ),
        },
        "right_censoring": {
            "horizon_step": int(config["steps"]),
            "horizon_time": int(config["steps"]) * dt,
            "horizon_tracks": horizon_tracks,
            "total_tracks": total_tracks,
            "horizon_track_fraction": horizon_tracks / total_tracks,
            "simulations_with_final_entity": simulations_with_final_entity,
            "simulations": len(raw_index),
            "horizon_measurement_windows": horizon_measurement_windows,
            "horizon_probe_rows": horizon_probe_rows,
            "median_track_span_time": float(
                np.median(np.frombuffer(track_spans, dtype=np.float64))
            ),
            "median_horizon_track_span_time": float(
                np.median(np.frombuffer(horizon_track_spans, dtype=np.float64))
            ),
        },
        "pseudoreplication_diagnostics": {
            "run_measurement_rows_min": int(np.min(run_row_counts)),
            "run_measurement_rows_median": float(np.median(run_row_counts)),
            "run_measurement_rows_max": int(np.max(run_row_counts)),
            "row_weighted_probe_fraction": probe_rows / len(p_values),
            "equal_run_mean_probe_fraction": float(np.mean(run_probe_fractions)),
            "run_row_count_probe_fraction_correlation": run_size_probe_correlation,
        },
        "pareto_frontier_rows": len(pareto_rows),
        "statistical_warning": (
            "Measurement rows repeat tracks, overlapping windows, cadences, and lags; "
            "counts/correlations are descriptive and not independent evidence."
        ),
        "right_censoring_warning": (
            "Absence by simulated time 12 is right-censored, not proof of impossibility."
        ),
    }

    analysis_dir = result_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_csv(analysis_dir / "pm_joint_density.csv", joint_rows)
    _atomic_write_csv(
        analysis_dir / "measurement_aggregates_corrected.csv",
        corrected_measurement_aggregate_rows,
    )
    _atomic_write_csv(analysis_dir / "pm_by_cadence_tau.csv", cadence_tau_rows)
    _atomic_write_csv(
        analysis_dir / "pm_by_cadence_tau_flags.csv", cadence_tau_flag_rows
    )
    _atomic_write_csv(analysis_dir / "law_screening.csv", law_rows)
    _atomic_write_csv(analysis_dir / "lineage_summary.csv", lineage_rows)
    _atomic_write_csv(
        analysis_dir / "cross_cadence_candidate_rows.csv", cross_endpoint_rows
    )
    _atomic_write_csv(analysis_dir / "pareto_frontier.csv", pareto_rows)
    _atomic_write_csv(
        analysis_dir / "law_parameter_correlations.csv", correlation_rows
    )
    _atomic_write_json(analysis_dir / "exp02_analysis_summary.json", summary)
    _atomic_write_text(
        analysis_dir / "exp02_analysis_summary.md",
        f"""# EXP02 CORE V0 analysis

## OBSERVED

- Verified runs: {len(raw_index)}; measurement rows: {len(p_values)}.
- Descriptive r(P,M): {correlation} (rows are pseudoreplicated).
- Initial-probe rows: {probe_rows}; clean-long rows: {clean_long_probe_rows}.
- Frozen cross-cadence rule: {len(cross_endpoints)} endpoints in {len(cross_endpoints_by_law_seed)} law/seed pairs.
- Laws qualifying in at least two of three screening seeds: `{eligible_laws}`.
- Parent float-tau fragmentation detected: {fragmented_parent_groups > 0} ({fragmented_parent_groups} logical groups affected); this analysis uses integer step deltas and preserves the parent artefact unchanged.
- Horizon-censored tracks: {horizon_tracks}/{total_tracks}; simulations with a final entity: {simulations_with_final_entity}/{len(raw_index)}.
- Row-weighted probe fraction: {probe_rows / len(p_values)}; equal-run mean: {float(np.mean(run_probe_fractions))}.

## INFERRED

- Eligibility permits a separately frozen fresh-seed audit only. It is not evidence of individuality because every row retains the sparse-alias/static-flux alternative.
- Probe occupancy and descriptive P/M association vary with cadence/lag and repeated-measure structure.

## HYPOTHESIS

- Some eligible laws may reproduce clean cross-cadence endpoints on unseen seeds, but static occupancy/look-alike material flux remains a live explanation.

## WHAT WOULD FALSIFY THIS?

- Independent recomputation disagreement, source hash/row-count failure, or failure on frozen unseen seeds rejects candidate promotion.
- A direct trajectory audit showing stationary occupancy with constituent flow supports the alias/null explanation.

## Caveats

- Three screening seeds are not a probability estimate.
- Non-emergence by simulated time 12 is right-censored.
""",
    )
    _plot_joint_density(
        joint_histogram, pareto_rows, analysis_dir / "pm_joint_density.png"
    )
    _plot_probe_by_cadence_tau(
        cadence_tau, analysis_dir / "probe_by_cadence_tau.png"
    )
    _plot_law_probe_fraction(law_rows, analysis_dir / "law_probe_fraction.png")

    outputs = sorted(
        path for path in analysis_dir.iterdir() if path.name != "analysis_manifest.json"
    )
    analysis_manifest = {
        "status": "COMPLETE",
        "analysis": "EXP02 chunk-aware distribution and frozen candidate audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_git_commit": analysis_git_commit,
        "analysis_git_scope_clean": analysis_git_scope_clean,
        "parent_experiment_id": parent_manifest["experiment_id"],
        "parent_git_commit": parent_manifest["git_commit"],
        "parent_manifest_sha256": _hash_file(parent_manifest_path),
        "parent_raw_index_sha256": _hash_file(result_dir / "raw_index.json"),
        "grouping_correction": {
            "parent_tau_float_string_fragmentation": fragmented_parent_groups > 0,
            "analysis_key": "snapshot_cadence + integer lag_snapshots + normalized step_delta*dt",
        },
        "candidate_rule": (
            "P>0.8,M<0.5; each cadence track>=8 observations and never complex; "
            "same step endpoints under >=2 cadences; law eligible in >=2/3 seeds"
        ),
        "outputs": [path.name for path in outputs],
        "output_sha256": {path.name: _hash_file(path) for path in outputs},
        "output_sizes": {path.name: path.stat().st_size for path in outputs},
    }
    _atomic_write_json(analysis_dir / "analysis_manifest.json", analysis_manifest)
    return summary
