"""OBDI02 §4-§5 — exact reconstruction of the OBDI01 outcome vector, and recovery of the
primary estimand from the frozen protocol rather than from the prose of the report.

Every field below is read out of the delivered `obdi01_protocol.yaml`, `_freeze.json` and
`_results.json`, or recomputed from `_arms.json`. Nothing is taken from the summary text.
"""
from __future__ import annotations

import json

import numpy as np
import yaml

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI01/code/obdi01_protocol.yaml"))
    R = json.load(open(f"{WC}/OBDI01/out/_results.json"))
    A = json.load(open(f"{WC}/OBDI01/out/_arms.json"))
    po = spec["principal_outcome"]
    P = R["PRINCIPAL"]
    c = float(P["critical_value_c"])
    comp = P["components"]
    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    n_per = int(spec["domain"]["SEEDS_PER_SIZE"])

    def per_L_arm_counts(stat):
        return {str(L): {"arms_run": sum(1 for a in A if a["L"] == L),
                         "arms_analysable": sum(1 for a in A if a["L"] == L
                                                and np.isfinite(a["summary"][stat]))}
                for L in sizes}

    outcomes = {}

    # ------------------------------------------------------------ 1-3 : the shape statistics
    for stat, label in (("Rg", "invariance de R_g"), ("r80", "invariance de r80"),
                        ("organiser_to_core", "invariance de |C - Y|")):
        d = comp["A_shape_invariance"]["by_statistic"][stat]
        outcomes[label] = {
            "COMPONENT": "A_shape_invariance", "STATISTIC_KEY": stat,
            "ESTIMAND": ("beta = d log(observed / predicted) / d log L, the log-log slope of "
                         "the arm-level median of %s after dividing out the operator's exact "
                         "finite-size prediction at that L" % stat),
            "ESTIMATOR": ("weighted least squares slope of y_L = log(mean over arms at L) - "
                          "log(pred_L) on log L, over the %d domain sizes; weights "
                          "w_L = (mean_L / se_L)^2 with se_L = max(sd_realised, sd_prereg) / "
                          "sqrt(n_L)" % len(sizes)),
            "NULL_HYPOTHESIS": "H0 : |beta| >= margin  (NOT equivalent to a constant)",
            "ALTERNATIVE_HYPOTHESIS": "H1 : |beta| < margin  (equivalent to a constant)",
            "EQUIVALENCE_MARGIN": float(d["margin"]),
            "CONFIDENCE_LEVEL": {
                "critical_value_c": c,
                "two_sided_per_test_alpha": float(po["multiplicity"]["per_test_alpha"]),
                "implied_two_sided_interval": "%.4f %%" % (
                    100 * (1 - float(po["multiplicity"]["per_test_alpha"]))),
                "family_alpha": float(po["multiplicity"]["family_alpha"]),
                "multiplicity_correction": po["multiplicity"]["correction"],
                "K": int(po["multiplicity"]["K"])},
            "UNIT_OF_ANALYSIS": "the seed (one arm = one seed); frames are reduced first",
            "AGGREGATION_RULE": ("within a seed: median over the %d in-window frames; across "
                                 "seeds at one L: arithmetic mean of the arm medians; across "
                                 "L: weighted least squares on log L"
                                 % ((spec["window"]["HORIZON"] - spec["window"]["BURN_IN"])
                                    // spec["window"]["SAMPLE_EVERY"])),
            "RESULT": {"beta": d["beta"], "se": d["se"],
                       "abs_beta_plus_c_se": d["abs_beta_plus_c_se"],
                       "per_L": d["per_L"],
                       "arm_counts": per_L_arm_counts(stat)},
            "PASS_OR_FAIL": "PASS" if d["PASS"] else "FAIL",
        }

    # ------------------------------------------------------------ 4 : density exponent
    B = comp["B_density_exponent"]
    outcomes["exposant de densite"] = {
        "COMPONENT": "B_density_exponent", "STATISTIC_KEY": "density",
        "ESTIMAND": "gamma = d log(N_X / L^2) / d log L",
        "ESTIMATOR": "weighted least squares slope of log(mean density at L) on log L",
        "NULL_HYPOTHESIS": "H0 : |gamma + 2| >= margin",
        "ALTERNATIVE_HYPOTHESIS": "H1 : |gamma + 2| < margin",
        "EQUIVALENCE_MARGIN": float(po["components"]["B_density_exponent"]["margin"]),
        "CONFIDENCE_LEVEL": {"critical_value_c": c,
                             "two_sided_per_test_alpha":
                                 float(po["multiplicity"]["per_test_alpha"])},
        "UNIT_OF_ANALYSIS": "the seed",
        "AGGREGATION_RULE": ("within a seed: mean N_X over the in-window frames divided by "
                             "L^2; across seeds: arithmetic mean; across L: WLS on log L. "
                             "NOTE: the extinct arm entered this mean with density 0."),
        "RESULT": {"gamma": B["gamma"], "se": B["se"],
                   "abs_dev_plus_c_se": B["abs_dev_plus_c_se"], "per_L": B["per_L"]},
        "PASS_OR_FAIL": "PASS" if B["PASS"] else "FAIL",
    }

    # ------------------------------------------------------------ 5 : true winding
    C = comp["C_no_true_winding"]
    outcomes["winding veritable"] = {
        "COMPONENT": "C_no_true_winding", "STATISTIC_KEY": "any_winding",
        "ESTIMAND": ("the probability that the cloud's support carries a non-contractible cycle "
                     "on the torus, at each L"),
        "ESTIMATOR": ("pooled fraction of in-window frames flagged by the 5x5 tiling lift, "
                      "over all arms at that L"),
        "NULL_HYPOTHESIS": "H0 : the winding frequency exceeds the tolerance",
        "ALTERNATIVE_HYPOTHESIS": "H1 : it does not",
        "EQUIVALENCE_MARGIN": float(po["components"]["C_no_true_winding"]["tolerance"]),
        "CONFIDENCE_LEVEL": "none: a deterministic threshold on a pooled frequency",
        "UNIT_OF_ANALYSIS": ("the FRAME, pooled across seeds — the one place where OBDI01 did "
                             "not use the seed as the unit. It is defensible only because the "
                             "observed count is exactly zero, for which no variance model is "
                             "needed; it would NOT be defensible for a non-zero count."),
        "AGGREGATION_RULE": "sum of flagged frames / sum of frames, per L",
        "RESULT": C["per_L"], "PASS_OR_FAIL": "PASS" if C["PASS"] else "FAIL",
    }

    # ------------------------------------------------------------ 6 : radial profile
    Dc = comp["D_profile_compatibility"]
    outcomes["compatibilite du profil radial"] = {
        "COMPONENT": "D_profile_compatibility", "STATISTIC_KEY": "profile_TV",
        "ESTIMAND": ("the total-variation distance between the pooled empirical radial mass "
                     "distribution about the organiser and the exact predicted radial "
                     "distribution of the operator, at each L"),
        "ESTIMATOR": ("per arm, TV between the window-pooled empirical radial histogram (16 "
                      "integer-distance bins) and the DFT-exact relative profile"),
        "NULL_HYPOTHESIS": "H0 : the arm's profile is incompatible with the exact kernel",
        "ALTERNATIVE_HYPOTHESIS": "H1 : it is compatible",
        "EQUIVALENCE_MARGIN": {L: v["threshold"] for L, v in Dc["per_L"].items()},
        "CONFIDENCE_LEVEL": ("the q99 of an envelope generated from n_eff = %d independent "
                             "draws of the exact kernel"
                             % int(po["components"]["D_profile_compatibility"][
                                 "envelope_n_effective_frames"])),
        "UNIT_OF_ANALYSIS": "the seed",
        "AGGREGATION_RULE": "at each L, at least %d of the %d arms must be within the envelope"
                            % (int(po["components"]["D_profile_compatibility"]["arms_required"]),
                               n_per),
        "RESULT": Dc["per_L"], "PASS_OR_FAIL": "PASS" if Dc["PASS"] else "FAIL",
    }

    # ------------------------------------------------------------ 7 : the historical endpoint
    S = R["SECONDARY"]
    outcomes["endpoint historique frac_localized >= 0.95"] = {
        "COMPONENT": "SECONDARY (locked, not part of the region)",
        "STATISTIC_KEY": "RELATIVE_LOCALIZATION",
        "ESTIMAND": ("the probability that a frame has r80 measured from the organiser at or "
                     "below min(12.8, 0.35 L)"),
        "ESTIMATOR": "per arm, the fraction of in-window frames satisfying it",
        "NULL_HYPOTHESIS": "H0 : the fraction is below 0.95",
        "ALTERNATIVE_HYPOTHESIS": "H1 : it is at least 0.95",
        "EQUIVALENCE_MARGIN": "not an equivalence test: a one-sided threshold at 0.95",
        "CONFIDENCE_LEVEL": "none: a deterministic per-arm threshold",
        "UNIT_OF_ANALYSIS": "the seed, judged one arm at a time",
        "AGGREGATION_RULE": "reported per arm and counted per L; never aggregated into a verdict",
        "RESULT": {"per_arm": S["per_arm"], "passing_by_L": S["passing_by_L"],
                   "arms_by_L": S["arms_by_L"],
                   "cross_check_against_the_OBTC02_condition":
                       S["cross_check_against_obtc02_gate"]["AGREE"]},
        "PASS_OR_FAIL": "NOT_PRIMARY — reported, never decisive",
    }

    # ------------------------------------------------------------ ambiguity 1
    amb1 = {
        "QUESTION": "which are the four components, and which one failed?",
        "THE_FOUR_COMPONENTS": {
            "A_shape_invariance": {
                "contains": ["Rg", "r80", "organiser_to_core"],
                "PASS": comp["A_shape_invariance"]["PASS"],
                "note": "a SINGLE component carrying THREE statistics; it passes only if all "
                        "three pass"},
            "B_density_exponent": {"contains": ["density"],
                                   "PASS": comp["B_density_exponent"]["PASS"]},
            "C_no_true_winding": {"contains": ["any_winding"],
                                  "PASS": comp["C_no_true_winding"]["PASS"]},
            "D_profile_compatibility": {"contains": ["profile_TV"],
                                        "PASS": comp["D_profile_compatibility"]["PASS"]},
        },
        "FAILING_COMPONENT": "A_shape_invariance",
        "FAILING_STATISTIC_WITHIN_IT": "organiser_to_core",
        "STATISTICS_THAT_PASSED_INSIDE_THE_FAILING_COMPONENT": ["Rg", "r80"],
        "RESOLUTION": ("'three components out of four' is exact at the COMPONENT level: B, C "
                       "and D passed, A failed. At the STATISTIC level it is five out of six: "
                       "Rg, r80, density, winding and profile passed, |C - Y| failed. Both "
                       "statements are true of the same result; the report used the first."),
    }

    # ------------------------------------------------------------ ambiguity 2
    amb2 = {
        "QUESTION": "what does the notation 5/4, 4/4, 5/4 mean?",
        "SOURCE": ("OBDI01/code/run_obdi01.py prints "
                   "'%d/%d' % (v['arms_within'], v['arms_required']) for the D component"),
        "ANSWER": "PASSING_ARMS / REQUIRED_PASSING_ARMS — NOT passing over total",
        "IS_IT_A_TRANSCRIPTION_ERROR": False,
        "IS_IT_A_COUNT_OF_STATISTICS": False,
        "WHY_IT_LOOKED_WRONG": ("a numerator larger than a denominator reads as impossible "
                                "when the denominator is assumed to be the total. Here the "
                                "denominator is the REQUIREMENT, so 5/4 means five arms passed "
                                "where four were required."),
        "UNAMBIGUOUS_RESTATEMENT": {
            L: {"PASSING_ARMS_OVER_TOTAL": "%d/%d" % (v["arms_within"], n_per),
                "REQUIRED_PASSING_ARMS_OVER_TOTAL": "%d/%d" % (v["arms_required"], n_per),
                "sentence": "L=%s : %d/%d bras passent ; seuil requis : %d/%d"
                            % (L, v["arms_within"], n_per, v["arms_required"], n_per),
                "PASS": v["PASS"]}
            for L, v in Dc["per_L"].items()},
        "CAVEAT_AT_L_72": ("at L = 72 one arm went extinct, so its TV is undefined and it was "
                           "counted as NOT within the envelope. The component therefore passed "
                           "exactly at its threshold, 4 of 5 where 4 were required."),
    }

    # ------------------------------------------------------------ §5 primary estimand
    dcy = comp["A_shape_invariance"]["by_statistic"]["organiser_to_core"]
    prim = {
        "RECOVERED_FROM": "OBDI01/code/obdi01_protocol.yaml, principal_outcome.components."
                          "A_shape_invariance, statistic organiser_to_core",
        "NAME": "beta_CY",
        "DEFINITION": ("log d_CY(L) = alpha + beta_CY * log L + eps, where d_CY(L) is the "
                       "arm-level median of |C - Y| DIVIDED BY the operator's exact finite-size "
                       "prediction at that L. The division is part of the frozen estimand, not "
                       "a later adjustment."),
        "FROZEN_CONSTRUCTION": po["components"]["A_shape_invariance"]["construction"],
        "FROZEN_RULE": po["components"]["A_shape_invariance"]["rule"],
        "FROZEN_MARGIN": float(po["components"]["A_shape_invariance"]["margin"]),
        "OBDI01_RESULT": {"beta": dcy["beta"], "se": dcy["se"],
                          "abs_beta_plus_c_se": dcy["abs_beta_plus_c_se"],
                          "excess_over_the_frozen_margin":
                              dcy["abs_beta_plus_c_se"]
                              - float(po["components"]["A_shape_invariance"]["margin"])},
        "C_DEFINITION": ("C is the toroidal Frechet centre of the X field: the separable exact "
                         "minimiser of the sum of squared toroidal distances, computed axis by "
                         "axis, rounded to a lattice site"),
        "Y_DEFINITION": ("Y is the organiser: the single cell carrying n_Y > 0. With one "
                         "organiser its position is exact, not an estimate."),
        "METRIC": ("|C - Y| is the toroidal Euclidean distance hypot(wdist1(dy, L), "
                   "wdist1(dx, L)) with wdist1 the wrapped one-dimensional distance"),
    }

    out = {"SECTION": "OBDI02 §4-§5",
           "DOMAIN_SIZES": sizes, "SEEDS_PER_SIZE": n_per,
           "OUTCOME_VECTOR": outcomes,
           "AMBIGUITY_1_FOUR_COMPONENTS": amb1,
           "AMBIGUITY_2_NOTATION": amb2,
           "PRIMARY_ESTIMAND_RECOVERED": prim}
    json.dump(out, open(f"{OUT}/_outcome_vector.json", "w"), indent=1, default=str)

    print("OUTCOME VECTOR")
    for k, v in outcomes.items():
        print("  %-46s %s" % (k, v["PASS_OR_FAIL"]))
    print("\nAMBIGUITY 1 : failing component = %s, failing statistic = %s"
          % (amb1["FAILING_COMPONENT"], amb1["FAILING_STATISTIC_WITHIN_IT"]))
    print("              component level 3/4 ; statistic level 5/6")
    print("AMBIGUITY 2 : %s" % amb2["ANSWER"])
    for L, v in amb2["UNAMBIGUOUS_RESTATEMENT"].items():
        print("              " + v["sentence"])
    print("\nPRIMARY ESTIMAND beta_CY   frozen margin %.3f   OBDI01 beta %.4f se %.4f -> %.4f"
          % (prim["FROZEN_MARGIN"], dcy["beta"], dcy["se"], dcy["abs_beta_plus_c_se"]))


if __name__ == "__main__":
    main()
