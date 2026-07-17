"""Pure prospective contract for ``DOWNSTREAM-ORDER-READER-01``.

This module imports no simulator or experiment runner.  It freezes numerical
error propagation, original-world aggregation, and claim classification before
any prospective seed exists.
"""
from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import beta as beta_distribution
from scipy.stats import betabinom, binom
from scipy.stats import t as student_t


RAW_SCHEMA = "DOWNSTREAM-ORDER-READER-01-RAW-v1"
MANIFEST_SCHEMA = "DOWNSTREAM-ORDER-READER-01-MANIFEST-v1"
CLASSIFIER_VERSION = "DOWNSTREAM-ORDER-READER-01-CLASSIFIER-v1"

HISTORY_NAMES = ("H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE")
SOURCE_LABELS = ("zero", "intact")
RAMP_LABELS = ("minus", "sham", "plus")

MAX_SOURCE_WORLDS = 48
MINIMUM_VALID_WORLDS = 18
CONFIDENCE_LEVEL = 0.95
SIGN_CONVERGENCE_FRACTION = 0.75

FLOAT_ATOL = 1e-12
FLOAT_RTOL = 1e-10
CLOSED_IDENTITY_RESIDUAL = 5.551115123125783e-17
LOGGER_IDENTITY_RESIDUAL = 0.0
DETERMINISTIC_REPLAY_RESIDUAL = 0.0

SCIENTIFIC_OUTCOMES = (
    "PREDICTED_ATTENUATION",
    "OPPOSITE_SIGN_FUNCTIONAL_ACCESS",
    "NO_ACCESS_ESTABLISHED",
    "EQUIVALENT_AT_DECLARED_SCALE",
    "MANIPULATION_INVALID",
    "UNRESOLVED",
)
NONSCIENTIFIC_DISPOSITIONS = ("FEASIBILITY_FAIL", "NUMERICAL_FAILURE")


def binomial_feasibility_sensitivity(
    *,
    historical_complete: int = 17,
    historical_total: int = 24,
    fixed_maximum: int = MAX_SOURCE_WORLDS,
    minimum_complete: int = MINIMUM_VALID_WORLDS,
) -> dict:
    """Outcome-free capacity analysis for complete-block yield.

    The interval is exact Clopper--Pearson.  The predictive calculation uses a
    stated uniform Beta(1,1) sensitivity prior; it is logistics evidence, not
    effect power and not a scientific outcome.
    """

    historical_complete = int(historical_complete)
    historical_total = int(historical_total)
    fixed_maximum = int(fixed_maximum)
    minimum_complete = int(minimum_complete)
    if not (0 <= historical_complete <= historical_total and historical_total > 0):
        raise ValueError("invalid historical complete-world counts")
    if not (0 < minimum_complete <= fixed_maximum):
        raise ValueError("invalid fixed family/minimum")
    alpha = 1.0 - CONFIDENCE_LEVEL
    lower = 0.0 if historical_complete == 0 else float(beta_distribution.ppf(
        alpha / 2.0,
        historical_complete,
        historical_total - historical_complete + 1,
    ))
    upper = 1.0 if historical_complete == historical_total else float(beta_distribution.ppf(
        1.0 - alpha / 2.0,
        historical_complete + 1,
        historical_total - historical_complete,
    ))
    point = historical_complete / historical_total
    posterior_alpha = historical_complete + 1
    posterior_beta = historical_total - historical_complete + 1
    return {
        "historical_complete": historical_complete,
        "historical_total": historical_total,
        "historical_rate": float(point),
        "clopper_pearson_95": [lower, upper],
        "fixed_maximum_source_worlds": fixed_maximum,
        "minimum_complete_worlds": minimum_complete,
        "probability_meeting_minimum_at_point_rate": float(
            binom.sf(minimum_complete - 1, fixed_maximum, point)
        ),
        "probability_meeting_minimum_at_cp_lower_rate": float(
            binom.sf(minimum_complete - 1, fixed_maximum, lower)
        ),
        "uniform_prior_posterior_predictive_probability": float(
            betabinom.sf(
                minimum_complete - 1,
                fixed_maximum,
                posterior_alpha,
                posterior_beta,
            )
        ),
        "posterior_predictive_complete_world_quantiles": {
            str(probability): int(betabinom.ppf(
                probability,
                fixed_maximum,
                posterior_alpha,
                posterior_beta,
            ))
            for probability in (0.025, 0.05, 0.5, 0.95, 0.975)
        },
        "effect_power_computed": False,
        "adaptive_extension_allowed": False,
    }


def _finite_float(value, label: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _gamma(operation_count: int) -> float:
    """Standard first-order floating summation factor ``n*u/(1-n*u)``."""

    if operation_count < 0:
        raise ValueError("operation_count must be non-negative")
    unit_roundoff = np.finfo(np.float64).eps / 2.0
    product = operation_count * unit_roundoff
    if product >= 1.0:
        raise ValueError("operation count is too large for a finite gamma bound")
    return float(product / (1.0 - product))


def internal_flux_sum_error_bound(
    *,
    flux_abs_sum: float,
    n_faces: int,
    j_abs: float,
    dt: float,
    mass: float,
) -> float:
    """Conservative error bound for ``J=dt/M*sum(F_x)``.

    The bound combines the repository float64 comparison rule on every logged
    face, roundoff in the face sum, and multiplication/division roundoff.  It is
    an instrument-resolution term, never a practical-effect threshold.
    """

    flux_abs_sum = _finite_float(flux_abs_sum, "flux_abs_sum")
    j_abs = _finite_float(j_abs, "j_abs")
    dt = _finite_float(dt, "dt")
    mass = _finite_float(mass, "mass")
    if flux_abs_sum < 0.0 or j_abs < 0.0 or dt <= 0.0 or mass <= 0.0:
        raise ValueError("flux magnitudes must be non-negative and dt/mass positive")
    if int(n_faces) <= 0:
        raise ValueError("n_faces must be positive")
    n_faces = int(n_faces)

    per_face_input = n_faces * FLOAT_ATOL + FLOAT_RTOL * flux_abs_sum
    sum_roundoff = _gamma(n_faces - 1) * (flux_abs_sum + per_face_input)
    propagated = abs(dt / mass) * (per_face_input + sum_roundoff)
    scale_roundoff = _gamma(2) * (j_abs + propagated)
    return float(propagated + scale_roundoff)


def linear_contrast_error_bound(
    values: Sequence[float],
    errors: Sequence[float],
    coefficients: Sequence[float],
) -> float:
    """Propagate independent absolute bounds through a fixed linear contrast."""

    if not (len(values) == len(errors) == len(coefficients)) or not values:
        raise ValueError("values, errors, and coefficients must have equal non-zero length")
    values = [_finite_float(value, "contrast value") for value in values]
    errors = [_finite_float(error, "contrast error") for error in errors]
    coefficients = [_finite_float(coef, "contrast coefficient") for coef in coefficients]
    if any(error < 0.0 for error in errors):
        raise ValueError("contrast errors must be non-negative")
    propagated = sum(abs(coef) * error for coef, error in zip(coefficients, errors))
    magnitude = sum(abs(coef * value) for coef, value in zip(coefficients, values))
    arithmetic = _gamma(2 * len(values)) * (magnitude + propagated)
    return float(propagated + arithmetic)


def arm_numerical_error(arm: Mapping) -> float:
    return internal_flux_sum_error_bound(
        flux_abs_sum=arm["flux_abs_sum"],
        n_faces=arm["n_internal_faces"],
        j_abs=abs(float(arm["J_internal_x"])),
        dt=arm["dt"],
        mass=arm["core_mass"],
    )


def recompute_history_contrasts(history: Mapping) -> dict:
    """Recompute ``D`` and ``A`` plus their numerical error bounds from raw arms."""

    d_values: dict[str, float] = {}
    d_errors: dict[str, float] = {}
    for source in SOURCE_LABELS:
        arms = history["sources"][source]["arms"]
        plus = arms["plus"]
        minus = arms["minus"]
        values = [float(plus["J_internal_x"]), float(minus["J_internal_x"])]
        errors = [arm_numerical_error(plus), arm_numerical_error(minus)]
        d_values[source] = 0.5 * (values[0] - values[1])
        d_errors[source] = linear_contrast_error_bound(values, errors, (0.5, -0.5))

    a_value = d_values["zero"] - d_values["intact"]
    a_error = linear_contrast_error_bound(
        [d_values["zero"], d_values["intact"]],
        [d_errors["zero"], d_errors["intact"]],
        (1.0, -1.0),
    )
    return {
        "D": d_values,
        "D_error_bound": d_errors,
        "A": float(a_value),
        "A_error_bound": float(a_error),
    }


def recompute_world_contrast(world: Mapping) -> dict:
    """Recompute the original-world primary contrast and numerical floor."""

    histories = {
        name: recompute_history_contrasts(world["histories"][name])
        for name in HISTORY_NAMES
    }
    a_values = [histories[name]["A"] for name in HISTORY_NAMES]
    a_errors = [histories[name]["A_error_bound"] for name in HISTORY_NAMES]
    coefficients = (0.5, -0.5, 0.5, -0.5)
    primary = float(sum(coef * value for coef, value in zip(coefficients, a_values)))
    propagated = linear_contrast_error_bound(a_values, a_errors, coefficients)
    delta_num = max(
        propagated,
        CLOSED_IDENTITY_RESIDUAL,
        LOGGER_IDENTITY_RESIDUAL,
        DETERMINISTIC_REPLAY_RESIDUAL,
    )
    zero_d = [histories[name]["D"]["zero"] for name in HISTORY_NAMES]
    zero_order = 0.5 * (zero_d[0] - zero_d[1] + zero_d[2] - zero_d[3])
    result = {
        "history_contrasts": histories,
        "delta_A_order": primary,
        "delta_num_world": float(delta_num),
        "source_zero_order_response": float(zero_order),
    }
    calibration = []
    for name in HISTORY_NAMES:
        value = world["histories"][name].get("source_calibration", {}).get("chi_source")
        if value is None:
            calibration = []
            break
        calibration.append(_finite_float(value, "source calibration"))
    if calibration:
        result["source_calibration_order"] = float(
            0.5 * (calibration[0] - calibration[1] + calibration[2] - calibration[3])
        )
    return result


def two_sided_t_summary(values: Iterable[float], confidence: float = CONFIDENCE_LEVEL) -> dict:
    values = np.asarray([_finite_float(value, "world contrast") for value in values], dtype=float)
    n = int(values.size)
    if n == 0:
        return {
            "n_worlds": 0,
            "mean": None,
            "median": None,
            "sd": None,
            "ci95_t": [None, None],
            "positive": 0,
            "negative": 0,
            "zero": 0,
            "values": [],
        }
    mean = float(values.mean())
    median = float(np.median(values))
    sd = float(values.std(ddof=1)) if n > 1 else 0.0
    if n > 1:
        critical = float(student_t.ppf(0.5 + confidence / 2.0, n - 1))
        half = critical * sd / math.sqrt(n)
        interval = [float(mean - half), float(mean + half)]
    else:
        interval = [None, None]
    return {
        "n_worlds": n,
        "mean": mean,
        "median": median,
        "sd": sd,
        "ci95_t": interval,
        "positive": int(np.sum(values > 0.0)),
        "negative": int(np.sum(values < 0.0)),
        "zero": int(np.sum(values == 0.0)),
        "values": [float(value) for value in values],
    }


def classify_worlds(
    worlds: Sequence[Mapping],
    *,
    minimum_valid_worlds: int = MINIMUM_VALID_WORLDS,
    equivalence_margin: float | None = None,
) -> dict:
    """Apply frozen run-disposition and scientific-claim logic."""

    if any(bool(world.get("numerical_failure")) for world in worlds):
        return {
            "run_disposition": "NUMERICAL_FAILURE",
            "scientific_classification": "UNRESOLVED",
            "reason": "one_or_more_worlds_failed_numerical_gates",
        }
    if any(bool(world.get("manipulation_invalid")) for world in worlds):
        return {
            "run_disposition": "MANIPULATION_INVALID",
            "scientific_classification": "MANIPULATION_INVALID",
            "reason": "one_or_more_worlds_failed_mechanical_gates",
        }

    complete = [world for world in worlds if bool(world.get("complete_block"))]
    if len(complete) < int(minimum_valid_worlds):
        return {
            "run_disposition": "FEASIBILITY_FAIL",
            "scientific_classification": "UNRESOLVED",
            "reason": "minimum_complete_original_worlds_not_met",
            "n_complete_worlds": len(complete),
            "minimum_valid_worlds": int(minimum_valid_worlds),
        }

    recomputed = [recompute_world_contrast(world) for world in complete]
    values = [row["delta_A_order"] for row in recomputed]
    summary = two_sided_t_summary(values)
    delta_num = max(row["delta_num_world"] for row in recomputed)
    lower, upper = summary["ci95_t"]
    required_signs = int(math.ceil(SIGN_CONVERGENCE_FRACTION * len(complete)))
    positive_convergent = summary["positive"] >= required_signs
    negative_convergent = summary["negative"] >= required_signs

    if equivalence_margin is not None:
        equivalence_margin = _finite_float(equivalence_margin, "equivalence_margin")
        if equivalence_margin <= delta_num:
            raise ValueError("scientific equivalence margin must exceed numerical resolution")

    if equivalence_margin is not None and lower >= -equivalence_margin and upper <= equivalence_margin:
        classification = "EQUIVALENT_AT_DECLARED_SCALE"
        reason = "two_sided_interval_within_independently_declared_scientific_margin"
    elif lower > delta_num and positive_convergent:
        classification = "PREDICTED_ATTENUATION"
        reason = "positive_two_sided_interval_beyond_numerical_floor_with_sign_convergence"
    elif upper < -delta_num and negative_convergent:
        classification = "OPPOSITE_SIGN_FUNCTIONAL_ACCESS"
        reason = "negative_two_sided_interval_beyond_numerical_floor_with_sign_convergence"
    elif lower <= delta_num and upper >= -delta_num and not (positive_convergent or negative_convergent):
        classification = "NO_ACCESS_ESTABLISHED"
        reason = "interval_includes_numerical_null_without_directional_convergence_or_equivalence"
    else:
        classification = "UNRESOLVED"
        reason = "interval_and_directional_convergence_do_not_support_a_unique_claim"

    result = {
        "run_disposition": "SCIENTIFIC_CLASSIFIED",
        "scientific_classification": classification,
        "classification_reason": reason,
        "classifier_version": CLASSIFIER_VERSION,
        "n_complete_worlds": len(complete),
        "minimum_valid_worlds": int(minimum_valid_worlds),
        "delta_num": float(delta_num),
        "numerical_null": [-float(delta_num), float(delta_num)],
        "equivalence_margin": equivalence_margin,
        "required_directional_signs": required_signs,
        "primary_summary": summary,
        "source_zero_order_secondary": two_sided_t_summary(
            row["source_zero_order_response"] for row in recomputed
        ),
    }
    if all("source_calibration_order" in row for row in recomputed):
        result["direct_source_calibration_secondary"] = two_sided_t_summary(
            row["source_calibration_order"] for row in recomputed
        )
    return result
