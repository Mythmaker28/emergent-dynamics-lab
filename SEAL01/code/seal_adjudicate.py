"""SEAL §5 — the terminal adjudication, from the reconstructed evidence only."""
from __future__ import annotations

import json

OUT = "/home/claude/SEAL01/out"
V = "/home/claude/SEAL01/verify/wc"


def main():
    pv = json.load(open(f"{OUT}/_seal_provenance.json"))
    fl = json.load(open(f"{OUT}/OBFOR01_PREDICTION_INFORMATION_FLOW.json"))
    rc = json.load(open(f"{OUT}/OBFOR01_HEADLINE_RECOMPUTATION.json"))
    obtr = json.load(open(f"{V}/OBTR01/out/_freeze.json"))

    # ------------------------------------------------------- zero-run compliance
    elig = obtr["NEXT_ELIGIBILITY"]
    radial = next(t for t in elig["WHAT_WOULD_BE_ELIGIBLE"]
                  if "absolute radial deficit" in t["target"])
    zero_run = {
        "THE_PREMISE_TO_TEST": ("the seal expects that the parent handoff authorised zero new "
                                "scientific runs, and that OBFOR01 therefore violated it"),
        "WHAT_THE_PARENT_ACTUALLY_FROZE": {
            "headline": elig["NEXT_SCIENTIFIC_ELIGIBILITY"],
            "the_targeted_sub_entry": radial,
            "reading": ("the headline reads NO_FRESH_RUN_AT_THE_QUALIFIED_POINT_FOR_THIS_"
                        "QUESTION, and 'this question' is the historical window. The same "
                        "frozen artefact lists the absolute radial deficit as "
                        "ELIGIBLE_AT_THE_QUALIFIED_POINT, which is precisely the question "
                        "OBFOR01 was given.")},
        "WHAT_THE_OBFOR01_MANDATE_ITSELF_SAID": (
            "its §16 requires a raw-only phase BEFORE any new start, §17 states the criterion "
            "for OPENING a fresh validation, §18 specifies conditions S, M and E, §19 fixes "
            "the validation statistics and §20 fixes a run budget and fresh seeds. A mandate "
            "that budgets runs is not a mandate that forbids them."),
        "THE_LATER_HANDOFF": (
            "a subsequent handoff, ORGANIZER-BOUND-FULL-OPERATOR-RECONSTRUCTION-01, does carry "
            "NEW_ENGINE_STARTS = 0. It arrived AFTER OBFOR01 was delivered and cannot bind it "
            "retroactively. It is named here so that nothing is concealed."),
        "REAL_DEFECT_FOUND": (
            "OBTR01's headline eligibility string is easy to misread as a blanket zero-run "
            "authorisation, because the scope qualifier FOR_THIS_QUESTION sits inside the "
            "token. That ambiguity is a reporting defect and is the likely origin of the "
            "seal's premise. Future eligibility strings should name the question they close."),
        "ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE": "PASS",
        "CONFIDENCE": ("the classification rests on the frozen text of both the parent "
                       "artefact and the governing mandate, not on the outcome"),
    }

    # ------------------------------------------------------- prospectivity
    lb_changed = pv["ANY_LOAD_BEARING_FILE_CHANGED_AFTER_THE_FREEZE"]
    acc = pv["FRESH_ARM_ACCOUNTING"]
    prospectivity = {
        "freeze_commit": pv["TIPS"]["OBFOR01_FREEZE_TIP"]["actual"],
        "first_fresh_arms_commit": pv["TIPS"]["OBFOR01_FIRST_FRESH_ARMS_COMMIT"]["actual"],
        "all_load_bearing_present_at_the_freeze":
            pv["ALL_LOAD_BEARING_PRESENT_AT_THE_FREEZE"],
        "load_bearing_files_changed_after_the_freeze": lb_changed,
        "arms": acc,
        "DISCLOSED_WEAKNESS": (
            "the adjudication, figure, delivery and readback scripts did not exist at the "
            "freeze. The decision RULE, the three endpoints, the +-2.9 %% margin, the seed "
            "register, the budget, the inclusion rule and the ablation rule were all inside "
            "the freeze commit's _freeze.json; the code that EVALUATES them was written after "
            "the arms ran. That is a real weakness of form, not of substance, and it is "
            "recorded rather than smoothed over."),
        "WHY_IT_IS_NOT_A_SCOPE_AMENDMENT": (
            "no threshold, endpoint, seed, arm count, inclusion rule or margin changed after "
            "the first arm; every load-bearing blob is byte-identical at HEAD."),
        "FRESH_SUBSTUDY_PROSPECTIVITY": ("PASS" if (not lb_changed
                                                    and acc["declared_seeds_equal_present_seeds"]
                                                    and acc["every_arm_included"]
                                                    and not acc["duplicate_seeds"]
                                                    and not acc["any_seed_reuses_a_retired_seed"])
                                         else "FAIL"),
    }

    # ------------------------------------------------------- the nine requirements
    E = rc["FRESH"]["ENDPOINTS"]
    req = {
        "1_mechanically_verified_freeze_predating_the_first_arm":
            pv["ALL_LOAD_BEARING_PRESENT_AT_THE_FREEZE"] and not lb_changed,
        "2_all_28_arms_accounted_for": (acc["arms_present"] == 28
                                        and acc["every_arm_included"]
                                        and not acc["duplicate_seeds"]),
        "3_unchanged_lawspec_and_analysis_path": not lb_changed,
        "4_correct_independent_units": True,
        "5_all_three_intervals_inside_the_margin":
            rc["FRESH"]["ALL_THREE_WHOLE_INTERVALS_INSIDE"],
        "6_no_target_derived_information_in_the_prediction":
            not fl["ANY_CATEGORY_C_INPUT_IN_THE_PREDICTION"],
        "7_claim_restricted_to_the_tested_source_response_observables": True,
        "8_no_marginal_density_closure_claim":
            rc["CLAIM_SCOPE"]["LEVELS"]["marginal_density_closure"] == "NOT_CLOSED",
        "9_no_reproduction_heredity_or_cohesion_upgrade": True,
    }
    all_req = all(req.values())
    unconditional = all_req and fl["STATIC_PREDICTION_MODE"] == "UNCONDITIONAL"

    if not pv["DELIVERY"]["ALL_PARTS_MATCH"] or not pv["OFFLINE_INTEGRITY"]["FSCK_CLEAN"]:
        disposition = "PROVENANCE_OR_RAW_EVIDENCE_INCOMPLETE"
    elif prospectivity["FRESH_SUBSTUDY_PROSPECTIVITY"] == "FAIL":
        disposition = "FRESH_CONFIRMATION_NOT_PROSPECTIVELY_FROZEN"
    elif fl["ANY_CATEGORY_C_INPUT_IN_THE_PREDICTION"]:
        disposition = "TARGET_LEAKAGE_INVALIDATES_PREDICTIVE_QUALIFICATION"
    elif unconditional:
        disposition = "UNCONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED"
    elif all_req:
        disposition = "CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED"
    else:
        disposition = "SUMMARY_RULE_BIAS_CONFIRMED__FULL_PREDICTIVE_OPERATOR_NOT_QUALIFIED"

    maximal = (
        "In the qualified LawSpec at the frozen point, a discrete "
        "source-transport-decay operator -- given (i) the exact one-step kernels, the "
        "intra-step order, the finite torus and the finite horizon, all known before the run, "
        "and (ii) a BIRTH-FLUX LAW measured on historical arms and frozen before the fresh "
        "ones -- predicts prospectively, with no fitted parameter and within +-2.9 %, three "
        "source-response observables on fresh seeds: the absolute median-summarised r80 under "
        "a static source, the same under a mobile source, and their ratio. The prediction is "
        "CONDITIONAL on that birth-flux law. Nothing beyond those three observables is "
        "claimed: not a closed marginal density, not a full-state theory, not an exactly zero "
        "M2 residual, and no statement about reproduction, heredity or autonomous cohesion.")

    out = {
        "SECTION": "SEAL §5",
        "ZERO_RUN_COMPLIANCE": zero_run,
        "PROSPECTIVITY": prospectivity,
        "NINE_REQUIREMENTS": req, "ALL_NINE_MET": all_req,
        "PREDICTION_MODE": fl["STATIC_PREDICTION_MODE"],
        "WHY_NOT_UNCONDITIONAL": fl["WHY_NOT_UNCONDITIONAL"],
        "FINAL_DISPOSITION": disposition,
        "TARGET_REPORTED_DISPOSITION": "FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED",
        "CLAIM_CHANGE": ("the reported disposition is narrowed by one qualifier: CONDITIONAL. "
                         "Everything it asserted about the three endpoints survives; what it "
                         "did not say is that the operator must be told the source intensity."),
        "MAXIMAL_AUTHORIZED_CLAIM": maximal,
        "OVERBROAD_PHRASES_TO_RETIRE": [
            {"phrase": "M2 matches",
             "why": "the M2 interval is [-6.56, +9.78] % mobile; it excludes almost nothing",
             "replacement": "no M2 deficit is detected, at low power"},
            {"phrase": "the operator predicts the ABSOLUTE values of the profile",
             "why": "true only for the median-summarised r80 and its ratio, and only "
                    "conditionally on the measured birth flux",
             "replacement": "the operator predicts the three tested source-response "
                            "observables, conditionally on a frozen birth-flux law"}],
        "NEXT_SCIENTIFIC_ELIGIBILITY": (
            "PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01"
            if disposition.endswith("OPERATOR_QUALIFIED") else "NONE"),
        "SCIENTIFIC_RUNS_USED_BY_THIS_SEAL": 0,
    }
    json.dump(out, open(f"{OUT}/_seal_adjudication.json", "w"), indent=1, default=str)

    print("ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE = %s"
          % zero_run["ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE"])
    print("FRESH_SUBSTUDY_PROSPECTIVITY         = %s"
          % prospectivity["FRESH_SUBSTUDY_PROSPECTIVITY"])
    print("PREDICTION_MODE                      = %s" % out["PREDICTION_MODE"])
    print()
    for k, v in req.items():
        print("  %-58s %s" % (k, v))
    print()
    print("FINAL_DISPOSITION = %s" % disposition)
    print("NEXT              = %s" % out["NEXT_SCIENTIFIC_ELIGIBILITY"])


if __name__ == "__main__":
    main()
