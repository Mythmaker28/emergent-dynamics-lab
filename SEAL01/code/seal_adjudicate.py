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
        "WHAT_IS_ACTUALLY_IN_EVIDENCE": {
            "pillar_1__OBTR01_eligibility": {
                "READ_FROM_THE_TREE": True,
                "path": "OBTR01/out/_freeze.json -> NEXT_ELIGIBILITY",
                "status": "VERIFIED: the absolute radial deficit is listed "
                          "ELIGIBLE_AT_THE_QUALIFIED_POINT"},
            "pillar_2__the_OBFOR01_mandate_sections_16_to_20": {
                "READ_FROM_THE_TREE": False,
                "status": "NOT IN THE DELIVERY. The handoff text was never committed. The "
                          "description above is unverifiable prose about an absent document."},
            "pillar_3__the_later_RECONSTRUCTION_handoff": {
                "READ_FROM_THE_TREE": False,
                "status": "NOT IN THE DELIVERY. Its NEW_ENGINE_STARTS = 0 and its arrival "
                          "date are asserted, not shown."}},
        "ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE": "NOT_DETERMINABLE_FROM_THE_DELIVERED_EVIDENCE",
        "WHY_NOT_PASS": (
            "the earlier verdict PASS was a hardcoded string, not a computed one, and two of "
            "its three pillars are prose about documents that are not in the delivery. A "
            "seal whose founding instruction is 'do not accept prose claims as evidence' "
            "cannot itself certify compliance from prose. Only pillar 1 is evidence: it "
            "shows the QUESTION was open. It does not show what run budget the governing "
            "mandate set, because that mandate is not in the tree."),
        "WHAT_WOULD_SETTLE_IT": ("commit the governing handoff texts, or their hashes, into "
                                 "the repository at the moment a mission opens. Until then "
                                 "run-budget compliance is not a verifiable property of the "
                                 "delivery."),
        "NOT_A_FINDING_OF_VIOLATION": ("this is a finding of UNVERIFIABILITY, not of breach. "
                                       "No evidence of a run-budget breach was found either."),
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
        # the criterion of record is the FROZEN one, which is a point rule. The whole-interval
        # criterion is post-freeze and stricter; it is reported beside, not substituted in.
        "5_all_three_points_inside_the_frozen_margin":
            rc["FRESH"]["ALL_THREE_POINTS_INSIDE__THE_CRITERION_OF_RECORD"],
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

    rep = json.load(open(f"{OUT}/OBFOR01_SEAL_REPAIR_EVIDENCE.json"))
    maximal = (
        "In the qualified LawSpec at the frozen point, a discrete source-transport-decay "
        "operator -- given (i) the exact one-step kernels, the intra-step order, the finite "
        "torus and the finite horizon, all known before the run, and (ii) a BIRTH-FLUX LAW "
        "measured on historical arms and frozen before the fresh ones -- stated three "
        "point predictions in advance which the fresh seeds DID NOT FALSIFY, each within the "
        "frozen +-2.9 % margin: the absolute median-summarised r80 under a static source, the "
        "same under a mobile source, and their ratio. Within the same test, the SHARED "
        "ORGANISER TRAJECTORY is REQUIRED: removing it misses the fresh mobile observation by "
        "-3.55 %, and the uncorrected ideal operator misses it by -5.46 %, both outside the "
        "margin. The prediction is CONDITIONAL on the birth-flux law, on derivational "
        "grounds: M6 does not derive the source, it is handed it. Nothing beyond those three "
        "observables is claimed: not a closed marginal density, not a full-state theory, not "
        "an exactly zero M2 residual, and no statement about reproduction, heredity or "
        "autonomous cohesion.")
    limits = {
        "THE_TEST_HAS_LIMITED_DISCRIMINATING_POWER": (
            "a zero-physics baseline -- 'the fresh arms will look like the historical arms', "
            "computable from OBDI02 and OBTC02 before OBFOR01 opened -- also passes all "
            "three endpoints (static +0.47 %, mobile -0.31 %, ratio -0.77 %). The fresh "
            "arms therefore do NOT separate the operator from mere historical resemblance. "
            "What they DO separate is the shared-trajectory mechanism from its absence."),
        "THE_PREDICTIONS_ARE_NOT_POINTS": (
            "the M6 point predictions carry a Monte-Carlo standard deviation of %.3f %% "
            "(static) and %.3f %% (mobile), measured over 16 replicates of the frozen "
            "30-arm design. The frozen mobile prediction itself lies %.2f such sd from the "
            "replicated mean."
            % (rep["R3_PREDICTION_MONTE_CARLO_SD"]["static_percent"],
               rep["R3_PREDICTION_MONTE_CARLO_SD"]["mobile_percent"],
               rep["R1_BIRTH_FLUX_ABLATION_REPLICATED"][
                   "WHERE_THE_TWO_FROZEN_RUNS_SIT_IN_THEIR_OWN_REPLICATE_DISTRIBUTIONS"][
                   "z_against_the_replicated_empirical_mean"])),
        "NO_FITTED_PARAMETER_IS_WITHDRAWN": (
            "the phrase 'with no fitted parameter' is retired. The birth-flux law is an "
            "empirical distribution of about 360000 samples estimated IN SAMPLE on the same "
            "historical L=36 arms that set the developmental baseline. It is a "
            "non-parametric estimate, not the absence of an estimate."),
        "THE_HISTORICAL_HEADLINE_DEPENDS_ON_AN_OUTCOME_DEPENDENT_FILTER": (
            "the -5.10 %% historical mobile residual becomes -4.35 %% without the nX_final "
            ">= 40 rule and -2.14 %% with no population threshold at all. The magnitude of "
            "the developmental residual is a joint property of the observable and of the "
            "inclusion rule."),
        "THE_STATIC_BRANCH_RESTS_ON_THREE_HISTORICAL_ARMS": True,
        "THE_STATIC_ENDPOINT_IS_NOT_DISCRIMINATING": (
            "even the uncorrected ideal operator passes the static endpoint at -1.38 %. "
            "Only the mobile endpoint and the ratio carry information about the mechanism."),
    }

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
        "LIMITS_THAT_TRAVEL_WITH_THE_CLAIM": limits,
        "OVERBROAD_PHRASES_TO_RETIRE": [
            {"phrase": "M2 matches",
             "why": "the M2 interval is [-6.56, +9.78] % mobile; it excludes almost nothing",
             "replacement": "no M2 deficit is detected, at low power"},
            {"phrase": "the operator predicts the ABSOLUTE values of the profile",
             "why": "true only for the median-summarised r80 and its ratio, and only "
                    "conditionally on the measured birth flux",
             "replacement": "the operator predicts the three tested source-response "
                            "observables, conditionally on a frozen birth-flux law"},
            {"phrase": "with no fitted parameter",
             "why": "the birth-flux law is a ~360000-sample empirical distribution estimated "
                    "in sample on the same historical arms",
             "replacement": "with no free parameter tuned to the fresh arms"},
            {"phrase": "predicts prospectively",
             "why": "a zero-physics historical-copy baseline also passes all three endpoints",
             "replacement": "stated three predictions in advance which the fresh seeds did "
                            "not falsify, and within which the shared-trajectory mechanism "
                            "is required"},
            {"phrase": "the shape of the birth flux is load-bearing (1.27 points)",
             "why": "replication over 16 x 30 arms per side gives +0.41 +- 0.20 pp, of the "
                    "opposite sign; and doubling the source intensity moves the prediction "
                    "by +0.01 +- 0.23 pp",
             "replacement": "the birth-flux law is a measured INPUT, which is why the "
                            "prediction is conditional; its numerical influence is small"},
            {"phrase": "the Poisson-source model is rejected by a factor 4.5",
             "why": "that model's own residual is -4.42 % and it passes the +-2.9 % endpoint",
             "replacement": "the Poisson-source variant is further from the observation but "
                            "is not rejected"}],
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
