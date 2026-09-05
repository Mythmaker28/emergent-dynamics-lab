"""Frozen grouped inference for LCI-CAUSAL-TURNOVER-PRESEAL-03C.

The original world/seed is the only inferential unit. Models are fitted once
per outer leave-one-original-world-out fold. Uncertainty is then computed from
the fixed original-world fold losses; bootstrap resampling never refits a model
and never relabels duplicated worlds as new groups.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping

import numpy as np
from scipy.stats import t as student_t

RIDGE_LAMBDA = 1.0
BOOTSTRAP_SEED = 20260715
BOOTSTRAP_REPS = 5000


@dataclass(frozen=True)
class OuterPredictions:
    prediction: np.ndarray
    baseline_prediction: np.ndarray
    train_variance: np.ndarray
    fold_ids: np.ndarray
    audit: tuple[dict, ...]


def _as_2d(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    if X.ndim != 2:
        raise ValueError("X must be a two-dimensional matrix")
    if not np.isfinite(X).all():
        raise ValueError("X contains non-finite values")
    return X


def _ridge_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    lam: float,
) -> np.ndarray:
    """Train-only scaling and fixed-lambda ridge, using the dual when p > n."""
    mu = X_train.mean(axis=0)
    sd = X_train.std(axis=0)
    keep = sd > 1e-12
    y_mean = float(y_train.mean())
    if not np.any(keep):
        return np.full(X_test.shape[0], y_mean, dtype=float)

    A = (X_train[:, keep] - mu[keep]) / sd[keep]
    B = (X_test[:, keep] - mu[keep]) / sd[keep]
    yc = y_train - y_mean
    if A.shape[1] <= A.shape[0]:
        coef = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ yc)
        return B @ coef + y_mean

    alpha = np.linalg.solve(A @ A.T + lam * np.eye(A.shape[0]), yc)
    return B @ (A.T @ alpha) + y_mean


def outer_lowo_predictions(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    lam: float = RIDGE_LAMBDA,
) -> OuterPredictions:
    """Fit exactly once per original-world fold and persist a disjointness audit."""
    X = _as_2d(X)
    y = np.asarray(y, dtype=float)
    groups = np.asarray(groups)
    if len(X) != len(y) or len(y) != len(groups):
        raise ValueError("X, y, and groups must have equal row counts")
    if not np.isfinite(y).all():
        raise ValueError("y contains non-finite values")

    worlds = np.unique(groups)
    if len(worlds) < 3:
        raise ValueError("at least three original worlds are required")

    prediction = np.full(len(y), np.nan, dtype=float)
    baseline = np.full(len(y), np.nan, dtype=float)
    train_variance = np.full(len(y), np.nan, dtype=float)
    audit = []
    for held_out in worlds:
        test = groups == held_out
        train = ~test
        train_worlds = set(groups[train].tolist())
        test_worlds = set(groups[test].tolist())
        overlap = train_worlds & test_worlds
        if overlap:
            raise AssertionError(f"world leakage in outer fold: {sorted(overlap)}")

        prediction[test] = _ridge_predict(X[train], y[train], X[test], lam)
        baseline[test] = float(y[train].mean())
        variance = float(np.var(y[train], ddof=0))
        train_variance[test] = max(variance, 1e-15)
        audit.append(
            {
                "held_out_world": int(held_out),
                "train_worlds": sorted(int(v) for v in train_worlds),
                "test_worlds": sorted(int(v) for v in test_worlds),
                "intersection": [],
                "n_train_rows": int(train.sum()),
                "n_test_rows": int(test.sum()),
            }
        )

    if not np.isfinite(prediction).all():
        raise AssertionError("outer predictions are incomplete")
    return OuterPredictions(
        prediction=prediction,
        baseline_prediction=baseline,
        train_variance=train_variance,
        fold_ids=groups.copy(),
        audit=tuple(audit),
    )


def original_world_losses(
    y: np.ndarray,
    outer: OuterPredictions,
) -> Dict[int, dict]:
    """Return one normalized model and intercept loss per original world."""
    y = np.asarray(y, dtype=float)
    losses: Dict[int, dict] = {}
    for world in np.unique(outer.fold_ids):
        ix = outer.fold_ids == world
        scale = float(np.mean(outer.train_variance[ix]))
        model = float(np.mean((y[ix] - outer.prediction[ix]) ** 2) / scale)
        baseline = float(np.mean((y[ix] - outer.baseline_prediction[ix]) ** 2) / scale)
        losses[int(world)] = {
            "model_nmse": model,
            "intercept_nmse": baseline,
            "skill": baseline - model,
            "n_rows": int(ix.sum()),
        }
    return losses


def t_interval(scores: Iterable[float], alpha: float = 0.05) -> dict:
    values = np.asarray(list(scores), dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("at least two original-world scores are required")
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
    """Resample fixed fold scores only. This function has no model-fitting path."""
    values = np.asarray(list(scores), dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("at least two original-world scores are required")
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(reps, len(values)))
    means = values[draws].mean(axis=1)
    lo, med, hi = np.percentile(means, [2.5, 50.0, 97.5])
    return {
        "lower": float(lo),
        "median": float(med),
        "upper": float(hi),
        "reps": int(reps),
        "seed": int(seed),
        "method": "bootstrap of fixed original-world fold scores; no refitting",
    }


def evaluate_scope_models(
    matrices: Mapping[str, np.ndarray],
    own_dose: np.ndarray,
    original_world: np.ndarray,
) -> dict:
    """Evaluate every frozen scope against the same own-dose label and folds."""
    required = {"L", "N", "P", "E", "G", "B"}
    missing = required - set(matrices)
    if missing:
        raise ValueError(f"missing frozen scope matrices: {sorted(missing)}")

    own_dose = np.asarray(own_dose, dtype=float)
    original_world = np.asarray(original_world)
    models = {}
    raw_losses = {}
    common_audit = None
    for scope in ("L", "N", "P", "E", "G", "B"):
        outer = outer_lowo_predictions(matrices[scope], own_dose, original_world)
        loss_map = original_world_losses(own_dose, outer)
        worlds = sorted(loss_map)
        skills = [loss_map[w]["skill"] for w in worlds]
        models[scope] = {
            "fold_losses": {str(w): loss_map[w] for w in worlds},
            "skill_t95": t_interval(skills),
            "skill_fixed_fold_bootstrap95": fixed_fold_bootstrap(skills),
        }
        raw_losses[scope] = {w: loss_map[w]["model_nmse"] for w in worlds}
        if common_audit is None:
            common_audit = list(outer.audit)

    def contrast(name: str, reference: str, comparator: str) -> dict:
        worlds = sorted(raw_losses[reference])
        # Positive means the reference has lower held-out loss.
        scores = [raw_losses[comparator][w] - raw_losses[reference][w] for w in worlds]
        return {
            "name": name,
            "positive_means": f"{reference} has lower held-out loss than {comparator}",
            "fold_scores": {str(w): float(v) for w, v in zip(worlds, scores)},
            "t95": t_interval(scores),
            "fixed_fold_bootstrap95": fixed_fold_bootstrap(scores),
        }

    comparisons = {
        "L_over_N": contrast("target-local memory versus geometric-neighbour memory", "L", "N"),
        "L_over_E": contrast("target-local memory versus target-memory-masked environment", "L", "E"),
        "L_over_B": contrast("target-local memory versus body baseline", "L", "B"),
        "P_over_L": contrast("target-plus-neighbours versus target-local memory", "P", "L"),
        "G_over_L": contrast("complete target-centred world versus target-local memory", "G", "L"),
        "G_over_E": contrast("complete world versus the same world with target memory masked", "G", "E"),
    }

    local_gate = {
        "L_information_lower_gt_zero": models["L"]["skill_t95"]["lower"] > 0.0,
        "L_over_N_lower_gt_zero": comparisons["L_over_N"]["t95"]["lower"] > 0.0,
        "L_over_E_lower_gt_zero": comparisons["L_over_E"]["t95"]["lower"] > 0.0,
        "L_over_B_lower_gt_zero": comparisons["L_over_B"]["t95"]["lower"] > 0.0,
    }
    local_gate["pass"] = bool(all(local_gate.values()))
    return {
        "label": "own cumulative dose for every scope and comparator",
        "outer_validation": "leave one original world/seed out",
        "ridge_lambda": RIDGE_LAMBDA,
        "uncertainty_unit": "fixed original-world fold losses",
        "models": models,
        "comparisons": comparisons,
        "local_storage_gate": local_gate,
        "fold_disjointness_audit": common_audit,
    }
