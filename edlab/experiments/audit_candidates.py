"""Audit initial-probe rows against lineage complexity and observer cadence."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


COMPLEX_EVENTS = {"split", "merge", "ambiguous_association"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _key(row: dict[str, str]) -> tuple[int, int, int, int]:
    return (
        int(row["law_index"]),
        int(row["seed"]),
        int(row["snapshot_cadence"]),
        int(row["track_id"]),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_initial_probe(result_dir: Path) -> dict[str, Any]:
    measurements = _read_csv(result_dir / "measurements.csv")
    events = _read_csv(result_dir / "lineage_events.csv")
    observations = _read_csv(result_dir / "entity_observations.csv")
    observation_counts = Counter(_key(row) for row in observations)

    complex_by_track: dict[tuple[int, int, int, int], list[tuple[int, str]]] = defaultdict(list)
    for event in events:
        if event["kind"] not in COMPLEX_EVENTS:
            continue
        track_ids = set(json.loads(event["parent_track_ids_json"]))
        track_ids.update(json.loads(event["child_track_ids_json"]))
        for track_id in track_ids:
            key = (
                int(event["law_index"]),
                int(event["seed"]),
                int(event["snapshot_cadence"]),
                int(track_id),
            )
            complex_by_track[key].append((int(event["snapshot_step"]), event["kind"]))

    probe_rows: list[dict[str, Any]] = []
    for row in measurements:
        p_value = float(row["phenotype_continuity"])
        m_value = float(row["material_retention"])
        if not (p_value > 0.8 and m_value < 0.5):
            continue
        key = _key(row)
        start_step = int(row["start_step"])
        end_step = int(row["end_step"])
        complex_events = complex_by_track.get(key, [])
        interval_events = [
            kind for step, kind in complex_events if start_step <= step <= end_step
        ]
        enriched: dict[str, Any] = dict(row)
        enriched.update(
            {
                "phenotype_continuity": p_value,
                "material_retention": m_value,
                "track_observations": observation_counts[key],
                "track_ever_complex": bool(complex_events),
                "complex_event_in_interval": bool(interval_events),
                "interval_complex_kinds": ";".join(sorted(set(interval_events))),
                "unresolved_sparse_alias_risk": True,
            }
        )
        probe_rows.append(enriched)

    endpoint_cadences: dict[tuple[int, int, int, int], set[int]] = defaultdict(set)
    for row in probe_rows:
        endpoint = (
            int(row["law_index"]),
            int(row["seed"]),
            int(row["start_step"]),
            int(row["end_step"]),
        )
        endpoint_cadences[endpoint].add(int(row["snapshot_cadence"]))
    for row in probe_rows:
        endpoint = (
            int(row["law_index"]),
            int(row["seed"]),
            int(row["start_step"]),
            int(row["end_step"]),
        )
        row["probe_cadence_count_same_endpoints"] = len(endpoint_cadences[endpoint])

    probe_tracks = {_key(row) for row in probe_rows}
    interval_clean = [row for row in probe_rows if not row["complex_event_in_interval"]]
    track_clean = [row for row in probe_rows if not row["track_ever_complex"]]
    long_track_clean = [
        row
        for row in track_clean
        if int(row["track_observations"]) >= 8
    ]
    cross_cadence = [
        row
        for row in long_track_clean
        if int(row["probe_cadence_count_same_endpoints"]) >= 2
    ]

    def group_counts(rows: list[dict[str, Any]], column: str) -> dict[str, int]:
        return dict(sorted(Counter(str(row[column]) for row in rows).items()))

    clean_seeds_by_law: dict[int, set[int]] = defaultdict(set)
    for row in long_track_clean:
        clean_seeds_by_law[int(row["law_index"])].add(int(row["seed"]))
    cross_cadence_seeds_by_law: dict[int, set[int]] = defaultdict(set)
    cross_cadence_endpoint_counts_by_law: Counter[int] = Counter()
    seen_cross_endpoints: set[tuple[int, int, int, int]] = set()
    for row in cross_cadence:
        law = int(row["law_index"])
        seed = int(row["seed"])
        endpoint = (law, seed, int(row["start_step"]), int(row["end_step"]))
        cross_cadence_seeds_by_law[law].add(seed)
        if endpoint not in seen_cross_endpoints:
            cross_cadence_endpoint_counts_by_law[law] += 1
            seen_cross_endpoints.add(endpoint)

    total_by_cadence = Counter(int(row["snapshot_cadence"]) for row in measurements)
    probe_by_cadence = Counter(int(row["snapshot_cadence"]) for row in probe_rows)
    prevalence_by_cadence = {
        str(cadence): {
            "probe_rows": probe_by_cadence[cadence],
            "total_rows": total,
            "fraction": probe_by_cadence[cadence] / total if total else None,
        }
        for cadence, total in sorted(total_by_cadence.items())
    }
    audit = {
        "definition": "P > 0.8 and M < 0.5; unchanged initial exploratory probe",
        "total_measurement_rows": len(measurements),
        "probe_rows": len(probe_rows),
        "probe_rows_with_unresolved_sparse_alias_risk": len(probe_rows),
        "probe_unique_tracks": len(probe_tracks),
        "interval_clean_probe_rows": len(interval_clean),
        "track_clean_probe_rows": len(track_clean),
        "long_track_clean_probe_rows": len(long_track_clean),
        "long_track_clean_unique_tracks": len({_key(row) for row in long_track_clean}),
        "cross_cadence_same_endpoint_rows": len(cross_cadence),
        "cross_cadence_same_endpoints": len(
            {
                (
                    int(row["law_index"]),
                    int(row["seed"]),
                    int(row["start_step"]),
                    int(row["end_step"]),
                )
                for row in cross_cadence
            }
        ),
        "probe_by_cadence": prevalence_by_cadence,
        "probe_by_tau_rounded": dict(
            sorted(Counter(f"{float(row['tau']):.6g}" for row in probe_rows).items())
        ),
        "probe_by_law": group_counts(probe_rows, "law_index"),
        "long_track_clean_seeds_by_law": {
            str(law): sorted(seeds) for law, seeds in sorted(clean_seeds_by_law.items())
        },
        "cross_cadence_seeds_by_law": {
            str(law): sorted(seeds)
            for law, seeds in sorted(cross_cadence_seeds_by_law.items())
        },
        "cross_cadence_endpoint_counts_by_law": {
            str(law): count
            for law, count in sorted(cross_cadence_endpoint_counts_by_law.items())
        },
        "caveat": (
            "Rows repeat tracks, overlapping windows, cadences, and lags. Counts are descriptive, "
            "not independent evidence. Track-clean means no logged split, merge, or ambiguous "
            "association anywhere on that track under that cadence."
        ),
    }

    columns = list(probe_rows[0]) if probe_rows else []
    with (result_dir / "initial_probe_rows_audited.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if columns:
            writer.writeheader()
            writer.writerows(probe_rows)
    (result_dir / "candidate_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8"
    )
    markdown = f"""# Initial Probe Candidate Audit

## OBSERVED

- Probe definition was not changed: `P > 0.8, M < 0.5`.
- Probe rows: {audit['probe_rows']} / {audit['total_measurement_rows']}.
- Unique cadence-scoped tracks with a probe row: {audit['probe_unique_tracks']}.
- Rows without a complex lineage event inside their measurement interval: {audit['interval_clean_probe_rows']}.
- Rows on tracks with no split, merge, or ambiguous-association event anywhere: {audit['track_clean_probe_rows']}.
- Such rows on tracks with at least 8 observations: {audit['long_track_clean_probe_rows']} across {audit['long_track_clean_unique_tracks']} tracks.
- Clean long-track probe endpoints reproduced as probe-positive at the same physical endpoints under at least two cadences: {audit['cross_cadence_same_endpoints']} endpoints ({audit['cross_cadence_same_endpoint_rows']} cadence rows).

## INFERRED

- Raw probe occupancy alone is not evidence because the mandatory static-flux null also occupies it.
- Logged lineage complexity explains some but not necessarily all probe rows; the track-clean subset requires fresh-seed hold-out before any mechanistic interpretation.

## HYPOTHESIS

- Some track-clean rows may be static occupancy or look-alike stitching not captured by the current event log, rather than self-maintaining organization.

## WHAT WOULD FALSIFY THIS?

- Frozen fresh-seed hold-out, cadence consistency, and controlled perturbation can reject candidate laws.
- Direct trajectory audit showing stationary spatial occupancy with constituent flow would support the null explanation.

## Caveat

{audit['caveat']}
"""
    (result_dir / "candidate_audit.md").write_text(markdown, encoding="utf-8")
    parent_manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
    analysis_git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    analysis_manifest = {
        "analysis": "initial exploratory probe lineage/cadence audit",
        "analysis_git_commit": analysis_git_commit,
        "parent_experiment_id": parent_manifest["experiment_id"],
        "parent_experiment_git_commit": parent_manifest["git_commit"],
        "source_sha256": {
            filename: _sha256(result_dir / filename)
            for filename in (
                "measurements.csv",
                "lineage_events.csv",
                "entity_observations.csv",
                "association_edges.csv",
            )
        },
        "outputs": {
            filename: _sha256(result_dir / filename)
            for filename in (
                "initial_probe_rows_audited.csv",
                "candidate_audit.json",
                "candidate_audit.md",
            )
        },
    }
    (result_dir / "candidate_audit_manifest.json").write_text(
        json.dumps(analysis_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return audit


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(audit_initial_probe(arguments.result_dir), indent=2, sort_keys=True))
