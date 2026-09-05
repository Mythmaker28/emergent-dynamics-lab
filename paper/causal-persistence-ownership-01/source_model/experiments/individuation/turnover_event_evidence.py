"""Persisted evidence and frozen classification for turnover integrity events."""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

CONFIRM_FRAMES = 5
SPLIT_PARENT_FRACTION = 0.30
DESCENDANT_MATCH_FRACTION = 0.10
DEATH_LOCAL_MASS_RATIO = 0.20
LOCAL_DILATION_RADIUS = 3


def overlap_fraction(reference: np.ndarray, candidate: np.ndarray) -> float:
    denom = int(np.asarray(reference, dtype=bool).sum())
    if denom == 0:
        return 0.0
    return float((np.asarray(reference, dtype=bool) & np.asarray(candidate, dtype=bool)).sum() / denom)


def periodic_dilate(mask: np.ndarray, radius: int = LOCAL_DILATION_RADIUS) -> np.ndarray:
    out = np.asarray(mask, dtype=bool).copy()
    base = out.copy()
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dy * dy + dx * dx <= radius * radius:
                out |= np.roll(base, shift=(dy, dx), axis=(0, 1))
    return out


def _frame_summary(parent_masks: Sequence[np.ndarray], component_masks: Sequence[np.ndarray], rho: np.ndarray) -> dict:
    overlap = [
        [overlap_fraction(parent, component) for component in component_masks]
        for parent in parent_masks
    ]
    best = [int(np.argmax(row)) if row else None for row in overlap]
    claimants = {}
    for track_id, comp_id in enumerate(best):
        if comp_id is not None:
            claimants.setdefault(str(comp_id), []).append(int(track_id))
    return {
        "parent_sizes": [int(np.asarray(m, dtype=bool).sum()) for m in parent_masks],
        "parent_mass": [float(rho[np.asarray(m, dtype=bool)].sum()) for m in parent_masks],
        "component_sizes": [int(np.asarray(m, dtype=bool).sum()) for m in component_masks],
        "overlap_parent_fraction": overlap,
        "best_component_by_parent": best,
        "claimants_by_component": claimants,
    }


def start_event(
    raw_status: str,
    track_id: int,
    step: int,
    parent_masks: Sequence[np.ndarray],
    component_masks: Sequence[np.ndarray],
    rho: np.ndarray,
) -> tuple[dict, dict]:
    parent_masks = [np.asarray(m, dtype=bool).copy() for m in parent_masks]
    component_masks = [np.asarray(m, dtype=bool).copy() for m in component_masks]
    summary = _frame_summary(parent_masks, component_masks, rho)
    record = {
        "track_id": int(track_id),
        "event_step": int(step),
        "raw_tracker_status": str(raw_status),
        "event_frame": summary,
        "followup": [],
        "classification": None,
        "classification_rule_version": "TURNOVER-EVENTS-03C-v1",
    }
    state = {
        "parent_masks": parent_masks,
        "lost_region": periodic_dilate(parent_masks[track_id]),
        "lost_mass0": max(float(rho[periodic_dilate(parent_masks[track_id])].sum()), 1e-15),
        "descendants": [],
    }
    if raw_status == "SPLIT":
        row = summary["overlap_parent_fraction"][track_id]
        state["descendants"] = [
            component_masks[j].copy()
            for j, value in enumerate(row)
            if value >= SPLIT_PARENT_FRACTION
        ]
    return record, state


def append_followup(
    record: dict,
    state: dict,
    step: int,
    component_masks: Sequence[np.ndarray],
    rho: np.ndarray,
) -> None:
    component_masks = [np.asarray(m, dtype=bool).copy() for m in component_masks]
    descendants = state["descendants"]
    matched_descendants = []
    match_scores = []
    if descendants and component_masks:
        matrix = np.asarray(
            [[overlap_fraction(d, c) for c in component_masks] for d in descendants],
            dtype=float,
        )
        ri, cj = linear_sum_assignment(-matrix)
        for r, c in zip(ri, cj):
            if matrix[r, c] >= DESCENDANT_MATCH_FRACTION:
                matched_descendants.append(component_masks[c].copy())
                match_scores.append(float(matrix[r, c]))
    state["descendants"] = matched_descendants
    local_mass_ratio = float(rho[state["lost_region"]].sum() / state["lost_mass0"])
    record["followup"].append(
        {
            "step": int(step),
            "detected_component_count": int(len(component_masks)),
            "persistent_descendant_count": int(len(matched_descendants)),
            "descendant_match_fraction": match_scores,
            "local_mass_ratio": local_mass_ratio,
        }
    )


def finalize(record: dict) -> dict:
    status = record["raw_tracker_status"]
    followup = record["followup"]
    if status == "MERGED":
        cls = "MERGE"
    elif status == "SPLIT":
        event_row = record["event_frame"]["overlap_parent_fraction"][record["track_id"]]
        event_count = sum(v >= SPLIT_PARENT_FRACTION for v in event_row)
        persistent = (
            event_count >= 2
            and len(followup) == CONFIRM_FRAMES
            and all(frame["persistent_descendant_count"] >= 2 for frame in followup)
        )
        cls = "FISSION" if persistent else "TRANSIENT_FRAGMENTATION"
    elif status == "LOST":
        death = (
            len(followup) == CONFIRM_FRAMES
            and all(frame["local_mass_ratio"] <= DEATH_LOCAL_MASS_RATIO for frame in followup)
        )
        cls = "DEATH" if death else "LOSS"
    elif status == "AMBIGUOUS":
        cls = "AMBIGUOUS"
    else:
        cls = "UNCLASSIFIED"
    record["classification"] = cls
    record["classification_basis"] = {
        "confirm_frames": CONFIRM_FRAMES,
        "split_parent_fraction": SPLIT_PARENT_FRACTION,
        "descendant_match_fraction": DESCENDANT_MATCH_FRACTION,
        "death_local_mass_ratio": DEATH_LOCAL_MASS_RATIO,
        "outcome_used": False,
    }
    return record
