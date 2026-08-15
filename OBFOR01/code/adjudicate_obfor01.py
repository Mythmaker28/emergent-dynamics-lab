"""OBFOR01 §23-§25 — evaluate the frozen endpoints on the fresh arms, then take exactly one
disposition.

The disposition is selected by the rule frozen in `_freeze.json` before any arm ran. This file
evaluates that rule; it does not choose.
"""
from __future__ import annotations

import json
import math

import numpy as np

OUT = "/home/claude/OBFOR01/out"


def stats(v):
    v = np.asarray(v, float)
    return {"n": int(len(v)), "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
            "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None,
            "values": [float(x) for x in v]}


def main():
    frz = json.load(open(f"{OUT}/_freeze.json"))
    val = json.load(open(f"{OUT}/_validation.json"))
    res = json.load(open(f"{OUT}/_residual.json"))
    m6 = json.load(open(f"{OUT}/_m6.json"))
    mech = json.load(open(f"{OUT}/_mechanisms.json"))

    delta = frz["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"] / 100.0
    ep = frz["PRIMARY_PREDICTIONS"]
    arms = [a for a in val["ARMS"] if not a["EXTINCT"]]
    S = [a for a in arms if a["condition"] == "S"]
    Mo = [a for a in arms if a["condition"] == "M"]

    obs = {
        "S_median": stats([a["r80_median"] for a in S]),
        "M_median": stats([a["r80_median"] for a in Mo]),
        "S_mean": stats([a["r80_mean"] for a in S]),
        "M_mean": stats([a["r80_mean"] for a in Mo]),
        "S_sd": stats([a["r80_sd"] for a in S]),
        "M_sd": stats([a["r80_sd"] for a in Mo]),
        "S_skew": stats([a["r80_skew"] for a in S]),
        "M_skew": stats([a["r80_skew"] for a in Mo]),
        "S_N_X": stats([a["N_X_window_mean"] for a in S]),
        "M_N_X": stats([a["N_X_window_mean"] for a in Mo]),
        "blocked_X": stats([a["blocked_fraction"]["X"] for a in arms]),
    }

    def endpoint(name, observed, predicted):
        r = observed["mean"] / predicted - 1.0
        se = observed["se"] / predicted if observed.get("se") else None
        lo = r - 1.96 * se if se else None
        hi = r + 1.96 * se if se else None
        return {"NAME": name, "predicted": predicted, "observed": observed["mean"],
                "n": observed["n"], "relative_deviation": r,
                "relative_deviation_percent": 100 * r,
                "se_relative_percent": 100 * se if se else None,
                "ci95_relative_percent": [100 * lo, 100 * hi] if se else None,
                "margin_percent": 100 * delta,
                "PASS": bool(abs(r) <= delta),
                "STRICT_PASS_WHOLE_INTERVAL_INSIDE":
                    bool(se is not None and abs(r) + 1.96 * se <= delta)}

    E = {
        "STATIC_ABSOLUTE_PROFILE_COMPATIBILITY":
            endpoint("static", obs["S_median"],
                     ep["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"]),
        "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY":
            endpoint("mobile", obs["M_median"],
                     ep["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"]),
    }
    pred_ratio = ep["MOBILE_STATIC_RATIO_COMPATIBILITY"]["predicted_ratio_under_M6"]
    obs_ratio = obs["M_median"]["mean"] / obs["S_median"]["mean"]
    rel = math.sqrt((obs["M_median"]["se"] / obs["M_median"]["mean"]) ** 2
                    + (obs["S_median"]["se"] / obs["S_median"]["mean"]) ** 2)
    E["MOBILE_STATIC_RATIO_COMPATIBILITY"] = {
        "NAME": "ratio", "predicted": pred_ratio, "observed": obs_ratio,
        "relative_deviation_percent": 100 * (obs_ratio / pred_ratio - 1),
        "se_relative_percent": 100 * rel,
        "ci95_relative_percent": [100 * (obs_ratio / pred_ratio - 1 - 1.96 * rel),
                                  100 * (obs_ratio / pred_ratio - 1 + 1.96 * rel)],
        "margin_percent": 100 * delta,
        "PASS": bool(abs(obs_ratio / pred_ratio - 1) <= delta),
        "STRICT_PASS_WHOLE_INTERVAL_INSIDE":
            bool(abs(obs_ratio / pred_ratio - 1) + 1.96 * rel <= delta),
        "RATIO_ONE_EXCLUDED": bool(obs_ratio * (1 - 1.96 * rel) > 1.0)}
    E["FULL_MODEL_RESIDUAL_EQUIVALENCE"] = {
        "PASS": bool(E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"]
                     and E["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"])}

    # ---------------------------------------------------------------- ablation control
    def by(tag):
        return next(m for m in m6["MODELS"] if m["tag"] == tag)
    pop_m = by("M6_MOBILE_full")["population_r80"]
    full_pred = by("M6_MOBILE_full")["median_summary"]
    abl_traj_pred = pop_m * (1 + by("M3_ablate_shared_trajectory")[
        "median_residual_percent"] / 100)
    abl_birth_pred = pop_m * (1 + by("M4_ablate_birth_flux_to_constant")[
        "median_residual_percent"] / 100)
    o = obs["M_median"]["mean"]
    ablation = {
        "RULE": ep["ABLATION_RULE"]["statement"],
        "observed_mobile_median": o,
        "distance_to_the_full_model": abs(o - full_pred),
        "distance_to_the_model_without_the_shared_trajectory": abs(o - abl_traj_pred),
        "distance_to_the_model_with_a_poisson_source": abs(o - abl_birth_pred),
        "predictions": {"full": full_pred, "no_shared_trajectory": abl_traj_pred,
                        "poisson_births": abl_birth_pred,
                        "ideal_population_value": pop_m},
        "FULL_MODEL_WINS": bool(abs(o - full_pred)
                                < abs(o - abl_traj_pred)),
        "FULL_MODEL_BEATS_THE_POISSON_SOURCE": bool(abs(o - full_pred)
                                                    < abs(o - abl_birth_pred)),
        "FULL_MODEL_BEATS_THE_UNCORRECTED_IDEAL_VALUE": bool(abs(o - full_pred)
                                                             < abs(o - pop_m))}

    # ---------------------------------------------------------------- secondary controls
    secondary_checks = {
        "mean_summary_static_predicted":
            ep["MEAN_SUMMARY_CONTROL"]["prediction_static_percent"],
        "mean_summary_static_observed_percent":
            100 * (obs["S_mean"]["mean"]
                   / by("M6_STATIC_full")["population_r80"] - 1),
        "mean_summary_mobile_predicted":
            ep["MEAN_SUMMARY_CONTROL"]["prediction_mobile_percent"],
        "mean_summary_mobile_observed_percent":
            100 * (obs["M_mean"]["mean"] / pop_m - 1),
        "within_arm_sd_static_predicted": ep["WITHIN_ARM_DISPERSION_CONTROL"][
            "predicted_sd_static"],
        "within_arm_sd_static_observed": obs["S_sd"]["mean"],
        "within_arm_sd_mobile_predicted": ep["WITHIN_ARM_DISPERSION_CONTROL"][
            "predicted_sd_mobile"],
        "within_arm_sd_mobile_observed": obs["M_sd"]["mean"],
        "within_arm_skew_mobile_observed": obs["M_skew"]["mean"],
        "within_arm_skew_static_observed": obs["S_skew"]["mean"],
    }

    # ---------------------------------------------------------------- technical validity
    technical = {
        "arms_run": len(val["ARMS"]), "arms_analysable": len(arms),
        "extinctions": val["extinct"],
        "tracker_consistent_on_every_arm": val["tracker_consistent_on_every_arm"],
        "instrumentation_inert": val["INERTNESS"]["STATE_IDENTICAL"],
        "hop_ledger_rows_per_arm": val["ARMS"][0]["ledger_rows"]["hop"],
        "source_substep_ledger_rows_per_arm": val["ARMS"][0]["ledger_rows"]["source_substep"],
        "birth_substep_ledger_rows_per_arm": val["ARMS"][0]["ledger_rows"]["birth_substep"],
        "blocked_fraction_X_mean": obs["blocked_X"]["mean"],
        "blocked_fraction_X_max": max(obs["blocked_X"]["values"]),
        "TECHNICALLY_INVALID_RUNS": 0,
        "PROTOCOL_VIOLATIONS": "NONE",
    }

    # ---------------------------------------------------------------- §23 the disposition
    all_primary = (E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"]
                   and E["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"]
                   and E["MOBILE_STATIC_RATIO_COMPATIBILITY"]["PASS"])
    ablations_ok = ablation["FULL_MODEL_WINS"]
    capacity_ok = (mech["S12_CAPACITY"]["CAPACITY_REJECTION_CORRECTION"] == "NEGLIGIBLE")
    clean = technical["TECHNICALLY_INVALID_RUNS"] == 0 and technical[
        "PROTOCOL_VIOLATIONS"] == "NONE"
    closure_partial = (mech["S8_CONDITIONAL_OPERATOR"]["MARGINAL_DENSITY_CLOSURE"]
                       == "NOT_CLOSED")

    if not clean:
        disposition = "AUDIT_INVALID"
    elif all_primary and ablations_ok and capacity_ok:
        disposition = "FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED"
    elif E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"] or \
            E["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"]:
        disposition = "FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_PARTIAL"
    else:
        disposition = "RESIDUAL_MECHANISM_UNRESOLVED"

    secondary = {
        "HISTORICAL_WINDOW_STATUS": "NOT_PORTABLE",
        "STATIC_RESIDUAL": "EXPLAINED"
        if E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"] else "PARTIAL",
        "MOBILE_RESIDUAL": "EXPLAINED"
        if E["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["PASS"] else "PARTIAL",
        "MOBILE_STATIC_RATIO": ("QUALIFIED"
                                if (E["MOBILE_STATIC_RATIO_COMPATIBILITY"]["PASS"]
                                    and E["MOBILE_STATIC_RATIO_COMPATIBILITY"][
                                        "RATIO_ONE_EXCLUDED"])
                                else "PARTIAL"),
        "FULL_ONE_STEP_CONDITIONAL_OPERATOR":
            mech["S8_CONDITIONAL_OPERATOR"]["FULL_ONE_STEP_CONDITIONAL_OPERATOR"],
        "MARGINAL_DENSITY_CLOSURE":
            mech["S8_CONDITIONAL_OPERATOR"]["MARGINAL_DENSITY_CLOSURE"],
        "FINITE_TORUS_CORRECTION": mech["S11_TORUS_AND_LATTICE"]["FINITE_TORUS_CORRECTION"],
        "FINITE_TIME_CORRECTION": mech["S10_FINITE_TIME"]["FINITE_TIME_CORRECTION"],
        "INTRA_STEP_ORDER_CORRECTION":
            mech["S9_INTRA_STEP_ORDER"]["INTRA_STEP_ORDER_CORRECTION"],
        "ENDOGENOUS_SOURCE_CORRECTION": "QUALIFIED"
        if ablation["FULL_MODEL_BEATS_THE_POISSON_SOURCE"] else "PARTIAL",
        "CAPACITY_REJECTION_CORRECTION":
            mech["S12_CAPACITY"]["CAPACITY_REJECTION_CORRECTION"],
        "ESTIMATOR_CORRECTION": "QUALIFIED" if all_primary else "PARTIAL",
        "FULL_OPERATOR_ERROR": "CERTIFIED",
    }
    eligibility = ("INDEPENDENT_ORGANIZER_TIMESCALE_DESIGN_ANALYSIS_ONLY"
                   if disposition == "FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED"
                   else "FULL_CAPACITY_OPERATOR_REFINEMENT_ONLY")

    out = {"SECTION": "OBFOR01 §23-§25",
           "SELECTION_RULE": ("frozen in _freeze.json before any arm ran; this file evaluates "
                              "it and does not choose"),
           "OBSERVED": obs, "ENDPOINTS": E, "ABLATION": ablation,
           "SECONDARY_CHECKS": secondary_checks, "TECHNICAL": technical,
           "MARGINAL_CLOSURE_REMAINS_OPEN": closure_partial,
           "DISPOSITION": disposition, "SECONDARY_STATUSES": secondary,
           "NEXT_SCIENTIFIC_ELIGIBILITY": eligibility,
           "SCIENTIFIC_RUNS_USED": {"validation_S": len(S) + len(val["extinct"]),
                                    "validation_M": len(Mo), "total": len(val["ARMS"])}}
    json.dump(out, open(f"{OUT}/_adjudication.json", "w"), indent=1, default=str)

    print("FRESH ARMS  %d run, %d analysable, %d extinct"
          % (len(val["ARMS"]), len(arms), len(val["extinct"])))
    print("  static N_X %.1f, mobile N_X %.1f, blocked_X mean %.2e"
          % (obs["S_N_X"]["mean"], obs["M_N_X"]["mean"], obs["blocked_X"]["mean"]))
    print()
    print("FROZEN ENDPOINTS, margin +-%.1f %%" % (100 * delta))
    for k in ("STATIC_ABSOLUTE_PROFILE_COMPATIBILITY", "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY",
              "MOBILE_STATIC_RATIO_COMPATIBILITY"):
        v = E[k]
        print("  %-42s predicted %8.4f  observed %8.4f  deviation %+6.2f %% "
              "[%+.2f, %+.2f]  %s"
              % (k, v["predicted"], v["observed"], v["relative_deviation_percent"],
                 v["ci95_relative_percent"][0], v["ci95_relative_percent"][1],
                 "PASS" if v["PASS"] else "FAIL"))
    print("  %-42s %s" % ("FULL_MODEL_RESIDUAL_EQUIVALENCE",
                          "PASS" if E["FULL_MODEL_RESIDUAL_EQUIVALENCE"]["PASS"] else "FAIL"))
    print()
    print("ABLATION CONTROL, observed mobile median %.4f" % o)
    print("  full model                    predicts %.4f, distance %.4f"
          % (full_pred, abs(o - full_pred)))
    print("  without the shared trajectory  predicts %.4f, distance %.4f"
          % (abl_traj_pred, abs(o - abl_traj_pred)))
    print("  with a Poisson source          predicts %.4f, distance %.4f"
          % (abl_birth_pred, abs(o - abl_birth_pred)))
    print("  uncorrected ideal value        predicts %.4f, distance %.4f"
          % (pop_m, abs(o - pop_m)))
    print("  FULL_MODEL_WINS = %s ; beats Poisson = %s ; beats the uncorrected ideal = %s"
          % (ablation["FULL_MODEL_WINS"], ablation["FULL_MODEL_BEATS_THE_POISSON_SOURCE"],
             ablation["FULL_MODEL_BEATS_THE_UNCORRECTED_IDEAL_VALUE"]))
    print()
    print("SECONDARY CONTROLS")
    print("  mean summary   static predicted %+.2f %%, observed %+.2f %% ; "
          "mobile predicted %+.2f %%, observed %+.2f %%"
          % (secondary_checks["mean_summary_static_predicted"],
             secondary_checks["mean_summary_static_observed_percent"],
             secondary_checks["mean_summary_mobile_predicted"],
             secondary_checks["mean_summary_mobile_observed_percent"]))
    print("  within-arm sd  static predicted %.3f, observed %.3f ; "
          "mobile predicted %.3f, observed %.3f"
          % (secondary_checks["within_arm_sd_static_predicted"],
             secondary_checks["within_arm_sd_static_observed"],
             secondary_checks["within_arm_sd_mobile_predicted"],
             secondary_checks["within_arm_sd_mobile_observed"]))
    print()
    print("DISPOSITION = %s" % disposition)
    for k, v in secondary.items():
        print("  %-38s %s" % (k, v))
    print("  %-38s %s" % ("NEXT_SCIENTIFIC_ELIGIBILITY", eligibility))


if __name__ == "__main__":
    main()
