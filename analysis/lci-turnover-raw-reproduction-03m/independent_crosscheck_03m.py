"""Independent frozen-raw cross-check for LCI-TURNOVER-RAW-REPRODUCTION-03M.

Raw inputs:
  results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json
  results/LCI-TURNOVER-PROSPECTIVE-03G/raw/seed_54001.json .. seed_54050.json
Frozen specification inputs:
  docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json
  docs/individuation/TURNOVER_DECISION_TREE_03G.json

This implementation intentionally does not import the canonical analyzer,
canonical statistics modules, runner, or simulation engine. It reimplements
the frozen preprocessing, leave-one-original-world-out ridge models,
fixed-fold uncertainty, within-world permutation null, causal contrasts, and
decision-tree evaluation directly from the validated JSON records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import t as student_t


RAW_SCHEMA = "LCI-TURNOVER-RAW-03G-v1"
RAW_MANIFEST_SCHEMA = "LCI-TURNOVER-RAW-MANIFEST-03G-v1"
EXPECTED_SEEDS = list(range(54001, 54051))
SCOPE_DIMS = {"L": 11, "N": 11, "P": 33, "E": 24, "Gm": 18, "Gf": 29, "B": 8}
FEASIBILITY_FIELDS = {
    "eligible",
    "deep_reached",
    "rest_assay_valid",
    "deep_assay_valid",
    "valid",
    "reason",
}
SCIENTIFIC_REQUIRED = {
    "histories",
    "target_ids",
    "g0",
    "target_centroids",
    "material_tracer",
    "tracking_event_evidence",
    "scopes",
    "causal_intervention_battery",
    "lambda_plus_only_control",
    "censoring_reason",
    "snapshot_time",
}

RIDGE_LAMBDA = 1.0
PERM_REPS = 1000
PERM_SEED = 20260715
OWN_PERM_ALPHA = 0.05
BOOTSTRAP_REPS = 5000
BOOTSTRAP_SEED = 20260715
COLLAPSE_FRACTION = 0.5

BANNED_MODULE_PREFIXES = (
    "edlab",
    "turnover_analyzer",
    "turnover_engine",
    "turnover_ledger",
    "turnover_raw_schema",
    "turnover_runner",
    "turnover_scope_features",
    "turnover_statistics",
)


class IndependentCheckError(RuntimeError):
    """Raised when frozen raw or the independent calculation is inconsistent."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def committed_bytes(repo: Path, relative_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "cat-file", "blob", f"HEAD:{relative_path}"],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _require(
        completed.returncode == 0,
        f"cannot read committed input {relative_path}: "
        f"{completed.stderr.decode('utf-8', errors='replace').strip()}",
    )
    return completed.stdout


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentCheckError(message)


def _finite_matrix(value, shape: tuple[int, int], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    _require(array.shape == shape, f"{name} shape {array.shape} != {shape}")
    _require(bool(np.isfinite(array).all()), f"{name} contains non-finite values")
    return array


def validate_record(record: dict, expected_seed: int) -> None:
    required = {
        "schema",
        "mode",
        "watermark",
        "seed",
        "world_id",
        "bindings",
        "feasibility",
        "scientific",
    }
    _require(required <= set(record), f"seed {expected_seed}: missing top-level fields")
    _require(record["schema"] == RAW_SCHEMA, f"seed {expected_seed}: wrong raw schema")
    _require(record["mode"] == "PROSPECTIVE", f"seed {expected_seed}: wrong mode")
    _require(int(record["seed"]) == expected_seed, f"seed {expected_seed}: seed mismatch")
    _require(int(record["world_id"]) == expected_seed, f"seed {expected_seed}: world mismatch")
    _require(
        set(record["feasibility"]) == FEASIBILITY_FIELDS,
        f"seed {expected_seed}: feasibility fields are not the frozen exact set",
    )
    for field in FEASIBILITY_FIELDS - {"reason"}:
        _require(
            isinstance(record["feasibility"][field], bool),
            f"seed {expected_seed}: feasibility {field} is not Boolean",
        )
    reason = record["feasibility"]["reason"]
    _require(reason is None or isinstance(reason, str), f"seed {expected_seed}: invalid reason")
    bindings = record["bindings"]
    for field in (
        "seal_sha256",
        "execution_manifest_sha256",
        "execution_manifest_git_blob",
        "environment_lock_sha256",
        "code_git_blobs",
        "code_sha256",
    ):
        _require(field in bindings, f"seed {expected_seed}: binding {field} absent")
    science = record["scientific"]
    _require(
        SCIENTIFIC_REQUIRED <= set(science),
        f"seed {expected_seed}: scientific payload fields absent",
    )
    if record["feasibility"]["valid"]:
        _require(science["scopes"] is not None, f"seed {expected_seed}: valid scope absent")
        _require(
            science["causal_intervention_battery"]["deep"] is not None,
            f"seed {expected_seed}: valid deep battery absent",
        )
        _require(len(science["histories"]["own_dose"]) == 3, "own-dose labels must have 3 rows")
        values = science["scopes"]["values"]
        for scope, dimension in SCOPE_DIMS.items():
            _finite_matrix(values[scope], (3, dimension), f"seed {expected_seed} scope {scope}")
        gf = np.asarray(values["Gf"], dtype=np.float64)
        local = np.asarray(values["L"], dtype=np.float64)
        _require(
            bool(np.array_equal(gf[:, :11], local)),
            f"seed {expected_seed}: Gf does not contain exact L slice",
        )


def load_validated_raw(repo: Path) -> tuple[dict, list[dict], dict]:
    run_dir = (repo / "results" / "LCI-TURNOVER-PROSPECTIVE-03G").resolve()
    manifest_path = run_dir / "raw_manifest_03g.json"
    manifest_rel = str(manifest_path.relative_to(repo)).replace("\\", "/")
    manifest_bytes = committed_bytes(repo, manifest_rel)
    manifest = json.loads(manifest_bytes)
    _require(manifest.get("schema") == RAW_MANIFEST_SCHEMA, "wrong raw-manifest schema")
    _require(manifest.get("raw_schema") == RAW_SCHEMA, "wrong manifest raw schema")
    entries = manifest.get("entries")
    _require(isinstance(entries, list), "raw-manifest entries are not a list")
    seeds = [int(entry["seed"]) for entry in entries]
    _require(seeds == EXPECTED_SEEDS, f"raw seeds/order mismatch: {seeds}")
    _require(len(seeds) == len(set(seeds)), "duplicate raw seed")
    _require(manifest.get("n_records") == 50, "raw-manifest count is not 50")
    records: list[dict] = []
    digest_rows = []
    for entry in entries:
        seed = int(entry["seed"])
        path = (run_dir / entry["path"]).resolve()
        _require(run_dir in path.parents, f"seed {seed}: raw path escapes run directory")
        path_rel = str(path.relative_to(repo)).replace("\\", "/")
        raw_bytes = committed_bytes(repo, path_rel)
        digest = sha256_bytes(raw_bytes)
        _require(digest == entry["sha256"], f"seed {seed}: raw SHA-256 mismatch")
        record = json.loads(raw_bytes)
        validate_record(record, seed)
        _require(
            bool(record["feasibility"]["valid"]) == bool(entry["valid"]),
            f"seed {seed}: manifest validity mismatch",
        )
        records.append(record)
        digest_rows.append({"seed": seed, "path": entry["path"], "sha256": digest})
    n_valid = sum(bool(record["feasibility"]["valid"]) for record in records)
    _require(n_valid == manifest.get("n_valid_worlds") == 21, "valid-world count mismatch")
    audit = {
        "raw_manifest_path": str(manifest_path.relative_to(repo)).replace("\\", "/"),
        "raw_manifest_sha256": sha256_bytes(manifest_bytes),
        "byte_source": "exact committed Git blobs (working-tree EOL conversion bypassed)",
        "raw_record_count": len(records),
        "raw_record_sha256": digest_rows,
        "seeds_exact_ascending": True,
        "duplicate_seed_count": 0,
        "reserve_seed_count": 0,
    }
    return manifest, records, audit


def _world_signature(rows: np.ndarray) -> str:
    rows = np.asarray(rows, dtype=np.float64)
    order = np.lexsort(tuple(rows[:, index] for index in reversed(range(rows.shape[1]))))
    return hashlib.sha256(np.ascontiguousarray(rows[order]).tobytes()).hexdigest()


def build_matrices(records: Sequence[dict]) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    valid = [record for record in records if record["feasibility"]["valid"]]
    matrices = {scope: [] for scope in SCOPE_DIMS}
    labels: list[float] = []
    groups: list[int] = []
    for record in valid:
        values = record["scientific"]["scopes"]["values"]
        dose = record["scientific"]["histories"]["own_dose"]
        for target in range(3):
            for scope in matrices:
                matrices[scope].append(values[scope][target])
            labels.append(float(dose[target]))
            groups.append(int(record["world_id"]))
    arrays = {scope: np.asarray(rows, dtype=np.float64) for scope, rows in matrices.items()}
    y = np.asarray(labels, dtype=np.float64)
    original_world = np.asarray(groups, dtype=np.int64)
    _require(len(np.unique(original_world)) == len(valid), "duplicate valid original-world ID")
    seen: dict[str, int] = {}
    for world in np.unique(original_world):
        signature = _world_signature(arrays["L"][original_world == world])
        _require(signature not in seen, f"duplicate world content: {seen.get(signature)} and {world}")
        seen[signature] = int(world)
    return arrays, y, original_world


def _ridge_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    ridge_lambda: float,
) -> np.ndarray:
    mu = x_train.mean(axis=0)
    sd = x_train.std(axis=0)
    keep = sd > 1e-12
    y_mean = float(y_train.mean())
    if not np.any(keep):
        return np.full(x_test.shape[0], y_mean, dtype=float)
    train_scaled = (x_train[:, keep] - mu[keep]) / sd[keep]
    test_scaled = (x_test[:, keep] - mu[keep]) / sd[keep]
    centered = y_train - y_mean
    if train_scaled.shape[1] <= train_scaled.shape[0]:
        coef = np.linalg.solve(
            train_scaled.T @ train_scaled
            + ridge_lambda * np.eye(train_scaled.shape[1]),
            train_scaled.T @ centered,
        )
        return test_scaled @ coef + y_mean
    alpha = np.linalg.solve(
        train_scaled @ train_scaled.T + ridge_lambda * np.eye(train_scaled.shape[0]),
        centered,
    )
    return test_scaled @ (train_scaled.T @ alpha) + y_mean


def outer_lowo_predictions(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    ridge_lambda: float = RIDGE_LAMBDA,
) -> dict:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    groups = np.asarray(groups)
    _require(x.ndim == 2 and len(x) == len(y) == len(groups), "LOWO input shape mismatch")
    _require(bool(np.isfinite(x).all() and np.isfinite(y).all()), "LOWO non-finite input")
    worlds = np.unique(groups)
    _require(len(worlds) >= 3, "LOWO requires at least three worlds")
    prediction = np.full(len(y), np.nan, dtype=np.float64)
    baseline = np.full(len(y), np.nan, dtype=np.float64)
    train_variance = np.full(len(y), np.nan, dtype=np.float64)
    audit = []
    for held_out in worlds:
        test = groups == held_out
        train = ~test
        train_worlds = set(groups[train].tolist())
        test_worlds = set(groups[test].tolist())
        _require(not (train_worlds & test_worlds), "world leakage in LOWO fold")
        prediction[test] = _ridge_predict(x[train], y[train], x[test], ridge_lambda)
        baseline[test] = float(y[train].mean())
        train_variance[test] = max(float(np.var(y[train], ddof=0)), 1e-15)
        audit.append(
            {
                "held_out_world": int(held_out),
                "train_worlds": sorted(int(value) for value in train_worlds),
                "test_worlds": sorted(int(value) for value in test_worlds),
                "intersection": [],
                "n_train_rows": int(train.sum()),
                "n_test_rows": int(test.sum()),
            }
        )
    _require(bool(np.isfinite(prediction).all()), "LOWO predictions incomplete")
    return {
        "prediction": prediction,
        "baseline_prediction": baseline,
        "train_variance": train_variance,
        "fold_ids": groups.copy(),
        "audit": audit,
    }


def original_world_losses(y: np.ndarray, outer: dict) -> dict[int, dict]:
    losses: dict[int, dict] = {}
    for world in np.unique(outer["fold_ids"]):
        index = outer["fold_ids"] == world
        scale = float(np.mean(outer["train_variance"][index]))
        model = float(np.mean((y[index] - outer["prediction"][index]) ** 2) / scale)
        baseline = float(
            np.mean((y[index] - outer["baseline_prediction"][index]) ** 2) / scale
        )
        losses[int(world)] = {
            "model_nmse": model,
            "intercept_nmse": baseline,
            "skill": baseline - model,
            "n_rows": int(index.sum()),
        }
    return losses


def t_interval(scores: Iterable[float], alpha: float = 0.05) -> dict:
    values = np.asarray(list(scores), dtype=np.float64)
    _require(values.ndim == 1 and len(values) >= 2, "t interval needs at least two worlds")
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(len(values)))
    critical = float(student_t.ppf(1.0 - alpha / 2.0, df=len(values) - 1))
    return {
        "mean": mean,
        "lower": mean - critical * se,
        "upper": mean + critical * se,
        "n_original_worlds": int(len(values)),
        "method": "Student-t interval over fixed original-world fold scores",
    }


def fixed_fold_bootstrap(
    scores: Iterable[float],
    reps: int = BOOTSTRAP_REPS,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    values = np.asarray(list(scores), dtype=np.float64)
    _require(values.ndim == 1 and len(values) >= 2, "bootstrap needs at least two worlds")
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(reps, len(values)))
    means = values[draws].mean(axis=1)
    lower, median, upper = np.percentile(means, [2.5, 50.0, 97.5])
    return {
        "lower": float(lower),
        "median": float(median),
        "upper": float(upper),
        "reps": int(reps),
        "seed": int(seed),
        "method": "bootstrap of fixed original-world fold scores; no refitting",
    }


def scope_result(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> tuple[dict, dict[int, dict]]:
    outer = outer_lowo_predictions(x, y, groups, RIDGE_LAMBDA)
    losses = original_world_losses(y, outer)
    worlds = sorted(losses)
    skills = [losses[world]["skill"] for world in worlds]
    result = {
        "ridge_lambda": RIDGE_LAMBDA,
        "fold_losses": {str(world): losses[world] for world in worlds},
        "skill_t95": t_interval(skills),
        "skill_fixed_fold_bootstrap95": fixed_fold_bootstrap(skills),
        "fold_disjointness_audit": list(outer["audit"]),
        "predictions": [
            {
                "row": int(index),
                "original_world": int(groups[index]),
                "observed": float(y[index]),
                "prediction": float(outer["prediction"][index]),
                "baseline_prediction": float(outer["baseline_prediction"][index]),
            }
            for index in range(len(y))
        ],
    }
    return result, losses


def within_world_permutation(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    reps: int = PERM_REPS,
    seed: int = PERM_SEED,
) -> dict:
    observed_result, observed_losses = scope_result(x, y, groups)
    observed = float(np.mean([row["skill"] for row in observed_losses.values()]))
    rng = np.random.default_rng(seed)
    indices = {group: np.where(groups == group)[0] for group in np.unique(groups)}
    null = np.empty(reps, dtype=np.float64)
    for rep in range(reps):
        permuted = y.copy()
        for group, rows in indices.items():
            permuted[rows] = y[rows][rng.permutation(len(rows))]
        outer = outer_lowo_predictions(x, permuted, groups, RIDGE_LAMBDA)
        losses = original_world_losses(permuted, outer)
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
    permutation_reps: int,
) -> dict:
    models: dict[str, dict] = {}
    losses: dict[str, dict[int, dict]] = {}
    for scope in ("L", "N", "P", "E", "Gm", "Gf", "B"):
        models[scope], losses[scope] = scope_result(
            np.asarray(matrices[scope], dtype=np.float64), own_dose, original_world
        )

    def contrast(comparator: str) -> dict:
        worlds = sorted(losses["L"])
        scores = [
            losses[comparator][world]["model_nmse"] - losses["L"][world]["model_nmse"]
            for world in worlds
        ]
        return {
            "positive_means": f"L has lower held-out loss than {comparator}",
            "fold_scores": {
                str(world): float(score) for world, score in zip(worlds, scores)
            },
            "t95": t_interval(scores),
            "fixed_fold_bootstrap95": fixed_fold_bootstrap(scores),
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
        own_dose,
        original_world,
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
    own: list[float] = []
    own_minus_sham: list[float] = []
    own_minus_neighbour: list[float] = []
    own_fixed: list[float] = []
    own_lambda_plus: list[float] = []
    for battery in deep_batteries:
        intact = battery["intact"]
        sham = battery["sham"]
        erase = battery["erase"]
        ablate_plus = battery["ablate_plus"]
        erase_ablate_plus = battery["erase_ablate_plus"]
        target_count = len(intact["tracked"])
        own_world = []
        sham_world = []
        neighbour_world = []
        fixed_world = []
        plus_world = []
        for target in range(target_count):
            own_effect = intact["tracked"][target] - erase[target]["tracked"][target]
            sham_effect = intact["tracked"][target] - sham["tracked"][target]
            neighbour_effects = [
                intact["tracked"][target] - erase[other]["tracked"][target]
                for other in range(target_count)
                if other != target
            ]
            own_world.append(own_effect)
            sham_world.append(own_effect - sham_effect)
            neighbour_world.append(own_effect - float(np.mean(neighbour_effects)))
            fixed_world.append(intact["fixed"][target] - erase[target]["fixed"][target])
            plus_world.append(
                ablate_plus["tracked"][target]
                - erase_ablate_plus[target]["tracked"][target]
            )
        own.append(float(np.mean(own_world)))
        own_minus_sham.append(float(np.mean(sham_world)))
        own_minus_neighbour.append(float(np.mean(neighbour_world)))
        own_fixed.append(float(np.mean(fixed_world)))
        own_lambda_plus.append(float(np.mean(plus_world)))
    own_ci = t_interval(own)
    sham_ci = t_interval(own_minus_sham)
    neighbour_ci = t_interval(own_minus_neighbour)
    fixed_ci = t_interval(own_fixed)
    plus_ci = t_interval(own_lambda_plus)
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


def eval_expression(expression, gates: Mapping[str, bool]) -> bool:
    if isinstance(expression, str):
        _require(expression in gates, f"unknown gate in tree: {expression}")
        return bool(gates[expression])
    _require(isinstance(expression, dict) and len(expression) == 1, "invalid tree expression")
    operator, value = next(iter(expression.items()))
    if operator == "not":
        return not eval_expression(value, gates)
    if operator == "all":
        return all(eval_expression(item, gates) for item in value)
    if operator == "any":
        return any(eval_expression(item, gates) for item in value)
    raise IndependentCheckError(f"unsupported tree operator: {operator}")


def select_outcome(tree: dict, gates: Mapping[str, bool]) -> tuple[str, dict]:
    matched = [
        code
        for code, definition in tree["outcomes"].items()
        if eval_expression(definition["expression"], gates)
    ]
    _require(len(matched) == 1, f"decision tree does not select uniquely: {matched}")
    return matched[0], tree["outcomes"][matched[0]]


def _assert_no_banned_imports() -> list[str]:
    found = sorted(
        name
        for name in sys.modules
        if any(name == prefix or name.startswith(prefix + ".") for prefix in BANNED_MODULE_PREFIXES)
    )
    _require(not found, f"banned canonical/simulation modules imported: {found}")
    return found


def run(repo: Path) -> dict:
    repo = repo.resolve()
    execution_manifest_path = repo / "docs" / "individuation" / "TURNOVER_EXECUTION_MANIFEST_03G.json"
    decision_tree_path = repo / "docs" / "individuation" / "TURNOVER_DECISION_TREE_03G.json"
    execution_manifest_rel = str(execution_manifest_path.relative_to(repo)).replace("\\", "/")
    decision_tree_rel = str(decision_tree_path.relative_to(repo)).replace("\\", "/")
    execution_manifest_bytes = committed_bytes(repo, execution_manifest_rel)
    decision_tree_bytes = committed_bytes(repo, decision_tree_rel)
    execution_manifest = json.loads(execution_manifest_bytes)
    decision_tree = json.loads(decision_tree_bytes)
    raw_manifest, records, raw_audit = load_validated_raw(repo)
    matrices, own_dose, original_world = build_matrices(records)
    permutation_reps = int(execution_manifest["analysis"]["permutation_reps"])
    minimum = int(execution_manifest["seed_plan"]["minimum_valid_worlds"])
    _require(permutation_reps == PERM_REPS, "frozen permutation count changed")
    _require(float(execution_manifest["analysis"]["ridge_lambda"]) == RIDGE_LAMBDA, "ridge changed")
    ownership = evaluate_ownership(
        matrices,
        own_dose,
        original_world,
        permutation_reps=permutation_reps,
    )
    deep_batteries = [
        record["scientific"]["causal_intervention_battery"]["deep"]
        for record in records
        if record["feasibility"]["valid"]
    ]
    causal = causal_expression_gate(deep_batteries, minimum)
    primary = primary_gate(ownership, causal)
    gates = {
        "FEASIBILITY": len(deep_batteries) >= minimum,
        "G_OWN_PERM": bool(ownership["G_OWN_PERM"]["pass"]),
        "G_LOCAL_EXCLUSION": bool(ownership["G_LOCAL_EXCLUSION"]["pass"]),
        "G_CAUSAL": bool(causal["pass"]),
        "DISTRIBUTED_ENV": bool(ownership["DISTRIBUTED_ENV"]["pass"]),
    }
    outcome, definition = select_outcome(decision_tree, gates)
    banned = _assert_no_banned_imports()
    return {
        "schema": "LCI-TURNOVER-INDEPENDENT-CROSSCHECK-03M-v1",
        "method": "independent reimplementation from validated raw JSON and frozen specification",
        "inputs": {
            "raw_manifest": raw_audit,
            "execution_manifest": {
                "path": str(execution_manifest_path.relative_to(repo)).replace("\\", "/"),
                "sha256": sha256_bytes(execution_manifest_bytes),
            },
            "decision_tree": {
                "path": str(decision_tree_path.relative_to(repo)).replace("\\", "/"),
                "sha256": sha256_bytes(decision_tree_bytes),
            },
        },
        "frozen_parameters": {
            "ridge_lambda": RIDGE_LAMBDA,
            "permutation_reps": PERM_REPS,
            "permutation_seed": PERM_SEED,
            "permutation_alpha": OWN_PERM_ALPHA,
            "bootstrap_reps": BOOTSTRAP_REPS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "causal_collapse_fraction": COLLAPSE_FRACTION,
            "minimum_valid_worlds": minimum,
        },
        "n_raw_worlds": len(records),
        "n_valid_worlds": len(deep_batteries),
        "ownership": ownership,
        "causal": causal,
        "primary": primary,
        "gates": gates,
        "outcome": outcome,
        "outcome_name": definition["name"],
        "authorized_wording": definition["authorized_wording"],
        "engine_imported": False,
        "banned_imports": banned,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = run(args.repo)
    text = json.dumps(
        result,
        sort_keys=True,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
        allow_nan=False,
    ) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
