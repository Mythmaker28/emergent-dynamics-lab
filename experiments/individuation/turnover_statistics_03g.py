"""Frozen grouped ownership, distributed-access, and causal inference for turnover 03G."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load("_turnover_statistics_base_03g", "turnover_statistics.py")

RIDGE_LAMBDA = 1.0
PERM_REPS = 1000
PERM_SEED = 20260715
OWN_PERM_ALPHA = 0.05
COLLAPSE_FRACTION = 0.5


def _world_signature(rows: np.ndarray) -> str:
    rows = np.asarray(rows, dtype=np.float64)
    order = np.lexsort(tuple(rows[:, index] for index in reversed(range(rows.shape[1]))))
    return hashlib.sha256(np.ascontiguousarray(rows[order]).tobytes()).hexdigest()


def assert_no_duplicate_worlds(matrices: Mapping[str, np.ndarray], groups: np.ndarray) -> None:
    groups = np.asarray(groups)
    local = np.asarray(matrices["L"], dtype=np.float64)
    seen: dict[str, int] = {}
    for group in np.unique(groups):
        signature = _world_signature(local[groups == group])
        if signature in seen and seen[signature] != int(group):
            raise ValueError(
                f"duplicate original world content under ids {seen[signature]} and {int(group)}"
            )
        seen[signature] = int(group)


def _scope_result(X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> tuple[dict, dict[int, dict]]:
    outer = base.outer_lowo_predictions(X, y, groups, lam=RIDGE_LAMBDA)
    losses = base.original_world_losses(y, outer)
    worlds = sorted(losses)
    skills = [losses[world]["skill"] for world in worlds]
    return (
        {
            "ridge_lambda": RIDGE_LAMBDA,
            "fold_losses": {str(world): losses[world] for world in worlds},
            "skill_t95": base.t_interval(skills),
            "skill_fixed_fold_bootstrap95": base.fixed_fold_bootstrap(skills),
            "fold_disjointness_audit": list(outer.audit),
            "predictions": [
                {
                    "row": int(index),
                    "original_world": int(groups[index]),
                    "observed": float(y[index]),
                    "prediction": float(outer.prediction[index]),
                    "baseline_prediction": float(outer.baseline_prediction[index]),
                }
                for index in range(len(y))
            ],
        },
        losses,
    )


def within_world_permutation(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    *,
    reps: int = PERM_REPS,
    seed: int = PERM_SEED,
) -> dict:
    observed_result, observed_losses = _scope_result(X, y, groups)
    observed = float(np.mean([row["skill"] for row in observed_losses.values()]))
    rng = np.random.default_rng(seed)
    indices = {group: np.where(groups == group)[0] for group in np.unique(groups)}
    null = np.empty(reps, dtype=np.float64)
    for rep in range(reps):
        permuted = y.copy()
        for group, rows in indices.items():
            permuted[rows] = y[rows][rng.permutation(len(rows))]
        outer = base.outer_lowo_predictions(X, permuted, groups, lam=RIDGE_LAMBDA)
        losses = base.original_world_losses(permuted, outer)
        null[rep] = np.mean([row["skill"] for row in losses.values()])
    p_value = float((np.sum(null >= observed) + 1) / (reps + 1))
    return {
        "observed_mean_skill": observed,
        "null_p95": float(np.percentile(null, 95)),
        "p_value": p_value,
        "reps": int(reps),
        "seed": int(seed),
        "alpha": OWN_PERM_ALPHA,
        "pass": bool(p_value < OWN_PERM_ALPHA),
        "coordinate": "own cumulative dose / m-plus",
        "method": "within-original-world label permutation with unchanged LOWO folds",
        "observed_scope_result": observed_result,
    }


def evaluate_ownership(
    matrices: Mapping[str, np.ndarray],
    own_dose: np.ndarray,
    original_world: np.ndarray,
    *,
    permutation_reps: int = PERM_REPS,
) -> dict:
    required = {"L", "N", "P", "E", "Gm", "Gf", "B"}
    missing = required - set(matrices)
    if missing:
        raise ValueError(f"missing scope matrices: {sorted(missing)}")
    y = np.asarray(own_dose, dtype=np.float64)
    groups = np.asarray(original_world)
    if len(np.unique(groups)) < 3:
        raise ValueError("at least three original worlds are required for grouped inference")
    assert_no_duplicate_worlds(matrices, groups)
    models: dict[str, dict] = {}
    losses: dict[str, dict[int, dict]] = {}
    for scope in ("L", "N", "P", "E", "Gm", "Gf", "B"):
        models[scope], losses[scope] = _scope_result(
            np.asarray(matrices[scope], dtype=np.float64), y, groups
        )

    def contrast(comparator: str) -> dict:
        worlds = sorted(losses["L"])
        scores = [
            losses[comparator][world]["model_nmse"] - losses["L"][world]["model_nmse"]
            for world in worlds
        ]
        return {
            "positive_means": f"L has lower held-out loss than {comparator}",
            "fold_scores": {str(world): float(score) for world, score in zip(worlds, scores)},
            "t95": base.t_interval(scores),
            "fixed_fold_bootstrap95": base.fixed_fold_bootstrap(scores),
        }

    comparisons = {scope: contrast(scope) for scope in ("N", "E", "Gm", "B")}
    local = {
        "L_information_lower_gt_zero": models["L"]["skill_t95"]["lower"] > 0.0,
        "L_over_N": comparisons["N"]["t95"]["lower"] > 0.0,
        "L_over_E": comparisons["E"]["t95"]["lower"] > 0.0,
        "L_over_Gm": comparisons["Gm"]["t95"]["lower"] > 0.0,
        "L_over_B": comparisons["B"]["t95"]["lower"] > 0.0,
    }
    local["pass"] = bool(all(local.values()))
    distributed_sources = {
        scope: bool(
            models[scope]["skill_t95"]["lower"] > 0.0
            and comparisons[scope]["t95"]["lower"] <= 0.0
        )
        for scope in ("E", "Gm")
    }
    permutation = within_world_permutation(
        np.asarray(matrices["L"], dtype=np.float64),
        y,
        groups,
        reps=permutation_reps,
        seed=PERM_SEED,
    )
    return {
        "unit": "original world",
        "label": "target own cumulative dose / m-plus",
        "models": models,
        "G_OWN_PERM": permutation,
        "G_LOCAL_EXCLUSION": {**local, "comparisons": comparisons},
        "DISTRIBUTED_ENV": {
            "sources": distributed_sources,
            "pass": bool(any(distributed_sources.values())),
            "rule": "E or Gm has positive held-out skill and L does not strictly beat that scope",
        },
        "diagnostics_non_gating": {
            "P": models["P"],
            "Gf": models["Gf"],
            "Gf_never_used_as_exclusion_control": True,
        },
    }


def causal_expression_gate(deep_batteries: Sequence[dict], minimum_valid_worlds: int) -> dict:
    own = []
    own_minus_sham = []
    own_minus_neighbour = []
    own_fixed = []
    own_lambda_plus = []
    for battery in deep_batteries:
        intact = battery["intact"]
        sham = battery["sham"]
        erase = battery["erase"]
        ablate_plus = battery["ablate_plus"]
        erase_ablate_plus = battery["erase_ablate_plus"]
        k = len(intact["tracked"])
        own_world = []
        sham_world = []
        neighbour_world = []
        fixed_world = []
        plus_world = []
        for target in range(k):
            own_effect = intact["tracked"][target] - erase[target]["tracked"][target]
            sham_effect = intact["tracked"][target] - sham["tracked"][target]
            neighbour_effects = [
                intact["tracked"][target] - erase[other]["tracked"][target]
                for other in range(k)
                if other != target
            ]
            own_world.append(own_effect)
            sham_world.append(own_effect - sham_effect)
            neighbour_world.append(own_effect - float(np.mean(neighbour_effects)))
            fixed_world.append(
                intact["fixed"][target] - erase[target]["fixed"][target]
            )
            plus_world.append(
                ablate_plus["tracked"][target]
                - erase_ablate_plus[target]["tracked"][target]
            )
        own.append(float(np.mean(own_world)))
        own_minus_sham.append(float(np.mean(sham_world)))
        own_minus_neighbour.append(float(np.mean(neighbour_world)))
        own_fixed.append(float(np.mean(fixed_world)))
        own_lambda_plus.append(float(np.mean(plus_world)))
    if len(own) < 2:
        raise ValueError("at least two valid worlds are required for causal intervals")
    own_ci = base.t_interval(own)
    sham_ci = base.t_interval(own_minus_sham)
    neighbour_ci = base.t_interval(own_minus_neighbour)
    fixed_ci = base.t_interval(own_fixed)
    plus_ci = base.t_interval(own_lambda_plus)
    collapse = bool(
        own_ci["mean"] > 0.0
        and plus_ci["upper"] < COLLAPSE_FRACTION * own_ci["mean"]
    )
    result = {
        "n_valid_worlds": len(own),
        "minimum_valid_worlds": int(minimum_valid_worlds),
        "own_t95": own_ci,
        "own_minus_sham_t95": sham_ci,
        "own_minus_neighbour_t95": neighbour_ci,
        "own_fixed_t95": fixed_ci,
        "own_under_lambda_plus_only_ablation_t95": plus_ci,
        "lambda_plus": 0.0,
        "lambda_minus_preserved": 0.15,
        "collapse_fraction": COLLAPSE_FRACTION,
        "own_positive": own_ci["lower"] > 0.0,
        "own_gt_sham": sham_ci["lower"] > 0.0,
        "own_gt_neighbour": neighbour_ci["lower"] > 0.0,
        "lambda_plus_only_collapse": collapse,
        "fixed_mask_direction_consistent": fixed_ci["mean"] > 0.0,
        "enough_worlds": len(own) >= minimum_valid_worlds,
    }
    result["pass"] = bool(
        result["own_positive"]
        and result["own_gt_sham"]
        and result["own_gt_neighbour"]
        and result["lambda_plus_only_collapse"]
        and result["fixed_mask_direction_consistent"]
        and result["enough_worlds"]
    )
    return result


def primary_gate(ownership: dict, causal: dict) -> dict:
    values = {
        "G_OWN_PERM": bool(ownership["G_OWN_PERM"]["pass"]),
        "G_LOCAL_EXCLUSION": bool(ownership["G_LOCAL_EXCLUSION"]["pass"]),
        "G_CAUSAL": bool(causal["pass"]),
    }
    return {
        **values,
        "pass": bool(all(values.values())),
        "rule": "G_OWN_PERM AND G_LOCAL_EXCLUSION AND G_CAUSAL",
        "feeding_effect_alone_is_insufficient": True,
    }
