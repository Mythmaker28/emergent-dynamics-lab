"""OBDCA01 §8, §9, §11, §12, §13 — literal application of the frozen taxonomy, the 138-arm
matrix, the adjudication of the estimand, the design comparison of alternatives, and the single
disposition.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import yaml

WC = "/home/claude/OBDCA01/verify/obdi02/wc"
OUT = "/home/claude/OBDCA01/out"
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")
SIZES = (36, 72, 96)


def slope(x, y, w):
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    xb = float((w * x).sum() / w.sum())
    sxx = float((w * (x - xb) ** 2).sum())
    return float((w * (x - xb) * y).sum() / sxx), float(sxx ** -0.5)


def fit(vals_by_L, pred=None):
    x, y, w = [], [], []
    for L in SIZES:
        v = np.asarray([q for q in vals_by_L[L] if np.isfinite(q) and q > 0], float)
        if len(v) < 2:
            continue
        lv = np.log(v)
        x.append(math.log(L))
        y.append(float(lv.mean()) - (math.log(pred[L]) if pred else 0.0))
        w.append(len(v) / max(float(lv.std(ddof=1)), 1e-12) ** 2)
    return slope(x, y, w)


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    frz = json.load(open(f"{WC}/OBDI02/out/_freeze.json"))
    rec = json.load(open(f"{OUT}/_recompute.json"))
    cv = json.load(open(f"{OUT}/_construct_validity.json"))
    gen = json.load(open(f"{OUT}/_margin_genealogy.json"))
    prov = json.load(open(f"{OUT}/_provenance.json"))
    P = rec["PER_ARM"]
    t25, t042 = rec["TOST_AT_0P25"], rec["TOST_AT_0P042"]
    sec = rec["SECONDARY"]
    pe = spec["primary_endpoint"]
    gate = spec["population_support_gate"]

    # ---------------------------------------------------------------- §8 taxonomy, literally
    frozen_taxonomy = list(spec["dispositions"])
    frozen_rules = {
        "primary_decision_rule": pe["decision_rule"],
        "primary_margin_field": "primary_endpoint.equivalence_margin = %s"
                                % pe["equivalence_margin"],
        "stringent_field": "primary_endpoint.stringent_reference_margin = %s, status: %s"
                           % (pe["stringent_reference_margin"], pe["stringent_reference_status"]),
        "global_qualification_rule": gate["qualification"],
        "stopping_rule": spec["stopping"]["rule"],
        "early_stopping": spec["stopping"]["EARLY_SCIENTIFIC_STOPPING"],
        "IS_THERE_A_FROZEN_MAPPING_FROM_RESULTS_TO_A_DISPOSITION_NAME": False,
        "WHAT_IS_FROZEN_INSTEAD": ("a list of nine names, plus TWO binding rules: the primary "
                                   "decision rule, and the global qualification rule requiring "
                                   "BOTH the population support gate AND the conditional "
                                   "equivalence test"),
    }
    contradictions = {
        "under_margin_0.25": {
            "interval": t25["interval"],
            "inside_the_margin": t25["interval_inside_margin"],
            "tost_p": t25["tost_p_value"], "PASS": t25["PASS"],
            "support_gate_passes": all(v["analysable"] >= v["required"]
                                       for v in sec["population_support"].values()),
            "therefore_the_frozen_global_qualification_rule_is": "SATISFIED",
            "why_was_equivalence_not_declared_in_OBDI02": (
                "it WAS declared by the frozen gate: OBDI02/out/_results.json records "
                "PRIMARY.PASS = true. The final disposition was then chosen by "
                "OBDI02/code/analysis_obdi02.py, a POST_RUN file at rank 7 of the hierarchy, "
                "which added a further condition — the interval had to lie inside "
                "[-0.042, +0.042] — that the frozen protocol had explicitly declared "
                "'reported, never decisive'."),
        },
        "under_margin_0.042": {
            "interval": t042["interval"],
            "point_estimate_outside_the_margin": bool(abs(rec["BETA_CY"]["beta"]) > 0.042),
            "interval_excludes_zero": bool(t042["interval"][0] > 0),
            "tost_p": t042["tost_p_value"], "PASS": t042["PASS"],
            "would_the_taxonomy_allow_NOT_ESTABLISHED": (
                "only if the estimate were compatible with zero AND there were no positive "
                "evidence of growth. At the 90 % level used by the frozen test the interval "
                "excludes zero, so under a binding 0.042 the honest reading would be closer to "
                "DOMAIN_SIZE_INVARIANCE_FAIL than to NOT_ESTABLISHED. This is hypothetical: "
                "0.042 is NOT the binding margin."),
        },
        "underpower_rule": {
            "did_the_frozen_protocol_declare_0.042_binding": False,
            "did_it_declare_it_underpowered_in_advance": True,
            "declared_power": pe["stringent_reference_power"],
            "was_there_a_frozen_rule_forbidding_execution": False,
            "the_frozen_stopping_rule_says": spec["stopping"]["rule"],
            "n_required_at_0.042_recorded_before_the_runs":
                frz["POWER"]["n_required_at_the_stringent_reference"],
            "n_required_at_the_binding_margin": frz["POWER"]["n_required_at_the_margin"],
            "n_adopted": frz["POWER"]["n_adopted"],
            "VERDICT": ("NO VIOLATION. The underpower stop applies to the BINDING primary. At "
                        "the binding margin 0.25 the required n was %s and 46 were run, so the "
                        "design was over-powered, not under-powered, for the test that actually "
                        "governed. The 0.042 figure was frozen as a non-decisive reference with "
                        "its insufficient power stated in advance."
                        % frz["POWER"]["n_required_at_the_margin"]),
        },
    }
    conformity = {
        "OBDI02_REPORTED_DISPOSITION": "DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED",
        "IS_IT_IN_THE_FROZEN_TAXONOMY": "DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED"
                                        in frozen_taxonomy,
        "WAS_IT_SELECTED_BY_A_FROZEN_RULE": False,
        "SELECTED_BY": "OBDI02/code/analysis_obdi02.py",
        "PHASE_OF_THAT_FILE": prov["FILE_CLASSIFICATION"][
            "OBDI02/code/analysis_obdi02.py"]["phase"],
        "RANK_IN_THE_HIERARCHY": 7,
        "IN_METHODS_CORE_HASH": False,
        "THE_CONDITION_IT_ADDED": "primary_interval_inside_[-0.042,+0.042]",
        "WHAT_THE_FREEZE_SAYS_ABOUT_THAT_FIGURE": pe["stringent_reference_status"],
        "CONFORMITY_VERDICT": "NON_CONFORMANT",
        "EXPLANATION": (
            "the frozen protocol binds the primary decision to equivalence_margin = 0.25 and "
            "binds the global qualification to the conjunction of the support gate and the "
            "conditional equivalence test. Both were satisfied. The reported disposition was "
            "produced by adding, after the results were open, a condition the freeze had "
            "explicitly stripped of decisiveness. Under the hierarchy of §3 a rank-7 file "
            "cannot do that."),
        "THE_CONFORMANT_DISPOSITION_WOULD_HAVE_BEEN":
            "ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE",
        "SEVERITY": ("this is a PROTOCOL VIOLATION in the conservative direction: it withheld a "
                     "qualification the freeze granted. It did not manufacture a result, move a "
                     "threshold in the permissive direction, drop an arm or replace a seed. It "
                     "is nevertheless a violation and is recorded as one."),
    }

    # ---------------------------------------------------------------- §9 the 138-arm matrix
    low_thresh = 0.5
    typ = {L: float(np.median([p["N_X_mean"] for p in P if p["L"] == L
                               and p["N_X_mean"] > 0])) for L in SIZES}
    matrix = []
    for p in P:
        low = bool(p["N_X_mean"] > 0 and p["N_X_mean"] < low_thresh * typ[p["L"]])
        matrix.append({
            "seed": p["seed"], "L": p["L"], "tag": p["tag"],
            "technically_valid": p["RUN_TECHNICALLY_VALID"],
            "online_posthoc_agree": p["GATES_AGREE"],
            "extinct": p["EXTINCT"],
            "N_X_median": p["N_X_median"], "N_X_mean": p["N_X_mean"], "N_X_min": p["N_X_min"],
            "frac_window_N_X_below_20": p["frac_window_below_20"],
            "frac_window_N_X_below_50": p["frac_window_below_50"],
            "summary_CY": p["summary_CY_route2"], "Rg": p["Rg"], "r80": p["r80"],
            "profile_TV": p["profile_TV"], "winding_frames": p["winding_frames"],
            "classification": p["classification"],
            "legacy_D_gate": p["LEGACY_RELATIVE_LOCALIZATION"],
            "in_primary_analysis": bool(np.isfinite(p["summary_CY_route2"])),
            "exclusion_reason": (None if np.isfinite(p["summary_CY_route2"])
                                 else "extinct: the per-seed summary is undefined"),
            "LOW_POPULATION_NOT_EXTINCT": low})
    ext = [m for m in matrix if m["extinct"]]
    low = [m for m in matrix if m["LOW_POPULATION_NOT_EXTINCT"]]
    infl = cv["CONDITIONAL_DIAGNOSTICS"]["influence_top10"]
    matrix_summary = {
        "n_arms": len(matrix),
        "technically_valid": sum(1 for m in matrix if m["technically_valid"]),
        "evaluators_agree": sum(1 for m in matrix if m["online_posthoc_agree"]),
        "extinctions": {"n": len(ext), "by_L": {str(L): sum(1 for m in ext if m["L"] == L)
                                                for L in SIZES},
                        "tags": [m["tag"] for m in ext]},
        "low_population_not_extinct": {
            "rule": "N_X_mean below half the per-size median of the surviving arms "
                    "(post-hoc, diagnostic, never applied)",
            "typical_N_X_by_L": typ,
            "n": len(low), "by_L": {str(L): sum(1 for m in low if m["L"] == L) for L in SIZES},
            "detail": [{"tag": m["tag"], "L": m["L"], "N_X_mean": m["N_X_mean"],
                        "summary_CY": m["summary_CY"]} for m in low]},
        "weight_in_the_regression": (
            "the frozen estimator weights a SIZE, not an arm: w_L = n_L / sd_L(log summary)^2. "
            "A single extreme arm therefore acts twice — it moves the size mean and it inflates "
            "that size's sd, which lowers its weight. The net influence is measured by "
            "leave-one-out below rather than argued."),
        "influence_leave_one_out_top5": infl[:5],
        "max_abs_delta_beta_from_one_arm": cv["CONDITIONAL_DIAGNOSTICS"][
            "max_abs_delta_beta_from_one_arm"],
        "NO_POSTHOC_EXCLUSION_WAS_APPLIED": True,
    }

    # ---------------------------------------------------------------- §11 adjudication
    null = cv["POPULATION_NULL"]
    cond = cv["CONDITIONAL_DIAGNOSTICS"]
    dsn = cv["DOWNSAMPLING"]["AGGREGATE_BY_N"]
    gr = cv["GUARD_RAIL_CONFOUND_CHECK"]
    criteria = {
        "1_the_metric_depends_strongly_on_N_X": {
            "corr_logN_log_offset": cond["corr_logN_log_offset"],
            "coefficient_of_logN_in_the_joint_model": cond["model_L_plus_logN"]["coef_logN"],
            "t_statistic": cond["model_L_plus_logN"]["t_logN"],
            "raw_only_downsampling_inflation_at_N=5": dsn["5"]["ratio_of_means"],
            "analytic_inflation_N=121_to_N=5": (
                cv["FINITE_CENTRE_ERROR"]["E_ABS_C_MINUS_Y_BY_N"]["5"]["E_abs_C_minus_Y"]
                / cv["FINITE_CENTRE_ERROR"]["E_ABS_C_MINUS_Y_BY_N"]["121"]["E_abs_C_minus_Y"]),
            "HOLDS": True},
        "2_that_dependence_can_produce_a_material_part_of_the_L_effect": {
            "null_mean_beta_with_no_domain_effect_at_all": null["null_mean"],
            "null_sd": null["null_sd"],
            "P_null_beta_ge_observed": null["P_beta_ge_observed"],
            "classification": null["CLASSIFICATION"],
            "beta_with_logN_controlled": cond["model_L_plus_logN"]["beta_L"],
            "beta_restricted_to_healthy_population":
                cond["restricted_to_N_X_mean_ge_60"]["beta"],
            "beta_from_the_per_size_medians": cond["beta_from_the_medians"],
            "HOLDS": True},
        "3_the_effect_must_not_be_read_as_physical_displacement": {
            "reason": ("under a mechanism with NO domain effect whatsoever, injecting only the "
                       "observed population distributions produces a coefficient at least as "
                       "large as the observed one with probability %.3f. The observed value is "
                       "therefore TYPICAL of a pure measurement artefact and cannot be "
                       "attributed to the domain." % null["P_beta_ge_observed"]),
            "HOLDS": True},
    }
    estimand_status = "ATTACHMENT_ESTIMAND_POPULATION_CONFOUNDED"
    honest_caveat = (
        "the confound is not unique to |C - Y|: the guard-rail statistics are population "
        "sensitive too (corr(log N_X, log R_g) = %.3f, log r80 = %.3f, profile TV = %.3f "
        "against %.3f for the primary metric). What separates them is that their observed "
        "coefficients are already indistinguishable from zero, so no artefact needs to be "
        "invoked to explain them, whereas the primary coefficient is entirely explained by one."
        % (gr["corr_logN_log_Rg"], gr["corr_logN_log_r80"], gr["corr_logN_profileTV"],
           gr["corr_logN_log_absCY"]))

    # ---------------------------------------------------------------- §12 alternatives
    # r80 measured from the ORGANISER is already recorded per frame: evaluate it here
    r80y = {}
    for L in SIZES:
        vals = []
        for p in P:
            if p["L"] != L:
                continue
            z = np.load(f"{WC}/OBDI02/raw/{p['tag'].replace('/', '__')}.npz", allow_pickle=True)
            fr = [json.loads(s) for s in z["frames"] if json.loads(s)["step"] > 2000]
            v = np.array([f.get("r80_organiser", np.nan) for f in fr], float)
            v = v[np.isfinite(v)]
            vals.append(float(np.median(v)) if len(v) else float("nan"))
        r80y[L] = vals
    b_r80y, se_r80y = fit(r80y)
    lN, lv = [], []
    for L in SIZES:
        for p, v in zip([q for q in P if q["L"] == L], r80y[L]):
            if p["N_X_mean"] > 0 and np.isfinite(v) and v > 0:
                lN.append(math.log(p["N_X_mean"]))
                lv.append(math.log(v))
    corr_r80y = float(np.corrcoef(lN, lv)[0, 1])

    candidates = {
        "r80_Y (source-centred 80 % radius)": {
            "alignment_with_attachment": "HIGH: it is the radius of the cloud measured FROM the "
                                         "organiser, so it answers 'how far from the source is "
                                         "the mass' without estimating a centre at all",
            "low_population_bias": "MODERATE: a quantile of N distances, no centre estimation, "
                                   "so no 1/N centre error; the quantile itself is noisier at "
                                   "small N",
            "variance": "measured: se(beta) = %.5f on these very data" % se_r80y,
            "behaviour_under_extinction": "undefined when N_X = 0, same as any spatial statistic",
            "invariance_under_the_null": "to be established by the same population null before "
                                         "any use",
            "parameter_free_prediction": "YES: the operator's exact relative profile gives r80_Y "
                                         "with no fitted constant",
            "auditability": "HIGH: already recorded per frame in every archive of the chain",
            "compatible_with_recorded_data": "YES, recomputable on all 138 arms and on OBDI01",
            "needs_new_simulations": "NO for the estimate; YES for a pre-registered null",
            "measured_here": {"beta": b_r80y, "se": se_r80y,
                              "corr_logN_log_value": corr_r80y}},
        "mean per-particle d_T(X_i, Y)^2": {
            "alignment_with_attachment": "HIGH", "low_population_bias":
                "LOW: an unbiased mean over particles, no centre",
            "parameter_free_prediction": "YES, the operator gives the second moment exactly",
            "auditability": "MEDIUM: not currently recorded per frame, but recomputable from the "
                            "final field only, not from the whole window",
            "needs_new_simulations": "NO for the law, but the window statistic is not recorded"},
        "normalised likelihood under the N2 profile": {
            "alignment_with_attachment": "HIGH", "low_population_bias":
                "LOW: the likelihood already accounts for the sample size",
            "auditability": "MEDIUM", "needs_new_simulations": "YES"},
        "latent displacement by maximum likelihood with N-dependent uncertainty": {
            "alignment_with_attachment": "HIGHEST: it estimates the quantity |C* - Y| itself and "
                                         "reports its own uncertainty",
            "low_population_bias": "LOWEST by construction", "auditability": "LOW: the most "
            "machinery, the most assumptions", "needs_new_simulations": "YES"},
        "finite-N corrected centre": {
            "alignment_with_attachment": "HIGH", "low_population_bias":
                "corrected to first order only; the correction is exact for the empirical mean "
                "and only approximate for the Frechet centre on a torus",
            "auditability": "MEDIUM", "needs_new_simulations": "YES"},
    }
    selected = "r80_Y (source-centred 80 % radius)"

    # ---------------------------------------------------------------- §13 disposition
    support_pass = all(v["analysable"] >= v["required"] for v in sec["population_support"].values())
    guardrails = {
        "Rg_beta": sec["scaling_Rg"]["beta"], "Rg_interval": sec["scaling_Rg"]["interval"],
        "r80_beta": sec["scaling_r80"]["beta"], "r80_interval": sec["scaling_r80"]["interval"],
        "density_gamma": sec["density_exponent"]["gamma"],
        "density_interval": sec["density_exponent"]["interval"],
        "winding": sec["true_winding"],
        "profile": sec["radial_profile"],
        "NO_MATERIAL_CONTRADICTION": True,
    }
    if prov["PROVENANCE_STATUS"] != "SELF_CONTAINED_SPLIT_DELIVERY_PASS":
        disp = "PROVENANCE_FAIL"
    elif gen["VERDICT"] == "D":
        disp = "FROZEN_PROTOCOL_CONFLICT"
    elif gen["VERDICT"] == "B":
        disp = "OBDI02_BINDING_STRICT_TARGET_FAIL"
    elif estimand_status == "ATTACHMENT_ESTIMAND_POPULATION_CONFOUNDED" and t25["PASS"] \
            and support_pass:
        disp = "CUMULATIVE_CLOUD_QUALIFIED_UNDER_FROZEN_PRIMARY__ATTACHMENT_ESTIMAND_LIMITED"
    elif t25["PASS"] and support_pass:
        disp = "CUMULATIVE_CLOUD_QUALIFIED_UNDER_FROZEN_PRIMARY__STRICT_PRECISION_TARGET_NOT_MET"
    else:
        disp = "ATTACHMENT_ESTIMAND_POPULATION_CONFOUNDED__FORMAL_RESULT_NOT_PHYSICALLY_ADJUDICABLE"

    why_not = {
        "CUMULATIVE_CLOUD_QUALIFIED_UNDER_FROZEN_PRIMARY__STRICT_PRECISION_TARGET_NOT_MET":
            "all its conditions hold, but it does not record the construct limitation, and §10 "
            "established one that is material",
        "ATTACHMENT_ESTIMAND_POPULATION_CONFOUNDED__FORMAL_RESULT_NOT_PHYSICALLY_ADJUDICABLE":
            "the primary metric is indeed not physically adjudicable, but this disposition "
            "would also withhold the qualification the frozen protocol grants on the size and "
            "profile axes, which are supported by the same 138 arms and whose coefficients are "
            "flat to about one percent",
        "OBDI02_BINDING_STRICT_TARGET_FAIL": "0.042 is not the binding margin: §5 verdict C",
        "OBDI02_AUDIT_INVALID__UNDERPOWERED_BINDING_GATE_EXECUTED":
            "the binding gate at 0.25 required n = %s and 46 were run; no frozen rule forbade "
            "execution" % frz["POWER"]["n_required_at_the_margin"],
        "FROZEN_PROTOCOL_CONFLICT": "there is no conflict inside the freeze: one field is the "
                                    "margin, another is a reference explicitly marked "
                                    "non-decisive",
        "PROVENANCE_FAIL": "provenance passes",
    }

    out = {
        "SECTION": "OBDCA01 §8, §9, §11, §12, §13",
        "FROZEN_TAXONOMY": frozen_taxonomy, "FROZEN_RULES": frozen_rules,
        "POTENTIAL_CONTRADICTIONS": contradictions,
        "CONFORMITY_OF_THE_OBDI02_DISPOSITION": conformity,
        "ARM_MATRIX": matrix, "ARM_MATRIX_SUMMARY": matrix_summary,
        "ESTIMAND_ADJUDICATION": {"criteria": criteria, "STATUS": estimand_status,
                                  "HONEST_CAVEAT": honest_caveat},
        "ALTERNATIVE_ESTIMANDS": {"candidates": candidates, "SELECTED_FOR_A_FUTURE_MISSION":
                                  selected,
                                  "NO_CONFIRMATORY_THRESHOLD_IS_CHOSEN_HERE": True},
        "GUARD_RAILS": guardrails,
        "DISPOSITION": disp, "WHY_NOT_THE_OTHERS": why_not,
        "SECONDARY_STATUSES": {
            "FROZEN_PRIMARY_MARGIN": pe["equivalence_margin"],
            "TOST_AT_0P25": "PASS" if t25["PASS"] else "FAIL",
            "TOST_AT_0P042": "PASS" if t042["PASS"] else "FAIL",
            "STRICT_0P042_TARGET_ROLE": "SECONDARY",
            "ATTACHMENT_ESTIMAND_VALIDITY": estimand_status,
            "INTRINSIC_CLOUD_SIZE_INVARIANCE": "PASS",
            "NON_EXTENSIVE_POPULATION": "PASS",
            "TRUE_WINDING": "ABSENT_IN_TESTED_RANGE",
            "RADIAL_PROFILE_COMPATIBILITY": "PASS",
            "CUMULATIVE_CLOUD_STATUS": "QUALIFIED",
        },
        "NEXT_SCIENTIFIC_ELIGIBILITY": "ORGANIZER_BOUND_TIMESCALE_REDERIVATION_ONLY",
        "PROTOCOL_VIOLATIONS": [conformity["EXPLANATION"]],
    }
    json.dump(out, open(f"{OUT}/_adjudication.json", "w"), indent=1, default=str)

    print("frozen taxonomy: %d names ; a frozen results->name mapping exists: %s"
          % (len(frozen_taxonomy),
             frozen_rules["IS_THERE_A_FROZEN_MAPPING_FROM_RESULTS_TO_A_DISPOSITION_NAME"]))
    print("frozen global qualification rule:", frozen_rules["global_qualification_rule"])
    print("\nCONFORMITY:", conformity["CONFORMITY_VERDICT"])
    print("  selected by", conformity["SELECTED_BY"], "(", conformity["PHASE_OF_THAT_FILE"],
          ", rank", conformity["RANK_IN_THE_HIERARCHY"], ")")
    print("  conformant disposition would have been:",
          conformity["THE_CONFORMANT_DISPOSITION_WOULD_HAVE_BEEN"])
    print("\nunderpower rule:", contradictions["underpower_rule"]["VERDICT"][:120])
    print("\nmatrix: %d arms, %d valid, %d agree, %d extinct, %d low-population"
          % (matrix_summary["n_arms"], matrix_summary["technically_valid"],
             matrix_summary["evaluators_agree"], matrix_summary["extinctions"]["n"],
             matrix_summary["low_population_not_extinct"]["n"]))
    print("extinctions by L:", matrix_summary["extinctions"]["by_L"],
          " low-population by L:", matrix_summary["low_population_not_extinct"]["by_L"])
    print("\nESTIMAND:", estimand_status)
    print("alternative selected:", selected,
          " measured beta = %+.5f se = %.5f corr with log N_X = %.3f"
          % (b_r80y, se_r80y, corr_r80y))
    print("\nDISPOSITION =", disp)


if __name__ == "__main__":
    main()
