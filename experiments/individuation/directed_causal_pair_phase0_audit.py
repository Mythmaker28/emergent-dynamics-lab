"""Outcome-blind DEV audit for DIRECTED-CAUSAL-PAIR-00 Phase 0.

This module reads only already-open 50001--50010 DEV artefacts.  It does not
instantiate an engine, enumerate a prospective namespace, or calculate any
pair-feeding outcome.  Its purpose is to make the Phase-0 geometry and
provenance judgement reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any


MISSION = "DIRECTED-CAUSAL-PAIR-00-PHASE0"
PARENT_COMMIT = "7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b"
OPEN_DEV_SEEDS = tuple(range(50001, 50011))
GRID_SIZE = 64
MIN_SEPARATION = 24.0
CORE_RADIUS = 10
BARRIER_WIDTH = 2
HALO_OUTER_RADIUS = CORE_RADIUS + BARRIER_WIDTH

RAW_PATH = Path("experiments/individuation/turnover_dev_raw.json")
PHASE05_PATH = Path("docs/individuation/ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json")
NOSWAP_PATH = Path("docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def toroidal_distance(a: list[float], b: list[float], size: int = GRID_SIZE) -> float:
    deltas = [min(abs(float(x) - float(y)), size - abs(float(x) - float(y))) for x, y in zip(a, b)]
    return float(math.hypot(*deltas))


def pair_candidates(initial: list[list[float]], deep: list[list[float]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in combinations(range(len(initial)), 2):
        initial_distance = toroidal_distance(initial[left], initial[right])
        deep_distance = toroidal_distance(deep[left], deep[right])
        rows.append(
            {
                "target_indices": [left, right],
                "initial_distance": initial_distance,
                "deep_distance": deep_distance,
                "initial_halo_gap": initial_distance - 2 * HALO_OUTER_RADIUS,
                "deep_halo_gap": deep_distance - 2 * HALO_OUTER_RADIUS,
                "initial_separation_pass": initial_distance >= MIN_SEPARATION,
                "deep_endpoint_separation_pass": deep_distance >= MIN_SEPARATION,
            }
        )
    return rows


def select_pair(candidates: list[dict[str, Any]], original_world_id: int) -> dict[str, Any]:
    """Select before history by maximum initial separation, never by feeding.

    The world-parity orientation is an experimental label only.  It is not
    available to the detector, tracker, association gates, or physics.
    """

    winner = max(candidates, key=lambda row: (row["initial_distance"], -row["target_indices"][0], -row["target_indices"][1]))
    left, right = winner["target_indices"]
    target_a, target_b = (left, right) if original_world_id % 2 == 0 else (right, left)
    return {
        **winner,
        "selection_rule": "maximum initial toroidal centroid separation; ties by ascending target-index pair",
        "orientation_rule": "even original_world_id: ascending A/B; odd original_world_id: descending A/B",
        "target_A": target_a,
        "target_B": target_b,
        "sentinel_targets": sorted(set(range(3)) - {left, right}),
    }


def _valid_noswap_target(target: dict[str, Any]) -> bool:
    arms = target["arms"]
    return bool(
        target["free_continuation_valid"]
        and target["exact_isolation"]["bit_exact_isolation"]
        and target["exact_isolation"]["up_ref_zero"]
        and arms["own_replay_clamp_sham"]["run"]["valid"]
        and arms["reference_replay_clamp"]["run"]["valid"]
    )


def audit(repo: Path) -> dict[str, Any]:
    raw_path = repo / RAW_PATH
    phase05_path = repo / PHASE05_PATH
    noswap_path = repo / NOSWAP_PATH
    raw = _load(raw_path)
    phase05 = _load(phase05_path)
    noswap = _load(noswap_path)

    raw_seeds = {int(row["seed"]) for row in raw}
    if not raw_seeds <= set(OPEN_DEV_SEEDS):
        raise ValueError("turnover DEV raw contains a seed outside the already-open 50001--50010 namespace")
    if set(phase05["allowed_seed_namespace"]) != set(OPEN_DEV_SEEDS):
        raise ValueError("Phase-0.5 allowed namespace does not match the frozen open DEV namespace")
    if set(noswap["allowed_seed_namespace"]) != set(OPEN_DEV_SEEDS):
        raise ValueError("Phase-0.6B allowed namespace does not match the frozen open DEV namespace")
    if phase05["new_seed_or_prospective_family_opened"] or noswap["new_seed_or_prospective_family_opened"]:
        raise ValueError("input artefact claims that a new/prospective family was opened")

    p05_by_seed = {int(row["seed"]): row for row in phase05["worlds"]}
    noswap_by_seed = {int(row["seed"]): row for row in noswap["worlds"]}
    worlds: list[dict[str, Any]] = []

    for row in raw:
        seed = int(row["seed"])
        p05 = p05_by_seed.get(seed, {})
        nsw = noswap_by_seed.get(seed)
        turnover = row.get("turnover", {})
        deep = row.get("deep")
        eligible = bool(
            row.get("eligible")
            and row.get("feasible")
            and deep
            and deep.get("g0_valid")
            and not turnover.get("first_censor")
            and p05.get("feasible")
            and p05.get("C_blocks_pairwise_disjoint")
            and all(p05.get("body_inside_C", []))
            and nsw
            and len(nsw.get("targets", [])) == 3
            and all(_valid_noswap_target(target) for target in nsw["targets"])
        )
        if not eligible:
            worlds.append(
                {
                    "original_world_id": seed,
                    "eligible_pair_world": False,
                    "reason": row.get("reason") or row.get("deep_reason") or p05.get("reason") or "failed frozen DEV gates",
                }
            )
            continue

        candidates = pair_candidates(row["cents"], deep["cents"])
        selected = select_pair(candidates, seed)
        worlds.append(
            {
                "original_world_id": seed,
                "eligible_pair_world": True,
                "deep_turnover_step": int(deep["step"]),
                "turnover_first_censor": turnover["first_censor"],
                "deep_joint_M": [float(value) for value in deep["M"]],
                "all_three_deep_g0_valid": bool(deep["g0_valid"]),
                "phase05_core_blocks_pairwise_disjoint": bool(p05["C_blocks_pairwise_disjoint"]),
                "noswap_single_target_qualification": {
                    "targets_valid": len(nsw["targets"]),
                    "all_exact_isolation_up_ref_zero": all(
                        target["exact_isolation"]["bit_exact_isolation"]
                        and target["exact_isolation"]["up_ref_zero"]
                        for target in nsw["targets"]
                    ),
                    "pair_composition_executed": False,
                    "history_bearing_recipient_executed": False,
                },
                "pair_candidates_outcome_blind": candidates,
                "selected_pair": selected,
            }
        )

    valid = [world for world in worlds if world["eligible_pair_world"]]
    selected_pass = [
        world["selected_pair"]["initial_separation_pass"]
        and world["selected_pair"]["deep_endpoint_separation_pass"]
        for world in valid
    ]
    selected_gaps = [
        min(world["selected_pair"]["initial_halo_gap"], world["selected_pair"]["deep_halo_gap"])
        for world in valid
    ]

    return {
        "schema": "DIRECTED-CAUSAL-PAIR-00-PHASE0-DEV-AUDIT-v1",
        "mission": MISSION,
        "mode": "DEV_ONLY_OUTCOME_BLIND_STATIC_AUDIT",
        "parent_commit": PARENT_COMMIT,
        "new_seed_or_prospective_family_opened": False,
        "pair_feeding_outcomes_computed": False,
        "inputs": {
            str(RAW_PATH).replace("\\", "/"): _sha256(raw_path),
            str(PHASE05_PATH).replace("\\", "/"): _sha256(phase05_path),
            str(NOSWAP_PATH).replace("\\", "/"): _sha256(noswap_path),
        },
        "frozen_geometry": {
            "grid_size": GRID_SIZE,
            "minimum_centroid_separation": MIN_SEPARATION,
            "core_radius": CORE_RADIUS,
            "barrier_width": BARRIER_WIDTH,
            "halo_outer_radius": HALO_OUTER_RADIUS,
        },
        "summary": {
            "n_open_dev_worlds": len(raw),
            "n_eligible_pair_worlds": len(valid),
            "n_selected_pairs": len(valid),
            "all_selected_pairs_pass_available_endpoint_separation": all(selected_pass),
            "selected_pair_min_endpoint_halo_gap": min(selected_gaps) if selected_gaps else None,
            "all_turnover_tracks_nonfusing_and_uncensored": all(not world["turnover_first_censor"] for world in valid),
            "single_target_noswap_qualified_targets": sum(
                world["noswap_single_target_qualification"]["targets_valid"] for world in valid
            ),
            "pair_context_history_bearing_recipient_noswap_qualified": False,
            "simultaneous_dual_clamp_required_by_draft": False,
            "continuous_pair_distance_raw_available": False,
            "exact_clone_H00_H10_H01_H11_executed": False,
            "mechanical_judgement": "COMPOSITION_PLAUSIBLE_BUT_PAIR_SPECIFIC_QUALIFICATION_REQUIRED",
            "recommendation": "REVISE",
        },
        "limitations": [
            "turnover_dev_raw.json stores initial and deep centroids but not per-step pair distance or halo overlap",
            "Phase-0.6B qualified one clamped target at a time in no-history continuations, not a clamped recipient beside a history-bearing partner",
            "the H00/H10/H01/H11 pair clone set has not been executed even on DEV",
            "four original worlds establish feasibility only and are below the draft minimum-valid-world rule",
        ],
        "worlds": worlds,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.repo.resolve())
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        # Keep the committed machine artefact byte-stable across Windows and POSIX.
        args.output.write_bytes(payload.encode("utf-8"))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
