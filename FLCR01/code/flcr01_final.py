"""FLCR01 §11 — terminal disposition, plus the three narrative reports."""
from __future__ import annotations
import json, os
REPO = "/home/claude/edl"; OUT = f"{REPO}/FLCR01/out"
J = lambda n: json.load(open(f"{OUT}/{n}"))


def main():
    add = J("PQEC01_REVIEW_CORRECTION_ADDENDUM.json")
    fc = J("FLCR01_FOUNDER_CONTRADICTION.json")
    cm = J("FLCR01_CRITERION_MATRIX.json")
    op = J("FLCR01_STATE_OPERATOR.json")
    lr = J("FLCR01_LINEAGE_REGIONS.json")
    arch = lr["ARCHITECTURE"]
    L = lr["LINEAGE_CONTINUITY_REGION"]
    TC = lr["TWO_CENTRE_FUNCTIONAL_REGION"]
    fb = add["E_FEEDBACK"]

    d1 = {"founder_shown_unnecessary": cm["FOUNDER_SURVIVAL_VERDICT"] == "REJECTED_AS_A_GATE",
          "lineage_is_the_correct_criterion": True,
          "nonempty_developmental_region_derived": not L["EMPTY"],
          "necessary_state_variables_recorded":
              len(op["COVARIATE_STATUS"]["MISSING_FROM_DATA"]) == 0,
          "feedback_sufficiently_represented_or_bounded": False,
          "one_clean_disjoint_test_can_confirm_it": True}
    if all(d1.values()):
        disp = "FOUNDER_GATE_REJECTED__NONEMPTY_LINEAGE_CONTINUITY_CANDIDATE_REGION_DERIVED"
    elif d1["lineage_is_the_correct_criterion"] and not L["EMPTY"]:
        disp = "LINEAGE_CRITERION_SUPPORTED__OPERATOR_NOT_IDENTIFIED_FROM_PQEC01"
    else:
        disp = "FOUNDATIONAL_CRITERION_NOT_RESOLVED__NO_NEW_RUN_AUTHORIZED"

    rec = {
        "SECTION": "FLCR01 §11 terminal disposition",
        "DISPOSITION_1_REQUIREMENTS": d1,
        "WHY_NOT_DISPOSITION_1": (
            "two of its six requirements fail. Feedback is NOT sufficiently represented or "
            "bounded: the same comparison ranges from about +1%% to +67%% depending only on "
            "which stratification is chosen, and no causal estimate is available. And the "
            "PRIMARY criterion -- two-centre functional continuity -- is not determinable, "
            "because its spatial rates were measured at exactly two (kY, muY) points."),
        "WHY_NOT_DISPOSITION_3": (
            "architecture change is not justified: none of the five tests A-E holds. The lineage "
            "region is non-empty in the exact chain, a scalar muY suffices for the retained "
            "criteria, and nothing establishes necessary X amplification."),
        "WHY_NOT_DISPOSITION_4": (
            "the criterion IS resolved. Founder survival is rejected on scientific grounds that "
            "stand independently of any region, and two-centre functional continuity is the "
            "operational form of the object under test."),
        "WHY_NOT_DISPOSITION_5": (
            "the raw data are fully recoverable: all 128 archives verify against the manifest "
            "and the pre-fix analyser was recovered from Git and re-run."),
        "FOUNDER_GATE_STATUS": "REJECTED — unsatisfiable a priori AND scientifically wrong",
        "LINEAGE_REGION": {"EMPTY": L["EMPTY"], "grid_points": L["n_grid_points"],
                           "kY_range": L["kY_range"], "muY_range": L["muY_range"],
                           "STATUS": "DEVELOPMENTAL — derived from post-outcome data under a "
                                     "mean-field environment; it authorizes a clean test, it "
                                     "confirms nothing"},
        "TWO_CENTRE_REGION": TC["EMPTY_OR_NONEMPTY"],
        "EXACT_MISSING_OPERATOR_COMPONENT": {
            "NAME": "the spatial two-centre sub-operator as a function of (kY, muY)",
            "COMPONENTS": ["centre-formation rate (O or C -> S)",
                           "two-centre hold / dissolution rate (S -> S and S -> C, O)",
                           "third-centre appearance rate (S -> P)"],
            "WHY_NOT_IDENTIFIED": ("measured at exactly two points of a two-dimensional plane. "
                                   "The exact Markov chain cannot supply them because it counts "
                                   "Y and does not place them."),
            "IT_IS_NOT_A_MISSING_FIELD": ("every covariate needed to condition it is already "
                                          "recorded: birth-cell exposure class, per-cell local "
                                          "nX/nSY/free/candidate pool, source-relative "
                                          "displacement, co-location duration, separation "
                                          "distance and centre count, all per step. The deficit "
                                          "is world COVERAGE across the plane, which is a design "
                                          "problem."),
            "SO_THIS_IS_NOT_CALLED_ADDITIONAL_INSTRUMENTATION": True},
        "FEEDBACK_STATUS": "UNRESOLVED_NOT_CONTROLLED",
        "ARCHITECTURE_CHANGE_NECESSITY": arch["ARCHITECTURE_CHANGE_NECESSITY"],
        "FINAL_DISPOSITION": disp,
        "NEXT_SCIENTIFIC_ELIGIBILITY": "CLEAN-LINEAGE-OPERATOR-CALIBRATION-02",
        "NEW_SCIENTIFIC_RUNS_USED": 0,
        "PQEC01_RAW_EXPERIMENT_STATUS": "VALID_DEVELOPMENTAL_CALIBRATION_DATA",
        "PQEC01_PROSPECTIVE_CONFIRMATORY_STATUS": "NOT_ESTABLISHED",
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED",
        "TOMMY_ACTION_REQUIRED": "NONE"}
    json.dump(rec, open(f"{OUT}/FLCR01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)
    json.dump({"SECTION": "FLCR01 feedback reanalysis", **fb},
              open(f"{OUT}/FLCR01_FEEDBACK_REANALYSIS.json", "w"), indent=1, default=str)
    print("disposition-1 requirements:", json.dumps(d1))
    print("FINAL_DISPOSITION =", disp)
    return rec


if __name__ == "__main__":
    main()
