"""Analyse the pilot.  Descriptive only: no k, no 42/9, no POSITIVE, no NEGATIVE.

The convention-sensitivity matrix is computed from the SAME persisted evidence, with no
new engine step and no second seed.  It is a DIAGNOSTIC, not the primary outcome: the
primary outcome is whatever ``derive_world_outcome`` returned at the frozen measurement
specification, and it is reported first and unchanged.  The full matrix is reported; the
convention that yields most successes is never selected.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta

from edlab import route_e_pilot as pilot
from edlab import route_e_pilot_acquisition as acq
from edlab import route_e_pilot_admission as adm
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)

THRESHOLDS = (0.30, 0.45, 0.60)
MIN_CELLS = (2, 3, 5)
CONVENTIONS = (0.01, 0.05, 0.20)


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def _load_world(directory: Path):
    header, ledger = adm._load_ledger(directory)
    return header, ledger


def sensitivity(directory: Path, header, ledger, threshold: float, min_cells: int):
    """Re-detect and re-track from the PERSISTED matter and tracer.  No engine step."""
    shape = (int(header["frame_shape"][0]), int(header["frame_shape"][1]))
    labels = [int(v) for v in header["sampled_frames"]]
    matter = ledger["matter"]
    tracer = ledger["tracer"]
    detector = DetectorSpec(matter_threshold=float(threshold), min_cells=int(min_cells))
    tracker = TrackerSpec()
    frames = []
    for label in labels:
        mask = matter[label] >= float(threshold)
        frames.append(list(detect_components(adm._materialise(mask, int(label)), detector,
                                             frame=int(label))))
    wrapping_at_t0 = any(bool(c.wraps_y or c.wraps_x) for c in frames[0])
    first_wrap = None
    for position, components in enumerate(frames):
        if any(bool(c.wraps_y or c.wraps_x) for c in components):
            first_wrap = labels[position]
            break
    any_wrap = first_wrap is not None
    result = {
        "any_component_at_t0": bool(frames[0]),
        "components_at_t0": len(frames[0]),
        "first_wrapping_frame": first_wrap,
        "largest_area_fraction_t0": (
            max((int(c.area) for c in frames[0]), default=0) / (shape[0] * shape[1])
        ),
        "min_cells": int(min_cells),
        "threshold": float(threshold),
        "wrapping_anywhere": bool(any_wrap),
        "wrapping_at_t0": bool(wrapping_at_t0),
    }
    if any_wrap or not frames[0]:
        result["eligible"] = False
        result["cause"] = "WRAPPING_COMPONENT_PRESENT" if any_wrap else "NO_COMPONENT_AT_ENROLMENT"
        return result

    tracking = track_components(tuple(frames), tracker, sampled_frames=tuple(labels))
    cells_total = shape[0] * shape[1]
    by_index_last = {int(c.index): c for c in frames[-1]}
    residuals: dict[int, float] = {}
    for track in tracking.tracks:
        points = list(track.points)
        if not points or int(points[0].frame) != labels[0]:
            continue
        if [int(p.frame) for p in points] != labels:
            continue
        component = by_index_last.get(int(points[-1].component_index))
        if component is None:
            continue
        ok = True
        for position, point in enumerate(points):
            observed = next(
                (c for c in frames[position] if int(c.index) == int(point.component_index)), None
            )
            if observed is None or bool(observed.wraps_y or observed.wraps_x):
                ok = False
                break
            if int(observed.area) * 2 > cells_total:
                ok = False
                break
        if not ok:
            continue
        rows, cols = np.divmod(np.asarray(sorted(int(x) for x in component.cells)), shape[1])
        mass = float(np.sum(matter[labels[-1]][rows, cols]))
        if mass <= 0.0:
            continue
        residuals[int(track.track_id)] = float(np.sum(tracer[labels[-1]][rows, cols])) / mass
    result["eligible"] = bool(residuals)
    result["cause"] = "" if residuals else "NO_ELIGIBLE_TRACK_TO_HORIZON"
    if residuals:
        best_track = min(residuals, key=lambda t: residuals[t])
        best = residuals[best_track]
        result["residual_min"] = best
        result["residual_all"] = sorted(round(v, 9) for v in residuals.values())
        result["eligible_track_count"] = len(residuals)
        result["Y_by_f"] = {f"{c:g}": int(best <= c) for c in CONVENTIONS}

        # UNION vs FOCAL.  The primary cohort labels the union of every component detected
        # at enrolment, so it measures replacement by matter that was outside that whole
        # union.  The focal cohort labels only the largest eligible component at t0.  The
        # transport is linear in the cohort, so the focal trajectory is obtained from the
        # SAME persisted flows -- no engine step, no second run.
        focal_cells = adm._largest_component_cells(frames[0], shape)
        if focal_cells is not None:
            focal = np.zeros(shape, dtype=np.float64)
            r0, c0 = np.divmod(np.asarray(sorted(focal_cells)), shape[1])
            focal[r0, c0] = matter[0][r0, c0]
            forward = ledger["forward"]; reverse = ledger["reverse"]
            for t in range(int(header["transitions"])):
                focal = adm._advance_tracer_from_ledger(
                    focal, matter[t], forward[t], reverse[t], float(header["dt"])
                )
            for track in tracking.tracks:
                if int(track.track_id) != int(best_track) or not track.points:
                    continue
                component = by_index_last.get(int(track.points[-1].component_index))
                if component is None:
                    continue
                rr, cc = np.divmod(np.asarray(sorted(int(x) for x in component.cells)), shape[1])
                mass = float(np.sum(matter[labels[-1]][rr, cc]))
                if mass > 0.0:
                    result["residual_focal_of_min_track"] = float(np.sum(focal[rr, cc])) / mass
            total_matter_end = float(np.sum(matter[labels[-1]]))
            total_tracer_end = float(np.sum(tracer[labels[-1]]))
            unlabelled = total_matter_end - total_tracer_end
            rr, cc = np.divmod(
                np.asarray(sorted(int(x) for x in by_index_last[
                    int(next(t for t in tracking.tracks
                             if int(t.track_id) == int(best_track)).points[-1].component_index)
                ].cells)),
                shape[1],
            )
            mass = float(np.sum(matter[labels[-1]][rr, cc]))
            result["component_mass_end"] = mass
            result["total_unlabelled_end"] = unlabelled
            result["q_min_inventory"] = max(0.0, 1.0 - unlabelled / mass) if mass > 0 else 1.0
            result["labelled_fraction_end"] = (
                total_tracer_end / total_matter_end if total_matter_end > 0 else None
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.run)
    raw = json.loads((root / "PILOT_RAW_RESULTS.json").read_text())
    results = raw["results"]

    per_world = []
    for entry in results:
        world = entry["world"]
        admission = entry["admission"]
        directory = root / "worlds" / f"{int(world['ordinal']):06d}"
        record = {
            "ordinal": int(world["ordinal"]),
            "law_ordinal": int(world["law_ordinal"]),
            "ic_ordinal": int(world["ic_ordinal"]),
            "lattice_size": int(world["lattice_size"]),
            "status": admission["status"],
            "Y_by_f": admission.get("Y_by_f", {}),
            "mechanically_ineligible": admission.get("mechanically_ineligible"),
            "cause": admission.get("ineligibility_cause", ""),
            "terminal_states": admission.get("terminal_states", []),
            "wrapping_at_t0": None,   # filled from the frozen-spec sensitivity row below
            "wrapping_anywhere": None,
            "engine_reexecution_verified": entry["engine_provenance"]["verified"],
            "transitions_recomputed": admission.get("transport_transitions_recomputed"),
            "tracer_deviation": admission.get("transport_max_tracer_deviation"),
            "conservation_drift": admission.get("global_tracer_conservation_max_drift"),
            "labelled_fraction_t0": (admission.get("labelled_fraction") or [None])[0],
            "labelled_fraction_end": (admission.get("labelled_fraction") or [None])[-1],
            "eligible_tracks": admission.get("eligible_tracks", []),
        }
        if directory.is_dir():
            header, ledger = _load_world(directory)
            record["sensitivity"] = [
                sensitivity(directory, header, ledger, t, m)
                for t in THRESHOLDS
                for m in MIN_CELLS
            ]
            frozen = next(
                s
                for s in record["sensitivity"]
                if s["threshold"] == 0.45 and s["min_cells"] == 3
            )
            record["wrapping_at_t0"] = frozen["wrapping_at_t0"]
            record["wrapping_anywhere"] = frozen["wrapping_anywhere"]
            record["first_wrapping_frame"] = frozen["first_wrapping_frame"]
            record["components_at_t0"] = frozen["components_at_t0"]
            record["largest_area_fraction_t0"] = frozen["largest_area_fraction_t0"]
            # the frozen-spec sensitivity row must REPRODUCE the primary admission
            assert bool(frozen.get("eligible")) == bool(record["eligible_tracks"]), (
                f"world {record['ordinal']}: the frozen-spec recomputation disagrees "
                "with the primary admission"
            )
        per_world.append(record)

    def counts(rows):
        return {
            "n": len(rows),
            "admitted": sum(1 for r in rows if r["status"] == "ADMITTED"),
            "technical_invalid": sum(1 for r in rows if r["status"] != "ADMITTED"),
            "mechanically_ineligible": sum(1 for r in rows if r["mechanically_ineligible"]),
            "with_eligible_track": sum(1 for r in rows if r["eligible_tracks"]),
            "wrapping_at_t0": sum(1 for r in rows if r["wrapping_at_t0"]),
            "wrapping_anywhere": sum(1 for r in rows if r["wrapping_anywhere"]),
            "engine_verified": sum(1 for r in rows if r["engine_reexecution_verified"]),
        }

    ci1 = [r for r in per_world if r["ic_ordinal"] == 0]
    summary = {
        "all_48_worlds": counts(per_world),
        "primary_descriptive_sample_ci1_only": counts(ci1),
        "by_stratum": {
            f"L{size}": counts([r for r in per_world if r["lattice_size"] == size])
            for size in (16, 24, 32)
        },
        "by_stratum_ci1_only": {
            f"L{size}": counts([r for r in ci1 if r["lattice_size"] == size])
            for size in (16, 24, 32)
        },
    }
    n1 = len(ci1)
    k_inelig = sum(1 for r in ci1 if r["mechanically_ineligible"])
    lo, hi = clopper_pearson(k_inelig, n1)
    summary["ineligibility_ci1"] = {
        "count": k_inelig,
        "n": n1,
        "clopper_pearson_95": [round(lo, 4), round(hi, 4)],
        "note": (
            "descriptive; the pilot attaches no decision rule and 24 draws cannot "
            "establish a proportion to the confirmatory design's precision"
        ),
    }
    summary["ci1_ci2_concordance"] = {
        "pairs": pilot.PILOT_LAWS,
        "same_eligibility": sum(
            1
            for law in range(pilot.PILOT_LAWS)
            for pair in [[r for r in per_world if r["law_ordinal"] == law]]
            if len(pair) == 2
            and bool(pair[0]["eligible_tracks"]) == bool(pair[1]["eligible_tracks"])
        ),
        "same_wrapping_anywhere": sum(
            1
            for law in range(pilot.PILOT_LAWS)
            for pair in [[r for r in per_world if r["law_ordinal"] == law]]
            if len(pair) == 2 and pair[0]["wrapping_anywhere"] == pair[1]["wrapping_anywhere"]
        ),
    }
    first_wraps = [r.get("first_wrapping_frame") for r in per_world
                   if r.get("first_wrapping_frame") is not None]
    summary["wrapping_onset_at_frozen_spec"] = {
        "worlds": len(per_world),
        "wrapping_at_enrolment_frame": sum(1 for r in per_world if r["wrapping_at_t0"]),
        "wrapping_somewhere_in_the_horizon": sum(1 for r in per_world if r["wrapping_anywhere"]),
        "first_wrapping_frame_min": min(first_wraps) if first_wraps else None,
        "first_wrapping_frame_median": (
            float(np.median(first_wraps)) if first_wraps else None
        ),
        "first_wrapping_frame_max": max(first_wraps) if first_wraps else None,
        "reading": (
            "if most worlds do NOT wrap at enrolment but ALL wrap later, the percolating "
            "component is produced by the dynamics, not by the initial-condition law"
        ),
    }
    fractions = [r["labelled_fraction_t0"] for r in per_world if r["labelled_fraction_t0"]]
    summary["labelled_fraction_at_enrolment"] = {
        "n": len(fractions),
        "mean": round(float(np.mean(fractions)), 6) if fractions else None,
        "min": round(float(np.min(fractions)), 6) if fractions else None,
        "max": round(float(np.max(fractions)), 6) if fractions else None,
        "meaning": (
            "matter and cohort are BOTH exactly conserved, so this lattice-wide ratio is "
            "fixed for the whole run; under complete mixing every local residual tends to "
            "it, and every frozen convention (0.01, 0.05, 0.20) lies far below it"
        ),
    }

    matrix: dict[str, dict] = {}
    for t in THRESHOLDS:
        for m in MIN_CELLS:
            key = f"threshold={t:g},min_cells={m}"
            cell = [
                s
                for r in per_world
                for s in r.get("sensitivity", [])
                if s["threshold"] == t and s["min_cells"] == m
            ]
            eligible = [s for s in cell if s.get("eligible")]
            matrix[key] = {
                "worlds": len(cell),
                "wrapping_at_t0": sum(1 for s in cell if s["wrapping_at_t0"]),
                "wrapping_anywhere": sum(1 for s in cell if s["wrapping_anywhere"]),
                "no_component_at_t0": sum(1 for s in cell if not s["any_component_at_t0"]),
                "eligible_worlds": len(eligible),
                "residual_min_over_eligible": (
                    round(min(s["residual_min"] for s in eligible), 6) if eligible else None
                ),
                "residual_median_over_eligible": (
                    round(float(np.median([s["residual_min"] for s in eligible])), 6)
                    if eligible
                    else None
                ),
                "Y_counts": {
                    f"{c:g}": sum(1 for s in eligible if s["Y_by_f"][f"{c:g}"] == 1)
                    for c in CONVENTIONS
                },
                "residual_union_over_eligible": [
                    round(s["residual_min"], 6) for s in eligible
                ],
                "residual_focal_over_eligible": [
                    round(s["residual_focal_of_min_track"], 6)
                    for s in eligible
                    if "residual_focal_of_min_track" in s
                ],
                "q_min_inventory_over_eligible": [
                    round(s["q_min_inventory"], 6) for s in eligible if "q_min_inventory" in s
                ],
                "labelled_fraction_end_over_eligible": [
                    round(s["labelled_fraction_end"], 6)
                    for s in eligible
                    if s.get("labelled_fraction_end") is not None
                ],
            }
    summary["convention_and_detector_sensitivity_matrix"] = matrix
    summary["sensitivity_matrix_status"] = (
        "DIAGNOSTIC ONLY.  The frozen specification is threshold=0.45, min_cells=3, and "
        "its row is the primary result.  No cell of this matrix is selected, and the "
        "matrix is reported whole."
    )

    document = {
        "kind": "route-e-pilot-analysis/v1",
        "mission": pilot.PILOT_MISSION,
        "pre_run_root": raw["pre_run_root"],
        "per_world": per_world,
        "summary": summary,
        "wall_clock_seconds": raw["wall_clock_seconds"],
        "worlds_completed": raw["worlds_completed"],
        "worlds_expected": raw["worlds_expected"],
    }
    Path(args.out).write_bytes(pilot.canonical_bytes(document))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
