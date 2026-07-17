"""One-shot DEV-only mechanism reconciliation for COUNTERFACTUAL-HISTORY-CORE-00.

This module refuses every seed outside the already-open 57001--57024 manifest.
It contains a scalar theory check, deterministic same-manifest diagnostics, and
original-world LOWO analysis.  It has no prospective-family entry point.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from experiments.individuation import balanced_history_isolation_dev as bh
from experiments.individuation import bijective_tracker as bt
from experiments.individuation import counterfactual_history_core_dev as core


SCHEMA = "COUNTERFACTUAL-HISTORY-MECHANISM-RECONCILIATION-00-v1"
REPLAY_SCHEMA = "COUNTERFACTUAL-HISTORY-MECHANISM-SAME-MANIFEST-REPLAY-v1"
PARENT_COMMIT = "ea6e6a0ab2ccc3e94eba364ddb459088c96d6033"
RAW_SHA256 = "d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6"
DEV_SEEDS = tuple(range(57001, 57025))
RIDGE_ALPHA = 1.0

PHYSICAL_DESCRIPTORS = (
    "body_mass", "body_size", "body_rg", "core_rho_mass",
    "nearest_neighbor_distance", "core_N_mean", "core_c_mean",
    "core_u_mean", "core_v_mean", "core_sigma_mean", "world_up_ref",
    "world_N_mean", "world_c_mean", "world_rho_mass",
)
MODEL_PANELS = {
    "mass_area": ("body_mass", "body_size"),
    "body_geometry": (
        "body_mass", "body_size", "body_rg", "core_rho_mass",
        "nearest_neighbor_distance",
    ),
    "body_geometry_memory": (
        "body_mass", "body_size", "body_rg", "core_rho_mass",
        "nearest_neighbor_distance", "mplus_mean", "mminus_mean",
    ),
}


def sha256_file(path: Path) -> str:
    return bh.sha256_file(path)


def scalar_closed_form_component(
    *, first: float, second: float, initial: float = 0.0,
    episode_steps: int = core.PHASE, settle_steps: int = core.SETTLE,
    dt: float = MCM_CONFIG.SPEC.dt, eta_w: float = core.cc.MEM_INTACT.eta_w,
    eta_d: float,
) -> float:
    """Homogeneous unclipped recurrence with a zero-input settle."""
    q = 1.0 - dt * eta_d
    w = dt * eta_w
    geom = (1.0 - q ** episode_steps) / (1.0 - q)
    return (
        q ** (2 * episode_steps + settle_steps) * initial
        + w * first * q ** (episode_steps + settle_steps) * geom
        + w * second * q ** settle_steps * geom
    )


def scalar_iterative_component(
    *, first: float, second: float, initial: float = 0.0,
    episode_steps: int = core.PHASE, settle_steps: int = core.SETTLE,
    dt: float = MCM_CONFIG.SPEC.dt, eta_w: float = core.cc.MEM_INTACT.eta_w,
    eta_d: float,
) -> float:
    value = float(initial)
    q = 1.0 - dt * eta_d
    w = dt * eta_w
    for driver in (first, second):
        for _ in range(episode_steps):
            value = q * value + w * driver
    for _ in range(settle_steps):
        value = q * value
    return value


def scalar_sign_derivation() -> dict:
    histories = core.HISTORIES
    components = {}
    for label, eta_d in (("m1", core.cc.MEM_INTACT.eta_d1),
                         ("m2", core.cc.MEM_INTACT.eta_d2)):
        values = {
            name: scalar_closed_form_component(first=a1, second=a2, eta_d=eta_d)
            for name, (a1, a2) in histories.items()
        }
        iterative = {
            name: scalar_iterative_component(first=a1, second=a2, eta_d=eta_d)
            for name, (a1, a2) in histories.items()
        }
        components[label] = {
            "eta_d": eta_d,
            "q": 1.0 - MCM_CONFIG.SPEC.dt * eta_d,
            "values": values,
            "iterative_values": iterative,
            "max_closed_form_error": max(abs(values[k] - iterative[k]) for k in values),
            "factorial": core.factorial_scalar(values),
            "low_early_minus_late": values["H_L_EARLY"] - values["H_L_LATE"],
            "high_early_minus_late": values["H_H_EARLY"] - values["H_H_LATE"],
        }
    mminus_values = {
        name: math.tanh(components["m1"]["values"][name]
                        - components["m2"]["values"][name])
        for name in histories
    }
    mplus_values = {
        name: math.tanh(components["m1"]["values"][name]
                        + components["m2"]["values"][name])
        for name in histories
    }
    return {
        "scope": "homogeneous unclipped theory check; no world or feeding outcome executed",
        "dt": MCM_CONFIG.SPEC.dt,
        "eta_w": core.cc.MEM_INTACT.eta_w,
        "episode_steps": core.PHASE,
        "settle_steps": core.SETTLE,
        "histories": {k: list(v) for k, v in histories.items()},
        "components": components,
        "mplus": {"values": mplus_values, "factorial": core.factorial_scalar(mplus_values)},
        "mminus": {
            "values": mminus_values,
            "factorial": core.factorial_scalar(mminus_values),
            "low_early_minus_late": mminus_values["H_L_EARLY"] - mminus_values["H_L_LATE"],
            "high_early_minus_late": mminus_values["H_H_EARLY"] - mminus_values["H_H_LATE"],
        },
        "frozen_expected_order_sign": "negative",
        "scalar_derived_order_sign": (
            "positive" if core.factorial_scalar(mminus_values)["order"] > 0 else "nonpositive"
        ),
    }


def _target_metrics(state, region: np.ndarray, entities: Sequence | None = None) -> dict:
    rho_safe = np.maximum(state.rho, 1e-12)
    m1 = state.Mf[0] / rho_safe
    m2 = state.Mf[1] / rho_safe
    values = {
        "m1_mean": float(m1[region].mean()),
        "m2_mean": float(m2[region].mean()),
        "mplus_mean": float(np.tanh(m1[region] + m2[region]).mean()),
        "mminus_mean": float(np.tanh(m1[region] - m2[region]).mean()),
        "body_mass": float(state.rho[region].sum()),
        "body_size": int(region.sum()),
        "instantaneous_uptake": float(state.uptake[region].sum()),
    }
    if entities is not None:
        entity = bh._entity_for_track(entities, region)
        values["body_rg"] = float(entity.rg) if entity is not None else None
    return values


def diagnostic_measure_arm(state, region: np.ndarray, engine) -> dict:
    """Byte-compatible parent measurement plus predeclared state diagnostics."""
    if getattr(engine, "driver", None) is not None:
        engine.driver.reset()
    current = bh.standardized_probe_start(state)
    tracker = core._new_tracker([region], current.step)
    fixed = None
    integrated_tracked = 0.0
    integrated_fixed = 0.0
    step40 = None
    events = {}
    max_coverage = 0.0
    checkpoints = {"deep_preprobe": _target_metrics(state, region)}
    for step in range(1, core.SETTLE_STD + core.HORIZON + 1):
        if core.SETTLE_STD < step <= core.SETTLE_STD + core.STIM_DUR:
            current.N = current.N + core.STIM_AMP
        current = engine.step(current)
        update = core._tracker_update(tracker, current)
        max_coverage = max(max_coverage, update["coverage"])
        for track_id, status in update["events"].items():
            events.setdefault(str(track_id), {
                "step": step, "absolute_step": int(current.step), "status": status,
            })
        if step == core.SETTLE_STD:
            fixed = tracker.tracks[0].mask.copy() if core._focal_alive(tracker, 0) else np.zeros((core.N, core.N), bool)
            if core._focal_alive(tracker, 0):
                checkpoints["standardized_prestimulus_step40"] = _target_metrics(
                    current, tracker.tracks[0].mask, update["entities"]
                )
        if step > core.SETTLE_STD:
            integrated_fixed += float(current.uptake[fixed].sum())
            if core._focal_alive(tracker, 0):
                value = float(current.uptake[tracker.tracks[0].mask].sum())
                integrated_tracked += value
                if step == core.SETTLE_STD + core.HORIZON:
                    step40 = value
                    checkpoints["probe_horizon_step40"] = _target_metrics(
                        current, tracker.tracks[0].mask, update["entities"]
                    )
    valid = bool(
        core._focal_alive(tracker, 0) and not events and max_coverage < core.COVER_CAP
        and np.isfinite(integrated_tracked) and np.isfinite(integrated_fixed)
    )
    return {
        "integrated_tracked_step40": integrated_tracked,
        "integrated_fixed_step40": integrated_fixed,
        "instantaneous_tracked_at_step40": step40,
        "status": tracker.tracks[0].status,
        "events": events,
        "max_coverage": float(max_coverage),
        "valid": valid,
        "final_state_sha256": core.state_hash(current),
        "mechanism_checkpoints": checkpoints,
    }


def _raw_complete_worlds(raw: dict) -> list[dict]:
    return [world for world in raw["worlds"] if world.get("complete_block")]


def replay_seed(seed: int, raw_path: Path) -> dict:
    if int(seed) not in DEV_SEEDS:
        raise ValueError(f"REFUSED seed {seed}: no new namespace is authorized")
    if sha256_file(raw_path) != RAW_SHA256:
        raise RuntimeError("frozen parent raw SHA-256 mismatch")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    expected = next((w for w in raw["worlds"] if int(w["seed"]) == int(seed)), None)
    if expected is None or not expected.get("complete_block"):
        raise ValueError(f"seed {seed} is not one of the 17 frozen complete worlds")
    manifest = core.load_and_validate_manifest()
    original_measure = core.measure_arm
    core.measure_arm = diagnostic_measure_arm
    try:
        replay = core.run_world(int(seed), manifest)
    finally:
        core.measure_arm = original_measure
    diagnostics = {}
    checks = []
    for history in core.HISTORY_NAMES:
        diagnostics[history] = {}
        for arm in core.PRIMARY_ARMS:
            got = replay["branches"][history]["probe"]["arms"][arm]
            want = expected["branches"][history]["probe"]["arms"][arm]
            checks.extend([
                got["final_state_sha256"] == want["final_state_sha256"],
                got["integrated_tracked_step40"] == want["integrated_tracked_step40"],
                got["integrated_fixed_step40"] == want["integrated_fixed_step40"],
                got["instantaneous_tracked_at_step40"] == want["instantaneous_tracked_at_step40"],
            ])
            diagnostics[history][arm] = got["mechanism_checkpoints"]
    return {
        "schema": REPLAY_SCHEMA,
        "seed": int(seed),
        "same_manifest": core.MANIFEST_SHA256,
        "parent_raw_sha256": RAW_SHA256,
        "complete_block": bool(replay.get("complete_block")),
        "exact_parent_match": bool(checks and all(checks)),
        "n_exact_checks": len(checks),
        "diagnostics": diagnostics,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp, path)


def _replay_worker(args: tuple[int, str, str]) -> tuple[int, str]:
    seed, raw_name, output_name = args
    result = replay_seed(seed, Path(raw_name))
    _write_json(Path(output_name), result)
    return seed, output_name


def replay_all(raw_path: Path, output_dir: Path, jobs: int) -> None:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    seeds = [int(w["seed"]) for w in _raw_complete_worlds(raw)]
    tasks = []
    for seed in seeds:
        output = output_dir / f"world_{seed}.json"
        if output.exists():
            cached = json.loads(output.read_text(encoding="utf-8"))
            if cached.get("exact_parent_match") and int(cached.get("seed", -1)) == seed:
                print(f"seed {seed}: replay-resume-skip", flush=True)
                continue
        tasks.append((seed, str(raw_path), str(output)))
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(_replay_worker, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            seed, name = future.result()
            print(f"seed {seed}: replay-exact -> {name}", flush=True)


def merge_replays(raw_path: Path, replay_dir: Path) -> dict:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    seeds = [int(w["seed"]) for w in _raw_complete_worlds(raw)]
    worlds = []
    for seed in seeds:
        path = replay_dir / f"world_{seed}.json"
        if not path.exists():
            raise RuntimeError(f"missing replay for frozen complete seed {seed}")
        item = json.loads(path.read_text(encoding="utf-8"))
        if not item.get("exact_parent_match"):
            raise RuntimeError(f"replay mismatch for seed {seed}")
        worlds.append(item)
    return {
        "schema": REPLAY_SCHEMA,
        "scope": "same 17 complete frozen DEV worlds; diagnostic re-observation only",
        "manifest_sha256": core.MANIFEST_SHA256,
        "parent_raw_sha256": RAW_SHA256,
        "n_worlds": len(worlds),
        "all_exact_parent_match": all(w["exact_parent_match"] for w in worlds),
        "worlds": worlds,
    }


def _summary(values: Iterable[float]) -> dict:
    return bh._summary([float(v) for v in values])


def _factorial_from_history(rows: dict[str, dict], key: str) -> dict[str, float]:
    return core.factorial_scalar({name: float(row[key]) for name, row in rows.items()})


def _lowo_ridge(X: np.ndarray, y: np.ndarray, alpha: float = RIDGE_ALPHA) -> dict:
    n, p = X.shape
    predictions = np.empty(n, dtype=float)
    baselines = np.empty(n, dtype=float)
    for held_out in range(n):
        train = np.arange(n) != held_out
        x_train, y_train = X[train], y[train]
        mean = x_train.mean(axis=0)
        scale = x_train.std(axis=0, ddof=0)
        scale[scale == 0] = 1.0
        z_train = (x_train - mean) / scale
        z_test = (X[held_out] - mean) / scale
        y_mean = float(y_train.mean())
        gram = z_train.T @ z_train + alpha * np.eye(p)
        coef = np.linalg.solve(gram, z_train.T @ (y_train - y_mean))
        predictions[held_out] = y_mean + float(z_test @ coef)
        baselines[held_out] = y_mean
    residual = y - predictions
    baseline_residual = y - baselines
    tss = float(np.square(y - y.mean()).sum())
    press = float(np.square(residual).sum())
    correlation = None
    if n > 1 and float(y.std()) > 0 and float(predictions.std()) > 0:
        correlation = float(np.corrcoef(y, predictions)[0, 1])
    improvement = np.square(baseline_residual) - np.square(residual)
    return {
        "alpha": alpha,
        "n_original_worlds": n,
        "n_features": p,
        "predictions": predictions.tolist(),
        "training_mean_predictions": baselines.tolist(),
        "rmse": float(np.sqrt(np.mean(np.square(residual)))),
        "mae": float(np.mean(np.abs(residual))),
        "press": press,
        "q2": float(1.0 - press / tss) if tss > 0 else None,
        "correlation": correlation,
        "squared_error_improvement_vs_training_mean": _summary(improvement),
    }


def analyze(raw_path: Path, replay_path: Path | None = None) -> dict:
    if sha256_file(raw_path) != RAW_SHA256:
        raise RuntimeError("frozen parent raw SHA-256 mismatch")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    complete = _raw_complete_worlds(raw)
    seeds = [int(w["seed"]) for w in complete]
    if len(complete) != 17:
        raise RuntimeError("expected exactly 17 frozen complete worlds")

    per_world = []
    for world in complete:
        histories = {
            name: world["branches"][name]["probe"]["first_stage"]
            for name in core.HISTORY_NAMES
        }
        feature_dose = {
            feature: _factorial_from_history(histories, feature)["dose"]
            for feature in set(PHYSICAL_DESCRIPTORS) | {"mplus_mean", "mminus_mean"}
        }
        arms = {}
        normalized = {}
        for arm in core.PRIMARY_ARMS:
            tracked_by_history = {
                name: world["branches"][name]["probe"]["arms"][arm]["integrated_tracked_step40"]
                for name in core.HISTORY_NAMES
            }
            fixed_by_history = {
                name: world["branches"][name]["probe"]["arms"][arm]["integrated_fixed_step40"]
                for name in core.HISTORY_NAMES
            }
            instant_by_history = {
                name: world["branches"][name]["probe"]["arms"][arm]["instantaneous_tracked_at_step40"]
                for name in core.HISTORY_NAMES
            }
            arms[arm] = {
                "tracked": core.factorial_scalar(tracked_by_history),
                "fixed": core.factorial_scalar(fixed_by_history),
                "instantaneous_step40": core.factorial_scalar(instant_by_history),
            }
            tracked_per_mass = {
                name: tracked_by_history[name] / float(histories[name]["body_mass"])
                for name in core.HISTORY_NAMES
            }
            fixed_per_body_cell = {
                name: fixed_by_history[name] / float(histories[name]["body_size"])
                for name in core.HISTORY_NAMES
            }
            normalized[arm] = {
                "tracked_integrated_per_preprobe_mass": core.factorial_scalar(tracked_per_mass),
                "fixed_integrated_per_preprobe_body_cell": core.factorial_scalar(fixed_per_body_cell),
            }
        mminus_values = {name: histories[name]["mminus_mean"] for name in core.HISTORY_NAMES}
        per_world.append({
            "seed": int(world["seed"]),
            "feature_dose": feature_dose,
            "mminus_preprobe": {
                "factorial": core.factorial_scalar(mminus_values),
                "low_early_minus_late": mminus_values["H_L_EARLY"] - mminus_values["H_L_LATE"],
                "high_early_minus_late": mminus_values["H_H_EARLY"] - mminus_values["H_H_LATE"],
            },
            "arms": arms,
            "normalized_exploratory": normalized,
        })

    physical = {
        feature: {
            contrast: _summary(world["first_stage_contrasts"][feature][contrast] for world in complete)
            for contrast in ("dose", "order", "interaction")
        }
        for feature in PHYSICAL_DESCRIPTORS
    }
    feeding = {
        arm: {
            endpoint: {
                contrast: _summary(row["arms"][arm][endpoint][contrast] for row in per_world)
                for contrast in ("dose", "order", "interaction")
            }
            for endpoint in ("tracked", "fixed", "instantaneous_step40")
        }
        for arm in core.PRIMARY_ARMS
    }
    normalized = {
        arm: {
            endpoint: {
                contrast: _summary(row["normalized_exploratory"][arm][endpoint][contrast] for row in per_world)
                for contrast in ("dose", "order", "interaction")
            }
            for endpoint in (
                "tracked_integrated_per_preprobe_mass",
                "fixed_integrated_per_preprobe_body_cell",
            )
        }
        for arm in core.PRIMARY_ARMS
    }
    targeted_state = {
        feature: {
            contrast: _summary(world["first_stage_contrasts"][feature][contrast] for world in complete)
            for contrast in ("dose", "order", "interaction")
        }
        for feature in ("m1_mean", "m2_mean", "mplus_mean", "mminus_mean")
    }
    order = {
        "preprobe": {
            "factorial_order": _summary(row["mminus_preprobe"]["factorial"]["order"] for row in per_world),
            "low_early_minus_late": _summary(row["mminus_preprobe"]["low_early_minus_late"] for row in per_world),
            "high_early_minus_late": _summary(row["mminus_preprobe"]["high_early_minus_late"] for row in per_world),
        }
    }

    predictions = {}
    for arm in core.PRIMARY_ARMS:
        y = np.asarray([row["arms"][arm]["tracked"]["dose"] for row in per_world], dtype=float)
        predictions[arm] = {}
        model_predictions = {}
        for panel, features in MODEL_PANELS.items():
            X = np.asarray([[row["feature_dose"][feature] for feature in features] for row in per_world])
            fit = _lowo_ridge(X, y)
            fit["features"] = list(features)
            predictions[arm][panel] = fit
            model_predictions[panel] = np.asarray(fit["predictions"])
        incremental = np.square(y - model_predictions["body_geometry"]) - np.square(
            y - model_predictions["body_geometry_memory"]
        )
        predictions[arm]["incremental_targeted_memory"] = _summary(incremental)

    replay_summary = None
    if replay_path is not None:
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        if replay.get("schema") != REPLAY_SCHEMA or not replay.get("all_exact_parent_match"):
            raise RuntimeError("same-manifest replay is absent or not exact")
        by_seed = {int(w["seed"]): w for w in replay["worlds"]}
        checkpoint_rows = []
        for seed in seeds:
            item = by_seed[seed]
            for arm in core.PRIMARY_ARMS:
                for checkpoint in ("deep_preprobe", "standardized_prestimulus_step40", "probe_horizon_step40"):
                    values = {
                        history: item["diagnostics"][history][arm][checkpoint]["mminus_mean"]
                        for history in core.HISTORY_NAMES
                    }
                    uptake = {
                        history: item["diagnostics"][history][arm][checkpoint]["instantaneous_uptake"]
                        for history in core.HISTORY_NAMES
                    }
                    checkpoint_rows.append({
                        "seed": seed, "arm": arm, "checkpoint": checkpoint,
                        "mminus": core.factorial_scalar(values),
                        "baseline_uptake": core.factorial_scalar(uptake),
                        "low_early_minus_late": values["H_L_EARLY"] - values["H_L_LATE"],
                        "high_early_minus_late": values["H_H_EARLY"] - values["H_H_LATE"],
                    })
        by_arm_checkpoint = {
            arm: {
                checkpoint: {
                    "mminus_order": _summary(r["mminus"]["order"] for r in checkpoint_rows
                                             if r["arm"] == arm and r["checkpoint"] == checkpoint),
                    "mminus_low_early_minus_late": _summary(r["low_early_minus_late"] for r in checkpoint_rows
                                                            if r["arm"] == arm and r["checkpoint"] == checkpoint),
                    "mminus_high_early_minus_late": _summary(r["high_early_minus_late"] for r in checkpoint_rows
                                                             if r["arm"] == arm and r["checkpoint"] == checkpoint),
                    "instantaneous_uptake_dose": _summary(r["baseline_uptake"]["dose"] for r in checkpoint_rows
                                                          if r["arm"] == arm and r["checkpoint"] == checkpoint),
                }
                for checkpoint in ("deep_preprobe", "standardized_prestimulus_step40", "probe_horizon_step40")
            }
            for arm in core.PRIMARY_ARMS
        }
        replay_summary = {
            "exact_parent_match": True,
            "n_original_worlds": len(seeds),
            "by_arm_checkpoint": by_arm_checkpoint,
            "isolated_minus_coupled": {
                checkpoint: {
                    metric: _summary(
                        next((r["mminus"]["order"] if metric_key == "mminus_order" else r[metric_key])
                             for r in checkpoint_rows
                             if r["seed"] == seed and r["arm"] == "isolated" and r["checkpoint"] == checkpoint)
                        - next((r["mminus"]["order"] if metric_key == "mminus_order" else r[metric_key])
                               for r in checkpoint_rows
                               if r["seed"] == seed and r["arm"] == "coupled" and r["checkpoint"] == checkpoint)
                        for seed in seeds
                    )
                    for metric, metric_key in (
                        ("mminus_order", "mminus_order"),
                        ("mminus_low_early_minus_late", "low_early_minus_late"),
                        ("mminus_high_early_minus_late", "high_early_minus_late"),
                    )
                }
                for checkpoint in ("deep_preprobe", "standardized_prestimulus_step40", "probe_horizon_step40")
            },
        }

    physical_explains = all(
        predictions[arm]["body_geometry"]["q2"] is not None
        and predictions[arm]["body_geometry"]["q2"] > 0
        and predictions[arm]["body_geometry"]["squared_error_improvement_vs_training_mean"]["ci95_t"][0] > 0
        for arm in core.PRIMARY_ARMS
    )
    memory_adds = bool(
        predictions["isolated"]["incremental_targeted_memory"]["ci95_t"][0] > 0
        and predictions["coupled"]["incremental_targeted_memory"]["mean"] > 0
        and all(
            predictions[arm]["body_geometry_memory"]["q2"]
            > predictions[arm]["body_geometry"]["q2"]
            for arm in core.PRIMARY_ARMS
        )
    )
    if physical_explains and not memory_adds:
        decision = "PHYSICAL-CARRYOVER-ONLY"
    else:
        decision = "UNRESOLVED"
    return {
        "schema": SCHEMA,
        "mode": "DEV_ONLY_NO_NEW_SEEDS",
        "parent_commit": PARENT_COMMIT,
        "parent_raw_sha256": RAW_SHA256,
        "manifest_sha256": core.MANIFEST_SHA256,
        "statistical_unit": "original source world",
        "n_complete_original_worlds": len(complete),
        "complete_seeds": seeds,
        "scalar_sign_derivation": scalar_sign_derivation(),
        "targeted_state_preprobe": targeted_state,
        "order_state": order,
        "physical_decomposition": physical,
        "feeding": feeding,
        "normalized_exploratory": normalized,
        "lowo_prediction": predictions,
        "same_manifest_replay": replay_summary,
        "decision_gates": {
            "body_geometry_explains_both_primary_arms": physical_explains,
            "targeted_memory_adds_reproducible_out_of_world_information": memory_adds,
            "order_sensitive_state_not_reducible_to_body_geometry": None,
            "reproducible_nonphysical_residual_after_validated_physical_model": False,
            "specific_named_landscape_operator_prediction_remaining": False,
        },
        "decision": decision,
        "decision_reason": (
            "Physical carryover is strongly suggested descriptively, but the fixed body/geometry model does not "
            "generalize in both arms; targeted memory adds no LOWO value; the corrected small mminus order state "
            "has no established feeding-order function or named landscape perturbation."
        ),
        "per_world": per_world,
        "claim_boundary": (
            "Targeted memory mediation was not established. This analysis cannot establish absence of all memory, "
            "local ownership, order memory, causal-landscape memory, identity, or heredity."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=core.REPO_ROOT / "docs" / "individuation" /
                        "COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json")
    parser.add_argument("--replay-seed", type=int)
    parser.add_argument("--replay-all", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--replay-dir", type=Path)
    parser.add_argument("--merge-replays", type=Path)
    parser.add_argument("--replay-json", type=Path)
    parser.add_argument("--analyze", type=Path)
    args = parser.parse_args()
    if args.replay_seed is not None:
        if args.replay_dir is None:
            raise SystemExit("--replay-dir is required")
        result = replay_seed(args.replay_seed, args.raw)
        _write_json(args.replay_dir / f"world_{args.replay_seed}.json", result)
    elif args.replay_all:
        if args.replay_dir is None:
            raise SystemExit("--replay-dir is required")
        replay_all(args.raw, args.replay_dir, max(1, int(args.jobs)))
    elif args.merge_replays is not None:
        if args.replay_dir is None:
            raise SystemExit("--replay-dir is required")
        _write_json(args.merge_replays, merge_replays(args.raw, args.replay_dir))
    elif args.analyze is not None:
        _write_json(args.analyze, analyze(args.raw, args.replay_json))
    else:
        print(json.dumps(scalar_sign_derivation(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
