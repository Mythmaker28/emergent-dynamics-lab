"""Independent raw-only reproduction for COUNTERFACTUAL-HISTORY-CORE-00.

This module does not import the experiment runner.  It recomputes the primary
factorial contrasts, survival accounting, targeted first-stage gates, transport,
and final classification directly from the persisted JSON potential outcomes.
It never initializes a world or calls an engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t


HISTORIES = ("H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE")
ARMS = ("coupled", "isolated", "coupled_g0", "sham_own_replay_g0",
        "coupled_lamplus0", "isolated_lamplus0")
CONTRASTS = ("dose", "order", "interaction")
SIGN_FRACTION = 0.75


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def factorial(values: dict[str, float]) -> dict[str, float]:
    le = float(values["H_L_EARLY"])
    ll = float(values["H_L_LATE"])
    he = float(values["H_H_EARLY"])
    hl = float(values["H_H_LATE"])
    return {
        "dose": 0.5 * ((he + hl) - (le + ll)),
        "order": 0.5 * ((le + he) - (ll + hl)),
        "interaction": (he - hl) - (le - ll),
    }


def summarize(values: list[float], expected: str | None = None) -> dict:
    array = np.asarray(values, dtype=float)
    n = int(array.size)
    if n == 0:
        return {"n_worlds": 0, "values": []}
    mean = float(array.mean())
    sd = float(array.std(ddof=1)) if n > 1 else None
    if n > 1:
        half = float(student_t.ppf(0.975, n - 1) * array.std(ddof=1) / math.sqrt(n))
        ci = [mean - half, mean + half]
    else:
        ci = [None, None]
    positive = int((array > 0).sum())
    negative = int((array < 0).sum())
    required = int(math.ceil(SIGN_FRACTION * n))
    passes = None
    if expected == "positive":
        passes = bool(positive >= required and ci[0] is not None and ci[0] > 0)
    elif expected == "negative":
        passes = bool(negative >= required and ci[1] is not None and ci[1] < 0)
    return {
        "n_worlds": n,
        "values": array.tolist(),
        "mean": mean,
        "median": float(np.median(array)),
        "sd": sd,
        "ci95_t": ci,
        "positive": positive,
        "negative": negative,
        "required_same_orientation": required,
        "expected_orientation": expected,
        "passes_expected_orientation_and_ci": passes,
    }


def two_sided_gate(summary: dict) -> bool:
    if summary.get("n_worlds", 0) < 4:
        return False
    lo, hi = summary["ci95_t"]
    return bool(
        (lo > 0 or hi < 0)
        and max(summary["positive"], summary["negative"]) >= summary["required_same_orientation"]
    )


def _equal_float(a, b, atol=1e-12, rtol=1e-10) -> bool:
    return bool(np.isclose(float(a), float(b), atol=atol, rtol=rtol))


def _equal_summary(a: dict, b: dict) -> bool:
    exact_keys = ("n_worlds", "positive", "negative", "required_same_orientation",
                  "expected_orientation", "passes_expected_orientation_and_ci")
    if any(a.get(key) != b.get(key) for key in exact_keys):
        return False
    numeric_keys = ("mean", "median", "sd")
    for key in numeric_keys:
        if a.get(key) is None or b.get(key) is None:
            if a.get(key) != b.get(key):
                return False
        elif not _equal_float(a[key], b[key]):
            return False
    if len(a.get("values", [])) != len(b.get("values", [])):
        return False
    if not np.allclose(a.get("values", []), b.get("values", []), atol=1e-12, rtol=1e-10):
        return False
    for left, right in zip(a.get("ci95_t", []), b.get("ci95_t", [])):
        if left is None or right is None:
            if left != right:
                return False
        elif not _equal_float(left, right):
            return False
    return True


def reproduce(raw: dict) -> dict:
    worlds = raw["worlds"]
    stored = raw["summary"]
    eligible = [world for world in worlds if world.get("prehistory_eligible")]
    complete = [world for world in worlds if world.get("complete_block")]

    per_world_arm = {}
    per_world_first = {}
    per_world_transport = {}
    stored_world_contrasts_match = True
    for world in complete:
        seed = str(world["seed"])
        per_world_arm[seed] = {}
        for arm in ARMS:
            endpoints = {
                history: world["branches"][history]["probe"]["arms"][arm]["integrated_tracked_step40"]
                for history in HISTORIES
            }
            values = factorial(endpoints)
            per_world_arm[seed][arm] = values
            for contrast in CONTRASTS:
                stored_world_contrasts_match &= _equal_float(
                    values[contrast], world["arm_contrasts"][arm]["tracked"][contrast]
                )
        per_world_first[seed] = {}
        for feature in ("mplus_mean", "mminus_mean"):
            endpoints = {
                history: world["branches"][history]["probe"]["first_stage"][feature]
                for history in HISTORIES
            }
            values = factorial(endpoints)
            per_world_first[seed][feature] = values
            for contrast in CONTRASTS:
                stored_world_contrasts_match &= _equal_float(
                    values[contrast], world["first_stage_contrasts"][feature][contrast]
                )
        per_world_transport[seed] = {
            contrast: per_world_arm[seed]["isolated"][contrast]
            - per_world_arm[seed]["coupled"][contrast]
            for contrast in CONTRASTS
        }

    feeding = {
        arm: {
            contrast: summarize(
                [per_world_arm[str(world["seed"])][arm][contrast] for world in complete],
                expected=("positive" if arm in ("coupled", "isolated") and contrast == "dose" else None),
            )
            for contrast in CONTRASTS
        }
        for arm in ARMS
    }
    first_stage = {
        "mplus_mean": {
            contrast: summarize(
                [per_world_first[str(world["seed"])]["mplus_mean"][contrast] for world in complete],
                expected=("positive" if contrast == "dose" else None),
            ) for contrast in CONTRASTS
        },
        "mminus_mean": {
            contrast: summarize(
                [per_world_first[str(world["seed"])]["mminus_mean"][contrast] for world in complete],
                expected=("negative" if contrast == "order" else None),
            ) for contrast in CONTRASTS
        },
    }
    transport = {
        contrast: summarize([
            per_world_transport[str(world["seed"])][contrast] for world in complete
        ]) for contrast in CONTRASTS
    }

    survival = {
        history: {"assigned": 0, "posthistory_alive": 0, "deep_alive": 0, "complete_probe": 0}
        for history in HISTORIES
    }
    survival_values = {contrast: [] for contrast in CONTRASTS}
    for world in eligible:
        potential = {}
        for history in HISTORIES:
            branch = world["branches"][history]
            survival[history]["assigned"] += 1
            survival[history]["posthistory_alive"] += int(branch.get("posthistory_alive", False))
            survival[history]["deep_alive"] += int(branch.get("deep_valid", False))
            survival[history]["complete_probe"] += int(branch.get("complete_probe", False))
            potential[history] = float(branch.get("deep_valid", False))
        contrasts = factorial(potential)
        for contrast, value in contrasts.items():
            survival_values[contrast].append(value)
    survival_contrasts = {
        contrast: summarize(values) for contrast, values in survival_values.items()
    }
    survival_effect = any(two_sided_gate(summary) for summary in survival_contrasts.values())

    enough = len(complete) >= 4
    clone_valid = all(world["clone_checkpoint"]["valid"] for world in eligible)
    sham_valid = bool(enough and all(
        world["branches"][history]["probe"]["sham_exact"]
        for world in complete for history in HISTORIES
    ))
    dose_stage = bool(enough and first_stage["mplus_mean"]["dose"]["passes_expected_orientation_and_ci"])
    order_stage = bool(enough and first_stage["mminus_mean"]["order"]["passes_expected_orientation_and_ci"])
    dose_feed = bool(enough and feeding["isolated"]["dose"]["passes_expected_orientation_and_ci"])
    coupled_dose_direction = bool(enough and feeding["coupled"]["dose"]["median"] > 0)
    iso_order = feeding["isolated"]["order"]
    coupled_order = feeding["coupled"]["order"]
    order_feed = bool(
        enough and two_sided_gate(iso_order)
        and iso_order["median"] != 0 and coupled_order["median"] != 0
        and math.copysign(1.0, iso_order["median"]) == math.copysign(1.0, coupled_order["median"])
    )
    if not enough:
        conclusion = "DEV-FEASIBILITY-FAIL"
    elif not sham_valid:
        conclusion = "MANIPULATION_INVALID"
    elif survival_effect:
        conclusion = "SURVIVAL_EFFECT"
    elif not dose_stage and not order_stage:
        conclusion = "NO_MEMORY_FIRST_STAGE"
    elif order_stage and not order_feed:
        conclusion = "ORDER_STATE_WITHOUT_FEEDING"
    elif dose_stage and dose_feed and coupled_dose_direction and order_stage and order_feed:
        conclusion = "DOSE_AND_ORDER"
    elif dose_stage and dose_feed and coupled_dose_direction and not (order_stage and order_feed):
        conclusion = "DOSE_ONLY"
    elif (dose_stage or order_stage) and not (dose_feed or order_feed):
        conclusion = "NO_TRANSPORT"
    else:
        conclusion = "UNRESOLVED"

    comparisons = {
        "n_eligible": len(eligible) == stored["n_pre_history_eligible_worlds"],
        "n_complete": len(complete) == stored["n_complete_valid_worlds"],
        "survival_counts": survival == stored["survival_by_history"],
        "survival_effect": survival_effect == stored["survival_effect_detected"],
        "conclusion": conclusion == stored["conclusion"],
        "world_contrasts": stored_world_contrasts_match,
        "clone_gate": clone_valid == stored["gates"]["exact_clone_valid_all_eligible_worlds"],
        "sham_gate": sham_valid == stored["gates"]["manipulation_sham_exact"],
    }
    for arm in ARMS:
        for contrast in CONTRASTS:
            comparisons[f"feeding::{arm}::{contrast}"] = _equal_summary(
                feeding[arm][contrast], stored["feeding_contrasts"][arm][contrast]
            )
    for feature in ("mplus_mean", "mminus_mean"):
        for contrast in CONTRASTS:
            comparisons[f"first_stage::{feature}::{contrast}"] = _equal_summary(
                first_stage[feature][contrast], stored["first_stage"][feature][contrast]
            )
    for contrast in CONTRASTS:
        comparisons[f"transport::{contrast}"] = _equal_summary(
            transport[contrast], stored["transport_isolated_minus_coupled"][contrast]
        )
        comparisons[f"survival::{contrast}"] = _equal_summary(
            survival_contrasts[contrast], stored["survival_factorial_contrasts"][contrast]
        )
    return {
        "schema": "COUNTERFACTUAL-HISTORY-CORE-00-RAW-REPRODUCTION-v1",
        "pass": all(comparisons.values()),
        "comparisons": comparisons,
        "reproduced": {
            "n_planned": len(worlds),
            "n_eligible": len(eligible),
            "n_complete": len(complete),
            "survival_by_history": survival,
            "survival_effect_detected": survival_effect,
            "targeted_first_stage": first_stage,
            "primary_feeding": {arm: feeding[arm] for arm in ("coupled", "isolated")},
            "transport": transport,
            "conclusion": conclusion,
            "prereg_candidate_go": False,
        },
        "engine_initialized": False,
        "prospective_execution_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_sha = sha256_file(args.raw)
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    result = reproduce(raw)
    result["source_raw_sha256"] = raw_sha
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "source_raw_sha256": raw_sha,
                      "output_sha256": sha256_file(args.output)}, sort_keys=True))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
