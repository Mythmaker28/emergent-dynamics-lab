"""Raw-only reproduction for M_MINUS-ORDER-READER-00.

Reads the persisted reader JSON only.  It imports neither the reader runner nor
the simulation engine and initializes no world.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.stats import t as student_t


SCHEMA = "M_MINUS-ORDER-READER-00-DEV-v1"
REPRO_SCHEMA = "M_MINUS-ORDER-READER-00-RAW-REPRODUCTION-v1"
PROTOCOL_SHA256 = "d0096f028b9d9e35d6cabb54b73c0e47ca8ee512efb8b0702c8ab8de86cf2ead"
PARENT_COMMIT = "ea6e6a0ab2ccc3e94eba364ddb459088c96d6033"
PARENT_RAW_SHA256 = "d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6"
COMPLETE_SEEDS = (
    57001, 57003, 57006, 57008, 57009, 57010, 57013, 57015, 57016,
    57017, 57018, 57019, 57020, 57021, 57022, 57023, 57024,
)
HISTORIES = ("H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE")
SIGN_FRACTION = 0.75
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW = REPO_ROOT / "docs" / "individuation" / "M_MINUS_ORDER_READER_00_DEV_RESULTS.json"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "individuation" / "M_MINUS_ORDER_READER_00_RAW_REPRODUCTION.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")
    os.replace(temp, path)


def factorial(values: dict[str, float]) -> dict[str, float]:
    le = float(values["H_L_EARLY"])
    ll = float(values["H_L_LATE"])
    he = float(values["H_H_EARLY"])
    hl = float(values["H_H_LATE"])
    return {
        "dose": 0.5 * ((he + hl) - (le + ll)),
        "order": 0.5 * ((le - ll) + (he - hl)),
        "interaction": (he - hl) - (le - ll),
    }


def summary(values: Iterable[float], expected: str | None = None) -> dict:
    array = np.asarray(list(values), dtype=float)
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
    oriented = None
    if expected == "positive":
        oriented = bool(positive >= required and ci[0] is not None and ci[0] > 0)
    elif expected == "negative":
        oriented = bool(negative >= required and ci[1] is not None and ci[1] < 0)
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
        "passes_expected_orientation_and_ci": oriented,
    }


def _close(a: float, b: float) -> bool:
    return bool(np.isclose(float(a), float(b), atol=NUMERIC_ATOL, rtol=NUMERIC_RTOL))


def _recompute_world(world: dict) -> dict:
    histories = world["histories"]
    if set(histories) != set(HISTORIES):
        raise RuntimeError(f"history order mismatch in {world['seed']}")
    mappings = {
        "deep_mminus": {name: histories[name]["deep"]["mminus_mean"] for name in HISTORIES},
        "chi_raw": {name: histories[name]["intact"]["chi_raw"] for name in HISTORIES},
        "chi_per_core_mass": {name: histories[name]["intact"]["chi_per_core_mass"] for name in HISTORIES},
        "chi_raw_lam_minus_zero": {
            name: histories[name]["lam_minus_zero"]["chi_raw"] for name in HISTORIES
        },
        "chi_per_core_mass_lam_minus_zero": {
            name: histories[name]["lam_minus_zero"]["chi_per_core_mass"] for name in HISTORIES
        },
    }
    contrasts = {key: factorial(values) for key, values in mappings.items()}
    contrasts.update({
        "low_dose_order_raw": float(mappings["chi_raw"]["H_L_EARLY"] - mappings["chi_raw"]["H_L_LATE"]),
        "high_dose_order_raw": float(mappings["chi_raw"]["H_H_EARLY"] - mappings["chi_raw"]["H_H_LATE"]),
        "low_dose_order_per_core_mass": float(
            mappings["chi_per_core_mass"]["H_L_EARLY"] - mappings["chi_per_core_mass"]["H_L_LATE"]
        ),
        "high_dose_order_per_core_mass": float(
            mappings["chi_per_core_mass"]["H_H_EARLY"] - mappings["chi_per_core_mass"]["H_H_LATE"]
        ),
    })
    contrasts["order_attenuation_fraction"] = float(
        1.0 - abs(contrasts["chi_raw_lam_minus_zero"]["order"])
        / max(abs(contrasts["chi_raw"]["order"]), 1e-300)
    )
    comparisons = {}
    for key, recomputed in contrasts.items():
        stored = world["contrasts"][key]
        if isinstance(recomputed, dict):
            comparisons[key] = all(_close(recomputed[c], stored[c]) for c in ("dose", "order", "interaction"))
        else:
            comparisons[key] = _close(recomputed, stored)
    manipulation = bool(
        world.get("manipulation_valid")
        and all(history[condition].get("valid") for history in histories.values()
                for condition in ("intact", "lam_minus_zero"))
        and all(history[condition].get("deterministic_rerun_exact") for history in histories.values()
                for condition in ("intact", "lam_minus_zero"))
        and all(history["lam_minus_zero"]["gates"].get("lam_minus_zero_arms_identical")
                for history in histories.values())
    )
    return {
        "seed": int(world["seed"]),
        "contrasts": contrasts,
        "stored_contrasts_match": comparisons,
        "all_stored_contrasts_match": all(comparisons.values()),
        "manipulation_valid": manipulation,
    }


def classify(rows: list[dict]) -> tuple[str, dict]:
    state = summary((row["contrasts"]["deep_mminus"]["order"] for row in rows), expected="positive")
    order_raw = summary((row["contrasts"]["chi_raw"]["order"] for row in rows), expected="positive")
    order_norm = summary((row["contrasts"]["chi_per_core_mass"]["order"] for row in rows), expected="positive")
    low_raw = summary((row["contrasts"]["low_dose_order_raw"] for row in rows), expected="positive")
    high_raw = summary((row["contrasts"]["high_dose_order_raw"] for row in rows), expected="positive")
    ablated = summary((row["contrasts"]["chi_raw_lam_minus_zero"]["order"] for row in rows))
    attenuation = summary((row["contrasts"]["order_attenuation_fraction"] for row in rows))
    if not all(row["manipulation_valid"] for row in rows):
        classification = "MANIPULATION_INVALID"
    else:
        lo, hi = ablated["ci95_t"]
        candidate = bool(
            state["passes_expected_orientation_and_ci"]
            and order_raw["passes_expected_orientation_and_ci"]
            and low_raw["positive"] >= low_raw["required_same_orientation"]
            and high_raw["positive"] >= high_raw["required_same_orientation"]
            and order_norm["passes_expected_orientation_and_ci"]
            and attenuation["mean"] >= 0.90
            and lo <= 0 <= hi
        )
        primary = bool(order_raw["passes_expected_orientation_and_ci"])
        normalized_reversal = bool(order_raw["mean"] > 0 and order_norm["mean"] <= 0)
        ablation_persists = bool(lo > 0 or hi < 0)
        if candidate:
            classification = "ORDER_READER_CANDIDATE"
        elif state["passes_expected_orientation_and_ci"] and not primary:
            classification = "ORDER_STATE_WITHOUT_READER_EFFECT"
        elif primary and (ablation_persists or normalized_reversal):
            classification = "PHYSICAL_SUSCEPTIBILITY"
        else:
            classification = "UNRESOLVED"
    return classification, {
        "deep_mminus_order": state,
        "chi_order_raw": order_raw,
        "chi_order_per_core_mass": order_norm,
        "low_dose_order_raw": low_raw,
        "high_dose_order_raw": high_raw,
        "chi_order_lam_minus_zero": ablated,
        "order_attenuation_fraction": attenuation,
    }


def reproduce(raw_path: Path) -> dict:
    raw_sha = sha256_file(raw_path)
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA or payload.get("status") != "COMPLETE":
        raise RuntimeError("reader raw schema/status mismatch")
    if payload.get("protocol_sha256") != PROTOCOL_SHA256:
        raise RuntimeError("reader protocol binding mismatch")
    if payload.get("parent_commit") != PARENT_COMMIT:
        raise RuntimeError("reader parent mismatch")
    if payload.get("parent_raw_persisted_sha256") != PARENT_RAW_SHA256:
        raise RuntimeError("reader parent raw binding mismatch")
    worlds = payload.get("worlds", [])
    if tuple(int(row["seed"]) for row in worlds) != COMPLETE_SEEDS:
        raise RuntimeError("reader original-world set mismatch")
    recomputed = [_recompute_world(world) for world in worlds]
    classification, summaries = classify(recomputed)
    stored_match = classification == payload.get("classification")
    comparisons_pass = all(row["all_stored_contrasts_match"] for row in recomputed)
    prohibited = [name for name in sys.modules if name.startswith("edlab")
                  or name.endswith("mminus_order_reader_dev")]
    return {
        "schema": REPRO_SCHEMA,
        "source_raw_sha256": raw_sha,
        "protocol_sha256": PROTOCOL_SHA256,
        "n_original_worlds": len(recomputed),
        "seeds": list(COMPLETE_SEEDS),
        "original_world_statistical_unit": True,
        "engine_initialized": False,
        "runner_imported": False,
        "prohibited_runtime_modules": prohibited,
        "per_world": recomputed,
        "summaries": summaries,
        "classification": classification,
        "stored_classification": payload.get("classification"),
        "stored_classification_match": stored_match,
        "all_stored_contrasts_match": comparisons_pass,
        "reproduction_pass": bool(stored_match and comparisons_pass and not prohibited),
        "claim_boundary": payload.get("claim_boundary"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = reproduce(args.raw)
    _write_json(args.output, result)
    print(result["classification"])


if __name__ == "__main__":
    main()
